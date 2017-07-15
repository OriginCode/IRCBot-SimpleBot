# Import area
import socket, time, ssl, os, types

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
irc.send('PASS %s\r\n' % PASSWD)
irc.send('NICK %s\r\n' % NICK)
irc.send('USER %s %s %s :SimpleBot\r\n' % (NICK, NICK, NICK))
irc.send('JOIN #%s\r\n' % CHAN)

# Functions
while True:
    data = irc.recv(4096)
    print data
    user = data[data.find(':') + 1:data.find('!')]

    # Auto anti-ping
    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')

    if data.find('TideBot') != -1 or data.find('labots') != -1 or data.find('anotitlebot') != -1 or data.find('MoBot') != -1 or data.find('miaowbot') != -1 or data.find('varia') != -1:
        None

    elif data.find('#%s ::' % CHAN) != -1:
        # Help manual
        if data.find('help') != -1:
            irc.send('PRIVMSG #%s :%s: See the private chat.\r\n' % (CHAN, user))
            irc.send('PRIVMSG %s :The command of %s starts with \":\"\r\n' % (user, NICK))
            irc.send('PRIVMSG %s :----------Help of %s----------\r\n' % (user, NICK))
            irc.send('PRIVMSG %s :[version]Show the version of %s\r\n' % (user, NICK))
            irc.send('PRIVMSG %s :[time]Show the time. Format: :time (set:[Number](Default: GMT+8))(ts(Show Unix Timestamp))\r\n' % user)
            irc.send('PRIVMSG %s :[me ...]Just like /me ...\r\n' % user)
            irc.send('PRIVMSG %s :[hug ...]Have a hug!\r\n' % user)
            irc.send('PRIVMSG %s :[pia ...]...Pia!\r\n' % user)

        # Commands
        elif data.find('version') != -1:
            irc.send('PRIVMSG #%s :%s: 2.4\r\n' % (CHAN, user))

        elif data.find('time') != -1:
            if data.find('ts') != -1:
                irc.send('PRIVMSG #%s :%s: Timestamp: %s\r\n' % (CHAN, user, time.time()))

            elif data.find('set:') == -1:
                os.environ['TZ'] = 'Asia/Shanghai'
                time.tzset()
                irc.send('PRIVMSG #%s :%s: Time: %s (CST/GMT+8)\r\n' % (CHAN, user, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))

            else:
                try:
                    int(data[data.find('set:') + 4:len(data)])

                except ValueError, erroutput:
                    irc.send('PRIVMSG #%s :%s: %s\r\n' % (CHAN, user, erroutput))
                    continue

                irc.send('PRIVMSG #%s :%s: Time: %s (CST/GMT+%s)\r\n' % (CHAN, user, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time() - 8 * 3600 + int('%s' % data[data.find('set:') + 4:len(data)]) * 3600)), int(data[data.find('set:') + 4:len(data)])))

        elif data.find('me ') != -1:
            irc.send('PRIVMSG #%s :ACTION %s\r\n' % (CHAN, data[data.find('me') + 3:len(data) - 1]))

        elif data.find('hug ') != -1:
            irc.send('PRIVMSG #%s :%s had a hug with %s\r\n' % (CHAN, user, data[data.find('hug') + 4:len(data) - 1]))

        elif data.find('pia ') != -1:
            irc.send('PRIVMSG #%s :(╬￣皿￣)凸 Pia! %s\r\n' % (CHAN, data[data.find('pia') + 4:len(data) - 1]))

        elif data.find('test') != -1:
            irc.send('PRIVMSG #%s :%s: Tested Successfully!\r\n' % (CHAN, user))

        elif data.find('fortune') != -1:
            output = os.popen('fortune').read().split('\n')
            for i in xrange(len(output)):
                irc.send('PRIVMSG #%s :%s\r' % (CHAN, output[i].replace('\t', '    ')))

        # Exit (Default: Close)
        # elif data.find('quit') != -1:
            # irc.send('QUIT\r\n')
            # exit()
