from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DataBase:
    def __init__(
        self, url, echo: bool = False, autocommit: bool = False, autoflush: bool = False
    ):
        self.url = url
        self.async_engine = create_async_engine(url=self.url)
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine, autoflush=autoflush, autocommit=autocommit
        )

    async def get_async_session(self) -> AsyncSession:
        async with self.async_session_factory() as sess:
            yield sess
