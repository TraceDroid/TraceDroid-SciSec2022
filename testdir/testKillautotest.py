# -*- coding: utf-8 -*-
# @Time : 2021/5/8 16:50
# @Author : *
# @Site :
# @File : testKillautotest.py
# @Software: PyCharm
import os
import re
import signal
from subprocess import check_output
import psutil

def get_pid(name):
    return check_output(["pidof", name])


if __name__ == '__main__':
    pass




