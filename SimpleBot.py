# Import area
import socket, time, ssl, os, re

# Informations
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
        inc = str(data[data.find('::') + 2:len(data) - 1])
        print inc
        if re.match(r'^test\r$', inc):
            irc.send('PRIVMSG #%s :Success!\r' % CHAN)

        elif re.match(r'^help\r$', inc):
            irc.send('PRIVMSG #%s :%s: See the private chat.\r' % (CHAN, user))
            irc.send('PRIVMSG %s :The command of %s starts with \":\".\r' % (user, NICK))
            irc.send('PRIVMSG %s :----------Help of %s----------\r' % (user, NICK))
            irc.send('PRIVMSG %s :[version]Show the version of %s\r.' % (user, NICK))
            irc.send('PRIVMSG %s :[time]Show the time. Format: :time (tz:[Number](Default: GMT+8))(uts(Show Unix Timestamp)).\r\n' % user)
            irc.send('PRIVMSG %s :[fortune]Tell a fortune.\r' % (user))

        elif re.match(r'^version\r$', inc):
            irc.send('PRIVMSG #%s :%s: 3 - Alpha\r' % (CHAN, user))

        elif re.match(r'^fortune\r$', inc):
            output = os.popen('fortune').read().split('\n')
            for i in xrange(len(output)):
                irc.send('PRIVMSG #%s :%s\r' % (CHAN, output[i].replace('\t', '    ')))

        elif re.match(r'^time\r$', inc):
            os.environ['TZ'] = 'Asia/Shanghai'
            time.tzset()
            irc.send('PRIVMSG #%s :%s: Time: %s (CST/GMT+8)\r' % (CHAN, user, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))

        elif re.match(r'^time\stz:\d{1,3}\r$', inc):
            if int(inc[inc.find('tz:') + 3:len(inc) - 1]) <= 14 and int(inc[inc.find('tz:') + 3:len(inc) - 1]) >= -12:
                irc.send('PRIVMSG #%s :%s: Time: %s (CST/GMT+%s)\r' % (CHAN, user, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 8 * 3600 + int('%s' % inc[inc.find('tz:') + 3:len(inc) - 1]) * 3600)), int(inc[inc.find('tz:') + 3:len(inc) - 1])))

            else :
                irc.send('PRIVMSG #%s :%s: Argument must be lower than 14 and higher than -12\r' % (CHAN, user))

        elif re.match(r'^time\suts\r$', inc):
            irc.send('PRIVMSG #%s :%s: Unix Timestamp: %s\r' % (CHAN, user, time.time()))

        else :
            irc.send('PRIVMSG #%s :I don\'t know what you mean, %s.\r' % (CHAN, user))
