import { Connection, Keypair } from '@solana/web3.js';
import { RaydiumSDK, JupiterAPI, OrcaAPI } from './dexApis';

class DexRouter {
  private raydium: RaydiumSDK;
  private jupiter: JupiterAPI;
  private orca: OrcaAPI;

  constructor(private connection: Connection) {
    this.raydium = new RaydiumSDK(connection);
    this.jupiter = new JupiterAPI(connection);
    this.orca = new OrcaAPI(connection);
  }

  async swap(
    dex: 'raydium' | 'jupiter' | 'orca',
    wallet: Keypair,
    amount: number,
    type: 'buy' | 'sell' = 'buy'
  ): Promise<void> {
    switch (dex) {
      case 'raydium':
        await this.raydium.executeSwap(wallet, amount, type);
        break;
      case 'jupiter':
        await this.jupiter.executeSwap(wallet, amount, type);
        break;
      case 'orca':
        await this.orca.executeSwap(wallet, amount, type);
        break;
      default:
        throw new Error('Unsupported DEX');
    }
    console.log(`[DexRouter] Swap executed on ${dex} for ${amount}`);
  }
}
