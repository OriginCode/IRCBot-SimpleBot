#!/usr/bin/env python2
# -*- coding:utf8 -*-

# Import area
import socket
import ssl
import time
import os
import re
import requests
import json

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import module.calc_base as calc_base
import module.base as base

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Main functions

# Connect to the server
socket.connect((base.NETWORK, base.PORT))
irc = ssl.wrap_socket(socket)

# Sign into the server
irc.send('PASS %s\r' % base.PASSWD)
irc.send('NICK %s\r' % base.NICK)
irc.send('USER %s %s %s :SimpleBot\r' % (base.NICK, base.NICK, base.NICK))
for i in range(len(base.CHAN)):
    irc.send('JOIN #' + base.CHAN[i] + '\r')


def irc_send(string, chan, obj):
    irc.send('PRIVMSG %s :%s: %s' % (chan, obj, string))


def irc_send_nou(string, chan):
    irc.send('PRIVMSG %s :%s' % (chan, string))


# Functions
def main():
    while True:
        data = irc.recv(4096)
        print data
        user = data[data.find(':') + 1:data.find('!')]
        try:
            chan = re.split(r'\s?', data)[2]

        except IndexError, errout:
            print errout
            continue

        if data.find('PING') != -1:
            irc.send('PONG ' + data.split()[1] + '\r')

        if re.match(r'#\w', chan):
            if data.find('::') != -1:
                inc = data[data.find('::') + 2:len(data) - 1]
                if re.match(r'^test\r$', inc):
                    irc.send('PRIVMSG %s :Success!\r' % chan)

                elif re.match(r'^version\r$', inc):
                    irc_send('3.3.0\r', chan, user)

                elif re.match(r'^fortune\r$', inc):
                    output = os.popen('fortune').read().split('\n')
                    for i in xrange(len(output) - 1):
                        irc_send_nou('%s\r' % output[i].replace('\t', '    '), chan)

                elif re.match(r'^echo\s.+\r$', inc):
                    irc_send_nou('%s\r' % inc[inc.find('echo') + 5:len(inc) - 1], chan)

                # Time

                elif re.match(r'^time\r$', inc):
                    os.environ['TZ'] = 'Asia/Shanghai'
                    time.tzset()
                    irc_send('Time: %s (CST/GMT+8)\r' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), chan, user)

                elif re.match(r'^time\stz:[+-]\d{1,3}\r$', inc):
                    if -12 <= int(inc[inc.find('tz:') + 3:len(inc) - 1]) <= 14:
                        irc_send('Time: %s (CST/GMT%s)\r' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 3600 + int('%s' % inc[inc.find('tz:') + 3:len(inc) - 1]) * 3600)), inc[inc.find('tz:') + 3:len(inc) - 1]), chan, user)

                    else:
                        irc_send('Argument must be lower than 14 and higher than -12\r', chan, user)

                elif re.match(r'^time\suts\r$', inc):
                    irc_send('Unix Timestamp: %s\r' % time.time(), chan, user)

                # Calculate

                elif re.match(r'^calc\s.+\r$', inc):
                    s = inc[inc.find('cal') + 5:len(inc) - 1].replace(' ', '')
                    try:
                        answer = calc_base.l1_analysis(s)

                    except Exception, errout:
                        irc_send('%s\r' % errout, chan, user)
                        continue

                    irc_send('%s\r' % answer, chan, user)

                elif re.match(r'^wiki\s.+\r$', inc):
                    insert = inc[inc.find('wiki') + 5:len(inc) - 1].replace(' ', '_')
                    r = requests.get('https://en.wikipedia.org/wiki/%s' % insert)
                    if r.status_code == 404:
                        irc_send('tan90°\r', chan, user)
                    else:
                        irc_send('--> https://en.wikipedia.org/wiki/%s <--\r' % insert, chan, user)

                elif re.match(r'^github\(all\)\s.+\r$', inc):
                    insert = inc[inc.find('github(all)') + 12:len(inc) - 1].replace(' ', '+')
                    irc_send('--> https://github.com/search?q=%s <--\r' % insert, chan, user)

                elif re.match(r'^github\(user\)\s.+\r$', inc):
                    insert = inc[inc.find('github(user)') + 13:len(inc) - 1].replace(' ', '+')
                    headers = {
                        'Accept': 'application/vnd.github.v3.text-match+json'
                    }
                    req = requests.get('https://api.github.com/search/users?q=%s' % insert, headers=headers)
                    js = req.json()
                    try:
                        name = js['items'][0]['login']
                        link = js['items'][0]['html_url']

                    except IndexError, errout:
                        irc_send('tan90°\r', chan, user)
                        print errout
                        continue

                    irc_send('Top: [ %s ] - %s\r' % (name, link), chan, user)

                elif re.match(r'^github\(\w+\)\s.+\r$', inc):
                    insert = inc.split(' ')[1]
                    lang = inc[inc.find('(') + 1:inc.find(')')]
                    headers = {
                        'Authentication': 'token TOKEN',
                        'Accept': 'application/vnd.github.mercy-preview+json'
                    }
                    req = requests.get('https://api.github.com/search/repositories?q=%s+language:%s' % (insert, lang), headers=headers)
                    js = req.json()
                    try:
                        name = js['items'][0]['full_name']
                        link = js['items'][0]['html_url']
                        star = js['items'][0]['stargazers_count']
                        fork = js['items'][0]['forks_count']
                        description = js['items'][0]['description']

                    except IndexError, errout:
                        irc_send('tan90°\r', chan, user)
                        print errout
                        continue

                    irc_send('Top: [ %s ] - %s - Stars: %s Forks: %s\r' % (name, link, star, fork), chan, user)
                    irc_send_nou('Description: %s\r' % description, chan)

                elif re.match(r'^github\s.+\r$', inc):
                    insert = inc[inc.find('github') + 7:len(inc) - 1].replace(' ', '+')
                    headers = {
                        'Authentication': 'token TOKEN',
                        'Accept': 'application/vnd.github.mercy-preview+json'
                    }
                    req = requests.get('https://api.github.com/search/repositories?q=%s' % insert, headers=headers)
                    js = req.json()
                    try:
                        name = js['items'][0]['full_name']
                        link = js['items'][0]['html_url']
                        star = js['items'][0]['stargazers_count']
                        fork = js['items'][0]['forks_count']
                        # description = js['items'][0]['description']

                    except IndexError, errout:
                        irc_send('tan90°\r', chan, user)
                        print errout
                        continue

                    irc_send('Top: [ %s ] - %s - Stars: %s Forks: %s\r' % (name, link, star, fork), chan, user)

                elif re.match(r'^pypi\s.+\r$', inc):
                    insert = inc[inc.find('pypi') + 5:len(inc) - 1]
                    req = requests.get('http://pypi.python.org/pypi/%s/json' % insert)
                    try:
                        js = req.json()

                    except ValueError, errout:
                        irc_send('tan90°\r', chan, user)
                        print errout
                        continue

                    link = js['info']['package_url']
                    author = js['info']['author']
                    version = js['info']['version']
                    name = js['info']['name']

                    irc_send('Top: [ %s - %s ] - %s - Ver: %s\r' % (author, name, link, version), chan, user)

                elif re.match(r'^weather\s.+\r$', inc):
                    insert = inc[inc.find('weather') + 8:len(inc) - 1]
                    req = requests.get('http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=%s' % (insert, base.WEATHER_APPID))
                    js = req.json()
                    try:
                        country = js['sys']['country']
                        city = js['name']
                        weather = js['weather'][0]['main']
                        temp = int(js['main']['temp']) - 273.15
                        wind_speed = js['wind']['speed']

                    except Exception, errout:
                        irc_send('tan90°\r', chan, user)
                        print errout
                        continue

                    irc_send('[ %s - %s ] Weather: %s, Current Temperature: %d °C, Wind Speed: %s Mps.\r' % (country, city, weather, temp, wind_speed), chan, user)

                elif re.match(r'^zhweather\s.+\r$', inc):
                    insert = inc[inc.find('zhweather') + 10:len(inc) - 1]
                    req = requests.get('https://api.seniverse.com/v3/weather/now.json?key=%s&location=%s&language=zh-Hans&unit=c' % (base.CHWEATHER_APPID, insert))
                    js = req.json()
                    try:
                        last_update = js['results'][0]['last_update']
                        country = js['results'][0]['location']['country']
                        city = js['results'][0]['location']['name']
                        weather = js['results'][0]['now']['text']
                        temp = js['results'][0]['now']['temperature']

                    except Exception, errout:
                        irc_send('tan90°\r', chan, user)
                        print errout
                        continue

                    irc_send('[ %s - %s ] 当前天气：%s， 当前温度：%s °C， 最后更新时间：%s\r' % (country, city, weather, temp, last_update), chan, user)

                elif re.match(r'^city2id(\s|\(tq\)\s)[A-Z].+\r$', inc):
                    if re.match(r'^city2id\s[A-Z].+\r$', inc):
                        insert = inc[inc.find('city2id') + 8:len(inc) - 1]

                    elif re.match(r'^city2id\(tq\)\s[A-Z].+\r$', inc):
                        insert = inc[inc.find('city2id(tq)') + 12:len(inc) - 1]

                    f = file('json/city-city_id.json')
                    js = json.load(f)
                    try:
                        city_id = js[insert]

                    except KeyError, errout:
                        irc_send('tan90°\r', chan, user)
                        print errout
                        continue

                    if re.match(r'^city2id\s[A-Z].+\r$', inc):
                        irc_send('%s - %d\r' % (insert, city_id), chan, user)

                    elif re.match(r'^city2id\(tq\)\s[A-Z].+\r$', inc):
                        irc_send_nou('tq2 %s\r' % city_id, chan)

                elif re.match(r'^zhuyin\s.+$', inc):
                    insert = inc[inc.find('zhuyin') + 7:len(inc) - 1]
                    req = requests.get('https://www.moedict.tw/uni/%s' % insert)
                    js = req.json()
                    try:
                        zhuyin = js['heteronyms'][0]['bopomofo']
                        zhuyin1 = js['heteronyms'][0]['bopomofo2']

                    except Exception, errout:
                        irc_send('tan90°\r', chan, user)
                        print errout
                        continue

                    irc_send('%s - %s\r' % (zhuyin, zhuyin1), chan, user)

                elif re.match(r'^chanlist\r$', inc):
                    irc_send('See the private chat.\r', chan, user)
                    for i in range(len(base.CHAN)):
                        irc.send('PRIVMSG %s :#%s\r' % (user, base.CHAN[i]))

                elif re.match(r'^tell\s#.+\s.+\r$', inc):
                    regex_split = re.split('\s', inc)
                    insert = inc[inc.find('#') + len(regex_split[1]) + 1:len(inc)]
                    irc_send_nou('%s from %s told: %s\r' % (user, chan, insert), regex_split[1])

                elif re.match(r'^sh\s.+\r$', inc):
                    data = irc.recv(4096)
                    print data
                    inc_ = data[data.find('::') + 2:len(data) - 1]
                    if re.match('^ps\s%s\r$' % base.ADMIN_PASSWD, inc_):
                        output = os.popen(inc[inc.find('sh') + 3:len(inc) - 1]).read().split('\n')
                        for i in xrange(len(output) - 1):
                            irc_send_nou('%s\r' % output[i].replace('\t', '    '), chan)

                elif re.match(r'^exit\r$', inc):
                    data = irc.recv(4096)
                    print data
                    inc_ = data[data.find('::') + 2:len(data) - 1]
                    if re.match('^ps\s%s\r$' % base.ADMIN_PASSWD, inc_):
                        irc.send('QUIT :Going to leave.\r')
                        exit(0)

if __name__ == '__main__':
    main()
