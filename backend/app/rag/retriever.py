from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
import re


KNOWLEDGE_SOURCE = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "knowledge"
    / "environmental_guidance.md"
)

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)?")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "water",
    "with",
}


@dataclass(frozen=True)
class KnowledgeChunk:
    category: str
    title: str
    source: str
    url: str
    text: str


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_PATTERN.findall(text.lower())
        if token not in STOP_WORDS
    ]


def _parse_knowledge_source(path: Path = KNOWLEDGE_SOURCE) -> list[KnowledgeChunk]:
    sections = re.split(r"^##\s+(.+)$", path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    chunks: list[KnowledgeChunk] = []

    for index in range(1, len(sections), 2):
        title = sections[index].strip()
        body = sections[index + 1].strip()
        source_match = re.search(r"^Source:\s*(.+)$", body, re.MULTILINE)
        url_match = re.search(r"^URL:\s*(\S+)$", body, re.MULTILINE)
        guidance = re.sub(r"^(Source|URL):.*$", "", body, flags=re.MULTILINE).strip()

        if not source_match or not url_match or not guidance:
            continue

        paragraphs = [paragraph.strip() for paragraph in guidance.split("\n\n") if paragraph.strip()]
        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            chunks.append(
                KnowledgeChunk(
                    category=title.lower(),
                    title=title,
                    source=source_match.group(1).strip(),
                    url=url_match.group(1).strip(),
                    text=paragraph,
                )
            )

    if not chunks:
        raise ValueError(f"No knowledge chunks found in {path}")

    return chunks


def _tfidf_vectors(chunks: list[KnowledgeChunk]) -> tuple[list[dict[str, float]], dict[str, float]]:
    tokenized = [_tokens(chunk.text) for chunk in chunks]
    document_frequency = Counter(
        token
        for tokens in tokenized
        for token in set(tokens)
    )
    document_count = len(chunks)
    idf = {
        token: 1.0 + (document_count / (1 + frequency))
        for token, frequency in document_frequency.items()
    }

    vectors: list[dict[str, float]] = []
    for tokens in tokenized:
        counts = Counter(tokens)
        total = max(len(tokens), 1)
        vectors.append(
            {
                token: (count / total) * idf[token]
                for token, count in counts.items()
            }
        )

    return vectors, idf


def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    numerator = sum(value * right.get(key, 0.0) for key, value in left.items())
    left_norm = sqrt(sum(value * value for value in left.values()))
    right_norm = sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


class TfidfRetriever:
    def __init__(self, source_path: Path = KNOWLEDGE_SOURCE):
        self.chunks = _parse_knowledge_source(source_path)
        self.vectors, self.idf = _tfidf_vectors(self.chunks)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, object]]:
        query_tokens = _tokens(query)
        query_counts = Counter(query_tokens)
        query_total = max(len(query_tokens), 1)
        query_vector = {
            token: (count / query_total) * self.idf[token]
            for token, count in query_counts.items()
            if token in self.idf
        }

        scored = [
            (_cosine_similarity(query_vector, vector), chunk)
            for chunk, vector in zip(self.chunks, self.vectors)
        ]
        scored.sort(key=lambda item: item[0], reverse=True)

        results = []
        for score, chunk in scored[: max(top_k, 0)]:
            if score <= 0:
                continue
            results.append(
                {
                    "category": chunk.category,
                    "title": chunk.title,
                    "source": chunk.source,
                    "url": chunk.url,
                    "text": chunk.text,
                    "relevance": round(score, 4),
                }
            )
        return results


retriever = TfidfRetriever()


def retrieve_knowledge(query: str, top_k: int = 3) -> list[dict[str, object]]:
    """Retrieve source-attributed guidance using local TF-IDF vectors."""

    return retriever.retrieve(query, top_k=top_k)


def retrieve_environmental_guidance(
    air_input: dict,
    water_input: dict,
    waste_input: dict,
) -> dict[str, object]:
    """Retrieve one relevant knowledge chunk for each environmental domain."""

    queries = [
        f"air quality AQI {air_input['aqi']} risk health pollution",
        f"water quality pH {water_input['ph']} acidic basic measurement",
        (
            f"dissolved oxygen {water_input['dissolved_oxygen']} aquatic organisms "
            "water quality temperature decomposition"
        ),
        f"turbidity {water_input['turbidity']} water clarity suspended material",
        (
            f"waste litter management count {waste_input['litter_count']} "
            f"severe cleanup reuse recycling disposal"
        ),
    ]

    context = []
    seen = set()
    for query in queries:
        for result in retrieve_knowledge(query, top_k=1):
            key = (result["title"], result["text"])
            if key not in seen:
                context.append(result)
                seen.add(key)

    sources = []
    seen_sources = set()
    for item in context:
        source_key = (item["source"], item["url"])
        if source_key not in seen_sources:
            sources.append({"name": item["source"], "url": item["url"]})
            seen_sources.add(source_key)

    return {
        "enabled": True,
        "method": "local_tfidf_cosine",
        "context": context,
        "sources": sources,
    }
