from PIL import Image, ImageEnhance


def reproduce_shape(image: Image, target_size: tuple) -> Image:
    """Reproducing source image size
    Args:
        image (PIL.Image) - image to resize.
        target_size (tuple) - target size

    Returns:
        PIL.Image - resized image.
    """
    return image.resize(size=target_size, resample=Image.BICUBIC)


def increase_saturation(image, coefficient=1.25) -> Image:
    """Increase saturation of input image.

    Args:
        image (PIL.Image) - input image.
        coefficient (float) - coefficient for saturation increase

    Returns:
        image (PIL.Image) - image with increased saturation.
    """
    return ImageEnhance.Color(image).enhance(coefficient)
