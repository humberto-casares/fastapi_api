from google.protobuf import timestamp_pb2
from datetime import datetime
from enum import Enum, auto
from typing import TypedDict
import time
from zoneinfo import ZoneInfo

SERVICE_NAME = "academia_tesla"
mexico_tz = ZoneInfo("America/Mexico_City")

class StrEnum(str, Enum):
    """
    Override Enum class to return String values
    """

    def __new__(cls, *args):
        for arg in args:
            if not isinstance(arg, (str, auto)):
                raise TypeError("Values of StrEnums must be strings: {} is a {}".format(repr(arg), type(arg)))
        return super().__new__(cls, *args)

    def __str__(self):
        return str(self.value)

    def _generate_next_value_(name, *_):
        return name

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class MessageEnvelopeHeaderRow(TypedDict):
    """
    Kafka Message 'Header' field's definition
    """
    name: str
    topic: str
    timestamp: int
    partition: int
    offset: int


class MessageEnvelopeRow(TypedDict):
    """
    Kafka Message field's definition
    """
    headers: MessageEnvelopeHeaderRow
    events: dict
    body: dict


class EventClasses(StrEnum):
    """
    Protobuf Events Headers name
    """
    EVENT = "mx.academia_tesla.common.register.proto.RegisterEvent"

class KafkaTopics(StrEnum):
    """
    Kafka Events processed
    """
    REGISTER_EVENTS = "RegisterEvent"

class Tables(StrEnum):
    """
    list of tables name
    """
    TASKS = "tasks"
    LOCK_MANAGEMENT = "lock_management"


class LockManagementCols(StrEnum):
    """
    LockManagement table column's name
    """
    NAME = "name"
    EXPIRE_AT = "expire_at"


def mx_now():
    return datetime.now(mexico_tz)

def mx_now_timestamp():
    current_time = mx_now()
    # Convert the current time to a UNIX timestamp (seconds since epoch) and multiply by 1,000,000 for microseconds
    timestamp_microseconds = int(time.mktime(current_time.timetuple()) * 1_000_000 + current_time.microsecond)
    return timestamp_microseconds


def get_proto_time(date: datetime = None) -> timestamp_pb2.Timestamp:
    t = timestamp_pb2.Timestamp()
    t.FromDatetime(date)
    return t
