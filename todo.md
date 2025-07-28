

# Todos

go through the todos in the code

go through the meeting notes

---


# UI Suggestions

create a drop down for material types

create a slider for number of strands

---

## Graphs




---

## Further Experimentation

Test Reset Force After (s) + Equilibrium + The two height measurements. 

Experiment with other types of forces

Experiment with raising the num_beam_segments variable to 30 for Windows and test out a series

---

## Further Study

study beam theory a bit more

compare with other structures with the same material
figure out if there is a formula in beam theory for a single beam, of the same material, same weight
(normal robots can carry 25% of its own weight)

understand the create braided structure function better

understand _get_load_capacity_ratio_chart_values

---

## Further Work

fix the equilibrium util function

experiment with the structure: from the layer 0 layer 1 there is one distance, from layer 1 to 2 there is double distance and so on... it keeps doubling (linear, experiment with the constant, should it be half as big, double the size etc.)

experiment with, top nodes,
add torque to the top nodes, rotation, add torque to each node
add sinus to it 
forget all about all_nodes, side_nodes

consider the following below, don't have to implement
experiment that if we place 3 lines spread at 120 degrees in a circle that pull on the strands, but there are more strands, we would like to see what the shape becomes as we pull down the nodes, it pulls in the direction of the beam
what if we put the structure on its head and make it pull an object upwards


---

## Future Work

Create a Pychrono Docker setup without irrlicht but with FEA

Create a workflow that uses the Docker to test if it can run a simulation / that the codebase is still valid (?)

Websockets