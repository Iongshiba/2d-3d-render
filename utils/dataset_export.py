"""Dataset export utilities for COCO and YOLO formats."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
from PIL import Image
from OpenGL import GL


class DatasetExporter:
    """Handles exporting scene data to COCO and YOLO dataset formats."""

    def __init__(self, base_folder: str = "dataset"):
        self.base_folder = Path(base_folder)
        self.coco_folder = self.base_folder / "coco"
        self.yolo_folder = self.base_folder / "yolo"
        self.export_count = 0

        # Create directory structure
        self._setup_directories()

        # COCO dataset structure
        self.coco_data = {
            "info": {
                "description": "3D Graphics Export Dataset",
                "version": "1.0",
                "year": datetime.now().year,
                "contributor": "OpenGL Renderer",
                "date_created": datetime.now().isoformat(),
            },
            "licenses": [],
            "images": [],
            "annotations": [],
            "categories": [{"id": 1, "name": "model", "supercategory": "object"}],
        }
        self.annotation_id = 1

    def _setup_directories(self):
        """Create necessary directory structure."""
        # COCO structure
        (self.coco_folder / "images").mkdir(parents=True, exist_ok=True)
        (self.coco_folder / "depth").mkdir(parents=True, exist_ok=True)
        (self.coco_folder / "masks").mkdir(parents=True, exist_ok=True)

        # YOLO structure
        (self.yolo_folder / "images").mkdir(parents=True, exist_ok=True)
        (self.yolo_folder / "labels").mkdir(parents=True, exist_ok=True)
        (self.yolo_folder / "depth").mkdir(parents=True, exist_ok=True)
        (self.yolo_folder / "masks").mkdir(parents=True, exist_ok=True)

    def capture_framebuffer(self, width: int, height: int) -> np.ndarray:
        """Capture current OpenGL framebuffer."""
        # Read pixels from framebuffer
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        pixels = GL.glReadPixels(0, 0, width, height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE)

        # Convert to numpy array and flip vertically (OpenGL origin is bottom-left)
        image = np.frombuffer(pixels, dtype=np.uint8).reshape(height, width, 3)
        image = np.flipud(image)

        return image

    def extract_bounding_boxes(
        self, models: List
    ) -> List[Tuple[float, float, float, float]]:
        """
        Extract 2D bounding boxes from models.
        Returns list of (x_min, y_min, x_max, y_max) in normalized coordinates [0, 1].
        """
        bboxes = []

        for model in models:
            if not hasattr(model, "stored_model_matrix"):
                continue

            # Compute 2D bounding box
            bbox_data = model._compute_2d_bounding_box(
                model.stored_model_matrix,
                model.stored_view_matrix,
                model.stored_proj_matrix,
            )

            if bbox_data is None:
                continue

            corners, _ = bbox_data

            # Extract min/max coordinates (already in NDC [-1, 1])
            x_coords = corners[:, 0]
            y_coords = corners[:, 1]

            min_x = x_coords.min()
            max_x = x_coords.max()
            min_y = y_coords.min()
            max_y = y_coords.max()

            # Convert from NDC [-1, 1] to normalized [0, 1]
            min_x = (min_x + 1.0) / 2.0
            max_x = (max_x + 1.0) / 2.0
            min_y = (min_y + 1.0) / 2.0
            max_y = (max_y + 1.0) / 2.0

            bboxes.append((min_x, min_y, max_x, max_y))

        return bboxes

    def export_dataset(self, width: int, height: int, models: List, renderer) -> str:
        """
        Export current scene to both COCO and YOLO formats.

        Args:
            width: Framebuffer width
            height: Framebuffer height
            models: List of Model objects in the scene
            renderer: Renderer instance for mode switching

        Returns:
            Status message
        """
        if not models:
            return "No models found in scene to export"

        self.export_count += 1
        filename_base = f"export_{self.export_count:04d}"

        # Extract bounding boxes
        bboxes = self.extract_bounding_boxes(models)

        if not bboxes:
            return "Could not extract bounding boxes from models"

        # Capture normal render
        normal_image = self.capture_framebuffer(width, height)

        # Capture depth map
        depth_image = self._capture_depth_map(width, height, models, renderer)

        # Capture segmentation mask
        mask_image = self._capture_segmentation_mask(width, height, models, renderer)

        # Export COCO format
        self._export_coco(
            filename_base, normal_image, depth_image, mask_image, bboxes, width, height
        )

        # Export YOLO format
        self._export_yolo(
            filename_base, normal_image, depth_image, mask_image, bboxes, width, height
        )

        return f"Exported {filename_base} to COCO and YOLO formats"

    def _capture_depth_map(
        self, width: int, height: int, models: List, renderer
    ) -> np.ndarray:
        """Capture depth map visualization."""
        from config import ModelVisualizationMode

        # Store original modes
        original_modes = []
        for model in models:
            original_modes.append(model.visualization_mode)
            model.set_visualization_mode(ModelVisualizationMode.DEPTH_MAP)

        # Force a render with depth visualization
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        renderer.render(0.0)

        # Capture
        depth_image = self.capture_framebuffer(width, height)

        # Restore original modes
        for model, mode in zip(models, original_modes):
            model.set_visualization_mode(mode)

        # Force another render to restore display
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        renderer.render(0.0)

        return depth_image

    def _capture_segmentation_mask(
        self, width: int, height: int, models: List, renderer
    ) -> np.ndarray:
        """Capture segmentation mask visualization."""
        from config import ModelVisualizationMode

        # Store original modes
        original_modes = []
        for model in models:
            original_modes.append(model.visualization_mode)
            model.set_visualization_mode(ModelVisualizationMode.SEGMENTATION_MASK)

        # Force a render with mask visualization
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        renderer.render(0.0)

        # Capture
        mask_image = self.capture_framebuffer(width, height)

        # Restore original modes
        for model, mode in zip(models, original_modes):
            model.set_visualization_mode(mode)

        # Force another render to restore display
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        renderer.render(0.0)

        return mask_image

    def _export_coco(
        self,
        filename_base: str,
        normal_image: np.ndarray,
        depth_image: np.ndarray,
        mask_image: np.ndarray,
        bboxes: List[Tuple[float, float, float, float]],
        width: int,
        height: int,
    ):
        """Export in COCO format."""
        # Save images
        img_filename = f"{filename_base}.png"
        depth_filename = f"{filename_base}_depth.png"
        mask_filename = f"{filename_base}_mask.png"

        Image.fromarray(normal_image).save(self.coco_folder / "images" / img_filename)
        Image.fromarray(depth_image).save(self.coco_folder / "depth" / depth_filename)
        Image.fromarray(mask_image).save(self.coco_folder / "masks" / mask_filename)

        # Add image info
        image_id = self.export_count
        self.coco_data["images"].append(
            {
                "id": image_id,
                "file_name": img_filename,
                "width": width,
                "height": height,
                "depth_map": depth_filename,
                "segmentation_mask": mask_filename,
            }
        )

        # Add annotations for each bounding box
        for bbox in bboxes:
            x_min, y_min, x_max, y_max = bbox

            # Convert to pixel coordinates
            x_min_px = int(x_min * width)
            y_min_px = int(y_min * height)
            x_max_px = int(x_max * width)
            y_max_px = int(y_max * height)

            bbox_width = x_max_px - x_min_px
            bbox_height = y_max_px - y_min_px

            # COCO format: [x, y, width, height]
            annotation = {
                "id": self.annotation_id,
                "image_id": image_id,
                "category_id": 1,  # "model" category
                "bbox": [x_min_px, y_min_px, bbox_width, bbox_height],
                "area": bbox_width * bbox_height,
                "iscrowd": 0,
                "segmentation": [],  # Could be enhanced with polygon segmentation
            }

            self.coco_data["annotations"].append(annotation)
            self.annotation_id += 1

        # Save COCO JSON
        with open(self.coco_folder / "annotations.json", "w") as f:
            json.dump(self.coco_data, f, indent=2)

    def _export_yolo(
        self,
        filename_base: str,
        normal_image: np.ndarray,
        depth_image: np.ndarray,
        mask_image: np.ndarray,
        bboxes: List[Tuple[float, float, float, float]],
        width: int,
        height: int,
    ):
        """Export in YOLO format."""
        # Save images
        img_filename = f"{filename_base}.png"
        depth_filename = f"{filename_base}_depth.png"
        mask_filename = f"{filename_base}_mask.png"

        Image.fromarray(normal_image).save(self.yolo_folder / "images" / img_filename)
        Image.fromarray(depth_image).save(self.yolo_folder / "depth" / depth_filename)
        Image.fromarray(mask_image).save(self.yolo_folder / "masks" / mask_filename)

        # Create YOLO label file
        label_filename = f"{filename_base}.txt"
        label_path = self.yolo_folder / "labels" / label_filename

        with open(label_path, "w") as f:
            for bbox in bboxes:
                x_min, y_min, x_max, y_max = bbox

                # YOLO format: class_id center_x center_y width height (all normalized)
                center_x = (x_min + x_max) / 2.0
                center_y = (y_min + y_max) / 2.0
                bbox_width = x_max - x_min
                bbox_height = y_max - y_min

                # Class 0 for "model"
                f.write(
                    f"0 {center_x:.6f} {center_y:.6f} {bbox_width:.6f} {bbox_height:.6f}\n"
                )

        # Create or update data.yaml
        yaml_path = self.yolo_folder / "data.yaml"
        yaml_content = f"""# YOLO dataset configuration
path: {self.yolo_folder.absolute()}
train: images
val: images

# Classes
names:
  0: model
"""
        with open(yaml_path, "w") as f:
            f.write(yaml_content)

    def get_export_count(self) -> int:
        """Get the number of exports performed."""
        return self.export_count
