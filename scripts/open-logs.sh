#!/usr/bin/env bash

. ./env.sh
docker logs -f $(docker ps -f $(printf "ancestor=%s_python" "$PROJECTNAME") --format "{{.ID}}")
