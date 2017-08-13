#!/usr/bin/env python2
# -*- coding:utf-8 -*-

# Import area
import socket
import ssl
import time
import os
import re
import requests

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

                elif re.match(r'^help\r$', inc):
                    irc.send('PRIVMSG %s :%s: See the private chat.\r' % (chan, user))
                    irc.send('PRIVMSG %s :The command of %s starts with \":\".\r' % (user, base.NICK))
                    irc.send('PRIVMSG %s :----------Help of %s----------\r' % (user, base.NICK))
                    irc.send('PRIVMSG %s :[version]Show the version of %s.\r' % (user, base.NICK))
                    irc.send('PRIVMSG %s :[time]Show the time. Format: :time (tz:[Number](Default: GMT+8))(uts(Show Unix Timestamp)).\r' % user)
                    irc.send('PRIVMSG %s :[fortune]Tell a fortune.\r' % user)
                    irc.send('PRIVMSG %s :[echo ...]Print the message you told to %s.\r' % (user, base.NICK))
                    irc.send('PRIVMSG %s :[calc ...]Calculator.\r' % user)
                    irc.send('PRIVMSG %s :[tell #channel ...]Tell something to the other channel. Do not type other commands until the bot replied sent successfully.\r' % user)
                    irc.send('PRIVMSG %s :[wiki ...]Search in Wikipedia.\r' % user)
                    irc.send('PRIVMSG %s :[github ...]Search repositories/users in GitHub. Usage: github .../github(user) .../github(LANGUAGE) ...\r' % user)

                elif re.match(r'^version\r$', inc):
                    irc.send('PRIVMSG %s :%s: 3.3.0\r' % (chan, user))

                elif re.match(r'^fortune\r$', inc):
                    output = os.popen('fortune').read().split('\n')
                    for i in xrange(len(output) - 1):
                        irc.send('PRIVMSG %s :%s\r' % (chan, output[i].replace('\t', '    ')))

                elif re.match(r'^echo\s.+\r$', inc):
                    irc.send('PRIVMSG %s :%s\r' % (chan, inc[inc.find('echo') + 5:len(inc) - 1]))

                # Time

                elif re.match(r'^time\r$', inc):
                    os.environ['TZ'] = 'Asia/Shanghai'
                    time.tzset()
                    irc.send('PRIVMSG %s :%s: Time: %s (CST/GMT+8)\r' % (chan, user, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))

                elif re.match(r'^time\stz:[+-]\d{1,3}\r$', inc):
                    if -12 <= int(inc[inc.find('tz:') + 3:len(inc) - 1]) <= 14:
                        irc.send('PRIVMSG %s :%s: Time: %s (CST/GMT%s)\r' % (chan, user, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 3600 + int('%s' % inc[inc.find('tz:') + 3:len(inc) - 1]) * 3600)), inc[inc.find('tz:') + 3:len(inc) - 1]))

                    else:
                        irc.send('PRIVMSG %s :%s: Argument must be lower than 14 and higher than -12\r' % (chan, user))

                elif re.match(r'^time\suts\r$', inc):
                    irc.send('PRIVMSG %s :%s: Unix Timestamp: %s\r' % (chan, user, time.time()))

                # Calculate

                elif re.match(r'^calc\s.+\r$', inc):
                    s = inc[inc.find('cal') + 5:len(inc) - 1]
                    s = s.replace(' ', '')
                    try:
                        answer = calc_base.l1_analysis(s)

                    except Exception, errout:
                        irc.send('PRIVMSG %s :%s: %s\r' % (chan, user, errout))
                        continue

                    irc.send('PRIVMSG %s :%s: %s\r' % (chan, user, answer))

                elif re.match(r'^wiki\s.+\r$', inc):
                    insert = inc[inc.find('wiki') + 5:len(inc) - 1].replace(' ', '_')
                    r = requests.get('https://en.wikipedia.org/wiki/%s' % insert)
                    if r.status_code == 404:
                        irc.send('PRIVMSG %s :%s: tan 90°\r' % (chan, user))
                    else:
                        irc.send('PRIVMSG %s :%s: --> https://en.wikipedia.org/wiki/%s <--\r' % (chan, user, insert))

                elif re.match(r'^github\(all\)\s.+\r$', inc):
                    insert = inc[inc.find('github(all)') + 12:len(inc) - 1].replace(' ', '+')
                    irc.send('PRIVMSG %s :%s: --> https://github.com/search?q=%s <--\r' % (chan, user, insert))

                elif re.match(r'^github\(user\)\s.+\r$', inc):
                    insert = inc[inc.find('github(user)') + 13:len(inc) - 1].replace(' ', '+')
                    headers = {
                        'Accept': 'application/vnd.github.v3.text-match+json'
                    }
                    req = requests.get('https://api.github.com/search/users?q=%s' % insert, headers=headers)
                    req_ = req.json()
                    try:
                        name = req_['items'][0]['login']
                        connection = req_['items'][0]['html_url']

                    except IndexError, errout:
                        irc.send('PRIVMSG %s :%s: tan 90°\r' % (chan, user))
                        print errout
                        continue

                    irc.send('PRIVMSG %s :%s: Top: [ %s ] - %s\r' % (chan, user, name, connection))

                elif re.match(r'^github\(\w+\)\s.+\r$', inc):
                    insert = inc.split(' ')[1]
                    lang = inc[inc.find('(') + 1:inc.find(')')]
                    headers = {
                        'Authentication': 'token TOKEN',
                        'Accept': 'application/vnd.github.mercy-preview+json'
                    }
                    req = requests.get('https://api.github.com/search/repositories?q=%s+language:%s' % (insert, lang), headers=headers)
                    req_ = req.json()
                    try:
                        name = req_['items'][0]['full_name']
                        connection = req_['items'][0]['html_url']
                        star = req_['items'][0]['stargazers_count']
                        fork = req_['items'][0]['forks_count']
                        description = req_['items'][0]['description']

                    except IndexError, errout:
                        irc.send('PRIVMSG %s :%s: tan 90°\r' % (chan, user))
                        print errout
                        continue

                    irc.send('PRIVMSG %s :%s: Top: [ %s ] - %s - Stars: %s Forks: %s\r' % (chan, user, name, connection, star, fork))
                    irc.send('PRIVMSG %s :Description: %s\r' % (chan, description))

                elif re.match(r'^github\s.+\r$', inc):
                    insert = inc[inc.find('github') + 7:len(inc) - 1].replace(' ', '+')
                    headers = {
                        'Authentication': 'token TOKEN',
                        'Accept': 'application/vnd.github.mercy-preview+json'
                    }
                    req = requests.get('https://api.github.com/search/repositories?q=%s' % insert, headers=headers)
                    req_ = req.json()
                    try:
                        name = req_['items'][0]['full_name']
                        connection = req_['items'][0]['html_url']
                        star = req_['items'][0]['stargazers_count']
                        fork = req_['items'][0]['forks_count']
                        description = req_['items'][0]['description']

                    except IndexError, errout:
                        irc.send('PRIVMSG %s :%s: tan 90°\r' % (chan, user))
                        print errout
                        continue

                    irc.send('PRIVMSG %s :%s: Top: [ %s ] - %s - Stars: %s Forks: %s\r' % (chan, user, name, connection, star, fork))
                    irc.send('PRIVMSG %s :Description: %s\r' % (chan, description))

                elif re.match(r'^weather\s\w+\r$', inc):
                    insert = inc[inc.find('weather') + 8:len(inc) - 1]
                    req = requests.get('http://api.openweathermap.org/data/2.5/forecast?q=%s&APPID=b1c8d567252dcea6f7b7bce3940e8126' % insert)
                    req_ = req.json()
                    try:
                        country = req_['city']['country']
                        city = req_['city']['name']
                        weather = req_['list'][0]['weather'][0]['description']
                        temp = int(req_['list'][0]['main']['temp']) - 273.15
                        wind_speed = req_['list'][0]['wind']['speed']

                    except Exception, errout:
                        irc.send('PRIVMSG %s :%s: tan 90°\r' % (chan, user))
                        print errout
                        continue

                    irc.send('PRIVMSG %s :%s: [ %s - %s ] Weather: %s, Current Temperature: %d°C, Wind Speed: %s.\r' % (chan, user, country, city, weather, temp, wind_speed))

                elif re.match(r'^tell\s#.+\s.+\r$', inc):
                    regex_split = re.split('\s', inc)
                    insert = inc[inc.find('#') + len(regex_split[1]) + 1:len(inc)]
                    irc.send('PRIVMSG %s :%s from %s told: %s\r' % (regex_split[1], user, chan, insert))
                    data = irc.recv(4096)
                    errcode = re.split('\s', data)[1]
                    print data
                    if errcode == '401':
                        irc.send('PRIVMSG %s :%s: No such nick or channel.\r' % (chan, user))

                    elif errcode == '404':
                        irc.send('PRIVMSG %s :%s: Only available for these channel: #%s, #%s, #%s\r' % (chan, user, base.CHAN[0], base.CHAN[1], base.CHAN[2]))

                    else:
                        irc.send('PRIVMSG %s :%s: Successfully sent!\r' % (chan, user))

                elif re.match(r'^sh\s.+\r$', inc):
                    data = irc.recv(4096)
                    print data
                    inc_ = data[data.find('::') + 2:len(data) - 1]
                    if re.match('^ps\s%s\r$' % base.ADMIN_PASSWD, inc_):
                        output = os.popen(inc[inc.find('sh') + 3:len(inc) - 1]).read().split('\n')
                        for i in xrange(len(output) - 1):
                            irc.send('PRIVMSG %s :%s\r' % (chan, output[i].replace('\t', '    ')))

                elif re.match(r'^exit\r$', inc):
                    data = irc.recv(4096)
                    print data
                    inc_ = data[data.find('::') + 2:len(data) - 1]
                    if re.match('^ps\s%s\r$' % base.ADMIN_PASSWD, inc_):
                        irc.send('QUIT :Going to leave.\r')
                        exit(0)

if __name__ == '__main__':
    main()
