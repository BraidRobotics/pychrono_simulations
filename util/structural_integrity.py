import pychrono.fea as fea


def check_braid_failure(braid_mesh, failure_threshold=0.1):
    """
    Check if the braid has failed due to excessive strain or stress.

    Parameters:
    - braid_mesh: The mesh representing the braid structure.
    - failure_threshold: The maximum allowable strain or stress before failure (default 0.1).

    Returns:
    - True if the braid is broken (failure detected), False otherwise.
    """


    for beam in braid_mesh.GetElements():  # Iterate over all beams
        # Access beam's internal force or displacement
        internal_force = beam.GetInternalForce()  # Gets internal force vector (force per segment)
        displacement = beam.GetDisplacement()    # Gets the displacement at the beam node
        
        # Calculate stress or strain (simple approach, can be refined)
        stress = internal_force.Length() / beam.GetSection().GetArea()  # Stress = Force / Area
        strain = displacement.Length() / beam.GetLength()  # Strain = Displacement / Length
        
        # Print values to check if they seem reasonable
        print(f"Beam ID: {beam.GetID()} | Force: {internal_force.Length()} | Stress: {stress} | Displacement: {displacement.Length()} | Strain: {strain}")
        
        # If strain or stress exceeds threshold, we consider it as 'failure'
        if strain > failure_threshold or stress > failure_threshold:
            print(f"Failure detected in beam {beam.GetID()} with strain {strain} and stress {stress}")
            return True  # The braid has broken

    return False  # No failure detected
