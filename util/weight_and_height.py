def calculate_model_weight(beam_elements, braid_material):
	total_weight_newtons = 0
	GRAVITY_EARTH = 9.81  # m/s^2

	area = braid_material.GetArea()
	density = braid_material.GetDensity()

	print(f"{'Material density:':25} {density:.2f} kg/m³")
	print(f"{'Cross-sectional area:':25} {area:.8f} m²")

	total_length = 0
	for element in beam_elements:
		try:
			posA = element.GetNodeA().GetPos()
			posB = element.GetNodeB().GetPos()
			length = (posB - posA).Length()
			total_length += length
			total_weight_newtons += density * area * length * GRAVITY_EARTH
		except Exception as error:
			print("Error in calculate_model_weight. Skipping:", type(element), error)

	print(f"{'Total beam length:':25} {total_length:.4f} m")
	print(f"{'Total weight (N):':25} {total_weight_newtons:.6f} N")

	total_weight_kilograms = total_weight_newtons / GRAVITY_EARTH
	print(f"{'Total mass (kg):':25} {total_weight_kilograms:.6f} kg")

	return total_weight_kilograms


def calculate_model_height(beam_elements):
	positions = []

	for element in beam_elements:
		positions.append(element.GetNodeA().GetPos())
		positions.append(element.GetNodeB().GetPos())


	xs = [p.x for p in positions]

	height = max(xs) - min(xs)

	return height