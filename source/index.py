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


    """
    Объединяем шаблон и созданный контент в один PDF.
    """
    pdf_template_file_name = 'template.pdf'
    pdf_template = PdfFileReader(open(pdf_template_file_name, 'rb'))
    template_page = pdf_template.getPage(1)
    overlay_pdf = PdfFileReader(stream)
    template_page.mergePage(overlay_pdf.getPage(0))

    output_pdf = PdfFileWriter()
    output_pdf.addPage(pdf_template.getPage(0))
    output_pdf.addPage(template_page)
    buf = BytesIO()
    output_pdf.write(buf)
    print('output pdf is ready')


    """
    Загрузка файла в S3.
    """

    session = boto3.session.Session(aws_access_key_id='YCAJEizxOoBAkk64DSmSEQbJu',
              aws_secret_access_key='YCNGZooOD9oCbSc0L74--aKN43MpB8ewwStfD5El',
              region_name='ru-central1')
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )

    key = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(30))
    file_name = translit(name, "ru", reversed=True).replace(' ', '_').lower() + '_' + key + '.pdf'
    s3.put_object(Body=buf.getvalue(), Bucket='manifest-lab-space-pub', Key=file_name)
    print('pdf is uploaded')


    """
    Отправка письма через Unisender.
    """

    api_key = '6f3711m8kiqxdd6p4eetzugeky1oydha5f4hy5xe'
    sender_name = 'MANIFEST LAB'
    sender_email = 'info@manifest-lab.space'
    subject = 'Гид "Ролевая модель": Результаты прохождения'
    list_id = 2
    lang = 'ru'
    track_read = 1
    track_links = 1
    cc = 'aopichugin@gmail.com'
    error_checking = 1

    with open('role-model-email') as f:
        body = f.read()

    link = 'https://storage.yandexcloud.net/manifest-lab-space-pub/' + file_name
    body2 = body.replace('https://manifest-lab.space/guide', link)

    url = 'https://api.unisender.com/ru/api/sendEmail'
    myobj = {
        'format': 'json',
        'api_key': api_key,
        'email': email,
        'sender_name': sender_name,
        'sender_email': sender_email,
        'body': body2,
        'subject': subject,
        'list_id': list_id,
        'lang': lang,
        'track_read': track_read,
        'track_links': track_links,
        'error_checking': error_checking,
        'cc': cc
    }

    x = requests.post(url, data = myobj)
    print(x.text)
    print('the email is sent')


    return {
        'statusCode': 200,
        'body': 'Success!' + ' ' + link
    }
