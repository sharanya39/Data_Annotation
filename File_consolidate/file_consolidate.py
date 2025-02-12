import shutil
import pathlib
import logging
# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# Define source parent directory and destination directory
source_parent = pathlib.Path("/home/sharanya/Annotation/File_consolidate/Tv_shows")
destination = pathlib.Path("/home/sharanya/Annotation/File_consolidate/Result")
# Define extension categories
file_categories = {
    "images": {".jpeg", ".jpg", ".png", ".gif", ".bmp"},
    "audio_video": {".mp3", ".mp4", ".wav", ".mkv", ".avi"},
    "documents": {".pdf", ".docx", ".txt", ".xlsx"},
}
# Process files from all subdirectories
for file in source_parent.rglob("*.*"):  # Recursively find all files
    if file.is_file():
        file_ext = file.suffix.lower()
        # Skip files that don't belong to any category
        category = next((cat for cat, exts in file_categories.items() if file_ext in exts), None)
        if category is None:
            logging.warning(f"Skipping unsupported file: {file}")
            continue
        target_dir = destination / category
        target_path = target_dir / file.name
        # Ensure target directory exists
        target_dir.mkdir(parents=True, exist_ok=True)
        # Move file
        shutil.copy2(str(file), str(target_path))
        logging.info(f"Moved: {file} → {target_path}")
logging.info("File organization complete.")
