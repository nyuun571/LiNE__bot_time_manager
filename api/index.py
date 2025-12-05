from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv, find_dotenv
import sys
import os
import hashlib
import hmac
import base64
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sheet
import datetime as dt

load_dotenv(find_dotenv()) # .envファイルから環境変数を読み込む

app = Flask(__name__)

LINE_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
LINE_SECRET = os.getenv('CHANNEL_SECRET')
LINE_API_URL = "https://api.line.me/v2/bot/message/reply"

GoogleSheet = sheet.GoogleSheet()
day_of_week = {"月":1, "火":2, "水":3, "木":4, "金":5, "土":6, "日":7 }


@app.route("/")
def hello():
    return "<h1>Hello world!</h1>"

def signature_check(CHANNEL_SECRET, body_byte, receivedSignature):
    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'), body_byte, hashlib.sha256).digest()
    expected_signature = base64.b64encode(hash).decode('utf-8')
    return hmac.compare_digest(expected_signature, receivedSignature)
    

def reply_message(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(LINE_API_URL, headers=headers, json=data)

def get_user_profile(user_id):
    url = f"https://api.line.me/v2/bot/profile/{user_id}"
    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        profile = response.json()
        return profile["displayName"]
    

    

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    body_byte = request.get_data()
    received_signature = request.headers.get("X-Line-Signature")
    if not signature_check(LINE_SECRET, body_byte, received_signature):
        return jsonify({"status": "error", "message": "Invalid signature"}), 400
    if "events" in body:
        for event in body["events"]:
            user_id = event["source"]["userId"]
            sheet_name = f"{user_id}"
            if event["type"] == "follow":
                user_name = get_user_profile(user_id)
                GoogleSheet.add_sheet(sheet_name, user_name)
                reply_message(event["replyToken"], 
                            "【使い方】\n"
                            "iPhoneの場合以下のURLからショートカットを取得し、オートメーションから設定を行ってください\n"
                            "一日の時間割と1限目〜7限目までの時間に対応した時間割確認ショートカット\n"
                            "https://www.icloud.com/shortcuts/31d74ccaa5d8498da43a55f59952cf59 \nhttps://www.icloud.com/shortcuts/eeebeef6d4ae4e36b3857c31de380034 \nhttps://www.icloud.com/shortcuts/1a38aed74ab44aa5847608413ebc8290\nhttps://www.icloud.com/shortcuts/9a392f6c6b2e47f0b354b8a626f2daf8 \nhttps://www.icloud.com/shortcuts/2afe40bc875948c9a5ba9fa6b0d85e55\nhttps://www.icloud.com/shortcuts/108ddb2dafdd489aaa1f18c046687a84 \nhttps://www.icloud.com/shortcuts/f0408aad40024f99921d661f76418d59 \nhttps://www.icloud.com/shortcuts/ff4c779149f3439eb87e9b2a6e88cac0 \nhttps://www.icloud.com/shortcuts/31d74ccaa5d8498da43a55f59952cf59\n\n"
                            "メッセージで「曜日　何限」と送信するとその時間の授業を送信します。\n" 
                            "「曜日」のみの場合はその曜日の時間割を送信します。\n"
                            "時間割を作成するには、\n編集　曜日　何限　内容\nと送信してください。\n")
            if event["type"] == "message" and event["message"]["type"] == "text":
                message_text = event["message"]["text"]
                parts = message_text.split()
                if "編集" in message_text:
                    if (len(parts) >= 4):
                        day  = "".join(key for key, value in day_of_week.items() if key in  parts[1])
                        period, content = parts[2], f"{' '.join(parts[3:])}"
                        day_row = day_of_week.get(day[0]) + 1
                        period_col = int(period)
                        result = GoogleSheet.edit_value(sheet_name, day_row, period_col + 1, content)
                        reply_message(event["replyToken"], f"{day[0]}曜日の{period}限に「{content}」を追加しました。")
                    
                
                elif (key in parts[0] for key, value in day_of_week.items()):
                    if len(parts) == 1:
                        day = "".join(key for key, value in day_of_week.items() if key in  parts[0])
                        day_row = day_of_week.get(day[0]) + 1
                        result = GoogleSheet.get_row_values(sheet_name, day_row)
                        reply_message(event["replyToken"], f"{day[0]}曜日の時間割\n {f'\n'.join(result)}")
                    elif len(parts) == 2:
                        day = "".join(key for key, value in day_of_week.items() if key in  parts[0])
                        period = parts[1]
                        day_row = day_of_week.get(day[0]) + 1
                        period_col = int(period)
                        result = GoogleSheet.get_value(sheet_name, day_row, period_col + 1)
                        if result:
                            reply_message(event["replyToken"], f"{result}")

                    #課題管理機能を追加
                    
            if event["type"] == "unfollow":
                #修正点 unfollowイベントが実行されない→UserNameが取得されない→sheetIDをUserIDに変更
                result = GoogleSheet.delete_sheet(sheet_name)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run()
    