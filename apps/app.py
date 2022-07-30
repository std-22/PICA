import streamlit as st
from PIL import Image, ImageFile
from streamlit_option_menu import option_menu

from apps.image_app import ImageApp
from apps.video_app import VideoApp

ImageFile.LOAD_TRUNCATED_IMAGES = True


class Application:

    def set_config(self) -> None:
        """Configurate web-site settings."""
        st.set_page_config(page_title='PICA',
                           page_icon=Image.open('assets/Pica_logo_plus.jpg'),
                           layout="centered")
        st.title('PICA')
        st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
        st.markdown("<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> ",
                    unsafe_allow_html=True)

    def run(self) -> None:
        """Run apps."""
        # self.create_folder()
        self.navigation()

    def navigation(self) -> None:
        """Set navigation bar"""
        with st.sidebar:
            option = option_menu(menu_title='',
                                 options=['Image', 'Video', 'Gallery', 'Reference'],
                                 icons=['image', 'camera-video', 'archive', 'link'],
                                 orientation='vertical')
        if option == 'Image':
            image_app = ImageApp()
            image_app.image_upload()
            image_app.generate()
            image_app.history()
        elif option == 'Video':
            video_app = VideoApp()
            video_app.run()
        elif option == 'Gallery':
            st.image('assets/examples.png')
        else:
            st.markdown('You can find the network in this [paper](https://arxiv.org/abs/1705.06830).')

    def slider(self) -> int:
        """Display slider.
        Returns:
            intensity value (int)"""
        return st.slider(label='Intensity', min_value=0, max_value=100, value=50, step=1)
