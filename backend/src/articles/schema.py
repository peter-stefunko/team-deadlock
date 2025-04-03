from src.core.schema import APIModel

class Article(APIModel):
    id: int
    title: str
    url: str
    type: str
    classification: str
    credibility: str
    abstract: str
    publisher: str
    publication_id: int
    source_id: int
    published_at: str | None
    scanned_at: str
    trust_factor: float

class Stats(APIModel):
    count: int
