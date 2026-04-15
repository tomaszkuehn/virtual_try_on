"""
Example usage of the Virtual Try-On Application
"""
import os
import sys
from PIL import Image, ImageDraw

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tryon_app import VirtualTryOn


def create_sample_images():
    """Create sample person and clothing images for demonstration."""
    # Create a simple person silhouette
    person_img = Image.new('RGB', (400, 600), color='white')
    draw = ImageDraw.Draw(person_img)

    # Draw a simple person shape
    # Head
    draw.ellipse([175, 50, 225, 100], fill='peachpuff')
    # Body
    draw.rectangle([150, 100, 250, 400], fill='lightblue')
    # Arms
    draw.rectangle([100, 150, 150, 300], fill='lightblue')
    draw.rectangle([250, 150, 300, 300], fill='lightblue')
    # Legs
    draw.rectangle([150, 400, 200, 550], fill='saddlebrown')
    draw.rectangle([200, 400, 250, 550], fill='saddlebrown')

    person_img.save('sample_person.jpg')
    print("Created sample_person.jpg")

    # Create a simple clothing item (shirt)
    clothing_img = Image.new('RGB', (200, 150), color='white')
    draw = ImageDraw.Draw(clothing_img)

    # Draw a simple shirt shape
    draw.rectangle([25, 25, 175, 125], fill='red')  # Main body
    draw.rectangle([0, 50, 25, 100], fill='red')    # Left sleeve
    draw.rectangle([175, 50, 200, 100], fill='red') # Right sleeve
    draw.rectangle([25, 0, 175, 25], fill='white')  # Neck hole

    clothing_img.save('sample_clothing.jpg')
    print("Created sample_clothing.jpg")


def demonstrate_usage():
    """Demonstrate how to use the virtual try-on application."""
    print("Virtual Try-On Application Demo")
    print("=" * 40)

    # Create sample images if they don't exist
    if not os.path.exists('sample_person.jpg') or not os.path.exists('sample_clothing.jpg'):
        print("Creating sample images...")
        create_sample_images()

    # Initialize the application (demo mode since no Google Cloud project ID)
    tryon_app = VirtualTryOn()

    print("\nProcessing images...")
    print("- Person image: sample_person.jpg")
    print("- Clothing image: sample_clothing.jpg")

    # Generate try-on result
    result = tryon_app.generate_try_on(
        person_image_path='sample_person.jpg',
        clothing_image_path='sample_clothing.jpg',
        output_path='tryon_result.jpg'
    )

    print(f"\nGenerated try-on image: {result.size[0]}x{result.size[1]} pixels")
    print("Result saved as: tryon_result.jpg")
    print("\nNote: This is running in demo mode.")
    print("To use actual AI try-on capabilities:")
    print("1. Set up an Alibaba Cloud account")
    print("2. Enable the DashScope service")
    print("3. Get your API key from the Alibaba Cloud console")
    print("4. Run with --api-key YOUR_DASHSCOPE_API_KEY")


if __name__ == "__main__":
    demonstrate_usage()