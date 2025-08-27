import asyncio
from adapters.db.session import get_db
from adapters.db.repositories.parcel import SQLAlchemyParcelRepository
from application.parcel_service import ParcelService

async def test():
    async for db in get_db():
        repo = SQLAlchemyParcelRepository(db)
        service = ParcelService(repo)
        
        # Тестируем получение посылок для главной сессии
        parcels = await service.list_parcels('581283af-2523-4a2d-9dd2-1ec8eabf5ac0')
        print(f'Parcels count: {len(parcels)}')
        if parcels:
            # parcels теперь список словарей
            print(f'First parcel: id={parcels[0]["id"]}, type={parcels[0]["type"]}')
        break  # Выходим после первой итерации

asyncio.run(test())
