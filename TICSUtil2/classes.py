import os, sys, inspect, datetime, json
from loguru import logger
import __main__

# stdout unbuffering
# sys.stdout = os.fdopen(sys.stdout.fileno(), "w", buffering=1)
# sys.stderr = os.fdopen(sys.stderr.fileno(), "w", buffering=1)


class Event:
    """Class for sending events from TICS programs. TICSEvtMgr must be running for this to work"""

    def __init__(self, redis_client, pub_channel: str = "event_queue"):
        self.rclient = redis_client
        self.channel = pub_channel

    def send(self, event: str, data, tag_val: int = 1):
        evt_dict = {"tag": event, "value": tag_val, "data": data}
        # print(f"event_data: {evt_dict}")

        self.rclient.publish(self.channel, json.dumps(evt_dict))


class Alarm:
    """Class for rasing alarms from TICS programs. TICSAlmMgr must be running for this to work"""

    def __init__(self, redis_client, prg_name: str, call_depth: int = 2):
        self.rclient = redis_client
        self.program = prg_name
        self.call_depth = call_depth

    def send_alarm(self, alm_prio: str, alm_desc: str):
        alm_data: dict = {}
        call_func = inspect.stack()[self.call_depth][3]
        alm_data["alm_dt"] = str(datetime.datetime.now())
        alm_data["alm_tag"] = self.program
        alm_data["alm_type"] = call_func
        alm_data["alm_desc"] = alm_desc
        alm_data["alm_prio"] = alm_prio

        # print(call_func)

        self.rclient.publish("alarm_queue", json.dumps(alm_data))

    def high(self, alm_desc: str):
        self.send_alarm(alm_prio="HIGH", alm_desc=alm_desc)

    def medium(self, alm_desc: str):
        self.send_alarm(alm_prio="MEDIUM", alm_desc=alm_desc)

    def low(self, alm_desc: str):
        self.send_alarm(alm_prio="LOW", alm_desc=alm_desc)

    def oplog(self, desc: str, piece: str = "", host: str = "", user: str = "", func: str = ""):
        log_data: dict = {}
        log_data["opertime"] = str(datetime.datetime.now())
        log_data["opername"] = user
        log_data["function"] = func
        log_data["terminal"] = host
        log_data["piecename"] = piece
        log_data["message"] = desc
        self.rclient.publish("log_queue", json.dumps(log_data))

class LogRotation:
    """ Hourly Log Rotaion , interval -> Hours [must be interger]"""
    def __init__(self, interval) -> None:
        self.rotationInterval = interval
        self.setNextChangeTimeStamp()
        self.startUp = True
        
    def setNextChangeTimeStamp(self):
        self.nextChangeTimeStamp:datetime = datetime.datetime.now().astimezone().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours = self.rotationInterval)

    def logRotate(self, message, file):
        # rotate the log if the log time is in the next hour
        logTime = message.record["time"]
        if  logTime > self.nextChangeTimeStamp :
            self.setNextChangeTimeStamp()
            return True
        
        #rotate log if the current log file hour in not the current hour. Checked only at startup once.
        if self.startUp:
            try:
                with open(file.name, 'r') as file:
                    firstLine = file.readline()
                    timefomrat = "%Y-%m-%d %H:%M:%S"
                    lastLogFileStartTime :datetime.datetime = datetime.datetime.strptime(firstLine.split('|')[0].split('.')[0]  , timefomrat)
                    if lastLogFileStartTime.replace(minute=0, second=0, microsecond=0)  != datetime.datetime.now().replace(minute=0, second=0, microsecond=0):
                        self.startUp = False
                        return True
            except Exception:
                        pass
            self.startUp = False

        return False
    

def make_filter(name):
    def filter(record):
        return record["extra"].get("name") == name

    return filter


class TICSLogger:
    def __init__(
        self,
        filename=None,
        filter=None,
        dir=None,
        max_num=10,
        colorize=True,
        file_level="debug",
        console_level="debug",
        msg_col_len=80,
        rotation="00:00",
    ):
        self.msg_col_len = msg_col_len
        if filename is None:
            full_path = __main__.__file__
            script_name = os.path.basename(os.path.realpath(full_path))
            # print(f"{script_name = }")
            filename = script_name[:-3]

        if dir is None:
            full_path = __main__.__file__
            dir = os.path.dirname(os.path.realpath(full_path))

        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)

        if file_level is not None:
            file_level = file_level.upper()

        if console_level is not None:
            console_level = console_level.upper()

        #Hourly Log Rotation - with one hour are interval
        if rotation == "HOURLY" or rotation == "hourly":
            logRotator = LogRotation(interval = 1)
            rotation = logRotator.logRotate

        # Setup Filter for multi instance of Log File
        self.filter = "Default" if not filter else filter
        filter = make_filter(self.filter)

        # Setup loguru logger to TICS formatting.
        fmt = f"<green>{{time:YYYY-MM-DD HH:mm:ss.SSS}}</green> | <level>{{level: <8}}</level> | <level>{{message: <{msg_col_len}}}</level> | <cyan>{{function}}</cyan>:<cyan>{{line}}</cyan>"
        

        # Configure console logger
        if console_level is not None:
            logger.remove()  # Remove default logger
            logger.add(
                sys.stderr,
                level=console_level,
                format=fmt,
                colorize=colorize,
                enqueue=True,
                backtrace=False,
                diagnose=True,
            )

        # Configure file logger
        if file_level is not None:
            log_file_name = os.path.join(dir, filename)
            logger.add(
                log_file_name + ".log",
                level=file_level,
                filter=filter,
                format=fmt,
                rotation=rotation,
                retention=max_num,
                enqueue=True,
                backtrace=False,
                diagnose=True,
                delay=True,
            )

    def get_log(self):
        return logger.bind(msg_col_len=self.msg_col_len, name=self.filter)
