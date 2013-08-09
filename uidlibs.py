import stat
class IntendedPermission:
	def __init__(self, setuid=False, setgid=False):
		self.setuid, self.setgid = setuid, setgid
	def __str__(self):
		if self.setuid:
			if self.setgid:
				return "setuid and setgid"
			return "setuid"
		if self.setgid:
			return "setgid"
		return "not setid"
	def perm(self, mode):
		if self.setuid: mode = mode | stat.S_ISUID
		else: mode = mode & ~stat.S_ISUID
		if self.setgid: mode = mode | stat.S_ISGID
		else: mode = mode & ~stat.S_ISGID
		return mode
class Permission:
	def __init__(self, mode):
		self.mode = mode
	def __str__(self):
		return ''.join([
			(stat.S_IRUSR & self.mode) and "r" or "-",
			(stat.S_IWUSR & self.mode) and "w" or "-",
			(stat.S_IXUSR & self.mode) and ((stat.S_ISUID & self.mode) and "s" or "x") or ((stat.S_ISUID & self.mode) and "S" or "-"),
			(stat.S_IRGRP & self.mode) and "r" or "-",
			(stat.S_IWGRP & self.mode) and "w" or "-",
			(stat.S_IXGRP & self.mode) and ((stat.S_ISGID & self.mode) and "s" or "x") or ((stat.S_ISGID & self.mode) and "S" or "-"),
			(stat.S_IROTH & self.mode) and "r" or "-",
			(stat.S_IWOTH & self.mode) and "w" or "-",
			(stat.S_IXOTH & self.mode) and ((stat.S_ISVTX & self.mode) and "t" or "x") or ((stat.S_ISVTX & self.mode) and "T" or "-"),
			])