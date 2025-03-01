import datetime
import time
from TICSUtil2 import TICSLogger, emoji

# New Method
Log = TICSLogger(dir="./logs", msg_col_len=90, rotation="100 KB").get_log()
Log.info(f"Logger Configured...")
Log.log(50, f"Sample LOG message")
Log.debug(f"Sample DEBUG message")
Log.info(f"Sample INFO message")
Log.warning(f"Sample WARNING message")
Log.error(f"Sample ERROR message")
Log.critical(f"Sample CRITICAL message")
Log.info(emoji["namaste"])

# Second Logger.
Log2 = TICSLogger(
    dir="./logs", console_level=None, filename="two", filter="two", msg_col_len=90, rotation="100 KB"
).get_log()
Log2.info("Second Log")

Log.info("After second log")

Log2.info("Second Again Log")


@Log.catch()
def exception_log():
    try:
        x = 1
        y = 0
        a = x / y
    except Exception as e:
        Log.exception(f"Sample EXCEPTION message with traceback. Error: {e}")


# Exception logging
exception_log()

####################################################################################################
# Third Logger -> Hourly Rotaing Log
# rotaion parameter can be "HOURLY" or "hourly". the log will rotate at the start of every hour
Log3 = TICSLogger(
    dir="./logs", console_level=None, filename="hourly", filter="three", msg_col_len=90, rotation="HOURLY"
).get_log()
####################################################################################################
# Logging from classes
class TestClass:
    def __init__(self):
        Log.info(f"TestClass Initialized")

    def test_func(self):
        Log2.info(f"Inside Test Func")

test1 = TestClass()
test1.test_func()

##############################################################################
def hourlyLogCheck(runPeriod):
        stopAt = datetime.datetime.now() + datetime.timedelta(hours=runPeriod)
        while datetime.datetime.now() < stopAt:
            Log3.info(f"hourly Log Check {datetime.datetime.now()}")
            time.sleep(2)

hourlyLogCheck(4)
##############################################################################



