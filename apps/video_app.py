import os
import random
import tempfile
import time

import cv2 as cv
from vidgear.gears import WriteGear, VideoGear
import numpy as np
import streamlit as st
from PIL import Image

from algorithms import image_enhancer as ie
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
            src_video = st.file_uploader(label='Source video', type=['avi', 'mp4', 'gif'])
            if src_video:
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(src_video.read())
                self.src_video = tfile
                st.video(src_video)

        with col2:
            style_image = st.file_uploader(label='Style image', type=['png', 'jpg', 'webp'])
            if style_image:
                self.style_img = Image.open(style_image)
                st.image(self.style_img, caption='Style image')

    def transfer_style(self) -> None:
        stf = StyleTransfer()
        scale = self.__slider()
        if self.src_video and st.button(label='Transfer'):
            cap = cv.VideoCapture(self.src_video.name)
            fps = int(cap.get(cv.CAP_PROP_FPS))
            output_params = {'-fps': fps, '-fourcc': 'X264'}
            writer = WriteGear(output_filename="stylized_videos/output.mp4", compression_mode=False, **output_params)
            frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
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
                        resized_frame = ie.reproduce_shape(stylized_frame, (frame_width, frame_height))
                        enhanced_frame = ie.increase_saturation(resized_frame)
                        frame_rgb = np.asarray(enhanced_frame)[:, :, ::-1]
                        writer.write(frame_rgb, rgb_mode=True)
                        end = time.perf_counter()
                        img_placeholder.image(enhanced_frame)
                        time_to_wait = int((end - start) * (length - i) // 60)
                        timer_placeholder.write(
                            f'{i+1}/{length} frames are processed. Style transfer will end in {time_to_wait} minutes')
                        bar.progress((i + 1) / length)
                    except Exception as e:
                        st.write(e)
            timer_placeholder.write('Video style transfer is complete!')
            cap.release()
            writer.close()

    def __slider(self) -> int:
        """Display slider.
        Returns:
            intensity value (int)"""
        return st.slider(label='Interpolation', min_value=0, max_value=100, value=50, step=1)

    def download(self) -> None:
        if os.path.exists('stylized_videos/output.mp4'):
            with open('stylized_videos/output.mp4', 'rb') as file:
                with st.container():
                    st.download_button(label='Download',
                                       data=file,
                                       file_name=f'output.mp4',
                                       key=random.randint(0, 10000))
