import random
from style_transfer import StyleTransfer
import streamlit as sl
from PIL import Image
import os
import shutil


def set_appearance():
    """Configurate web-site settings."""
    sl.set_page_config(page_title='PICA',
                       page_icon=Image.open('C:/Users/User/Desktop/python/PICA/assets/Pica_logo_plus.jpg'),
                       layout="wide")
    sl.title('PICA')
    sl.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)


set_appearance()
scaler = sl.slider('Intensity', 0, 100)
style_transfer = StyleTransfer()

if not os.path.isdir('generated_images'):
    os.mkdir('generated_images')

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
    if sl.button('Generate') and style_image and src_image:
        stylized_image = style_transfer.transfer_style(src_image, style_image, scaler / 100 * (1080 - 360) + 360)
        sl.image(stylized_image)
        stylized_image.save(f'generated_images/{str(random.randint(0, 10000))}.png')

if sl.button('Clean history'):
    for image in os.listdir('generated_images'):
        os.remove(f'generated_images/{image}')

if len(os.listdir('generated_images')) > 0:
    for col, image in zip(sl.columns(len(os.listdir('generated_images'))), os.listdir('generated_images')):
        with col:
            style_image = Image.open('generated_images/' + image)
            sl.image(style_image, caption='Stylized image', use_column_width='always')
            with open('generated_images/' + image, 'rb') as file:
                btn = sl.download_button(label='Download',
                                         data=file,
                                         file_name=f'stylized_{image}',
                                         mime='image/png',
                                         key=random.randint(0, 10000))
