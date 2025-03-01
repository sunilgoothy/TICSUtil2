# TICS Event manager must be running for this program to work.
import redis
from TICSUtil2 import Event


rclient = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


EVENT = Event(rclient)

evt_data = "TES_TEVENT_STRING"
EVENT.send("TESTEVENT", evt_data)

evt_data1 = 1
EVENT.send("TESTEVENT1", evt_data1)

evt_data2 = ["one", 2, 3.33]
EVENT.send("TESTEVENT2", evt_data2)

evt_data3 = {"k1": "Key1", "k2": 2, "k3": 3.33}
EVENT.send("TESTEVENT3", evt_data3)
