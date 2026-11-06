"""BM25 retrieval with Unicode normalization and source-level evidence."""
import math
import re
import unicodedata
from collections import Counter

def tokens(text):
    normalized = unicodedata.normalize('NFKD', text.casefold())
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    return re.findall(r'\w+', normalized)

def chunks(text, size=120, overlap=25):
    words = text.split()
    for start in range(0, len(words), size-overlap):
        yield ' '.join(words[start:start+size])
        if start + size >= len(words): break

def rank(query, documents, limit=5):
    if not documents: return []
    corpus = [tokens(d['content']) for d in documents]
    avg = sum(map(len, corpus))/len(corpus)
    terms = set(tokens(query))
    results = []
    for document, words in zip(documents, corpus):
        counts = Counter(words)
        score = 0.0
        for term in terms:
            df = sum(term in row for row in corpus)
            idf = math.log(1 + (len(corpus)-df+0.5)/(df+0.5))
            tf = counts[term]
            score += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75*len(words)/max(avg, 1)))
        if score > 0:
            results.append({**document, 'score': round(score, 6)})
    return sorted(results, key=lambda d: (-d['score'], d['id']))[:limit]
