import pychrono as chrono

def create_floor(system, surface_material):
    floor = chrono.ChBodyEasyBox(5, 0.1, 5, 2700, True, True, surface_material)
    floor.SetFixed(True)
    floor.SetPos(chrono.ChVector3d(0, -0.1, 0))
    system.Add(floor)

    return floor
