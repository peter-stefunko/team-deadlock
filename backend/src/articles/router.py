from datetime import datetime

from fastapi import APIRouter, Depends

from src.articles.crud import ArticlesCRUD, get_articles_crud
from src.articles.models import ArticleModel
from src.articles.schema import Article, Stats
from src.embeddings.crud import EmbeddingsCRUD, get_embeddings_crud

router = APIRouter(prefix="/articles", tags=["articles"])


def parse_iso_datetime(dt: str) -> datetime:
    return datetime.fromisoformat(dt.replace("Z", "+00:00"))


@router.get("/generate_random_input")
async def generate_random_inout(
    embeddings_crud: EmbeddingsCRUD = Depends(get_embeddings_crud),
):
    return {"query": embeddings_crud.generate_random_inout()}


@router.get("/search", response_model=list[Article])
async def search_articles(
    query: str | None = None,
    cat: str | None = None,
    tp: str | None = None,
    cls: str | None = None,
    pub_ids: str | None = None,
    start_dt: str | None = None,
    end_dt: str | None = None,
    articles_crud: ArticlesCRUD = Depends(get_articles_crud),
    embeddings_crud: EmbeddingsCRUD = Depends(get_embeddings_crud),
) -> list[ArticleModel]:
    classifications = cls.split(",") if cls else None
    categories = cat.split(",") if cat else None
    publication_ids = (
        [int(id) for id in pub_ids.split(",")] if pub_ids else None
    )
    start_date = parse_iso_datetime(start_dt) if start_dt else None

    end_date = parse_iso_datetime(end_dt) if end_dt else None
    if end_date:
        end_date = end_date.replace(hour=23, minute=59, second=59)

    transformed_query = await embeddings_crud.sentence_transformer(
        query=query, categories=categories
    )

    query_embedding = embeddings_crud.generate_single_embedding(
        text=transformed_query
    )
    embeddings = await embeddings_crud.closest_embeddings(
        embedding=query_embedding, limit=100
    )

    return await articles_crud.get_articles(
        article_ids=[embedding.article_id for embedding in embeddings],
        type=tp,
        classifications=classifications,
        pub_ids=publication_ids,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/grabber")
async def article_grabber(
    limit: int = 10,
    articles_crud: ArticlesCRUD = Depends(get_articles_crud),
):
    init_count = await articles_crud.get_articles_count()
    await articles_crud.fetch_newsmatics_articles(
        limit=limit, init_count=init_count * 10000
    )


@router.get("/stats", response_model=Stats)
async def get_stats(
    articles_crud: ArticlesCRUD = Depends(get_articles_crud),
) -> Stats:
    articles_count = await articles_crud.get_articles_count()

    return Stats(count=articles_count)


@router.post("/not_trusted")
async def not_trusted(
    article_id: int,
    articles_crud: ArticlesCRUD = Depends(get_articles_crud),
    embeddings_crud: EmbeddingsCRUD = Depends(get_embeddings_crud),
):
    article = await articles_crud.set_trusted(article_id, False)
    embedding = await embeddings_crud.get_embedding_by_article(
        article.id
    )
    closest_embeddings = await embeddings_crud.closest_embeddings(
        embedding=embedding.embedding,
        limit=15,
        similarity_threshold=0.9,
    )
    for embedding in closest_embeddings:
        await articles_crud.set_trusted(
            embedding.article_id, False, multiplier=0.02
        )


@router.post("/trusted")
async def trusted(
    article_id: int,
    articles_crud: ArticlesCRUD = Depends(get_articles_crud),
    embeddings_crud: EmbeddingsCRUD = Depends(get_embeddings_crud),
):
    article = await articles_crud.set_trusted(article_id, True)
    embedding = await embeddings_crud.get_embedding_by_article(
        article.id
    )
    closest_embeddings = await embeddings_crud.closest_embeddings(
        embedding=embedding.embedding,
        limit=15,
        similarity_threshold=0.9,
    )
    for embedding in closest_embeddings:
        await articles_crud.set_trusted(
            embedding.article_id, True, multiplier=0.02
        )
