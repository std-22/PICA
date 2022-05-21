import os
import random

import numpy as np
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu

from algorithms.image_enhancer import ImageEnhancer
from algorithms.style_transfer import StyleTransfer


class Application:
    def __init__(self, source_img=None, style_img=None):
        self.source_img = source_img
        self.style_img = style_img

    @st.cache(ttl=1800)
    def get_style_transfer(self):
        return StyleTransfer()

    @st.cache(ttl=1800)
    def get_image_enhancer(self):
        return ImageEnhancer

    def run(self) -> None:
        self.navigation()
        # self.image_upload()
        # self.generate()
        # self.history()

    def navigation(self) -> None:
        """Set navigation bar"""
        with st.sidebar:
            option = option_menu(menu_title='',
                                 options=['Image', 'Video', 'Gallery', 'Reference'],
                                 icons=['image', 'camera-video', 'archive', 'link'],
                                 orientation='vertical')
        if option == 'Image':
            self.image_upload()
            self.generate()
            self.history()
        elif option == 'Video':
            st.info('In development process! Coming soon...')
        elif option == 'Gallery':
            st.info('In development process! Coming soon...')
        else:
            st.info('Link to article')

    def set_config(self) -> None:
        """Configurate web-site settings."""
        st.set_page_config(page_title='PICA',
                           page_icon=Image.open('assets/Pica_logo_plus.jpg'),
                           layout="centered")
        st.title('PICA')
        st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
        st.markdown("<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> ",
                    unsafe_allow_html=True)

    def image_upload(self) -> None:
        if not os.path.isdir('generated_images/'):
            os.mkdir('generated_images/')

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

    def generate(self) -> None:
        scale = self.slider()
        if 'generate_button_status' not in st.session_state:
            st.session_state.generate_button_status = False
        try:
            placeholder = st.empty()
            generate_button = placeholder.button('Generate', disabled=False, key='1')
            if generate_button and self.source_img and self.style_img:
                generate_button = placeholder.button('Generate', disabled=True, key='2')
                st.session_state.generate_button_status = True
                stylized_image = self.get_style_transfer().transfer_style(self.source_img, self.style_img,
                                                                          scale / 100 * (1080 - 360) + 360)
                stylized_image = ImageEnhancer.reproduce_shape(stylized_image, self.source_img.size)
                stylized_image = ImageEnhancer.increase_saturation(stylized_image, 1.15)
                stylized_image.save(f'generated_images/{np.random.randint(0, 10000)}.png')
                generate_button = placeholder.button('Generate', disabled=False, key='3')
                placeholder.empty()
                st.experimental_rerun()
        except Exception as e:
            st.error('Something went wrong...')
            st.error('We are already working to fix this bug!')

    def slider(self) -> int:
        """Display slider.
        Returns:
            intensity value (int)"""
        return st.slider(label='Intensity', min_value=0, max_value=100, value=50, step=1)

    def history(self):
        """"""
        path = 'generated_images/'
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
                                               file_name=f'stylized_{image.filename}',
                                               mime='image/png',
                                               key=random.randint(0, 10000))
                    if st.button(label='Delete', key=f'delete-button-{image.filename}'):
                        os.remove(f'{image.filename}')
                        st.experimental_rerun()
