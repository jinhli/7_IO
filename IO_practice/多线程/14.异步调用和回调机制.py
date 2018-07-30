#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/26/18


# 提交任务的两种模式
#1， 同步调用提交完成任务后， 就在原地等待人物执行完成， 再执行下一行代码


from concurrent.futures import ThreadPoolExecutor
import time
import random


pool=ThreadPoolExecutor(13)











# 2 异步调用, 提交任务完成后， 不在等待结果


