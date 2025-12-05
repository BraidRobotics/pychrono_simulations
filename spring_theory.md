

# Optimal Strand Count: 4 strands

Force-to-weight ratio: 9.14 (the highest!)
Max force: 1.7N (same as 6, 8, 10 strands)
Weight: 0.186 kg (much lighter than more strands)
Sweet spot: adding more strands adds weight but doesn't increase load capacity proportionally.

It does NOT behave like a spring
4-strand structure: 
Initial stiffness: ~16 N/m (at low compression)
Peak stiffness: ~37 N/m (at medium compression, ~10-15% compression)
Final stiffness: ~25 N/m (at high compression, ~17% compression)

The stiffness increases by 2.3x as you compress it, then softens again. This is called progressive stiffening followed by softening. 8-strand structure (stiffer):
Initial stiffness: ~104 N/m
Peak stiffness: ~226 N/m (at ~5% compression)
Final stiffness: ~207 N/m (at ~10% compression)


# Optimal Layer Count: As small as possible

As layers increase from 2 -> 8:
Weight scales linearly: Almost perfectly proportional to layer count (0.079 kg -> 0.555 kg)
Max force decreases: From 2.0N (2 layers) down to 0.89N (8 layers)
Force-to-weight ratio drops dramatically: 25.22 -> 1.61
More failures with more layers: 2-layer has 0 failures, 8-layer has 26/48 failures

Surprising insight: Taller structures (more layers) are weaker per unit weight. The structure becomes less efficient as it gets taller.

# Strand Thickness Experiments

Experiment series: strand_thickness__002 through strand_thickness__008
These experiments test the effect of varying strand thickness on spring performance.
(Renamed from material_thickness to strand_thickness for clarity)

# Insights

Your structures likely show:
Buckling transitions (sudden softening when critical load is reached)
Geometric effects (braids can compress, strands can reorient, contacts can slip)

