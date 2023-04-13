import streamlit as st
import time
import numpy as np
from PIL import Image
import base64

im = Image.open("ssd.ico")
st.set_page_config(
    page_title="Task Search (Beta)",
    page_icon=im,
    layout="wide",
)

page_bckg_sidebar = """
                        <style>
                                [class='css-1oe5cao e1fqkh3o9']{
                                padding-top: 20px;
                                }
                        </style>
            
                        """
st.markdown(page_bckg_sidebar, unsafe_allow_html=True)

st.markdown(
        """
        <style>
@font-face {
  font-family: 'Circe';
  font-style: normal;
  font-weight: 400;
  src: url(Circe_Medium.woff) format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

    html, body, [class*="css"]  {
    font-family: 'Circe';
    }
    </style>

    """,
        unsafe_allow_html=True,
    )

# Добавление фонового изображения
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('ssd.jpg') 

st.title("Демо образец")
st.sidebar.header("Демо образец")
st.write(
    """Демонстрация тестового графика"""
)

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
last_rows = np.random.randn(1, 1)
chart = st.line_chart(last_rows)

for i in range(1, 101):
    new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    status_text.text("%i%% Complete" % i)
    chart.add_rows(new_rows)
    progress_bar.progress(i)
    last_rows = new_rows
    time.sleep(0.05)

progress_bar.empty()

st.button("Re-run")