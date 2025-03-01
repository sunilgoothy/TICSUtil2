from TICSUtil2 import read_config_file, write_config_file
import datetime as dt

test_config = read_config_file("test_config.ini", "test_section", "my_var")
print(test_config)

write_config_file("test_config.ini", "test_section", "my_write_var", str(dt.datetime.now()))
