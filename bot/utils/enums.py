from enum import Enum

class Command(str, Enum):
    START = "start"
    STOP = "stop"