from TICSUtil2 import TICSLogger
import time

# Log = TICSLogger(dir="./logs", msg_col_len=90).get_log()
# Log = TICSLogger(dir="./logs", msg_col_len=90, rotation="18:39").get_log()
Log = TICSLogger(dir="./logs", msg_col_len=90, rotation="1 KB").get_log()


for i in range(10000):
    Log.info(f"{i}: Sample INFO message")
    time.sleep(0.1)
