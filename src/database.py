import os
import pymongo
import log
import datetime

logger = log.Logger(["DATABASE", log.FGREEN])

INITIAL_VALUES = {}


def init_db():
    """
    Initializes the connection to database
    """
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


def add_user(uid: int, ist: bool):
    """
    Adds user to the database
    Doesn't add them if they are already in the db
    """
    if users.find_one({"uid": uid}) is None:
        users.insert_one({"uid": uid, "is_teacher": ist})


def is_teacher(uid: int) -> bool:
    """
    Checks if a user is a teacher
    """
    user = users.find_one({"uid": uid})
    if user is None:
        return False
    return user["is_teacher"]


def get_user_list():
    """
    Gets the list of all users
    """
    userlist = set()
    for user in users.find():
        userlist.add(user["uid"])
    return list(userlist)


def add_event(text: str, day: int):
    """
    Adds event
    """
    events.insert_one({"text": text, "timestamp": day})


def events_from_period(start: int, end: int):
    """
    Gets every event in [`start`;`end`) period
    """
    return list(events.find({"timestamp": {"$gte": start, "$lt": end}}))


def get_events_since(start: int):
    """
    Gets every event since `start` timestamp
    """
    return list(events.find({"timestamp": {"$gte": start}}))


def get_value(name):
    """
    Gets global value `name`
    """
    vs = values.find_one({})
    if vs.get(name) is None:
        logger.error("value {name} not found")
    else:
        return vs[name]


def update_value(name, value):
    """
    Updates global value `name` to `value`
    """
    logger.info(f"Updated {name} to {value}")
    values.update_one({}, {"$set": {name: value}})
