import random
import urllib.parse
from datetime import datetime
from typing import AsyncGenerator, List

import requests
from fastapi import Depends
from sqlalchemy import DateTime, and_, cast, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from src.articles.models import ArticleModel
from src.core.db.session import get_async_db_session
from src.core.settings import settings


async def get_articles_crud(
    db: AsyncSession = Depends(get_async_db_session),
) -> AsyncGenerator["ArticlesCRUD", None]:
    yield ArticlesCRUD(db)


class ArticlesCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def insert_articles(self, articles: list[ArticleModel]):
        stmt = insert(ArticleModel).values(
            [article.dict() for article in articles]
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        await self.db.execute(stmt)
        await self.db.commit()

    async def fetch_newsmatics_articles(
        self,
        limit: int = 1000,
        page_after: int | None = None,
        init_count: int = 0,
        added_count: int = 0,
    ):
        if added_count >= limit:
            print("Limit has been reached")
            return

        params = {"include-text": "1", "page[size]": 1000}

        if page_after:
            params["page[after]"] = page_after

        headers = {
            "Authorization": f"Bearer {settings.newsmatics_api_token}"
        }

        response = requests.get(
            settings.newsmatics_api_base,
            params=params,
            headers=headers,
        )

        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])

            if not articles:
                print("No articles found. Stopping recursion.")
                return

            articles_data = [
                ArticleModel(
                    id=article.get("id"),
                    title=article.get("title"),
                    url=article.get("url"),
                    type=article.get("type"),
                    classification=article.get("classification"),
                    credibility=article.get("credibility"),
                    abstract=article.get("abstract"),
                    publisher=article.get("publisher"),
                    publication_id=article.get("publication_id"),
                    source_id=article.get("source_id"),
                    published_at=article.get("published_at"),
                    scanned_at=article.get("scanned_at"),
                    text=article.get("text"),
                    trust_factor=random.random(),
                )
                for article in articles
                if article.get("text") != ""
            ]

            await self.insert_articles(articles_data)

            after = await self.get_articles_count()

            next_page_after = (
                urllib.parse.parse_qs(
                    urllib.parse.urlparse(url).query
                ).get("page[after]", [None])[0]
                if (url := data.get("pagination", {}).get("next"))
                else None
            )

            if next_page_after:
                print(
                    f"Fetching next page after ID: {next_page_after}"
                )
                await self.fetch_newsmatics_articles(
                    limit=limit,
                    page_after=next_page_after,
                    init_count=init_count,
                    added_count=(after - init_count) * 10000,
                )
            else:
                print("No new articles found. Stopping.")

        else:
            print(
                "API request failed:",
                response.status_code,
                response.text,
            )

    async def get_articles(
        self,
        article_ids: List[int],
        type: str | None = None,
        classifications: List[str] | None = None,
        pub_ids: List[int] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> List[ArticleModel]:
        query = select(ArticleModel)

        filters = []

        if type:
            filters.append(ArticleModel.type == type)

        if classifications or pub_ids or start_date or end_date:
            sub_filters = []

            if classifications:
                sub_filters.append(
                    or_(
                        *[
                            func.replace(
                                func.lower(
                                    ArticleModel.classification
                                ),
                                "'t ",
                                "-",
                            )
                            == class_
                            for class_ in classifications
                        ]
                    )
                )

            if pub_ids:
                sub_filters.append(
                    or_(
                        *[
                            ArticleModel.publication_id == pub_id
                            for pub_id in pub_ids
                        ]
                    )
                )

            filters.append(or_(*sub_filters))

        if start_date:
            filters.append(
                cast(
                    coalesce(
                        ArticleModel.published_at,
                        ArticleModel.scanned_at,
                    ),
                    DateTime,
                )
                >= start_date
            )

        if end_date:
            filters.append(
                cast(
                    coalesce(
                        ArticleModel.published_at,
                        ArticleModel.scanned_at,
                    ),
                    DateTime,
                )
                <= end_date
            )

        if filters:
            query = query.filter(and_(*filters))

        query = query.filter(ArticleModel.id.in_(article_ids))

        query = query.limit(limit)

        res = await self.db.execute(query)

        return res.scalars().all()

    async def get_articles_count(self) -> int:
        query = select(func.count()).select_from(ArticleModel)
        res = await self.db.execute(query)
        return res.scalar()

    async def set_trusted(
        self, article_id: int, trusted: bool, multiplier: float = 0.05
    ):
        res = await self.db.execute(
            select(ArticleModel).where(ArticleModel.id == article_id)
        )
        article = res.scalar_one_or_none()
        if article:
            if not trusted:
                article.trust_factor = max(
                    0, article.trust_factor * (1.0 - multiplier)
                )
            else:
                article.trust_factor = min(
                    article.trust_factor * (1.0 + multiplier), 1
                )
        await self.db.flush()
        await self.db.refresh(article)
        return article
