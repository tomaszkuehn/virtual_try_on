"""
Virtual Try-On Application
Processes person and clothing photographs to generate try-on images using Alibaba Cloud Qwen.
"""

import os
import io
import base64
from typing import Optional, Tuple
from PIL import Image
import logging

# DashScope imports for Alibaba Cloud Qwen
try:
    import dashscope
    from dashscope import MultiModalConversation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    logging.warning("DashScope not available. Install dashscope for Alibaba Cloud Qwen functionality.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VirtualTryOn:
    """
    Main class for processing person and clothing images to generate try-on results.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Virtual Try-On application.

        Args:
            api_key: Alibaba Cloud DashScope API key (required for Qwen-Image-Max)
        """
        self.api_key = api_key
        self.model = "qwen-image-2.0"  # Using Qwen-Image-2.0 as requested
        self.initialized = False

        # Check if we should initialize DashScope
        if api_key and DASHSCOPE_AVAILABLE and api_key.strip():
            try:
                # Set the API key and base URL for international region (as in the example)
                dashscope.api_key = api_key
                dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'
                # Test the connection by setting a flag - actual test happens during API call
                self.initialized = True
                logger.info(f"Prepared to use DashScope with Qwen-Image-2.0 model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to prepare DashScope: {e}")
                self.initialized = False
        elif not DASHSCOPE_AVAILABLE:
            logger.warning("DashScope dependencies not installed. Running in demo mode.")
        else:
            logger.info("No valid API key provided. Running in demo mode.")

    def load_and_validate_image(self, image_path: str) -> Image.Image:
        """
        Load and validate an image file.

        Args:
            image_path: Path to the image file

        Returns:
            PIL Image object

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image cannot be loaded or is invalid
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        try:
            image = Image.open(image_path)
            # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            logger.info(f"Loaded image: {image_path} ({image.size[0]}x{image.size[1]})")
            return image
        except Exception as e:
            raise ValueError(f"Failed to load image {image_path}: {e}")

    def preprocess_images(self, person_image: Image.Image, clothing_image: Image.Image,
                         target_size: Tuple[int, int] = (512, 512)) -> Tuple[Image.Image, Image.Image]:
        """
        Preprocess person and clothing images for the try-on model.

        Args:
            person_image: PIL Image of the person
            clothing_image: PIL Image of the clothing item
            target_size: Target size for resizing (width, height)

        Returns:
            Tuple of preprocessed (person_image, clothing_image)
        """
        # Resize images while maintaining aspect ratio
        person_resized = self._resize_and_pad(person_image, target_size)
        clothing_resized = self._resize_and_pad(clothing_image, target_size)

        logger.info(f"Preprocessed images to {target_size}")
        return person_resized, clothing_resized

    def _resize_and_pad(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        Resize image to fit within target size while maintaining aspect ratio,
        then pad to exact target size.

        Args:
            image: PIL Image to resize
            target_size: Target size (width, height)

        Returns:
            Resized and padded PIL Image
        """
        # Calculate scaling factor to fit within target size
        scale = min(target_size[0] / image.width, target_size[1] / image.height)
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)

        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Create new image with target size and paste resized image in center
        new_image = Image.new('RGB', target_size, (0, 0, 0))
        paste_x = (target_size[0] - new_width) // 2
        paste_y = (target_size[1] - new_height) // 2
        new_image.paste(resized, (paste_x, paste_y))

        return new_image

    def generate_try_on(self, person_image_path: str, clothing_image_path: str,
                       output_path: Optional[str] = None) -> Image.Image:
        """
        Generate a try-on image by combining person and clothing photographs.

        Args:
            person_image_path: Path to person photograph
            clothing_image_path: Path to clothing photograph
            output_path: Optional path to save the result

        Returns:
            PIL Image of the try-on result
        """
        logger.info("Starting virtual try-on process")

        # Load and validate input images
        person_image = self.load_and_validate_image(person_image_path)
        clothing_image = self.load_and_validate_image(clothing_image_path)

        # Preprocess images
        person_processed, clothing_processed = self.preprocess_images(person_image, clothing_image)

        # Generate try-on result
        if self.initialized and DASHSCOPE_AVAILABLE:
            result_image = self._call_dashscope_qwen(person_processed, clothing_processed)
        else:
            # Fallback to demo/simulation mode
            result_image = self._demo_try_on(person_processed, clothing_processed)

        # Save result if output path provided
        if output_path:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            result_image.save(output_path)
            logger.info(f"Saved try-on result to: {output_path}")

        return result_image

    def _call_dashscope_qwen(self, person_image: Image.Image, clothing_image: Image.Image) -> Image.Image:
        """
        Call Alibaba Cloud Qwen for virtual try-on generation using DashScope.

        Args:
            person_image: Preprocessed person image
            clothing_image: Preprocessed clothing image

        Returns:
            Generated try-on image
        """
        if not self.initialized:
            logger.warning("DashScope not initialized. Falling back to demo mode.")
            return self._demo_try_on(person_image, clothing_image)

        logger.info("Calling DashScope Qwen-Image-2.0 for try-on generation using MultiModalConversation")

        # Convert PIL images to base64 with data URL format
        person_base64 = self._image_to_base64(person_image)
        clothing_base64 = self._image_to_base64(clothing_image)

        person_data_url = f"data:image/png;base64,{person_base64}"
        clothing_data_url = f"data:image/png;base64,{clothing_base64}"

        # Construct the messages for multi-modal conversation
        # Following the pattern from the example file
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": person_data_url},
                    {"image": clothing_data_url},
                    {"text": "Generate a realistic image showing the person from the first image wearing the dress, shoes, t-shirt, trousers, jewelerry items from the second image. Preserve the pose of the girl. Create a seamless virtual try-on result where the clothing fits naturally on the person."}
                ]
            }
        ]

        try:
            # Call the MultiModalConversation API
            response = MultiModalConversation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format='message',
                stream=False,
                watermark=False,
                prompt_extend=True,
                negative_prompt="Low resolution, low quality, distorted limbs, malformed fingers, oversaturated colors, wax-figure appearance, lack of facial detail, excessive smoothness, AI-looking artifacts, chaotic composition, blurry or warped text.",
                size='1024*1024'
            )

            if response.status_code == 200:
                # Extract the image URL from response following the example format
                if 'output' in response and 'choices' in response['output'] and len(response['output']['choices']) > 0:
                    choice = response['output']['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        for content_item in choice['message']['content']:
                            if 'image' in content_item:
                                result_url = content_item['image']

                                # Download the generated image
                                import requests
                                img_response = requests.get(result_url)
                                if img_response.status_code == 200:
                                    result_image = Image.open(io.BytesIO(img_response.content))
                                    logger.info("Successfully generated try-on image with Qwen-Image-2.0")
                                    return result_image
                                else:
                                    logger.error(f"Failed to download generated image: {img_response.status_code}")
                                    break

                logger.error("Could not extract image URL from response")
                logger.info("Falling back to demo mode due to response parsing failure.")
                return self._demo_try_on(person_image, clothing_image)
            else:
                logger.error(f"DashScope Qwen API error: {response.status_code}, {response.code}: {response.message}")
                # Check if it's an authentication error
                if response.status_code == 401 and "InvalidApiKey" in str(response.code):
                    logger.warning("Invalid API key detected. Falling back to demo mode.")
                    self.initialized = False  # Disable further API calls
                return self._demo_try_on(person_image, clothing_image)

        except Exception as e:
            logger.error(f"Error calling DashScope Qwen: {e}")
            logger.info("Falling back to demo mode due to exception.")
            return self._demo_try_on(person_image, clothing_image)

    def _demo_try_on(self, person_image: Image.Image, clothing_image: Image.Image) -> Image.Image:
        """
        Demo/simulation mode for try-on generation.
        In a real implementation, this would be replaced with actual AI model inference.

        Args:
            person_image: Preprocessed person image
            clothing_image: Preprocessed clothing image

        Returns:
            Combined/demo try-on image
        """
        logger.info("Running in demo mode - creating composite image")

        # Create a simple composite for demonstration purposes
        # In reality, this would be replaced with actual AI-generated content
        result = person_image.copy()

        # Simple overlay approach for demo (not realistic try-on, just for illustration)
        # Resize clothing to fit person's torso area approximately
        clothing_width = int(person_image.width * 0.4)
        clothing_height = int(clothing_image.height * (clothing_width / clothing_image.width))
        clothing_resized = clothing_image.resize((clothing_width, clothing_height), Image.Resampling.LANCZOS)

        # Position clothing on person (approximate torso placement)
        paste_x = (person_image.width - clothing_width) // 2
        paste_y = int(person_image.height * 0.3)  # Roughly torso level

        # Create a mask for better blending (simple approach)
        result.paste(clothing_resized, (paste_x, paste_y), clothing_resized if clothing_resized.mode == 'RGBA' else None)

        # Add some visual indication this is a demo
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(result)
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None

        demo_text = "DEMO MODE - Replace with actual AI model"
        text_bbox = draw.textbbox((0, 0), demo_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Position text at bottom
        text_x = (result.width - text_width) // 2
        text_y = result.height - text_height - 10

        # Semi-transparent background for text
        text_bg = [(text_x - 5, text_y - 5), (text_x + text_width + 5, text_y + text_height + 5)]
        draw.rectangle(text_bg, fill=(0, 0, 0, 128))
        draw.text((text_x, text_y), demo_text, fill=(255, 255, 255), font=font)

        return result

    def _image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string.

        Args:
            image: PIL Image to convert

        Returns:
            Base64 encoded image string
        """
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return base64.b64encode(img_bytes.read()).decode('utf-8')


def main():
    """
    Main function for command-line usage.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Virtual Try-On Application")
    parser.add_argument("--person", required=True, help="Path to person photograph")
    parser.add_argument("--clothing", required=True, help="Path to clothing photograph")
    parser.add_argument("--output", help="Path to save the result (optional)")
    parser.add_argument("--api-key", help="Alibaba Cloud DashScope API key (for Qwen-Image-2.0)")
    parser.add_argument("--demo", action="store_true", help="Force demo mode")

    args = parser.parse_args()

    # Initialize the try-on application
    tryon_app = VirtualTryOn(
        api_key=args.api_key if not args.demo else None
    )

    # Generate try-on
    try:
        result_image = tryon_app.generate_try_on(
            person_image_path=args.person,
            clothing_image_path=args.clothing,
            output_path=args.output
        )

        if args.output:
            print(f"Try-on image saved to: {args.output}")
        else:
            # Show image info if not saved
            print(f"Generated try-on image: {result_image.size[0]}x{result_image.size[1]}")
            print("Tip: Use --output to save the result to a file")

    except Exception as e:
        logger.error(f"Error during try-on generation: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())