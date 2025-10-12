#from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv, find_dotenv
import os, sys
import hashlib
import hmac
import base64
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheet import GoogleSheet
import datetime as dt

load_dotenv(find_dotenv()) # .envファイルから環境変数を読み込む



LINE_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
LINE_SECRET = os.getenv('CHANNEL_SECRET')

GoogleSheet = GoogleSheet()
day_of_week = {"月":1, "火":2, "水":3, "木":4, "金":5, "土":6, "日":7 }
time_schedule = {
    "08:50":1,
    "10:35":2,
    "12:20":3,
    "14:45":4,
    "16:30":5,
    "18:15":6,
    "20:00":7
}

def send_push_message(user_id, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": user_id.title,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=data)



def cron():
    today = dt.date.today()
    weekday = today.weekday() + 1
    tz_jst = dt.timezone(dt.timedelta(hours=9))
    now = dt.datetime.now(tz_jst)
    now_time = now.strftime('%H:%M')
    userId_list = GoogleSheet.get_sheet_names()
    for time, class_num in time_schedule.items():
        #現在時刻から何限かを確認
        if now_time == time:
            num = class_num
            for user_id in userId_list:
                class_name = GoogleSheet.get_value(user_id.title, weekday + 1, num + 1)
                if class_name:
                    text = f"{class_name}"
                    send_push_message(user_id, text)
                


if __name__ == "__main__":
    cron()