import streamlit as st
import pandas as pd
import numpy as np
from fast_bitrix24 import Bitrix
import json
import datetime
from dateutil.parser import parse
import base64
from PIL import Image
from streamlit_lottie import st_lottie
import requests
from streamlit_lottie import st_lottie_spinner

# Ставим подпись и иконку для кастомизации вкладки
im = Image.open("ssd.ico")
st.set_page_config(
    page_title="Task Search (Beta)",
    page_icon=im,
    layout="wide",
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

# Вебхук для доступа в Битрикс24
webhook = ""
b = Bitrix(webhook)


#############################################################################
#                       Поиск ID и Email по ФИО                             #
#############################################################################
page_bckg_sidebar = """
                        <style>
                                [class='css-1oe5cao e1fqkh3o9']{
                                padding-top: 20px;
                                }
                        </style>
            
                        """
st.markdown(page_bckg_sidebar, unsafe_allow_html=True)


# Добаляем в левый бар элементы с помощью втсавки sidebar
st.sidebar.image("ssd2.png", use_column_width=False)

with st.sidebar:
    path = "test.json"
    with open(path,"r") as file:
        url = json.load(file)

    st_lottie(url,
                reverse=True,
                height=None,  
                width=None,
                speed=1,  
                loop=True,  
                quality='high',
                key='ssd'
                ) 

# Название блока
st.sidebar.title('Поиск ID и Email по ФИО')

# Поля для ввода данных пользователем
last_name = st.sidebar.text_input('Введите фамилию: ', key='id1') # key нужен для того, чтоб сделать виджен уникальным
name = st.sidebar.text_input('Введите имя: ', key='id2')
second_name = st.sidebar.text_input('Введите отчество: ', key='id3')

# Переменные со строкой. В дальнейшем мы их подставим в вывод на экран
text_id = 'ID - '
text_mail = 'Email - '

# Делаем кнопку, по которой выполнится скрипт
if(st.sidebar.button('Принять')):
    try: # Ниже распишу, что это значит
        result_name = name.title()
        result_last_name = last_name.title()
        result_second_name = second_name.title()
        data = b.get_all('user.search',
                params={
                        'FILTER': {"LAST_NAME": result_last_name, "NAME": result_name, "SECOND_NAME": result_second_name}
                }
                        )
        user = data[0]['ID']
        mail = data[0]['EMAIL']
        fin_text_user = text_id + user # А вот и те самые переменные, которые мы объявляли ранее
        fin_text_mail = text_mail + mail
        
        # Выводим на экран результат отработки скрипта
        st.title(fin_text_user)
        st.title(fin_text_mail)
        st.success('Успешно :sunglasses:') # ":sunglasses:" это тэг со смайликом. Ниже аналогично
    except IndexError: # Обработчик ошибок try expert позволяет не выводить на экран ошибку в коде
        st.title('Упс... :heavy_exclamation_mark:')
        st.error('Пользователь не найден :fearful:')
