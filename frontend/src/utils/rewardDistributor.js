/**
 * ESG Activity Reward Distributor
 * Handles automatic token distribution for verified ESG activities
 */

import algosdk from 'algosdk';

// Algorand TestNet configuration
const ALGOD_SERVER = 'https://testnet-api.algonode.cloud';
const ALGOD_PORT = '';
const ALGOD_TOKEN = '';

/**
 * Get Algod client
 */
const getAlgodClient = () => {
  return new algosdk.Algodv2(ALGOD_TOKEN, ALGOD_SERVER, ALGOD_PORT);
};

/**
 * Platform ESG-GOLD Token Configuration
 * In production, this would be a single token ID managed by the platform
 * For demo, we'll use the user's token if available
 */
const PLATFORM_TOKEN_CONFIG = {
  name: 'ESG-GOLD',
  unitName: 'ESGOLD',
  decimals: 2
};

/**
 * Distribute reward to user wallet
 *
 * Note: In production, this would:
 * 1. Use a smart contract (PyTeal Application)
 * 2. Verify activity proof on-chain
 * 3. Transfer from platform reward pool
 * 4. Record activity in smart contract state
 *
 * For demo purposes:
 * - We'll create a note transaction to record the activity
 * - Simulate reward distribution (actual tokens would come from platform pool)
 *
 * @param {Object} wallet - User wallet object with mnemonic
 * @param {Object} activityRecord - Verified activity record
 * @returns {Promise<Object>} Transaction result
 */
export const distributeReward = async (wallet, activityRecord) => {
  try {
    const algodClient = getAlgodClient();
    const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);

    // Get suggested transaction parameters
    const params = await algodClient.getTransactionParams().do();

    // Create activity record as a note (proof of activity)
    const activityProof = {
      type: 'ESG_ACTIVITY',
      category: activityRecord.category,
      activityId: activityRecord.activityId,
      activityName: activityRecord.activityName,
      reward: activityRecord.reward,
      timestamp: activityRecord.timestamp,
      location: {
        lat: activityRecord.location.latitude,
        lng: activityRecord.location.longitude
      },
      verified: activityRecord.verified,
      aiConfidence: activityRecord.aiConfidence
    };

    const noteText = JSON.stringify(activityProof);
    const note = new Uint8Array(Buffer.from(noteText, 'utf-8'));

    // For demo: Create a self-payment transaction with activity proof in note
    // In production, this would be a token transfer from platform pool
    const txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
      from: account.addr,
      to: account.addr,
      amount: 0, // 0 ALGO payment (just recording activity)
      note: note,
      suggestedParams: params
    });

    // Sign transaction
    const signedTxn = txn.signTxn(account.sk);

    // Send transaction
    console.log('Submitting activity proof transaction...');
    const { txId } = await algodClient.sendRawTransaction(signedTxn).do();

    console.log('Transaction ID:', txId);

    // Wait for confirmation
    const confirmedTxn = await algosdk.waitForConfirmation(
      algodClient,
      txId,
      4
    );

    console.log('Activity recorded on-chain at round:', confirmedTxn['confirmed-round']);

    return {
      success: true,
      txId: txId,
      round: confirmedTxn['confirmed-round'],
      message: 'Activity recorded on blockchain'
    };

  } catch (error) {
    console.error('Error distributing reward:', error);
    throw error;
  }
};

/**
 * Create ESG-GOLD token for user (if not exists)
 * In production, users would opt-in to platform token instead
 *
 * @param {Object} wallet - User wallet object
 * @returns {Promise<number>} Asset ID of created token
 */
