from typing import List, Tuple
import re, unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein

# --- Normalización básica ---
def normalize(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = s.encode("ascii", "ignore").decode("utf-8")  # quita tildes
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

class FAQMatcher:
    def __init__(self):
        self.tfidf = None
        self.matrix = None
        self.questions_raw: List[str] = []
        self.questions_norm: List[str] = []
        self.faq_ids: List[int] = []

    def build(self, items: List[Tuple[int, str]]):
        """
        items: lista [(id, question), ...]
        """
        self.faq_ids = [i for i,_ in items]
        self.questions_raw = [q for _,q in items]
        self.questions_norm = [normalize(q) for q in self.questions_raw]
        self.tfidf = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        self.matrix = self.tfidf.fit_transform(self.questions_norm)

    def query(self, text: str, top_k=3):
        if not self.matrix or not self.tfidf:
            return []
        q = normalize(text)
        v = self.tfidf.transform([q])
        sims = cosine_similarity(v, self.matrix)[0]
        # indices ordenados
        idxs = sims.argsort()[::-1][:top_k]
        results = []
        for idx in idxs:
            fid = self.faq_ids[idx]
            score = float(sims[idx])
            # Bônus difuso para typos cercanos
            fuzzy = 1.0 - (Levenshtein.distance(q, self.questions_norm[idx]) / max(1,len(self.questions_norm[idx])))
            final = 0.8*score + 0.2*fuzzy
            results.append((fid, final, score, fuzzy))
        return results
