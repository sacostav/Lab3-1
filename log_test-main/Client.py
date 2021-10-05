import datetime
import socket
import hashlib
import threading
import logging
import time

SIZE=1024
FOLDER="ArchivosRecibidos"

FOLDER+="/"

#host = "192.168.0.4"
#host = socket.gethostname() 

port = 1234 

def hash_file(f):
    hash_object = hashlib.md5()
    hash_object.update(f)
    return hash_object.hexdigest()


def save_file(id, data):
    file = open(FOLDER+id+'-Prueba-'+str(clients)+'.txt', "wb")
    file.write(data)

def log(message, error=False):
    if not error:
        logging.info(message)
    else:
        logging.error(message)

while True:
    hr = input("Do you wanna use the host name as host ip? (Y|N):")
    host = socket.gethostname()
    host = socket.gethostbyname(host + ".local")

    if hr == 'N' or hr == 'n' or hr=='no':
        host = input("Specify the host ip:")
    global clients
    clients = int(input("Specify the number of concurrent clients to send:"))

    def connect_client():

        def send(message):
            connection.send(message.encode(encoding='ascii', errors='ignore'))

        def receive():
            return connection.recv(SIZE).decode(encoding="ascii", errors="ignore")

        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((host, port)) 
        print("Connected")
        print("Waiting for confirmation")

        #Receiving connetion confirmation
        id = receive()
        log('Client number: '+id+' connected to the server')
        print('Confirmation received id:', id)

        #Waiting for the hash code
        received_hash_code = receive()
        print('Client '+id+ ' - hash received:', received_hash_code)

        #Sending confirmation
        send('Client '+id+ ' - Hash received')

        #Waiting for the file
        start_time = time.time()
        data = connection.recv(SIZE)
        generated_hash_code = hash_file(data)

        if received_hash_code != generated_hash_code:
            print('Client '+id+ ' - Received file is corrupted')
            print('Client '+id+ ' - Hash received:', received_hash_code)
            print('Client '+id+ ' - Hash generated:', generated_hash_code)
            send('Received file is corrupted') 
            log('Client '+id+' received a corrupt file', True)
        else:
            log('File successfully received by client '+id)
            print('Client '+id+ ' - File received')
            send('Nice') 
        total_time = time.time() 
        log('Total transference time for client '+id+':'+str(total_time))
        
        save_file(id, data)
        connection.close()

    threads = []
    op = True
    for i in range(clients):
        thread = threading.Thread(target=connect_client)
        thread.start()
        threads.append(thread)
    now = datetime.datetime.now()
    log_path = './log/client/'+ str(now.year) +'-'+ str(now.month)+'-'+str(now.day)+'-'+str(now.hour)+'-'+str(now.minute)+'-'+str(now.second)+'-log.txt'
       
    logging.basicConfig(level=logging.INFO, filename=log_path, filemode='w', format='%(asctime)s - %(message)s')
            
    for t in threads:
        t.join()
