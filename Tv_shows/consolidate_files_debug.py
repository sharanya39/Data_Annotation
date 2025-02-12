import os
import shutil

# Define the parent folder and subfolders
parent_folder = "/home/sharanya/Annotation/Tv_shows"  # Ensure this is the correct path to your existing folder
subfolders = ["show1", "show2", "show3"]

# Define the output folders and their corresponding file extensions
output_folders = {
    "audio": [".mp3", ".mp4"],
    "image": [".png", ".jpeg", ".jpg"],  # Added .jpg for better matching
    "text": [".txt", ".docx"]
}

# Create output folders if they don't exist
for folder in output_folders.keys():
    os.makedirs(os.path.join(parent_folder, folder), exist_ok=True)

# Function to copy files to the appropriate folder
def copy_files(source_folder, destination_folder, extensions):
    #print(f"Copying files from {source_folder} to {destination_folder} with extensions: {extensions}")
    for root, _, files in os.walk(source_folder):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                # Construct the full source and destination paths
                src_path = os.path.join(root, file)
                dest_path = os.path.join(destination_folder, file)
                #print(f"Found file: {src_path} -> Copying to: {dest_path}")
                
                # Handle duplicate filenames
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_name = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(destination_folder, new_name)
                        counter += 1
                    print(f"File already exists. Renaming to: {dest_path}")
                
                # Copy the file
                shutil.copy2(src_path, dest_path)
                print(f"Copied: {src_path} -> {dest_path}")

# Consolidate files from subfolders
for subfolder in subfolders:
    subfolder_path = os.path.join(parent_folder, subfolder)
    if not os.path.exists(subfolder_path):
        print(f"Subfolder does not exist: {subfolder_path}")
        continue  # Skip if the subfolder doesn't exist

    for folder, extensions in output_folders.items():
        destination_folder = os.path.join(parent_folder, folder)
        copy_files(subfolder_path, destination_folder, extensions)

print("Files have been copied and consolidated successfully!")