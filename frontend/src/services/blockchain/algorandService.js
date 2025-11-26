/**
 * Algorand Blockchain Service
 * Algorand 블록체인 연동 서비스 (플레이스홀더)
 */

import algosdk from 'algosdk';

const ALGORAND_SERVER = process.env.REACT_APP_ALGORAND_SERVER || 'https://testnet-api.algonode.cloud';
const ALGORAND_PORT = process.env.REACT_APP_ALGORAND_PORT || 443;
const ALGORAND_TOKEN = '';

// PAM 토큰 자산 ID (TestNet)
export const PAM_TOKEN_ASSET_ID = 746418487;

// ESG-GOLD(DC) 토큰 자산 ID (TestNet) - 생성 후 업데이트 필요
export const ESG_GOLD_ASSET_ID = process.env.REACT_APP_ESG_GOLD_ASSET_ID || null;

// 담보 풀 주소 (관리자 계정)
export const COLLATERAL_POOL_ADDRESS = process.env.REACT_APP_COLLATERAL_POOL_ADDRESS || null;

// 담보 비율 (1 ALGO = 1000 DC)
export const COLLATERAL_RATIO = 1000;

// 최소 담보 예치량 (ALGO)
export const MIN_COLLATERAL_AMOUNT = 10;

// Algorand 클라이언트 생성
const algodClient = new algosdk.Algodv2(ALGORAND_TOKEN, ALGORAND_SERVER, ALGORAND_PORT);

