import sys
from time import time
HEADER_SIZE = 12

class RtpPacket:	
	header = bytearray(HEADER_SIZE)
	
	def __init__(self):
		pass
		
	def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
		"""Encode the RTP packet with header fields and payload."""
		
		# Get the current timestamp in seconds
		timestamp = int(time())
		
		# Initialize the header as a bytearray of size 12 (HEADER_SIZE)
		header = bytearray(HEADER_SIZE)
		
		#--------------
		# TO COMPLETE
		#--------------
		# Fill the header bytearray with RTP header fields
		
		# Header[0] contains: Version (2 bits), Padding (1 bit), Extension (1 bit), CC (4 bits)
		# We shift the version 6 bits to the left (V P X CC)
		# We shift padding 5 bits to the left
		# We shift extension 4 bits to the left
		# CC is the last 4 bits
		header[0] = (version << 6) | (padding << 5) | (extension << 4) | cc
		
		# Header[1] contains: Marker (1 bit), Payload Type (7 bits)
		# We shift the marker 7 bits to the left (M PT)
		# Payload Type (pt) is the last 7 bits
		header[1] = (marker << 7) | pt
		
		# Header[2] and Header[3] contain the Sequence Number (16 bits)
		# Header[2] gets the upper 8 bits (shift right by 8)
		header[2] = (seqnum >> 8) & 0xFF
		# Header[3] gets the lower 8 bits (mask with 0xFF)
		header[3] = seqnum & 0xFF
		
		# Header[4] to Header[7] contain the Timestamp (32 bits)
		# Header[4] gets bits 24-31
		header[4] = (timestamp >> 24) & 0xFF
		# Header[5] gets bits 16-23
		header[5] = (timestamp >> 16) & 0xFF
		# Header[6] gets bits 8-15
		header[6] = (timestamp >> 8) & 0xFF
		# Header[7] gets bits 0-7
		header[7] = timestamp & 0xFF
		
		# Header[8] to Header[11] contain the SSRC (32 bits)
		# Header[8] gets bits 24-31
		header[8] = (ssrc >> 24) & 0xFF
		# Header[9] gets bits 16-23
		header[9] = (ssrc >> 16) & 0xFF
		# Header[10] gets bits 8-15
		header[10] = (ssrc >> 8) & 0xFF
		# Header[11] gets bits 0-7
		header[11] = ssrc & 0xFF
		
		# Store the constructed header in the object's header attribute
		self.header = header
		
		# Get the payload from the argument
		# Store the payload (video data) in the object's payload attribute
		self.payload = payload
		
	def decode(self, byteStream):
		"""Decode the RTP packet."""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]
	
	def version(self):
		"""Return RTP version."""
		return int(self.header[0] >> 6)
	
	def seqNum(self):
		"""Return sequence (frame) number."""
		seqNum = self.header[2] << 8 | self.header[3]
		return int(seqNum)
	
	def timestamp(self):
		"""Return timestamp."""
		timestamp = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7]
		return int(timestamp)
	
	def payloadType(self):
		"""Return payload type."""
		pt = self.header[1] & 127
		return int(pt)
	
	def getPayload(self):
		"""Return payload."""
		return self.payload
		
	def getPacket(self):
		"""Return RTP packet."""
		return self.header + self.payload