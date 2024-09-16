from flask import Flask, request, jsonify
from modules.simulation_module import simulate_metamaterial

app = Flask(__name__)

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    mesh_data = data['mesh']
    frequencies = data['frequencies']
    sources = data['sources']
    
    # Run simulation
    results = simulate_metamaterial(mesh_data, frequencies, sources)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
