from .models import PrivateChatRoom
from django.contrib.humanize.templatetags.humanize import naturalday
from datetime import datetime

def find_or_create_private_chat(user1, user2):
    try:
        chat = PrivateChatRoom.objects.get(user1 = user1, user2 = user2)
    except PrivateChatRoom.DoesNotExist:
        try:
            chat = PrivateChatRoom.objects.get(user1 = user2, user2 = user1)
        except PrivateChatRoom.DoesNotExist:
            chat = PrivateChatRoom(user1 = user1, user2 = user2)
            chat.save()
    return chat


def calculate_timestamp(timestamp):
    #print(datetime.now())
    """
    1. Todat or yesterday:
        - EX: 'today at 10:56 AM'
        - EX: 'yesterday at 5:19 PM'
    2. other:
        - EX: 05/06/2020
        - EX: 12/12/2020
    """
    #today or yesterday
    if((naturalday(timestamp) == "today") or (naturalday(timestamp) == "yesterday")):
        str_time = datetime.strftime(timestamp, "%I:%M %p")
        str_time = str_time.strip("0")
        ts = f"{naturalday(timestamp)} at {str_time}"
    #other day
    else:
        str_time = datetime.strftime(timestamp, "%m/%d/%Y")
        ts = f"{str_time}"
    return str(ts)