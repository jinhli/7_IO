#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/27/18

from concurrent.futures import ThreadPoolExecutor
import requests
import time

def get(url):
    print('GET %s' % url)
    response = requests.get(url)
    time.sleep(3)
    return {'url':url,'content':response.text}


def parse(res):
    res = res.result()
    print('****************')
    # print(res['url'])
    print("%s parse res is %s" % (res['url'], len(res['content'])))


if __name__== '__main__':
    urls = [
        'https://www.baidu.com',
        'https://www.python.org',
        'https://www.openstack.org',
        'https://help.github.com/',
        'http://www.sina.com.cn/'
    ]
    p = ThreadPoolExecutor(2)
    for url in urls:
        p.submit(get, url).add_done_callback(parse)