import pychrono as chrono
import pychrono.irrlicht as irr


def create_visualization(system, floor, braid_mesh, initial_bounds):
	# create visualization for mesh
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

	# Set the camera position dynamically
	center_x = (initial_bounds["min_x"] + initial_bounds["max_x"]) / 2
	center_y = (initial_bounds["min_y"] + initial_bounds["max_y"]) / 2
	center_z = (initial_bounds["min_z"] + initial_bounds["max_z"]) / 2

	camera_target = chrono.ChVector3d(center_x, center_y, center_z)
	camera_pos = chrono.ChVector3d(center_x + 0.4, center_y + 0.8, center_z + 0.4)

	visualization.AddCamera(camera_pos, camera_target)


	return visualization

