# Socket guidance from:
# https://medium.com/hackernoon/socket-programming-in-python-client-server-and-peer-examples-a25c9782b584
# https://docs.python.org/3/library/socket.html
# https://stackoverflow.com/questions/5308080/python-socket-accept-nonblocking

import select
import socket
import pickle

import util

def connectToServer(ip = "0.0.0.0", port = 52021):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock

def sendInfo(info: dict, socket: socket.socket):
    print(info)

    msg = pickle.dumps(info)
    msgLength = len(msg)
    print(msgLength)

    msgLength = msgLength.to_bytes(2, byteorder="big", signed=False)
    socket.sendall(msgLength)
    socket.sendall(msg)

def recvMsg(socket: socket.socket, buffer: bytearray):
    headerLen = 2
    received = socket.recv(4096)
    if not received:
        return "EOF"

    buffer.extend(received)
    msgLength = int.from_bytes(buffer[0:headerLen], byteorder="big", signed=False)
    if len(buffer) >= headerLen+msgLength:
        data = pickle.loads(buffer[headerLen:headerLen+msgLength])
        buffer = buffer[headerLen+msgLength+1:]
        return data



def runServer():
    addr = ("", 52021)
    if socket.has_dualstack_ipv6():
        serv = socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True)
    else:
        serv = socket.create_server(addr)

    serv.listen(5)
    print(f"Server started on port {addr[1]}")

    maybeReadables = [serv]
    addresses = ["0.0.0.0"]
    buffers = [bytearray()]
    while True:
        readables, writables, errs = select.select(maybeReadables, [], [], 60)
        for readable in readables:
            if readable is serv:
                client, clientAddr = serv.accept()
                maybeReadables.append(client)
                addresses.append(clientAddr)
                buffers.append(bytearray())
                print(f"{clientAddr[0]} connected.")
            else:
                result = recvMsg(readable, buffers[maybeReadables.index(readable)])
                # Disconnect on EOF
                if result == "EOF":
                    readable.close()
                    i = maybeReadables.index(readable)
                    print(f"{addresses[i][0]} disconnected.")
                    addresses.pop(i)
                    maybeReadables.pop(i)
                    buffers.pop(i)
                else:



if __name__ == '__main__':
    runServer()