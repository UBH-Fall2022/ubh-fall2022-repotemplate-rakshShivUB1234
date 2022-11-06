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


@scheduler.task('interval', id='do_job_1', seconds=10, misfire_grace_time=3600)
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


# scheduler = BackgroundScheduler()
# job = scheduler.add_job(check_for_matching_dates, 'cron', day_of_week ='mon-sun', hour=0, minute=0, second=5)
# scheduler.start()

check_for_matching_dates()
# class Config:
#     SCHEDULER_API_ENABLED = True

@app.route('/', methods = ['POST', 'GET'])
def main_page():
    if request.method == 'POST':
        form_data = request.form
        if form_data.get("category") == "user_create":
            csv_file = 'contacts.csv'
            user_list = [form_data.get('name'), form_data.get('relation'), form_data.get('phone')]
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


if __name__ == '__main__':
    app.run()