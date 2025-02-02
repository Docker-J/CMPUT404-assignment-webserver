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

#Updated by Junesung Lee JLJL
class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))
        self.status = "200 OK"
        self.sock = self.request

        reqdatas = self.data.decode("utf-8").split()

        if len(reqdatas):
            reqtype = reqdatas[0]
            reqpath = "www" + os.path.abspath(reqdatas[1])
            if reqdatas[1].endswith("/"):
                reqpath += "/"

            #If the request method is other than GET, return "405 Method Not Allowed"
            if reqtype == "GET":
                self.file_handler(reqpath)
            else:
                self.status_handler(405)


    def status_handler(self, code, reqpath=None):
        if code == 301:
            self.status = "301 Moved Permanently"
        if code == 404:
            self.status = "404 Not Found"
        if code == 405:
            self.status = "405 Method Not Allowed"
        
        self.error_handler(reqpath)


    def file_handler(self, reqpath):
        if os.path.exists(reqpath):
            if os.path.isdir(reqpath):
                if reqpath.endswith("/"):
                    reqpath += "index.html"
            self.content_handler(reqpath)
        else:
            self.status_handler(404)

                
    def error_handler(self, reqpath):
        self.sock.sendall(str.encode(f"HTTP/1.1 {self.status}\r\n","utf-8"))
        if reqpath != None:
            location = reqpath.lstrip("www") + "/"
            self.sock.sendall(str.encode(f"Location: {location}\r\n"))
        self.sock.sendall(str.encode("Connection: close\r\n\r\n", "utf-8"))


    def content_handler(self, reqpath):
        contentType = ""
        if reqpath.endswith(".css"):
            contentType = "text/css"
        elif reqpath.endswith(".html"):
            contentType = "text/html"
        
        location = reqpath.lstrip("www")

        try:
            f = open(reqpath, 'r')
        except FileNotFoundError:
            self.status_handler(404)
        except IsADirectoryError:
            self.status_handler(301, reqpath)
        else:
            self.stauts = "200 OK"
            l = f.read(1024)
            while (l):
                self.sock.sendall(str.encode(f"HTTP/1.1 {self.status}\r\n","utf-8"))
                self.sock.sendall(str.encode(f"Location: {location}\r\n"))
                self.sock.sendall(str.encode(f"Content-Type: {contentType}\r\n", "utf-8"))
                self.sock.sendall(str.encode("Connection: close\r\n\r\n", "utf-8"))
                self.sock.sendall(str.encode(l, "utf-8"))
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