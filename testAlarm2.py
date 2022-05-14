import os
import signal
import time


def sigHandler(signum, frame):
    print("received signal %s", signum)
    print("Now, it's the time")
    exit()

#signal.signal(signal.SIGALRM, sigHandler)
signal.signal(signal.SIGINT, sigHandler)
    #signal.signal()
    #signal.alarm()



while True:
    print("not yet")
    print("child pid %s" % os.getpid())
    with open("child_file_new", "a", encoding="utf-8") as f:
        f.write("pid: " + str(os.getpid()))
        f.write("\n")
        #f.flush()
        #f.close()
    time.sleep(1)
