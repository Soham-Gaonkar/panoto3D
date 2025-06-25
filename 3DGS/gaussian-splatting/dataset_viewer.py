#!/usr/bin/env python3
"""
Simple Dataset Viewer for 3D Gaussian Splatting
Shows the input images from COLMAP datasets
"""

import os
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import argparse
from pathlib import Path

class DatasetViewer:
    def __init__(self, dataset_path):
        self.dataset_path = Path(dataset_path)
        self.images = []
        self.current_idx = 0
        
        # Load images
        self.load_images()
        
        if len(self.images) == 0:
            print("❌ No images found in dataset!")
            return
            
        # Setup matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.suptitle(f'3DGS Dataset Viewer: {self.dataset_path.name}', fontsize=16)
        
        # Create navigation buttons
        ax_prev = plt.axes([0.1, 0.01, 0.1, 0.05])
        ax_next = plt.axes([0.21, 0.01, 0.1, 0.05])
        ax_info = plt.axes([0.32, 0.01, 0.1, 0.05])
        
        self.btn_prev = Button(ax_prev, 'Previous')
        self.btn_next = Button(ax_next, 'Next')
        self.btn_info = Button(ax_info, 'Info')
        
        self.btn_prev.on_clicked(self.prev_image)
        self.btn_next.on_clicked(self.next_image)
        self.btn_info.on_clicked(self.show_info)
        
        # Show first image
        self.update_display()
        
    def load_images(self):
        """Load all images from the dataset"""
        image_dirs = ['images', 'input', 'images_4', 'images_2']
        
        for img_dir in image_dirs:
            img_path = self.dataset_path / img_dir
            if img_path.exists():
                print(f"📁 Loading images from: {img_path}")
                
                # Common image extensions
                extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
                
                for ext in extensions:
                    for img_file in img_path.glob(ext):
                        self.images.append(img_file)
                
                if self.images:
                    break  # Use first directory that has images
        
        self.images.sort()
        print(f"✅ Found {len(self.images)} images")
        
    def update_display(self):
        """Update the displayed image"""
        if len(self.images) == 0:
            return
            
        img_path = self.images[self.current_idx]
        
        # Load and display image
        img = cv2.imread(str(img_path))
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            self.ax.clear()
            self.ax.imshow(img_rgb)
            self.ax.set_title(f'Image {self.current_idx + 1}/{len(self.images)}: {img_path.name}')
            self.ax.axis('off')
            
            plt.draw()
        
    def prev_image(self, event):
        """Show previous image"""
        if len(self.images) > 0:
            self.current_idx = (self.current_idx - 1) % len(self.images)
            self.update_display()
            
    def next_image(self, event):
        """Show next image"""
        if len(self.images) > 0:
            self.current_idx = (self.current_idx + 1) % len(self.images)
            self.update_display()
            
    def show_info(self, event):
        """Show dataset information"""
        if len(self.images) == 0:
            return
            
        img_path = self.images[self.current_idx]
        img = cv2.imread(str(img_path))
        
        info_text = f"""
Dataset: {self.dataset_path.name}
Total Images: {len(self.images)}
Current: {self.current_idx + 1}
Image: {img_path.name}
Resolution: {img.shape[1]}x{img.shape[0]}
Path: {self.dataset_path}

Navigation:
- Previous/Next buttons or arrow keys
- Close window to exit
        """
        
        print(info_text)
        
    def show(self):
        """Show the viewer"""
        if len(self.images) > 0:
            # Enable keyboard navigation
            def on_key(event):
                if event.key == 'left':
                    self.prev_image(None)
                elif event.key == 'right':
                    self.next_image(None)
                elif event.key == 'q':
                    plt.close()
                    
            self.fig.canvas.mpl_connect('key_press_event', on_key)
            plt.show()
        else:
            print("❌ No images to display!")

def main():
    parser = argparse.ArgumentParser(description='View 3DGS dataset images')
    parser.add_argument('-d', '--dataset', 
                       default='/home/workbench/Documents/soham/projects/Data/Mips/bicycle',
                       help='Path to dataset directory')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset):
        print(f"❌ Dataset path not found: {args.dataset}")
        sys.exit(1)
        
    print("🎮 3DGS Dataset Viewer")
    print("====================")
    print(f"📂 Dataset: {args.dataset}")
    
    viewer = DatasetViewer(args.dataset)
    viewer.show()

if __name__ == "__main__":
    main()
