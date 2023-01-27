#  coding: utf-8 
import socketserver
import os

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
        # #print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))
        self.status = "200 OK"
        self.contentType = "text/html"
        self.sock = self.request

        reqdatas = self.data.decode("utf-8").split()
        reqtype = reqdatas[0]
        reqpath = os.path.abspath("www") + reqdatas[1]

        #If the request method is other than GET, return "405 Method Not Allowed"
        if reqtype == "GET":
            self.file_handler(reqpath)
        else:
            self.status_handler(405)

    def status_handler(self, code, reqpath=None):
        if code == 301:
            self.status = "301 Moved Permanently"
            reqpath += "/index.html"
            if os.path.exists(reqpath):
                self.file_handler(reqpath)

        if code == 404:
            self.status = "404 Not Found"
            self.header_handler()

        if code == 405:
            self.status = "405 Method Not Allowed"
            self.header_handler()

    def file_handler(self, reqpath):
        if os.path.exists(reqpath):
            if os.path.isdir(reqpath):
                if reqpath.endswith("/"):
                    reqpath += "index.html"

        if reqpath.endswith(".css"):
            self.contentType = "text/css"
        elif reqpath.endswith(".html"):
            self.contentType = "text/html"

        self.content_handler(reqpath)
    
    def header_handler(self):
        self.sock.sendall(str.encode(f"HTTP/1.1 {self.status}\r\n","utf-8"))
        self.sock.sendall(str.encode(f"Content-Type: {self.contentType}\r\n", "utf-8"))
        self.sock.sendall(str.encode("Connection: close\r\n", "utf-8"))
        # self.sock.sendall(str.encode("\r\n", 'utf-8'))

    def content_handler(self, reqpath):
        try:
            f = open(reqpath, 'r')
        except FileNotFoundError:
            self.status_handler(404)
        except IsADirectoryError:
            self.status_handler(301, reqpath)
        else:
            l = f.read(1024)
            while (l):
                self.sock.sendall(str.encode(f"HTTP/1.1 {self.status}\r\n","utf-8"))
                self.sock.sendall(str.encode(f"Location: {reqpath}"))
                self.sock.sendall(str.encode(f"Content-Type: {self.contentType}\r\n", "utf-8"))
                # self.sock.sendall(str.encode(f"Content-Length: 0\r\n", "utf-8"))
                self.sock.sendall(str.encode("Connection: close\r\n", "utf-8"))
                self.sock.sendall(str.encode('\r\n'))
                self.sock.sendall(str.encode(l, 'utf-8'))
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
