import sys
import pychrono as chrono


def is_Mac():
    return sys.platform == 'darwin'


def setup_solver(system):
    """
    The MKL Paradiso solver is more precise for finite element analysis (FEA)
    but does not support ARM64 architecture on macOS.
    """
    if is_Mac():
        return setup_macOS_solver(system)
    else:
        return setup_non_macOS_solver(system)


def setup_macOS_solver(system):
    linear_solver = chrono.ChSolverSparseLU()
    linear_solver.LockSparsityPattern(True)
    system.SetSolver(linear_solver)

    return linear_solver


def setup_non_macOS_solver(system):
    linear_solver = chrono.pardisomkl.ChSolverPardisoMKL()
    # linear_solver.LockSparsityPattern(True)
    system.SetSolver(linear_solver)

    return linear_solver
