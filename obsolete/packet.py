from collections import namedtuple

Packet = namedtuple('Packet', [
	'timestamp', # unix epoch
	'size_in_bytes',
	'src_address',
	'src_port',
	'dst_address',
	'dst_port',
	'seq',
	'ack',
	'flags'
])