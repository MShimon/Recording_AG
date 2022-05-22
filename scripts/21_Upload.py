# coding: utf-8
import sys, os
from pathlib import Path
from subprocess import check_call
from ftplib import FTP

# -- Main -- #
if __name__ == "__main__":
    # -コマンドライン引数からの取得- #
    dirPath = sys.argv[1]
    # FTP settings
    FTP.encoding = "utf-8"
    ftp = FTP(
        "192.168.10.230",
        "ftp_user",
        passwd="FTPPassw0rd"
        )
    # -mp4ファイルの一覧を取得- #
    list_ext = ["mp4", "mp3"]
    for ext in list_ext:
        path = Path(dirPath)/ext
        files = path.glob('**/*.' + ext)
        # -アップロード処理- #
        for fil in files:
            # ディレクトリ作成処理
            # 上位ディレクトリから順次作成
            flag_mkdir = False
            length_path = len(str(fil.parents[0]).split("/"))
            dir_mkd = str(Path("FTP")/"record_files_raspi3"/ext)
            for i in range(length_path):
                if flag_mkdir:
                    dir_mkd_parent = dir_mkd
                    dir_mkd = dir_mkd + "/" + fil.parents[length_path - (i+1)].name
                    if not dir_mkd in ftp.nlst(dir_mkd_parent):
                        ftp.mkd(dir_mkd + "/")  # 最後に/が必要
                    # upload処理
                    if i == (length_path - 1):
                        dir_mkd = dir_mkd + "/"
                        path_file = str(fil)
                        with open(path_file, "rb") as f:
                            ftp.storbinary("STOR " + dir_mkd + fil.name, f)
                        # アップロードしたファイルを削除
                        os.remove(path_file)
                if(fil.parents[length_path - (i+1)].name == ext): flag_mkdir = True
