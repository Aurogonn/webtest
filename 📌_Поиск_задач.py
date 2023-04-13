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


# Вебхук для доступа в Битрикс24
webhook = ""
b = Bitrix(webhook)

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


page_bckg_sidebar = """
                        <style>
                                [class='css-1544g2n e1fqkh3o4']{
                                padding-top: 20px;
                                }
                        </style>
            
                        """
st.markdown(page_bckg_sidebar, unsafe_allow_html=True)

#############################################################################
#          Поиск задач по исполнителю/постановщику по ФИО и дате            #
#############################################################################

st.sidebar.title('Поиск задач по исполнителю/постановщику по ФИО и дате')

# По аналогии с предыдущим блоком мы добавляем в боковую панель виджеты для воода данных
ts_last_name = st.sidebar.text_input('Введите фамилию: ', key='ts1')
ts_name = st.sidebar.text_input('Введите имя: ', key='ts2')
ts_second_name = st.sidebar.text_input('Введите отчество: ', key='ts3')

# Рисуем радиокнопку, даем ей название и задаем переменную
check_btn = st.sidebar.radio('Выберите статус сотрудника:', ('Исполнитель', 'Постановщик'))

# Как только пользователь нажимает на кнопку, в переменную подставляется значение, которое было под кнопкой
if(check_btn == 'Исполнитель'):
    status = 'RESPONSIBLE_ID'
elif(check_btn == 'Постановщик'):
    status = 'CREATED_BY'

st.sidebar.markdown('                      ')
st.sidebar.markdown('**За какой период ищем?**')

# Вводим дату
date_start = st.sidebar.date_input('От:', datetime.date(2023, 2, 5) ,key='date1')
day = date_start.strftime('%d.%m.%Y')
date_start = day


date_end = st.sidebar.date_input('До:', datetime.date(2023, 2, 5), key='date2')
day = date_end.strftime('%d.%m.%Y')
date_end = day

page_bckg_side = """
                <style>
                        [class='css-1oe5cao e1fqkh3o9']{
                        padding-top: 10px;
                        }
                </style>
    
                """
st.sidebar.markdown(page_bckg_side, unsafe_allow_html=True)

with st.spinner('Подождите'): # Спиннер будет крутится, пока не отработает скрипт
  try:
    # По нажатию кнопки, забираем внесенные пользователем данные и вставляем в запрос
    if(st.sidebar.button(':mag: Поиск')): 
        ts_result_name = ts_name.title()
        ts_result_last_name = ts_last_name.title()
        ts_result_second_name = ts_second_name.title()
        ts_date_start = date_start.title()
        ts_date_end = date_end.title()
        ts_data = b.get_all('user.search',
                    params={
                            'FILTER': {"LAST_NAME": ts_result_last_name, "NAME": ts_result_name, "SECOND_NAME": ts_result_second_name}
                    }
                            )
        ts_user_id = ts_data[0]['ID']
        
        tasks = b.get_all('tasks.task.list',
        params={
            'filter': {status: ts_user_id, 'UF_TASK_TYPE' : 237 ,'>=UF_CLOSED_PLAN_DATE': ts_date_start, '<=UF_CLOSED_PLAN_DATE': ts_date_end},
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

        for index, item in enumerate(task_status):
            if item == 6:
                task_status[index] = 'Отложена'    

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
                    st.title('№ '+ str(chck_id_task))
                    st.markdown('***Постановщик:***')
                    st.text(mail_crea_name)
                    st.markdown('***Ответственный:***')
                    st.text(mail_resp_name)
                    st.markdown('***Название задачи:***')
                    st.text(title)
                    st.markdown('***Крайний срок выполнения задачи:***')
                    st.text(deadl)
                    st.markdown('***Ссылка на задачу***' + '    ------------->>> [:globe_with_meridians:](%s)' % ts_link)
                    if ts_task_status == 'Выполнена' and ts_task_sub_status == 'Выполнена':
                        st.success(ts_task_status)
                    elif ts_task_sub_status == 'Просрочена':
                        st.error(ts_task_status + ' , ' + ts_task_sub_status)
                    elif ts_task_status == 'Ждет выполнения':
                        st.warning(ts_task_status)
                    elif ts_task_status == 'Выполняется':
                        st.warning(ts_task_status)
                    elif ts_task_status == 'Отложена':
                        st.warning(ts_task_status)

        # Переменные для дальнейшего применения в имени файла
        file_name_resp = 'Задачи ' + ts_last_name + ' (исполнитель).xlsx'
        file_name_crea = 'Задачи ' + ts_last_name + ' (постановщик).xlsx'
        
        # Создадим датафрейм
        data = np.array([task_id, check_resp_name, check_creators_name, tile_task, actual_date_deadline, actual_date_create, check_resp_mail, check_creators_mail, task_status, task_sub_status])
        df = pd.DataFrame(data=data, index=['ID задачи', 'Исполнитель', 'Постановщик', 'Описание', 'Крайний срок', 'Дата создания', 'Email исполнителя', 'Email постановщика', 'Статус', 'Подстатус'])

        # Тут, в зависимости от выбора статуса, мы формируем таблицу Exel и даем возможность её загрузить себе на ПК
        if check_btn == 'Исполнитель':
            with pd.ExcelWriter(file_name_resp, engine='xlsxwriter') as wb:
                df.to_excel(wb, sheet_name='Tasks')
                sheet = wb.sheets['Tasks']
                sheet.set_row(4, 80)
                sheet.set_column('A:A', 30)
                sheet.set_column(1, 100, 50)
            with open(file_name_resp, "rb") as template_file:
                template_byte = template_file.read()
                
                # Тут задаем имя кнопке и файлу
                st.sidebar.download_button(label="Скачать результат в Exel формате :inbox_tray:",
                        data=template_byte,
                        file_name = file_name_resp,
                        mime='application/octet-stream')

        elif check_btn == 'Постановщик':
            with pd.ExcelWriter(file_name_crea, engine='xlsxwriter') as wb:
                df.to_excel(wb, sheet_name='Tasks')
                sheet = wb.sheets['Tasks']
                sheet.set_row(4, 80)
                sheet.set_column('A:A', 30)
                sheet.set_column(1, 100, 50)
            with open(file_name_crea, "rb") as template_file:
                template_byte = template_file.read()

                st.sidebar.download_button(label="Скачать результат в Exel формате :inbox_tray:",
                        data=template_byte,
                        file_name = file_name_crea,
                        mime='application/octet-stream')
                


        with tab2:
            number_task = len(task_id)
            count = 0
            count_complete = 0
            for i in task_status:
                if i == 'Выполнена':
                    count_complete += 1
            for i in task_sub_status:
                if i == 'Просрочена':
                    count += 1
            st.markdown('**Просроченных задач:**')
            st.markdown(count)
            st.markdown('**Выполненных задач:**')
            st.markdown(count_complete)
            st.markdown('**Всего задач:**')
            st.markdown(number_task)


  except:
      st.error('Проверьте правильность введенных Вами данных.')
        

page_bckg_itog = """
                        <style>
                                .st-h5 {
                                     background: rgb(0, 0, 0 / 0%);
                                        }
                        </style>
            
                        """
st.markdown(page_bckg_itog, unsafe_allow_html=True)

