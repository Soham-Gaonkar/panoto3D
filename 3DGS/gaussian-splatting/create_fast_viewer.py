#!/usr/bin/env python3
"""
Fast 3D Gaussian Splatting Viewer Generator
Creates a lightweight, fast-loading interactive web viewer
"""

import numpy as np
import json
import os
from pathlib import Path

def load_ply_fast(ply_path, max_points=5000):
    """Load PLY file with reduced point count for fast viewing"""
    try:
        from plyfile import PlyData
        
        print(f"Loading PLY file: {ply_path}")
        plydata = PlyData.read(ply_path)
        vertex = plydata['vertex']
        
        # Extract coordinates
        x = np.array(vertex['x'])
        y = np.array(vertex['y'])
        z = np.array(vertex['z'])
        
        total_points = len(x)
        print(f"Total points in file: {total_points:,}")
        
        # Sample points for fast loading
        if total_points > max_points:
            print(f"Sampling {max_points:,} points for fast loading...")
            indices = np.random.choice(total_points, max_points, replace=False)
            x = x[indices]
            y = y[indices] 
            z = z[indices]
        
        positions = np.column_stack((x, y, z))
        
        # Extract colors if available
        colors = None
        field_names = vertex.data.dtype.names
        
        if 'red' in field_names:
            r = np.array(vertex['red'])
            g = np.array(vertex['green'])
            b = np.array(vertex['blue'])
            
            if total_points > max_points:
                r = r[indices]
                g = g[indices]
                b = b[indices]
            
            colors = np.column_stack((r, g, b))
            print(f"Colors loaded: RGB values")
        
        return {
            'positions': positions,
            'colors': colors,
            'num_points': len(positions),
            'original_points': total_points
        }
        
    except Exception as e:
        print(f"Error loading PLY file: {e}")
        return None

