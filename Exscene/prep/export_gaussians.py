# import json
# import numpy as np

# def convert_to_3dgs_json(in_json, out_json):
#     """
#     Convert simple JSON of means/covs/colors into 3DGS intermediate format:
#     {positions, covariances, colors}.
#     """
#     data = json.load(open(in_json))
#     gauss = data.get("gaussians", [])
#     N = len(gauss)

#     pos = np.zeros((N,3), np.float32)
#     covs = np.zeros((N,6), np.float32)
#     cols = np.zeros((N,3), np.float32)

#     for i, g in enumerate(gauss):
#         m = np.array(g["mean"], float)
#         C = np.array(g["cov"], float)
#         color = np.array(g["color"], float)
#         assert C.shape == (3,3)
#         pos[i] = m
#         covs[i] = [C[0,0], C[1,1], C[2,2], C[0,1], C[0,2], C[1,2]]
#         cols[i] = np.clip(color, 0.0, 1.0)

#     out = {
#         "positions": pos.tolist(),
#         "covariances": covs.tolist(),
#         "colors": cols.tolist()
#     }
#     with open(out_json, 'w') as f:
#         json.dump(out, f, indent=2)

# if __name__ == "__main__":
#     import argparse
#     p = argparse.ArgumentParser()
#     p.add_argument("in_json", help="Input simple Gaussians JSON")
#     p.add_argument("out_json", help="Output 3DGS intermediate JSON")
#     args = p.parse_args()
#     convert_to_3dgs_json(args.in_json, args.out_json)
#     print(f"Converted {args.in_json} to {args.out_json} in 3DGS format")

import json
import numpy as np

def convert_to_3dgs_json(in_json, out_json):
    data = json.load(open(in_json))
    gauss = data.get("gaussians", [])
    N = len(gauss)

    pos = np.zeros((N,3), np.float32)
    covs = np.zeros((N,6), np.float32)
    cols = np.zeros((N,3), np.float32)

    for i, g in enumerate(gauss):
        m = np.array(g["mean"], float)
        C = np.array(g["cov"], float)
        color = np.array(g["color"], float)
        assert C.shape == (3,3)
        pos[i] = m
        covs[i] = [C[0,0], C[1,1], C[2,2], C[0,1], C[0,2], C[1,2]]
        cols[i] = np.clip(color, 0.0, 1.0)

    out = {
        "positions": pos.tolist(),
        "covariances": covs.tolist(),
        "colors": cols.tolist()
    }
    with open(out_json, 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("in_json", help="Input simple Gaussians JSON")
    p.add_argument("out_json", help="Output 3DGS intermediate JSON")
    args = p.parse_args()
    convert_to_3dgs_json(args.in_json, args.out_json)
    print(f"Converted {args.in_json} to {args.out_json} in 3DGS format")