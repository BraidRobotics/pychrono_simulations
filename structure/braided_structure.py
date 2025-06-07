import pychrono as chrono
import pychrono.fea as fea
import math
from config import BraidedStructureConfig

def create_braid_structure(braid_mesh, braid_material, braided_structure_config: BraidedStructureConfig):
    num_strands = braided_structure_config.num_strands
    radius = braided_structure_config.radius
    pitch = braided_structure_config.pitch
    num_layers = braided_structure_config.num_layers

    layers = []
    node_positions = []
    beam_elements = []

    for layer_no in range(num_layers):
        current_layer = []

        for strand_no in range(num_strands):
            # --- Angular positioning ---
            strand_fraction = strand_no / num_strands
            base_angle = strand_fraction * 2 * math.pi

            twist_per_layer = math.pi / num_strands
            layer_twist = layer_no * twist_per_layer

            current_angle = base_angle + layer_twist

            # --- 3D position ---
            x = radius * math.cos(current_angle)
            y = layer_no * pitch / num_layers
            z = radius * math.sin(current_angle)

            current_point = chrono.ChVector3d(x, y, z)

            # --- Node creation ---
            current_node = fea.ChNodeFEAxyzrot(chrono.ChFramed(current_point))
            braid_mesh.AddNode(current_node)
            node_positions.append(current_node.GetPos())

            if layer_no == 0:
                current_node.SetFixed(True)

            current_layer.append(current_node)

        layers.append(current_layer)


    top_nodes = []
    num_beam_segments = 10

    for strand in range(num_strands):
        # CCW (vertical)
        builderccw = fea.ChBuilderBeamEuler()
        for layer_no in range(num_layers - 1):
            builderccw.BuildBeam(
                braid_mesh,
                braid_material,
                num_beam_segments,
                layers[layer_no][strand],
                layers[layer_no + 1][strand],
                chrono.ChVector3d(0, 1, 0)
            )
        beam_elements.extend(builderccw.GetLastBeamElements())

        # CW (diagonal wrap)
        buildercw = fea.ChBuilderBeamEuler()
        for layer_no in range(num_layers - 1):
            target = (strand - 1) % num_strands
            buildercw.BuildBeam(
                braid_mesh,
                braid_material,
                num_beam_segments,
                layers[layer_no][strand],
                layers[layer_no + 1][target],
                chrono.ChVector3d(0, 1, 0)
            )

        top_nodes.append(buildercw.GetLastBeamNodes()[-1])
        beam_elements.extend(buildercw.GetLastBeamElements())

    return layers, top_nodes, node_positions, beam_elements


def destroy_braid_structure(braid_mesh):
    braid_mesh.ClearElements()
    braid_mesh.ClearNodes()

