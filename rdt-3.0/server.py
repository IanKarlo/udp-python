from socket import *
import time
import os

from rdt3 import RDT3

server = RDT3(isServer=True, host = 'localhost', port= 8001)
BUFF_SIZE = 1024

def handleFile(filename,file_extension):
  '''
  Lê os dados relativo ao arquivo que será recebido, e o salva
  Enquanto não chegar na mensagem de fim.
  '''
  nome = filename + '.' + file_extension
  if os.path.isfile(nome): os.remove(nome)
  with open(nome, 'wb') as f:
    clientAddress = None
    while True:
      message, clientAddress = server.receiveData()
      filteredMessage = message
      if filteredMessage == 'EOF'.encode('utf-8'): break
      f.write(filteredMessage)
    print("ACABOU DE RECEBER")
    return clientAddress

def handleFileName(message):
  '''
  Divide o nome do arquivo e a extensão.
  '''
  filename, file_extension = message.decode().split('.')
  return filename + '_SERVER', file_extension

def handleSendFile(filename, clientAddress):
  '''
  Lê o arquivo salvo e envia através do socket.
  '''

  server.sendData(f"{filename}".encode('utf-8'),clientAddress)
  with open(filename, "rb") as f:
      while True:
          bytes_read = f.read(BUFF_SIZE)
          if not bytes_read: break
          server.sendData(bytes_read, clientAddress)
      server.sendData(("EOF").encode("utf-8"), clientAddress)
      print("ACABOU DE ENVIAR")

while True:
  message, clientAddress = server.receiveData()
  filename, file_extension = handleFileName(message)
  clientAddress = handleFile(filename, file_extension)
  handleSendFile(filename+'.'+file_extension, clientAddress)
  server.id = 0