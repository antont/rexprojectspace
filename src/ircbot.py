#Irc bot example from http://oreilly.com/pub/h/1968
#Original version contains code to login to a server and replying to ping
#(without threading)

#modified by Markus Santaniemi

import sys
import socket
import string
from threading import Thread

HOST="chat.freenode.net"
PORT=6667
NICK="ProjectSpaceBot4"
IDENT="projectspacebot4"
REALNAME="Project space-bot"
IRCROOM = "rpstestroom"

class IrcBot(Thread):
    
    def __init__(self,vOnMessage):
        """ vOnMessage is a callback function that will be called
            when irc bot receives a public message from a irc channel"""
        self.bIsLoggedIn = False
        self.readbuffer=""
        self.OnMessage = vOnMessage
        self.s=socket.socket( )
        self.s.connect((HOST, PORT))
        self.s.send("NICK %s\r\n" % NICK)
        self.s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
        super(IrcBot,self).__init__()
    
    def run(self):
            while 1:
                self.readbuffer=self.readbuffer+self.s.recv(2048)
                temp=string.split(self.readbuffer, "\n")
                self.readbuffer=temp.pop( )
                for line in temp:
                    line=string.rstrip(line)
                    line=string.split(line)
                    #print line
                    if(line[0]=="PING"):
                        print "pinged"
                        self.s.send("PONG %s\r\n" % line[1])
                    elif line[1] == "004":
                        print "connected"
                        self.bIsLoggedIn = True
                        #now join
                        self.s.send("JOIN #%s\r\n"%(IRCROOM))
                    elif line[1] == "PRIVMSG" and line[2] == "#"+IRCROOM:
                        print "message to room:%s"%(line[3])
                        self.OnMessage(line)



            