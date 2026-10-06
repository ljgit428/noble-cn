import struct
p = r"F:\steam\steamapps\common\Noble Demo\Noble_Data\globalgamemanagers"
f = open(p,'rb')
hdr = f.read(48)
print("metadata size:", struct.unpack(">I", hdr[0:4])[0])
ver = struct.unpack(">I", hdr[4:8])[0]
print("format version:", ver)
data = hdr[8:8+32]
print("unity version:", data.split(b"\x00")[0].decode())
p2 = r"F:\steam\steamapps\common\Noble Demo\Noble_Data\level0"
f2 = open(p2,'rb'); h2 = f2.read(48)
print("level0 ver:", struct.unpack(">I", h2[4:8])[0], h2[8:40].split(b"\x00")[0].decode())