const algorandService = {
  /**
   * 지갑 생성
   * @returns {Object} 새 지갑 정보 (address, mnemonic)
   */
  createWallet: () => {
    try {
      const account = algosdk.generateAccount();
      const mnemonic = algosdk.secretKeyToMnemonic(account.sk);

      return {
        address: account.addr,
        mnemonic,
      };
    } catch (error) {
      console.error('Create wallet error:', error);
      throw error;
    }
  },

  /**
   * 니모닉에서 지갑 복구
   * @param {string} mnemonic - 니모닉 구문
   * @returns {Object} 복구된 지갑 정보
   */
  recoverWallet: (mnemonic) => {
    try {
      const account = algosdk.mnemonicToSecretKey(mnemonic);

      return {
        address: account.addr,
      };
    } catch (error) {
      console.error('Recover wallet error:', error);
      throw error;
    }
  },

  /**
   * 잔액 조회
   * @param {string} address - 지갑 주소
   * @returns {Promise<number>} 잔액 (microAlgos)
   */
  getBalance: async (address) => {
    try {
      const accountInfo = await algodClient.accountInformation(address).do();
      return accountInfo.amount;
    } catch (error) {
      console.error('Get balance error:', error);
      throw error;
    }
  },

  /**
   * 트랜잭션 전송
   * @param {Object} txParams - 트랜잭션 파라미터
   * @param {string} txParams.from - 발신자 주소
   * @param {string} txParams.to - 수신자 주소
   * @param {number} txParams.amount - 전송 금액 (micro units)
   * @param {string} txParams.mnemonic - 발신자 니모닉
   * @param {number} txParams.assetId - 자산 ID (옵션, 없으면 ALGO 전송)
   * @returns {Promise<string>} 트랜잭션 ID
   */
  sendTransaction: async (txParams) => {
    try {
      const { from, to, amount, mnemonic, assetId, note } = txParams;

      // 니모닉에서 계정 복구
      const senderAccount = algosdk.mnemonicToSecretKey(mnemonic);

      // 트랜잭션 파라미터 가져오기
      const params = await algodClient.getTransactionParams().do();

      let txn;
      if (assetId) {
        // ASA 토큰 전송
        txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
          from: senderAccount.addr,
          to,
          amount: Math.floor(amount),
          assetIndex: assetId,
          suggestedParams: params,
          note: note ? new Uint8Array(Buffer.from(note)) : undefined,
        });
      } else {
        // ALGO 전송
        txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
          from: senderAccount.addr,
          to,
          amount: Math.floor(amount),
          suggestedParams: params,
          note: note ? new Uint8Array(Buffer.from(note)) : undefined,
        });
      }

      // 트랜잭션 서명
      const signedTxn = txn.signTxn(senderAccount.sk);

      // 트랜잭션 전송
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();

      // 트랜잭션 확인 대기
      await algosdk.waitForConfirmation(algodClient, txId, 4);

      console.log('Transaction successful! TxID:', txId);
      return txId;
    } catch (error) {
      console.error('Send transaction error:', error);
      throw error;
    }
  },

  /**
   * 네트워크 상태 확인
   * @returns {Promise<Object>} 네트워크 상태
   */
  getNetworkStatus: async () => {
    try {
      const status = await algodClient.status().do();
      return status;
    } catch (error) {
      console.error('Get network status error:', error);
      throw error;
    }
  },

  /**
   * ASA 자산 옵트인
   * @param {string} address - 지갑 주소
   * @param {string} mnemonic - 니모닉
   * @param {number} assetId - 자산 ID
   * @returns {Promise<string>} 트랜잭션 ID
   */
  optInToAsset: async (address, mnemonic, assetId) => {
    try {
      const account = algosdk.mnemonicToSecretKey(mnemonic);
      const params = await algodClient.getTransactionParams().do();

      // 옵트인은 자신에게 0개의 자산을 보내는 트랜잭션
      const txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
        from: account.addr,
        to: account.addr,
        amount: 0,
        assetIndex: assetId,
        suggestedParams: params,
      });

      const signedTxn = txn.signTxn(account.sk);
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();
      await algosdk.waitForConfirmation(algodClient, txId, 4);

      console.log('Asset opt-in successful! TxID:', txId);
      return txId;
    } catch (error) {
      console.error('Opt-in error:', error);
      throw error;
    }
  },

  /**
   * 자산 잔액 조회
   * @param {string} address - 지갑 주소
   * @param {number} assetId - 자산 ID
   * @returns {Promise<number>} 자산 잔액
   */
  getAssetBalance: async (address, assetId) => {
    try {
      const accountInfo = await algodClient.accountInformation(address).do();
      const asset = accountInfo.assets?.find((a) => a['asset-id'] === assetId);
      return asset ? asset.amount : 0;
    } catch (error) {
      console.error('Get asset balance error:', error);
      throw error;
    }
  },

  /**
   * 자산 옵트인 여부 확인
   * @param {string} address - 지갑 주소
   * @param {number} assetId - 자산 ID
   * @returns {Promise<boolean>} 옵트인 여부
   */
  isOptedIn: async (address, assetId) => {
    try {
      const accountInfo = await algodClient.accountInformation(address).do();
      const asset = accountInfo.assets?.find((a) => a['asset-id'] === assetId);
      return !!asset;
    } catch (error) {
      console.error('Check opt-in error:', error);
      return false;
    }
  },

  // ============================================
  // COLLATERAL & DC MINTING FUNCTIONS
  // ============================================

  /**
   * 담보 예치 (ALGO를 Collateral Pool에 전송)
   * @param {string} userAddress - 사용자 주소
   * @param {string} mnemonic - 사용자 니모닉
   * @param {number} algoAmount - 예치할 ALGO 수량
   * @returns {Promise<Object>} 트랜잭션 결과
   */
  depositCollateral: async (userAddress, mnemonic, algoAmount) => {
    try {
      if (!COLLATERAL_POOL_ADDRESS) {
        throw new Error('Collateral pool address not configured');
      }

      if (algoAmount < MIN_COLLATERAL_AMOUNT) {
        throw new Error(`Minimum collateral amount is ${MIN_COLLATERAL_AMOUNT} ALGO`);
      }

      const account = algosdk.mnemonicToSecretKey(mnemonic);
      const params = await algodClient.getTransactionParams().do();

      // ALGO 전송 (microALGO 단위)
      const txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
        from: account.addr,
        to: COLLATERAL_POOL_ADDRESS,
        amount: Math.floor(algoAmount * 1_000_000),
        suggestedParams: params,
        note: new Uint8Array(Buffer.from(`Collateral deposit: ${algoAmount} ALGO`)),
      });

      const signedTxn = txn.signTxn(account.sk);
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();
      await algosdk.waitForConfirmation(algodClient, txId, 4);

      const dcCapacity = algoAmount * COLLATERAL_RATIO;

      console.log('Collateral deposit successful!', {
        txId,
        algoAmount,
        dcCapacity
      });

      return {
        success: true,
        txId,
        algoAmount,
        dcCapacity,
        collateralRatio: COLLATERAL_RATIO
      };
    } catch (error) {
      console.error('Deposit collateral error:', error);
      throw error;
    }
  },

  /**
   * DC 토큰 발급 가능량 계산
   * @param {number} algoAmount - ALGO 담보량
   * @returns {number} 발급 가능한 DC 수량
   */
  calculateDcCapacity: (algoAmount) => {
    return algoAmount * COLLATERAL_RATIO;
  },

  /**
   * DC 토큰 발급 (백엔드 API를 통해 처리)
   * 주의: 실제 발급은 백엔드에서 RESERVE 계정으로 처리
   * 프론트엔드에서는 발급 요청만 전송
   * @param {string} userAddress - 사용자 주소
   * @param {string} collateralId - 담보 ID (DB)
   * @param {number} dcAmount - 발급할 DC 수량
   * @returns {Promise<Object>} 발급 요청 결과
   */
  requestDcMinting: async (userAddress, collateralId, dcAmount) => {
    try {
      if (!ESG_GOLD_ASSET_ID) {
        throw new Error('ESG-GOLD asset ID not configured');
      }

      // 백엔드 API 호출
      const response = await fetch('/api/collateral/mint-dc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userAddress,
          collateralId,
          dcAmount
        })
      });

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'DC minting failed');
      }

      console.log('DC minting successful!', result);
      return result;
    } catch (error) {
      console.error('Request DC minting error:', error);
      throw error;
    }
  },

  /**
   * DC 토큰 소각 (담보 상환 준비)
   * @param {string} userAddress - 사용자 주소
   * @param {string} mnemonic - 사용자 니모닉
   * @param {number} dcAmount - 소각할 DC 수량 (base units)
   * @returns {Promise<string>} 소각 트랜잭션 ID
   */
  burnDcToken: async (userAddress, mnemonic, dcAmount) => {
    try {
      if (!ESG_GOLD_ASSET_ID) {
        throw new Error('ESG-GOLD asset ID not configured');
      }

      if (!COLLATERAL_POOL_ADDRESS) {
        throw new Error('Collateral pool address not configured');
      }

      const account = algosdk.mnemonicToSecretKey(mnemonic);
      const params = await algodClient.getTransactionParams().do();

      // DC 토큰을 Collateral Pool로 전송 (소각 처리)
      const txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
        from: account.addr,
        to: COLLATERAL_POOL_ADDRESS,
        amount: Math.floor(dcAmount),
        assetIndex: ESG_GOLD_ASSET_ID,
        suggestedParams: params,
        note: new Uint8Array(Buffer.from(`DC burn for redemption: ${dcAmount / 1_000_000} DC`)),
      });

      const signedTxn = txn.signTxn(account.sk);
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();
      await algosdk.waitForConfirmation(algodClient, txId, 4);

      console.log('DC burn successful! TxID:', txId);
      return txId;
    } catch (error) {
      console.error('Burn DC token error:', error);
      throw error;
    }
  },

  /**
   * 담보 상환 요청 (DC 소각 후 ALGO 회수)
   * @param {string} userAddress - 사용자 주소
   * @param {string} mnemonic - 사용자 니모닉
   * @param {string} collateralId - 담보 ID
   * @param {number} dcAmount - 소각할 DC 수량 (base units)
   * @returns {Promise<Object>} 상환 결과
   */
  redeemCollateral: async (userAddress, mnemonic, collateralId, dcAmount) => {
    try {
      // 1. DC 토큰 소각
      const burnTxId = await algorandService.burnDcToken(userAddress, mnemonic, dcAmount);

      // 2. 백엔드 API를 통해 ALGO 반환 요청
      const response = await fetch('/api/collateral/redeem', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userAddress,
          collateralId,
          dcAmount: dcAmount / 1_000_000, // Convert to base DC
          burnTxId
        })
      });

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'Collateral redemption failed');
      }

      console.log('Collateral redemption successful!', result);
      return {
        success: true,
        burnTxId,
        returnTxId: result.returnTxId,
        algoReturned: result.algoReturned
      };
    } catch (error) {
      console.error('Redeem collateral error:', error);
      throw error;
    }
  },

  /**
   * 담보 상태 조회
   * @param {string} userAddress - 사용자 주소
   * @returns {Promise<Object>} 담보 상태
   */
  getCollateralStatus: async (userAddress) => {
    try {
      const response = await fetch(`/api/collateral/status/${userAddress}`);
      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'Failed to get collateral status');
      }

      return result.collaterals;
    } catch (error) {
      console.error('Get collateral status error:', error);
      throw error;
    }
  },
};

export default algorandService;
