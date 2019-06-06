
import socket, pdb

# const values for maximum clients, port number and quit message
MAX_CLIENTS = 30
PORT = 22221
QUIT_STRING = '<$quit$>'

#create socket 
def create_socket(address):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Now listening at ", address)
    return s

# class to handle the room operations
class Room:
    def __init__(self, name):
        self.members = [] 
        self.name = name	
    
# function to broadcast message from the client
    def broadcast(self, from_member, msg):
        msg = from_member.name.encode() + b":" + msg
        for member in self.members:
            member.socket.sendall(msg)
			
# function to welcome the new client to begin chat
    def welcome_new(self, from_member):
        msg = self.name + " welcomes: " + from_member.name + '\n'
        for member in self.members:
            member.socket.sendall(msg.encode())
			
# function to remove a client from the connection
    def remove_member(self, member):
        self.members.remove(member)
        leave_msg = member.name.encode() + b"has left the room\n"
        self.broadcast(member, leave_msg)
	
# class to maintain a list of clients present
class ChatMember:
    def __init__(self, socket, name = "new" , currentroomname="new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
	self.currentroomname=currentroomname

    def fileno(self):
        return self.socket.fileno()
	
class ChatHall:
# function to welcome the new client
    def __init__(self):
        self.rooms = {} 
        self.room_member_map = {} 
	self.members_map = {} 
	
# function to welcome the new client
    def welcome_new(self, new_member):
        new_member.socket.sendall(b'Welcome to pychat.\nPlease tell us your name:\n')
    
    def msg_handler(self, member, msg):
        
        instructions = b'Options:\n'\
            + b'[<list>] to list the available rooms\n'\
            + b'[<join> room_name] to join or create a new room\n' \
	    + b'[<personal> member_name] to start a private chat\n'\
            + b'[<manual>] to display the options\n' \
	    + b'[<switch>] to switch room\n' \
	    + b'[<leave>] to leave the current room\n'\
            + b'[<quit>] to quit the chat\n' \
            + b'Enjoy the chat..' \
            + b'\n'

        print(member.name + " says: " + msg)
        if "name:" in msg:
            name = msg.split()[1]
            member.name = name
            print("New connection from:", member.name)
	    self.members_map[member.name]=member
            member.socket.sendall(instructions)

			elif "<quit>" in msg:
            member.socket.sendall(QUIT_STRING.encode())
            self.remove_member(member)
   
         elif "<list>" in msg:
	    print self.rooms
	    print self.room_member_map
            self.list_rooms(member) 
			
        elif "<join>" in msg:
            same_room = False
            if len(msg.split()) >= 2: 
                room_name = msg.split()[1]
		member.currentroomname = room_name
                if member.name+"-"+room_name in self.room_member_map: 
                    if self.room_member_map[member.name+"-"+room_name] == room_name:
                        member.socket.sendall(b'You are already in room: ' + room_name.encode())
                        same_room = True
                    else: 
                        old_room = self.room_member_map[member.name+"-"+room_name]
                if not same_room:
                    if not room_name in self.rooms: 
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].members.append(member)
                    self.rooms[room_name].welcome_new(member)
                    self.room_member_map[member.name+"-"+room_name] = room_name
            else:
                member.socket.sendall(instructions)

        elif "<switch>" in msg:
	    if len(msg.split()) >= 2:
		    switchroomname=msg.split()[1]
	 	    if member.name+"-"+switchroomname in self.room_member_map:
	
			member.currentroomname = switchroomname

		    else:
			msg = "you are not in entered room please join"
			member.socket.sendall(msg.encode())
	    else:
		member.socket.sendall(instructions)
	
	elif "<leave>" in msg:
	    
	    if len(msg.split()) >= 2: 
		    leaveroomname=msg.split()[1]
		   
		    if member.name+"-"+leaveroomname in self.room_member_map:
			del self.room_member_map[member.name+"-"+member.currentroomname]
			self.rooms[leaveroomname].remove_member(member)
	       		print("ChatMember: " + member.name + " has left"+leaveroomname+"\n")
			if len(self.rooms[leaveroomname].members)==0:
			    del self.rooms[leaveroomname]
		    else :
			msg = "you entered wrong room name please try again\n"
			member.socket.sendall(msg.encode())
	    else:
                member.socket.sendall(instructions)
				
	elif "<personal>" in msg:
	    if len(msg.split()) >= 2:
		    membername = msg.split()[1]
		    if membername in self.members_map:
			    newmember = self.members_map[membername]
			    personal_room = Room("personal-"+member.name+"-"+membername)
			    self.rooms["personal-"+member.name+"-"+membername] = personal_room
			    self.rooms["personal-"+member.name+"-"+membername].members.append(member)
			    self.rooms["personal-"+member.name+"-"+membername].members.append(newmember)
			    self.room_member_map[member.name+"-"+"personal-"+member.name+"-"+membername] = "personal-"+member.name+"-"+membername
			    self.room_member_map[membername+"-"+"personal-"+member.name+"-"+membername] = "personal-"+member.name+"-"+membername
			    member.currentroomname = "personal-"+member.name+"-"+membername
			    newmember.currentroomname = "personal-"+member.name+"-"+membername
		    else:
			msg = "Entered member does not exsist!!"
			member.socket.sendall(msg.encode())
	    else:
		    member.socket.sendall(instructions)
			
			 elif "<manual>" in msg:
            member.socket.sendall(instructions)
		
	elif not msg:
	    self.remove_member(member)

        else:
# check if in a room or not first
            if member.name+"-"+member.currentroomname in self.room_member_map:
                self.rooms[self.room_member_map[member.name+"-"+member.currentroomname]].broadcast(member, msg.encode())
            else:
                msg = 'You are currently not in any room! \n' \
                    + 'Use [<list>] to see available rooms! \n' \
                    + 'Use [<join> room_name] to join a room! \n'
                member.socket.sendall(msg.encode())
    
# function to remove a client from the connection
    def remove_member(self, member):
        if member.name +"-"+member.currentroomname in self.room_member_map:
            self.rooms[self.room_member_map[member.name+"-"+member.currentroomname]].remove_member(member)
            del self.room_member_map[member.name+"-"+member.currentroomname]
        print("ChatMember: " + member.name + " has left\n")

# function to handle the listing of rooms
    def list_rooms(self, member):
        
        if len(self.rooms) == 0:
            msg = 'Oops, no active rooms currently. Create your own!\n' \
                + 'Use [<join> room_name] to create a room.\n'
            member.socket.sendall(msg.encode())
        else:
            msg = 'Listing current rooms and members...\n'
            for room in self.rooms:
		if 'personal' not in room:
			print (self.rooms[room].members)
		
		        msg += room + ": " + str(len(self.rooms[room].members)) + " member(s)\n"
			for member1 in self.rooms[room].members:
				msg += member1.name +"\n"
	    member.socket.sendall(msg.encode())

 
    

    
