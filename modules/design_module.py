import numpy as np

def design_metamaterial(freq_min, freq_max, material):
    # Material properties (example values)
    materials = {
        'Silicone Rubber': {'density': 1100, 'youngs_modulus': 0.01e9},
        'Polyurethane': {'density': 1200, 'youngs_modulus': 0.05e9}
    }
    
    material_props = materials.get(material, {})
    
    if not material_props:
        raise ValueError(f"Material {material} not found. Available materials: {list(materials.keys())}")
    
    # Frequencies to design for
    frequencies = np.linspace(freq_min, freq_max, 10)
    
    # Calculate resonator dimensions for each frequency
    dimensions = []
    for f in frequencies:
        dimension = calculate_helmholtz_resonator(f)
        dimensions.append(dimension)
        
    return dimensions

def calculate_helmholtz_resonator(frequency):
    c = 343  # Speed of sound in air (m/s)
    A = 1e-4  # Neck area in m^2 (example value)
    L_eff = 0.05  # Effective neck length in m (example value)
    V = (A) / ((2 * np.pi * frequency / c)**2 * L_eff)
    
    # Return dimensions as a dictionary
    return {
        'frequency': frequency, 
        'volume': V, 
        'neck_area': A, 
        'neck_length': L_eff
    }
