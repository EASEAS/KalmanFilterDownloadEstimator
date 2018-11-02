import socket               # Import socket module

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                 # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.
print("Server online ")
while True:
    f = open('received_file','wb')
    c, addr = s.accept()     # Establish connection with client.
    print ('Got connection from', addr)
    print ("Receiving...")
    l = c.recv(1024)
    while (l):
        f.write(l)
        l = c.recv(1024)
    f.close()
    print ("Done Receiving")
    c.sendall(b'Thank you for connecting')
    c.close()                # Close the connection
