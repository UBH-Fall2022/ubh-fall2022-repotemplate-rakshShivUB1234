#!/usr/bin/env python3
from datetime import datetime
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import pandas as pd
from twilio.rest import Client
from csv import writer
from flask import Flask, render_template, request
from flask_apscheduler import APScheduler
import random

app = Flask(__name__)

account_sid = 'AC64cf9331582590cc9d79870ced615333'
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


def send_birthday_wish(client, recipient_number, recipient_name):
    """Send a birthday wish to a recipient using their WhatsApp number.

    Args:
        client (object): An instantiation of the Twilio API's Client object
        recipient_number (str): The number associated with the recipient's WhatsApp account,
            including the country code, and prepended with '+'. For example, '+14155238886'.
        recipient_name (str): The recipient's name

    Returns:
        True if successful, otherwise returns False
    """


    import requests

    url = "https://ajith-messages.p.rapidapi.com/getMsgs"

    querystring = {"category":"Birthday"}

    headers = {
        "X-RapidAPI-Key": "f29217e6c5msh0b30c4948c69cf3p129f36jsn3d7abd77728a",
        "X-RapidAPI-Host": "ajith-messages.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    json_obj = json.loads(response.text)
    birthday_wish = json_obj['Message']
    birthday_wish += """
I am so proud of you {}.""".format(recipient_name)
    try:
        message = client.messages.create(
            body=birthday_wish,
            from_='whatsapp:+14155238886',  # The default Sandbox number provided by Twilio
            to='whatsapp:' + recipient_number
        )

        print("Birthday wish sent to", recipient_name, "on WhatsApp number", recipient_number)
        return True

    except Exception as e:
        print("Something went wrong. Birthday message not sent.")
        print(repr(e))
        return False

def create_birthdays_dataframe():
    """Create a pandas dataframe containing birth date information from a CSV file.

    Args:
        None

    Returns:
        A dataframe if successful, otherwise returns False.
    """

    try:
        dateparse = lambda x: datetime.strptime(x, "%m-%d-%Y")
        birthdays_df = pd.read_csv(
            "birthdays.csv",
            dtype=str,
            parse_dates=['Birth Date'],
            date_parser=dateparse
        )
        print(birthdays_df)
        return birthdays_df

    except Exception as e:
        print("Something went wrong. Birthdays dataframe not created.")
        print(repr(e))
        return False


@scheduler.task('interval', id='check_for_matching_dates', seconds=10, misfire_grace_time=3600)
def check_for_matching_dates():
    """Calls the send_birthday_wish() function if today is someone's birthday.

    Args:
        None
    Returns:
        True if successful, otherwise returns False.
    """
    print("Running interval function")
    try:
        birthdays_df = create_birthdays_dataframe()
        birthdays_df["day"] = birthdays_df["Birth Date"].dt.day
        birthdays_df["month"] = birthdays_df["Birth Date"].dt.month
        today = datetime.now()
        print(today)
        for i in range(birthdays_df.shape[0]):
            birthday_day = birthdays_df.loc[i, "day"]
            birthday_month = birthdays_df.loc[i, "month"]
            print(birthday_day,birthday_month,today.day)
            if today.day == birthday_day and today.month == birthday_month:
                print('Yes')
                send_birthday_wish(client, birthdays_df.loc[i, "WhatsApp Number"], birthdays_df.loc[i, "Name"])
        return True

    except Exception as e:
        print("Something went wrong. Birthday check not successful.")
        print(repr(e))
        return False


def send_greeting_wish(client, recipient_number, recipient_name, recipient_relation):
    """Send a birthday wish to a recipient using their WhatsApp number.

    Args:
        client (object): An instantiation of the Twilio API's Client object
        recipient_number (str): The number associated with the recipient's WhatsApp account,
            including the country code, and prepended with '+'. For example, '+14155238886'.
        recipient_name (str): The recipient's name

    Returns:
        True if successful, otherwise returns False
    """

    # birthday_wish = """
    #     Hey {}, this is Tanvi's personal birthday wisher.
    #     Happy Birthday to you! I wish you all the happiness that you deserve.
    #     I am so proud of you.""".format(recipient_name)
    
    print(recipient_relation)
    if recipient_relation == 'Friend':
        msgs = ["Hi, hello, hey there, howdy!","Just a friendly little hello from me to you.","Hi there! Just felt like sharing a smile with you today.","Hey, you! What's new?","In the immortal words of Adele, 'Hello…it's me…'","¡Hola! Just thought I’d try multi-tasking by practicing my Spanish and saying hi to you at the same time."]
        greeting_wish = random.choice(msgs)
    elif recipient_relation == 'Mother':
        msgs = ["No one can ever replace you, not now and in the next million years to come. I love you, Mom.","You're the sweetest mom ever. Thanks for your care and the support you do for us every day. I love you, mom.","You have the first place in my heart, Mom. I'm so thankful to be under your supervision and care.","I cannot describe in words what you mean to me. Thanks for always being there for me.","If I could live my life once again, I would still want you to be my mother.","My dearest mommy, I love you very much. I can't ever be thankful enough to you. You are the reason for my smile and happiness. Love you always!"]
        greeting_wish = random.choice(msgs)
    elif recipient_relation == 'Father':
        msgs = ["Dad, you've given me so much. Here's to you.","Dad—you've made my life so much better. From the bottom of my heart, thank you.","Thank you for giving fatherhood your all. You've made me the person I am today.","Where would I be without you as my dad? I'm so grateful for you.","Thank you for being my dad.","God took the strength of a mountain, the patience of eternity, and combined them to create the thing we call dad.","To my dad, the man who moves fire and earth for his family.","Dad, even when you aren't there, I feel you in the world all around me."]
        greeting_wish = random.choice(msgs)
    try:
        message = client.messages.create(
            body=greeting_wish,
            from_='whatsapp:+14155238886',  # The default Sandbox number provided by Twilio
            to='whatsapp:' + recipient_number
        )

        print("Birthday wish sent to", recipient_name, "on WhatsApp number", recipient_number)
        return True

    except Exception as e:
        print("Something went wrong. Birthday message not sent.")
        print(repr(e))
        return False

def create_contacts_dataframe():
    """Create a pandas dataframe containing birth date information from a CSV file.

    Args:
        None

    Returns:
        A dataframe if successful, otherwise returns False.
    """

    try:
        contacts_df = pd.read_csv(
            "contacts.csv",
            dtype=str
        )
        print(contacts_df)
        return contacts_df

    except Exception as e:
        print("Something went wrong. Birthdays dataframe not created.")
        print(repr(e))
        return False


@scheduler.task('interval', id='send_greeting_message', minutes=1, misfire_grace_time=3600)
def send_greeting_message(sender=""):
    """Calls the send_greeting_wish() function if today is someone's birthday.

    Args:
        None
    Returns:
        True if successful, otherwise returns False.
    """
    try:
        contacts_df = create_contacts_dataframe()
        print("send_greeting_message called -------------------------")
        if sender:
            send_greeting_wish(client, contacts_df.loc[contacts_df.shape[0]-1, "WhatsApp Number"], contacts_df.loc[contacts_df.shape[0]-1, "Name"], contacts_df.loc[contacts_df.shape[0]-1, "Relation"])
        else:
            for i in range(contacts_df.shape[0]):
                send_greeting_wish(client, contacts_df.loc[i, "WhatsApp Number"], contacts_df.loc[i, "Name"], contacts_df.loc[i, "Relation"])
        return True

    except Exception as e:
        print("Something went wrong. Birthday check not successful.")
        print(repr(e))
        return False


# scheduler = BackgroundScheduler()
# job = scheduler.add_job(check_for_matching_dates, 'cron', day_of_week ='mon-sun', hour=0, minute=0, second=5)
# scheduler.start()


@app.route('/', methods = ['POST', 'GET'])
def main_page():
    if request.method == 'POST':
        form_data = request.form
        if form_data.get("category") == "user_create":
            csv_file = 'contacts.csv'
            user_list = [form_data.get('name'), form_data.get('relation'), form_data.get('phone')]
            send_greeting_message(form_data.get('name'))
        else:
            csv_file = 'birthdays.csv'
            user_list = [form_data.get('name'), form_data.get('date'), form_data.get('phone')]
        print(user_list)
        with open(csv_file, 'a+', newline='') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(user_list)
            f_object.close()
    return render_template('index.html')


# @scheduler.task('interval', id='do_job_1', minutes=1, misfire_grace_time=3600)
# def job1():
#     print('Job 1 executed')


# if __name__ == '__main__':
#     app.run()