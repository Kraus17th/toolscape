#!/usr/bin/env python3
#
# Для работы необходим внешний тулз sendemail:
#   sudo apt install sendemail
#
import binascii
import mimetypes
import pathlib
import random
import string
import re
import os
from bs4 import BeautifulSoup
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
from yaml import safe_load
from subprocess import run
from argparse import ArgumentParser
from time import sleep


def check_email(email: str, info: str):
    if re.fullmatch(regex, email):
        return(True)
    else:
        print(f'[{info}] Incorrect email: \'{email}\'')
        return(False)

def read_file(path: str, mode: str, encoding=None, exit_on_error=True, error_msg=None):
    try:
        with open(path, mode, encoding=encoding) as fp:
            out = fp.read()
        return(out)
    except:
        if error_msg: print(error_msg)
        if exit_on_error: exit(1)
        else:
            return(None)

def write_file(data, filename: str, directory: str, mode: str):
    directory_path = pathlib.Path(directory).resolve()
    if not directory_path.exists():
        directory_path.mkdir(parents=True)
    filepath = directory_path.joinpath(filename).resolve()
    with open(filepath, mode) as f:
        f.write(data)
    return(filepath)


def replace_in_text(input: str, replacer: str, text: str):
    if replacer: 
        out = input.replace(replacer, text)
    else: 
        out = text
    return(out)

def canary_make(email: str):
    preout =  binascii.hexlify(email.encode())
    out = preout.decode('ascii')
    return(out)

def ran_gen(size, chars=string.ascii_uppercase + string.digits):
    return(''.join(random.choice(chars) for x in range(size)))

def yaml_fast_error(content, types: list, can_be_empty=False, exit_on_error=True, error_msg=None):
    if type(content) in types:
        return(content)
    elif can_be_empty and not content:
        return(content)
    else:
        if error_msg: print(error_msg)
        if exit_on_error: exit(1)
        else:
            return(None)

def yaml_joinpath(directory, content, types: list, can_be_empty=False, exit_on_error=True, error_msg=None):
    checked_content = yaml_fast_error(content=content,
                                      types=types,
                                      can_be_empty=can_be_empty,
                                      exit_on_error=exit_on_error,
                                      error_msg=error_msg)
    out = directory.joinpath(checked_content).resolve()
    return(out)

def sendemail(sender_email: str,
              recipient_email: str,
              subject: str,
              smtp_server: str,
              log_file_path: str,
              raw_email_path: str,
              sender_password: str):
    cmd = ['sendemail',
           '-f', sender_email,
           '-t', recipient_email,
           '-u', subject,
           '-s', smtp_server,
           '-l', log_file_path,
           '-o', 'message-charset=utf-8',
           '-o', 'message-format=raw',
           '-o', f'message-file={raw_email_path}',
           '-o', f'reply-to={sender_email}',
           '-o', 'tls=auto',
           '-xu', sender_email,
           '-xp', sender_password]
    run(cmd)

### Старт
# -------
parser = ArgumentParser()
parser.add_argument("config")
parser.add_argument("emails")
parser.add_argument("--outdir")
parser.add_argument("--send", action='store_true')
args = parser.parse_args()

yaml_path = args.config
emails_list = args.emails
out_directory = args.outdir
send_this = args.send

