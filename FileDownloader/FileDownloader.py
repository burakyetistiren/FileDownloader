'''
Whilst running our application in terminal, the structure of the command should be the following: 

    If a range is not given:
        - python3 FileDownloader.py <index_file>

        Example:
            python3 FileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt 
    
    If a range is given:
        - python3 FileDownloader.py <index_file> <lower_endpoint>-<upper_endpoint> 

        Example:
            python3 FileDownloader.py www.cs.bilkent.edu.tr/~cs421/fall21/project1/index1.txt 0-100
'''
from socket import *
import sys
import os

# Default server port for TCP connection for server
serverPort = 80

# Create and return a socket
def createSocket():
    return socket(AF_INET, SOCK_STREAM)

# Split the link into server name and directory
def splitLink(link):
    return link.split("/", 1)

# Create GET request message
def createGETrequestMessage(directory, serverName, rangeStart=-1, rangeEnd=-1):
    if rangeStart > -1 and rangeEnd > -1:
        return "GET /%s HTTP/1.1\r\nHost:%s\r\nRange: bytes=%d-%d\r\n\r\n" % (directory, serverName, rangeStart, rangeEnd)
    return "GET /%s HTTP/1.1\r\nHost:%s\r\n\r\n" % (directory, serverName)

# Create HEAD request message
def createHEADrequestMessage(directory, serverName, rangeStart=-1, rangeEnd=-1):
    if rangeStart > -1 and rangeEnd > -1:
        return "HEAD /%s HTTP/1.1\r\nHost:%s\r\nRange: bytes=%d-%d\r\n\r\n" % (directory, serverName, rangeStart, rangeEnd)
    return "HEAD /%s HTTP/1.1\r\nHost: %s\r\n\r\n" % (directory, serverName)

# Get the body of the response
def getBody(head, get):
    message = get[len(head):]
    lines = []
    for line in message.splitlines():
        lines.append(line)
    return lines

def getBody_message(head, get):
    message = get[len(head):]
    return message

def getBodySizeChar(head):
    count = 0
    for i in body:
        count += len(i)
    return count

# Save the file in the current directory
def save_file(file_name, body):
    file_name = file_name.replace("/", "")
    f = open(os.path.join(os.getcwd(), file_name), 'w')
    for i in body:
        f.write(i + "\r\n")
    f.close()

def save_file_message(file_name, body):
    file_name = file_name.replace("/", "")
    with open(os.path.join(os.getcwd(), file_name), 'w') as f:
        f.write(body)
    f.close()

# Create socket, connect to server and send request message
def prepareSocket(server_name, request_mes):
    clientSocket = createSocket()
    clientSocket.connect((server_name, serverPort))
    clientSocket.send(request_mes.encode())
    return clientSocket

