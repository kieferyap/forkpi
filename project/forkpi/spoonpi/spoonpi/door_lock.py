
class DoorLock(object):
	'''
	Dummy class for communicating with an electric door lock.
	'''

	def __init__(self):
		self.is_door_closed = True
		self.is_door_locked = True

	def unlock(self):
		# Unlock the door whether it is closed or not
		self.is_door_locked = False

	def lock(self):
		# Lock the door only when it is closed
		if self.is_door_closed:
			self.is_door_locked = True

	def door_was_opened(self):
		self.is_door_closed = False

	def door_was_closed(self):
		# Lock the door every time it is closed
		self.is_door_closed = True
		self.is_door_locked = True