import collections
import math
import time

# Used to name columns in the lockout table
(streak, time_left) = range(2)

class LockoutTable(object):

	def __init__(self, attempt_limit, lockout_time_minutes):
		'''
		Parameters
		----------
		attempt_limit : int
			The max streak of failed attempts where an RFID tag or
			fingerprint is presented and the wrong PIN is entered.
			This is to prevent guessing the PIN via brute force.
		lockout_time_minutes : int
			The amount of time (in minutes) to block the RFID tag or
			fingerprint from further use once the incorrect streak reaches the attempt limit.
		'''
		self.attempt_limit = attempt_limit
		self.lockout_time = lockout_time_minutes * 60 # convert to seconds
		'''
		Maps credentials (ex. RFID UID) to a list with two values.
		The values correspond to
			current failed attempt streak, and
			remaining lockout time respectively.
		If a new credential is searched, return [0,0] by default.
		'''
		self.lockouts = collections.defaultdict(lambda : [0,0])
		# used to determine how much time has elapsed between time updates
		self.last_update_time = 0

	def get_lockout(self, credential):
		'''
		Returns
		-------
		(bool, int)
			bool - True if credential is currently locked out, else False
			int - Lockout time remaining in minutes (0 if the bool is False)
		'''
		lockout_time_left = self.lockouts[credential][time_left]
		return lockout_time_left > 0, int(math.ceil(lockout_time_left / 60.0))

	def failed_attempt(self, credential):
		row = self.lockouts[credential]
		row[streak] += 1
		if row[streak] >= self.attempt_limit:
			row[time_left] = self.lockout_time

	def reset_streak(self, credential):
		row = self.lockouts[credential]
		row[streak] = 0
		row[time_left] = 0

	def update_timers(self):
		time_elapsed = time.time() - self.last_update_time
		for credential in self.lockouts:
			row = self.lockouts[credential]
			if row[time_left] > 0:
				row[time_left] = max(0, row[time_left] - time_elapsed)
				if row[time_left] == 0:
					# lockout expired
					self.reset_streak(credential)
		self.last_update_time = time.time()