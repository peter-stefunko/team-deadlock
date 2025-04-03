from fastapi import APIRouter, Depends

from src.articles.crud import ArticlesCRUD, get_articles_crud
from src.embeddings.crud import EmbeddingsCRUD, get_embeddings_crud

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


@router.get("/generate")
async def generate_embeddings(
    limit: int = 10,
    embeddings_crud: EmbeddingsCRUD = Depends(get_embeddings_crud),
):
    if limit <= 0:
        return {"message": "Limit cannot be 0."}
    (
        article_ids,
        article_texts,
    ) = await embeddings_crud.get_unprocessed_articles(limit=limit)

    text_embeddings = embeddings_crud.generate_embeddings_batch(
        data=article_texts
    )
    if not article_ids:
        return {"message": "No new articles to process."}
    await embeddings_crud.insert_embeddings_batch(
        article_ids, text_embeddings
    )
    return {
        "message": f"""Embeddings generated successfully
            for {len(article_ids)} articles."""
    }


@router.get("/stats")
async def get_stats(
    embeddings_crud: EmbeddingsCRUD = Depends(get_embeddings_crud),
    articles_crud: ArticlesCRUD = Depends(get_articles_crud),
):
    embeddings_count = await embeddings_crud.get_embeddings_count()
    articles_count = await articles_crud.get_articles_count()
    missing_embeddings = articles_count - embeddings_count

    return {
        "count": embeddings_count,
        "missing": missing_embeddings,
    }

