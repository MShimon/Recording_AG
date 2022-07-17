import json
import shutil
import re
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from parameters import URL_AG,DIR_AG

#@brief:htmlタグから「番組名」「パーソナリティ」「開始時刻」「放送時間(分)」「リピート放送かどうか」の情報を抜き出す
#@param:program　1番組分のhtml情報
#@return:title, 番組名
#        personality, パーソナリティ名
#        onair, 番組開始時刻
#        time_duration, 番組放送時間(分)
#        repeat, repeat放送か否か(True or False)
def extract_program_info(program):
    # title
    title = program.find("p",{"class":"dailyProgram-itemTitle"}).find("a").get_text()
    # personality
    list_personality = program.find("p",{"class":"dailyProgram-itemPersonality"}).find_all("a")
    if len(list_personality) != 0:
        personality = list_personality[0].get_text()
        for p in list_personality[1:]:
            personality = personality + "、" + p.get_text()
    else:
        personality = "None"
    # onair
    onair = program.find("h3",{"dailyProgram-itemHeaderTime"}).get_text().split()[0]
    # time_duration
    time_begin = program.find("h3",{"dailyProgram-itemHeaderTime"}).get_text().split()[0]
    time_end = program.find("h3",{"dailyProgram-itemHeaderTime"}).get_text().split()[-1]
    # 24時を超えた場合の例外処理
    delta_begin = 0
    delta_end = 0
    # time_beginの修正
    begin_hour = int(time_begin.split(':')[0])
    if begin_hour >= 24:
        delta_begin = int(begin_hour / 24)
        begin_hour = begin_hour % 24
        time_begin = str(begin_hour) + ':' + time_begin.split(':')[-1]
    # time_endの修正
    end_hour = int(time_end.split(':')[0])
    if end_hour >= 24:
        delta_end = int(end_hour / 24)
        end_hour = end_hour % 24
        time_end = str(end_hour) + ':' + time_end.split(':')[-1]
    # 差分計算
    time_begin = (datetime.strptime(time_begin,"%H:%M") + timedelta(days = delta_begin))
    time_end = (datetime.strptime(time_end,"%H:%M") + timedelta(days = delta_end))
    time_duration = str(int((time_end - time_begin).total_seconds()/60)) # convert to minute
    # repeat
    repeat = "is-repeat" in program["class"]

    return title, personality, onair, time_duration, repeat

if __name__ == '__main__':
    ## --html取得-- #
    # 明日の番組表のURLを作成
    date_tommorow = (datetime.now() + timedelta(days = 1)).date().strftime('%Y%m%d')
    URL_SCHEDULE = urljoin(URL_AG, "?date=" + date_tommorow)
    #url取得処理を成功するまで繰り返す
    for _ in range(1000):#最大ループ回数
        try:
            html = urlopen(URL_SCHEDULE)
        except Exception as e:
            time.sleep(10)#10秒待ってからもう一度実行
        else: # リトライが全部失敗したときの処理
            break
    
    ## --webページから番組表部分を取得-- ##
    table_AG = BeautifulSoup(html, "html5lib").find("div",{"class":"block_contents_bg"})
    list_programs = table_AG.find_all("article")#trタグで囲まれている部分のみ抜き出す
    # 明日の番組表を作成
    schedule_tommrow = {}
    for program in list_programs:
        title, personality, onair, time_duration, repeat = extract_program_info(program)
        # 各情報を詰め込む
        tmp_program = {}
        tmp_program["title"] = title
        tmp_program["personality"] = personality
        tmp_program["onair"] = onair
        tmp_program["time"] = time_duration
        tmp_program["repeat"] = repeat
        title_json = title + " " + onair
        schedule_tommrow[title_json] = tmp_program
    #-JSON形式で番組表を保存-#
    #前日までのファイルを全削除し、新しくディレクトリを作成する
    if Path(DIR_AG).exists():
        shutil.rmtree(DIR_AG)
        Path(DIR_AG).mkdir(parents=True)
    else:
        Path(DIR_AG).mkdir(parents=True)
    # 保存処理
    date_tommorow = (datetime.now() + timedelta(days = 1)).date().strftime('%m%d')
    file_name = 'schedule_' + date_tommorow + '.json'
    with open(Path(DIR_AG)/file_name, "w") as f:
        json.dump(schedule_tommrow, f, ensure_ascii=False, indent=5)#indent値はかなり大きめ
