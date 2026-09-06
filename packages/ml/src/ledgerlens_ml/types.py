"""Plain data passed between pipeline stages. No ORM here; the pipeline maps these to rows."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Box:
    page: int
    x0: float
    y0: float
    x1: float
    y1: float

    def as_list(self) -> list[float]:
        return [self.page, self.x0, self.y0, self.x1, self.y1]


@dataclass
class Candidate:
    value: str | None
    probability: float


@dataclass
class ExtractedField:
    name: str
    value: str | None
    raw_confidence: float
    boxes: list[Box] = field(default_factory=list)
    alternatives: list[Candidate] = field(default_factory=list)
    line_index: int | None = None
    stability: float | None = None


@dataclass
class ExtractionResult:
    fields: list[ExtractedField]
    raw_output: dict[str, object]
    latency_ms: int

    def as_labels(self) -> dict[str, object]:
        from ledgerlens_ml.baseline import labels_from_fields

        return labels_from_fields(self.fields)


@dataclass
class OcrWord:
    text: str
    box: Box
    score: float


@dataclass
class OcrResult:
    words: list[OcrWord]
    page_sizes: dict[int, tuple[int, int]]
