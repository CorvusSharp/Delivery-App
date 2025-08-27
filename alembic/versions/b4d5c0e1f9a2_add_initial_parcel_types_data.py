"""Add initial parcel types data

Revision ID: b4d5c0e1f9a2
Revises: 294aae9445bc
Create Date: 2025-08-27 03:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4d5c0e1f9a2'
down_revision: Union[str, Sequence[str], None] = '294aae9445bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add initial parcel types data."""
    # Создаем подключение для выполнения SQL
    connection = op.get_bind()
    
    # Проверяем, есть ли уже данные
    result = connection.execute(sa.text("SELECT COUNT(*) FROM parcel_types"))
    count = result.scalar()
    
    if count == 0:
        # Вставляем базовые типы посылок
        connection.execute(sa.text("""
            INSERT INTO parcel_types (id, name) VALUES 
            (1, 'Clothing'),
            (2, 'Electronics'), 
            (3, 'Other')
        """))
        
        # Обновляем sequence для PostgreSQL
        connection.execute(sa.text("""
            SELECT setval('parcel_types_id_seq', (SELECT MAX(id) FROM parcel_types))
        """))


def downgrade() -> None:
    """Remove initial parcel types data."""
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM parcel_types WHERE id IN (1, 2, 3)"))
