from socket import *
from datetime import datetime
import os

from rdt3 import RDT3

dict_info = {}
dict_ids = {}

server = RDT3(isServer=True, host = 'localhost', port= 8001)
BUFF_SIZE = 1024

def broadcast(message, name, socket, new):
  msg = None
  address = None
  if new:
    msg = f'{name} entrou na sala'
  else:
    now = datetime.now()
    msg = f'{now.hour :02}:{now.minute:02}:{now.second:02} {name}: {message}'

  print(msg)

  for key  in dict_info.keys():
    address = (key.split(':')[0], int(key.split(':')[1]))
    socket.sendDataServer(dict_ids,msg.encode('utf-8'), address)

def listClients(socket, address):
  socket.sendDataServer(dict_ids,'Os usuários atívos são:'.encode('utf-8'), address)
  for key, name in dict_info.items():
    socket.sendDataServer(dict_ids,name.encode('utf-8'), address)

while True:
  msg, address, new_client, name = server.receiveDataServer(dict_ids, dict_info)
  key = address[0] + ':' + str(address[1])
  if msg.decode() == 'list':
    broadcast(msg.decode(), name, server, False)
    listClients(server, address)
  elif new_client:
    broadcast('', name, server, True)
  else:
    broadcast(msg.decode(), name, server, False)
