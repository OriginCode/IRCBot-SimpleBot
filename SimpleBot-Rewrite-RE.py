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

# Module RE Matches


# Functions
while True:
    data = irc.recv(4096)
    print data
