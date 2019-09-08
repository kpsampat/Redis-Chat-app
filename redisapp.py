import redis
import socket
import thread
import logging

r = redis.Redis(host="localhost", port=6379, db=0)

contact_info = []
contact_list = {}
con = {}
data={}

def got_input():
    name = raw_input("enter the user name :")
    ip = raw_input("enter the ip of user with port seperated by -p :")
    data = {"name":name,"ip":ip}
    return data

def add_user():
    info =got_input()
    count=r.get("count")
    if count in (None,""):
        count = 1
        r.set("count",count)
    else:
        r.incr("count",1)
        count = int(r.get("count"))
    r.hmset(count,info)


def get_connection():
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address1 = ("127.0.0.1", 2500)
        sock1.bind(server_address1)
        while True:
            sock1.listen(5)
            conn, addr = sock1.accept()
            con[conn]=addr

def load():
    count = r.get("count")
    if count in (None,""):
        print "No Contacts"
    else:
        count = int(count)
        for i in range(1,count+1):
            user = r.hgetall("user:{}".format(i))
            contact_list[user["name"]] = user["ip"]
            contact_info.append(user)



def show_contact():
    load()
    count = 1
    for user,ip in contact_list.items():
        print "{}. Name:{}, ip:{}".format(count,user,ip)
        count = count + 1



def client():
    user = raw_input("Enter the user")
    IP,port = contact_list[user].split("-p")
    port = int(port)
    status = 0                                   #establish a connection if 0 and 1 is connection is there
    logging.info("GOT the user input")
    while True:
        message_data = raw_input("Enter the message")
        try:
            if status == 0:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((IP, port))
                while True:
                    queue_data = r.lpop('data')
                    if queue_data:
                        s.sendall(queue_data)
                    else:
                        break
                s.sendall(message_data)
                status = 1
            elif status == 1:
                s.sendall(message_data)
                status = 1
            else:
                pass

        except:
            print("data in queue")
            if queue_data not in (None,""):
                r.lpush("data",queue_data)
            r.rpush("data",message_data)
            status = 0

def start_chat():
    try:
        thread.start_new_thread(client, ( ) )
        logging.info("Threat of client executed")
    except Exception,e:
        logging.error("There is an error {}".format(e))

    while True:
        pass

thread.start_new_thread(get_connection, ( ))
load()


while True:
    print "Select 1 to show existing contact list | 2 to add if u want to add a contact is directory | 3 to start chatting | 4 to exit"
    choice = raw_input("Enter the input")
    if choice == "1":
        show_contact()
    elif choice == "2":
        add_user()
    elif choice == "3":
        start_chat()
    elif choice == "4":
        break
    else:
        print"Need an input"
