import numpy as np
import open3d as o3d
from PIL import Image
import cv2

def render_with_camera(pcd, intrinsics, extrinsic, width, height):
    """
    Render point cloud using a simple pinhole projection.
    This is a *very simplified* renderer using Open3D.
    """
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=width, height=height, visible=False)
    vis.add_geometry(pcd)

    ctr = vis.get_view_control()
    ctr.convert_from_pinhole_camera_parameters(
        o3d.camera.PinholeCameraParameters()._replace(
            intrinsic=intrinsics,
            extrinsic=extrinsic
        )
    )

    vis.poll_events()
    vis.update_renderer()

    # Capture RGB image
    rgb = np.asarray(vis.capture_screen_float_buffer(False)) * 255
    rgb_img = Image.fromarray(rgb.astype(np.uint8))

    # No real depth rendered here (Open3D limitation in headless), return dummy
    depth_img = np.zeros((height, width), dtype=np.float32)

    vis.destroy_window()
    return rgb_img, depth_img
