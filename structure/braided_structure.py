import pychrono as chrono
import pychrono.fea as fea
import math
from config import BraidedStructureConfig

def create_braid_structure(braid_mesh, braid_material, braided_structure_config: BraidedStructureConfig):	
	nodes = generate_nodes(braid_mesh, braided_structure_config)
	node_pairs = define_connectivity(nodes, braided_structure_config)
	beams, joints = create_beam_elements(braid_mesh, node_pairs, braid_material, braided_structure_config)
	node_positions = [node.GetPos() for layer in nodes for node in layer]
	return nodes, node_positions, beams


def generate_nodes(braid_mesh, config: BraidedStructureConfig):
	nodes = []
	for layer in range(config.num_layers):
		radius = config.radius - (layer * config.radius_taper)
		y = layer * config.pitch / config.num_layers
		layer_nodes = []

		for strand in range(config.num_strands):
			angle = (strand / config.num_strands) * 2 * math.pi + layer * (math.pi / config.num_strands)
			x = radius * math.cos(angle)
			z = radius * math.sin(angle)

			node = fea.ChNodeFEAxyzrot(chrono.ChFramed(chrono.ChVector3d(x, y, z)))
			if layer == 0:
				node.SetFixed(True)

			braid_mesh.AddNode(node)
			layer_nodes.append(node)

		nodes.append(layer_nodes)

	return nodes


def define_connectivity(nodes, config: BraidedStructureConfig):
	node_pairs = []

	for layer_no in range(len(nodes) - 1):
		current_layer = nodes[layer_no]
		next_layer = nodes[layer_no + 1]

		for strand_no in range(config.num_strands):
			vertical_pair = (current_layer[strand_no], next_layer[strand_no])
			diagonal_pair = (current_layer[strand_no], next_layer[(strand_no - 1) % config.num_strands])

			node_pairs.append(('beam', vertical_pair))
			node_pairs.append(('beam', diagonal_pair))

			# intersection joints for tape, slight compliance
			node_pairs.append(('joint', vertical_pair[1], diagonal_pair[1]))

	return node_pairs


def create_beam_elements(braid_mesh, node_pairs, braid_material, config: BraidedStructureConfig):
	for pair in node_pairs:
		assert isinstance(pair, tuple), f"Not a tuple: {pair}"
		assert len(pair) in (2, 3), f"Unexpected pair length: {pair}"

	beams = []
	joints = []

	num_beam_segments = config.num_beam_segments

	for pair_type, *nodes in node_pairs:
		if pair_type == 'beam':
			node_a, node_b = nodes[0]
			builder = fea.ChBuilderBeamEuler()
			builder.BuildBeam(
				braid_mesh,
				braid_material,
				num_beam_segments,
				node_a,
				node_b,
				chrono.ChVector3d(0, 1, 0)
			)
			beams.extend(builder.GetLastBeamElements())

		elif pair_type == 'joint':
			node_a, node_b = nodes

			# Use short compliant beam to simulate taped connection
			builder = fea.ChBuilderBeamEuler()
			builder.BuildBeam(
				braid_mesh,
				braid_material,
				1,
				node_a,
				node_b,
				chrono.ChVector3d(0, 1, 0)
			)
			beams.extend(builder.GetLastBeamElements())

	return beams, joints