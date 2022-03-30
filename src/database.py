"""Module for database access"""
import os
import pymongo
import log
import datetime
from dataclasses import dataclass, asdict
from typing import Optional

logger = log.Logger(["DATABASE", log.FGREEN])

INITIAL_VALUES = {}


def init_db():
    """Initializes the connection to database"""
    global values, users, events, homework

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
    homework = abigail["homework"]

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
@dataclass
class Event:
    """Represents an object in event"""

    text: str
    date: datetime.datetime


NOID_PROJECT = {"_id": False}


def add_event(event: Event):
    """Adds event"""
    events.insert_one(asdict(event))


def get_event_date(mfilter):
    """
    Gets events filtered by date
    https://www.mongodb.com/docs/realm/rules/filters
    """
    data = events.find({"date": mfilter}, NOID_PROJECT)
    return [Event(**e) for e in data]


# Operations with homework
SUBJECT = "subject"
TIMESTAMP = "timestamp"
TEXT = "text"


def add_hw(subject: str, timestamp: int, text: str):
    """Adds homework"""
    homework.insert_one({SUBJECT: subject, TIMESTAMP: timestamp, TEXT: text})


def get_hw_since(start: int):
    """Get homework since"""
    return list(homework.find({TIMESTAMP: {"$gte": start}}))


def get_hw_date(date: int):
    """Get homework by date"""
    date = date - date % (24 * 60 * 60)
    return list(homework.find({TIMESTAMP: date}))


def get_hw_period(start: int, finish: int):
    """Get hw in period [start;finish)"""
    return list(homework.find({TIMESTAMP: {"$gte": start, "$lt": finish}}))


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
