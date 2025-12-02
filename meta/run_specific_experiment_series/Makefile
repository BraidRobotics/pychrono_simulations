.PHONY: help force_no_force material_thickness layers strands all

# Default target
help:
	@echo "Available targets:"
	@echo "  make force_no_force      - Run all force_no_force experiment series"
	@echo "  make material_thickness  - Run all material_thickness experiment series"
	@echo "  make layers              - Run all number_of_layers experiment series"
	@echo "  make strands             - Run all number_of_strands experiment series"
	@echo "  make all                 - Run all experiment series (force_no_force, material_thickness, layers, strands)"
	@echo ""
	@echo "Note: Each script includes a 90-second sleep between experiment series"

# Run force_no_force experiments
force_no_force:
	@echo "Running force_no_force experiment series..."
	python3 run_force_no_force.py

# Run material_thickness experiments
material_thickness:
	@echo "Running material_thickness experiment series..."
	python3 run_material_thickness.py

# Run number_of_layers experiments
layers:
	@echo "Running number_of_layers experiment series..."
	python3 run_number_of_layers.py

# Run number_of_strands experiments
strands:
	@echo "Running number_of_strands experiment series..."
	python3 run_number_of_strands.py

# Run all experiment series sequentially
all: force_no_force material_thickness layers strands
	@echo ""
	@echo " All experiment series completed!"
