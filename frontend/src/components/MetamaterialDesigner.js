import React, { useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Sphere, Plane, Box, useTexture } from '@react-three/drei';

const MetamaterialDesigner = () => {
  const [meshData, setMeshData] = useState([]);
  const [selectedShape, setSelectedShape] = useState('sphere');

  // Handle adding shapes
  const addShape = () => {
    const newShape = {
      type: selectedShape,
      position: [Math.random() * 2, Math.random() * 2, 0], // Random positions
    };
    setMeshData([...meshData, newShape]);
  };

  // Handle sending mesh data to the backend
  const sendMeshToBackend = async () => {
    const response = await fetch('http://localhost:5000/simulate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mesh: meshData,
        frequencies: [200, 500, 1000],  // Example frequencies
        sources: [{ x: 0, y: 0 }, { x: 1, y: 1 }],  // Example sound sources
      }),
    });

    const result = await response.json();
    console.log('Simulation Result:', result);
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Left side panel for shape options and controls */}
      <div style={{ flex: 1, padding: '20px', background: '#f5f5f5' }}>
        <h2>Design Metamaterial</h2>
        <select onChange={(e) => setSelectedShape(e.target.value)} value={selectedShape}>
          <option value="sphere">Sphere</option>
          <option value="box">Box</option>
        </select>
        <button onClick={addShape}>Add Shape</button>
        <button onClick={sendMeshToBackend}>Run Simulation</button>
        <h3>Current Mesh Data:</h3>
        <pre>{JSON.stringify(meshData, null, 2)}</pre>
      </div>

      {/* Canvas for 3D rendering */}
      <div style={{ flex: 3 }}>
        <Canvas>
          <ambientLight intensity={0.5} />
          <OrbitControls />
          {/* Render the shapes dynamically based on the meshData */}
          {meshData.map((shape, index) =>
            shape.type === 'sphere' ? (
              <Sphere key={index} position={shape.position} args={[0.2, 32, 32]}>
                <meshStandardMaterial color="skyblue" />
              </Sphere>
            ) : (
              <Box key={index} position={shape.position} args={[0.3, 0.3, 0.3]}>
                <meshStandardMaterial color="orange" />
              </Box>
            )
          )}
          <Plane args={[10, 10]} rotation-x={-Math.PI / 2} position={[0, -0.5, 0]} />
        </Canvas>
      </div>
    </div>
  );
};

export default MetamaterialDesigner;
