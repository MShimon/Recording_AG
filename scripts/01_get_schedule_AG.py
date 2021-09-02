import os
import json
import shutil
import sys
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from parameters import URL_AG,DIR_AG
from datetime import datetime, date, timedelta

# @brief:「08:00」のような文字表記の時間を、「480」のような分表記に変換する
#@param:time_str　文字列表記の時間
#@return:分単位に変換した時間
def convert_time(time_str):
    t = time_str.split(":")
    h,m = int(t[0]),int(t[1])
    time_min = 60*h + m
    return time_min

if __name__ == '__main__':
    #url取得処理を成功するまで繰り返す
    for _ in range(1000):#最大ループ回数
        try:
            html = urlopen(URL_AG)
        except Exception as e:
            time.sleep(10)#10秒待ってからもう一度実行
        else: # リトライが全部失敗したときの処理
            break
    ## --webページから番組表部分を取得-- ##
    table_AG = BeautifulSoup(html, "html5lib").find("table",{"class":"weeklyProgram-table"})
    #
    schedule_week = [{} for i in range(7)]
    # テーブル本体（番組表）の取得
    tmp_programs = table_AG.find("tbody") #番組表部分を取り出す
    tmp_programs = tmp_programs.find_all("tr")#trタグで囲まれている部分のみ抜き出す
    #空のタグを取り除く
    list_programs = []
    for tmp in tmp_programs:
        if len(tmp.get_text()) > 1: #中身が1文字でもあれば、番組情報だと判定
            list_programs.append(tmp)
    
    ##--番組情報をリストに格納していく--##
    programs_1week = []
    for prog in list_programs:#行毎に取り出す
        info= prog.find_all("td")
        for i in info:#一番組づつ取り出して処理
            #-番組ごとのディクショナリを作成していく-#
            program_single = {}
            # -番組名とパーソナリティの取得- #
            tmp = i.find("div",{"class":"weeklyProgram-content"}).find_all("a")
            tmp = [t.get_text().strip() for t in tmp]
            if len(tmp) < 1: # 「放送休止」等をskip
                break
            # 番組名
            program_single["title"] = tmp[0].replace("&","_").replace("/","_").replace("／","_") 
            # パーソナリティ
            if len(tmp) > 1:
                personality = tmp[1]
                for t in tmp[2:]: personality = personality + "、" + t
            else:
                personality = ""
            program_single["personality"] = personality
            # 放送開始時間
            program_single["onair"] = i.find("div",{"class":"weeklyProgram-time"}).get_text().strip().replace("頃","")#放送開始時間
            program_single["time"] = i.get("rowspan")#放送時間
            #program_single["repeat"] = (i.get("class") is not None) # リピート放送か否か
            program_single["repeat"] = ("repeat" in str(i.get("class"))) # リピート放送か否か
            # 全体リストに追加
            programs_1week.append(program_single)
    ## --開始時間毎でリストを分割する -- ##
    tmp_programs_1week = []
    tmp_list = []
    for program in programs_1week:
        if len(tmp_list) == 0:
            tmp_list.append(program)
        else:
            group_onair = tmp_list[0]["onair"]
            if program["onair"] == group_onair:
                tmp_list.append(program)
            else:
                tmp_programs_1week.append(tmp_list)
                tmp_list = []
                tmp_list.append(program)
    # 最後にappend
    tmp_programs_1week.append(tmp_list)
    programs_1week = tmp_programs_1week
    ## -- 番組を曜日毎に分割 -- ##
    for program_groupByOnair in programs_1week:
        num_week = 0
        for program in program_groupByOnair:# 同一時間帯毎に処理
                schedule = schedule_week[num_week]
                if len(schedule) == 0: #その日の一番最初の番組
                    schedule[program["title"] + " " + program["onair"]] = program#番組表に追加
                else:#それ以降の番組
                    while True:
                        now_onair = convert_time(program["onair"])#今の番組の時間
                        last_dif = 60*24 # 適当に大きめの値で初期化
                        last_time = 60*24
                        # １つ前にやっていた番組の情報を特定
                        for k in schedule.keys():
                            tmp_last_onair = convert_time(schedule[k]["onair"])#番組の開始時刻を取得
                            tmp_dif = now_onair - tmp_last_onair
                            if (tmp_dif > 0) and (tmp_dif < last_dif):#より時間の近い番組であれば更新
                                #last_time = int(schedule[k]["time"])
                                last_dif = tmp_dif
                                last_time = int(schedule[k]["time"])
                        # 前の番組の放送時刻が被っていなければ、スケジュールに追加する
                        if (last_dif >= last_time):
                            schedule[program["title"] + " " + program["onair"]] = program
                            break
                        else:
                            num_week = (num_week + 1) % 7
                            schedule = schedule_week[num_week]
                #曜日を進める
                num_week = (num_week + 1) % 7
    #-JSON形式で番組表を保存-#
    #前日までのファイルを全削除し、新しくディレクトリを作成する
    if os.path.exists(DIR_AG):
        shutil.rmtree(DIR_AG)
        os.makedirs(DIR_AG)
    else:
        os.makedirs(DIR_AG)
    ## --json形式で保存-- ##
    # 明日から一週間分の日付を取得
    tmp_weekday = {}
    list_dates = []
    for i in range(7):
        tmp_date = datetime.today() + timedelta(days= i+1)
        #tmp_date = datetime.today() + timedelta(days= i)
        month = str(tmp_date.month) if len(str(tmp_date.month)) >= 2 else  "0" + str(tmp_date.month)
        day = str(tmp_date.day) if len(str(tmp_date.day)) >= 2 else "0" + str(tmp_date.day)
        date = month + day
        weekday = int(tmp_date.weekday())
        tmp_weekday[weekday] = date
    for i in range(7):
        list_dates.append(tmp_weekday[i])
    
    # 保存処理
    for i in range(len(list_dates)):
        file_name = "schedule_" + list_dates[i]#ファイル名から「/」を取り除く
        with open(DIR_AG + "/" + file_name + ".json", "w") as f:
            json.dump(schedule_week[i], f, ensure_ascii=False, indent=5)#indent値はかなり大きめ
