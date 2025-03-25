import pychrono as chrono

def setup_system():
    # Create a Chrono physical system
    system = chrono.ChSystemSMC()
    system.SetCollisionSystemType( chrono.ChCollisionSystem.Type_BULLET )
    return system
