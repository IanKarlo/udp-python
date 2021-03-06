from socket import *

BUFF_SIZE = 4096

class RDT3():
  def __init__(self, isServer=None, **kargs):
    self.id = 0
    self.socket = socket(AF_INET, SOCK_DGRAM)
    if isServer:
      self.socket.bind((kargs['host'], kargs['port']))
      print ('The server is ready to receive')

  def getChecksum(self, data):
    result = 0
    for index in range(0, len(data), 2):
      result += int.from_bytes(data[index: index+2], 'big')
    bytes_result = result.to_bytes(513, 'big')
    return_value = bytes_result[0] + int.from_bytes(bytes_result[1:513], 'big')
    return return_value.to_bytes(512, 'big')

  def isCorrupt(self, message):
    data = message[513:]
    rcv_checksum = message[1:513]
    return rcv_checksum != self.getChecksum(data)

  def isACK(self, message):
    try:
      ACK = message[513:]
      ack_id = message[0]

      if ack_id == self.id and ACK.decode() == "ACK":
        return True
      else:
        return False
    except:
      return False

  def isACKServer(self, message, id):
    try:
      ACK = message[513:]
      ack_id = message[0]

      if ack_id == id and ACK.decode() == "ACK":
        return True
      else:
        return False
    except:
      return False

  def seqValue(self, data):
    value = data[0]
    return value

  def sendData(self, data, receiverAddress):
    self.socket.settimeout(0.001)
    checksum = self.getChecksum(data)
    message = self.id.to_bytes(1, 'big')+checksum+data
    self.socket.sendto(message, receiverAddress)

    while True:
      try:
        response, address = self.socket.recvfrom(BUFF_SIZE)
        if not self.isCorrupt(response) and self.isACK(response):
          break
      except:
        self.socket.sendto(message, receiverAddress)

    self.id = 1 if self.id == 0 else 0

  def sendACK(self, ACK, checksum, address):
    packet = (self.id).to_bytes(1, 'big') + checksum +'ACK'.encode()
    self.socket.sendto(packet, address)

  def sendACKServer(self, id, checksum, address):
    packet = (id).to_bytes(1, 'big') + checksum +'ACK'.encode()
    self.socket.sendto(packet, address)

  def receiveData(self):
    self.socket.settimeout(0.001)
    response = None
    address = None
    while True:
      response, address = self.socket.recvfrom(BUFF_SIZE)
      if not self.isCorrupt(response) and self.seqValue(response) == self.id:
        break
      else:
        checksum = self.getChecksum('ACK'.encode('utf-8'))
        ACK_value = 1 if self.id == 0 else 0
        self.sendACK(ACK_value, checksum, address)

    data = response[513:]

    checksum = self.getChecksum('ACK'.encode('utf-8'))
    self.sendACK(self.id, checksum, address)

    self.id = 1 if self.id == 0 else 0

    return data, address

  def sendDataServer(self, dict_ids, data, receiverAddress):
    self.socket.settimeout(0.1)
    checksum = self.getChecksum(data)
    key = receiverAddress[0] + ':' + str(receiverAddress[1])
    message = dict_ids[key].to_bytes(1, 'big')+checksum+data
    self.socket.sendto(message, receiverAddress)

    while True:
      try:
        response, address = self.socket.recvfrom(BUFF_SIZE)
        if not self.isCorrupt(response) and self.isACKServer(response, dict_ids[key]):
          break
      except:
        self.socket.sendto(message, receiverAddress)

    if dict_ids[key] == 0:
      dict_ids[key] = 1
    else:
      dict_ids[key] = 0

  def receiveDataServer(self, dict_ids, dict_info):
    self.socket.settimeout(None)
    response = None
    address = None
    id = 0
    new_client = False
    key = None

    while True:
      id = 0
      response, address = self.socket.recvfrom(BUFF_SIZE)
      key = address[0] + ':' + str(address[1])

      if key in dict_ids:
        id = dict_ids[key]

      if not self.isCorrupt(response) and self.seqValue(response) == id:
        break
      else:
        checksum = self.getChecksum('ACK'.encode('utf-8'))
        ACK_value = 1 if id == 0 else 0
        self.sendACKServer(id, checksum, address)

    data = response[513:]

    checksum = self.getChecksum('ACK'.encode('utf-8'))
    self.sendACKServer(id, checksum, address)

    if key not in dict_info.keys():
      dict_info[key] = response[513 + 16:].decode()
      dict_ids[key] = 0
      new_client = True

    name = dict_info[key]

    if id == 0:
      dict_ids[key] = 1
    else:
      dict_ids[key] = 0

    if data.decode() == 'bye':
      del dict_info[key]
      del dict_ids[key]

    return data, address, new_client, name



