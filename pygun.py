#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# __________           ________                 
# \______   \ ___.__. /  _____/  __ __   ____   
#  |     ___/<   |  |/   \  ___ |  |  \ /    \  
#  |    |     \___  |\    \_\  \|  |  /|   |  \ 
#  |____|     / ____| \______  /|____/ |___|  / 
#  v0.1       \/Twi @dzethoxy\/Github @zdanl\/


# This is a network and compute benchmarking tool.
# 
# It generates a blob of 64 true random bytes, and transfers them to a remote
# node. It awaits the return of the bytes in reverse order and measures the
# time. It then compresses and encrypts the bytes.
#

# (c) 2022 Mescalin Semiconductor Ltd.
# (c) 2022 All rights reserved.

# Author: Dan Zulla <dan@mescalin.co>

import socket, time, sys, os
import pygun.types

from pygun.networking.client import Client
from pygun.tricks import _ov

PyGun_Runmode = pygun.types.Unknown

PyGun_Config = _ov({
    "SERVER_PORT": 4444,
    "SERVER_HOST": "0.0.0.0",
    "CLIENT_PORT": 4444,
    "CLIENT_HOST": "127.0.0.1",
    "HANDSHAKE_BYTES": b":3"
})

#
# pygun has 2 runmodes, client & server.
#
def main():
    if PyGun_Runmode == pygun.types.Server:
        print("Running PyGun in Server mode.")
        server_main()
    elif PyGun_Runmode == pygun.types.Client:
        print("Running PyGun in Client mode.")
        client_main()
    else:
        print("Unknown runmode.")
        sys.exit(1)

#
# This runs the pygun TCP server.
#
def server_main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((PyGun_Config.SERVER_HOST, PyGun_Config.SERVER_PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connection by {addr}, sending greeting")
            conn.send(PyGun_Config.HANDSHAKE_BYTES)
            print("Handshake sent, awaiting payload")
            data = conn.recv(64)
            conn.send(bytes(reversed(data)))
            print("Exiting.")

#
# This runs the pygun TCP client.
#
def client_main():
    client = Client()
    
    client.read_sixtyfour_random_bytes()

    print("Generated 64 bytes of entropy payload.")
    print(client.entropy_payload)
    print("-"*80)

    s = client.create_socket()
    remote_ip = client.get_remote_ip(PyGun_Config.CLIENT_HOST)
    client.connect(remote_ip, PyGun_Config.CLIENT_PORT)
    status = client.await_ready_signal(signal=PyGun_Config.HANDSHAKE_BYTES)

    if status == 0:
        start_time = time.time()
        client.send_entropy_payload()
        print("# Handshake successful.")
        client.recv_entropy_return()
        print("# Payload Inverse successful.")
        end_time = time.time()
        print("# It took %f seconds." %(end_time-start_time))
    else:
        print("# Handshake failed.")
        sys.exit(1)

if __name__ == "__main__":
    os.system("clear")
    
    print("""
     __________           ________
     \______   \ ___.__. /  _____/  __ __   ____
      |     ___/<   |  |/   \  ___ |  |  \ /    \\
      |    |     \___  |\    \_\  \|  |  /|   |  \\
      |____|     / ____| \______  /|____/ |___|  /
      v0.1       \/Twi @dzethoxy\/Github @zdanl\/
    """)

    if len(sys.argv) < 2:
        PyGun_Runmode = pygun.types.Server
    else:
        PyGun_Runmode = pygun.types.Client
        host = sys.argv[1]
        port = PyGun_Config.CLIENT_PORT
        if len(sys.argv) == 3:
            port = sys.argv[2]

    main()
