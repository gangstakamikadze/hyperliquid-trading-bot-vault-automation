import { Connection, Keypair } from '@solana/web3.js';
import { DexRouter } from './dexRouter';

interface RiskConfig {
  stopLoss: number;
  takeProfit: number;
}

class RiskManagementDex {
  constructor(
    private connection: Connection,
    private dexRouter: DexRouter
  ) {}

  async manageTrade(
    wallet: Keypair,
    poolAddress: string,
    entryPrice: number,
    config: RiskConfig
  ): Promise<void> {
    const currentPrice = await this.getTokenPrice(poolAddress);

    if (currentPrice <= entryPrice * (1 - config.stopLoss / 100)) {
      await this.dexRouter.swap('raydium', wallet, 0, 'sell');
      console.log(`[RiskManagementDex] Stop loss triggered at ${currentPrice}`);
    } else if (currentPrice >= entryPrice * (1 + config.takeProfit / 100)) {
      await this.dexRouter.swap('raydium', wallet, 0, 'sell');
      console.log(`[RiskManagementDex] Take profit triggered at ${currentPrice}`);
    }
  }

  private async getTokenPrice(poolAddress: string): Promise<number> {
    // Simulate price fetching
    return 0.10;
  }
}
