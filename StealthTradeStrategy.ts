import { Connection, Keypair } from '@solana/web3.js';
import { DexRouter } from './dexRouter';

class StealthTradeStrategy {
  constructor(
    private connection: Connection,
    private dexRouter: DexRouter
  ) {}

  async executeStealthTrade(
    wallets: Keypair[],
    poolAddress: string,
    totalVolume: number
  ): Promise<void> {
    const volumePerWallet = totalVolume / wallets.length;

    for (const wallet of wallets) {
      const delay = this.randomDelay(1000, 5000);
      await this.sleep(delay);
      await this.dexRouter.swap('jupiter', wallet, volumePerWallet);
      console.log(`[StealthTradeStrategy] Trade executed for wallet ${wallet.publicKey.toBase58()}`);
    }
  }

  private randomDelay(min: number, max: number): number {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
