import os
import socket 
import hashlib
import threading
import logging
import datetime
import time
import subprocess
import time
import threading
import pyshark
from os import error

wait_hours = 12  #Stop for 12 hours and then run again
run_hours = 1/60    #We will run ngrep for an hour. The nth run will be dumped to net_log_n.txt
run_time_limit = 100 

SIZE=1024
PORT = 1234 


def hash_file(path):
    f = open(path, "rb").read(SIZE)
    hash_object = hashlib.md5()
    hash_object.update(f)
    return f, hash_object.hexdigest()

def log(message, error=False):
    if not error:
        logging.info(message)
    else:
        logging.error(message)



def handle_client(connection, addr, id, f):
    def send(message):
        connection.send(message.encode(encoding='ascii', errors='ignore'))

    def receive():
        return connection.recv(SIZE).decode(encoding="ascii", errors="ignore")
    
    log('Connected to client number: ' +id+' with ip:'+str(addr))
    print('Connection obtained from', addr)

    def capture(timeout=60):
        capture = pyshark.LiveCapture(output_file='./result.pcap')
        capture.clear()
        capture.close()

    t = threading.Thread(target=capture)
    #t.start()
    #print('Starting pyshark')
    
    #Saying hi
    send(str(id))
    
    #Sending file hash
    send(hash_code) 

    #waiting for confirmation
    print(receive())

    #sending file
    start_time = time.time()
    connection.send(f) 

    #waiting for the file transfer result
    result = receive()
    total_time = time.time() - start_time

    if result == 'Nice':
        log('File successfully received by client '+id)
    else:
        log('Client '+id+' received a corrupt file', True)
    connection.close()
    log('Total transference time for client '+id+':'+str(total_time))
    
    #print('Killing pyshark')
    
    print('done')



while True:
    
    clients = int(input("Specify the number of concurrent clients to receive:"))
    print("Choose the file to send:")

    file_name=input("0 for 100 MB\n1 for 250MB\n")
    if file_name == '0':
        file_size = '100MB'
        file_name = 'small'
        #file_name = 'test.txt'
    else:
        file_size = '250MB'
        file_name = 'big'

    f, hash_code = hash_file(file_name)
    print("Hash:", hash_code)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    host = socket.gethostbyname(host + ".local")
    print('Listening on ip ', host)
    server_socket.bind((host, PORT)) 
    server_socket.listen(clients)
    print('Bind done')
    threads = []
    op = True
    i = 0
    while op:
        connection, addr = server_socket.accept ()
        i += 1
        thread = threading.Thread(target=handle_client, args=(connection, addr, str(i), f))
        threads.append(thread)

        if i >= clients:
            op = False

            now = datetime.datetime.now()
            log_path = './log/server/'+ str(now.year) +'-'+ str(now.month)+'-'+str(now.day)+'-'+str(now.hour)+'-'+str(now.minute)+'-'+str(now.second)+'-log.txt'
            
            logging.basicConfig(level=logging.INFO, filename=log_path, filemode='w', format='%(asctime)s - %(message)s')
            
            log('Starting test')    
            log('File name: ' + file_name+', Size: '+file_size)    

            for t in threads:
                t.start()
            for t in threads:
                t.join()
