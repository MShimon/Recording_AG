import datetime
import glob
import os
import json
import shutil
from parameters import DIR_AG, DIR_RES

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


    ##--A&G番組表のサーチ--##
    if os.path.exists(DIR_AG):#全ての番組表のパスを取得
        files = glob.glob(DIR_AG + "/*")
        #月と日でファイル名に検索をかけ、明日の番組表のパスを取得
        pattern = month_tommorow + day_tommorow
        for f in files:
            if find_keyword(f,pattern):
                schedule_path_AG = f
    
    ##--キーワードで番組表に検索をかける--##
    schedule_AG = json.load(open(schedule_path_AG,"r"))
    #keywordテキストファイル読み込み
    with open("keyword.txt","r") as f:
        keywords = (f.read().split())#改行区切りでリストで保存

    #キーワードでマッチングをかける
    reservation_AG = {}#予約する番組表
    for k in schedule_AG.keys():
        for word in keywords:
            #番組名かパーソナリティー名がキーワードと一致したら、予約番組表に追加
            if (find_keyword(schedule_AG[k]["title"],word)) or (find_keyword(schedule_AG[k]["personality"],word)):
                reservation_AG[k] = schedule_AG[k]
                break#複数回のマッチングを避ける
    
    ##--キーワード検索で引っかかった番組情報を予約番組表として保存--##
    #ディレクトリの作成
    if os.path.exists(DIR_RES):
        shutil.rmtree(DIR_RES)
        os.makedirs(DIR_RES)
    else:
        os.makedirs(DIR_RES)
    #JSON形式で保存
    file_name = "reservationAG_" + month_tommorow + day_tommorow
    with open(DIR_RES + "/" + file_name + ".json", "w") as f:
        json.dump(reservation_AG, f, ensure_ascii=False, indent=5)#indent値はかなり大きめ
