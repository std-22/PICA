from PIL import Image, ImageEnhance


class ImageEnhancer:
    @staticmethod
    def reproduce_shape(image: Image, target_size: tuple) -> Image:
        """"""
        return image.resize(size=target_size, resample=Image.BICUBIC)

    @staticmethod
    def increase_saturation(image, coefficient=1.25) -> Image:
        """Increase saturation of input image.

        Args:
          image (PIL.Image) - input image.
          coefficient (float) - coefficient for saturation increase

        Returns:
          image (PIL.Image)
        """
        return ImageEnhance.Color(image).enhance(coefficient)
