from tkinter import *
import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os, time, queue, io

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	"""
	Client class for RTSP/RTP Video Streaming.
	Handles the GUI, RTSP control connection, and RTP data reception.
	"""
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		"""
		Initialize the Client.
		
		Args:
			master (Tk): The root Tkinter widget.
			serveraddr (str): IP address of the server.
			serverport (int): Port number of the server (RTSP).
			rtpport (int): Port number for RTP data reception.
			filename (str): Name of the video file to stream.
		"""
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		
		# Statistics variables
		self.totalBytes = 0
		self.startTime = 0
		self.totalPackets = 0
		self.lostPackets = 0
		self.expectedSeqNum = 0
		
		# Buffering variables
		self.frameBuffer = queue.Queue()
		self.BUFFER_THRESHOLD = 10 # Pre-buffer 10 frames for low latency
		self.buffering = True
		self.playEvent = None
		
		# Reassembly buffer for HD frames
		self.currentFrame = bytearray()
		self.lastSeqNum = -1
		self.discardingFrame = False
		
	def createWidgets(self):
		"""Build the GUI components (Buttons and Label)."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		# Use a placeholder image to set initial size (16:9 aspect ratio)
		self.placeholder = ImageTk.PhotoImage(Image.new("RGB", (640, 360), "black"))
		self.label = Label(self.master, image=self.placeholder)
		self.label.image = self.placeholder # Keep reference to prevent garbage collection
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def setupMovie(self):
		"""
		Handler for Setup button.
		Sends SETUP request to the server.
		"""
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)
	
	def exitClient(self):
		"""
		Handler for Teardown button.
		Sends TEARDOWN request and closes the application.
		"""
		self.sendRtspRequest(self.TEARDOWN)		
		self.master.destroy() # Close the gui window
		try:
			os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video
		except OSError:
			pass

	def pauseMovie(self):
		"""
		Handler for Pause button.
		Sends PAUSE request to the server.
		"""
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)
	
	def playMovie(self):
		"""
		Handler for Play button.
		Starts RTP listening thread and sends PLAY request.
		"""
		if self.state == self.READY:
			# Create a new thread to listen for RTP packets
			threading.Thread(target=self.listenRtp).start()
			self.playEvent = threading.Event()
			self.playEvent.clear()
			self.sendRtspRequest(self.PLAY)
			
			# Reset statistics when playing starts
			self.startTime = time.time()
			self.totalBytes = 0
			self.totalPackets = 0
			self.lostPackets = 0
			self.expectedSeqNum = 0
			self.currentFrame = bytearray()
			
			# Start buffer consumer loop (GUI thread safe)
			self.buffering = True
			# self.consumeBuffer() # Moved to parseRtspReply to ensure state is PLAYING
	
	def consumeBuffer(self):
		"""
		Consume frames from the buffer and update the GUI.
		Implements client-side buffering and adaptive timing for smooth playback.
		"""
		if self.state == self.PLAYING:
			if self.buffering:
				# Check if buffer has enough frames to start playback
				if self.frameBuffer.qsize() >= self.BUFFER_THRESHOLD:
					self.buffering = False
					print("Buffering Complete. Starting Playback.")
				else:
					# Check again in 10ms
					self.master.after(10, self.consumeBuffer)
					return
			
			if not self.buffering:
				if self.frameBuffer.empty():
					self.buffering = True
					print("Buffer Empty. Buffering...")
					# Check again in 10ms
					self.master.after(10, self.consumeBuffer)
					return
				
				try:
					startTime = time.time()
					
					# Frame Skipping Logic
					# If buffer has too many frames (>15), skip the oldest ones to catch up.
					# This prevents "slow motion" effect when decoding is slower than receiving.
					while self.frameBuffer.qsize() > 15:
						self.frameBuffer.get(block=False)
						print("Skipping frame to catch up...")
					
					frameData = self.frameBuffer.get(block=False)
					self.updateMovie(frameData)
					
					# Adaptive Timing: Adjust sleep time based on processing time
					elapsed = (time.time() - startTime) * 1000 # ms
					delay = max(1, int(33 - elapsed)) # Target 33ms (30 FPS)
					
					self.master.after(delay, self.consumeBuffer)
				except queue.Empty:
					self.master.after(10, self.consumeBuffer)
	
	def listenRtp(self):		
		"""
		Listen for RTP packets from the server.
		Handles packet reception, statistics calculation, and frame reassembly.
		"""
		while True:
			try:
				data = self.rtpSocket.recv(20480) # Receive up to 20KB
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data)
					
					currFrameNbr = rtpPacket.seqNum()
					
					# Calculate Statistics
					# 1. Data Rate
					self.totalBytes += len(data)
					elapsedTime = time.time() - self.startTime
					if elapsedTime > 0:
						dataRate = (self.totalBytes * 8) / elapsedTime / 1000 # kbps
					else:
						dataRate = 0
						
					# 2. Packet Loss
					if self.expectedSeqNum > 0: # Ignore the very first packet check
						if currFrameNbr > self.expectedSeqNum:
							loss = currFrameNbr - self.expectedSeqNum
							self.lostPackets += loss
							print("-" * 20)
							print(f"Packet Loss Event: Expected {self.expectedSeqNum}, Got {currFrameNbr}, Lost {loss}")
					
					self.totalPackets += 1
					# Avoid division by zero
					if (self.totalPackets + self.lostPackets) > 0:
						lossRate = (self.lostPackets / (self.totalPackets + self.lostPackets)) * 100
					else:
						lossRate = 0
					
					self.expectedSeqNum = currFrameNbr + 1
					
					# Print Stats (Throttle to avoid console blocking)
					if currFrameNbr % 100 == 0:
						print(f"Seq: {currFrameNbr} | Rate: {dataRate:.2f} kbps | Loss: {lossRate:.2f}%")
										
					# Reassembly Logic
					# Check for sequence gap
					if self.lastSeqNum != -1 and currFrameNbr != self.lastSeqNum + 1:
						# Packet loss detected!
						# If we were building a frame, it's now corrupted. Discard it.
						if len(self.currentFrame) > 0:
							print(f"Packet loss detected (Expected {self.lastSeqNum+1}, Got {currFrameNbr}). Discarding corrupted frame.")
							self.currentFrame = bytearray()
						self.discardingFrame = True
					
					self.lastSeqNum = currFrameNbr
					
					if self.discardingFrame:
						if rtpPacket.marker():
							# End of the bad frame. Reset flag and get ready for next frame.
							self.discardingFrame = False
						return # Ignore this packet
					
					if len(self.currentFrame) + len(rtpPacket.getPayload()) > 5000000: # 5MB limit
						self.currentFrame = bytearray()
						print("Frame buffer overflow, clearing.")
						self.discardingFrame = True # Start discarding until next marker
						return
						
					self.currentFrame.extend(rtpPacket.getPayload())
					
					if rtpPacket.marker():
						# Frame complete (Marker bit set)
						# Put frame data (bytes) into buffer
						self.frameBuffer.put(self.currentFrame)
						# Reset buffer
						self.currentFrame = bytearray()
						
			except:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.playEvent.isSet(): 
					break
				
				# Upon receiving ACK for TEARDOWN request,
				# close the RTP socket
				if self.teardownAcked == 1:
					self.rtpSocket.shutdown(socket.SHUT_RDWR)
					self.rtpSocket.close()
					break
					
	def writeFrame(self, data):
		"""
		Write the received frame to a temp image file. 
		
		Args:
			data (bytes): The image data.
			
		Returns:
			str: The name of the cache file.
		"""
		cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(cachename, "wb")
		file.write(data)
		file.close()
		
		return cachename
	
	def updateMovie(self, imageData):
		"""
		Update the image file as video frame in the GUI.
		
		Args:
			imageData (bytes): The raw image data (JPEG).
		"""
		try:
			photo = ImageTk.PhotoImage(Image.open(io.BytesIO(imageData)))
			self.label.configure(image = photo) 
			self.label.image = photo
		except:
			print("Error updating movie frame")
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.rtspSocket.connect((self.serverAddr, self.serverPort))
		except:
			tkMessageBox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
	
	def sendRtspRequest(self, requestCode):
		"""
		Send RTSP request to the server.
		
		Args:
			requestCode (int): The type of request (SETUP, PLAY, PAUSE, TEARDOWN).
		"""	
		
		# Setup request
		if requestCode == self.SETUP and self.state == self.INIT:
			threading.Thread(target=self.recvRtspReply).start()
			# Update RTSP sequence number.
			# Increment the sequence number for each new request
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			# Format: SETUP filename RTSP/1.0
			# CSeq: sequence_number
			# Transport: RTP/AVP;unicast;client_port=rtp_port
			request = "SETUP " + str(self.fileName) + " RTSP/1.0\n" + \
					  "CSeq: " + str(self.rtspSeq) + "\n" + \
					  "Transport: RTP/AVP;unicast;client_port=" + str(self.rtpPort)
			
			# Keep track of the sent request.
			# Store the request type to handle the response correctly
			self.requestSent = self.SETUP
		
		# Play request
		elif requestCode == self.PLAY and self.state == self.READY:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			# Format: PLAY filename RTSP/1.0
			# CSeq: sequence_number
			# Session: session_id
			request = "PLAY " + str(self.fileName) + " RTSP/1.0\n" + \
					  "CSeq: " + str(self.rtspSeq) + "\n" + \
					  "Session: " + str(self.sessionId)
			
			# Keep track of the sent request.
			self.requestSent = self.PLAY
		
		# Pause request
		elif requestCode == self.PAUSE and self.state == self.PLAYING:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			# Format: PAUSE filename RTSP/1.0
			# CSeq: sequence_number
			# Session: session_id
			request = "PAUSE " + str(self.fileName) + " RTSP/1.0\n" + \
					  "CSeq: " + str(self.rtspSeq) + "\n" + \
					  "Session: " + str(self.sessionId)
			
			# Keep track of the sent request.
			self.requestSent = self.PAUSE
			
		# Teardown request
		elif requestCode == self.TEARDOWN and not self.state == self.INIT:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			# Format: TEARDOWN filename RTSP/1.0
			# CSeq: sequence_number
			# Session: session_id
			# NOTE: 
			# - Must insert the Session header.
			# - Must NOT put the Transport header.
			request = "TEARDOWN " + str(self.fileName) + " RTSP/1.0\n" + \
					  "CSeq: " + str(self.rtspSeq) + "\n" + \
					  "Session: " + str(self.sessionId)
			
			# Keep track of the sent request.
			self.requestSent = self.TEARDOWN
		else:
			return
		
		# Send the RTSP request using rtspSocket.
		# Encode the string to bytes before sending
		self.rtspSocket.send(request.encode())
		
		print('\nData sent:\n' + request)
	
	def recvRtspReply(self):
		"""
		Receive RTSP reply from the server.
		Reads the server's response and parses it.
		"""
		while True:
			reply = self.rtspSocket.recv(1024)
			
			if reply: 
				self.parseRtspReply(reply.decode("utf-8"))
			
			# Close the RTSP socket upon requesting Teardown
			if self.requestSent == self.TEARDOWN:
				self.rtspSocket.shutdown(socket.SHUT_RDWR)
				self.rtspSocket.close()
				break
	
	def parseRtspReply(self, data):
		"""
		Parse the RTSP reply from the server.
		
		Args:
			data (str): The RTSP reply string.
		"""
		lines = data.split('\n')
		seqNum = int(lines[1].split(' ')[1])
		
		# Process only if the server reply's sequence number is the same as the request's
		if seqNum == self.rtspSeq:
			session = int(lines[2].split(' ')[1])
			# New RTSP session ID
			if self.sessionId == 0:
				self.sessionId = session
			
			# Process only if the session ID is the same
			if self.sessionId == session:
				if int(lines[0].split(' ')[1]) == 200: 
					if self.requestSent == self.SETUP:
						# Update RTSP state.
						# Transition state to READY after successful SETUP
						self.state = self.READY
						
						# Open RTP port.
						self.openRtpPort() 
					elif self.requestSent == self.PLAY:
						# Transition state to PLAYING after successful PLAY
						self.state = self.PLAYING
						
						# Start buffer consumer loop now that state is PLAYING
						self.consumeBuffer()
					elif self.requestSent == self.PAUSE:
						# Transition state to READY after successful PAUSE
						self.state = self.READY
						
						# The play thread exits. A new thread is created on resume.
						self.playEvent.set()
					elif self.requestSent == self.TEARDOWN:
						# Transition state to INIT after successful TEARDOWN
						self.state = self.INIT
						
						# Flag the teardownAcked to close the socket.
						self.teardownAcked = 1 
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		# Create a new datagram socket to receive RTP packets from the server
		# SOCK_DGRAM indicates UDP
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# Set the timeout value of the socket to 0.5sec
		self.rtpSocket.settimeout(0.5)
		
		# Increase Receive Buffer Size for HD Video (5MB)
		self.rtpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 5 * 1024 * 1024)
		
		try:
			# Bind the socket to the address using the RTP port given by the client user
			# self.state is already set, so we can bind
			self.rtpSocket.bind(("", self.rtpPort))
		except:
			tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		self.pauseMovie()
		if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
			self.exitClient()
		else: # When the user presses cancel, resume playing.
			self.playMovie()
