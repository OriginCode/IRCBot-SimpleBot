# Import area
import socket
import ssl
import time
import os
import re

# Global Information
NETWORK = 'irc.freenode.net'
NICK = 'SimpleBot'
CHAN = ['archlinux-cn-offtopic', 'linuxba', 'liuyanbot']
PORT = 6697
PASSWD = 'Aa32504863'

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Main functions

# Connect to the server
socket.connect((NETWORK, PORT))
irc = ssl.wrap_socket(socket)

# Sign into the server
irc.send('PASS %s\r' % PASSWD)
irc.send('NICK %s\r' % NICK)
irc.send('USER %s %s %s :SimpleBot\r' % (NICK, NICK, NICK))
irc.send('JOIN #%s,#%s,#%s\r' % (CHAN[0], CHAN[1], CHAN[2]))

# Calculate Author:niunai
l1_pattern = re.compile(r'\([^()]*\)')
l2_pattern = re.compile(r'(-?\d+)(\.\d+)?[/*](-?\d+)(\.\d+)?')
l3_pattern = re.compile(r'(-?\d+)(\.\d+)?[-+](-?\d+)(\.\d+)?')
mul_sub_pattern = re.compile(r'(-?\d+)(\.\d+)?\*-(-?\d+)(\.\d+)?')
div_sub_pattern = re.compile(r'(-?\d+)(\.\d+)?/-(-?\d+)(\.\d+)?')


def min_cal(string):
    if string.count('+') == 1:
        return str(float(string[:string.find('+')]) + float(string[string.find('+')+1:]))
    elif string[1:].count('-') == 1:
        return str(float(string[:string.find('-', 1)]) - float(string[string.find('-', 1)+1:]))
    elif string.count('*') == 1:
        return str(float(string[:string.find('*')]) * float(string[string.find('*')+1:]))
    elif string.count('/') == 1:
        return str(float(string[:string.find('/')]) / float(string[string.find('/')+1:]))


def nomal_numerator(string):
    if string.count('+') + string.count('*') + string.count('/') == 0 and string[1:].find('-') < 0:
        return string

    elif string.count('+-') + string.count('--') + string.count('*-') + string.count('/-') != 0:
        string = string.replace('+-', '-')
        string = string.replace('--', '+')
        if string.count('*-') != 0:
            string = string.replace(mul_sub_pattern.search(string).group(),'-' + mul_sub_pattern.search(string).group().replace('*-', '*'))

        if string.count('/-') != 0:
            string = string.replace(div_sub_pattern.search(string).group(),'-' + div_sub_pattern.search(string).group().replace('/-', '/'))

        return nomal_numerator(string)

    elif string.count('*') + string.count('/') != 0:
        from_str = l2_pattern.search(string).group()
        string = string.replace(from_str, min_cal(from_str))
        return nomal_numerator(string)

    elif string.count('+') != 0 or string.count('-') != 0:
        from_str = l3_pattern.search(string).group()
        string = string.replace(from_str, min_cal(from_str))
        return nomal_numerator(string)


def l1_analysis(string):
    if string.find('(') == -1:
        return nomal_numerator(string)

    else:
        from_str = l1_pattern.search(string).group()
        string = string.replace(from_str, nomal_numerator(from_str[1:-1]))
        return l1_analysis(string)

# Functions
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
            inc = re.split(r'\s?::', data)[1]
            if re.match(r'^test\r$', inc):
                irc.send('PRIVMSG %s :Success!\r' % chan)

            elif re.match(r'^help\r$', inc):
                irc.send('PRIVMSG %s :%s: See the private chat.\r' % (chan, user))
                irc.send('PRIVMSG %s :The command of %s starts with \":\".\r' % (user, NICK))
                irc.send('PRIVMSG %s :----------Help of %s----------\r' % (user, NICK))
                irc.send('PRIVMSG %s :[version]Show the version of %s.\r' % (user, NICK))
                irc.send('PRIVMSG %s :[time]Show the time. Format: :time (tz:[Number](Default: GMT+8))(uts(Show Unix Timestamp)).\r' % user)
                irc.send('PRIVMSG %s :[fortune]Tell a fortune.\r' % user)
                irc.send('PRIVMSG %s :[echo ...]Print the message you told to %s.\r' % (user, NICK))
                irc.send('PRIVMSG %s :[calc ...]Calculator.\r' % user)

            elif re.match(r'^version\r$', inc):
                irc.send('PRIVMSG %s :%s: 3.1\r' % (chan, user))

            elif re.match(r'^fortune\r$', inc):
                output = os.popen('fortune').read().split('\n')
                for i in xrange(len(output) - 1):
                    irc.send('PRIVMSG %s :%s\r' % (chan, output[i].replace('\t', '    ')))

            elif re.match(r'^echo\s\w*\r$', inc):
                irc.send('PRIVMSG %s :%s\r' % (chan, inc[inc.find('echo') + 5:len(inc) - 1]))

            # Time

            elif re.match(r'^time\r$', inc):
                os.environ['TZ'] = 'Asia/Shanghai'
                time.tzset()
                irc.send('PRIVMSG %s :%s: Time: %s (CST/GMT+8)\r' % (chan, user, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))

            elif re.match(r'^time\stz:\d{1,3}\r$', inc):
                if -12 <= int(inc[inc.find('tz:') + 3:len(inc) - 1]) <= 14:
                    irc.send('PRIVMSG %s :%s: Time: %s (CST/GMT+%s)\r' % (chan, user, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 3600 + int('%s' % inc[inc.find('tz:') + 3:len(inc) - 1]) * 3600)), int(inc[inc.find('tz:') + 3:len(inc) - 1])))

                else:
                    irc.send('PRIVMSG %s :%s: Argument must be lower than 14 and higher than -12\r' % (chan, user))

            elif re.match(r'^time\suts\r$', inc):
                irc.send('PRIVMSG %s :%s: Unix Timestamp: %s\r' % (chan, user, time.time()))

            # Calculate

            elif re.match(r'^calc\s.*', inc):
                s = inc[inc.find('cal') + 5:len(inc) - 1]
                s = s.replace(' ', '')
                try:
                    l1_analysis(s)

                except AttributeError, errout:
                    irc.send('PRIVMSG %s :%s: %s\r' % (chan, user, errout))
                    continue

                irc.send('PRIVMSG %s :%s: %s\r' % (chan, user, l1_analysis(s)))

            elif user == 'OriginCode':
                if re.match(r'^sh\s.*\r$', inc):
                    output = os.popen(inc[inc.find('sh') + 3:len(inc) - 1]).read().split('\n')
                    for i in xrange(len(output) - 1):
                        irc.send('PRIVMSG %s :%s\r' % (chan, output[i].replace('\t', '    ')))
