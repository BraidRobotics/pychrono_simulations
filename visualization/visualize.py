import pychrono as chrono
import pychrono.fea as fea
import pychrono.irrlicht as irr

def create_visualization(system, floor, braided_mesh, node_positions):
    # create visualization for mesh
    visualization_mesh = chrono.ChVisualShapeFEA(braided_mesh)
    visualization_mesh.SetFEMdataType(chrono.ChVisualShapeFEA.DataType_ELEM_BEAM_TY)
    visualization_mesh.SetColorscaleMinMax(-0.5, 0.5)
    visualization_mesh.SetSmoothFaces(True)
    visualization_mesh.SetWireframe(False)
    braided_mesh.AddVisualShapeFEA(visualization_mesh)

    visualizefloor = chrono.ChVisualShapeBox(chrono.ChVector3d(5, 0.1, 5))
    visualizefloor.SetColor(chrono.ChColor(0.2, 0.2, 0.2))
    floor.AddVisualShape(visualizefloor)

    # Create a visualization system
    visualization = irr.ChVisualSystemIrrlicht()
    visualization.AttachSystem(system)
    visualization.SetWindowSize(600, 800)
    visualization.SetWindowTitle("Biaxial Braid Simulation")
    visualization.SetShadows(False)
    visualization.Initialize()
    visualization.AddSkyBox()
    visualization.AddTypicalLights()

    visualization.AddCamera(chrono.ChVector3d(0.5, 1.2, 0.5), chrono.ChVector3d(0, 0.5, 0))
    # center, size = compute_mesh_bounds_from_positions(node_positions)
    # camera_pos = chrono.ChVector3d(center.x + 2 * size.x, center.y + size.y, center.z * size.z)
    # camera_target = chrono.ChVector3d(center.x, center.y + 0.1 * size.y, center.z)
    # visualization.AddCamera(camera_pos, camera_target)

    return visualization


def compute_mesh_bounds_from_positions(positions):
	bbox_min = chrono.ChVector3d(1e30, 1e30, 1e30)
	bbox_max = chrono.ChVector3d(-1e30, -1e30, -1e30)

	for pos in positions:
		bbox_min = chrono.ChVector3d(
			min(bbox_min.x, pos.x),
			min(bbox_min.y, pos.y),
			min(bbox_min.z, pos.z)
		)
		bbox_max = chrono.ChVector3d(
			max(bbox_max.x, pos.x),
			max(bbox_max.y, pos.y),
			max(bbox_max.z, pos.z)
		)

	center = (bbox_min + bbox_max) * 0.5
	size = bbox_max - bbox_min
	return center, size




