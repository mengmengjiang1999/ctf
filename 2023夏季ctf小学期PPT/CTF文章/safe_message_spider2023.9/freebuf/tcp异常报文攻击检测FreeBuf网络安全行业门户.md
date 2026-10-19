# 简介

TCP报文标志位包括：

URG

ACK

PSH

RST

SYN

FIN

攻击者通过发送非法TCP flag组合的报文对主机造成危害。

# 检测异常

检查TCP报文的各个标志位URG、ACK、PSH、RST、SYN、FIN，如果标志位异常，则认为是TCP异常报文。内置规则将所有TCP异常报文全部丢弃，记录攻击日志。异常检测如下：

Syn option字段不完整（syn-64）

6个标志位全为1。

6个标志位全为0。

SYN和FIN位同时为1。

SYN和RST位同时为1。

FIN和RST位同时为1。

PSH、FIN和URG位同时为1。

仅FIN位为1。

仅URG位为1。

仅PSH位为1。

SYN/RST/FIN标记位为1的分片报文。

带有载荷的SYN、SYN-ACK报文。

