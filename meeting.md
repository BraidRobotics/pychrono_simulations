
### Pages

Be able to replay specific experiments (visualizations).

---

# UI Suggestions

create a drop down for material types

create a slider for number of strands

create a way to select what nodes to apply pressure to and how much

---

## Graphs

compare with other structures with the same material
figure out if there is a formula in beam theory for a single beam, of the same material, same weight
(normal robots can carry 25% of its own weight)



Force vs. Final Height
a graph, with (each?) directional force applied on the x axis and the final height at equilibrium

Deformation Stability
a graph with equilibrium_after_seconds on the x axis and the height final height

Elastic Recovery
a graph with height_under_load on the x axis and the final_height on the y axis








---

## Further Work

fix the equilibrium util function

experiment with the structure: from the layer 0 layer 1 there is one distance, from layer 1 to 2 there is double distance and so on... it keeps doubling (linear, experiment with the constant, should it be half as big, double the size etc.)

study beam theory a bit more

experiment with, top nodes,
add torque to the top nodes, rotation, add torque to each node
add sinus to it 
forget all about all_nodes, side_nodes

create a weightToForce util method that is able to take a desired weight and it should convert it to force applied

consider the following below, don't have to implement
experiment that if we place 3 lines spread at 120 degrees in a circle that pull on the strands, but there are more strands, we would like to see what the shape becomes as we pull down the nodes, it pulls in the direction of the beam
what if we put the structure on its head and make it pull an object upwards


