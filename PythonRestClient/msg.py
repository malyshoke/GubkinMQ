import threading
from dataclasses import dataclass
import socket, struct, time

MT_INIT		= 0
MT_EXIT		= 1
MT_GETDATA	= 2
MT_DATA		= 3
MT_NODATA	= 4
MT_CONFIRM	= 5
MT_GETLAST  = 6
MT_INITSTORAGE = 7
MT_GETLAST_PUBLIC = 8
MT_REST = 9

MR_BROKER	= 10
MR_STORAGE  = 20
MR_RESTSERVER = 30
MR_ALL		= 50
MR_USER		= 100



@dataclass
class MsgHeader:
	To: int = 0
	From: int = 0
	Type: int = 0
	Size: int = 0

	def Send(self, s):
		s.send(struct.pack(f'iiii', self.To, self.From, self.Type, self.Size))

	def Receive(self, s):
		try:
			(self.To, self.From, self.Type, self.Size) = struct.unpack('iiii', s.recv(16))
		except:
			self.Size = 0
			self.Type = MT_NODATA

class Message:
	ClientID = 0

	def __init__(self, To = 0, From = 0, Type = MT_DATA, Data=""):
		self.Header = MsgHeader(To, From, Type, len(Data))
		self.Data = Data

	def Send(self, s):
		self.Header.Send(s)
		if self.Header.Size > 0:
			s.send(struct.pack(f'{self.Header.Size}s', self.Data.encode('cp866')))

	def Receive(self, s):
		self.Header.Receive(s)
		if self.Header.Size > 0:
			self.Data = struct.unpack(f'{self.Header.Size}s', s.recv(self.Header.Size))[0].decode('cp866')

	def SendAsClient(To, From, Type = MT_DATA, Data=""):
		HOST = 'localhost'
		PORT = 12435
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((HOST, PORT))
			m = Message(To, From, Type, Data)
			print("LogSendAsClientData: ", Data)
			if m.Header.From == m.Header.To:
				print("You can't send message to yoursef")
			else:
				m.Send(s)
				m.Receive(s)
				return m

	def SendMessage(To, Type = MT_DATA, Data=""):
		HOST = 'localhost'
		PORT = 12435
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((HOST, PORT))
			m = Message(To, Message.ClientID, Type, Data)
			if m.Header.From == m.Header.To:
				print("You can't send message to yoursef")
			else:
				m.Send(s)
				m.Receive(s)
				if m.Header.Type == MT_REST:
					Message.ClientID = m.Header.To
					print("REST server's id is  " + str(m.Header.To))
				return m