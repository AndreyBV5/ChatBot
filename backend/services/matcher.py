from typing import List, Tuple, Optional
import re, unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from Levenshtein import distance as lev_distance
except Exception:
    try:
        from rapidfuzz.distance import Levenshtein as RF_Levenshtein
        lev_distance = RF_Levenshtein.distance
    except Exception:
        # Fallback mínimo
        def lev_distance(a: str, b: str) -> int:
            return abs(len(a) - len(b))

# --- Normalización básica ---
def normalize(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = s.encode("ascii", "ignore").decode("utf-8")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

class FAQMatcher:
    def __init__(self):
        self.tfidf: Optional[TfidfVectorizer] = None
        self.matrix = None
        self.questions_raw: List[str] = []
        self.questions_norm: List[str] = []
        self.faq_ids: List[int] = []

    def build(self, items: List[Tuple[int, str]]):
        """
        items: lista [(id, question), ...]
        """
        self.faq_ids = [i for i, _ in items]
        self.questions_raw = [q for _, q in items]
        self.questions_norm = [normalize(q) for q in self.questions_raw]

        if len(self.questions_norm) == 0:
            self.tfidf = None
            self.matrix = None
            return

        self.tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self.matrix = self.tfidf.fit_transform(self.questions_norm)

    def query(self, text: str, top_k=3):
        if self.tfidf is None or self.matrix is None or self.matrix.shape[0] == 0:
            return []

        q = normalize(text)
        v = self.tfidf.transform([q])
        sims = cosine_similarity(v, self.matrix)[0]

        # indices ordenados
        k = min(top_k, self.matrix.shape[0])
        idxs = sims.argsort()[::-1][:k]

        results = []
        for idx in idxs:
            fid = self.faq_ids[idx]
            score = float(sims[idx])

            # Bono difuso para tipos cercanos 
            target = self.questions_norm[idx]
            denom = max(1, len(target))
            fuzzy = 1.0 - (lev_distance(q, target) / denom)

            # Mezcla: 80% coseno + 20% fuzzy
            final = 0.8 * score + 0.2 * fuzzy
            results.append((fid, final, score, fuzzy))

        return results
