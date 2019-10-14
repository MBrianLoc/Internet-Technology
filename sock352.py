
import binascii
import socket as syssock
import struct
import sys
import collections
import random

# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from



'''
struct __attribute__ ((__packed__)) sock352_pkt_hdr {
uint8_t version; /* version number */
uint8_t flags; /* for connection set up, tear-down, control */
uint8_t opt_ptr; /* option type between the header and payload */
uint8_t protocol; /* higher-level protocol */
uint16_t header_len; /* length of the header */
uint16_t checksum; /* checksum of the packet */
uint32_t source_port; /* source port */
uint32_t dest_port; /* destination port */
uint64_t sequence_no; /* sequence number */
uint64_t ack_no; /* acknowledgement number */
uint32_t window; /* receiver advertised window in bytes*/
uint32_t payload_len; /* length of the payload */
}; typedef struct sock352_pkt_hdr sock352_pkt_hdr_t; /* typedef shortcut
'''
#Version set to 0x1 for part 1
version = 0x1
#Defining Blue Attributes
opt_ptr = 0x0
protocol = 0x0
checksum = 0x0
source_port = 0x0
dest_port = 0x0
window = 0x0
#header_len always set to length of header in bytes - 40
header_len = struct.calcsize('!BBBBHHLLQQLL')
#Header Format
headerDataFormat = '!BBBBHHLLQQLL'

'''
Flag Name       Byte(Hex)       Byte(Binary)    Meaning
SOCK352_SYN     0x01            00000001        Connection Initiation
SOCK352_FIN     0x02            00000010        Connection End
SOCK352_ACK     0x04            00000100        Acknowledgement Number
SOCK352_RESET   0x08            00001000        Reset the Connection
SOCK352_HAS_OPT 0xA0            00010000        Option field is valid
'''
#Defining pairs, Useful later when displaying message: signal[flags]
SOCK352_SYN = 0x01
SOCK352_FIN = 0x02
SOCK352_ACK = 0x04
SOCK352_RESET = 0x08
SOCK352_HAS_OPT = 0xA0



def init(UDPportTx,UDPportRx):   # initialize your UDP socket here 
    global transmitter, receiver, sock
    
    #Check ports defined
    if(UDPportRx==''):
        print('Port needs to be defined')
        return
    
    #Initialized UDP socket
    sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
    
    #Set 0.2 second timeout. Probably will be set in the methods, 10 good for testing
    sock.settimeout(10)
    
    #Check creation of socket
    if not sock:
        print('Socket creation Failed.')
        return
    print('Socket Created...')
        
    transmitter = int(UDPportTx)
    receiver = int(UDPportRx)

    #If 0 set to port of choosing
    if transmitter==0:
        transmitter = 33821
    if receiver==0:
        receiver = 33821
    return
#Method for packaging headers; Since tuples cannot be modified we just have to read the flags ect. struct.unpack('!BBBBHHLLQQLL',header)[1]
def packheader(version,flags,opt_ptr,protocol, header_len,checksum,source_port,dest_port,sequence_no,ack_no,window,payload_len):
    #headerDataFormat = '!BBBBHHLLQQLL' defined up top
    headerData = struct.Struct(headerDataFormat)
    #This doesn't work with any negative bytes apparently
    header = headerData.pack(version, flags, opt_ptr, protocol, header_len, checksum, source_port, dest_port, sequence_no, ack_no, window, payload_len)
    return header
