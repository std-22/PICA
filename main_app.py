import random
from style_transfer import StyleTransfer
import streamlit as st
from PIL import Image
import os


def set_appearance():
    """Configurate web-site settings."""
    st.set_page_config(page_title='PICA',
                       page_icon=Image.open('assets/Pica_logo_plus.jpg'),
                       layout="wide")
    st.title('PICA')
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)


set_appearance()
scaler = st.slider('Intensity', 0, 100)
style_transfer = StyleTransfer()

if not os.path.isdir('generated_images'):
    os.mkdir('generated_images')

col1, col2, col3 = st.columns(3)
with col1:
    src_image = st.file_uploader(label='Source image', type=['png', 'jpg', 'webp'])
    if src_image:
        src_image = Image.open(src_image)
        st.image(src_image, caption='Source image')

with col2:
    style_image = st.file_uploader(label='Style image', type=['png', 'jpg', 'webp'])
    if style_image:
        style_image = Image.open(style_image)
        st.image(style_image, caption='Style image')

with col3:
    if st.button('Generate') and style_image and src_image:
        stylized_image = style_transfer.transfer_style(src_image, style_image, scaler / 100 * (1080 - 360) + 360)
        st.image(stylized_image)
        stylized_image.save(f'generated_images/{str(random.randint(0, 10000))}.png')

if st.button('Clean history'):
    for image in os.listdir('generated_images'):
        os.remove(f'generated_images/{image}')

if len(os.listdir('generated_images')) > 0:
    stylized_images = [Image.open('generated_images/' + image) for image in os.listdir('generated_images')]
    COLS_IN_GRID = 5
    cols = st.columns(COLS_IN_GRID)
    for index, image in enumerate(stylized_images):
        with cols[index % COLS_IN_GRID]:
            st.image(stylized_images[index], caption='Stylized image', use_column_width='always')
            with open(image.filename, 'rb') as file:
                btn = st.download_button(label='Download',
                                         data=file,
                                         file_name=f'stylized_{image}',
                                         mime='image/png',
                                         key=random.randint(0, 10000))
