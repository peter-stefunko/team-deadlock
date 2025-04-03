import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


async def get_async_db_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = request.app.state.db_session_factory()

    try:
        yield session
    except Exception as e:
        logging.warning(e)
        await session.rollback()
        raise e
    else:
        await session.commit()
    finally:
        await session.close()
