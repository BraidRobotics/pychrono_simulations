"""initial

Revision ID: 430271c97400
Revises: 
Create Date: 2025-07-10 04:34:43.891720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '430271c97400'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('experiment_series',
    sa.Column('experiment_series_name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('num_experiments', sa.Integer(), nullable=True),
    sa.Column('max_simulation_time', sa.Float(), nullable=True),
    sa.Column('bounding_box_volume_threshold', sa.Float(), nullable=True),
    sa.Column('beam_strain_threshold', sa.Float(), nullable=True),
    sa.Column('node_velocity_threshold', sa.Float(), nullable=True),
    sa.Column('initial_force_applied_in_y_direction', sa.Float(), nullable=True),
    sa.Column('final_force_in_y_direction', sa.Float(), nullable=True),
    sa.Column('initial_force_applied_in_x_direction', sa.Float(), nullable=True),
    sa.Column('final_force_in_x_direction', sa.Float(), nullable=True),
    sa.Column('initial_force_applied_in_z_direction', sa.Float(), nullable=True),
    sa.Column('final_force_in_z_direction', sa.Float(), nullable=True),
    sa.Column('torsional_force', sa.Float(), nullable=True),
    sa.Column('num_strands', sa.Integer(), nullable=True),
    sa.Column('num_layers', sa.Integer(), nullable=True),
    sa.Column('radius', sa.Float(), nullable=True),
    sa.Column('pitch', sa.Float(), nullable=True),
    sa.Column('radius_taper', sa.Float(), nullable=True),
    sa.Column('material_thickness', sa.Float(), nullable=True),
    sa.Column('material_youngs_modulus', sa.Float(), nullable=True),
    sa.Column('weight_kg', sa.Float(), nullable=True),
    sa.Column('height_m', sa.Float(), nullable=True),
    sa.Column('is_experiments_outdated', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('experiment_series_name'),
    sa.UniqueConstraint('experiment_series_name')
    )
    op.create_table('experiments',
    sa.Column('experiment_id', sa.Integer(), nullable=False),
    sa.Column('experiment_series_name', sa.String(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('force_in_x_direction', sa.Float(), nullable=True),
    sa.Column('force_in_y_direction', sa.Float(), nullable=True),
    sa.Column('force_in_z_direction', sa.Float(), nullable=True),
    sa.Column('torsional_force', sa.Float(), nullable=True),
    sa.Column('time_to_bounding_box_explosion', sa.Float(), nullable=True),
    sa.Column('max_bounding_box_volume', sa.Float(), nullable=True),
    sa.Column('time_to_beam_strain_exceed_explosion', sa.Float(), nullable=True),
    sa.Column('max_beam_strain', sa.Float(), nullable=True),
    sa.Column('time_to_node_velocity_spike_explosion', sa.Float(), nullable=True),
    sa.Column('max_node_velocity', sa.Float(), nullable=True),
    sa.Column('final_height', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['experiment_series_name'], ['experiment_series.experiment_series_name'], ),
    sa.PrimaryKeyConstraint('experiment_id')
    )


def downgrade() -> None:
    op.drop_table('experiments')
    op.drop_table('experiment_series')
