import pychrono as chrono
import pychrono.fea as fea

def create_braid_mesh():
    # Create a mesh, that is a container for groups of elements and nodes
    mesh = fea.ChMesh()
    mesh.SetAutomaticGravity(True)
    return mesh


def create_strand_material(young_modulus, material_thickness):
    braid_material = fea.ChBeamSectionEulerSimple()
    braid_material.SetAsCircularSection(material_thickness)

    braid_material.SetYoungModulus(young_modulus) # Glass-reinforced polyester (GRP) - https://en.wikipedia.org/wiki/Young%27s_modulus
    braid_material.SetDensity(1200)  # 1.2 g/cm^3 = 1200kg/m^3  
    
    #braid_material.SetShearModulus(0.01e9 * 0.3)
    braid_material.SetRayleighDamping(0.03)
    
    return braid_material


def create_tape_material():
    tape_material = fea.ChBeamSectionEulerSimple()
    tape_material.SetAsCircularSection(0.001)
    tape_material.SetYoungModulus(1e4)
    tape_material.SetDensity(1200)
    tape_material.SetRayleighDamping(0.03)
    return tape_material


def create_floor_material():
    floor_material = chrono.ChContactMaterialSMC()
    return floor_material

