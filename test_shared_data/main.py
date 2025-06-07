from shared_config import braided_structure_config
from start_server import start_server


start_server()

while True:
    snapshot = braided_structure_config.get_snapshot()
    if snapshot["rebuild_requested"]:
        braided_structure_config.update(rebuild_requested=False)
        print("Rebuilding braid structure...")
        print(braided_structure_config.num_strands)
