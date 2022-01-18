#!/usr/bin/env sh

. ./env.sh
docker-compose up -d
docker logs -f $(docker ps | awk '{if($2=="abigail_python"){print $1}}')