def create_fast_viewer(model_data, output_path="fast_viewer.html"):
    """Create a fast-loading web viewer"""
    if not model_data or 'positions' not in model_data:
        print("No valid model data available")
        return False
    
    positions = model_data['positions']
    colors = model_data['colors']
    
    # Convert to JSON for JavaScript
    points_data = []
    for i, pos in enumerate(positions):
        point = {
            'x': float(pos[0]),
            'y': float(pos[1]),
            'z': float(pos[2])
        }
        if colors is not None:
            color = colors[i]
            point['r'] = int(color[0])
            point['g'] = int(color[1])
            point['b'] = int(color[2])
        points_data.append(point)
    
    # Calculate center and scale
    center = np.mean(positions, axis=0)
    scale = np.max(np.std(positions, axis=0)) * 3
    
    # Create optimized HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fast 3D Gaussian Splatting Viewer</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            background: linear-gradient(135deg, #0f0f23, #1a1a2e);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
            color: white;
        }}
        #container {{ width: 100vw; height: 100vh; }}
        #loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 1000;
            background: rgba(0,0,0,0.8);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        #loading.hidden {{ display: none; }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        #info {{
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            max-width: 300px;
            font-size: 14px;
        }}
        #controls {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
            font-size: 12px;
            transition: background 0.3s;
        }}
        .btn:hover {{ background: #2980b9; }}
        .slider {{
            width: 120px;
            margin: 5px 0;
        }}
        #status {{
            position: absolute;
            bottom: 15px;
            left: 15px;
            background: rgba(0,0,0,0.8);
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div id="loading">
        <div class="spinner"></div>
        <h3>Loading 3D Model...</h3>
        <p>Preparing {len(points_data):,} points</p>
        <p>Please wait...</p>
    </div>
    
    <div id="container"></div>
    
    <div id="info">
        <h3>🚲 3D Bicycle Model</h3>
        <p><strong>Points:</strong> {len(points_data):,} / {model_data.get('original_points', len(points_data)):,}</p>
        <p><strong>Status:</strong> <span id="loadStatus">Loading...</span></p>
        <hr style="margin: 10px 0; opacity: 0.3;">
        <div style="font-size: 11px;">
            <p><strong>Controls:</strong></p>
            <p>🖱️ Drag: Rotate</p>
            <p>🖱️ Right-drag: Pan</p>
            <p>⚡ Scroll: Zoom</p>
        </div>
    </div>
    
    <div id="controls">
        <h4>Settings</h4>
        <div>
            <label>Point Size:</label><br>
            <input type="range" id="pointSize" class="slider" min="0.005" max="0.03" step="0.001" value="0.015">
            <span id="sizeValue">0.015</span>
        </div>
        <div>
            <button id="resetView" class="btn">Reset View</button>
            <button id="autoRotate" class="btn">Auto Rotate</button>
        </div>
    </div>
    
    <div id="status">
        <div>FPS: <span id="fps">0</span></div>
        <div>Loaded: <span id="progress">0%</span></div>
    </div>
    
    <script>
        let scene, camera, renderer, controls, points;
        let isLoading = true;
        let autoRotateEnabled = false;
        let frameCount = 0;
        let lastTime = Date.now();
        
        // Initialize
        async function init() {{
            console.log('Initializing 3D viewer...');
            
            // Scene setup
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0a);
            
            // Camera
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            
            // Renderer
            renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setClearColor(0x0a0a0a);
            document.getElementById('container').appendChild(renderer.domElement);
            
            // Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.minDistance = 1;
            controls.maxDistance = 50;
            
            // Load model
            await loadModel();
            
            // Setup controls
            setupControls();
            
            // Start animation
            animate();
            
            // Hide loading screen
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('loadStatus').textContent = 'Ready';
            
            console.log('3D viewer initialized successfully!');
        }}
        
        async function loadModel() {{
            console.log('Loading point cloud data...');
            
            const pointsData = {json.dumps(points_data)};
            
            // Create geometry
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(pointsData.length * 3);
            const colors = new Float32Array(pointsData.length * 3);
            
            // Fill arrays
            for (let i = 0; i < pointsData.length; i++) {{
                const point = pointsData[i];
                
                positions[i * 3] = point.x;
                positions[i * 3 + 1] = point.y;
                positions[i * 3 + 2] = point.z;
                
                if (point.r !== undefined) {{
                    colors[i * 3] = point.r / 255;
                    colors[i * 3 + 1] = point.g / 255;
                    colors[i * 3 + 2] = point.b / 255;
                }} else {{
                    colors[i * 3] = 0.7;
                    colors[i * 3 + 1] = 0.8;
                    colors[i * 3 + 2] = 1.0;
                }}
                
                // Update progress
                if (i % 1000 === 0) {{
                    const progress = Math.round((i / pointsData.length) * 100);
                    document.getElementById('progress').textContent = progress + '%';
                    await new Promise(resolve => setTimeout(resolve, 1));
                }}
            }}
            
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            
            // Create material
            const material = new THREE.PointsMaterial({{
                size: 0.015,
                vertexColors: true,
                transparent: true,
                opacity: 0.9
            }});
            
            // Create points
            points = new THREE.Points(geometry, material);
            scene.add(points);
            
            // Position camera
            camera.position.set({center[0] + scale}, {center[1] + scale}, {center[2] + scale});
            camera.lookAt({center[0]}, {center[1]}, {center[2]});
            controls.target.set({center[0]}, {center[1]}, {center[2]});
            
            // Add lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
            directionalLight.position.set(10, 10, 5);
            scene.add(directionalLight);
            
            document.getElementById('progress').textContent = '100%';
            console.log('Model loaded successfully!');
        }}
        
        function setupControls() {{
            const pointSizeSlider = document.getElementById('pointSize');
            const sizeValue = document.getElementById('sizeValue');
            const resetButton = document.getElementById('resetView');
            const autoRotateButton = document.getElementById('autoRotate');
            
            pointSizeSlider.oninput = function() {{
                if (points) {{
                    points.material.size = parseFloat(this.value);
                    sizeValue.textContent = this.value;
                }}
            }};
            
            resetButton.onclick = function() {{
                camera.position.set({center[0] + scale}, {center[1] + scale}, {center[2] + scale});
                camera.lookAt({center[0]}, {center[1]}, {center[2]});
                controls.target.set({center[0]}, {center[1]}, {center[2]});
            }};
            
            autoRotateButton.onclick = function() {{
                autoRotateEnabled = !autoRotateEnabled;
                this.textContent = autoRotateEnabled ? 'Stop Rotate' : 'Auto Rotate';
                this.style.background = autoRotateEnabled ? '#e74c3c' : '#3498db';
            }};
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            
            // Auto rotation
            if (autoRotateEnabled && points) {{
                points.rotation.y += 0.005;
            }}
            
            // Update controls
            controls.update();
            
            // Render
            renderer.render(scene, camera);
            
            // Update FPS
            frameCount++;
            const now = Date.now();
            if (now - lastTime >= 1000) {{
                const fps = Math.round((frameCount * 1000) / (now - lastTime));
                document.getElementById('fps').textContent = fps;
                frameCount = 0;
                lastTime = now;
            }}
        }}
        
        // Handle window resize
        window.addEventListener('resize', function() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        // Start initialization
        init().catch(error => {{
            console.error('Error initializing viewer:', error);
            document.getElementById('loadStatus').textContent = 'Error loading';
        }});
    </script>
</body>
</html>"""
    
    # Save HTML file
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    return True

def main():
    """Generate fast 3D viewer"""
    print("🚀 Fast 3D Gaussian Splatting Viewer Generator")
    print("=" * 50)
    
    model_path = "/home/workbench/Documents/soham/projects/3DGS/gaussian-splatting/output/bicycle"
    ply_files = [f for f in os.listdir(model_path) if f.endswith('.ply')]
    
    if not ply_files:
        print("❌ No PLY files found")
        return False
    
    ply_path = os.path.join(model_path, ply_files[0])
    
    # Load with reduced points for fast loading
    print("🔄 Loading model with fast sampling...")
    model_data = load_ply_fast(ply_path, max_points=5000)
    
    if not model_data:
        print("❌ Failed to load model")
        return False
    
    print(f"✅ Model loaded: {model_data['num_points']:,} points")
    
    # Generate fast viewer
    output_path = "/home/workbench/Documents/soham/projects/3DGS/gaussian-splatting/fast_viewer.html"
    
    print("🎨 Creating fast viewer...")
    success = create_fast_viewer(model_data, output_path)
    
    if success:
        print(f"✅ Fast viewer created: {output_path}")
        print("🌐 This viewer loads much faster with 5,000 points")
        return True
    
    return False

if __name__ == "__main__":
    main()
