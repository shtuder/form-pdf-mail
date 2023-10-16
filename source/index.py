#  Copyright (c) ChernV (@otter18), 2021.

import ast
from urllib.parse import urlparse, parse_qs, unquote_plus
import base64
from fpdf import FPDF
from PyPDF2 import PdfFileWriter, PdfFileReader
import boto3
from io import StringIO, BytesIO
from transliterate import translit
import requests
import string
import random


def handler(event, context):
    print(event)
    if type(event) == str:
        data = ast.literal_eval(event)
    else:
        data = event
    body = data['body']


    """
    Декодируем данные из base64.
    """

    base64_bytes = body.encode('utf8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf8')


    """
    Делаем полную строку, чтобы распарсить форму.
    """

    url = 'https://someurl.com/with/query_string?' + message
    parsed_url = urlparse(url)
    dada = parse_qs(parsed_url.query)


    """
    Парсим форму и конвертируем в киррилицу поля.
    """

    email = dada['Email'][0]
    name = unquote_plus(dada['Name'][0], encoding="utf-8")
    role_model = unquote_plus(dada['role-model'][0], encoding="utf-8")
    traits = unquote_plus(dada['traits'][0], encoding="utf-8")
    similarities = unquote_plus(dada['similarities'][0], encoding="utf-8")
    achievments = unquote_plus(dada['achievments'][0], encoding="utf-8")
    success_factors = unquote_plus(dada['success-factors'][0], encoding="utf-8")
    mission = unquote_plus(dada['mission'][0], encoding="utf-8")
    resources = unquote_plus(dada['resources'][0], encoding="utf-8")
    advice = unquote_plus(dada['barriers'][0], encoding="utf-8")
    next_step = unquote_plus(dada['next-step'][0], encoding="utf-8")
    print('the form is parsed')


    """
    Данные для PDF.
    """

    titles1 = [
    'Твои ролевые модели: ',
    'Качества, которые уже есть в тебе, но еще могут быть не признаны: ',
    'Качества, которые ты уже признаешь в себе: ',
    'Масштаб достижений, который вдохновляет: ',
    'То, что может помочь раскрыть твой потенциал: '
    ]
    titles2 = [
    'Возможная миссия: ',
    'То, чего не хватает (ресурсы, которые нужно найти): ',
    'Что сделала бы ролевая модель (совет от нее тебе): ',
    'Твой следующий шаг, который ты сделаешь в течение 24 часов: '
    ]
    answers1 = [role_model, traits, similarities, achievments, success_factors]
    answers2 = [mission, resources, advice, next_step]


    """
    Контент PDF-документа.
    """

    fpdf = FPDF(orientation = 'P', unit = 'mm', format = (271, 361))
    fpdf.add_font('SuisseIntl Light', '', 'SuisseIntl-Light.ttf', uni=True)
    fpdf.add_font('SuisseIntl SemiBold', '', 'SuisseIntl-SemiBold.ttf', uni=True)
    fpdf.set_text_color(0, 0, 0)

    fpdf.add_page()
    fpdf.set_font('SuisseIntl SemiBold', '', 30)
    fpdf.cell(0, h=40, txt=name, align = 'R')

    height = 60
    fpdf.set_y(68)
    fpdf.set_left_margin(30)
    fpdf.set_right_margin(20)
    for idx, text in enumerate(titles1):
        fpdf.set_x(30)
        fpdf.set_font('SuisseIntl SemiBold', '', 12)
        fpdf.write(h=6, txt=text)
        fpdf.set_font('SuisseIntl Light', '', 12)
        fpdf.write(h=6, txt=answers1[idx].replace(' \n', ', ') +'\n')
        fpdf.ln(h = 4)

    fpdf.set_y(185)
    fpdf.set_right_margin(55)
    for idx, text in enumerate(titles2):
        fpdf.set_x(30)
        fpdf.set_font('SuisseIntl SemiBold', '', 12)
        fpdf.write(h=6, txt=text)
        fpdf.set_font('SuisseIntl Light', '', 12)
        fpdf.write(h=6, txt=answers2[idx].replace(' \n', ', ') +'\n')
        fpdf.ln(h = 4)

    byte_string = fpdf.output(dest='S').encode('latin-1')
    stream = BytesIO(byte_string)
    print('pdf is ready to be merged')
