#!/usr/bin/env sh

. ./env.sh
docker-compose up --build -d
docker logs -f $(docker ps -f $(printf "ancestor=%s_python" "$PROJECTNAME") --format "{{.ID}}")
