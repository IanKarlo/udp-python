from socket import *
import sys
import os

BUFF_SIZE = 1024

serverName = 'localhost'
serverPort = 8001
s = socket(AF_INET, SOCK_DGRAM)

filename = sys.argv[1]

filesize = os.path.getsize(filename)

def handleSendFile(filename, clientAddress):
  '''
  This function is responsible for reading a saved file and
  sending it to a destination through the socket.
  '''
  s.sendto(f"{filename}".encode('utf-8'),clientAddress)
  with open(filename, "rb") as f:
      while True:
          bytes_read = f.read(BUFF_SIZE)
          if not bytes_read:
              break
          s.sendto(bytes_read, clientAddress)
      s.sendto("/EOF".encode('utf-8'), clientAddress)

def handleFile(filename,file_extension):
  '''
    This  function is responsible for reading the data stream
    relative to the file that will be received, and save it in
    its proper place, knowing its name and extension
  '''
  with open(filename + '.' + file_extension, "wb") as f:
    while True:
      message, clientAddress = s.recvfrom(BUFF_SIZE)
      filteredMessage = message
      if filteredMessage == '/EOF'.encode('utf-8'):
        break
      f.write(filteredMessage)

def handleFileName(message):
  '''
  This function takes the full name of the file and splits it
  into its real name and its extension.
  '''
  filename, file_extension = message.decode().split('.')
  return filename + '_CLIENT', file_extension

handleSendFile(filename, (serverName, serverPort))
#---------------

message, clientAddress = s.recvfrom(BUFF_SIZE)
filename, file_extension = handleFileName(message)
handleFile(filename, file_extension)
print("Arquivo salvo no client")

s.close()