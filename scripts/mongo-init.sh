#!/usr/bin/env sh

. ./env.sh
mongosh mongodb://127.0.1:27077/admin ./scripts/mongo-init.js --quiet
