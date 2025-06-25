# exsceneimplementation/prep/erp_to_pointcloud.py
import numpy as np
from PIL import Image
import struct

def erp_to_pointcloud(rgb_path, depth_path, ply_path):
    """
    Unproject an equirectangular RGB (H×W×3) + depth (H×W) to a PLY point cloud.
    """
    # Load
    rgb   = np.array(Image.open(rgb_path).convert("RGB"), dtype=np.uint8)
    # load depth as single‐channel float
    depth = np.array(Image.open(depth_path).convert("F"), dtype=np.float32)
    H, W = depth.shape

    # Compute spherical coords
    # θ ∈ [0, 2π) longitude across width, φ ∈ [−π/2, π/2] latitude down height
    jj, ii = np.meshgrid(np.arange(W), np.arange(H))
    theta = (jj / W) * 2 * np.pi               # [0,2π]
    phi   = (0.5 - ii / H) * np.pi             # [+π/2→−π/2]

    # Spherical to Cartesian
    x = depth * np.cos(phi) * np.sin(theta)
    y = depth * np.sin(phi)
    z = depth * np.cos(phi) * np.cos(theta)

    # Flatten
    pts = np.stack((x, y, z), axis=-1).reshape(-1, 3)
    cols = rgb.reshape(-1, 3)

    # Write PLY (binary little-endian)
    with open(ply_path, 'wb') as f:
        # Header
        f.write(b"ply\n")
        f.write(b"format binary_little_endian 1.0\n")
        f.write(f"element vertex {pts.shape[0]}\n".encode())
        f.write(b"property float x\nproperty float y\nproperty float z\n")
        f.write(b"property uchar red\nproperty uchar green\nproperty uchar blue\n")
        f.write(b"end_header\n")
        # Data
        for (x,y,z), (r,g,b) in zip(pts, cols):
            f.write(struct.pack("<fffBBB", x, y, z, r, g, b))

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("rgb")
    p.add_argument("depth")
    p.add_argument("ply_out")
    args = p.parse_args()
    erp_to_pointcloud(args.rgb, args.depth, args.ply_out)
