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
};

export default algorandService;
