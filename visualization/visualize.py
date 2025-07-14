import pychrono as chrono
import pychrono.irrlicht as irr


def create_visualization(system, floor, braid_mesh, initial_bounds):
	visualization_mesh = chrono.ChVisualShapeFEA(braid_mesh)
	visualization_mesh.SetFEMdataType(chrono.ChVisualShapeFEA.DataType_ELEM_BEAM_TY)
	visualization_mesh.SetColorscaleMinMax(-0.5, 0.5)
	visualization_mesh.SetSmoothFaces(True)
	visualization_mesh.SetWireframe(False)
	braid_mesh.AddVisualShapeFEA(visualization_mesh)

	visualizefloor = chrono.ChVisualShapeBox(chrono.ChVector3d(5, 0.1, 5))
	visualizefloor.SetColor(chrono.ChColor(0.2, 0.2, 0.2))
	floor.AddVisualShape(visualizefloor)

	# Create a visualization system
	visualization = irr.ChVisualSystemIrrlicht()
	visualization.AttachSystem(system)
	visualization.SetWindowSize(600, 800)
	visualization.SetWindowTitle("Braid Simulation")
	visualization.SetShadows(False)
	visualization.Initialize()
	visualization.AddSkyBox()
	visualization.AddTypicalLights()

	# Set the camera position to frame the structure closely from a slightly elevated front-right angle
	center_x = (initial_bounds["min_x"] + initial_bounds["max_x"]) / 2
	center_y = (initial_bounds["min_y"] + initial_bounds["max_y"]) / 2
	center_z = (initial_bounds["min_z"] + initial_bounds["max_z"]) / 2

	size_x = initial_bounds["max_x"] - initial_bounds["min_x"]
	size_y = initial_bounds["max_y"] - initial_bounds["min_y"]
	size_z = initial_bounds["max_z"] - initial_bounds["min_z"]

	camera_target = chrono.ChVector3d(center_x, center_y, center_z)
	camera_pos = chrono.ChVector3d(center_x + size_x * 1.2, center_y + size_y * 0.7, center_z + size_z * 1.2)

	visualization.AddCamera(camera_pos, camera_target)


	return visualization
