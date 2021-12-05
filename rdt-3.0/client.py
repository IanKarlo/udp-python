from socket import *
import sys
import os
import time

from rdt3 import RDT3

client = RDT3()
BUFF_SIZE = 1024

serverName = 'localhost'
serverPort = 8001

serverAddress = (serverName, serverPort)

filename = None

try:
  if sys.argv[1]: filename = sys.argv[1]
except:
  filename = input("Coloque o nome do arquivo para enviar: ")

def handleSendFile(filename, serverAddress):
  '''
  Lê o arquivo salvo e envia através do socket.
  '''
  client.sendData(f"{filename}".encode('utf-8'), serverAddress)
  with open(filename, "rb") as f:
      while True:
          bytes_read = f.read(BUFF_SIZE)
          if not bytes_read: break
          client.sendData(bytes_read, serverAddress)
      client.sendData("EOF".encode("utf-8"), serverAddress)
      print("Acabou de enviar")

def handleFile(filename,file_extension):
  '''
  Lê os dados relativo ao arquivo que será recebido, e o salva
  Enquanto não chegar na mensagem de fim.
  '''
  nome = filename + '.' + file_extension
  if os.path.isfile(nome): os.remove(nome)
  with open(nome, "wb") as f:
    while True:
      message, clientAddress = client.receiveData()
      filteredMessage = message
      if filteredMessage == 'EOF'.encode('utf-8'): break
      f.write(filteredMessage)
    print("ACABOU DE RECEBER")

def handleFileName(message):
  '''
  Divide o nome do arquvio e a extensão.
  '''
  filename, file_extension = message.decode().split('.')
  return filename + '_CLIENT', file_extension

handleSendFile(filename, serverAddress)
#---------------
message, clientAddress = client.receiveData()
filename, file_extension = handleFileName(message)
handleFile(filename, file_extension)
print("Arquivo salvo no client")

# s.close()