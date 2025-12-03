from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket

class ServerWorker:
	"""
	ServerWorker class to handle RTSP/RTP requests from a single client.
	Manages the RTSP state machine and RTP video streaming.
	"""
	SETUP = 'SETUP'
	PLAY = 'PLAY'
	PAUSE = 'PAUSE'
	TEARDOWN = 'TEARDOWN'
	
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2
	
	MAX_PAYLOAD_SIZE = 1400 # Max size for RTP payload (fragmentation threshold)
	
	clientInfo = {}
	
	def __init__(self, clientInfo):
		"""
		Initialize the ServerWorker.
		
		Args:
			clientInfo (dict): Dictionary containing client connection info (socket, address).
		"""
		self.clientInfo = clientInfo
		self.rtpSequenceNumber = 0
		
	def run(self):
		"""Start the ServerWorker thread to receive RTSP requests."""
		threading.Thread(target=self.recvRtspRequest).start()
	
	def recvRtspRequest(self):
		"""
		Receive RTSP request from the client.
		Continuously listens on the RTSP socket for commands.
		"""
		connSocket = self.clientInfo['rtspSocket'][0]
		while True:            
			try:
				data = connSocket.recv(256)
				if data:
					print("Data received:\n" + data.decode("utf-8"))
					self.processRtspRequest(data.decode("utf-8"))
				else:
					# Client closed connection
					break
			except Exception as e:
				print(f"RTSP Connection Error: {e}")
				break
		
		# Cleanup
		connSocket.close()
		if 'event' in self.clientInfo:
			self.clientInfo['event'].set()
	
	def processRtspRequest(self, data):
		"""
		Process RTSP request sent from the client.
		
		Args:
			data (str): The raw RTSP request string.
		"""
		# Get the request type
		request = data.split('\n')
		line1 = request[0].split(' ')
		requestType = line1[0]
		
		# Get the media file name
		filename = line1[1]
		
		# Get the RTSP sequence number 
		seq = request[1].split(' ')
		
		# Process SETUP request
		if requestType == self.SETUP:
			if self.state == self.INIT:
				# Update state
				print("processing SETUP\n")
				
				try:
					self.clientInfo['videoStream'] = VideoStream(filename)
					self.state = self.READY
				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])
				
				# Generate a randomized RTSP session ID
				self.clientInfo['session'] = randint(100000, 999999)
				
				# Send RTSP reply
				self.replyRtsp(self.OK_200, seq[1])
				
				# Get the RTP/UDP port from the last line
				try:
					self.clientInfo['rtpPort'] = request[2].split('client_port=')[1].split(';')[0].strip()
				except:
					print("Error parsing RTP port from: " + request[2])
					self.clientInfo['rtpPort'] = "0"
		
		# Process PLAY request 		
		elif requestType == self.PLAY:
			if self.state == self.READY:
				print("processing PLAY\n")
				self.state = self.PLAYING
				
				# Create a new socket for RTP/UDP
				self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				
				self.replyRtsp(self.OK_200, seq[1])
				
				# Create a new thread and start sending RTP packets
				self.clientInfo['event'] = threading.Event()
				self.clientInfo['worker']= threading.Thread(target=self.sendRtp) 
				self.clientInfo['worker'].start()
		
		# Process PAUSE request
		elif requestType == self.PAUSE:
			if self.state == self.PLAYING:
				print("processing PAUSE\n")
				self.state = self.READY
				
				self.clientInfo['event'].set()
			
				self.replyRtsp(self.OK_200, seq[1])
		
		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print("processing TEARDOWN\n")

			self.clientInfo['event'].set()
			
			self.replyRtsp(self.OK_200, seq[1])
			
			# Close the RTP socket
			self.clientInfo['rtpSocket'].close()
			
	def sendRtp(self):
		"""
		Send RTP packets over UDP.
		Reads frames from VideoStream, packetizes them (with fragmentation), and sends them.
		"""
		while True:
			self.clientInfo['event'].wait(0.025) # Wait 25ms (approx 40 FPS) - Balanced speed
			
			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet(): 
				break 
				
			data = self.clientInfo['videoStream'].nextFrame()
			if not data:
				# End of video, send EOS signal and stop
				print("End of stream, sending EOS and stopping...")
				try:
					address = self.clientInfo['rtspSocket'][1][0]
					port = int(self.clientInfo['rtpPort'])
					self.rtpSequenceNumber += 1
					# Send special EOS packet
					self.clientInfo['rtpSocket'].sendto(self.makeRtp(b'EOS', self.rtpSequenceNumber, 1),(address,port))
				except:
					print("Error sending EOS")
				break
				
			if data: 
				# frameNumber = self.clientInfo['videoStream'].frameNbr()
				try:
					address = self.clientInfo['rtspSocket'][1][0]
					port = int(self.clientInfo['rtpPort'])
					
					# Fragmentation Logic
					if len(data) > self.MAX_PAYLOAD_SIZE:
						# Split data into chunks
						chunks = [data[i:i + self.MAX_PAYLOAD_SIZE] for i in range(0, len(data), self.MAX_PAYLOAD_SIZE)]
						for i, chunk in enumerate(chunks):
							self.rtpSequenceNumber += 1
							# Set marker to 1 only for the last chunk
							marker = 1 if i == len(chunks) - 1 else 0
							self.clientInfo['rtpSocket'].sendto(self.makeRtp(chunk, self.rtpSequenceNumber, marker),(address,port))
					else:
						self.rtpSequenceNumber += 1
						marker = 1
						self.clientInfo['rtpSocket'].sendto(self.makeRtp(data, self.rtpSequenceNumber, marker),(address,port))
						
				except:
					print("Connection Error")
					#print('-'*60)
					#traceback.print_exc(file=sys.stdout)
					#print('-'*60)

	def makeRtp(self, payload, frameNbr, marker=0):
		"""
		RTP-packetize the video data.
		
		Args:
			payload (bytes): The video data (or chunk).
			frameNbr (int): The sequence number.
			marker (int): The marker bit (1 for last chunk of frame, 0 otherwise).
			
		Returns:
			bytes: The encoded RTP packet.
		"""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		# marker is passed as argument
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0 
		
		rtpPacket = RtpPacket()
		
		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
		
		return rtpPacket.getPacket()
		
	def replyRtsp(self, code, seq):
		"""
		Send RTSP reply to the client.
		
		Args:
			code (int): The status code (200, 404, 500).
			seq (str): The sequence number of the request being replied to.
		"""
		if code == self.OK_200:
			#print("200 OK")
			reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq + '\nSession: ' + str(self.clientInfo['session'])
			connSocket = self.clientInfo['rtspSocket'][0]
			connSocket.send(reply.encode())
		
		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print("404 NOT FOUND")
		elif code == self.CON_ERR_500:
			print("500 CONNECTION ERROR")
