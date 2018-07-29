import os
from datetime import datetime
from pymessenger.bot import Bot

class NewBot(Bot):
    """
        this is a child of Bot class from pymessenger module
    """
    def send_quick_replies(self, recipient_id, text, quick_replies):
        """
            Added a functionality to send quick replies
        """
        response = {"text": text, "quick_replies": quick_replies}
        return self.send_message(recipient_id, response)




def user_subscription(db_obj, psid, sub_id):
    db_obj.execute("INSERT OR IGNORE INTO user_preference (fb_id, subject) VALUES (:id, :subid)", {"id": int(psid), "subid": int(sub_id)})
    db_obj.commit()

def get_today_events(db_obj):

    """
        Will perform a scheduled query on subject table in db and get a list of all
        scientists born on this day
    """
    day = datetime.today().strftime('%m-%d')
    data = db_obj.execute("SELECT u.fb_id AS uid, s.name, s.date_of_birth, s.bio FROM user_preference AS u JOIN subject AS s ON s.sub_id = u.subject WHERE SUBSTR(s.date_of_birth, 6) = :today", {"today": day}).fetchall()
    tmp = []
    for event in data:
        tmp.append(list(event))
    today_events = tmp
    return today_events

def request_processing(response_events):
    """
        A function that will process the response from messenger to determine which webhook
        event it originated from.
        response_events is Array containing event data see: https://developers.facebook.com/docs/messenger-platform/reference/webhook-events
        the bot expects 2 kind of webhook events messages and messaging_postbacks.
        messages: is when user sends a message to the bot
        messaging_postbacks is the event that occurs when the user clicks on a button from the subject list sent to him
    """
    for event in response_events:
        try:
            if event['messaging'][0]['message'].get('quick_reply') != None:
                uid = event['messaging'][0]['sender']['id']
                message_text = event['messaging'][0]['message'].get('text')
                payload = event['messaging'][0]['message']['quick_reply']['payload']
                return {'uid': uid, 'text': message_text, 'payload': payload}
            else:
                uid = event['messaging'][0]['sender']['id']
                message_text = event['messaging'][0]['message'].get('text')
                return {'uid': uid, 'text': message_text}
        except KeyError:
            return None


def analyze_text(received_text):
    """
        A function that will analyze the user's text message and then will decied which response is appropriate
    """
    default_response = 'مرحبا، لطلب قائمة المواد قم بإرسال "إشتراك" أو قم بإرسال مرحبًا '

    if received_text == "مرحبًا" or received_text == "مرحبا" or received_text == "مرحباً":
        return 'مرحبًا بك وأتمنى لك يوم سعيد'
    elif received_text == "شكرًا" or received_text == "شكرا" or received_text == "شكراً":
        return 'عفوًا وأتمنى لك يوم جميل'
    elif received_text == "إشتراك" or received_text == "اشتراك":
        return 0
    return default_response

def queued_message(sched, data_queue,bot_obj, message_temp):
    try:
        response_parameters = data_queue.pop()
        print(response_parameters)
        response = message_temp.format(response_parameters[2][0:4], response_parameters[1], response_parameters[3])
        print(response)
        bot_obj.send_text_message(str(response_parameters[0]), response)
        return "sent"
    except IndexError:
        sched.remove_job("message_queue")

