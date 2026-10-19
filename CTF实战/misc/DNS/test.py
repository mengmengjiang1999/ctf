from scapy.all import *
pks= rdpcap("./ezDNS.pcap")

# pr = PcapReader("./ezDNS.pcap")
# pkt = pr.read_packet()


bs =[]

for i in range(0,1000):
    pkt = pks[i]

    if int(pkt.proto)==17:
        hexdump(pkt)
        b=raw(pkt)
        bs.append(b[42])
        bs.append(b[43])
        print(hex(b[42]))
        print(hex(b[43]))



# pkt=pks[23]
# print(pkt)
# pkt.show()
# print(pkt.proto)


# # print("11111")
# pkthex=hexdump(pkt)
# print("11111")
# b=raw(pkt)
# # pktstr=str(pkt)
# print(b)
# # export_object(pkt)

# print(len(b))
# print(b[42])
# print(hex(b[42]))
# print(hex(b[43]))

