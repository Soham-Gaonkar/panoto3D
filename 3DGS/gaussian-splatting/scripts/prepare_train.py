# prepare_train.py

import argparse, os, json
from pathlib import Path

def main(source_path):
    source = Path(source_path)
    json_path = source / "transforms.json"

    with open(json_path, "r") as f:
        meta = json.load(f)

    frames = meta["frames"]
    frames = sorted(frames, key=lambda x: x["file_path"])

    # 90% train, 10% test split
    N = len(frames)
    train_N = int(0.9 * N)
    train_frames = frames[:train_N]
    test_frames  = frames[train_N:]

    meta_train = dict(meta)
    meta_train["frames"] = train_frames
    meta_test  = dict(meta)
    meta_test["frames"]  = test_frames

    with open(source / "transforms_train.json", "w") as f:
        json.dump(meta_train, f, indent=2)
    with open(source / "transforms_test.json", "w") as f:
        json.dump(meta_test, f, indent=2)

    print(f"Split complete → {len(train_frames)} train + {len(test_frames)} test views")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_path", required=True, help="Directory with transforms.json and images/")
    args = parser.parse_args()

    main(args.source_path)
