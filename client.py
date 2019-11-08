# This is a simple FTP client implemented in python,
# just to get to know networking works in python and how FTP works underneath the hood.

import socket

FTP_HOST = ''
FTP_USER = ''
FTP_PASS = ''
FTP_ACTIVE_MODE = True
FTP_MAX_COMMAND_SIZE = 1024

def make_command(command, param):
    return bytes(command + ' ' + param + '\r\n', 'ascii')

def ftp_login(soc, username, password):
    soc.sendall(make_command('USER', username))
    response = soc.recv(FTP_MAX_COMMAND_SIZE).decode('ascii')

    # code 331 means that username is OK, password is needed
    if '331' not in response:
        return False
    
    soc.sendall(make_command('PASS', password))
    response = soc.recv(FTP_MAX_COMMAND_SIZE).decode('ascii')

    # code 230 means successful login
    if '230' in response:
        return True
    
    #TODO: check for more detailed errors if login failed
    return False


# AF_INET means using ipv4 address, SOCK_STREAM means using TCP protocol (used by FTP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
    host_ip = socket.gethostbyname(FTP_HOST)
    # FTP servers uses 2 ports: port 21 for interchange FTP commands (that's what we use to connect),
    # and port 20 for sending the desired data
    soc.connect((host_ip, 21))
    response = soc.recv(FTP_MAX_COMMAND_SIZE)

    #FTP uses the Telnet procotol for exchanging commands
    if not ftp_login(soc, FTP_USER, FTP_PASS):
        print('login failed')
        exit()

    #now if we logged in, we need to initialize a data connection
    #there is 2 kinds of connection types: active and passive:
    #- active means that the client chooses a port N for command port and N + 1 for data port.
    #The active connection setup looks like this:
    #client port N connects to server port 21, and then server port 20 connects back to client port N + 1
    #- passive means that 

    if FTP_ACTIVE_MODE:
        data_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_soc.connect((host_ip, 20))

        local_ip = soc.getsockname()[0]
        local_data_port = data_soc.getsockname()[1]
        #we need to use the PORT command to send the server our data port
        #PORT command format is: PORT a1,a2,a3,a4,s1,s2 where a1-a4 are ip address octets,
        #and s1,s2 are our socket number in a format that
        #port number = s1 * 256 + s2
        s1 = local_data_port // 256
        s2 = local_data_port % 256
        #this should be sometinh like 192,168,0,101,255,151
        port_cmd_arg = local_ip.replace('.', ',') + ',' + str(s1) + ',' + str(s2)

        soc.sendall(make_command('PORT', port_cmd_arg))
        response = soc.recv(FTP_MAX_COMMAND_SIZE).decode('ascii')
        
        #we successfully initialied the active data connection, so we can now use the MLSD command for example
        #to retrieve the files in the current directory
        if '200' in response:
            soc.sendall(make_command('MLSD', ''))
            reponse = data_soc.recv(FTP_MAX_COMMAND_SIZE).decode('ascii')
            print(reponse)
        else:
            print('Active connection failed')
        data_soc.close()
    else:
        print('Passive mode has not been implemented yet.')

    # soc.sendall(make_command('LIST', ''))
    # response = soc.recv(FTP_MAX_COMMAND_SIZE).decode('ascii')
    # print(response)
    # soc.sendall(make_command('QUIT', ''))