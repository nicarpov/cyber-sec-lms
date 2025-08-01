"""cascade delete

Revision ID: b48886663b8d
Revises: 47a6f2b92351
Create Date: 2025-07-31 00:25:55.279482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b48886663b8d'
down_revision = '47a6f2b92351'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('backup', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_backup_save_id_save'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_backup_host_id_host'), type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_backup_save_id_save'), 'save', ['save_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('fk_backup_host_id_host'), 'host', ['host_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('save', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_save_lab_id_lab'), type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_save_lab_id_lab'), 'lab', ['lab_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('save', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_save_lab_id_lab'), type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_save_lab_id_lab'), 'lab', ['lab_id'], ['id'])

    with op.batch_alter_table('backup', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_backup_host_id_host'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_backup_save_id_save'), type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_backup_host_id_host'), 'host', ['host_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_backup_save_id_save'), 'save', ['save_id'], ['id'])

    # ### end Alembic commands ###
