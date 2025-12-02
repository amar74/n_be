"""Add notifications table

Revision ID: 20251202_add_notifications
Revises: 20251112_add_proposals
Create Date: 2025-12-02 02:12:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251202_add_notifications'
down_revision: Union[str, None] = '0d32e3791e12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create notification_type enum (if not exists)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notificationtype AS ENUM (
                'opportunity_created',
                'opportunity_stage_changed',
                'opportunity_promoted',
                'opportunity_high_value',
                'opportunity_deadline_approaching',
                'opportunity_assigned',
                'proposal_created',
                'proposal_status_changed',
                'account_created',
                'account_updated',
                'system_alert',
                'general'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create notification_priority enum (if not exists)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notificationpriority AS ENUM (
                'low',
                'medium',
                'high',
                'urgent'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create notifications table
    notification_type_enum = postgresql.ENUM(
        'opportunity_created', 'opportunity_stage_changed', 'opportunity_promoted', 
        'opportunity_high_value', 'opportunity_deadline_approaching', 'opportunity_assigned',
        'proposal_created', 'proposal_status_changed', 'account_created', 'account_updated',
        'system_alert', 'general',
        name='notificationtype',
        create_type=False
    )
    
    notification_priority_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'urgent',
        name='notificationpriority',
        create_type=False
    )
    
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('type', notification_type_enum, nullable=False),
        sa.Column('priority', notification_priority_enum, nullable=False, server_default='medium'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('related_entity_type', sa.String(50), nullable=True),
        sa.Column('related_entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('ix_notifications_id', 'notifications', ['id'])
    op.create_index('ix_notifications_org_id', 'notifications', ['org_id'])
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_related_entity_id', 'notifications', ['related_entity_id'])
    op.create_index('ix_notifications_user_unread', 'notifications', ['user_id', 'is_read', 'created_at'])
    op.create_index('ix_notifications_org_type', 'notifications', ['org_id', 'type', 'created_at'])
    
    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('preferences', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for notification_preferences
    op.create_index('ix_notification_preferences_id', 'notification_preferences', ['id'])
    op.create_index('ix_notification_preferences_user_id', 'notification_preferences', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_notifications_org_type', table_name='notifications')
    op.drop_index('ix_notifications_user_unread', table_name='notifications')
    op.drop_index('ix_notifications_related_entity_id', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_index('ix_notifications_org_id', table_name='notifications')
    op.drop_index('ix_notifications_id', table_name='notifications')
    
    op.drop_index('ix_notification_preferences_user_id', table_name='notification_preferences')
    op.drop_index('ix_notification_preferences_id', table_name='notification_preferences')
    
    # Drop tables
    op.drop_table('notification_preferences')
    op.drop_table('notifications')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS notificationpriority')
    op.execute('DROP TYPE IF EXISTS notificationtype')

