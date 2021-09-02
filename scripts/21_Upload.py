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
        "xxx.xxx.xxx.xxx",
        "ftp_user",
        passwd="xxxx"
        )
    # -mp4ファイルの一覧を取得- #
    list_ext = ["mp4", "mp3"]
    for ext in list_ext:
        path = Path(dirPath)/ext
        files = path.glob('**/*.' + ext)
        # -アップロード処理- #
        for fil in files:
            # ディレクトリ作成処理
            dir_parent01 = str(Path(dirPath).name)
            dir_parent02 = str(fil.parents[0]).split("/")[-2]
            dir_parent03 = str(fil.parents[0]).split("/")[-1]
            dir_mkd = str(Path("FTP")/dir_parent01/dir_parent02/dir_parent03)
            dir_mkd_parent = str(Path("FTP")/dir_parent01/dir_parent02)
            if not dir_mkd in ftp.nlst(dir_mkd_parent):
                ftp.mkd(dir_mkd + "/")  # 最後に/が必要
            dir_mkd = dir_mkd + "/"
            # upload処理
            path_file = str(fil)
            with open(path_file, "rb") as f:
                ftp.storbinary("STOR " + dir_mkd + fil.name, f)
            # アップロードしたファイルを削除
            os.remove(path_file)
