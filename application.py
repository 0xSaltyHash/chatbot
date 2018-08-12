# -*- coding: utf-8 -*-
# a facebook messenger chat bot
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, request, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED
from helpers import request_processing, analyze_text, user_subscription, get_today_events, NewBot, queued_message
from config import bio_temp
from datetime import datetime


app = Flask(__name__)
engine = create_engine(os.getenv('DB_URL'))
db = scoped_session(sessionmaker(bind=engine))



ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('FB_VERIFY_TOKEN')
bot = NewBot(ACCESS_TOKEN)
scheduler = BackgroundScheduler()
MESSAGE_QUEUE = []

def job_listener(event):
    if event.job_id == 'query':
        MESSAGE_QUEUE = event.retval
        print(MESSAGE_QUEUE)
        if len(MESSAGE_QUEUE) != 0:
            scheduler.add_job(queued_message, 'interval', [scheduler, MESSAGE_QUEUE, bot, bio_temp], timezone='UTC', seconds=20, id="message_queue")
            return "message queue started"
    elif event.job_id == 'message_queue':
        return 1




scheduler.add_job(get_today_events, 'cron', [db], timezone='UTC', hour=5, minute=25, id='query')
scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED)
scheduler.start()

def verify_fb_token(token_sent):

    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def send_message(recipient_id, response):

    bot.send_text_message(recipient_id, response)
    return "success"


def send_subject_list(rec_id):
    """
        Sends subjects list to the user of rec_id as a quick replies buttons
    """
    quick_reply = [{"content_type": "text", "title": "فيزياء", "payload": 1},
    {"content_type": "text", "title": "كيمياء", "payload": 2},
    {"content_type": "text", "title": "أحياء", "payload": 3},
    {"content_type": "text", "title": "رياضيات", "payload": 4}
    ]
    return bot.send_quick_replies(rec_id, "من فضلك اختر مادة لتتابعها", quick_reply)




@app.route('/', methods=['GET')
def index():

    if request.method == 'GET':
        return render_template("index.html")

@app.route('/webhook', methods=['GET', 'POST'])
def recieve_webhook():
    if request.method == 'POST':
        output = request.get_json()
        print(output)
        message_recieved = request_processing(output['entry'])
        try:
            psid = message_recieved.get('uid', None)
        except AttributeError:
            return "Unknown Webhook"
        print(psid)
        if psid == None:
            return "Not valid webhook"
        elif message_recieved.get('payload') == None:
            response = analyze_text(message_recieved['text'])
            if response == 0:
                send_subject_list(psid)
            else:
                send_message(psid, response)
        else:
            sub_id = message_recieved.get('payload')
            user_subscription(db,psid, sub_id)
            response = "تم اشتراكك في مادة {0} بنجاح".format(message_recieved['text'])
            send_message(psid, response)

        return "Success"

    else:

        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
