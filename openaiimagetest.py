import os
from PIL import Image
import openai

def get_images_from_folder(folder_path):
    """Load image file paths from the given folder."""
    supported_formats = [".jpg", ".jpeg", ".png"]
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.splitext(file)[-1].lower() in supported_formats]

def generate_image_metadata(image_path):
    """Extract basic metadata from an image."""
    with Image.open(image_path) as img:
        metadata = {
            "filename": os.path.basename(image_path),
            "format": img.format,
            "size": img.size,  # (width, height)
            "mode": img.mode,  # e.g., RGB, CMYK
        }
    return metadata

def transform_metadata_to_text(metadata):
    """Convert image metadata into a textual description."""
    description = (
        f"Image {metadata['filename']} is a {metadata['format']} file with dimensions "
        f"{metadata['size'][0]}x{metadata['size'][1]} pixels and a color mode of {metadata['mode']}."
    )
    return description

def compare_images_with_openai(image_descriptions):
    """Send image descriptions to OpenAI API for comparison."""
    str1 = "sk-proj-VZeebfbISGNPnpTyL_jfGEhDiFZLm7nxC7-"
    str2 = "jxzicheaKb2uff_ch6OniIlM0HXuSGuLT_k1LxfT3BlbkFJvrXO_"
    str3 = "ditN99xACAqJ_ifMX8_OkVNhQM2IXEqMY_"
    str4 = "a6jPViBTHVv9d8Uv7_DMapROEnk9ET30wUA"
    openai.api_key = str1 + str2 + str3 + str4
    # Construct a prompt to compare the images
    prompt = (
        "Here are descriptions of images:\n\n" +
        "\n".join(f"{i+1}. {desc}" for i, desc in enumerate(image_descriptions)) +
        "\n\nWhich image is better for social media and why?"
    )

    # Send the prompt to OpenAI's Chat API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in analyzing images for social media suitability."},
            {"role": "user", "content": prompt}
        ]
    )

    return response["choices"][0]["message"]["content"]

if __name__ == "__main__":
    folder_path = r"C:\\Users\\roman\\Downloads\\test"
    image_paths = get_images_from_folder(folder_path)

    if not image_paths:
        print("No valid images found in the folder.")
    else:
        # Generate metadata and transform into textual descriptions
        image_descriptions = [transform_metadata_to_text(generate_image_metadata(path)) for path in image_paths]
        
        # Compare the images using OpenAI
        result = compare_images_with_openai(image_descriptions)
        print("Comparison Results:")
        print(result)