### Чтение YAML-конфига
# ---------------------
key_error_str = '<SCRIPT STOPPED>: Key \'{key_name}\' at \'{yaml_path}\' has incorrect value'
yaml_dir_path = pathlib.Path(yaml_path).parent.resolve()
# ---------------------
try:
    with open(yaml_path, mode='r', encoding='utf-8') as f:
        content = safe_load(f)
        body_text_path = yaml_joinpath(directory=yaml_dir_path, 
                                       content=content['body_text_path'],
                                       types=[str],
                                       error_msg=key_error_str.format(key_name='body_text_path', yaml_path=yaml_path))
        body_html_path = yaml_joinpath(directory=yaml_dir_path, 
                                       content=content['body_html_path'],
                                       types=[str],
                                       error_msg=key_error_str.format(key_name='body_html_path', yaml_path=yaml_path))

        __attachments_paths__ = yaml_fast_error(content=content['attachments_paths'],
                                                types=[str, list],
                                                can_be_empty=True,
                                                error_msg=key_error_str.format(key_name='attachments_paths', yaml_path=yaml_path))

        attachments_paths = []
        if type(__attachments_paths__) is str: 
            __attachments_paths__ = [__attachments_paths__]
        elif type(__attachments_paths__) is list:
            for path in __attachments_paths__:
                attachments_paths.append(yaml_joinpath(directory=yaml_dir_path,
                                                       content=path,
                                                       types=[str],
                                                       error_msg=f'<SCRIPT STOPPED>: List key \'attachments_paths\' at \'{yaml_path}\' has incorrect value \'{path}\''))

        recipient_id_replacer = yaml_fast_error(content=content['recipient_id_replacer'],
                                                types=[str],
                                                can_be_empty=True,
                                                error_msg=key_error_str.format(key_name='recipient_id_replacer', yaml_path=yaml_path))
        subject = yaml_fast_error(content=content['subject'],
                                  types=[str],
                                  error_msg=key_error_str.format(key_name='subject', yaml_path=yaml_path))
        sender_name = yaml_fast_error(content=content['sender_name'],
                                      types=[str],
                                      can_be_empty=True,
                                      error_msg=key_error_str.format(key_name='sender_name', yaml_path=yaml_path))
        sender_email = yaml_fast_error(content=content['sender_email'],
                                       types=[str],
                                       error_msg=key_error_str.format(key_name='sender_email', yaml_path=yaml_path))
        sender_password = yaml_fast_error(content=content['sender_password'],
                                          types=[str],
                                          error_msg=key_error_str.format(key_name='sender_password', yaml_path=yaml_path))
        smtp_server = yaml_fast_error(content=content['smtp_server'],
                                      types=[str],
                                      error_msg=key_error_str.format(key_name='smtp_server', yaml_path=yaml_path))
        send_delay = yaml_fast_error(content=content['send_delay'],
                                     types=[int],
                                     error_msg=key_error_str.format(key_name='send_delay', yaml_path=yaml_path))
        log_file_path = yaml_joinpath(directory=yaml_dir_path,
                                      content=content['log_file_path'],
                                      types=[str],
                                      error_msg=key_error_str.format(key_name='log_file_path', yaml_path=yaml_path))

except:
    print(f'<SCRIPT STOPPED>: YAML file \'{yaml_path}\' can\'t be open')
    exit(1)



### Подготовка данных
# -------------------
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
# -------------------
if not sender_name:
    sender_name = sender_email.split('@')[0]

sender_addr = Address(sender_name, sender_email.split('@')[0], sender_email.split('@')[1])
body_text = read_file(path=body_text_path,
                      mode='r',
                      encoding='utf-8',
                      error_msg=f'<SCRIPT STOPPED>: File \'{body_text_path}\' open error')
body_html = read_file(path=body_html_path,
                      mode='r',
                      encoding='utf-8',
                      error_msg=f'<SCRIPT STOPPED>: File \'{body_html_path}\' open error')


### Подготовка img вложений, подстановка cid в html
# -------------------------------------------------
html_dir_path = pathlib.Path(body_html_path).parent.resolve()
soup = BeautifulSoup(body_html, features="html.parser")
img_attachs = {}
# -------------------------------------------------
for img in soup.findAll('img'):
    src = img['src']
    src_path = html_dir_path.joinpath(src).resolve()
    img_data = read_file(path=src_path,
                         mode='rb',
                         error_msg=f'<SCRIPT STOPPED>: Image \'{src}\' at html-code open error')
    ext = pathlib.Path(src).suffix[1:]
    cid = f'<{src_path.name}@{ran_gen(8)}.{ran_gen(8)}>'
    img_attachs[cid] = [img_data, ext, src_path.name]
    img['src'] = 'cid:{cid}'.format(cid=cid[1:-1])

