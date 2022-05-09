import os
import random
import socket
from requests import get

import streamlit as st
from PIL import Image

from style_transfer import StyleTransfer


class Application:
    def __init__(self, source_img=None, style_img=None):
        self.source_img = source_img
        self.style_img = style_img
        self.user_ip = get('https://api.ipify.org').text

    def run(self):
        self.set_config()
        self.image_upload()
        self.generate()
        self.history()

    def set_config(self):
        """Configurate web-site settings."""
        st.set_page_config(page_title='PICA',
                           page_icon=Image.open('assets/Pica_logo_plus.jpg'),
                           layout="wide")
        st.title('PICA')
        st.markdown(""" <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style> """, unsafe_allow_html=True)

    @st.cache(ttl=1800)
    def get_style_transfer(self):
        return StyleTransfer()

    def slider(self):
        return st.slider('Intensity', 0, 100)

    def image_upload(self):
        if not os.path.isdir('generated_images/' + self.user_ip):
            os.mkdir('generated_images/' + self.user_ip)

        col1, col2 = st.columns(2)
        with col1:
            src_image = st.file_uploader(label='Source image', type=['png', 'jpg', 'webp'])
            if src_image:
                self.source_img = Image.open(src_image)
                st.image(src_image, caption='Source image')

        with col2:
            style_image = st.file_uploader(label='Style image', type=['png', 'jpg', 'webp'])
            if style_image:
                self.style_img = Image.open(style_image)
                st.image(style_image, caption='Style image')

    def generate(self):
        scale = self.slider()
        if st.button('Generate') and self.source_img and self.style_img:
            stylized_image = self.get_style_transfer().transfer_style(self.source_img, self.style_img,
                                                                      scale / 100 * (1080 - 360) + 360)
            stylized_image.save(f'generated_images/{self.user_ip}/{str(random.randint(0, 10000))}.png')

    def history(self):
        path = 'generated_images/' + self.user_ip
        if len(os.listdir(path)) > 0 and st.button('Clean history'):
            for image in os.listdir(path):
                os.remove(f'{path}/{image}')

        if len(os.listdir(path)) > 0:
            stylized_images = [Image.open(path + '/' + image) for image in os.listdir(path)]
            COLS_IN_GRID = 5
            cols = st.columns(COLS_IN_GRID)
            for index, image in enumerate(stylized_images):
                with cols[index % COLS_IN_GRID]:
                    st.image(stylized_images[index], caption='Stylized image', use_column_width='always')
                    with open(image.filename, 'rb') as file:
                        with st.container():
                            st.download_button(label='Download',
                                               data=file,
                                               file_name=f'stylized_{image}',
                                               mime='image/png',
                                               key=random.randint(0, 10000))
                    if st.button(label='Delete', key=f'delete-button-{image.filename}'):
                        os.remove(f'{image.filename}')
                        st.experimental_rerun()
