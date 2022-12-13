"""empty message

Revision ID: 782e7de4c58f
Revises: 
Create Date: 2022-12-07 21:55:35.917374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '782e7de4c58f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('business',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('business', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_business_name'), ['name'], unique=True)

    op.create_table('employee',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('firstname', sa.String(length=64), nullable=False),
    sa.Column('lastname', sa.String(length=64), nullable=False),
    sa.Column('hourly_rate', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_employee_firstname'), ['firstname'], unique=False)
        batch_op.create_index(batch_op.f('ix_employee_lastname'), ['lastname'], unique=False)

    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('shift',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('finish_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_roles')
    op.drop_table('shift')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('roles')
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_employee_lastname'))
        batch_op.drop_index(batch_op.f('ix_employee_firstname'))

    op.drop_table('employee')
    with op.batch_alter_table('business', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_business_name'))

    op.drop_table('business')
    # ### end Alembic commands ###
