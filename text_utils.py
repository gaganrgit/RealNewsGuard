import re
import string
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

# --- NLTK Setup ---
# Ensures that the required NLTK data (for tokenizing and stop words) is available.
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK data (punkt, stopwords). This is a one-time setup.")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

# --- Predefined Regex Patterns for Feature Detection ---
# These lists contain common phrases and patterns found in misleading content.
CLICKBAIT_PATTERNS = [r"you won't believe", r"mind-blowing", r"shocking", r"jaw-dropping", r"secret", r"top \d+", r"\d+ reasons", r"this is why", r"what happens next", r"doctors hate", r"one simple trick", r"incredible"]
SENSATIONALIST_PATTERNS = [r"breaking", r"urgent", r"alert", r"bombshell", r"scandal", r"explosive", r"slams", r"destroys", r"chaos", r"crisis", r"nightmare", r"devastating"]
SUSPICIOUS_CLAIM_PATTERNS = [r"scientists shocked", r"they don't want you to know", r"government is hiding", r"mainstream media won't tell you", r"cures? (cancer|covid)", r"miracle (cure|treatment)", r"big pharma", r"100% effective", r"guaranteed", r"overnight"]

def clean_text(text: str) -> str:
    """Cleans text by lowercasing, removing URLs, HTML tags, and punctuation."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def _find_patterns(text: str, patterns: list) -> list:
    """Helper function to find all occurrences of a list of regex patterns in text."""
    found = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            found.extend(matches)
    return found

def detect_clickbait(headline: str) -> tuple[bool, list]:
    """Detects if a headline uses common clickbait phrases."""
    patterns = _find_patterns(headline.lower(), CLICKBAIT_PATTERNS)
    return len(patterns) > 0, patterns

def detect_sensationalist_language(text: str) -> tuple[bool, list]:
    """Detects if text uses sensationalist or emotionally charged words."""
    patterns = _find_patterns(text.lower(), SENSATIONALIST_PATTERNS)
    return len(patterns) > 0, patterns

def detect_suspicious_claims(text: str) -> tuple[bool, list]:
    """Detects if text contains claims often associated with misinformation."""
    patterns = _find_patterns(text.lower(), SUSPICIOUS_CLAIM_PATTERNS)
    return len(patterns) > 0, patterns

def extract_keywords(text: str, top_n: int = 5) -> list:
    """
    Extracts top keywords from text using TF-IDF (Term Frequency-Inverse Document Frequency).
    This helps identify the main topics of the text.
    """
    if not text:
        return []
    try:
        cleaned_text = clean_text(text)
        if not cleaned_text.strip():
            return []
            
        vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
        tfidf_matrix = vectorizer.fit_transform([cleaned_text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        keywords = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
        keywords.sort(key=lambda x: x[1], reverse=True)
        return [kw[0] for kw in keywords[:top_n]]
    except ValueError:
        # This can occur if the text contains only stop words or is too short.
        return []