#! /bin/sh

. ./env.sh
mongosh $(printf "mongodb://127.0.0.1:%s/admin" "$MONGO_PORT") -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD"
