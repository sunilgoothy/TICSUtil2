import timeit, datetime

############ Perf Test for Logging ###################
# code snippet to be executed only once
mysetup = """
from TICSUtil2 import TICSLogger
Log = TICSLogger(
    dir="./logs", console_level="error", filename="hourly", filter="three", msg_col_len=90, rotation="HOURLY"
).get_log()
"""

# code snippet whose execution time is to be measured
mycode = """  
Log.debug("I")
"""
    

# timeit statement
exec_time = timeit.timeit(setup=mysetup, stmt=mycode, number=100000)
print(f"Perf Test Execution time: {exec_time} secs")
