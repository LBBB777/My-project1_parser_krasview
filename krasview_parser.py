### 0) ИМПОРТИРОВАННЫЕ МОДУЛИ
import json
import csv
import re
import datetime
import requests
from collections import Counter
import numpy as np

from bs4 import BeautifulSoup
from lxml.html.defs import empty_tags
# 1) БЛОК КОДА 1.  ФОРМИРУЕТСЯ ЦИКЛ ЗАПОЛНЕНИЯ ХРАНИЛИЩА  НОВЫХ ФИЛЬМОВ С  1 по 10

class krasview_parser:
     def __init__(self):
         self.url = 'https://qfilms.ru/movie/fresh?page='

     def parse_krasview(self, start_page:int, end_page:int,output_type:str):
        if (start_page or end_page) < 0 :
            return (-1),"Не корректное значение страниц"
        if  output_type not in ['csv','json']:
            return (-1),"Не верный тип вывода"

        slovar_movie =  {}
        slovar_filmov_csv = []

        page_num = start_page
        #  создаем список - хранилище записей
        data = []
        # пока страница не более 10
        while page_num <= end_page:
            #  создается строка запроса из постоянного текста и номера страницы
            url = self.url + str(page_num)
            #   делаем запрос по адресу, которыей только что был сформирован и сохраняем тело ответа  html_content
            html_content = requests.get(url).text
            #   тело ответа преобразуется в дерево  методом  BeautifulSoup.  soup - дерево
            soup = BeautifulSoup(html_content, 'lxml')
            # находим все записи (в дереве soup) с конкретным тегом по конкретному id
            entries_1 = soup.find_all('li', id=re.compile("c-"))
            # добавляются записи в хранилище записей
            data = data + entries_1
            # номер страницы увеличиваем на 1
            page_num += 1
        #############

        # 2)  БЛОК КОДА 2. НА ОСНОВЕ ХРАНИЛИЩА НОВЫХ ФИЛЬМОВ СОЗДАЕМ ХРАНИЛИЩЕ АДРЕСОВ НОВЫХ ФИЛЬМОВ ПО ТЕГУ
        # создаем хранилище (список) адресов фильмов film_adress
        film_adress = []
        #  Для каждой записи в хранилище записей   data
        for record_1 in data:
            #  найти запись с тегом а и поместить ее в переменную film
            film = record_1.find('a')
            #  тот адрес, который соответсвует тегу а поместить в хранилище (список) адресов фильмов - в film_adress
            film_adress.append(film['href'])
        #############

        # 3) БЛОК КОДА 3. НА ОСНОВЕ ХРАНИЛИЩА АДРЕСОВ НОВЫХ ФИЛЬМОВ СОЗДАЕМ ХРАНИЛИЩЕ ПРИКЛЮЧЕНЧЕСКИХ ФИЛЬМОВ
        # объявляется хранилище записей (словарь) с адресами приключенческих фильмов (имеют тег ПРИКЛЮЧЕНИЯ)
        #  для каждого  адреса в хранилище (списке) адресов фильмов film_adress
        for adres in film_adress:    # цикл по каждому найденомуадресу
        #  зайти по аресу фильма  и получить тело ответа
            film = requests.get(adres).text
            #  преобразовать тело ответа в дерево
            soup = BeautifulSoup(film, 'lxml')
            # Найти в дереве запись фильмы с конкретным тегом   ПРИКЛЮЧЕНИЯ/текст тега прключения.
            film_adventures = soup.find('a', href="/movie/tag/%D0%9F%D1%80%D0%B8%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D1%8F")
        #############

        # 4) БЛОК КОДА 4. РЕАЛИЗУЕМ БЛОК ПОИСКА ПО ВЕТКЕ ПРИКЛЮЧЕНЧЕСКИХ ФИЛЬМОВ
            # БК-4.1 Если тег ПРИКЛЮЧЕНИЯ у фильма  есть
            if film_adventures:
                #  находим все записи с конкретным тегом и классом,
                # где содержатся название и год фильма. Выбираю только НАЗВАНИЕ ФИЛЬМА
                film_name = soup.find('h1',itemprop="name", id="movie-l")

                # БК-4.2 Ищем по той же ветке ГОД ВЫХОДА ФИЛЬМА
                film_year = soup.find('a', href= re.compile("/movie/tag/"))

                # БК-4.3. Ищем по той же ветке СТРАНУ ГДЕ БЫЛ ВЫПУЩЕН ФИЛЬМ
                film_country = film_year.find_next('a', href= re.compile("/movie/tag/"))

                # БК -4.4. Ищем по той же ветке РЕЖИССЕРА ФИЛЬМА
                film_director = soup.find('a', itemprop='director')

                # БК-4.5. Ищем по той же ветке СЦЕНАРИСТА ФИЛЬМА
                film_writer = soup.find('a', itemprop='writer')

                # БК- 4.6. Ищем первых трех АКТЕРОВ.
                # Для этого получим всех АКТЕРОВ и выведем  трех нужных
                actors = soup.find_all('a', itemprop='actor')
                # ВАРИАНТ РЕАЛИЗАЦИИ 1: выводим в одну строку трех первых АКТЕРОВ -  первые три элемента списка:
                qq = actors[0].text + ", " + actors[1].text + ", " + actors[2].text

                # БК- 4.7. Ищем количество просмотров, коментариев и лайков с начала выхода.
                        # Для этого:
                # выбираю в дереве  (soup) тег (small)  и помещаю его в переменную (film_statistics)
                film_statistics = soup.find('small')
                # Ищу все числа в теге (film_statistics) и помещаю их в переменную (number_of_views).
                number_of_views = re.findall(r'\d+', film_statistics.text)

                # Обрезаю  первый элемент, потому что это количество времени с публикации.
                number_of_views.pop(0)
                if len(number_of_views) == 2:
                    number_of_views.insert(1, '0')
                ##########

                # БК-4.8. Проверяем фильм на наличие тега "боевик". Для этого получаем  тег "боевик".
                # Если нет тега - пишем "не боевик".
                # получить тег "боевик" из ветки дерева soup
                film_boevik_teg = soup.find('a', href="/movie/tag/%D0%91%D0%BE%D0%B5%D0%B2%D0%B8%D0%BA")
                if  not film_boevik_teg:
                    boevik = "не боевик"
                else:
                    boevik = film_boevik_teg.text
                ##########

                # БК- 4.9 Проверяем фильм на наличие  трейлера
                # СПРАВКА: Выбрать все теги с названиями видео и
                # СПРАВКА: проверить их текст на наналичие счлов "Трейлер" и "трейлер"
                # завожу переменную "трейлер фильма"
                film_trail = "нет трейлера"
                # получить список тегов, котрые могут содержать имя видео
                www = soup.find_all('div', class_="text", itemprop = "name")
                # для каждого тега в  списке  тегов  www :
                for ww in www:
                # если Трейлер  или трейлер в тексте тега содержится   то
                    if ("Трейлер" in ww.text) or ("трейлер" in ww.text):
                        trail = "есть трейлер"
                        break
                ################

                # БК- 4.10. Получаю текущий год
                today = datetime.date.today()
                tekuch_year = today.year
                ################

        # БК- 4.10. ВЫЧИСЛЯЮ СРЕДНИЕ ПОКАЗТЕЛИ В ГОД на данной платформе
                # СПРАВКА: Делимое - просмотры. Делитель - количество лет, которое фильм провел на данной платформе
                # СПРАВКА:если год выпуска (film_year) совпадает с текущим годом  (tekuch_year), то делитель - 1.
                # СПРАВКА:если год выпуска (film_year) не совпадает с текущим годом, то делитель - это разница  "film_year-tekuch_year"

        # ШАГ 1: НАДО ОПРЕДЕЛИТЬ ДЕЛИТЕЛЬ. ОН ЖЕ количество лет проката фильма.   Завожу переменную - divider"/ДЕЛИТЕЛЬ  -условное количество лет для всех показателей
                divider  =  0
                # Завожу переменные для рассчета ДЕЛИТЕЛЯ
                a = int(film_year.text)     # год выпуска фильма
                b = int(tekuch_year)        # текущий год
                # Для определения делителя: Если год выпуска совпадает с текущим годом
                # УСЛОВИЕ, вариант  1
                if a == b:
                    divider = 1
                else:
                    divider = b - a
                # print(divider)  #  ЭТО ДЕЛИТЕЛЬ И ОДНОВРЕМЕННО КОЛИЧЕСТВО ЛЕТ ПРОКАТА ФИЛЬМА
                #########

        # ШАГ 2: НАДО ОПРЕДЕЛИТЬ СРЕДНЕЕ КОЛИЧЕСТВО ПРОСМОТРОВ В ГОД на данной платформе: количество просмотров / делитель (колич. лет)
                # Завожу переменную - average_number_of_views - среднее количество просмотров в год
                average_number_of_views = int(number_of_views[0])/divider
                #########

        # ШАГ 3: НАДО ОПРЕДЕЛИТЬ СРЕДНЕЕ КОЛИЧЕСТВО КОММЕНТАРИЕВ В ГОД на данной платформе: количество комментариев/ делитель (кол. лет)
                # Завожу переменную - average_number_of_comments - среднее количество комментариев в год
                average_number_of_comments = int(number_of_views[1])/ divider
                #########

        # ШАГ 4: НАДО ОПРЕДЕЛИТЬ СРЕДНЕЕ КОЛИЧЕСТВО СРЕДНЕГО ЛАЙКА В ГОД на данной платформе: сумма лайков всего (положительных и отрицательных)/ делитель (кол. лет)
                # Завожу переменную - average_number_of_comments_likes - среднее количество комментариев лайков в год
                average_number_of_comments_likes = int(number_of_views[2])/divider
                #########

        # БК-5. Определяем количество комментариев по годам в формате «год- количество»- отдельный список на каждый фильм.

        #  Формируем хранилище комментариев переведенных в текст
                comment_storage_text = []  #  хранилище комментариев переведенных в текст
            #  найти запись с тегом а и поместить ее в переменную comment_teg
                comment_teg = soup.find_all('a', class_='i')
                for comment in comment_teg:
                    zz = comment.text[len(comment.text)-4:]
                    # если zz переменная азад ,
                    # то заменяем ее текущим годом
                    if zz == 'азад':
                       zz = str(tekuch_year)
                    comment_storage_text.append(zz)

        #БК -6.  ФОРМИРОВАНИЕ СЛОВАРЯ 2  с  содержанием " год- количество  комментариев"
                values_parameters_2 = {}
        #   Получить список уникальных элементов
                unikvelus = np.unique(comment_storage_text)
        #  Для каждого элемента в списке
                for uu in unikvelus:
        #  получить количество  вхождений
                    cc = comment_storage_text.count(uu)
        #   определить  значения словаря
                    values_parameters_2[uu.item()] = cc
                if output_type == 'json':
            # ФОРМИРОВАНИЕ переменной "values_parameters_1", которая является словарем  с  содержанием в ключах требуемых параметров фильма, а в значениях -  соответсвующих переменных
                    values_parameters_1 = {'Страна': film_country.text,
                                           'Год  выхода': film_year.text,
                                           'Сколько лет фильму на данный момент ': divider,
                                           'Режиссер ': film_director.text,
                                           'Сценарист': film_writer.text if film_writer else "",
                                           '<Первые три актера из списка актеров> ': qq,
                                           '<Приключения- боевик / Приключения- не боевик> ': boevik,
                                           'Всего с начала выхода фильма: Кол. просмотров  фильма': number_of_views[0],
                                           'Всего с начала выхода фильма: Кол. Комментариев': number_of_views[1],
                                           'Всего с начала выхода фильма: Кол. Лайков': number_of_views[2],
                                           'Среднее количество: просмотров в год на данной платформе ': int(average_number_of_views),
                                           'Среднее количество: комментариев в год': int(average_number_of_comments),
                                           'Динамика комментариев  год/количество ': values_parameters_2
                                           }
                    #  Задание основных параметров словаря slovar_movie
                    slovar_movie[film_name.text[:len(film_name.text) - 5]] = values_parameters_1
                # Если словарь с динамикой комментариев пустой
                if output_type == 'csv':
                    if  not values_parameters_2:
                        yyy = (film_name.text[:len(film_name.text) - 5].replace('\xe9','e'), film_country.text.replace('\xe9','e'), film_year.text, divider,
                               film_director.text.replace('\xe9','e'),
                               film_writer.text.replace('\xe9','e') if film_writer else "", qq, boevik, number_of_views[0], number_of_views[1], number_of_views[2],
                               int(average_number_of_views), int(average_number_of_comments), "____", 0)
                        slovar_filmov_csv.append(yyy)
                    for key, value in values_parameters_2.items():
                        yyy = (film_name.text[:len(film_name.text) - 5].replace('\xe9','e'),film_country.text.replace('\xe9','e'),film_year.text,divider, film_director.text,
                               film_writer.text.replace('\xe9','e') if film_writer else "",qq,boevik,number_of_views[0],number_of_views[1],number_of_views[2],int(average_number_of_views),int(average_number_of_comments),key, value)
                        slovar_filmov_csv.append(yyy)


                ################ СПРАВКА ДЛЯ СЕБЯ
                # if not slovar_filmov_csv:
                #     print("СЛОВАРЬ пустой! Проверьте логику сбора данных")
                #     exit()
                # print(slovar_filmov_csv)
                ## Перегоняем скрипт в  джейсон
        # print(slovar_movie)
        # json_format = json.dumps(slovar_movie, indent=4,ensure_ascii=False)
        # print(json_format)
                ################ СПРАВКА ДЛЯ СЕБЯ

        ## создать джейсон файл
        if output_type == 'json':
        # создаю джесон файл: в  переменную кладу  название файла с расширением
            json_file =  'output.json'
            # открываю   поток  записи 'w' в файл
            json_obj = open(json_file, 'w',encoding='utf-8')
            # в поток записи заношу структуру данных которая хранится в джейсон формате
            json.dump(slovar_movie, json_obj, indent=4, ensure_ascii=False)
            # закрвть поток записи
            json_obj.close()
            return (0), 'Создан output.json'
        if output_type == 'csv':
            with open('output.csv', 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile,
                                       delimiter=';',  # разделитель
                                       quotechar='"',  # кавычки для текстовых значений
                                       quoting=csv.QUOTE_MINIMAL )  # миним

                # запись одной строки
                csv_writer.writerow(['Название фильма' ,'Страна','Год  выхода','Сколько лет фильму на данный момент','Режиссер','Сценарист', 'Первые три актера из списка актеров', 'Приключения- боевик / Приключения- не боевик', 'Всего с начала выхода фильма: Кол. просмотров  фильма', 'Всего с начала выхода фильма: Кол. Комментариев', 'Всего с начала выхода фильма: Кол. Лайков', 'Среднее количество: просмотров в год на данной платформе' , 'Среднее количество: комментариев в год', 'Динамика комментариев  год/количество', 'Динамика комментариев  год/количество'])
                #   перебрать список  и записать в  файл каждый элемент списка
                # Проверка типа данных в списке и запись
                for   rec in slovar_filmov_csv:
                    csv_writer.writerow(rec)
                csvfile.close()                            # закрытие потока записи
            return (0), 'Создан output.csv'
        return (-1), 'Что-то пошло не так'

