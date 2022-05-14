import os
import re
import signal
from subprocess import check_output
import psutil

def get_pid(name):
    return check_output(["pidof", name])


if __name__ == '__main__':
    pass




