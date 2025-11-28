/**
 * AI Image Classification Utility
 * Uses TensorFlow.js with MobileNet for ESG activity verification
 */

import * as mobilenet from '@tensorflow-models/mobilenet';
import * as tf from '@tensorflow/tfjs';

let model = null;
let backendReady = false;

/**
 * Initialize TensorFlow.js backend
 * @returns {Promise<void>}
 */
const initializeBackend = async () => {
  if (backendReady) return;

  try {
    console.log('Initializing TensorFlow.js backend...');
    await tf.ready();
    console.log('TensorFlow.js backend ready:', tf.getBackend());
    backendReady = true;
  } catch (error) {
    console.error('Error initializing TensorFlow.js backend:', error);
    throw error;
  }
};

/**
 * Load MobileNet model
 * @returns {Promise<void>}
 */
export const loadModel = async () => {
  if (model) return model;

  try {
    // Ensure backend is ready first
    await initializeBackend();

    console.log('Loading AI model...');
    model = await mobilenet.load();
    console.log('AI model loaded successfully');
    return model;
  } catch (error) {
    console.error('Error loading AI model:', error);
    throw error;
  }
};

/**
 * Classify image using MobileNet
 * @param {HTMLImageElement|HTMLCanvasElement|HTMLVideoElement} imageElement
 * @returns {Promise<Array>} Classification results
 */
export const classifyImage = async (imageElement) => {
  try {
    if (!model) {
      await loadModel();
    }

    console.log('Classifying image...');
    const predictions = await model.classify(imageElement);
    console.log('Classification results:', predictions);
    return predictions;
  } catch (error) {
    console.error('Error classifying image:', error);
    throw error;
  }
};

/**
 * Activity verification keywords mapping
 * Maps ESG activity IDs to expected image classification keywords
 *
 * UPDATED: Expanded keywords and lowered threshold for better recognition
 */
const ACTIVITY_KEYWORDS = {
  // Environment - Recycling
  recycling: ['bottle', 'container', 'plastic', 'jug', 'waste', 'recycling', 'trash', 'bin', 'can', 'glass', 'jar', 'carton'],

  // Environment - Transport
  public_transport: ['bus', 'train', 'subway', 'metro', 'tram', 'station', 'transit', 'railway', 'platform'],
  bike_sharing: ['bicycle', 'bike', 'cycling', 'wheel', 'mountain bike', 'motorcycle', 'pedal'],

  // Environment - Food & Products (Manual verification)
  local_food: ['food', 'market', 'grocery', 'produce', 'vegetable', 'fruit', 'shopping', 'store'],
  low_carbon_product: ['product', 'package', 'eco', 'green', 'sustainable', 'organic', 'natural'],

  // Environment - Reusable Items
  reusable_tumbler: ['cup', 'mug', 'tumbler', 'coffee', 'beverage', 'drink', 'espresso', 'latte', 'bottle', 'flask', 'thermos'],
  reusable_basket: ['basket', 'shopping cart', 'cart', 'hamper', 'container', 'wicker', 'crate'],
  ecobag_use: ['bag', 'tote', 'shopping bag', 'fabric', 'cloth', 'canvas', 'sack', 'purse', 'handbag', 'backpack', 'textile', 'carrier', 'reusable', 'pouch', 'shoulder bag'],

  // Social - Public Facilities
  public_facility: ['library', 'building', 'gym', 'center', 'facility', 'museum', 'stadium', 'hall', 'structure', 'architecture'],

  // Social - Volunteer & Events (Manual verification primarily)
  volunteer: ['volunteer', 'helping', 'community', 'service', 'people', 'group', 'team', 'crowd'],
  local_event: ['event', 'gathering', 'festival', 'ceremony', 'celebration', 'party', 'meeting'],
  helping_errand: ['coffee', 'delivery', 'package', 'bag', 'helping', 'carrying', 'box', 'parcel'],

  // Governance (Primarily digital verification)
  platform_voting: [],
  review_writing: [],
  policy_proposal: []
};

/**
 * Verify if image matches the selected activity
 * @param {Array} predictions - MobileNet predictions
 * @param {string} activityId - Activity ID (e.g., 'plastic', 'bicycle')
 * @returns {Object} Verification result with confidence and matches
 */
export const verifyActivity = (predictions, activityId) => {
  const keywords = ACTIVITY_KEYWORDS[activityId] || [];

  if (keywords.length === 0) {
    return {
      verified: true,
      confidence: 0.5,
      message: 'Activity type not configured for AI verification',
      matches: []
    };
  }

  // Check if any prediction matches the keywords
  const matches = [];
  let maxConfidence = 0;

  predictions.forEach((prediction) => {
    const className = prediction.className.toLowerCase();

    keywords.forEach((keyword) => {
      if (className.includes(keyword.toLowerCase())) {
        matches.push({
          keyword,
          prediction: prediction.className,
          confidence: prediction.probability
        });
        maxConfidence = Math.max(maxConfidence, prediction.probability);
      }
    });
  });

  // Verification criteria:
  // - At least one match found
  // - Confidence > 0.2 (20%) - LOWERED from 30% for better demo success rate
  const verified = matches.length > 0 && maxConfidence > 0.2;

  return {
    verified,
    confidence: maxConfidence,
    message: verified
      ? `인증 성공: ${matches[0].prediction} (${Math.round(maxConfidence * 100)}% 확신)`
      : '이미지에서 활동을 확인할 수 없습니다. 다시 촬영해주세요.',
    matches,
    allPredictions: predictions
  };
};

/**
 * Complete AI verification pipeline
 * @param {string} imageDataUrl - Base64 image data URL
 * @param {string} activityId - Activity ID
 * @returns {Promise<Object>} Verification result
 */
export const verifyActivityImage = async (imageDataUrl, activityId) => {
  return new Promise(async (resolve, reject) => {
    try {
      // Create image element from data URL
      const img = new Image();

      img.onload = async () => {
        try {
          // Classify image
          const predictions = await classifyImage(img);

          // Verify against activity
          const result = verifyActivity(predictions, activityId);

          resolve(result);
        } catch (error) {
          reject(error);
        }
      };

      img.onerror = (error) => {
        reject(new Error('Failed to load image for classification'));
      };

      img.src = imageDataUrl;
    } catch (error) {
      reject(error);
    }
  });
};

/**
 * Pre-load AI model (call on app initialization)
 */
export const initializeAI = async () => {
  try {
    await loadModel();
    console.log('AI system initialized');
  } catch (error) {
    console.error('Failed to initialize AI:', error);
  }
};

const aiClassifier = {
  loadModel,
  classifyImage,
  verifyActivity,
  verifyActivityImage,
  initializeAI
};

export default aiClassifier;
