from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.models import Base


class DatabaseManager:
    """
    Owns database engine and session lifecycle.

    Responsibilities:
    - Create async SQLAlchemy engine
    - Provide async session factory
    - Handle startup/shutdown
    """

    def __init__(
        self,
        database_url: str,
        echo: bool = False,
    ) -> None:
        self._database_url = database_url
        self._echo = echo

        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    async def startup(self) -> None:
        """
        Initialize database engine and session factory.
        """
        if self._engine is not None:
            return

        self._engine = create_async_engine(
            self._database_url,
            echo=self._echo,
            future=True,
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def shutdown(self) -> None:
        """
        Dispose database engine.
        """
        if self._engine is None:
            return

        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    # ---------------------------------------------------------
    # Session access
    # ---------------------------------------------------------

    def session(self) -> AsyncSession:
        """
        Create and return a new AsyncSession.
        """
        if self._session_factory is None:
            raise RuntimeError("DatabaseManager not started")

        return self._session_factory()

    async def create_tables(self) -> None:
        if self._engine is None:
            raise RuntimeError("DatabaseManager not started")

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)