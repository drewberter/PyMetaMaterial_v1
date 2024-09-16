import pyvista as pv
from dolfinx import io
import numpy as np
import os
import matplotlib.pyplot as plt

# Check if running in headless mode
headless_mode = os.getenv("DISPLAY") is None

if headless_mode:
    pv.OFF_SCREEN = True

def plot_attenuation(frequencies, attenuation):
    """
    Plot the attenuation values as a function of frequency.
    
    Parameters:
    frequencies (list): List of frequency values.
    attenuation (list): List of attenuation values corresponding to the frequencies.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies, attenuation, marker='o', linestyle='-', color='b')
    plt.title('Attenuation vs Frequency')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Attenuation (dB)')
    plt.grid(True)
    plt.show()

def visualize_solution(mesh_obj, u_sol, frequency, dimensions):
    """
    Visualize the solution using PyVista. Supports both 2D and 3D meshes.
    
    Parameters:
        mesh_obj: FEniCSx mesh object.
        u_sol: Solution of the PDE (displacement or pressure field).
        frequency: The frequency of the wave being simulated.
        dimensions: '2D' or '3D' to specify the mesh type.
    """
    # Convert the FEniCSx mesh and solution into PyVista format
    topology, cell_types, geometry = io.extract_topology_and_geometry(mesh_obj, mesh_obj.topology.dim)
    grid = pv.UnstructuredGrid(topology, cell_types, geometry)

    # Attach the solution data to the grid
    grid["solution"] = u_sol.x.array.real

    # Create a PyVista plotter for visualization
    plotter = pv.Plotter(off_screen=headless_mode)

    # Add the mesh and plot the scalar field (displacement/pressure) as a heatmap
    plotter.add_mesh(grid, scalars="solution", show_edges=True, cmap="coolwarm", show_scalar_bar=True)

    # Adjust the camera and view settings based on 2D or 3D
    if dimensions == '2D':
        plotter.view_xy()
    elif dimensions == '3D':
        plotter.view_isometric()

    # Save the plot or display it based on headless mode
    if headless_mode:
        # Save the visualization to a file if headless
        plotter.screenshot(f'simulation_result_{frequency}Hz.png')
    else:
        # Display interactive visualization if not headless
        plotter.show()

def visualize_heatmap(mesh_obj, u_sol, frequency, sources, dimensions):
    """
    Visualize a heatmap showing the intensity of the sound field over the metamaterial surface.
    
    Parameters:
        mesh_obj: FEniCSx mesh object.
        u_sol: Solution field over the mesh.
        frequency: The frequency of the sound wave being simulated.
        sources: The sound sources positions used in the simulation.
        dimensions: '2D' or '3D' to specify the mesh type.
    """
    # Convert the mesh and solution to PyVista grid
    topology, cell_types, geometry = io.extract_topology_and_geometry(mesh_obj, mesh_obj.topology.dim)
    grid = pv.UnstructuredGrid(topology, cell_types, geometry)

    # Attach the solution data to the grid
    grid["solution"] = u_sol.x.array.real

    # Create PyVista plotter for visualization
    plotter = pv.Plotter(off_screen=headless_mode)

    # Add the solution heatmap to the plot
    plotter.add_mesh(grid, scalars="solution", show_edges=False, cmap="viridis", show_scalar_bar=True)

    # Add source markers to the plot (if provided)
    if sources:
        for source in sources:
            plotter.add_point([source['position'][0], source['position'][1], 0.0], color='red', point_size=10)

    # Adjust camera for 2D or 3D
    if dimensions == '2D':
        plotter.view_xy()
    elif dimensions == '3D':
        plotter.view_isometric()

    # Save or show the plot based on headless mode
    if headless_mode:
        plotter.screenshot(f'heatmap_result_{frequency}Hz.png')
    else:
        plotter.show()