# Get the response message from the server for each link in index file
def download_files(links, upper_endpoint, lower_endpoint):
    responseList = []
    
    count = 1
    # Traverse through all the links in the index file
    for link in links:
        link_data = splitLink(link)
        requestMessageHead = createHEADrequestMessage(link_data[1], link_data[0])
        requestMessageGet = createGETrequestMessage(link_data[1], link_data[0])

        clientSocket = prepareSocket(link_data[0], requestMessageHead)

        # Get the response HEAD message from the buffer 
        responseHead = ""
        while True:
            resp_part = clientSocket.recv(4096)
            if resp_part == b'':
                break
            responseHead += resp_part.decode()
        clientSocket.close()

        clientSocket = prepareSocket(link_data[0], requestMessageGet)

        # Get the response GET message from the buffer
        responseGet = ""
        while True:
            resp_part = clientSocket.recv(4096)
            if resp_part == b'':
                break
            responseGet += resp_part.decode()
        clientSocket.close()

        # Check the response status code and if the status code is 200, save the file if no range is specified
        if "200 OK" in responseHead.splitlines()[0]:
            body = getBody(responseHead, responseGet)
            length = getBodySizeChar(responseHead)
            print(length)
            print(responseHead)
            # If range is specified, send the request message again with the range specified
            if upper_endpoint > -1 or lower_endpoint > -1:
                # If body is smaller than the lower endpoint, don't download the file and print the error message
                if length < lower_endpoint:
                    #print("%d. %s (size = %d) is downloaded." %(count, link, lower_endpoint))
                    print("ERROR: The requested file is not requested since the size of the file is smaller than lower endpoint!" + "\n\t" + "File: " + link + "\n\t" + "Size: " + str(length))
                else:
                    requestMessagePartialGET = createGETrequestMessage(link_data[1], link_data[0], lower_endpoint, upper_endpoint)
                    requestMessagePartialHEAD = createHEADrequestMessage(link_data[1], link_data[0], lower_endpoint, upper_endpoint)
                    
                    clientSocket = prepareSocket(link_data[0], requestMessagePartialGET)

                    responsePartialGET = ""
                    while True:
                        resp_part = clientSocket.recv(4096)
                        if resp_part == b'':
                            break
                        responsePartialGET += resp_part.decode()
                    
                    clientSocket.close()

                    clientSocket = prepareSocket(link_data[0], requestMessagePartialHEAD)

                    responsePartialHEAD = ""
                    while True:
                        resp_part = clientSocket.recv(4096)
                        if resp_part == b'':
                            break
                        responsePartialHEAD += resp_part.decode()
                    
                    clientSocket.close()

                    partialBody = getBody_message(responsePartialHEAD, responsePartialGET)
                    save_file_message(link_data[1], partialBody)  
                    print("%d. %s (range = %d - %d) is downloaded." %(count, link, lower_endpoint, upper_endpoint))
            else:
                save_file(link_data[1], body)  
                print("%d. %s (range = Complete file) is downloaded." %(count, link))
        else:
            print("%d. %s is not found." %(count, link))
        count += 1

index_file = ""
endpoints = ""
upper_endpoint = -1
lower_endpoint = -1

# Read the command line arguments
for i, arg in enumerate(sys.argv):
    # Index 0 is FileDownloader.py So we start at 1
    if i == 1:
        index_file = arg
    elif i == 2:
        endpoints = arg
        endpoints = endpoints.split("-")

        lower_endpoint = int(endpoints[0])
        upper_endpoint = int(endpoints[1])

index_file = splitLink(index_file)

# Specify server name and server port
serverName = index_file[0]
directory = index_file[1]

print("URL of the index file: %s" %sys.argv[1])

if lower_endpoint > -1:
    print("Lower endpoint = %d" %lower_endpoint)
else:
    print("Lower endpoint = Not specified")

if upper_endpoint > -1:
    print("Lower endpoint = %d" %upper_endpoint)
else:
    print("Lower endpoint = Not specified")


# Create client socket and GET message for the index file
requestMessageIndexGET = createGETrequestMessage(directory, serverName)
clientSocket = prepareSocket(serverName, requestMessageIndexGET)

responseIndexGET = ""
while True:
    resp_part = clientSocket.recv(4096)
    if resp_part == b'':
        break
    responseIndexGET += resp_part.decode()
clientSocket.close()

requestMessageIndexHEAD = createHEADrequestMessage(directory, serverName)
clientSocket = prepareSocket(serverName, requestMessageIndexHEAD)

responseIndexHEAD = ""
while True:
    resp_part = clientSocket.recv(4096)
    if resp_part == b'':
        break
    responseIndexHEAD += resp_part.decode()
clientSocket.close()

file_count = -1

body = ""
if "200 OK" in responseIndexHEAD.splitlines()[0]:
    body = getBody(responseIndexHEAD, responseIndexGET)
    file_count = len(body)
    print("There are %d file URLs in the index file." % file_count)
    print("Index file is downloaded.")
else:
    print("ERROR: The index file is not found!\r\n" + responseIndexHEAD.splitlines()[0])
    sys.exit(1)

download_files(body, upper_endpoint, lower_endpoint)
