#####################################
#
#  Rough python script to redirect stdin/stdout 
#  of an application to a socket
#
#####################################

import socket
import sys

from subprocess import Popen, PIPE
from time import sleep

from threading import Thread
from Queue import Queue, Empty

class NonBlockingStreamReader:

    def __init__(self, stream):
        '''
        stream: the stream to read from.
        Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = Queue()
        
        def _populateQueue(stream, queue):
            '''
            Collect bytes from 'stream' and put them in 'queue'.
            '''

            while True:
                ret_byte = stream.read(1)
                if ret_byte:
                    queue.put(ret_byte)
                else:
                    raise UnexpectedEndOfStream

        self._t = Thread(target = _populateQueue, args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def readbyte(self, timeout = None):
        #Check if thread is dead
        if self._t.is_alive() == False:
            raise UnexpectedEndOfStream

        try:
            return self._q.get(block = timeout is not None,
            timeout = timeout)
        except Empty:
            return None

class UnexpectedEndOfStream(Exception): pass

def read_until( sock, a_char):
	ret_str = ''
	cur_char = None
	while cur_char != a_char:
		cur_char = sock.recv(1)
		ret_str += cur_char
		
	return ret_str

def run_program( sock, program_arr ):
	# run the shell as a subprocess:
	p = Popen(program_arr,
			stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = False)
	# wrap p.stdout with a NonBlockingStreamReader object:
	nbsr = NonBlockingStreamReader(p.stdout)	
	while True:
		
		try:
			data = read_until(sock, "\n")
			if len(data) > 0:
				#print "Read %d bytes:\n" % len(data)
				# issue command:
				p.stdin.write(data)
		except socket.timeout:
			pass
			
		# get the output
		output = nbsr.readbyte(0.01)
		# 0.1 secs to let the shell output the result
		if output != None:
			sock.send(output)
			#print "Sent %d bytes:\n" % len(output)
			

 
HOST = ''   
PORT = 1234 # Arbitrary non-privileged port
PROGRAM = "C:\chal\ConsoleApplication2.exe"
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
#Start listening on socket
s.listen(10)
print '[+] Listening for incoming connection to application.'
 
#wait to accept a connection - blocking call
conn, addr = s.accept()
conn.settimeout(0.01) 
print 'Connected with ' + addr[0] + ':' + str(addr[1])
run_program(conn, [PROGRAM] )
     
s.close()