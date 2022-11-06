from datetime import datetime
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import pandas as pd
from twilio.rest import Client
import random

app = Flask(__name__)

account_sid = 'AC64cf9331582590cc9d79870ced615333'
auth_token = '269f82d1c467469e9ca43861570d365a'
client = Client(account_sid, auth_token)


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

def create_birthdays_dataframe():
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

def check_for_matching_dates():
    """Calls the send_greeting_wish() function if today is someone's birthday.

    Args:
        None
    Returns:
        True if successful, otherwise returns False.
    """
    try:
        contacts_df = create_birthdays_dataframe()
        for i in range(contacts_df.shape[0]):
            send_greeting_wish(client, contacts_df.loc[i, "WhatsApp Number"], contacts_df.loc[i, "Name"], contacts_df.loc[i, "Relation"])
        return True

    except Exception as e:
        print("Something went wrong. Birthday check not successful.")
        print(repr(e))
        return False

# scheduler = BackgroundScheduler()
# job = scheduler.add_job(check_for_matching_dates, 'cron', day_of_week ='mon-sun', hour=0, minute=15)
# scheduler.start()
check_for_matching_dates()


if __name__ == '__main__':
    app.run(port=9000)
