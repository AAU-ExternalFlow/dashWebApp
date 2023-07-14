import os
from PIL import Image

def rotate_newest_image(directory, degrees):
    # Get a list of files in the directory
    files = os.listdir(directory)

    # Filter the list to include only image files (you can modify the condition as per your file extensions)
    image_files = [file for file in files if file.endswith((".png", ".jpg", ".jpeg"))]

    if not image_files:
        print("No image files found in the directory.")
        return

    # Sort the image files based on their creation time (most recent first)
    sorted_files = sorted(image_files, key=lambda file: os.path.getmtime(os.path.join(directory, file)), reverse=True)

    # Select the newest image file
    newest_image_path = os.path.join(directory, sorted_files[0])

    # Rotate the newest image
    image = Image.open(newest_image_path)
    rotated_image = image.rotate(degrees, expand=True)
    rotated_image.save("rotated_image.png")
    rotated_image.show()

