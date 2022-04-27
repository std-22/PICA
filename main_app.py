from style_transfer import StyleTransfer
import streamlit as sl
from PIL import Image

sl.set_page_config(page_title='PICA')
sl.title('PICA')

scaler = sl.slider('Интенсивность преобразований', 240, 720, 480)

col1, col2, col3 = sl.columns(3)
with col1:
    src_image = sl.file_uploader(label='Source image', type=['png', 'jpg', 'webp'])
    if src_image:
        src_image = Image.open(src_image)
        sl.image(src_image, caption='Source image')

with col2:
    style_image = sl.file_uploader(label='Style image', type=['png', 'jpg', 'webp'])
    if style_image:
        style_image = Image.open(style_image)
        sl.image(style_image, caption='Style image')

with col3:
    if style_image and src_image and sl.button('Generate'):
        style_transfer = StyleTransfer()
        stylized_image = style_transfer.transfer_style(src_image, style_image, scaler)
        sl.image(stylized_image, caption='Stylized image')