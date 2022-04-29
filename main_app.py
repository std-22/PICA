from style_transfer import StyleTransfer
import streamlit as sl
from PIL import Image


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
        style_transfer = StyleTransfer()
        stylized_image = style_transfer.transfer_style(src_image, style_image, scaler / 100 * (1080 - 360) + 360)
        sl.image(stylized_image, caption='Stylized image')
