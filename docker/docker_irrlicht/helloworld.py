import os
import pychrono as chrono
import pychrono.irrlicht as chronoirr

system = chrono.ChSystemNSC()
vis = chronoirr.ChVisualSystemIrrlicht(system)
vis.SetWindowSize(800, 600)
vis.SetWindowTitle("Hello Chrono")
vis.AddTypicalLights()
vis.AddSkyBox()
vis.Initialize()


if "DISPLAY" not in os.environ:
    print("⚠️ Headless environment detected — skipping visualization")
    exit(1)

if not vis.Run():
    print("❌ Visualization could not start — likely DISPLAY issue")
    exit(1)

while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()
    system.DoStepDynamics(1 / 100.0)