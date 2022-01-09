import os
import pymongo
import log
import datetime

MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")


def __init__():
    global values, users, events, notices
    log.info(log.DB, "Starting the db...")

    client = pymongo.MongoClient(
        host="127.0.0.1",
        port=27017,
        username=MONGO_INITDB_ROOT_USERNAME,
        password=MONGO_INITDB_ROOT_PASSWORD,
    )

    abigail = client["abigail"]
    users = abigail["users"]
    events = abigail["events"]
    notices = abigail["notices"]
    values = abigail["values"]

    initialize_values()

    log.info(log.DB, "Started the db")


LAST_NOTICE_UPDATE = "last_notice_update"
INITIAL_VALUES = {LAST_NOTICE_UPDATE: 0}


def initialize_values():
    log.info(log.DB, "Initializing values")

    ninit = INITIAL_VALUES.copy()

    vs = list(values.find({}))
    if len(vs) != 0:
        log.info(log.DB, f"Removing previous values")
        values.delete_many({})

        ninit.update(vs[0])
        del ninit["_id"]

    log.info(log.DB, f"Setting values to {ninit}")

    values.insert_one(ninit)
    log.info(log.DB, "Initialized values")


def add_user(uid: int, ist: bool):
    """
    adds user to the database
    doesn't add them if they are already in the db
    """
    if users.find_one({"uid": uid}) is None:
        users.insert_one({"uid": uid, "is_teacher": ist})


def is_teacher(uid: int) -> bool:
    """
    checks if a user is a teacher
    """
    user = users.find_one({"uid": uid})
    if user is None:
        return False
    return user["is_teacher"]


def get_user_list():
    """
    gets the list of all users
    """
    userlist = set()
    for user in users.find():
        userlist.add(user["uid"])
    return list(userlist)


def add_event(text: str, day: int):
    """
    Adds event
    Timestamp is in unix seconds
    """
    events.insert_one({"text": text, "timestamp": day})


def add_notice(text: str, timestamp: int):
    """
    Adds notice
    Timestamp is in unix seconds
    """
    notices.insert_one({"text": text, "timestamp": timestamp})


def events_from_period(start: int, end: int):
    return list(events.find({"timestamp": {"$gte": start, "$lt": end}}))


def get_events_since(start: int):
    return list(events.find({"timestamp": {"$gte": start}}))


def notices_from_period(start: int, end: int):
    return list(notices.find({"timestamp": {"$gte": start, "$lt": end}}))


def get_notices_since(start: int):
    return list(notices.find({"timestamp": {"$gte": start}}))


def get_value(name):
    vs = values.find_one({})
    if vs.get(name) is None:
        log.error(log.DB, "value {name} not found")
    else:
        return vs[name]


def update_value(name, value):
    log.info(log.DB, f"Updated {name} to {value}")
    values.update_one({}, {"$set": {name: value}})


def get_unmarked_notices():
    last_update = get_value(LAST_NOTICE_UPDATE)
    update_timestamp = datetime.datetime.now().timestamp()
    notices = notices_from_period(last_update, update_timestamp)
    update_value(LAST_NOTICE_UPDATE, update_timestamp)
    return notices


__init__()
