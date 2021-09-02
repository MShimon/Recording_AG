# How to run
1. build docker image
```
$ docker image build ./ -t record-ag
```

2. run docker container
```
$ docker container run -itd --mount type=bind,src=/home/ubuntu/Recording_AG/scripts,dst=/root/scripts record-ag
```
3. install package at host_machine
```
$ apt install ffmpeg at
```
4. make directory at host_machine
```
$ mkdir ./recording_files/mp4
$ mkdir ./recording_files/mp3
```
5. add below at host_machine's crontab
```
@reboot docker container run -itd --mount type=bind,src=/home/ubuntu/Recording_AG/scripts,dst=/root/scripts record-ag
40 22 * * * cd /home/ubuntu/Recording_AG/scripts; /usr/bin/python3 /home/ubuntu/Recording_AG/scripts/03_reservation.py > /tmp/log_record.log
```