import os
import random
import tempfile
import time

import cv2 as cv
import numpy as np
import streamlit as st
from PIL import Image
from subprocess import Popen, PIPE

from algorithms import image_enhancer as ie
from algorithms.style_transfer import StyleTransfer


class VideoApp:
    def __init__(self, src_video=None, style_img=None):
        st.session_state['video_status'] = None
        self.src_video = src_video
        self.style_img = style_img

    def run(self) -> None:
        self.create_folder()
        self.upload()
        self.transfer_style()
        self.assemble_video()
        self.download()

    def create_folder(self) -> None:
        """Create folders if they do not exist"""
        if not os.path.isdir('stylized_videos/'):
            os.mkdir('stylized_videos/')
        if not os.path.isdir('stylized_video_frames/'):
            os.mkdir('stylized_video_frames/')

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
                st.session_state['video_status'] = 'Uploaded'

        with col2:
            style_image = st.file_uploader(label='Style image', type=['png', 'jpg', 'webp'], key='video-style-image')
            if style_image:
                self.style_img = Image.open(style_image)
                st.image(self.style_img, caption='Style image')

    def transfer_style(self) -> None:
        stf = StyleTransfer()
        scale = self.__slider()
        if self.src_video and st.button(label='Transfer'):
            cap = cv.VideoCapture(self.src_video.name)
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
                        frame_rgb = Image.fromarray(np.asarray(enhanced_frame))
                        frame_rgb.save(f'stylized_video_frames/{i}.jpg')
                        end = time.perf_counter()
                        img_placeholder.image(enhanced_frame)
                        time_to_wait = int((end - start) * (length - i) // 60)
                        timer_placeholder.write(
                            f'{i + 1}/{length} frames are processed. Style transfer will end in {time_to_wait} minutes')
                        bar.progress((i + 1) / length)
                    except Exception as e:
                        st.write(e)
            timer_placeholder.write('Video style transfer is complete!')
            cap.release()
            st.session_state['video_status'] = 'Stylized'

    def __slider(self) -> int:
        """Display slider.
        Returns:
            intensity value (int)"""
        return st.slider(label='Interpolation', min_value=0, max_value=100, value=50, step=1)

    def assemble_video(self):
        if st.session_state['video_status'] == 'Stylized':
            cap = cv.VideoCapture(self.src_video.name)
            fps = int(cap.get(cv.CAP_PROP_FPS))
            cap.release()
            p = Popen(
                ['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', str(fps), '-i', '-', '-vcodec', 'mpeg4',
                 '-qscale', '5', '-r', str(fps), 'stylized_videos/pica-stylized-video.mp4'], stdin=PIPE)
            bar = st.progress(0)
            directory = sorted(os.listdir('stylized_video_frames'), key=len)
            length = len(directory)
            placeholder = st.empty()
            placeholder.write(f'Video assembling in process')
            for index, image in enumerate(directory):
                frame = Image.open('stylized_video_frames/' + image)
                frame.save(p.stdin, 'JPEG')
                bar.progress((index + 1) / length)
            placeholder.write('Video assembling is complete')
            p.stdin.close()
            p.wait()
            st.session_state['video_status'] = 'Assembled'

    def download(self) -> None:
        if os.path.exists('stylized_videos/pica-stylized-video.mp4'):
            with open('stylized_videos/pica-stylized-video.mp4', 'rb') as file:
                with st.container():
                    if st.download_button(label='Download',
                                          data=file,
                                          file_name=f'pica-stylized-video.mp4',
                                          key=random.randint(0, 10000)):
                        st.session_state['video_status'] = 'DOWNLOADED'

    def clean_directory(self):
        if st.session_state['video_status'] == 'DOWNLOADED' and os.path.exists('stylized_video_frames'):
            for file in os.listdir('stylized_video_frames'):
                os.remove('stylized_video_frames/' + file)
