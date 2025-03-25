import pychrono as chrono
import pychrono.fea as fea
import math

######################################################################################################
#### parameters for the braid ########################################################################
######################################################################################################
######################################################################################################

num_rods = 12   # has to be an even number
radius = 0.15
pitch = 1.13
num_layers = 10

# generate points
num_intersections = int(num_rods / 2)   # two rods insect at each point

######################################################################################################
######################################################################################################
######################################################################################################


def create_braided_structure(braid_mesh, braid_material):
    layers= []
    for layer_no in range(num_layers):
        current_layer = []
        for point_no in range(num_intersections):
            current_angle = layer_no*2*math.pi/(2*num_intersections) + point_no/num_intersections * 2 * math.pi
            current_point = chrono.ChVector3d(radius * math.cos(current_angle), layer_no * pitch / num_rods, radius * math.sin(current_angle))
            current_node = fea.ChNodeFEAxyzrot( chrono.ChFramed( current_point ) )       
            braid_mesh.AddNode( current_node )
            if layer_no == 0:
                current_node.SetFixed( True )  
            current_layer.append( current_node )
        layers.append( current_layer )



    topnodes = []

    for rods in range(int(num_rods/2)):

        # counter clock-wise
        builderccw = fea.ChBuilderBeamEuler()
        for layer_no in range(num_layers-1):
            builderccw.BuildBeam(braid_mesh,
                                braid_material,
                                10,
                                layers[layer_no][rods],
                                layers[layer_no+1][rods],
                                chrono.ChVector3d( 0,1,0 ) )
        
            
        # clock-wise
        buildercw = fea.ChBuilderBeamEuler()
        if rods > 0:
            for layer_no in range(0,num_layers-1):
                buildercw.BuildBeam(braid_mesh,
                                    braid_material,
                                    10,
                                    layers[layer_no][rods],
                                    layers[layer_no+1][rods-1],
                                    chrono.ChVector3d( 0,1,0 ) )
        else:
            for layer_no in range(0,num_layers-1):
                buildercw.BuildBeam(braid_mesh,
                                    braid_material,
                                    10,
                                    layers[layer_no][rods],
                                    layers[layer_no+1][int(num_rods/2)-1],
                                    chrono.ChVector3d( 0,1,0 ) )
        topnodes.append( buildercw.GetLastBeamNodes()[-1] )

        return layers, topnodes