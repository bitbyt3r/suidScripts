url="http://monitor.cs.umbc.edu/suid/"

setuid = 1 << 0
setgid = 1 << 1
rules = {"./bar": setuid + setgid,
	"./foo": setuid,
	"./baz": setgid,
	}
