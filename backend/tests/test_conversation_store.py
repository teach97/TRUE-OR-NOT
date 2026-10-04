import asyncio
import pytest
from conversation_store import ConversationStore, StorageError


def test_missing_database_is_storage_error():
    async def run():
        with pytest.raises(StorageError, match='NOT_CONFIGURED'):
            await ConversationStore('').open()
    asyncio.run(run())


def test_db_acquisition_is_bounded_and_diagnostics_are_hidden():
    class SlowPool:
        async def acquire(self):
            await asyncio.sleep(10)
    async def run():
        store = ConversationStore('postgres://unused', timeout=.02)
        store.pool = SlowPool()
        with pytest.raises(StorageError, match='STORAGE_UNAVAILABLE'):
            async with store.connection():
                pass
    asyncio.run(run())