body_html_imgfix = str(soup)


### Подготовка остальных вложений
# -------------------------------
other_attachs = {}
# -------------------------------
for path in attachments_paths:
    filename = path.name
    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    other_attachs[filename] = {'data': read_file(path=path,
                                                 mode='rb',
                                                 error_msg=f'<SCRIPT STOPPED>: Attachment \'{path}\' open error'),
                               'maintype': maintype,
                               'subtype': subtype}


### Сборка msg
# ------------
for line_number, line in enumerate(read_file(path=emails_list,
                                             mode='r',
                                             error_msg=f'<SCRIPT STOPPED>: Email list \'{emails_list}\' open error').splitlines(),
                                   start=1):
    if line:
        recipient_data = line.split(':', 1)
        recipient_email = recipient_data[0]
        if not check_email(recipient_email, 'Recipient'):
            print(f'line {line_number} (\'{line}\') at file \'{emails_list}\' was skiped')
            continue
        if len(recipient_data) == 2 and recipient_data[1]:
            recipient_name = recipient_data[1] 
        else:
            recipient_name = recipient_data[0].split("@", 1)[0].title()
        recipient_addr = Address(recipient_name, recipient_email.split('@', 1)[0], recipient_email.split('@', 1)[1])
        canary_str = canary_make(recipient_email)
        new_body_text = replace_in_text(input=body_text, replacer=recipient_id_replacer, text=canary_str)
        body_html_fin = replace_in_text(input=body_html_imgfix, replacer=recipient_id_replacer, text=canary_str)
        
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_addr
        msg['To'] = recipient_addr
        msg['Accept-Language'] = 'ru-RU, en-US'
        msg['Reply-To'] = sender_addr
        msg['Return-Path'] = sender_email
        #if img_attachs.keys() or other_attachs.keys():
        #    msg['X-MS-Has-Attach'] = 'yes'
        #msg['X-Mailer'] = 'calc.exe'
        msg.preamble = 'This is a multi-part message in MIME format.\n'
        
        msg.set_content(new_body_text, cte="base64")

        msg.add_alternative(body_html_fin, subtype='html', cte="base64")
        for img_cid in img_attachs.keys():
            msg.get_payload()[1].add_related(img_attachs[img_cid][0],
                                             maintype='image',
                                             subtype=img_attachs[img_cid][1],
                                             cid=img_cid,
                                             filename=img_attachs[img_cid][2],
                                             disposition='inline',
                                             params={'name': img_attachs[img_cid][2]})

        for filename in other_attachs.keys():
            msg.add_attachment(other_attachs[filename]['data'], 
                               maintype=other_attachs[filename]['maintype'],
                               subtype=other_attachs[filename]['subtype'],
                               filename=filename,
                               params={'name': filename},
                               headers=[f'Content-Description: {filename}'])
    
        
        ### Отправка и/или сохранение eml-файлов
        # --------------------------------------
        if not out_directory and not send_this:
            print('Nothing happends ¯\\_(ツ)_/¯')
            exit(1)
        if out_directory:
            out_file_path = write_file(data=bytes(msg),
                       filename=f'{recipient_email}.eml',
                       directory=out_directory,
                       mode='wb')
            print(f'Raw email was saved: {out_file_path}')
        if send_this:
            temp_file_path = write_file(data=bytes(msg),
                                        filename=f'temp_output.eml',
                                        directory=yaml_dir_path,
                                        mode='wb')
            try:
                sendemail(sender_email=sender_email,
                          recipient_email=recipient_email,
                          subject=subject,
                          smtp_server=smtp_server,
                          log_file_path=log_file_path,
                          raw_email_path=temp_file_path,
                          sender_password=sender_password)
                sleep(send_delay)
            except:
                raise
            finally:
                os.remove(temp_file_path)
