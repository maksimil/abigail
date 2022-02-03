"""Module for database access"""
import os
import pymongo
import log
import datetime

logger = log.Logger(["DATABASE", log.FGREEN])

INITIAL_VALUES = {}


def init_db():
    """Initializes the connection to database"""
    global values, users, events

    # Connection to the database
    logger.info("Initializing the connection")
    root_username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    root_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    port = os.getenv("MONGO_PORT")

    logger.info("Starting the db...")

    client = pymongo.MongoClient(
        host="127.0.0.1",
        port=int(port),
        username=root_username,
        password=root_password,
    )

    abigail = client["abigail"]
    users = abigail["users"]
    events = abigail["events"]
    values = abigail["values"]

    # Initializing the values
    logger.info("Initializing values")

    ninit = INITIAL_VALUES.copy()

    vs = list(values.find({}))
    if len(vs) != 0:
        logger.info("Removing previous values")
        values.delete_many({})

        ninit.update(vs[0])
        del ninit["_id"]

    logger.info(f"Setting values to {ninit}")

    values.insert_one(ninit)

    logger.info("Started the db")


# Operations with users
UID = "uid"
IS_TEACHER = "is_teacher"


def add_user(uid: int, ist: bool):
    """
    Adds user to the database
    Doesn't add them if they are already in the db
    """
    if users.find_one({UID: uid}) is None:
        users.insert_one({UID: uid, IS_TEACHER: ist})
    logger.info(f"User list: {get_user_list()}")


def set_is_teacher(uid: int, its: bool):
    """Sets is_teacher status for a user"""
    users.update_one({UID: uid}, {"$set": {IS_TEACHER: its}})


def is_teacher(uid: int) -> bool:
    """Checks if a user is a teacher"""
    user = users.find_one({UID: uid})
    if user is None:
        logger.warn(f"is_teacher({uid}) failed because the uid is not in the db")
        return False
    return user[IS_TEACHER]


def get_user_list():
    """Gets the list of all users"""
    return [user[UID] for user in users.find()]


# Operations with events
TEXT = "text"
TIMESTAMP = "timestamp"


def add_event(text: str, day: int):
    """Adds event"""
    events.insert_one({TEXT: text, TIMESTAMP: day})


def events_from_period(start: int, end: int):
    """Gets every event in [`start`;`end`) period"""
    return list(events.find({TIMESTAMP: {"$gte": start, "$lt": end}}))


def get_events_since(start: int):
    """Gets every event since `start` timestamp"""
    return list(events.find({TIMESTAMP: {"$gte": start}}))


# Operations with global values
def get_value(name):
    """Gets global value `name`"""
    vs = values.find_one({})
    if vs.get(name) is None:
        logger.error("value {name} not found")
    else:
        return vs[name]


def update_value(name, value):
    """Updates global value `name` to `value`"""
    logger.info(f"Updated {name} to {value}")
    values.update_one({}, {"$set": {name: value}})
