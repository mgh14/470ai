import telnetlib

HOST = "localhost"
port = 57240

tn = telnetlib.Telnet(HOST, port)

#tn.open(HOST, port)

print tn.read_until("\n")
tn.write("agent 1\n")

while True:
	tn.write("shoot 0\n")
	print tn.expect(["ok\n","fail\n"], 3)[2]