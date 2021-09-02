import subprocess
#-いろんなパラメータを記述しておくプログラム-#
#パスは基本的に絶対パス
#全般
PWD = subprocess.check_output("pwd").decode("utf-8").strip()
#PWD = PWD + "/recording_radio"
#A&G
#URL_AG = "http://www.agqr.jp/timetable/streaming.html"
URL_AG = "https://www.joqr.co.jp/qr/agregularprogram/"
DIR_AG = PWD + "/json/schedule_A&G"

#録画予約ディレクトリ
DIR_RES = PWD + "/json/reservation"

#A&G関連
#RTMP_URL_AG = "rtmp://fms-base1.mitene.ad.jp/agqr/aandg1"#streamのurl
RTMP_URL_AG = "https://fms2.uniqueradio.jp/agqr10/aandg1.m3u8"#streamのurl

#録画関係
MARGIN_BEGIN = 10#何秒前から録画するか　0~60
MARGIN_END = 10#終了後、何秒余分に録画するか
DIR_SH = PWD + "/scripts/recording"#シェルスクリプト保存ディレクトリ
DIR_SAVE_MP4 = PWD + "/record_files/mp4"
DIR_SAVE_MP3 = PWD + "/record_files/mp3"
#DIR_SAVE_MP4 = "/nas01/recording/mp4"
#DIR_SAVE_MP4 = "/nas02/recording/mp4"
#DIR_SAVE_MP3 = "/nas01/recording/mp3"
#DIR_SAVE_MP3 = "/nas02/recording/mp3"
BPS = str(128) #mp3ファリに変換するときのビットレート　単位は[kbps]
