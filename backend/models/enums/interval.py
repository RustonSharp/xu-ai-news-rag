
from enum import Enum

class IntervalEnum(str, Enum):
    MINUTE = 60
    HOUR = 60 * 60
    DAY = 24 * 60 * 60
