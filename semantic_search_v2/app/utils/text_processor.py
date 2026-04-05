

import re
import math



STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "need",
    "this", "that", "these", "those", "it", "its", "they", "them", "their",
    "we", "our", "you", "your", "he", "she", "his", "her", "i", "my", "me",
    "which", "who", "what", "when", "where", "how", "not", "no", "nor",
    "so", "yet", "both", "either", "neither", "each", "more", "most",
    "than", "then", "also", "just", "into", "onto", "about", "above",
    "after", "before", "between", "through", "during", "while", "if",
    "although", "because", "since", "until", "unless", "however", "therefore",
    "such", "any", "all", "some", "other", "only", "even", "very", "well",
    "one", "two", "three", "new", "use", "used", "using", "make", "like",
    "many", "much", "over", "out", "up", "down", "there", "here",
    "has", "same", "different", "including", "without", "within", "across",
    "often", "provide", "provides", "provided", "providing", "allow",
    "allows", "allowed", "require", "requires", "required",
}



def tokenize(text: str) -> list:
    """
    Convert raw text into a clean list of meaningful words.

    Pipeline:
      "AI Systems are transforming Finance!"
          ↓ lowercase
      "ai systems are transforming finance!"
          ↓ remove punctuation (keep only a-z and spaces)
      "ai systems are transforming finance"
          ↓ split by whitespace
      ["ai", "systems", "are", "transforming", "finance"]
          ↓ remove stop words + words shorter than 3 chars
      ["systems", "transforming", "finance"]

    Args:
        text: Raw document or query string
    Returns:
        List of clean, meaningful tokens
    """
   
    text = text.lower()


    text = re.sub(r"[^a-z\s]", " ", text)


    tokens = text.split()

   
    tokens = [
        t for t in tokens
        if t not in STOP_WORDS and len(t) >= 3
    ]

    return tokens



def compute_tf(tokens: list) -> dict:
    """
    Calculate Term Frequency for each word in a token list.

    Formula:  TF(word) = count(word in doc) / total words in doc

    Example:
        tokens = ["ai", "finance", "ai", "investment"]
        total  = 4
        TF("ai")         = 2/4 = 0.5
        TF("finance")    = 1/4 = 0.25
        TF("investment") = 1/4 = 0.25

    Returns:
        dict: { word -> tf_score }
    """
    if not tokens:
        return {}

    tf = {}
    total = len(tokens)

    for token in tokens:
        tf[token] = tf.get(token, 0) + 1

    
    for word in tf:
        tf[word] = tf[word] / total

    return tf


def compute_idf(all_token_lists: list) -> dict:

    total_docs = len(all_token_lists)
    doc_freq = {} 

    for tokens in all_token_lists:
        # Use set()
        for word in set(tokens):
            doc_freq[word] = doc_freq.get(word, 0) + 1

    idf = {}
    for word, df in doc_freq.items():
        idf[word] = math.log(total_docs / (1 + df))

    return idf



def compute_tfidf(tf: dict, idf: dict) -> dict:
    """
    Multiply TF × IDF to get the final weight of each word.

    TF-IDF(word, doc) = TF(word, doc) × IDF(word)

    High TF-IDF means:
    - The word appears often in THIS document (high TF)
    - AND the word is rare across ALL documents (high IDF)
    → This word truly DEFINES this document

    Low TF-IDF means the word is either rare in this doc
    or very common across all docs (like "the").

    Args:
        tf:  { word -> tf_score } for ONE document
        idf: { word -> idf_score } across ALL documents
    Returns:
        dict: { word -> tfidf_score }
    """
    tfidf = {}
    for word, tf_val in tf.items():
        # If word not in idf (shouldn't happen, but safe fallback)
        idf_val = idf.get(word, 0.0)
        score = tf_val * idf_val
        # Only keep non-zero scores (saves memory)
        if score > 0:
            tfidf[word] = score
    return tfidf


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: COSINE SIMILARITY
# ─────────────────────────────────────────────────────────────────────────────
def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """
    Compute cosine similarity between two sparse TF-IDF vectors.

    Formula:  cos(θ) = (A · B) / (|A| × |B|)

    Intuition:
    - Treat each vector as an arrow in multi-dimensional space
    - Each dimension = one unique word
    - Cosine similarity = how much the arrows point the same way
    - 1.0 = identical direction (same topic)
    - 0.0 = perpendicular (nothing in common)

    Why cosine over regular distance?
    → A long document and a short document on the same topic
      will have vectors pointing the SAME direction but different
      lengths. Cosine handles this; Euclidean distance doesn't.

    Args:
        vec_a: TF-IDF vector (dict) for document/query A
        vec_b: TF-IDF vector (dict) for document/query B
    Returns:
        float: similarity score between 0.0 and 1.0
    """
    if not vec_a or not vec_b:
        return 0.0

   
    common_words = set(vec_a.keys()) & set(vec_b.keys())

    if not common_words:
       
        return 0.0

    dot_product = sum(vec_a[w] * vec_b[w] for w in common_words)


    magnitude_a = math.sqrt(sum(v * v for v in vec_a.values()))
    magnitude_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)
