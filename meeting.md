## Experiment UI



should I keep the config classes with default values so that I can still run main and run_experiments directly?


### Pages

1. Experiment overview page
I can see all experiments in a searchable table

2. I can see the experiment config data including, the graphs for that experiment (use a nice JS graph library)
I should have a way to "redo the experiment" that deletes the data, keeps the config and does them over, this is useful as I expand the SQLITE schema

3. Create new experiment page, must fill out the required values (experiment name)
 I can setup my own experiment, all config should be able to be defined there. 
The config should be displayed in an editable table on the page. 
The experiment data should also be in a table (non-editable of course). 
As I run the experiments I could consider piping the python output to the frontend (nice to have), I could update how many experiments have been conducted (progress line) or I could have a toast that is called once all the experiments have been completed. 
The latter two, I could achieve either by quering the SQLITE db (count rows for that experiment) or I could use websockets (or other?).

Be able to select config values from an existing experiment when creating a new experiment
be able to edit config values but a warning should appear the discrepency OR better, it should just redo the experiment

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

create graph, with force applied on the x axis and the final height at equilibrium

create a graph, payload to weight ratio before it explodes
normal robots can carry 25% of its own weight

create an equilibrium util function

create a graph, height in y, x is amount of strands and the force would be constant

material thickness: graph, x thickness, y height

---

## Experiment

isItDeterministic
run the same experiment with the same config twice
create a small test to see if the simulation is deterministic, run one experiment 10 times and see if I get the same result

---

## Further Work

refactor create braided structure function

create a describe the braided structure function (height of strands, each beam, etc.)

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


