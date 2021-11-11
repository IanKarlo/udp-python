from socket import *

serverPort = 8001
serverSocket = socket(AF_INET, SOCK_DGRAM)
BUFF_SIZE = 1024

serverSocket.bind(('localhost', serverPort))

print ('The server is ready to receive')

def handleFile(filename,file_extension):
  '''
    This  function is responsible for reading the data stream
    relative to the file that will be received, and save it in
    its proper place, knowing its name and extension
  '''
  with open(filename + '.' + file_extension, "wb") as f:
    clientAddress = None
    while True:
      message, clientAddress = serverSocket.recvfrom(BUFF_SIZE)
      filteredMessage = message
      if filteredMessage == '/EOF'.encode('utf-8'):
        break
      f.write(filteredMessage)
    return clientAddress


def handleFileName(message):
  '''
  This function takes the full name of the file and splits it
  into its real name and its extension.
  '''
  filename, file_extension = message.decode().split('.')
  return filename + '_SERVER', file_extension


def handleSendFile(filename, clientAddress):
  '''
  This function is responsible for reading a saved file and
  sending it to a destination through the socket.
  '''
  serverSocket.sendto(f"{filename}".encode('utf-8'),clientAddress)
  with open(filename, "rb") as f:
      while True:
          bytes_read = f.read(BUFF_SIZE)
          if not bytes_read:
              break
          serverSocket.sendto(bytes_read, clientAddress)
      serverSocket.sendto("/EOF".encode('utf-8'), clientAddress)

while True:
  message, clientAddress = serverSocket.recvfrom(BUFF_SIZE)
  filename, file_extension = handleFileName(message)
  clientAddress = handleFile(filename, file_extension)
  handleSendFile(filename+'.'+file_extension, clientAddress)

