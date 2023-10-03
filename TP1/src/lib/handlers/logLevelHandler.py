from enum import Enum


class LogLevel(Enum):
    HIGH = 2
    NORMAL = 1
    LOW = 0


def retrieveLevel(v=False, q=False):
    if v:
        return LogLevel.HIGH
    if q:
        return LogLevel.LOW
    return LogLevel.NORMAL


def log(message, level, actualLevel):
    if level <= actualLevel:
        print(message)
