from email import message
import smtplib
import json
import os
from parameters import PWD
import datetime
import time

smtp_host = 'smtp.gmail.com'
smtp_port = 587
from_email = 'recrad0000@gmail.com' # 送信元のアドレス
to_email = 'recrad0000@gmail.com' # 送りたい先のアドレス
username = 'recrad0000@gmail.com' # Gmailのアドレス
password = 'Ncanon0315' # Gmailのパスワード

#日時を取得
month_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 1)).month
day_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 1)).day

#@brief
#@param
#@return
def make_message():
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
            mail_string += '\nパーソナリティ：' + sch_reservation[k]["personality"] 
            mail_string += '\n放送開始時刻：' + sch_reservation[k]["onair"] 
            mail_string += '\n録画時間：' + sch_reservation[k]["time"] + '分\n' 
    else:
        mail_string = "error"

    return mail_string

if __name__=="__main__":
    # メールの内容を作成
    msg = message.EmailMessage()
    msg.set_content(make_message()) # メールの本文
    msg['Subject'] = 'recording_demon' # 件名
    msg['From'] = from_email # メール送信元
    msg['To'] = to_email #メール送信先
    
    # メールサーバーへアクセス
    for _ in range(1000):#最大ループ回数
        try:
            server = smtplib.SMTP(smtp_host, smtp_port)
        except Exception as e:
            time.sleep(10)#10秒待ってからもう一度実行
        else:
            break
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.send_message(msg)
    server.quit()
