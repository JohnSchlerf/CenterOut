# This lets me import code in the "devices" directory using
# the syntax: "from devices import <X>"

try: from Clock import *
except (ImportError): 
    print("Clock.py is broken or missing.")

try: from Monitor import *
except (ImportError):
    print("Monitor.py is broken or missing.")

try: from Cursor import *
except (ImportError): 
    print("Cursor.py is broken or missing.")
