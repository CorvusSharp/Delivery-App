import asyncio
from core.db import AsyncSessionLocal
from repositories.parcel import ParcelRepository
from domain.services import ParcelService

async def test():
    async with AsyncSessionLocal() as db:
        repo = ParcelRepository(db)
        service = ParcelService(repo)
        
        # Тестируем получение посылок для главной сессии
        parcels = await service.list_parcels('581283af-2523-4a2d-9dd2-1ec8eabf5ac0')
        print(f'Parcels count: {len(parcels)}')
        if parcels:
            print(f'First parcel: id={parcels[0].id}, type={parcels[0].type}')

asyncio.run(test())
