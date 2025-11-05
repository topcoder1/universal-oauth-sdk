"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255)),
        sa.Column('stripe_customer_id', sa.String(255), unique=True),
        sa.Column('subscription_status', sa.String(50), server_default='trialing'),
        sa.Column('plan', sa.String(50), server_default='starter'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_tenants_email', 'tenants', ['email'])
    
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('key_prefix', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('last_used_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_api_keys_key_hash', 'api_keys', ['key_hash'])
    
    # Create tokens table
    op.create_table(
        'tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('access_token_encrypted', sa.Text, nullable=False),
        sa.Column('refresh_token_encrypted', sa.Text),
        sa.Column('token_type', sa.String(50), server_default='Bearer'),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('scope', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('last_refreshed_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_tokens_tenant_key', 'tokens', ['tenant_id', 'key'], unique=True)
    op.create_index('ix_tokens_expires_at', 'tokens', ['expires_at'])
    
    # Create webhooks table
    op.create_table(
        'webhooks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('events', postgresql.ARRAY(sa.String), server_default="{'token.refreshed','token.expired'}"),
        sa.Column('secret', sa.String(255)),
        sa.Column('enabled', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('webhooks')
    op.drop_table('tokens')
    op.drop_table('api_keys')
    op.drop_table('tenants')
