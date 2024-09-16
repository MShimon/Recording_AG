import json
import glob
import datetime
import subprocess
import os
from parameters import MARGIN_BEGIN,MARGIN_END,DIR_RES,RTMP_URL_AG,DIR_SH,DIR_SAVE_MP4,DIR_SAVE_MP3,BPS

#@brief:渡された文章の中に特定の文字列が含まれているかを判定する
#@param:strings マッチングさせる文章（渡す文章）
#       pattern マッチングを行う文字列
#@return:True or False  
def find_keyword(strings,pattern):
   if not strings.find(pattern) == -1:
       return True
   else:
       return False

if __name__ == "__main__":
    ##--明日の年月日を取得--##
    year_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 1)).year
    month_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 1)).month
    day_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 1)).day
    #year_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 0)).year
    #month_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 0)).month
    #day_tommorow = (datetime.datetime.now() + datetime.timedelta(days = 0)).day
    #日時を文字列に変換 month,dayは表記を変更
    #year
    year_tommorow = str(year_tommorow)#year
    #month
    if len(str(month_tommorow)) == 1:
        month_tommorow = "0" + str(month_tommorow)
    else:
        month_tommorow = str(month_tommorow)
    #day
    if len(str(day_tommorow)) == 1:
        day_tommorow = "0" + str(day_tommorow)
    else:
        day_tommorow = str(day_tommorow)

    #録画した映像を保存するディレクトリを作成
    if not os.path.exists(DIR_SAVE_MP4):
        os.makedirs(DIR_SAVE_MP4)
    if not os.path.exists(DIR_SAVE_MP3):
        os.makedirs(DIR_SAVE_MP3)

    reservation_list = []#予約を行う番組情報を格納するリスト
    reservation_path = glob.glob(DIR_RES + "/*")
    for rp in reservation_path:
        if find_keyword(rp,"AG"):#AGの番組リストであれば
            schedule = json.load(open(rp,"r"))
            for k in schedule.keys():
                reservation_list.append(schedule[k])

    ##--録音用のシェルスクリプトを作成していく--##
    #録画した番組を保存するディレクトリ
    if not os.path.exists(DIR_SH):
        os.makedirs(DIR_SH)
    #pwd = subprocess.check_output("pwd").decode("utf-8").strip()
    #実行コマンドの文字列を作成
    num = 0
    for rl in reservation_list:#リストに追加されている分だけシェルスクリプトを作成
        #番組毎の保存ディレクトリを作成
        #mp4
        dir_save_mp4_prog = DIR_SAVE_MP4 + "/" + rl["title"]
        if not os.path.exists(dir_save_mp4_prog):
            os.makedirs(dir_save_mp4_prog)
        if rl["repeat"]:
            dir_save_mp4_prog = dir_save_mp4_prog + "/repeat"
            if not os.path.exists(dir_save_mp4_prog):
                os.makedirs(dir_save_mp4_prog)
        #mp3
        dir_save_mp3_prog = DIR_SAVE_MP3 + "/" + rl["title"]
        if not os.path.exists(dir_save_mp3_prog):
            os.makedirs(dir_save_mp3_prog)
        if rl["repeat"]:
            dir_save_mp3_prog = dir_save_mp3_prog + "/repeat"
            if not os.path.exists(dir_save_mp3_prog):
                os.makedirs(dir_save_mp3_prog)

        delay_time = str(60 - MARGIN_BEGIN)#rtmpdump実行前のsleep時間
        time = str(MARGIN_BEGIN + 60*int(rl["time"]) + MARGIN_END)#録画単位は秒
        #録画開始時間を求める
        file_name = '"' + dir_save_mp4_prog + "/" + (rl["title"] + "_" + year_tommorow + month_tommorow + day_tommorow + ".mp4") + '"'#保存ファイル名
        command_recording = 'ffmpeg -i "' + RTMP_URL_AG + '" -t ' + time + " " + file_name#実行するコマンド文字列
        command_convert = "ffmpeg -i " + file_name + " -ab " + BPS + "k " + file_name.replace("mp4","mp3")
        #シェルスクリプトを作成
        sh_name = "recording_" + year_tommorow + month_tommorow + day_tommorow + "_" + str(num) + ".sh"
        num = num + 1
        with open(DIR_SH + "/" +sh_name,"w") as f:#シェルスクリプトに書き込み
            f.write("#!/bin/sh\n")#ヘッダー
            f.write("sleep " + delay_time + "\n")
            f.write(command_recording + "\n")
            f.write(command_convert)
        #atコマンドを作成
        #録画開始時間を求める　録画開始時刻は番組放送開始時刻の一分前
        onair_hour,onair_minute = int(rl["onair"].split(":")[0]),int(rl["onair"].split(":")[1])
        if onair_hour < 24:
            start_rec = datetime.datetime(int(year_tommorow),int(month_tommorow),int(day_tommorow),onair_hour,onair_minute,0) + datetime.timedelta(minutes = -1)
        elif onair_hour >= 24:
            onair_hour = onair_hour % 24
            start_rec = datetime.datetime(int(year_tommorow),int(month_tommorow),int(day_tommorow),onair_hour,onair_minute,0) + datetime.timedelta(days = 1 ,minutes = -1)
        #日時の表記を冗長にする
        rec_month = str(start_rec.month) if len(str(start_rec.month))==2 else "0" +  str(start_rec.month)
        rec_day = str(start_rec.day) if len(str(start_rec.day))==2 else "0" +  str(start_rec.day)
        rec_hour = str(start_rec.hour) if len(str(start_rec.hour))==2 else "0" +  str(start_rec.hour)
        rec_minute = str(start_rec.minute) if len(str(start_rec.minute))==2 else "0" +  str(start_rec.minute)
        #コマンドの文字列作成
        command = "at -f " + DIR_SH + "/" + sh_name + " " + rec_hour+":"+rec_minute + " " + rec_month + rec_day + str(start_rec.year)[2:4]
        #コマンドを実行
        # print(command)
        subprocess.call(command,shell=True)
