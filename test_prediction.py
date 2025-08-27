import sys
# This ensures that the script can find and import modules from the parent directory.
sys.path.insert(0, '.')

from models.prediction import predict_fake_news

def test_fake_news_detection():
    """
    Tests the system's ability to correctly identify a news article
    with multiple strong fake news indicators.
    """
    print("\n--- [Test 1] Testing with Obvious Fake News ---")
    headline = "SHOCKING: Scientists discover miracle cure that doctors don't want you to know about"
    content = "This incredible breakthrough will change everything. The government is hiding this secret treatment that can cure all diseases overnight. You won't believe what happens next!"
    
    result = predict_fake_news(headline, content)
    
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Explanation: {result['explanation']}")
    
    # Assertions verify that the function behaves as expected for this input.
    assert result['prediction'] == "FAKE"
    assert result['confidence'] > 0.7, "Confidence for fake news should be high."
    assert "Clickbait" in result['explanation'], "Explanation should mention clickbait."
    assert "Suspicious claims" in result['explanation'], "Explanation should mention suspicious claims."
    print("--- [Test 1] PASSED ---")

def test_real_news_detection():
    """
    Tests the system's ability to correctly identify a legitimate-sounding
    news article with no fake news indicators.
    """
    print("\n--- [Test 2] Testing with Real News ---")
    headline = "Local community center opens new facility for residents"
    content = "The community center has completed construction of its new recreation facility. The building includes a gymnasium, swimming pool, and meeting rooms for local residents."
    
    result = predict_fake_news(headline, content)
    
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Explanation: {result['explanation']}")
    
    # Assertions verify that the function behaves as expected for this input.
    assert result['prediction'] == "REAL"
    assert result['confidence'] > 0.7, "Confidence for real news should be high."
    assert "No significant issues detected" in result['explanation'], "Explanation for real news is incorrect."
    print("--- [Test 2] PASSED ---")

if __name__ == "__main__":
    try:
        test_fake_news_detection()
        test_real_news_detection()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")