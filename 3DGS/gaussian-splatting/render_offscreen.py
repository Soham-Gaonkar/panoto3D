import os
import json
import torch
import numpy as np
from pathlib import Path
from PIL import Image
import sys

# Ensure repo modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Correct import from actual file
from gaussian_renderer.gaussian_renderer import GaussianRenderer


def load_gaussians(json_path, device="cuda"):
    data = json.load(open(json_path))
    pos = torch.tensor(data["positions"], dtype=torch.float32, device=device)
    cov = torch.tensor(data["covariances"], dtype=torch.float32, device=device)
    col = torch.tensor(data["colors"], dtype=torch.float32, device=device)
    return pos, cov, col

def make_cameras(radius=2.0, N=8):
    cams = []
    for i in range(N):
        theta = i * (2*np.pi/N)
        cam_pos = np.array([radius*np.sin(theta), 0.0, radius*np.cos(theta)], dtype=np.float32)
        up = np.array([0,1,0], np.float32)
        forward = -cam_pos / np.linalg.norm(cam_pos)
        right   = np.cross(up, forward)
        up2     = np.cross(forward, right)
        R = np.stack([right, up2, forward], axis=1)
        M = np.eye(4, dtype=np.float32)
        M[:3,:3] = R
        M[:3,  3] = cam_pos
        cams.append(M)
    return cams

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("gaussian_json", help="Path to gaussians_3dgs.json")
    p.add_argument("out_dir", help="Directory to save rendered images")
    p.add_argument("--width",  type=int, default=512)
    p.add_argument("--height", type=int, default=512)
    p.add_argument("--fov",    type=float, default=60.0)
    p.add_argument("--views",  type=int,   default=16)
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    pos, cov, col = load_gaussians(args.gaussian_json, device)
    renderer = GaussianRenderer(
        positions=pos, covariances=cov, colors=col,
        image_width=args.width, image_height=args.height,
        fov_degrees=args.fov, device=device
    )

    os.makedirs(args.out_dir, exist_ok=True)
    cams = make_cameras(radius=2.0, N=args.views)

    for i, c2w in enumerate(cams):
        with torch.no_grad():
            rgb = renderer.render(c2w)
        img = (rgb.cpu().numpy() * 255).astype(np.uint8)
        Image.fromarray(img).save(f"{args.out_dir}/view_{i:03d}.png")

    print("Done.")
