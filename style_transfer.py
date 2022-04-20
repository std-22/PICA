import tensorflow_hub as hub
import tensorflow as tf
from matplotlib import pyplot as plt
import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageEnhance
import requests

plt.rcParams.update({'font.size': 22})


class StyleTransfer:
    """Transfer style from one image into another.

    Args:
      model - trained model for image style transfer.
    """

    def __init__(self, model):
        self.model = model

    def transfer_style(self, content_image: str, style_image: str, scaler):
        """Transfer style from style image into content image.

        Args:
          content_image (str) - source image.
          style_image (str) - image with specific style.
          scaler (int) - intensity of processing.

        Returns:
          stylized_image (PIL.Image) - stylized source image.
        """
        max_dim = scaler
        try:
            content_image = Image.open(content_image)
            style_image = Image.open(style_image)
        except Exception as e:
            raise e
        content_image = self.__img_to_tensor(content_image, max_dim)
        style_image = self.__img_to_tensor(style_image, max_dim)
        stylized_image = self.model(tf.constant(content_image), tf.constant(style_image))[0]
        return self.__tensor_to_image(stylized_image)

    def __img_to_tensor(self, img, max_dim):
        """Converting image to tensor.

        Args:
            img (PIL.Image) - image.

        Returns:
            img (tensorflow.Tensor) - tensor from image.
        """
        img = tf.io.read_file(img.filename)
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.convert_image_dtype(img, tf.float32)

        shape = tf.cast(tf.shape(img)[:-1], tf.float32)
        long_dim = max(shape)
        scale = max_dim / long_dim

        new_shape = tf.cast(shape * scale, tf.int32)

        img = tf.image.resize(img, new_shape)
        img = img[tf.newaxis, :]
        return img

    def __tensor_to_image(self, tensor):
        """Converts tensor to image.

        Args:
          tensor (tensorflow.Tensor) - tensor with values of pixels.

        Returns:
          image (PIL.Image) - image getted from tensor.
        """
        tensor = tensor * 255
        tensor = np.array(tensor, dtype=np.uint8)
        if np.ndim(tensor) > 3:
            assert tensor.shape[0] == 1
            tensor = tensor[0]
        return Image.fromarray(tensor)

    @staticmethod
    def show_images(images, figsize=(15, 15)):
        """Demonstrates content image, style image and stylized image.

        Args:
          images (dict) - title as key and image as value.
          figsize (tuple) - size of each figure.
        """
        fig, ax = plt.subplots(1, len(images), figsize=figsize)

        for index, (title, image) in enumerate(images.items()):
            ax[index].imshow(image)
            ax[index].title.set_text(title)
            ax[index].axis('off')

    @staticmethod
    def increase_saturation(image, coefficient=1.25):
        """Increase saturation of input image.

        Args:
          image (PIL.Image) - input image.
          coefficient (float) - coefficient for saturation increase

        Returns:
          image (PIL.Image)
        """
        return ImageEnhance.Color(image).enhance(coefficient)


if __name__ == '__main__':
    model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
    style_transfer = StyleTransfer(model)
    source_image_url = "Content Images/NightSight.jpg"
    style_image_url = "Style Images/VanGoghStarryNight.jpg"
    stylized_image = style_transfer.transfer_style(source_image_url, style_image_url, 540)
    stylized_image = StyleTransfer.increase_saturation(stylized_image)
    StyleTransfer.show_images({'Source image': Image.open(source_image_url),
                                'Style image': Image.open(style_image_url),
                                'Stylized image': stylized_image})
