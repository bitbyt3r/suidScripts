#! /usr/bin/python
import urllib, os, stat, sys, setuidconfig
from uidlibs import IntendedPermission, Permission

if sys.hexversion <= 0x02040000: # only works for 2.3
	import sets
	set = sets.Set

Debug = False

fileperms, changedfiles = {}, []
for (k,v) in setuidconfig.rules.iteritems():
	fileperms[k] = IntendedPermission(v & setuidconfig.setuid, v & setuidconfig.setgid)
allowedsetid = set(fileperms.keys())

def fix(arg, dirname, fnames):
	global allowedsetid, changedfiles, rootdev
	f2d = [] # Files to remove from the list.  We need to iterate over all files before deleting any of them.
	modes = {}
	for i in range(len(fnames)):
		try:
			path = os.path.join(dirname, fnames[i])
			pstat = os.lstat(path)
			modes[fnames[i]] = pstat.st_mode
			# Skip other filesystems
			if pstat.st_dev != rootdev:
				if Debug:
					print "Removing %s because it is on a different fs" % (path)
				f2d.append(i)
			# Ignore zoneroots
			if path == "/zones":
				if Debug:
					print "Removing /zones"
				f2d.append(i)
		except OSError, e:
			print e
	# Now actually prune out the files we decided to skip before processing them
	f2d.sort()
	f2d.reverse()
	for index in f2d:
		del fnames[index]
	for f in fnames:
		try:
			# Ignore symlinks
			# 
			path = os.path.join(dirname, f)
			if stat.S_ISLNK(modes[f]):
				if Debug:
					print "Ignoring %s because it is a symlink" % (path)
				continue
			# If this file can have the setid bits configured, ensure it has the right ones set
			if path in allowedsetid:
				newmode = fileperms[path].perm(modes[f])
				if modes[f] != newmode:
					if Debug:
						print "Setting %s to have mode %s (%o -> %o)" % (path, fileperms[path], modes[f], newmode)
					changedfiles.append((path, Permission(modes[f]), Permission(newmode)))
					os.chmod(path, newmode)
			else:
				newmode = modes[f] & ~stat.S_ISUID & ~stat.S_ISGID
				if modes[f] != newmode:
					if Debug:
						print "Removing extra setid bits from %s (%o -> %o)" % (path, modes[f], newmode)
					changedfiles.append((path, Permission(modes[f]), Permission(newmode)))
					os.chmod(path, newmode)
		except OSError, e:
			print e

rootdev = os.stat("/").st_dev

os.path.walk("/", fix, None)

if Debug:
	sys.exit(0)

data = urllib.urlencode({"changed": ';'.join(["%s,%d,%d" % (f[0], f[1].mode, f[2].mode) for f in changedfiles])})
if len(changedfiles) > 0:
	u = urllib.urlopen(setuidconfig.url, data)

