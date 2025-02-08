import os
import cv2
import shutil
from ultralytics import YOLO

# Define paths
source_dir = "/home/sharanya/Annotation/airplane_dataset"  # Directory containing all your images
target_dir = "Airplane"  # Target directory where the structure will be created
model_path = "yolov8n.pt"  # Path to YOLOv8 model

# Create the target directory structure
os.makedirs(os.path.join(target_dir, "annotated_images"), exist_ok=True)  # Folder for annotated images

# Load YOLOv8 model
model = YOLO(model_path)

# Function to check occlusion level
def check_occlusion(box, frame_shape):
    x1, y1, x2, y2 = box
    box_area = (x2 - x1) * (y2 - y1)
    frame_area = frame_shape[0] * frame_shape[1]

    # Full occlusion: bounding box area is too small
    if box_area < 0.01 * frame_area:
        return 0  # Fully occluded
    # Partial occlusion: bounding box area is reduced but not too small
    elif box_area < 0.5 * frame_area:
        return 1  # Partially occluded
   

# Function to check if an object is out of view
def is_out_of_view(box, frame_shape):
    x1, y1, x2, y2 = box
    # If the bounding box is outside the frame, it's out of view
    return x1 < 0 or y1 < 0 or x2 > frame_shape[1] or y2 > frame_shape[0]

# Open annotation files
groundtruth_file = open(os.path.join(target_dir, "Groundtruth.txt"), "w")
occlusion_file = open(os.path.join(target_dir, "fully_occlusion.txt"), "w")
out_of_view_file = open(os.path.join(target_dir, "out_of_view.txt"), "w")

# Process each image
for image_file in os.listdir(source_dir):
    if image_file.endswith((".jpg", ".png", ".jpeg")):
        # Read the image
        image_path = os.path.join(source_dir, image_file)
        frame = cv2.imread(image_path)
        frame_shape = frame.shape

        # Perform object detection
        results = model(image_path)
        boxes = results[0].boxes.xyxy.cpu().numpy()  # Get bounding boxes

        # Initialize annotation variables
        occlusion_status = -1  # Default: no occlusion
        out_of_view_status = 0  # Default: not out of view
        ground_truth_values = []  # To store bounding box values

        # Draw bounding boxes and process detections
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)

            # Save bounding box values
            ground_truth_values.append(f"{x1},{y1},{x2},{y2}")

            # Draw bounding box on the image
            color = (0, 255, 0)  # Green color for bounding box
            thickness = 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            # Check occlusion level
            occlusion_level = check_occlusion((x1, y1, x2, y2), frame_shape)
            if occlusion_level != -1:
                occlusion_status = occlusion_level

            # Check for out of view
            if is_out_of_view((x1, y1, x2, y2), frame_shape):
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

# Close annotation files
groundtruth_file.close()
occlusion_file.close()
out_of_view_file.close()

print("Dataset organized, annotations generated, and images annotated successfully!")