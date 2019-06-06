import select, socket, sys, pdb
from chat_utilities import ChatHall, Room, ChatMember
import chat_utilities
buffer = 4096

host = sys.argv[1] if len(sys.argv) >= 2 else ''
listensocket = chat_utilities.create_socket((host, chat_utilities.PORT))
serversocket=listensocket
chat_hall_list = ChatHall()
connection_list = []
connection_list.append(listensocket)

while True:
    read_players, write_players, error_sockets = select.select(connection_list, [], []) 
	    
    for member in read_players:
        if member is listensocket: # new connection, member is a socket
            new_socket, add = member.accept()
            new_member = ChatMember(new_socket)
            connection_list.append(new_member)
            chat_hall_list.welcome_new(new_member)
        else: 
            msg = member.socket.recv(buffer)
	    
	    if not msg:
		chat_hall_list.remove_member(member)
            if msg:
                msg = msg.decode().lower()
                chat_hall_list.msg_handler(member, msg)
            else:
                member.socket.close()
                connection_list.remove(member)
    
# error in sockets
# close the error sockets 
# remove error socket from client list    
    for sock in error_sockets: 
        sock.close()
        connection_list.remove(sock)
