# File: prep/pointcloud_to_scene_init.py
#!/usr/bin/env python3
"""
Prep script: pointcloud.ply → scene_init/
  • Generates transforms_train.json & transforms_test.json using multi-radius Fibonacci-sphere sampling
  • Renders color images and depth maps for each view (headless)
  • Allows cameras to move closer/farther to capture fine object details
"""
import os, json, argparse
import numpy as np
from plyfile import PlyData
from PIL import Image

def load_pointcloud(ply_path):
    ply = PlyData.read(ply_path)
    v   = ply['vertex'].data
    xyz = np.vstack([v['x'], v['y'], v['z']]).T.astype(np.float32)
    rgb = np.vstack([v['red'], v['green'], v['blue']]).T.astype(np.float32)/255.0
    return xyz, rgb


def multi_radius_fibonacci(samples=60, radii=(3.0, 6.0), center=(0,0,0)):
    """
    Generate camera positions: for each direction on a Fibonacci sphere,
    sample at each radius in `radii` to get multi-distance coverage.
    """
    dirs = []
    offset = 2.0 / samples
    increment = np.pi * (3.0 - np.sqrt(5.0))
    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2)
        r = np.sqrt(max(0.0, 1 - y*y))
        phi = i * increment
        x = np.cos(phi) * r
        z = np.sin(phi) * r
        dirs.append((x, y, z))
    positions = []
    cx, cy, cz = center
    for d in dirs:
        for rad in radii:
            positions.append((d[0]*rad + cx,
                              d[1]*rad + cy,
                              d[2]*rad + cz))
    return np.array(positions, dtype=np.float32)


def look_at(cam_pos, target=(0,0,0), up=(0,1,0)):
    pos    = np.array(cam_pos, dtype=np.float32)
    target = np.array(target, dtype=np.float32)
    upv    = np.array(up, dtype=np.float32)
    forward = (target - pos)
    forward /= np.linalg.norm(forward)
    right   = np.cross(upv, forward)
    right  /= np.linalg.norm(right)
    true_up = np.cross(forward, right)
    R = np.stack([right, true_up, forward], axis=1)
    M = np.eye(4, dtype=np.float32)
    M[:3,:3] = R
    M[:3, 3] = pos
    return M


def render_views(xyz, rgb, transforms, out_dir, W, H, fx, fy, cx, cy):
    img_dir   = os.path.join(out_dir, 'images')
    depth_dir = os.path.join(out_dir, 'depths')
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(depth_dir, exist_ok=True)

    for idx, M_c2w in enumerate(transforms):
        M = np.linalg.inv(np.array(M_c2w, dtype=np.float32))
        R, t = M[:3,:3], M[:3,3]
        Xc = (xyz @ R.T) + t
        zs = Xc[:,2]
        mask = zs>0
        pts, ds, cols = Xc[mask], zs[mask], rgb[mask]
        us = np.round((fx*pts[:,0]/ds)+cx).astype(int)
        vs = np.round((fy*pts[:,1]/ds)+cy).astype(int)
        valid = (us>=0)&(us<W)&(vs>=0)&(vs<H)
        us, vs, ds, cols = us[valid], vs[valid], ds[valid], cols[valid]

        img   = np.zeros((H, W, 3), dtype=np.uint8)
        depth = np.full((H, W), np.inf, dtype=np.float32)
        for u,v,z,c in zip(us, vs, ds, cols):
            if z < depth[v,u]:
                depth[v,u] = z
                img[v,u]   = (c*255).astype(np.uint8)

        valid_d = np.isfinite(depth)
        depth_vis = np.zeros((H,W), dtype=np.uint8)
        if valid_d.any():
            dmin, dmax = depth[valid_d].min(), depth[valid_d].max()
            with np.errstate(invalid='ignore'):
                norm = (depth - dmin)/(dmax - dmin)
            norm = np.clip(norm, 0.0, 1.0)
            depth_vis[valid_d] = (norm[valid_d]*255).astype(np.uint8)

        Image.fromarray(img).save(f"{img_dir}/{idx:03d}.png")
        Image.fromarray(depth_vis).save(f"{depth_dir}/{idx:03d}.png")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ply",     required=True, help="Input PLY path")
    p.add_argument("--out_dir", required=True, help="scene_init folder")
    p.add_argument("--views",   type=int,   default=60,  help="Base number of directions (will multiply by radii count)")
    p.add_argument("--radii",   type=float, nargs='+', default=[3.0,6.0], help="List of radii for multi-distance sampling")
    p.add_argument("--width",   type=int,   default=512)
    p.add_argument("--height",  type=int,   default=256)
    args = p.parse_args()

    xyz, rgb = load_pointcloud(args.ply)
    cam_pos  = multi_radius_fibonacci(samples=args.views, radii=args.radii)
    poses    = [look_at(pos).tolist() for pos in cam_pos]

    os.makedirs(args.out_dir, exist_ok=True)
    train_j = os.path.join(args.out_dir, 'transforms_train.json')
    test_j  = os.path.join(args.out_dir, 'transforms_test.json')
    data    = {"frames": [{"transform_matrix": M} for M in poses]}
    json.dump(data, open(train_j, 'w'), indent=2)
    json.dump(data, open(test_j,  'w'), indent=2)

    fx = fy = 0.5 * args.width
    cx, cy = 0.5 * args.width, 0.5 * args.height
    render_views(xyz, rgb, poses, args.out_dir,
                 args.width, args.height, fx, fy, cx, cy)

    print(f" scene_init prepared with {len(poses)} views and radii={args.radii}")

if __name__ == "__main__":
    main()