export const createUserToken = async (wallet) => {
  try {
    const algodClient = getAlgodClient();
    const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);
    const params = await algodClient.getTransactionParams().do();

    // Create ESG-GOLD token
    const txn = algosdk.makeAssetCreateTxnWithSuggestedParamsFromObject({
      from: account.addr,
      total: 1000000 * 100, // 1,000,000 tokens with 2 decimals
      decimals: PLATFORM_TOKEN_CONFIG.decimals,
      assetName: PLATFORM_TOKEN_CONFIG.name,
      unitName: PLATFORM_TOKEN_CONFIG.unitName,
      assetURL: 'https://pam-talk.com/esg-gold',
      manager: account.addr,
      reserve: account.addr,
      freeze: account.addr,
      clawback: account.addr,
      defaultFrozen: false,
      suggestedParams: params,
      note: new Uint8Array(Buffer.from('ESG-GOLD token for ESG activities', 'utf-8'))
    });

    const signedTxn = txn.signTxn(account.sk);
    const { txId } = await algodClient.sendRawTransaction(signedTxn).do();

    console.log('Token creation tx:', txId);

    const confirmedTxn = await algosdk.waitForConfirmation(
      algodClient,
      txId,
      4
    );

    const assetId = confirmedTxn['asset-index'];
    console.log('ESG-GOLD token created with ID:', assetId);

    // Update wallet with token ID
    const updatedWallet = {
      ...wallet,
      esgGoldAssetId: assetId
    };

    localStorage.setItem('algorand_wallet', JSON.stringify(updatedWallet));

    return assetId;

  } catch (error) {
    console.error('Error creating token:', error);
    throw error;
  }
};

/**
 * Mint reward tokens to user balance
 * Simulates platform rewarding user
 *
 * @param {Object} wallet - User wallet
 * @param {number} amount - Reward amount (in tokens, will be converted to base units)
 * @returns {Promise<Object>} Transaction result
 */
export const mintRewardTokens = async (wallet, amount) => {
  try {
    // In production, platform would transfer from reserve
    // For demo, we simulate minting by recording the reward amount
    console.log(`Minting ${amount} ESGOLD tokens to user`);

    // Update local balance tracking
    const currentBalance = parseFloat(localStorage.getItem('esg_gold_balance') || '0');
    const newBalance = currentBalance + amount;
    localStorage.setItem('esg_gold_balance', newBalance.toString());

    return {
      success: true,
      amount: amount,
      newBalance: newBalance
    };

  } catch (error) {
    console.error('Error minting tokens:', error);
    throw error;
  }
};

/**
 * Complete reward distribution flow
 * 1. Check wallet exists
 * 2. Check ESG-GOLD token exists (create if needed)
 * 3. Record activity on-chain
 * 4. Mint reward tokens
 *
 * @param {Object} activityRecord - Verified activity record
 * @returns {Promise<Object>} Complete reward result
 */
export const processActivityReward = async (activityRecord) => {
  try {
    // Get wallet
    const walletData = localStorage.getItem('algorand_wallet');
    if (!walletData) {
      throw new Error('No wallet found. Please create a wallet first.');
    }

    const wallet = JSON.parse(walletData);

    // Check if user has ESG-GOLD token
    if (!wallet.esgGoldAssetId) {
      console.log('Creating ESG-GOLD token for user...');
      const assetId = await createUserToken(wallet);
      wallet.esgGoldAssetId = assetId;
    }

    // Record activity on blockchain
    console.log('Recording activity on blockchain...');
    const blockchainResult = await distributeReward(wallet, activityRecord);

    // Mint reward tokens
    console.log('Minting reward tokens...');
    const mintResult = await mintRewardTokens(wallet, activityRecord.reward);

    return {
      success: true,
      txId: blockchainResult.txId,
      round: blockchainResult.round,
      reward: activityRecord.reward,
      newBalance: mintResult.newBalance,
      message: `Successfully rewarded ${activityRecord.reward} ESGOLD tokens!`
    };

  } catch (error) {
    console.error('Error processing reward:', error);
    throw error;
  }
};

const rewardDistributor = {
  distributeReward,
  createUserToken,
  mintRewardTokens,
  processActivityReward
};

export default rewardDistributor;
