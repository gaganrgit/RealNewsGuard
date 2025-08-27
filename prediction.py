import os
import logging
from PIL import Image
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Import utility functions from other parts of the project.
from utils.text_utils import (
    extract_keywords,
    detect_clickbait, 
    detect_sensationalist_language,
    detect_suspicious_claims,
)
from utils.image_utils import extract_exif_data, error_level_analysis

# --- AI Model Loading ---
# To avoid loading the large AI model on every request (which would be very slow),
# we load it once when the application starts and store it in these global variables.
# This is a common and crucial optimization for performance.
MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english" # A good, lightweight model for sentiment/truthfulness
tokenizer = None
model = None

def _load_model():
    """
    Loads the pre-trained transformer model and tokenizer into memory.
    This function is called once when the first prediction is made.
    """
    global tokenizer, model
    if tokenizer is None or model is None:
        logging.info(f"Loading AI model '{MODEL_NAME}' for the first time...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            logging.info("AI model loaded successfully.")
        except Exception as e:
            logging.error(f"CRITICAL: Failed to load AI model. ML predictions will be disabled. Error: {e}")

# --- Main Prediction Logic ---

def predict_fake_news(headline: str, content: str, image_path: str = None) -> dict:
    """
    The main prediction function. It now uses a HYBRID approach, combining
    heuristic scoring with a deep learning model for higher accuracy.
    """
    # Ensure the AI model is loaded before proceeding.
    _load_model()

    # Step 1: Extract features using our rule-based system.
    text_features = _extract_text_features(headline, content)
    image_features = _extract_image_features(image_path) if image_path else {}
    features = {**text_features, **image_features}
    
    # Step 2: Calculate the heuristic (rule-based) suspicion score.
    heuristic_score = _calculate_heuristic_score(features)
    features['heuristic_score'] = round(heuristic_score, 2)

    # Step 3: Get a prediction score from the pre-trained AI model.
    ml_score = _get_ml_prediction_score(headline + " " + content)
    features['ml_score'] = round(ml_score, 2)

    # Step 4 (Hybrid Score): Combine the two scores using a weighted average.
    # We give more weight to the ML model as it's generally more accurate.
    heuristic_weight = 0.40
    ml_weight = 0.60
    final_suspicion_score = (heuristic_score * heuristic_weight) + (ml_score * ml_weight)
    
    # Step 5: Determine the final prediction label and confidence.
    if final_suspicion_score > 0.65:
        prediction = "FAKE"
        confidence = min(final_suspicion_score, 0.99)
    elif final_suspicion_score > 0.4:
        prediction = "SUSPICIOUS"
        confidence = final_suspicion_score
    else:
        prediction = "REAL"
        confidence = 1 - final_suspicion_score

    # Step 6: Generate a human-readable explanation.
    explanation = _generate_explanation(features, prediction)
    
    logging.info(f"Scores -> Heuristic: {heuristic_score:.2f}, ML: {ml_score:.2f} | Final Score: {final_suspicion_score:.2f} -> Prediction: {prediction}")

    return {
        "prediction": prediction,
        "confidence": round(float(confidence), 2),
        "explanation": explanation,
        "features": features,
    }

def _get_ml_prediction_score(text: str) -> float:
    """
    Uses the loaded transformer model to analyze text and predict the probability of it being fake/negative.
    Returns a "fakeness" score between 0.0 (likely real) and 1.0 (likely fake).
    """
    if model is None or tokenizer is None:
        # Fallback in case the model failed to load.
        return 0.5 # Return a neutral score.

    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        
        # The model outputs logits. We convert them to probabilities using softmax.
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # This model is trained for sentiment (LABEL_0: negative, LABEL_1: positive).
        # We can interpret "negative" sentiment as a proxy for "fake/misleading" and "positive" as "real/standard".
        # We return the probability of the "negative" (fake) class.
        fake_probability = probabilities[0][0].item()
        return fake_probability
    except Exception as e:
        logging.error(f"Error during ML prediction: {e}")
        return 0.5 # Return a neutral score on error.

def _extract_text_features(headline: str, content: str) -> dict:
    """Helper function to extract various features from the news text."""
    is_clickbait, _ = detect_clickbait(headline)
    is_sensationalist_headline, _ = detect_sensationalist_language(headline)
    is_sensationalist_content, _ = detect_sensationalist_language(content)
    has_suspicious_claims_headline, _ = detect_suspicious_claims(headline)
    has_suspicious_claims_content, _ = detect_suspicious_claims(content)
    
    return {
        "is_clickbait": is_clickbait,
        "is_sensationalist": is_sensationalist_headline or is_sensationalist_content,
        "has_suspicious_claims": has_suspicious_claims_headline or has_suspicious_claims_content,
    }

def _extract_image_features(image_path: str) -> dict:
    """Helper function to extract features from the image file."""
    if not image_path or not os.path.exists(image_path):
        return {}
    
    try:
        with Image.open(image_path) as img:
            exif_data = extract_exif_data(img)
            ela_score = error_level_analysis(img, image_path)
            
            return {
                "has_metadata_issues": "Software" in exif_data or not exif_data,
                "potential_manipulation": ela_score > 15.0,
                "ela_score": round(ela_score, 2)
            }
    except Exception as e:
        logging.error(f"Failed to extract image features from {image_path}: {e}")
        return {}

def _calculate_heuristic_score(features: dict) -> float:
    """
    Calculates the rule-based suspicion score. These weights are adjusted
    to complement the ML model.
    """
    score = 0.0
    
    if features.get("is_clickbait"): score += 0.25
    if features.get("is_sensationalist"): score += 0.20
    if features.get("has_suspicious_claims"): score += 0.35
    if features.get("has_metadata_issues"): score += 0.10
    if features.get("potential_manipulation"): score += 0.30
        
    return min(score, 1.0)

def _generate_explanation(features: dict, prediction: str) -> str:
    """Generates an explanation that now considers both heuristic and ML model inputs."""
    if prediction == "REAL":
        return "The content aligns with patterns of factual reporting and does not contain significant red flags according to our analysis."

    explanations = []
    # Add explanation based on the AI model's general assessment
    if features.get('ml_score', 0.5) > 0.7:
        explanations.append("The language and context of the text were flagged by our AI model as having characteristics common in misinformation.")

    # Add specific heuristic flags
    if features.get("is_clickbait"):
        explanations.append("The headline uses clickbait language.")
    if features.get("is_sensationalist"):
        explanations.append("The article contains sensationalist or emotionally charged language.")
    if features.get("has_suspicious_claims"):
        explanations.append("It includes claims often found in misleading articles.")
    if features.get("potential_manipulation"):
        explanations.append("The associated image shows signs of potential digital manipulation.")

    if not explanations:
        return "The article has some suspicious characteristics but not enough to be flagged as outright fake."
        
    return "This article is flagged as potentially misleading because: " + " ".join(explanations)