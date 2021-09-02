FROM python:3.8.11-slim-buster

ENV TZ Asia/Tokyo
# apt
RUN apt update
RUN apt install -y ffmpeg cron at vim procps
RUN pip install beautifulsoup4 lxml html5lib
# add sudo user
#RUN groupadd -g 1000 ubuntu && \
#    useradd  -g      ubuntu -G sudo -m -s /bin/bash ubuntu && \
#    echo 'ubuntu:hogehoge' | chpasswd
#RUN echo 'Defaults visiblepw'            >> /etc/sudoers
#RUN echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
#USER ubuntu

# install
RUN echo '30 22 * * * cd /root/scripts; bash /root/scripts/GetSchedule.sh > /root/scripts/log_record.log' >> /etc/crontab
RUN echo '45 22 * * * cd /root/scripts; /usr/local/bin/python3 /root/scripts/11_send_mail.py > /root/scripts/log_mail.log' >> /etc/crontab
RUN echo '0 4 * * * cd /root/scripts; /usr/local/bin/python3 /root/scripts/21_Upload.py /root/scripts/record_files > /root/scripts/log_upload.log' >> /etc/crontab
RUN echo '0 0 * * * find /root/scripts/recording -mtime +5 | xargs rm' >> /etc/crontab
# start crontab
RUN crontab /etc/crontab
CMD ["cron", "-f"]
