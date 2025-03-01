# TICS Alarm Manager must be running for this program to work.
import redis
from TICSUtil2 import Alarm


rclient = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


alarm = Alarm(rclient, "testalarm")


def call_alarm():
    alarm.low("LOW ALARM")
    alarm.medium("Medium ALARM")
    alarm.high("high Alarm")


call_alarm()
# alarm.low("Low QWERTYU")
# alarm.medium("Medium QWERTYU")
# alarm.high("high QWERTYU")
