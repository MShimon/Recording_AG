import pickle
import os.path
import datetime
import json
from parameters import PWD
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
from apiclient import errors
SCOPES = ['https://www.googleapis.com/auth/gmail.send'] # Gmail APIのスコープを設定

# -Functions- #
# @brief :メール本文の作成
# @return:メール本文(str形式)
def create_text():
    month_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 1)).month
    day_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 1)).day
    mail_string = ""
    json_reservation = os.listdir(PWD + "/json/reservation/")
    if len(json_reservation) == 1:
        #文字列を作成
        mail_string += "明日" + str(month_tommorow) + "月" + str(day_tommorow) + '日の予約リストは以下のようになります\n'
        mail_string += "---------------------"
        #jsonを読み込み
        sch_reservation = json.load(open(PWD + "/json/reservation/" + json_reservation[0],"r"))
        for k in sch_reservation.keys():
            mail_string += '\n○' + sch_reservation[k]["title"]
            if sch_reservation[k]["repeat"]:
                mail_string = mail_string + "(リピート放送)"
            mail_string += '\nパーソナリティ：' + sch_reservation[k]["personality"]
            mail_string += '\n放送開始時刻：' + sch_reservation[k]["onair"]
            mail_string += '\n録画時間：' + sch_reservation[k]["time"] + '分\n'
    else:
        mail_string = "error"

    return mail_string

# @brief :メール送信用のMIME形式のデータを作成する
# @param :sender, メール送信者
#         to, 宛先
#         subject, メールタイトル
# @return:MIME形式のメールデータ
def create_message(sender, to, subject):
    message = MIMEText(create_text())
    message['from'] = sender
    message['to'] = to
    message['subject'] = subject
    # base64でエンコードしてreturn
    encode_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': encode_message.decode()}

# @brief :メール送信
# @param :service, 認証情報
#         user_id, user_id
#         message, MIME形式のメールデータ
def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    # アクセストークンの取得
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)

    # メール本文の作成
    sender = 'example@gmail.com'
    to = 'recrad0000@gmail.com'
    subject = '録画番組一覧'
    message = create_message(sender, to, subject)

    # Gmail APIを呼び出してメール送信
    send_message(service, 'me', message)
