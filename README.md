# Solana Auto Sniping Bot 🌟
The bot is optimized and ready for trading in mainnet. Just configure config and RPC, in config.yaml you can specify unlimited number of wallets based on the templates

Solana Sniper is tool for conquering the Solana blockchain! 🚀 This , open-source bot is designed to automate trading, portfolio management, and market-making with lightning speed and precision. Whether you're a DeFi enthusiast or a seasoned trader, Solana Sniper gives you the edge to snipe new token pools, optimize profits, and stay ahead of the game. 💸
## Why Solana Auto Sniping is Unique? 🎯
- Blazing Fast on Solana ⚡: Built for Solana’s high-speed blockchain, it snipes new liquidity pools and executes trades in milliseconds.

- Smart Trading Strategies 📈: Uses advanced technical indicators (RSI, ATR, Bollinger Bands) to identify profitable opportunities with precision.

- Multi-Wallet Support 🔗: Manage multiple Solana wallets simultaneously for diversified trading and portfolio syncing.

- Seamless Notifications 📱: Get real-time updates via Telegram for trades, portfolio syncs, and errors, keeping you in the loop 24/7.

- User-Friendly Web Interface 🌐: Control and monitor your bot through an intuitive FastAPI dashboard at http://localhost:8000/docs.

## Key Features 🔥
- **Pool Sniping 🎯**: Automatically detects and trades new liquidity pools on Raydium or other DEXes, maximizing early entry profits.
- **Portfolio Syncing 💼**: Securely transfers SOL and SPL tokens (like USDC) to a designated wallet, ensuring efficient asset management.
- **Market-Making & Arbitrage 💹**: Places strategic buy/sell orders and exploits price differences for consistent gains.
- **Technical Analysis 📊**: Leverages RSI, ATR, and Bollinger Bands to make data-driven trading decisions.
- **Telegram Integration 📩**: Sends instant alerts for executed trades, portfolio updates, and system status.
- **FastAPI Dashboard 🖥️**: Monitor wallet balances, trade history, and bot performance via a sleek web interface.
- **Flexible Configuration ⚙️**: Customize trading parameters, timeframes, and wallet settings via an easy-to-edit config.yaml.
- **Open-Source & Customizable 🛠️**: Fully open-source on GitHub, allowing you to tweak and tailor it to your trading style.
### Contact
Telegram: [@ZeronodeX](https://t.me/ZeronodeX)
# Solana Sniper Installation Guide 🎉
## If you swing the .zip, skip the installation through git repository, specify the folder or open the unzipped folder and install the required dependencies and run the bot through Visual Studio or Terminal form macOS and Linux
```
cd your_unzip_folder
```
```
python -m venv venv
```
```
.\venv\Scripts\activate
```
```
python -m pip install --upgrade pip setuptools
```
```
pip install numpy==1.26.4 pandas pandas_ta pyyaml python-telegram-bot==21.4 solana solders fastapi uvicorn websockets
```

## Welcome to the Solana Sniper setup guide! This bot helps you trade and manage SPL tokens on Solana with ease. Follow these simple steps for Windows, macOS, or Linux to get started. Let’s dive in! 😎

## Prerequisites 📋
Before you begin, make sure you have:

- **Python 3.13.2** installed (works great with all dependencies! 🐍).
- Git installed to clone the repository 🌐.
- A Solana wallet with:
     - Private key.
     - Balance >0.003 SOL for fees 💸.

- A Telegram bot token and chat ID for notifications (optional, see **Configure Telegram** 📱).
- A text editor like Visual Studio Code to edit config.yaml ✍️.

Installation Instructions 🛠️

## Windows 🖥️

### 1. Install Python 3.13.2

- Download Python 3.13.2 from python.org 🌐.
- Run the installer:
- Check **Add Python to PATH** ✅.
- Click **Install Now**.

- Verify:
```
python --version
```

Expected: Python 3.13.2 🎯.
### Install Git
- Download Git from git-scm.com.
- Install with default settings.

- Verify:
```
git --version
```
### 2. Clone the Repository

- Create and navigate to the project folder:
```
mkdir C:\Users\<YourUsername>\Desktop\solana-sniper
```
```
cd C:\Users\<YourUsername>\Desktop\solana-sniper
```
```
git clone https://github.com/yourusername/solana-sniper.git
```
### 3. Create and Activate Virtual Environment

- Create a virtual environment:
```
python -m venv venv
```

- Activate it:
```
.\venv\Scripts\activate
```
Look for (venv) in your terminal! 😊

### 4. Install Dependencies

- Update pip and install all packages:
```
python -m pip install --upgrade pip setuptools
```
```
pip install numpy==1.26.4 pandas pandas_ta pyyaml python-telegram-bot==21.4 solana solders fastapi uvicorn websockets
```

- Check installations:
```
pip list
```
You should see: numpy, pandas, pandas_ta, pyyaml, python-telegram-bot, solana, solders, fastapi, uvicorn, websockets ✅.

### 5. Install Solana CLI (Optional)
To manage wallets and check balances:

- Install Solana CLI:
```
curl https://release.solana.com/stable/solana-install-init-x86_64-pc-windows-msvc.exe -o solana-installer.exe
```
```
.\solana-installer.exe stable
```

Verify:
```
solana --version
```

### 6. Configure the Project
Jump to Configure Project below! 🚀

## macOS 🍎

### 1. Install Python 3.13.2

Install Homebrew (if not installed):
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install Python 3.13.2:
```
brew install python@3.13
```

Verify:
```
python3.13 --version
```

Expected: Python 3.13.2 🎉.
### Install Git
- Install Git via Homebrew:
```
brew install git
```
Verify:
```
git --version
```
### 2. Clone the Repository

- Create a directory and clone the project:
```
mkdir ~/Desktop/solana-sniper
```
```
cd ~/Desktop/solana-sniper
```
```
git clone https://github.com/yourusername/solana-sniper.git
```

### 3. Create and Activate Virtual Environment

- Create a virtual environment:
```
python3.13 -m venv venv
```

- Activate it:
```
source venv/bin/activate
```

You’ll see (venv) in the terminal! 😄

### 4. Install Dependencies

Update pip and install packages:
```
python -m pip install --upgrade pip setuptools
```
```
pip install numpy==1.26.4 pandas pandas_ta pyyaml python-telegram-bot==21.4 solana solders fastapi uvicorn websockets
```
Verify:
```
pip list
```
### 5. Install Solana CLI (Optional)

- Install Solana CLI:
```
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

Update PATH (if prompted) and verify:
```
solana --version
```
### 6. Configure the Project
See Configure Project below! 🌟

## Linux 🐧

### 1. Install Python 3.13.2

- Update package manager (Ubuntu/Debian):
```
sudo apt update
```
```
sudo apt install -y software-properties-common
```
- Add PPA and install Python 3.13.2:
```
sudo add-apt-repository ppa:deadsnakes/ppa
```
```
sudo apt install -y python3.13 python3.13-venv python3.13-dev
```

Verify:
```
python3.13 --version
```

Expected: Python 3.13.2 🚀.

### Install Git
- Install Git:
```
sudo apt install -y git
```
Verify:
```
git --version
```

### 2. Clone the Repository

Create a directory and clone the project:
```
mkdir ~/Desktop/solana-sniper
```
```
cd ~/Desktop/solana-sniper
```
### 3. Create and Activate Virtual Environment

Create a virtual environment:
```
python3.13 -m venv venv
```

Activate it:
```
source venv/bin/activate
```

Look for (venv) in the terminal! 😎

### 4. Install Dependencies

Update pip and install packages:
```
python -m pip install --upgrade pip setuptools
```
```
pip install numpy==1.26.4 pandas pandas_ta pyyaml python-telegram-bot==21.4 solana solders fastapi uvicorn websockets
```

Verify:
```
pip list
```

### 5. Install Solana CLI (Optional)

Install Solana CLI:
```
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

Update PATH (if prompted) and verify:
```
solana --version
```

### 6. Configure the Project
Check out Configure Project below! 🎯

## Configure Project ⚙️

### 1. Verify Project Files

Ensure these files are in your project directory (solana-sniper):

- **solana_bot.py**: The main bot script for trading and syncing 📈.
- **utils.py**: Helper functions for token validation and data 📚.
- **config.yaml**: Settings for wallets and bot parameters ⚙️. if you take in config.yaml exampale, delete "add more" in last line
- **raydium_sdk.py**: raydium placeholder
- **orca_sdk.py**: orca placeholder
- **jupiter_sdk.py**: jupiter placeholder

If missing, get them from the project repository or author. Example config.yaml:
```
wallet1:
  private_key: <your_private_key>
  token_address: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
  solana_rpc: https://api.mainnet-beta.solana.com
  dex: raydium
  symbol: USDC
  timeframe: 1h
  rsi_period: 14
  rsi_overbought: 70
  rsi_oversold: 30
  position_size: 0.1
  stop_loss_pct: 0.05
  take_profit_pct: 0.1
  spread_pct: 0.01
  atr_period: 14
  telegram_chat_id: <your_chat_id>
  telegram_token: <your_telegram_token>
```
you can add more wallet's with settings, just copy, but use wallet2, wallet3, etc

### 2. Configure Wallets

- Check balance:
```
solana balance <wallet_address>
```

- Ensure >0.003 SOL 💰.
- Add your wallet’s private key to config.yaml.

### 3. Configure Telegram (Optional)

Create a Telegram bot:
- Find @BotFather in Telegram, send /start, then /newbot 🤖.
- Set name (e.g., MySniperBot) and username (e.g., @MySniperBot).
- Copy the token API.

Get your chat ID:
- Send /start to @userinfobot for personal chat ID 📱.
- For groups, add @getidsbot to the group.

Update config.yaml with telegram_token and telegram_chat_id.

### 4. Configure Token

- Set token_address to your SPL token (e.g., USDC: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v) 💸.
- Set symbol to the token’s ticker (e.g., USDC).
- Customize parameters for your trading

## Run the Bot 🚀

### 1. Activate the virtual environment:

Windows:
```
.\venv\Scripts\activate
```

macOS/Linux:
```
source venv/bin/activate
```

### 2. Run the bot:
```
python solana_bot.py
```

### 3. Check logs:
cat sniper_bot.log

Look for:
2025-05-06 23:50:00,000 - INFO - Sniper bot started

Open the web interface (optional):

Visit http://localhost:8000/docs in your browser 🌐.

## Troubleshooting 🔍
### ModuleNotFoundError:
- Check dependencies:
```
pip list
```
- Reinstall:
```
pip install numpy==1.26.4 pandas pandas_ta pyyaml python-telegram-bot==21.4 solana solders fastapi uvicorn websockets
```

### yaml.scanner.ScannerError:
- Verify config.yaml syntax (e.g., no missing : or invalid text like add more).
- Use yaml-online-parser to validate 📝.

### Invalid token address:
- Ensure token_address is valid (e.g., EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v for USDC).

### No Telegram notifications:
- Check telegram_token and telegram_chat_id in config.yaml.
- Look for errors:
```
cat sniper_bot.log | grep Telegram
```
- Low SOL balance:
Top up your wallet:solana transfer <wallet_address> 0.01

## Tips & Tricks 🌟

Use Python 3.13.2 for smooth compatibility with all libraries 🐍.

Keep config.yaml secure—it contains private keys! 🔒

For faster RPC, try QuickNode or Helius ⚡.

