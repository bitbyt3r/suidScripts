#!/usr/bin/python
import os, stat, sys

OUTPUT_FILE = "./setuidconfig.py"

sidFiles = {}
skipDir = []

def checkFile(file):
  try:
    perms = os.stat(file)
    if bool(perms.st_mode & stat.S_ISUID) or bool(perms.st_mode & stat.S_ISGID):
      sidFiles[file] = (bool(perms.st_mode & stat.S_ISUID), bool(perms.st_mode & stat.S_ISGID))
  except OSError:
    print file, " is not a valid file."

def checkDir(arg, dirname, names):
  print "Checking:", dirname
  for i in skipDir:
    if i in dirname:
      print "Skipping", dirname, "Parent skipped."
      return
  if os.stat(dirname).st_dev == rootdev:
    for i in names:
      checkFile(os.path.join(dirname, i))
  else:
    skipDir.append(dirname)
    print "Skipping", dirname, "Not on root device."

def makeConfig(sidFiles):
  with open(OUTPUT_FILE, "w") as output:
    output.write("url=\"http://monitor.cs.umbc.edu/suid/\"\n\n")
    output.write("setuid = 1 << 0\nsetgid = 1 << 1\nrules = {")
    keys = list(sidFiles.keys())    

    output.write("\""+keys[0]+"\": ")
    if sidFiles[keys[0]][0] and sidFiles[keys[0]][1]:
      output.write("setuid + setgid,\n")
    elif sidFiles[keys[0]][0]:
      output.write("setuid,\n")
    elif sidFiles[keys[0]][1]:
      output.write("setgid,\n")

    for i in keys[1:]:
      output.write("\t\""+i+"\": ")
      if sidFiles[i][0] and sidFiles[i][1]:
        output.write("setuid + setgid,\n")
      elif sidFiles[i][0]:
        output.write("setuid,\n")
      elif sidFiles[i][1]:
        output.write("setgid,\n")
    output.write("\t}\n")

rootdev = os.stat("/").st_dev
os.path.walk("/", checkDir, None)
makeConfig(sidFiles)
