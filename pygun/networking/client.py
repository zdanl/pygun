#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This generates a blob of 64 true random bytes, and transfers them to a remote
# node. It awaits the return of the bytes in reverse order and measures the
# time.

# Author: Dan Zulla <dan@mescalin.co>

# (c) 2022 Mescalin Semiconductor Ltd.
# (c) 2022 All rights reserved.

import socket, sys, os

class Client:

    entropy_payload = []
    ready_signal = b":3"

    def read_sixtyfour_random_bytes(self):
        with open("/dev/random", 'rb') as f:
            self.entropy_payload = f.read(64)

    def create_socket(self):
        print("# Creating socket")
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print("# Failed to create socket.")
            sys.exit(1)

    def get_remote_ip(self, host="0.0.0.0"):
        try:
            remote_ip = socket.gethostbyname(host)
        except socket.error:
            print("# Socket gethostbyname failed.")
            sys.exit(1)

        return remote_ip

    def connect(self, remote_ip, port):
        try:
            self.s.connect((remote_ip, port))
        except socket.error:
            print("# Couldn't connect to remote hostt.")
            sys.exit(1)

    def await_ready_signal(self, signal=b":3"):
        try:
            reply = self.s.recv(8)
        except socket.timeout:
            print("# Socket timeout.")
            sys.exit(1)
        except socket.error:
            print("# Socket error.")
            sys.exit(1)

        print("Ready signal:")
        print(reply)
        print("-"*80)

        if reply == self.ready_signal or reply == signal:
            print("Server is ready for data.")
            return 0
        else:
            print("Server sent some garbage.")
            return 1

    def send_entropy_payload(self):
        try:
            self.s.send(self.entropy_payload)
        except socket.error:
            print("# Couldn't send entropy payload, socket error")

    def recv_entropy_return(self):
        try:
            inverse_payload = self.s.recv(64)
        except socket.timeout:
            print("# Receiving socket timed out")
        except socket.error:
            print("# Socket error while receiving payload.")

        print("Inverse Payload:")
        print(inverse_payload)
        print("-"*80)

        if inverse_payload == bytes(reversed(self.entropy_payload)):
            print("Mission Assurance")
        else:
            print("Server sent %d bytes but they aren't correct." %(len(inverse_payload)))
