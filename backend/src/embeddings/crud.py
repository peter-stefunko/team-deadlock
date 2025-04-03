import uuid
from typing import AsyncGenerator

import tiktoken
from fastapi import Depends
from openai import OpenAI
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models import ArticleModel
from src.core.db.session import get_async_db_session
from src.core.settings import settings
from src.embeddings.models import EmbeddingModel


async def get_embeddings_crud(
    db: AsyncSession = Depends(get_async_db_session),
) -> AsyncGenerator["EmbeddingsCRUD", None]:
    yield EmbeddingsCRUD(db)


class EmbeddingsCRUD:
    def __init__(self, db: AsyncSession):
        self.token_limit = 4000
        self.db = db
        self.client = OpenAI(api_key=settings.openai_token)
        self.encoding = tiktoken.encoding_for_model(
            "text-embedding-ada-002"
        )

    async def get_embedding_by_article(
        self, article_id: int
    ) -> EmbeddingModel:
        res = await self.db.execute(
            select(EmbeddingModel).where(
                EmbeddingModel.article_id == article_id
            )
        )
        return res.scalars().first()

    def generate_random_inout(self) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": ("You generate a single, unique, and unpredictable search query, try to make it look human and ask about anything interesting like you would be asking the web, also. output ONLY the search query, and nothing else. (Max 50 characters)"),
                }
            ],
        )
        return response.choices[0].message.content.strip()

    def generate_single_embedding(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text,
            encoding_format="float",
        )
        return response.data[0].embedding

    async def closest_embeddings(
        self,
        embedding: list[float],
        limit: int = 100,
        similarity_threshold: float = 0.68,
    ) -> list[EmbeddingModel]:
        embedding_parsed = str(list(map(float, embedding)))

        cosine_similarity_sql = "1 - (embedding <=> :query_embedding)"

        res = await self.db.execute(
            select(
                EmbeddingModel,
                text(
                    f"{cosine_similarity_sql} AS similarity"
                ),
            )
            .where(
                text(f"{cosine_similarity_sql} >= :threshold")
            )
            .order_by(
                text(f"{cosine_similarity_sql} DESC")
            )
            .limit(limit)
            .params(
                query_embedding=embedding_parsed,
                threshold=similarity_threshold,
            )
        )

        return res.scalars().all()

    async def sentence_transformer(
        self, query: str | None, categories: list[str] | None
    ) -> str:
        chat_response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You are a sentence transformer. Convert the user's search query into a concise and clear query optimal for searching relevant articles. Enhance the query with additional relevant context and correct any spelling mistakes."
                    + f" Only show the results of the articles which correspond with the user selected categories: {', '.join(categories)}"
                    if categories
                    else "",
                },
                {"role": "user", "content": query},
            ],
        )
        transformed_query = chat_response.choices[
            0
        ].message.content.strip()
        return transformed_query

    async def get_unprocessed_articles(self, limit: int = 10):
        res = await self.db.execute(
            select(ArticleModel)
            .where(
                ArticleModel.id.notin_(
                    select(EmbeddingModel.article_id)
                )
            )
            .limit(limit)
        )
        unprocessed_articles = res.scalars().all()
        article_ids = []
        article_texts = []
        for article in unprocessed_articles:
            tokens = self.encoding.encode(article.text)
            if article.text == "":
                article_ids.append(article.id)
                article_texts.append(article.title)
            elif len(tokens) > self.token_limit:
                for i in range(0, len(tokens), self.token_limit):
                    article_ids.append(article.id)
                    chunk = self.encoding.decode(
                        tokens[i : i + self.token_limit]
                    )
                    article_texts.append(chunk)
            else:
                article_ids.append(article.id)
                article_texts.append(article.text)
        return article_ids, article_texts

    def generate_embeddings_batch(
        self, data: list[str]
    ) -> list[list[float]]:
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=data,
            encoding_format="float",
        )
        return [item.embedding for item in response.data]

    async def insert_embeddings_batch(
        self, article_ids: list[int], embeddings: list[list[float]]
    ) -> None:
        embedding_models = [
            EmbeddingModel(
                id=str(uuid.uuid4()),
                article_id=article_id,
                embedding=embedding,
            )
            for article_id, embedding in zip(article_ids, embeddings)
        ]
        self.db.add_all(embedding_models)
        await self.db.commit()

    async def get_embeddings_count(self) -> int:
        query = select(func.count()).select_from(EmbeddingModel)
        res = await self.db.execute(query)
        return res.scalar()
