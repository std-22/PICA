import os
import random
import tempfile
import time

import cv2 as cv
import numpy as np
import streamlit as st
from PIL import Image

from algorithms.image_enhancer import ImageEnhancer
from algorithms.style_transfer import StyleTransfer


class VideoApp:
    def __init__(self, src_video=None, style_img=None):
        self.src_video = src_video
        self.style_img = style_img

    def run(self) -> None:
        self.create_folder()
        self.upload()
        self.transfer_style()
        self.download()

    def create_folder(self) -> None:
        """Create folders if they do not exist"""
        if not os.path.isdir('stylized_videos/'):
            os.mkdir('stylized_videos/')

    def upload(self) -> None:
        """Displays two button for content and style image uploading."""
        col1, col2 = st.columns(2)
        with col1:
            src_video = st.file_uploader(label='Source video', type=['mp4'])
            if src_video:
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(src_video.read())
                self.src_video = cv.VideoCapture(tfile.name)
                st.video(src_video)

        with col2:
            style_image = st.file_uploader(label='Style image', type=['png', 'jpg', 'webp'])
            if style_image:
                self.style_img = Image.open(style_image)
                st.image(self.style_img, caption='Style image')

    def transfer_style(self) -> None:
        stf = StyleTransfer()
        img_enhancer = ImageEnhancer()
        scale = self.__slider()
        if self.src_video and st.button(label='Transfer'):
            fps = int(self.src_video.get(cv.CAP_PROP_FPS))
            frame_width = int(self.src_video.get(cv.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.src_video.get(cv.CAP_PROP_FRAME_HEIGHT))
            out = cv.VideoWriter(f'stylized_videos/stylized_video.avi',
                                 cv.VideoWriter_fourcc(*'XVID'),
                                 fps,
                                 (frame_width, frame_height))
            cap = self.src_video
            length = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
            img_placeholder = st.empty()
            timer_placeholder = st.empty()
            bar = st.progress(0)
            for i in range(length):
                ret, frame = cap.read()
                if ret:
                    try:
                        start = time.perf_counter()
                        stylized_frame = stf.transfer_style(frame, self.style_img,
                                                            (100 - scale) / 100 * (1080 - 360) + 360)
                        enhanced_frame = img_enhancer.reproduce_shape(stylized_frame, (frame_width, frame_height))
                        end = time.perf_counter()
                        img_placeholder.image(stylized_frame)
                        out.write(np.asarray(enhanced_frame))
                        time_to_wait = int((end - start) * (length - i) // 60)
                        timer_placeholder.write(
                            f'{i}/{length} frames are processed. Style transfer will end in {time_to_wait} minutes')
                        bar.progress(i / length)
                    except Exception:
                        pass
            cap.release()
            cv.destroyAllWindows()

    def __slider(self) -> int:
        """Display slider.
        Returns:
            intensity value (int)"""
        return st.slider(label='Interpolation', min_value=0, max_value=100, value=50, step=1)

    def download(self) -> None:
        if os.path.exists('stylized_videos/stylized_video.avi'):
            with open('stylized_videos/stylized_video.avi', 'rb') as file:
                with st.container():
                    st.download_button(label='Download',
                                       data=file,
                                       file_name=f'stylized_video.avi',
                                       key=random.randint(0, 10000))
