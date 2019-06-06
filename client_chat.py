
# import modules
import select, socket, sys
from chat_utilities import Room, ChatHall, ChatMember
import chat_utilities
buffer = 4096

# check the number of arguments
if len(sys.argv) < 2:
    print("Requried arguments - python client_chat.py [host ip address]")
    sys.exit(1)

# correct input is given
else:
    connect_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect_to_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connect_to_server.connect((sys.argv[1], chat_utilities.PORT))

# successful connection
print("Connected to server\n")
msg_prefix = ''

socket_list = [sys.stdin, server_connection]

def prompt():
    sys.stdout.write('<Me>')
    sys.stdout.flush()
try:
	while True:
	    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
	    
	    for s in read_sockets:
		if s is server_connection:  
		    msg = s.recv(buffer) # to receive the data from the client socket
		    if not msg:
			print("Server down!")
			sys.exit(2)
		    else:
			if msg == chat_utilities.QUIT_STRING.encode():
			    sys.stdout.write('Bye\n')
			    sys.exit(2)
			else:
			    sys.stdout.write(msg.decode())
			    if 'Please tell us your name' in msg.decode():
				msg_prefix = 'name: ' # identifier for name
			    else:
				msg_prefix = ''
			    prompt()

		else:
		    msg = msg_prefix + sys.stdin.readline()
		    server_connection.sendall(msg.encode())
finally:
    sys.exit(2)
		
