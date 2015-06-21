#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    * MurmurQuery
    *
    * Based on GT MURMUR PLUGIN, which allows us to query a Murmur server
    * without having to install PHP ICE on the web server.
    * http://www.gametracker.com/downloads/gtmurmurplugin.php
    *
    * The response is constructed using Channel Viewer Protocl.
    * http://mumble.sourceforge.net/Channel_Viewer_Protocol
    *
    * Inspiration taken from a PHP class with the same name.
    * https://github.com/edmundask/MurmurQuery
"""

import socket
import time
import json

class MurmurQuery(object):
    """ * MurmurQuery
        *
        * Attributes:
        * host: Hostname to the Murmur server
        * port: Port to the Murmur server
        * timeout: Connection timeout limit
        * _socket: Connection socket
        * online: Online status of Murmur server
        * raw: Raw captured data
        * channels: Array containing channels
        * users: Array containing users online
        *
        * Constants:
        * Q_JSON: Message sent to Murmur server
    """

    # pylint: disable=too-many-instance-attributes
    # The amount of attributes is just fine.
    # pylint: disable=bare-except

    Q_JSON = "\x6A\x73\x6F\x6E".encode('utf8')

    def __init__(self, host="", port=27800, timeout=1):
        """ Initialization """
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket = ""
        self.online = False
        self.response = ""
        self.raw = ""
        self.channels = []
        self.users = []

    def setup(self, host="", port=27800, timeout=1):
        """ Config """
        self.host = host
        self.port = port
        self.timeout = timeout

    def is_online(self):
        """ Return online status of Mumur server """
        return self.online

    def get_channels(self):
        """ Return channels """
        return self.channels

    def get_users(self):
        """ Return users """
        return self.users

    def get_status(self):
        """ Return JSON encoded captured data """
        return self.raw

    def connect(self):
        """ Establish a socket connection """
        try:
            self._socket = socket.create_connection((self.host, self.port),\
                                                    self.timeout)
        except socket.error:
            return False
        except socket.herror:
            return False
        return True

    def send_query(self):
        """ * Documentation """
        try:
            self._socket.sendall(self.Q_JSON)
        except socket.error:
            return False
        return True

    def catch_response(self, sock):
        """ * Returns JSON-encoded response """
        if not sock:
            return False
        sock.setblocking(0)
        data = ""
        received_data = []
        start_time = time.time()
        wait = False
        while 1:
            if received_data and time.time()-start_time > self.timeout:
                break
            elif time.time()-start_time > self.timeout:
                break
            try:
                data = sock.recv(8192)
                if data:
                    received_data.append(data.decode('utf8'))
                    start_time = time.time()
                else:
                    if not wait:
                        wait = True
                        time.sleep(0.1)
                    else:
                        break
            except:
                pass
        self.response = "".join(received_data)
        self.raw = self.response
        return self.raw

    def parse_channels(self, data):
        """ * Convert response to arrays filled with data """
        if "root" in data:
            if len(data["root"]["users"]) > 0:
                for user in data["root"]["users"]:
                    self.users.append(user)
            tmp = data["root"]["channels"]
            del data["root"]["channels"]
            del data["root"]["users"]
            self.parse_channels(tmp)
        else:
            if len(data) > 0:
                for channel in data:
                    if len(channel["users"]) > 0:
                        for user in channel["users"]:
                            self.users.append(user)
                    del channel["users"]
                    self.parse_channels(channel["channels"])
                    del channel["channels"]
                    self.channels.append(channel)

    def parse_response(self):
        """ * Documentation """
        if self._socket:
            self.catch_response(self._socket)
            data = json.loads(self.raw)
            self.parse_channels(data)

    def close(self):
        """ * Close socket """
        self._socket.close()
        self._socket = ""
        self.response = ""

    def query(self):
        """ * Query the server """
        if self.connect():
            self.send_query()
            self.parse_response()
            if self.response:
                self.online = True
            self.close()

