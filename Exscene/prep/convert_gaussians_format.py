# import json
# import numpy as np
# import argparse

# def decompose_covariance_to_scale_and_rotation(cov):
#     U, S, Vt = np.linalg.svd(cov)
#     scale = np.sqrt(S)
#     R = U @ Vt
#     return scale, R

# def quaternion_from_matrix(R):
#     q = np.empty(4)
#     t = np.trace(R)
#     if t > 0:
#         s = 0.5 / np.sqrt(t+1)
#         q[3] = 0.25 / s
#         q[0] = (R[2,1]-R[1,2]) * s
#         q[1] = (R[0,2]-R[2,0]) * s
#         q[2] = (R[1,0]-R[0,1]) * s
#     else:
#         i = np.argmax(np.diag(R))
#         if i==0:
#             s = 2*np.sqrt(1+R[0,0]-R[1,1]-R[2,2])
#             q[3] = (R[2,1]-R[1,2])/s; q[0]=0.25*s
#             q[1] = (R[0,1]+R[1,0])/s; q[2] = (R[0,2]+R[2,0])/s
#         elif i==1:
#             s = 2*np.sqrt(1+R[1,1]-R[0,0]-R[2,2])
#             q[3] = (R[0,2]-R[2,0])/s; q[1]=0.25*s
#             q[0] = (R[0,1]+R[1,0])/s; q[2] = (R[1,2]+R[2,1])/s
#         else:
#             s = 2*np.sqrt(1+R[2,2]-R[0,0]-R[1,1])
#             q[3] = (R[1,0]-R[0,1])/s; q[2]=0.25*s
#             q[0] = (R[0,2]+R[2,0])/s; q[1] = (R[1,2]+R[2,1])/s
#     return q.tolist()

# def convert(in_json, out_json, scale_factor=1.0, min_scale=0.2, brightness=1.0):
#     data = json.load(open(in_json))
#     pos = np.array(data["positions"], np.float32)
#     covs= data["covariances"]
#     cols= data["colors"]

#     scales, rotations, shs = [], [], []
#     for cov, col in zip(covs, cols):
#         cxx, cyy, czz, cxy, cxz, cyz = cov
#         C = np.array([[cxx,cxy,cxz],[cxy,cyy,cyz],[cxz,cyz,czz]])
#         C += np.eye(3)*1e-4
#         s, R = decompose_covariance_to_scale_and_rotation(C)
#         s = np.clip(s, min_scale, None)
#         scales.append(s.tolist())
#         rotations.append(quaternion_from_matrix(R))
#         shs.append([min(1,col[0]*brightness), min(1,col[1]*brightness), min(1,col[2]*brightness)] + [0.0]*45)

#     out = {
#         "positions": pos.tolist(),
#         "scales": scales,
#         "rotations": rotations,
#         "shs": shs
#     }
#     json.dump(out, open(out_json, 'w'), indent=2)

# if __name__ == "__main__":
#     p = argparse.ArgumentParser()
#     p.add_argument("input", help="3DGS intermediate JSON")
#     p.add_argument("output", help="Full 3DGS JSON with scales/rotations/SHs")
#     args = p.parse_args()
#     convert(args.input, args.output)
#     print(f"Converted {args.input} to {args.output} with scales, rotations, and SHs")

import json
import numpy as np
import argparse

def decompose_covariance_to_scale_and_rotation(cov):
    U, S, Vt = np.linalg.svd(cov)
    scale = np.sqrt(S)
    R = U @ Vt
    return scale, R

def quaternion_from_matrix(R):
    q = np.empty(4)
    t = np.trace(R)
    if t > 0:
        s = 0.5 / np.sqrt(t+1)
        q[3] = 0.25 / s
        q[0] = (R[2,1]-R[1,2]) * s
        q[1] = (R[0,2]-R[2,0]) * s
        q[2] = (R[1,0]-R[0,1]) * s
    else:
        i = np.argmax(np.diag(R))
        if i==0:
            s = 2*np.sqrt(1+R[0,0]-R[1,1]-R[2,2])
            q[3] = (R[2,1]-R[1,2])/s; q[0]=0.25*s
            q[1] = (R[0,1]+R[1,0])/s; q[2] = (R[0,2]+R[2,0])/s
        elif i==1:
            s = 2*np.sqrt(1+R[1,1]-R[0,0]-R[2,2])
            q[3] = (R[0,2]-R[2,0])/s; q[1]=0.25*s
            q[0] = (R[0,1]+R[1,0])/s; q[2] = (R[1,2]+R[2,1])/s
        else:
            s = 2*np.sqrt(1+R[2,2]-R[0,0]-R[1,1])
            q[3] = (R[1,0]-R[0,1])/s; q[2]=0.25*s
            q[0] = (R[0,2]+R[2,0])/s; q[1] = (R[1,2]+R[2,1])/s
    return q.tolist()

def convert(in_json, out_json, scale_factor=1.0, min_scale=0.2, brightness=1.0):
    data = json.load(open(in_json))
    pos = np.array(data["positions"], np.float32)
    covs= data["covariances"]
    cols= data["colors"]

    scales, rotations, shs = [], [], []
    for cov, col in zip(covs, cols):
        cxx, cyy, czz, cxy, cxz, cyz = cov
        C = np.array([[cxx,cxy,cxz],[cxy,cyy,cyz],[cxz,cyz,czz]])
        C += np.eye(3)*1e-4
        s, R = decompose_covariance_to_scale_and_rotation(C)
        s = np.clip(s, min_scale, None)
        scales.append(s.tolist())
        rotations.append(quaternion_from_matrix(R))
        shs.append([min(1,col[0]*brightness), min(1,col[1]*brightness), min(1,col[2]*brightness)] + [0.0]*45)

    out = {
        "positions": pos.tolist(),
        "scales": scales,
        "rotations": rotations,
        "shs": shs
    }
    json.dump(out, open(out_json, 'w'), indent=2)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("input", help="3DGS intermediate JSON")
    p.add_argument("output", help="Full 3DGS JSON with scales/rotations/SHs")
    args = p.parse_args()
    convert(args.input, args.output)
    print(f"Converted {args.input} to {args.output} with scales, rotations, and SHs")