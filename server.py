
import socket
from  threading import Thread
import time

IP_ADDRESS = '127.0.0.1'
PORT = 8080
SERVER = None
BUFFER_SIZE = 4096

clients = {}






def disconnectWithClient(message, client, client_name):
   global clients

   ecn = message[11:].strip()
   if(ecn in clients):
       clients[ecn]["connected_with"]=""
       clients[client_name]["connected_with"]=""
       ocs = clients[ecn]["client"]
       greet = f"hello, {ecn} you are successfully disconnected with {client_name}"
       ocs.send(greet.encode())
       msg = f"you are successfully disconnected with {ecn}"
       client.send(msg.encode()) 

def connectClient(message, client, client_name):
    global clients

    ecn = message[8:].strip()
    if (ecn in clients):
        if(not clients[client_name]["connected_with"]):
            clients[ecn]["connected_with"] = client_name
            clients[client_name]["connected_with"] = ecn

            ocs = clients[ecn]["client"]

            greet = f"hello, {ecn} {client_name} connected with you!"
            ocs.send(greet.encode())
            msg = f"you are successfully connected with {ecn}"
            client.send(msg.encode())
        else:
            ocn = clients[client_name]["connected_with"]
            msg = f"you are already connected with {ocn}"

            client.send(msg.encode())



def handleShowList(client):
    global clients

    counter = 0
    for c in clients:
        counter +=1
        client_address = clients[c]["address"][0]
        connected_with = clients[c]["connected_with"]
        message =""
        if(connected_with):
            message = f"{counter},{c},{client_address}, connected with {connected_with},tiul,\n"
        else:
            message = f"{counter},{c},{client_address}, Available,tiul,\n"
        client.send(message.encode())
        time.sleep(1)



def handleMessges(client, message, client_name):
    if(message=="show list"):
        handleShowList(client)

    elif(message[:7]=="connect"):
        connectClient(message, client, client_name)
    
    elif(message[:10]=="disconnect"):
        disconnectWithClient(message, client, client_name)



def handleClient(client, client_name):
    global clients
    global BUFFER_SIZE
    global SERVER

    # Sending welcome message
    banner1 = "Welcome, You are now connected to Server!\nClick on Refresh to see all available users.\nSelect the user and click on Connect to start chatting."
    client.send(banner1.encode())

    while True:
        try:
            BUFFER_SIZE = clients[client_name]["file_size"]
            chunk = client.recv(BUFFER_SIZE)
            message = chunk.decode().strip().lower()
            if(message):
                handleMessges(client, message, client_name)
        except:
            pass



def acceptConnections():
    global SERVER
    global clients

    while True:
        client, addr = SERVER.accept()

        client_name = client.recv(4096).decode().lower()
        clients[client_name] = {
                "client"         : client,
                "address"        : addr,
                "connected_with" : "",
                "file_name"      : "",
                "file_size"      : 4096
            }

        print(f"Connection established with {client_name} : {addr}")

        thread = Thread(target = handleClient, args=(client,client_name,))
        thread.start()


def setup():
    print("\n\t\t\t\t\t\tIP MESSENGER\n")

    # Getting global values
    global PORT
    global IP_ADDRESS
    global SERVER


    SERVER  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind((IP_ADDRESS, PORT))

    # Listening incomming connections
    SERVER.listen(100)

    print("\t\t\t\tSERVER IS WAITING FOR INCOMMING CONNECTIONS...")
    print("\n")

    acceptConnections()



setup_thread = Thread(target=setup)           
setup_thread.start()
