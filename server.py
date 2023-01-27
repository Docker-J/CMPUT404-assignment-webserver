#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        self.request.sendall(bytearray("OK",'utf-8'))

        sock = self.request
        status = ""

        reqdatas = self.data.split()
        reqtype = reqdatas[0].decode()
        reqpath = reqdatas[1].decode()
        # contentType = reqdatas[1].rsplit('.',1)
        contentType = "text/html"
        # print(contentType)

        if reqtype != "GET":
            status = "405 Method Not Allowed"

        if reqpath[-1] == "/":
            reqpath = reqpath + "index.html"
        else:
            reqpath = reqpath + "/index.html"
            status = "301 Moved Permanently"

        filename = "www" + reqpath
        print(reqdatas)

        try:
            f = open(filename, 'r')
        except FileNotFoundError:
            status = "404 Not FOUND"
            sock.sendall(str.encode(f"HTTP/1.1 {status}\r\n","utf-8"))
            sock.sendall(str.encode(f"Content-Type: {contentType}\r\n", "utf-8"))
            sock.sendall(str.encode("Connection: close\r\n", "utf-8"))
            sock.sendall(str.encode("\r\n", 'utf-8'))
            f.close()
        else:
            l = f.read(1024)
            while (l):
                sock.sendall(str.encode(f"HTTP/1.1 {status}\r\n","utf-8"))
                sock.sendall(str.encode(f"Content-Type: {contentType}\r\n", "utf-8"))
                sock.sendall(str.encode('\r\n'))
                sock.sendall(str.encode(l, 'utf-8'))
                l = f.read(1024)
            f.close()


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
