# import numpy as np
# import open3d as o3d
# from sklearn.cluster import DBSCAN
# import json

# def fit_gaussians(pcd_path, out_json, eps=0.05, min_samples=50, ransac_dist=0.02, min_cluster_size=200):
#     """
#     Load PLY pointcloud, segment planes via RANSAC and objects via DBSCAN,
#     fit one Gaussian per segment (mean + covariance + color),
#     regularize covariance and boost colors.
#     """
#     pcd = o3d.io.read_point_cloud(pcd_path)
#     pts = np.asarray(pcd.points)
#     cols = np.asarray(pcd.colors)

#     gaussians = []
#     # 1) Plane segmentation
#     for _ in range(3):
#         model, inliers = pcd.segment_plane(distance_threshold=ransac_dist,
#                                            ransac_n=3,
#                                            num_iterations=1000)
#         if len(inliers) < min_cluster_size:
#             break
#         inliers = np.array(inliers)
#         group_pts = pts[inliers]
#         group_cols = cols[inliers]
#         color = group_cols.mean(axis=0)
#         color = np.clip(color, 0.0, 1.0)  # Remove boost
#         mu = group_pts.mean(axis=0)
#         C = np.cov(group_pts, rowvar=False)
#         C += np.eye(3) * 1e-4
#         gaussians.append({"mean": mu.tolist(), "cov": C.tolist(), "color": color.tolist()})
#         pcd = pcd.select_by_index(inliers, invert=True)

#     # 2) DBSCAN on remaining pts
#     rem_pts = np.asarray(pcd.points)
#     rem_cols = np.asarray(pcd.colors)
#     clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(rem_pts)
#     for label in np.unique(clustering.labels_):
#         if label == -1: continue
#         mask = clustering.labels_ == label
#         if mask.sum() < min_cluster_size: continue
#         group_pts = rem_pts[mask]
#         group_cols = rem_cols[mask]
#         color = group_cols.mean(axis=0)
#         color = np.clip(color, 0.0, 1.0)
#         mu = group_pts.mean(axis=0)
#         C = np.cov(group_pts, rowvar=False)
#         C += np.eye(3) * 1e-4
#         gaussians.append({"mean": mu.tolist(), "cov": C.tolist(), "color": color.tolist()})

#     with open(out_json, 'w') as f:
#         json.dump({"gaussians": gaussians}, f, indent=2)

# if __name__ == "__main__":
#     import argparse
#     p = argparse.ArgumentParser()
#     p.add_argument("ply_in", help="Input point cloud PLY")
#     p.add_argument("json_out", help="Output simple Gaussians JSON")
#     p.add_argument("--eps", type=float, default=0.05)
#     p.add_argument("--min_samples", type=int, default=50)
#     p.add_argument("--ransac_dist", type=float, default=0.02)
#     p.add_argument("--min_cluster_size", type=int, default=200)
#     args = p.parse_args()
#     fit_gaussians(args.ply_in, args.json_out,
#                   eps=args.eps,
#                   min_samples=args.min_samples,
#                   ransac_dist=args.ransac_dist,
#                   min_cluster_size=args.min_cluster_size)
#     print(f"Fitted {len(json.load(open(args.json_out))['gaussians'])} Gaussians to {args.ply_in}")

import numpy as np
import open3d as o3d
import json

def per_point_gaussians(pcd_path, out_json):
    """
    One Gaussian per point: diagonal covariance, color from point, small scale.
    """
    pcd = o3d.io.read_point_cloud(pcd_path)
    pts = np.asarray(pcd.points)
    cols = np.asarray(pcd.colors)

    gaussians = []
    for pt, col in zip(pts, cols):
        C = np.eye(3) * 0.0025  # Small diagonal covariance
        color = np.clip(col, 0.0, 1.0)
        gaussians.append({
            "mean": pt.tolist(),
            "cov": C.tolist(),
            "color": color.tolist()
        })

    with open(out_json, 'w') as f:
        json.dump({"gaussians": gaussians}, f, indent=2)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("ply_in", help="Input point cloud PLY")
    p.add_argument("json_out", help="Output simple Gaussians JSON")
    args = p.parse_args()
    per_point_gaussians(args.ply_in, args.json_out)
    print(f"Fitted {len(json.load(open(args.json_out))['gaussians'])} Gaussians to {args.ply_in}")