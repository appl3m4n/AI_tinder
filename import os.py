import os
from PIL import Image
import cv2
import openai
import numpy as np

def get_images_from_folder(folder_path):
    """Load image file paths from the given folder."""
    supported_formats = [".jpg", ".jpeg", ".png"]
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.splitext(file)[-1].lower() in supported_formats]

def detect_faces(image_path):
    """Detect faces in an image using OpenCV."""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces), faces

def evaluate_image_quality(image_path):
    """Evaluate basic image quality metrics for social media suitability."""
    image = Image.open(image_path)
    np_image = np.array(image)

    # Calculate brightness
    brightness = np.mean(np_image)

    # Calculate sharpness using Laplacian
    gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    return brightness, sharpness

def compare_images_for_social_media(image_paths):
    """Compare images and determine which is better for social media."""
    results = []

    for image_path in image_paths:
        num_faces, faces = detect_faces(image_path)
        brightness, sharpness = evaluate_image_quality(image_path)
        
        # Criteria for scoring
        score = 0
        score += num_faces * 50  # Prioritize images with faces
        score += brightness / 2  # Scale brightness
        score += sharpness / 10  # Scale sharpness

        results.append({
            "path": image_path,
            "score": score,
            "num_faces": num_faces,
            "brightness": brightness,
            "sharpness": sharpness
        })

    # Sort results by score (higher is better)
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

if __name__ == "__main__":
    folder_path = r"C:\\Users\\roman\\Downloads\\test"
    image_paths = get_images_from_folder(folder_path)

    if not image_paths:
        print("No valid images found in the folder.")
    else:
        comparison_results = compare_images_for_social_media(image_paths)

        print("Social Media Image Comparison Results:")
        for result in comparison_results:
            print(f"Image: {result['path']}")
            print(f"  Score: {result['score']:.2f}")
            print(f"  Faces Detected: {result['num_faces']}")
            print(f"  Brightness: {result['brightness']:.2f}")
            print(f"  Sharpness: {result['sharpness']:.2f}")
            print("---")

        best_image = comparison_results[0]
        print(f"\nBest image for social media: {best_image['path']} with score {best_image['score']:.2f}")