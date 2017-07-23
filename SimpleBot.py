# Import area
import socket
import ssl
import time
import os
import re

# Global Information
NETWORK = 'irc.freenode.net'
NICK = 'SimpleBot'
CHAN = 'linuxba'
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
irc.send('JOIN #%s\r' % CHAN)

# Functions
while True:
    data = irc.recv(4096)
    print data
    user = data[data.find(':') + 1:data.find('!')]

    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r')

    if data.find('::') != -1:
        inc = data[data.find('::') + 2:len(data) - 1]
        if re.match(r'^test\r$', inc):
            irc.send('PRIVMSG #%s :Success!\r' % CHAN)

        elif re.match(r'^help\r$', inc):
            irc.send('PRIVMSG #%s :%s: See the private chat.\r' % (CHAN, user))
            irc.send('PRIVMSG %s :The command of %s starts with \":\".\r' % (user, NICK))
            irc.send('PRIVMSG %s :----------Help of %s----------\r' % (user, NICK))
            irc.send('PRIVMSG %s :[version]Show the version of %s.\r' % (user, NICK))
            irc.send('PRIVMSG %s :[time]Show the time. Format: :time (tz:[Number](Default: GMT+8))(uts(Show Unix Timestamp)).\r' % user)
            irc.send('PRIVMSG %s :[fortune]Tell a fortune.\r' % user)
            irc.send('PRIVMSG %s :[echo ...]Print the message you told to %s.\r' % (user, NICK))
            irc.send('PRIVMSG %s :[x add/sub/mtp/div y]Basic calculate + - * /.\r' % user)

        elif re.match(r'^version\r$', inc):
            irc.send('PRIVMSG #%s :%s: 3 - Alpha\r' % (CHAN, user))

        elif re.match(r'^fortune\r$', inc):
            output = os.popen('fortune').read().split('\n')
            for i in xrange(len(output) - 1):
                irc.send('PRIVMSG #%s :%s\r' % (CHAN, output[i].replace('\t', '    ')))

        elif re.match(r'^echo\s\w*\r$', inc):
            irc.send('PRIVMSG #%s :%s\r' % (CHAN, inc[inc.find('echo') + 5:len(inc) - 1]))

        # Time

        elif re.match(r'^time\r$', inc):
            os.environ['TZ'] = 'Asia/Shanghai'
            time.tzset()
            irc.send('PRIVMSG #%s :%s: Time: %s (CST/GMT+8)\r' % (CHAN, user, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))

        elif re.match(r'^time\stz:\d{1,3}\r$', inc):
            if -12 <= int(inc[inc.find('tz:') + 3:len(inc) - 1]) <= 14:
                irc.send('PRIVMSG #%s :%s: Time: %s (CST/GMT+%s)\r' % (CHAN, user, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 3600 + int('%s' % inc[inc.find('tz:') + 3:len(inc) - 1]) * 3600)), int(inc[inc.find('tz:') + 3:len(inc) - 1])))

            else:
                irc.send('PRIVMSG #%s :%s: Argument must be lower than 14 and higher than -12\r' % (CHAN, user))

        elif re.match(r'^time\suts\r$', inc):
            irc.send('PRIVMSG #%s :%s: Unix Timestamp: %s\r' % (CHAN, user, time.time()))

        # Calculate

        elif re.match(r'^\d\sadd\s\d\r$', inc):
            irc.send('PRIVMSG #%s :%s: %s\r' % (CHAN, user, float(inc[:inc.find('add')]) + float(inc[inc.find('add') + 4:len(inc) - 1])))

        elif re.match(r'^\d\ssub\s\d\r$', inc):
            irc.send('PRIVMSG #%s :%s: %s\r' % (CHAN, user, float(inc[:inc.find('sub')]) - float(inc[inc.find('sub') + 4:len(inc) - 1])))

        elif re.match(r'^\d\smtp\s\d\r$', inc):
            irc.send('PRIVMSG #%s :%s: %s\r' % (CHAN, user, float(inc[:inc.find('mtp')]) * float(inc[inc.find('mtp') + 4:len(inc) - 1])))

        elif re.match(r'^\d\sdiv\s\d\r$', inc):
            irc.send('PRIVMSG #%s :%s: %s\r' % (CHAN, user, float(inc[:inc.find('div')]) / float(inc[inc.find('div') + 4:len(inc) - 1])))

        elif user == 'OriginCode':
            if re.match(r'^sh\s.*\r$', inc):
                output = os.popen(inc[inc.find('sh') + 3:len(inc) - 1]).read().split('\n')
                for i in xrange(len(output) - 1):
                    irc.send('PRIVMSG #%s :%s\r' % (CHAN, output[i].replace('\t', '    ')))
