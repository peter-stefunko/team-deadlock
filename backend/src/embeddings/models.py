from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.declaration import CustomDeclarativeBase


class EmbeddingModel(CustomDeclarativeBase):
    __tablename__ = "embeddings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda _: str(uuid4)
    )
    article_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(dim=1536), nullable=False
    )
