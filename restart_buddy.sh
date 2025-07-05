#!/bin/bash
sudo docker network inspect mjapi >/dev/null 2>&1 || sudo docker network create mjapi

image_version=$(sudo docker image ls|grep buddyagent|tail -n +1|head -n 1|awk -F ' ' '{print $2}'|cut -f2 -d '.')
incr_number=$(($image_version+1))
new_version="0."$incr_number".0"

echo 'start build buddyagent with new version=>'$new_version

sudo docker build -t buddyagent:$new_version .

echo 'build done'

ps_id=$(sudo docker ps|grep buddyagent|tail -n +1|cut -f1 -d ' ')

echo 'stop=>'$ps_id'and restart with new version=>'$new_version

if [ -z "$ps_id" ]; then
    echo "No running container found. Skipping stop operation."
else
    sudo docker stop $ps_id
fi

sudo docker rm buddyagent -f

sudo docker run -d --net mjapi --name buddyagent -p  8000:8000 buddyagent:$new_version

echo 'buddyagent restart done'

echo '------------------------>logs of new container------------------------>'
new_ps_id=$(sudo docker ps|grep buddyagent|tail -n +1|cut -f1 -d ' ')

sudo docker logs $new_ps_id -f