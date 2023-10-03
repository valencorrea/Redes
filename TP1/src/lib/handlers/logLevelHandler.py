from enum import Enum


class LogLevel(Enum):
    HIGH = 2
    NORMAL = 1
    LOW = 0


def retrieve_level(v=False, q=False):
    if v:
        return LogLevel.HIGH
    if q:
        return LogLevel.LOW
    return LogLevel.NORMAL


def log(message, level, actual_level):
    if level <= actual_level:
        print(message)
