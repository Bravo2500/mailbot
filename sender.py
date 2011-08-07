#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
    batch smtp sender

    crontab: (www)

    */1 * * * *  sender.py path/to/data/dir
"""

SMTP_HOST = "localhost"
SMTP_PORT = "25"
SMTP_USER = ""
SMTP_PASS = ""
SMTP_FROM = "info@100druzei.info"

EMAIL_FROM = "100 Друзей <info@100druzei.info>"
EMAIL_REPL = "200@100druzei.info"

TASK_SUFFIX = ".data.json"
REPT_SUFFIX = ".result.json"


from datetime import datetime
import json, sys, os, shutil

import smtplib

from email import Charset
from email.header import Header
from email.mime.text import MIMEText

Charset.add_charset('utf-8', Charset.SHORTEST, Charset.QP, 'utf-8')


def err(msg):
    sys.stderr.write(msg+"\n")
#--


def dt_iso(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def flush_result(res, of):
    tmp = of+".tmp"
    json.dump(res, open(tmp,"w+"), ensure_ascii=False)
    shutil.move(tmp, of)
#--


def send_mail(email, subj, text):

    msg = MIMEText(text.encode('utf-8'))
    msg.set_charset('utf-8')
    msg['From'] = Header(EMAIL_FROM,'utf-8').encode()
    msg['To'] = Header(email,'utf-8').encode()
    msg['Replay-To'] = Header(EMAIL_REPL,'utf-8').encode()
    msg['Subject'] = Header(subj,'utf-8').encode()

    s = smtplib.SMTP()
    s.connect(SMTP_HOST, SMTP_PORT)
    s.ehlo()
    if SMTP_USER:
        s.login(SMTP_USER, SMTP_PASS)
    s.sendmail(SMTP_FROM, [email], msg.as_string())
    s.quit()

#--

def process_file(base_dir, in_name, out_name):

    of = os.path.join(base_dir, out_name)
    open(of, "w+").close() # touch output

    try:
        task = json.load( open(os.path.join(base_dir, in_name)) )
    except ValueError as ex:
        err("Unable to load: "+in_name+"\n"+str(ex))
        return

    res = dict(pid=os.getpid(), ts=dt_iso(datetime.now()))
    flush_result(res, of)

    try:
        subj, text = task['topic'], task['template']
        for i, u in enumerate(task['users']):
            res['count'] = i
            try:
                send_mail(u['email'], subj.format(**u), text.format(**u))
            except Exception as ex:
                err("send_mail error: "+str(ex))
                res.setdefault('errors', []).append(u['email'])
            #-
            if i % 10:
                flush_result(res, of)
        #-
    except (KeyError, IndexError, TypeError, ValueError) as ex:
        err("Error processing task [{0}]: {1}".format(in_name, str(ex)))

    res['te'] = dt_iso(datetime.now())
    flush_result(res, of)
#--

def scandir(base_dir):
    fls = sorted(os.listdir(base_dir))
    sl = len(TASK_SUFFIX)
    for f in fls:
        if f.endswith(TASK_SUFFIX):
            out = f[:-sl]+REPT_SUFFIX
            if out in fls:
                continue
            process_file(base_dir, f, out)
            return
        #-
    #-
#--

if __name__ == "__main__":

    if len(sys.argv) > 1:
        scandir(sys.argv[1])
    else:
        sys.stderr.write("Parameter missing\n")
        sys.exit(1)
    #-
#.
