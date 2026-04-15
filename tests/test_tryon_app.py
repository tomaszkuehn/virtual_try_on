"""
Unit tests for the Virtual Try-On Application
"""
import unittest
import tempfile
import os
from PIL import Image
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tryon_app import VirtualTryOn


class TestVirtualTryOn(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.tryon_app = VirtualTryOn()  # No project ID for demo mode

        # Create temporary test images
        self.temp_dir = tempfile.mkdtemp()

        # Create a simple person-like image (red rectangle)
        self.person_image = Image.new('RGB', (400, 600), color='red')
        self.person_path = os.path.join(self.temp_dir, 'person.jpg')
        self.person_image.save(self.person_path)

        # Create a simple clothing-like image (blue rectangle)
        self.clothing_image = Image.new('RGB', (200, 150), color='blue')
        self.clothing_path = os.path.join(self.temp_dir, 'clothing.jpg')
        self.clothing_image.save(self.clothing_path)

    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_and_validate_image(self):
        """Test loading and validating images."""
        # Test valid image loading
        person_img = self.tryon_app.load_and_validate_image(self.person_path)
        self.assertIsInstance(person_img, Image.Image)
        self.assertEqual(person_img.mode, 'RGB')

        clothing_img = self.tryon_app.load_and_validate_image(self.clothing_path)
        self.assertIsInstance(clothing_img, Image.Image)
        self.assertEqual(clothing_img.mode, 'RGB')

    def test_load_nonexistent_image(self):
        """Test loading nonexistent image raises error."""
        with self.assertRaises(FileNotFoundError):
            self.tryon_app.load_and_validate_image('nonexistent.jpg')

    def test_preprocess_images(self):
        """Test image preprocessing."""
        person_img = self.tryon_app.load_and_validate_image(self.person_path)
        clothing_img = self.tryon_app.load_and_validate_image(self.clothing_path)

        person_processed, clothing_processed = self.tryon_app.preprocess_images(
            person_img, clothing_img, target_size=(256, 256)
        )

        # Check that images are resized to target size
        self.assertEqual(person_processed.size, (256, 256))
        self.assertEqual(clothing_processed.size, (256, 256))
        self.assertEqual(person_processed.mode, 'RGB')
        self.assertEqual(clothing_processed.mode, 'RGB')

    def test_generate_try_on_demo_mode(self):
        """Test try-on generation in demo mode."""
        result = self.tryon_app.generate_try_on(
            person_image_path=self.person_path,
            clothing_image_path=self.clothing_path
        )

        # Check that we get a valid image back
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, 'RGB')

        # In demo mode, we should get a reasonable size image
        # (exact size depends on preprocessing, but should be usable)
        self.assertGreater(result.width, 0)
        self.assertGreater(result.height, 0)

    def test_generate_try_on_with_output(self):
        """Test try-on generation with output file."""
        output_path = os.path.join(self.temp_dir, 'output.jpg')

        result = self.tryon_app.generate_try_on(
            person_image_path=self.person_path,
            clothing_image_path=self.clothing_path,
            output_path=output_path
        )

        # Check that result is valid
        self.assertIsInstance(result, Image.Image)

        # Check that output file was created
        self.assertTrue(os.path.exists(output_path))

        # Check that we can load the saved image
        saved_img = Image.open(output_path)
        self.assertIsInstance(saved_img, Image.Image)

    def test_image_to_bytes_conversion(self):
        """Test converting PIL Image to bytes."""
        person_img = self.tryon_app.load_and_validate_image(self.person_path)
        image_bytes = self.tryon_app._image_to_bytes(person_img)

        # Should get bytes back
        self.assertIsInstance(image_bytes, bytes)
        self.assertGreater(len(image_bytes), 0)

        # Should be able to convert back to image
        import io
        restored_img = Image.open(io.BytesIO(image_bytes))
        self.assertIsInstance(restored_img, Image.Image)


if __name__ == '__main__':
    unittest.main()