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
import matplotlib.pyplot as plt

# Ставим подпись и иконку для кастомизации вкладки
im = Image.open("ssd.ico")
st.set_page_config(
    page_title="Task Search (Beta)",
    page_icon=im,
    layout="wide",
)

# Исходящий вебхук для работы с битриксом
webhook = ""
b = Bitrix(webhook)

# Настройка шрифта на странице
st.markdown(
        """
        <style>
@font-face {
  font-family: 'Circe';
  font-style: normal;
  font-weight: 13;
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

# Настройка отступа меню выбора страницы
page_bckg_sidebar = """
                        <style>
                                [class="css-1oe5cao e1fqkh3o9"]{
                                padding-top: 20px;
                                }
                        </style>
            
                        """
st.markdown(page_bckg_sidebar, unsafe_allow_html=True)

# Добавление фона
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

# Загрузка картинки для профиля, когда у пользователя нет фото
no_im = Image.open("no_photo.png")

# Массив с ФИО
persone_list = ['Булатов Артем Эльмирович', 'Медведева Ольга Владимировна', 'Вокин Геннадий Олегович', 'Морозов Алексей Владимирович', 'Кравченко Дмитрий Викторович']

# Виджет для выбора пользователя
respname = st.sidebar.selectbox('**Выберите сотрудника:**', persone_list)

# Добавление колонн на страницу
col1, col2, col3, col4 = st.columns(4)
result = respname.split()
try:
    last_name = result[0]
    name = result[1]
    second_name = result[2]
        
    user = b.get_all('user.search',
            params={
                    'FILTER': {"LAST_NAME": name, "NAME": last_name, "SECOND_NAME": second_name}
            }
                    )

    id_user = user[0]['ID']
    pers_photo = user[0]['PERSONAL_PHOTO']
    phone = user[0]['PERSONAL_MOBILE']
    email = user[0]['EMAIL']
    work_position = user[0]['WORK_POSITION']
    user_name = user[0]['NAME']
    user_last_name = user[0]['LAST_NAME']
    user_second_name = user[0]['SECOND_NAME']
    
    with col4:
        st.image(pers_photo, width=200)
except AttributeError:
    with col4:
        st.image(no_im, width=200)


container_info_info_phone = '**Мобильный телефон:** ' + phone
container_info_info_email = '**Почтовый адресс:** ' + email
container_info_info_work = '**Должность:** ' + work_position


with col3:
    container_info = st.container()
    container_info.write(container_info_info_phone)
    container_info.write(container_info_info_email)
    container_info.write(container_info_info_work)
with col2:
    st.title('')
with col1:
        st.markdown('**За какой период сформируем отчет?**')

        # Вводим дату
        date_start = st.date_input('От:', datetime.date(2023, 2, 5) ,key='date3')
        day = date_start.strftime('%d.%m.%Y')
        date_start = day


        date_end = st.date_input('До:', datetime.date(2023, 2, 5), key='date4')
        day = date_end.strftime('%d.%m.%Y')
        date_end = day
if(st.button('Принять')):
    expander = st.expander('Открой меня', expanded=False)
    with st.spinner('Подождите'): # Спиннер будет крутится, пока не отработает скрипт
        # По нажатию кнопки, забираем внесенные пользователем данные и вставляем в запрос
            page_bckg_col = """
                        <style>
                                [class="css-1v0mbdj etr89bj1"] {
                                        border: solid 3px black;
                                        border-radius: 50%;
                                               }

                                img {
                                    border-radius: 50%;
                                }
                        </style>
            
                        """
            st.markdown(page_bckg_col, unsafe_allow_html=True)
            
            ts_date_start = date_start.title()
            ts_date_end = date_end.title()
            ts_data = b.get_all('user.search',
                        params={
                                'FILTER': {"LAST_NAME": user_last_name, "NAME": user_name, "SECOND_NAME": user_second_name}
                        }
                                )
            ts_user_id = ts_data[0]['ID']
            
            tasks = b.get_all('tasks.task.list',
            params={
                'filter': {'RESPONSIBLE_ID': ts_user_id, '>=UF_CLOSED_PLAN_DATE': ts_date_start, '<=UF_CLOSED_PLAN_DATE': ts_date_end},
                'select': ['ID', 'CREATED_DATE', 'DEADLINE', 'CREATED_BY', 'RESPONSIBLE_ID', 'TITLE', 'STATUS']
            }
                    )
            
            # Формируем json из строки
            json_tasks = json.dumps(tasks)
            tasks_pad = pd.read_json(json_tasks)
            
            # Вытаскиваем из JSON'a только то, что нам нужно
            task_id = tasks_pad['id'].tolist() # Тут массив из айдишников задач. Ниже по аналогии
            resp_id = tasks_pad['responsibleId'].tolist()
            create_id = tasks_pad['createdBy'].tolist()
            tile_task = tasks_pad['title'].tolist()
            deadline_task = tasks_pad['deadline'].tolist()
            create_task = tasks_pad['createdDate'].tolist()
            task_status = tasks_pad['status'].tolist()
            task_sub_status = tasks_pad['subStatus'].tolist()
            
            # Тут мы меняем значения статуса задачи с числа на строку
            for index, item in enumerate(task_status):
                if item == 1:
                    task_status[index] = 'Новая'

            for index, item in enumerate(task_status):
                if item == 2:
                    task_status[index] = 'Ждет выполнения'

            for index, item in enumerate(task_status):
                if item == 3:
                    task_status[index] = 'Выполняется'

            for index, item in enumerate(task_status):
                if item == 4:
                    task_status[index] = 'Ждет контроля'
                
            for index, item in enumerate(task_status):
                if item == 5:
                    task_status[index] = 'Выполнена'    

            for index, item in enumerate(task_sub_status):
                if item == -1:
                    task_sub_status[index] = 'Просрочена'

            for index, item in enumerate(task_sub_status):
                if item == -3:
                    task_sub_status[index] = 'Почти просрочена'

            for index, item in enumerate(task_sub_status):
                if item == -2:
                    task_sub_status[index] = 'Не просмотренная задача'

            for index, item in enumerate(task_sub_status):
                if item == 1:
                    task_sub_status[index] = 'Новая'

            for index, item in enumerate(task_sub_status):
                if item == 2:
                    task_sub_status[index] = 'Ждет выполнения'

            for index, item in enumerate(task_sub_status):
                if item == 3:
                    task_sub_status[index] = 'Выполняется'

            for index, item in enumerate(task_sub_status):
                if item == 4:
                    task_sub_status[index] = 'Ждет контроля'
                
            for index, item in enumerate(task_sub_status):
                if item == 5:
                    task_sub_status[index] = 'Выполнена' 


            check_resp_mail = []
            
            # Вытаскиваем мэйл пользователя
            for i in resp_id:
                user = b.get_all('user.get',
                    params={
                            'FILTER': {'ID': i}
                    }
                            )
                email = user[0]["EMAIL"] 
                check_resp_mail.append(email)

            
            check_creators_mail = []
            
            # Вытаскиваем мэйл пользователя
            for i in create_id:
                user = b.get_all('user.get',
                    params={
                            'FILTER': {'ID': i}
                    }
                            )
                email = user[0]["EMAIL"] 
                check_creators_mail.append(email)


            check_title = []
            
            # Вытаскиваем описание задачи
            for i in task_id:
                task_get = b.get_all('tasks.task.get',
                    params={
                            'taskId': i, 'select': ['TITLE']
                    }
                                )
                title = task_get['task']['title'] 
                check_title.append(title)


            check_resp_name = []
            
            # Вытаскиваем ФИО пользователя
            for i in resp_id:
                user = b.get_all('user.get',
                    params={
                            'FILTER': {'ID': i}
                    }
                            )
                last_name = user[0]["LAST_NAME"]
                name = user[0]["NAME"]
                second_name = user[0]["SECOND_NAME"]
                check_resp_name.extend([last_name + ' ' + name + ' ' + second_name])


            check_creators_name = []
            
            # Вытаскиваем ФИО пользователя
            for i in create_id:
                user = b.get_all('user.get',
                    params={
                            'FILTER': {'ID': i}
                    }
                            )
                last_name = user[0]["LAST_NAME"]
                name = user[0]["NAME"]
                second_name = user[0]["SECOND_NAME"]
                check_creators_name.extend([last_name + ' ' + name + ' ' + second_name])


            actual_date_deadline = []
            
            # Вытаскиваем дедлайн и придаем читаемый формат
            for i in deadline_task:
                act_day_dead = parse(i, ignoretz=True)
                actual_dead = act_day_dead.strftime('%d.%m.%Y %H:%M')
                actual_date_deadline.extend([actual_dead])

            actual_date_create = []
            
            # Вытаскиваем дату создания задачи и придаем читаемый формат
            for i in create_task:
                act_day_crea = parse(i, ignoretz=True)
                actual_crea = act_day_crea.strftime('%d.%m.%Y %H:%M')
                actual_date_create.extend([actual_crea])
            
            
            # Зададим красивую оболочку для вывода нашей информации на экран
            page_bckg = """
                            <style>
                                    [class='block-container css-z5fcl4 egzxvld4']{
                                    wight: 550px;
                                    padding-left: 20px;
                                    padding-top: 20px;
                                    padding-bottom: 20px;
                                    }
                            </style>
                
                            """
            st.markdown(page_bckg, unsafe_allow_html=True)


            tab1, tab2= st.tabs([":clipboard: Список задач ", " :chart_with_upwards_trend: Свод "])
            # Тут мы пробегаемся по массивам циклом и формируем каждую задачу по очереди

            with tab1:    
                with st.container():
                    for mail_r, mail_c, title, chck_id_task, chck_id_resp, deadl, mail_crea_name, mail_resp_name, ts_task_status, ts_task_sub_status in zip(check_resp_mail, check_creators_mail, check_title, task_id, resp_id, actual_date_deadline, check_creators_name, check_resp_name, task_status, task_sub_status):
                        ts_link = 'https://portal.sevensuns.ru/company/personal/user/'+ str(chck_id_resp)+'/tasks/task/view/'+ str(chck_id_task) + '/'
                        st.subheader('№ '+ str(chck_id_task))
                        st.markdown('**Постановщик:**')
                        st.text(mail_crea_name)
                        st.markdown('**Ответственный:**')
                        st.text(mail_resp_name)
                        st.markdown('**Название задачи:**')
                        st.text(title)
                        st.markdown('**Крайний срок выполнения задачи:**')
                        st.text(deadl)
                        st.markdown('**Ссылка на задачу**' + '    ------------->>> [:globe_with_meridians:](%s)' % ts_link)
                        if ts_task_status == 'Выполнена' and ts_task_sub_status == 'Выполнена':
                            st.success(ts_task_status)
                        elif ts_task_sub_status == 'Просрочена':
                            st.error(ts_task_status + ' , ' + ts_task_sub_status)
                        elif ts_task_status == 'Ждет выполнения':
                            st.warning(ts_task_status)
                        elif ts_task_status == 'Выполняется':
                            st.warning(ts_task_status)
                        elif ts_task_status == 'Ждет контроля':
                            st.warning(ts_task_status)
                #Считаем кол-во задач
                with tab2:
                    number_task = len(task_id)
                    count = 0
                    count_complete = 0
                    count_in_prog = 0
                    count_wait_ctr = 0
                    for i in task_status:
                        if i == 'Выполнена':
                            count_complete += 1
                    for i in task_sub_status:
                        if i == 'Просрочена':
                            count += 1
                    for i in task_status:
                        if i == 'Ждет выполнения':
                            count_in_prog += 1
                    for i in task_status:
                        if i == 'Ждет контроля':
                            count_wait_ctr += 1
                    # st.markdown('**:red[Просроченных задач:]**')
                    # st.markdown(count)
                    # st.markdown('**:green[Выполненных задач:]**')
                    # st.markdown(count_complete)
                    # st.markdown('**Всего задач:**')
                    # st.markdown(number_task)

                    data = np.array([number_task,count, count_complete, count_in_prog, count_wait_ctr])
                    df = pd.DataFrame([data], columns=['Всего задач','Просрочено','Выполнено', 'Ждут выполнения', 'Ждут контроля'], index=None)

                    st.dataframe(df)

# Обводим фото профиля в круг с рамкой
page_bckg_col = """
                        <style>
                                [class="css-1v0mbdj etr89bj1"] {
                                        border: solid 3px black;
                                        border-radius: 50%;
                                               }

                                img {
                                    border-radius: 50%;
                                }
                        </style>
            
                        """
st.markdown(page_bckg_col, unsafe_allow_html=True)

# Даем прозрачный фон двум элементам на странице ("Список задач", "Свод")
page_bckg_itog = """
                        <style>
                                .st-hy {
                                    background: rgb(0 0 0 / 0%);
                                        }
                        </style>
            
                        """
st.markdown(page_bckg_itog, unsafe_allow_html=True)

####
