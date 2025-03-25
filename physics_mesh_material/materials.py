import pychrono as chrono
import pychrono.fea as fea

def create_braid_mesh():
    # Create a mesh, that is a container for groups of elements and nodes
    mesh = fea.ChMesh()
    mesh.SetAutomaticGravity(True)
    return mesh


def create_braid_material():
    # Create a material for the braid
    material_radius = 0.002
    braidmaterial = fea.ChBeamSectionEulerSimple()
    braidmaterial.SetAsCircularSection( material_radius )
    braidmaterial.SetYoungModulus( 1.72e10 ) # Glass-reinforced polyester (GRP) - https://en.wikipedia.org/wiki/Young%27s_modulus
    braidmaterial.SetDensity( 1200 )  # 1.2 g/cm^3 = 1200kg/m^3  
    #material.SetShearModulus(0.01e9 * 0.3)
    #material.SetRayleighDamping(0.000)
    return braidmaterial


def create_surface_material():
    # create material for floor
    surfacematerial = chrono.ChContactMaterialSMC()
    return surfacematerial

