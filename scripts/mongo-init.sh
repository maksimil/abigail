#! /bin/sh

. ./env.sh
mongosh admin ./scripts/mongo-init.js --quiet
