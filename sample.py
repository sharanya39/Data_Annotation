import os
import cv2
import logging
from ultralytics import YOLO

# Define paths
source_dir = "/home/sharanya/Annotation/airplane_dataset"  # Directory containing all your images
target_dir = "result"  # Target directory where the structure will be created
model_path = "yolov8n.pt"  # Path to YOLOv8 model

# Create the target directory structure
os.makedirs(os.path.join(target_dir, "annotated_images"), exist_ok=True)  # Folder for annotated images

# Load YOLOv8 model
model = YOLO(model_path)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Starting object detection...")

# Function to check occlusion level
def check_occlusion(box, frame_shape):
    x1, y1, width, height = box
    box_area = width * height
    frame_area = frame_shape[0] * frame_shape[1]

    if box_area < 0.01 * frame_area:
        return 0  # Fully occluded
    elif box_area < 0.5 * frame_area:
        return 1  # Partially occluded
    else:
        return -1  # No occlusion

# Function to check if an object is out of view
def is_out_of_view(box, frame_shape):
    x1, y1, width, height = box
    x2 = x1 + width
    y2 = y1 + height
    frame_height, frame_width = frame_shape[:2]
    return (x1 < 0 or y1 < 0 or x2 > frame_width or y2 > frame_height)

# Get list of images in the dataset (sorted to maintain order)
image_files = sorted([f for f in os.listdir(source_dir) if f.endswith((".jpg", ".png", ".jpeg"))])

# Open annotation files
with open(os.path.join(target_dir, "Groundtruth.txt"), "w") as groundtruth_file, \
     open(os.path.join(target_dir, "fully_occlusion.txt"), "w") as occlusion_file, \
     open(os.path.join(target_dir, "out_of_view.txt"), "w") as out_of_view_file:

    # Process each image in order
    for image_file in image_files:
        # Read the image
        image_path = os.path.join(source_dir, image_file)
        frame = cv2.imread(image_path)
        if frame is None:
            logging.warning(f"Unable to read image: {image_file}")
            continue
        frame_shape = frame.shape

        # Perform object detection
        results = model(image_path, conf=0.5)  # Set confidence threshold
        boxes = results[0].boxes.xyxy.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()

        # Initialize annotation variables
        occlusion_status = 0  # Default: no occlusion
        out_of_view_status = 0  # Default: not out of view
        ground_truth_values = []  # To store bounding box values

        # Draw bounding boxes and process detections
        for box, cls, conf in zip(boxes, classes, confidences):
            if cls == 4 and conf >= 0.5:  # Filter for airplane class and confidence threshold
                x1, y1, x2, y2 = map(int, box)
                width = x2 - x1
                height = y2 - y1

                # Save bounding box values in (x1, y1, width, height) format
                ground_truth_values.append(f"{x1},{y1},{width},{height}")

                # Draw bounding box on the image
                color = (0, 255, 0)  # Green color for bounding box
                thickness = 2
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

                # Check occlusion level
                occlusion_level = check_occlusion((x1, y1, width, height), frame_shape)
                if occlusion_level != -1:
                    occlusion_status = occlusion_level

                # Check for out of view
                if is_out_of_view((x1, y1, width, height), frame_shape):
                    out_of_view_status = 1  # Out of view

        # Save the annotated image
        annotated_image_path = os.path.join(target_dir, "annotated_images", image_file)
        cv2.imwrite(annotated_image_path, frame)

        # Write ground truth values to Groundtruth.txt (only values, no image filename)
        groundtruth_file.write(f"{' '.join(ground_truth_values)}\n")

        # Write occlusion status to fully_occlusion.txt (only values, no image filename)
        occlusion_file.write(f"{occlusion_status}\n")

        # Write out-of-view status to out_of_view.txt (only values, no image filename)
        out_of_view_file.write(f"{out_of_view_status}\n")

        logging.info(f"Processed {image_file}: {len(ground_truth_values)} detections")

logging.info("Dataset organized, annotations generated, and images annotated successfully!")