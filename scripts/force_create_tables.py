from sqlalchemy import insert, text
from core.db import sync_engine, Base
import adapters.db.models  # ensure models are registered

def main():
    print('Using sync_engine:', sync_engine.url)
    with sync_engine.begin() as conn:  # type: ignore
        print('Calling create_all...')
        Base.metadata.create_all(bind=conn)
        print('create_all finished')
        # insert test row if not exists
        try:
            res = conn.execute(text("SELECT COUNT(*) FROM parcel_types WHERE name='test';"))
            cnt = res.scalar()
        except Exception:
            cnt = 0
        if not cnt:
            print('Inserting test row into parcel_types')
            conn.execute(insert(adapters.db.models.ParcelType).values(name='test'))
        else:
            print('Test row already exists')

if __name__ == '__main__':
    main()
