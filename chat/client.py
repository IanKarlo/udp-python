from socket import *
import threading
import sys

from rdt3 import RDT3

client = RDT3()
startPort = 5000
while True:
  try:
    client.socket.bind(('', startPort))
    break
  except:
    startPort += 1

BUFF_SIZE = 1024

serverName = 'localhost'
serverPort = 8001

serverAddress = (serverName, serverPort)

username = None

threadlock = threading.Lock()

loop = True


def clearLine():
  sys.stdout.write("\033[F")
  sys.stdout.write("\033[K")

def handleStart(threadlock):
  while True:
    text = input()
    if text[0:16] == 'hi, meu nome eh ':
      global username
      username = text[16:]
      client.sendData(text.encode('utf-8'), serverAddress)
      clearLine()
      break
  #CHAT CONNECTION
  thread = threading.Thread(target=waitMessage, args=(client, threadlock))
  thread.start()

  global loop

  while loop:
    message = input()
    clearLine()
    threadlock.acquire()
    client.sendData(message.encode('utf-8'), serverAddress)
    threadlock.release()

    if(message == 'bye'):
      loop = False

  print("Desconectado do chat, até logo.")


def waitMessage(socket, theadlock):
  while loop:
    threadlock.acquire()
    try:
      msg, address = socket.receiveData()
      print(msg.decode())
    except:
      pass
    threadlock.release()

handleStart(threadlock)
