import os
import random

import streamlit as st
from PIL import Image

from algorithms import image_enhancer as ie
from algorithms.style_transfer import StyleTransfer


@st.experimental_singleton
def get_style_transfer() -> StyleTransfer:
    """"""
    return StyleTransfer()


class ImageApp:
    def __init__(self, source_img=None, style_img=None):
        super().__init__()
        self.source_img = source_img
        self.style_img = style_img

    def run(self):
        self.create_folder()
        self.image_upload()
        self.generate()
        self.history()

    def image_upload(self) -> None:
        """Displays two button for content and style image uploading."""
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

    def create_folder(self) -> None:
        """Create folders if they do not exist"""
        if not os.path.isdir('generated_images/'):
            os.mkdir('generated_images/')

    def generate(self) -> None:
        """Generates stylized image on button click and ave to history."""
        scale = self.slider()
        if 'generate_button_status' not in st.session_state:
            st.session_state.generate_button_status = False
        try:
            placeholder = st.empty()
            generate_button = placeholder.button('Generate', disabled=False, key='1')
            if generate_button and self.source_img and self.style_img:
                placeholder.button('Generate', disabled=True, key='2')
                st.session_state.generate_button_status = True
                stylized_image = get_style_transfer().transfer_style(self.source_img, self.style_img,
                                                                     (100 - scale) / 100 * (1080 - 360) + 360)
                stylized_image = ie.reproduce_shape(stylized_image, self.source_img.size)
                stylized_image = ie.increase_saturation(stylized_image, 1.15)
                stylized_image_number = len(os.listdir(f'generated_images')) if os.path.isdir(
                    f'generated_images') else 0
                stylized_image.save(f'generated_images/{stylized_image_number}.png')
                placeholder.button('Generate', disabled=False, key='3')
                placeholder.empty()
                st.experimental_rerun()
        except Exception as e:
            st.error('Something went wrong...')
            st.error('We are already working to fix this bug!')
            st.write(e)

    def slider(self) -> int:
        """Display slider.
        Returns:
            intensity value (int)"""
        return st.slider(label='Interpolation', min_value=0, max_value=100, value=50, step=1)

    def history(self):
        """Displays history of generated images"""
        path = f'generated_images'
        if len(os.listdir(path)) > 0 and st.button('Clean history'):
            for image in os.listdir(path):
                os.remove(f'{path}/{image}')

        if len(os.listdir(path)) > 0:
            stylized_images = [Image.open(path + '/' + image) for image in os.listdir(path)][::-1]
            cols_in_grid = 5
            cols = st.columns(cols_in_grid)
            for index, image in enumerate(stylized_images):
                with cols[index % cols_in_grid]:
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
