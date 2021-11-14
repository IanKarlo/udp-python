from socket import *
import time
import os

serverPort = 8001
serverSocket = socket(AF_INET, SOCK_DGRAM)
BUFF_SIZE = 1024
DELAY = 1e-3 # No Linux alguns arquivos podem não chegar

serverSocket.bind(('localhost', serverPort))
print ('The server is ready to receive')

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
      time.sleep(DELAY)
      message, clientAddress = serverSocket.recvfrom(BUFF_SIZE)
      filteredMessage = message
      if filteredMessage == '/EOF'.encode('utf-8'): break
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

  serverSocket.sendto(f"{filename}".encode('utf-8'),clientAddress)
  with open(filename, "rb") as f:
      while True:
          time.sleep(DELAY)
          bytes_read = f.read(BUFF_SIZE)
          if not bytes_read: break
          serverSocket.sendto(bytes_read, clientAddress)
          print("ENVIANDO")
      serverSocket.sendto(("/EOF").encode("utf-8"), clientAddress)
      print("ACABOU DE ENVIAR")

while True:
  message, clientAddress = serverSocket.recvfrom(BUFF_SIZE)
  filename, file_extension = handleFileName(message)
  clientAddress = handleFile(filename, file_extension)
  handleSendFile(filename+'.'+file_extension, clientAddress)

