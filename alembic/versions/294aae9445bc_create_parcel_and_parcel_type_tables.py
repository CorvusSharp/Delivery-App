"""Create parcel and parcel_type tables

Revision ID: 294aae9445bc
Revises: 
Create Date: 2025-08-27 02:55:38.217183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '294aae9445bc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "parcel_types",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=32), nullable=False, unique=True),
    )
    op.create_table(
        "parcels",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("weight", sa.Float, nullable=False),
        sa.Column("type_id", sa.Integer, sa.ForeignKey("parcel_types.id"), nullable=False),
        sa.Column("value_usd", sa.Float, nullable=False),
        sa.Column("delivery_price_rub", sa.Float, nullable=True),
        sa.Column("session_id", sa.String(length=64), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("parcels")
    op.drop_table("parcel_types")
