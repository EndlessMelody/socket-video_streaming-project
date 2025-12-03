class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.frameNum = 0
		
	def nextFrame(self):
		"""Get next frame."""
		data = self.file.read(5) # Try to read 5 bytes
		if data: 
			try:
				framelength = int(data)
				# Read the current frame (custom format)
				data = self.file.read(framelength)
				self.frameNum += 1
			except ValueError:
				# Not a custom header, assume standard MJPEG (starts with 0xFF 0xD8)
				frame_data = bytearray(data)
				while True:
					# Read in chunks for performance (10KB)
					chunk = self.file.read(10240)
					if not chunk:
						break
					frame_data.extend(chunk)
					
					# Search for EOI (0xFF 0xD9)
					eoi_index = frame_data.find(b'\xff\xd9')
					if eoi_index != -1:
						# Found EOI!
						frame_end = eoi_index + 2
						data = bytes(frame_data[:frame_end])
						
						# Seek back if we read too much
						extra_bytes = len(frame_data) - frame_end
						if extra_bytes > 0:
							self.file.seek(-extra_bytes, 1)
						
						self.frameNum += 1
						return data
				
				# EOF reached
				data = bytes(frame_data)
				if data:
					self.frameNum += 1
		return data
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum

	def reset(self):
		"""Reset the video stream to the beginning."""
		self.file.seek(0)
		self.frameNum = 0