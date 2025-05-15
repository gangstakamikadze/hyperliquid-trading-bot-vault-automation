import { Connection } from '@solana/web3.js';
import { SolanaFM } from './solanaFM';

interface SafetyCheck {
  lpBurned: boolean;
  freezeAuthority: boolean;
}

class HoneypotFilterDex {
  constructor(
    private connection: Connection,
    private solanaFM: SolanaFM
  ) {}

  async isSafeToken(poolAddress: string): Promise<SafetyCheck> {
    const poolData = await this.solanaFM.getPoolMetadata(poolAddress);
    const lpBurned = poolData.liquidityBurned;
    const freezeAuthority = poolData.freezeAuthority === null;

    console.log(`[HoneypotFilterDex] LP Burned: ${lpBurned}, Freeze Authority: ${freezeAuthority}`);
    return { lpBurned, freezeAuthority };
  }

  async filterTrade(poolAddress: string): Promise<boolean> {
    const { lpBurned, freezeAuthority } = await this.isSafeToken(poolAddress);
    return lpBurned && freezeAuthority;
  }
}
