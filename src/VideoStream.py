class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			file = open(filename, 'rb')
			self.data = file.read() # Load entire file into memory
			file.close()
		except:
			raise IOError
		self.frameNum = 0
		self.pos = 0 # Current position in the memory buffer
		
	def nextFrame(self):
		"""Get next frame from memory."""
		if self.pos < len(self.data):
			# Try to read 5 bytes for custom header
			header = self.data[self.pos : self.pos+5]
			if len(header) == 5:
				try:
					framelength = int(header)
					# Read the current frame (custom format)
					self.pos += 5
					frame_data = self.data[self.pos : self.pos+framelength]
					self.pos += framelength
					self.frameNum += 1
					return frame_data
				except ValueError:
					# Not a custom header, assume standard MJPEG (starts with 0xFF 0xD8)
					# Scan for EOI (0xFF 0xD9)
					eoi_index = self.data.find(b'\xff\xd9', self.pos)
					if eoi_index != -1:
						frame_end = eoi_index + 2
						frame_data = self.data[self.pos : frame_end]
						self.pos = frame_end
						self.frameNum += 1
						return frame_data
		return None
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum

	def reset(self):
		"""Reset the video stream to the beginning."""
		self.pos = 0
		self.frameNum = 0