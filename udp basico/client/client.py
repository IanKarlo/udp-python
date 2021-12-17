from socket import *
import sys
import os
import time

BUFF_SIZE = 1024
DELAY = 1e-3 # No Linux alguns arquivos podem não chegar

serverName = 'localhost'
serverPort = 8001
s = socket(AF_INET, SOCK_DGRAM)

filename = None

try: 
  if sys.argv[1]: filename = sys.argv[1]
except: 
  filename = input("Coloque o nome do arquivo para enviar: ")

def handleSendFile(filename, clientAddress):
  '''
  Lê o arquivo salvo e envia através do socket.
  '''
  global s
  s.sendto(f"{filename}".encode('utf-8'),clientAddress)
  with open(filename, "rb") as f:
      while True:
          time.sleep(DELAY)
          bytes_read = f.read(BUFF_SIZE)
          if not bytes_read: break
          s.sendto(bytes_read, clientAddress)
      s.sendto(("/EOF").encode("utf-8"), clientAddress)
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
      time.sleep(DELAY)
      message, clientAddress = s.recvfrom(BUFF_SIZE)
      filteredMessage = message
      if '/EOF'.encode('utf-8') in filteredMessage: break
      f.write(filteredMessage)
    print("ACABOU DE RECEBER")

def handleFileName(message):
  '''
  Divide o nome do arquvio e a extensão.
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