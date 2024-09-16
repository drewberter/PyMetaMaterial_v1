import os  # Add this line at the top of the file
from dolfinx import mesh, fem, io
from mpi4py import MPI
import ufl
import numpy as np
import pyvista as pv
from petsc4py import PETSc

# Check if running in headless mode for off-screen rendering
headless_mode = os.getenv("DISPLAY") is None
if headless_mode:
    pv.OFF_SCREEN = True

def simulate_metamaterial(mesh_data, frequencies, sources, dimensions):
    """
    Simulate the metamaterial's response to different frequencies and visualize the result.
    """
    attenuation_results = []

    # Iterate over multiple frequencies
    for freq in frequencies:
        attenuation, mesh_obj, u_sol = simulate_attenuation(mesh_data, freq, sources, dimensions)
        attenuation_results.append((freq, attenuation))
        
        # Visualize the solution after the simulation
        visualize_solution(mesh_obj, u_sol, freq, dimensions)
        visualize_heatmap(mesh_obj, u_sol, freq, sources, dimensions)

    return attenuation_results

def simulate_attenuation(mesh_data, frequency, sources, dimensions):
    """
    Perform the simulation for a specific frequency and compute the attenuation.
    """
    # Convert the user-designed mesh into a FEniCSx-compatible mesh (2D or 3D)
    mesh_obj = convert_to_fenics_mesh(mesh_data, dimensions)

    # Create function space for FEniCSx
    V = fem.FunctionSpace(mesh_obj, ("Lagrange", 1))

    # Define test and trial functions for solving PDE
    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)

    # Physical parameters for wave propagation
    c = 343  # Speed of sound in air (m/s)
    k = 2 * np.pi * frequency / c  # Wave number

    # Helmholtz equation for acoustic wave propagation
    a = ufl.dot(ufl.grad(u), ufl.grad(v)) * ufl.dx - (k ** 2) * u * v * ufl.dx
    L = fem.Constant(mesh_obj, 0.0) * v * ufl.dx

    # Solve the PDE for each sound source
    solutions = []
    for source in sources:
        u_sol = solve_pde(a, L, mesh_obj, V)
        solutions.append(u_sol)

    # Compute attenuation and return the results
    attenuation = compute_attenuation(solutions)
    return attenuation, mesh_obj, solutions[0]

def solve_pde(a, L, mesh_obj, V):
    """
    Solve the Helmholtz equation PDE using FEniCSx.
    """
    u_sol = fem.Function(V)
    problem = fem.petsc.LinearProblem(a, L, petsc_options={"ksp_type": "preonly", "pc_type": "lu"})
    return problem.solve()

def compute_attenuation(solutions):
    """
    Compute the attenuation based on the solution of the PDE.
    """
    attenuation = 0
    for solution in solutions:
        attenuation += fem.assemble_scalar(fem.form(ufl.sqrt(ufl.dot(solution, solution)) * ufl.dx))
    return 20 * np.log10(1 + attenuation)

# --- PyVista Visualization for Solutions ---

def visualize_solution(mesh_obj, u_sol, frequency, dimensions):
    """
    Visualize the solution using PyVista as a heatmap, showing how the metamaterial
    interacts with the sound wave at the given frequency. Supports both 2D and 3D.
    """
    topology, cell_types, geometry = io.extract_topology_and_geometry(mesh_obj, mesh_obj.topology.dim)
    grid = pv.UnstructuredGrid(topology, cell_types, geometry)

    # Add the solution (displacement or pressure field) as a scalar to the grid
    grid["solution"] = u_sol.x.array.real

    # Create a PyVista plotter for visualization
    plotter = pv.Plotter(off_screen=headless_mode)
    plotter.add_mesh(grid, scalars="solution", show_edges=True, cmap="coolwarm", show_scalar_bar=True)

    # Adjust the view based on whether the mesh is 2D or 3D
    if dimensions == '2D':
        plotter.view_xy()
    elif dimensions == '3D':
        plotter.view_isometric()

    # Save the plot if headless, or show the interactive plot otherwise
    if headless_mode:
        plotter.screenshot(f'simulation_result_{frequency}Hz.png')
    else:
        plotter.show()

# --- PyVista Visualization for Heatmaps ---

def visualize_heatmap(mesh_obj, u_sol, frequency, sources, dimensions):
    """
    Visualize a heatmap showing the intensity of the sound field over the metamaterial surface.
    """
    topology, cell_types, geometry = io.extract_topology_and_geometry(mesh_obj, mesh_obj.topology.dim)
    grid = pv.UnstructuredGrid(topology, cell_types, geometry)

    # Add the solution data to the grid
    grid["solution"] = u_sol.x.array.real

    # Create PyVista plotter for visualization
    plotter = pv.Plotter(off_screen=headless_mode)
    plotter.add_mesh(grid, scalars="solution", show_edges=False, cmap="viridis", show_scalar_bar=True)

    # Add source markers
    if sources:
        for source in sources:
            plotter.add_point([source['position'][0], source['position'][1], 0.0], color='red', point_size=10)

    # Adjust camera view for 2D or 3D
    if dimensions == '2D':
        plotter.view_xy()
    elif dimensions == '3D':
        plotter.view_isometric()

    # Save the plot if headless, or show the interactive plot otherwise
    if headless_mode:
        plotter.screenshot(f'heatmap_result_{frequency}Hz.png')
    else:
        plotter.show()

# --- Helper function to convert the 3D mesh ---
def convert_to_fenics_mesh(mesh_data, dimensions):
    """
    Converts user-designed 3D mesh data from the frontend into a FEniCSx-compatible mesh.
    Supports both 2D and 3D meshes.
    """
    if dimensions == '2D':
        length = mesh_data.get('length', 1.0)
        width = mesh_data.get('width', 1.0)
        resolution = mesh_data.get('resolution', [64, 64])
        mesh_obj = mesh.create_rectangle(MPI.COMM_WORLD, 
                                         [np.array([0.0, 0.0]), np.array([length, width])],
                                         resolution)
    elif dimensions == '3D':
        length = mesh_data.get('length', 1.0)
        width = mesh_data.get('width', 1.0)
        height = mesh_data.get('height', 1.0)
        resolution = mesh_data.get('resolution', [32, 32, 32])
        mesh_obj = mesh.create_box(MPI.COMM_WORLD, 
                                   [np.array([0.0, 0.0, 0.0]), np.array([length, width, height])],
                                   resolution)
    else:
        raise ValueError("Invalid dimension type. Please provide either '2D' or '3D'.")
    
    return mesh_obj
