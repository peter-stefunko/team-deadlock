from sqlalchemy import BigInteger, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.declaration import CustomDeclarativeBase


class ArticleModel(CustomDeclarativeBase):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    classification: Mapped[str] = mapped_column(String)
    credibility: Mapped[str] = mapped_column(String)
    abstract: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String)
    publisher: Mapped[str] = mapped_column(String)
    publication_id: Mapped[int] = mapped_column(BigInteger)
    source_id: Mapped[int] = mapped_column(BigInteger)
    published_at: Mapped[str] = mapped_column(String)
    scanned_at: Mapped[str] = mapped_column(String)
    trust_factor: Mapped[float] = mapped_column(Float)

    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "type": self.type,
            "classification": self.classification,
            "credibility": self.credibility,
            "abstract": self.abstract,
            "text": self.text,
            "publisher": self.publisher,
            "publication_id": self.publication_id,
            "source_id": self.source_id,
            "published_at": self.published_at,
            "scanned_at": self.scanned_at,
            "trust_factor": self.trust_factor
        }