class socket:
    
    def __init__(self):  # fill in your code here
        self.isClient = False
        self.connected = 0
        self.header = []
        
        #Fields in Red
        self.flags = 0
        self.header_len = struct.calcsize('!BBBBHHLLQQLL') #40
        self.sequence_no = 0
        self.ack_no = 0
        self.payload_len = 0
        
        return
    
    def bind(self,address):
        return 

    def connect(self,address):  # fill in your code here
        #This is called from the client
        self.isClient = True
        sock.settimeout(0.2)
        
        #idk, bind to '' to all. Not sure about proper way to use transmitter/receiver ports
        sock.bind(('', receiver))
        print('Address of target server: ',address[0] ,',',transmitter)
        print('starting handshake')
        #Initiate triple handshake
        #generate random sequence number
        self.sequence_no = int(random.randint(1,10000))
        #SYN bit
        self.flags = 0x01

        #Packs into self.header
        print('Packet1 sent from Client to Server:')
        print([version,self.flags,opt_ptr,protocol,self.header_len,checksum,source_port,dest_port,self.sequence_no,self.ack_no,window,self.payload_len])
        
        self.header = packheader(version, self.flags, opt_ptr, protocol, self.header_len, checksum, source_port, dest_port, self.sequence_no, self.ack_no, window, self.payload_len)
        
        #Server has responded/ Exits when Server responds with SYN and ACK bits set
        while self.flags!=SOCK352_SYN+SOCK352_ACK:
            try:
                sock.sendto(self.header,(address[0],transmitter))
                print('Packet1 sent')
                #Receiving packet now
                rawpacket,address =  sock.recvfrom(header_len)
                print('Address of Server received:', address)
                print('Packet2 received from Server')
                unpackedpacket = struct.unpack(headerDataFormat, rawpacket)
                print(unpackedpacket)
                #Receiver Flags
                self.flags = unpackedpacket[1]
                break
            except syssock.timeout:
                #Just trying to connect no need to throw out bad packets>ACK# yet
                print('timeout...')
                pass
            
        #Received SEQ(y)/ACK(x+1)
        self.sequence_no = unpackedpacket[8]
        self.ack_no = unpackedpacket[9]
        
        #unpackedpacket[1] ==check flag if Reset flag reset the connection


        #Send SYN(seq=x+1,ACK=y+1)//Sent flag is same one as received so no changes 0x01+0x04
        
        #Hold previous value
        temp = self.sequence_no
        #Changing seq and ack to values to send back
        self.sequence_no = self.ack_no
        self.ack_no = temp+1

        print('Packet3 sent from Client to Server')
        print([version,self.flags,opt_ptr,protocol,self.header_len,checksum,source_port,dest_port,self.sequence_no,self.ack_no,window,self.payload_len])

        
        self.header = packheader(version, self.flags, opt_ptr, protocol, self.header_len, checksum, source_port, dest_port, self.sequence_no, self.ack_no, window, self.payload_len)
        
        sock.sendto(self.header,(address[0],transmitter))
        print('Connect() end')
        return 
    
    def listen(self,backlog):
        return

    def accept(self):
        #Server calls this
        sock.settimeout(None)
        sock.bind(('',receiver))

        #recv returns bytes and sender's address
        rawpacket, address = sock.recvfrom(header_len)
        
        #Used later
        clientsocket = address[1]
        address1 = address[0]
        
        print('Address of Client received:', address)
        
        unpackedpacket = struct.unpack(headerDataFormat, rawpacket)
        #Check for SYN flag
        self.flags = unpackedpacket[1]
        
        if self.flags!=SOCK352_SYN:
            sys.exit('SYN flag missing')
        
        print('Packet1 Received from Client')
        print(unpackedpacket)
        #Unpacked Seq and ACK #s
        self.sequence_no = unpackedpacket[8]
        self.ack_no = unpackedpacket[9]
        
        #Responds with both SYN and ACK bits set
        self.flags = SOCK352_SYN+SOCK352_ACK
        
        #Random # for sequence_no field and sets the ack_no field to the client's incoming sequence_no+1
        self.ack_no = self.sequence_no+1
        self.sequence_no = int(random.randint(1,10000))


        print('Packet2 sent')
        print([version,self.flags,opt_ptr,protocol,self.header_len,checksum,source_port,dest_port,self.sequence_no,self.ack_no,window,self.payload_len])
        #Sends SYN(seq=y,ACK=x+1) back to client
        
        self.header = packheader(version, self.flags, opt_ptr, protocol, self.header_len, checksum, source_port, dest_port, self.sequence_no, self.ack_no, window, self.payload_len)
        sock.sendto(self.header,address)
        #receives SYN(seq = x+1,ACK=y+1) to finish connection
        
        rawpacket2 = sock.recvfrom(header_len)[0]
        unpackedpacket2 = struct.unpack(headerDataFormat, rawpacket2)

        print('Packet3 received from Client')
        print(unpackedpacket2)
        
        if self.flags!=SOCK352_SYN+SOCK352_ACK:
            sys.exit('SYN+ACK flag missing')
            
        print('Final Check for Connection', self.ack_no, '==',unpackedpacket2[8], ' and ', self.sequence_no+1, '==', unpackedpacket2[9])
        if self.ack_no==unpackedpacket2[8] and self.sequence_no+1==unpackedpacket2[9]:
            print('Sucessfully Connected.')
            #Successful connection
            (clientsocket, address1) = (1,1)  # change this to your code
        else:
            sys.exit('SEQ and ACK expected are incorrect')
        print('Accept() end')
        return (clientsocket,address1)
    
    def close(self):   # fill in your code here 
        return 

    def send(self,buffer):
        bytessent = 0     # fill in your code here 
        return bytessent 

    def recv(self,nbytes):
        bytesreceived = 0     # fill in your code here
        return bytesreceived

    


    
    


    
