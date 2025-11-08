import pychrono as chrono
import pychrono.fea as fea
import math

def create_braid_structure(braid_mesh, braid_material, tape_material, experiment_series):
	nodes = generate_nodes(braid_mesh, experiment_series)
	node_pairs = define_connectivity(nodes, experiment_series)
	beams, joints = create_beam_elements(braid_mesh, node_pairs, braid_material, tape_material)
	node_positions = [node.GetPos() for layer in nodes for node in layer]
	return nodes, node_positions, beams


def generate_nodes(braid_mesh, config):
	nodes = []
	num_intersections = config.num_strands  # strands assumed to be even
	twist_per_layer = (2 * math.pi) / (2 * num_intersections)

	for layer_no in range(int(config.num_layers)):
		layer_nodes = []
		for point_no in range(num_intersections):
			angle = layer_no * twist_per_layer + (point_no / num_intersections) * 2 * math.pi
			radius = config.radius - (layer_no * config.radius_taper)
			y = layer_no * config.pitch
			x = radius * math.cos(angle)
			z = radius * math.sin(angle)

			node = fea.ChNodeFEAxyzrot(chrono.ChFramed(chrono.ChVector3d(x, y, z)))
			if layer_no == 0:
				node.SetFixed(True)
			braid_mesh.AddNode(node)
			layer_nodes.append(node)
		nodes.append(layer_nodes)

	return nodes


def define_connectivity(nodes, config):
	node_pairs = []
	num_rods = config.num_strands

	for rod in range(num_rods):
		# counter-clockwise
		for layer_no in range(len(nodes) - 1):
			node_pairs.append(('beam', (nodes[layer_no][rod], nodes[layer_no + 1][rod])))

		# clockwise
		for layer_no in range(len(nodes) - 1):
			target = rod - 1 if rod > 0 else num_rods - 1
			node_pairs.append(('beam', (nodes[layer_no][rod], nodes[layer_no + 1][target])))

	# # Add 'joint' connections between neighboring nodes in the same layer
	# for layer_no in range(len(nodes)):
	# 	for rod in range(num_rods):
	# 		next_rod = (rod + 1) % num_rods
	# 		node_pairs.append(('joint', nodes[layer_no][rod], nodes[layer_no][next_rod]))

	# # Add diagonal tape joints between adjacent rods in adjacent layers
	# for layer_no in range(len(nodes) - 1):
	# 	for rod in range(num_rods):
	# 		next_rod = (rod + 1) % num_rods
	# 		node_pairs.append(('joint', nodes[layer_no][rod], nodes[layer_no + 1][next_rod]))

	return node_pairs


def create_beam_elements(braid_mesh, node_pairs, braid_material, tape_material):
	for pair in node_pairs:
		assert isinstance(pair, tuple), f"Not a tuple: {pair}"
		assert len(pair) in (2, 3), f"Unexpected pair length: {pair}"

	beams = []
	joints = []

	num_beam_segments = 10

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
				tape_material,
				1, # How many segments for the joint beam (braid)
				node_a,
				node_b,
				chrono.ChVector3d(0, 1, 0)
			)
			beams.extend(builder.GetLastBeamElements())

	return beams, joints