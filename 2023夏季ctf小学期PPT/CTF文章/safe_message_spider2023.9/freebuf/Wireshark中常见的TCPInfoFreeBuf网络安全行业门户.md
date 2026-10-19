## 1\. TCP out-of-order segment

TCP存在问题。

Wireshark判断TCP out-of-order是基于TCP包中SEQ number并非期望收到的下一个SEQ number，则判断为out-of-order。因此，出现TCP out-of-order时，很大可能是TCP存在乱序或丢包，导致接收端的seq number不连续。

如下图，第4包数据，在客户端已经收到服务端的SYN ACK后，服务端再次发送了SYN ACK，wireshark将此包标记为out-of-order。

![](https://image.3001.net/images/20210808/1628429504_610fdcc02a467109cc4f0.png!small)

如下图，第7包数据，本应收到seq
number为1366882的TCP包，但却收到了1044834的包，这包数据应该是晚到了，因此wireshark标记为out-of-order。

![](https://image.3001.net/images/20210808/1628429535_610fdcdfcaa250a7ae527.png!small)

如果抓包中出现大量的out-of-order包，则说明网络存在较大的TCP乱序或丢包。

## 2\. TCP Previous segment not captured

前一个TCP分段没有抓到。

在TCP连接建立的时候，SYN包里面会把彼此TCP最大的报文段长度，即MSS标志，一般都是1460.如果发送的包比最大的报文段长度长的话就要分片了，被分片出来的包，就会被标记了“TCP
segment of a reassembled PDU”，这些包分片存在同样的ack number，且每个分片的seq number不同。

![](https://image.3001.net/images/20210808/1628429561_610fdcf9c59f0c56acc2c.png!small)

这些分片正常应该是连续接收的，即前一个分片指示的next seq number即为下一个收到的分片的seq number。假如收到的下一个分片的seq
number与上一个比不连续的话，wireshark就会将该分片标记为TCP Previous segment not captured。如下图，ack
number为705的TCP包被分为多个分片发送，其中有一个长度为1408的分片没有被抓到。

![](https://image.3001.net/images/20210808/1628429609_610fdd29aef02dc9d15d1.png!small)

需要注意的是，前一个分片丢失，有可能是网络中确实丢失了，或者晚到了，也有可能是wireshark本身并没有抓到。

## 3\. TCP Spurious Retransmission

TCP虚假重传。

当抓到2次同一包数据时，wireshark判断网络发生了重传，同时，wireshark抓到初传包的反馈ack，因此wireshark判断初传包实际并没有丢失，因此称为虚假重传。基于wireshark的判断机制，如果抓包点在客户端的话，虚假重传一般为下行包，因为这时，客户端在收到服务端的下行包后发送反馈ack，并被wireshark抓到，但很有可能服务端未收到此反馈ack，RTO超时，触发服务端重传。如下图，红框内出现了2次虚假重传，其中绿色的两条为同一包数据，粉色的两条为同一包数据。

![](https://image.3001.net/images/20210808/1628429668_610fdd64741d5d30bd793.png!small)

## 4\. TCP Retransmission

TCP重传。

当抓到2次同一包数据时，wireshark判断发生了重传，同时wireshark没有抓到初传包的反馈ack，因此，wireshark判定重传有效，标记为TCP
Retransmission。基于软件的判定机制，如果抓包点在客户端的话，TCP重传一般为上行包，因为这时，客户端并没有收到服务端的反馈ack，无从知晓服务端是否收到了初传包，RTO超时后触发客户端重传。此时存在2种情况，即1）服务端收到了初传包，只是下发的反馈ack丢包，客户端没有收到；2）服务端没有收到初传包，因此也就没有下发反馈ack。对于第一种情况，如果抓包点在服务端的话，wireshark很有可能就会把来自客户端的重传包标记为TCP
Spurious Retransmission。

如下图，红线的TCP包为重传包，wireshark为该包添加了重传原因，是由于TRO超时导致，以及初传包序号45，并给出了当前的RTO超时时间。

![](https://image.3001.net/images/20210808/1628429693_610fdd7d0d39fdc0c70e6.png!small)

## 5\. TCP fast Retransmission

TCP快速重传。

TCP协议设定了快速重传机制以避免过多的慢启动对传输速率的影响。快速重传通过接收到3个或3个以上重复的ack反馈触发。快速重传不需要等待RTO超时。如下图。

325包，客户端向服务端反馈ack=133251，说明下一个期望收到服务端seq=133251的包；

326包，服务端向客户端发送了seq=135771的数据包，与客户端的期望不符，因此客户端在327包重传了ack=133251的包，再次申明期望收到seq=133251的包。Wireshark将重复ack标记为TCP
Dup ACK，#后边指明为第几次重传。

328包，服务端向客户端发送了seq=137031的数据包，仍然与客户端期望不符，客户端在329包再次重传ack=133251的包。

330包，服务端收到3次重复ack，触发快速重传，重传了seq=133251的TCP分片。

![](https://image.3001.net/images/20210808/1628429718_610fdd96b6dc56f2d11b3.png!small)

## 6\. TCP Dup ACK

重复ack。

当网络中存在乱序或者丢包时，将会导致接收端接收到的seq number不连续。此时接收端会向发送端回复重复ack，ack值为期望收到的下一个seq
number。重复ack数大于等于3次将会触发快速重传。如下图，

315包，客户端向服务端发送ack=126951的反馈，期望下一包收到seq=126951的TCP包。但下一包接收到的却是seq=128211的TCP包，由于seq不连续，wireshark将该报标记为TCP
Previous segment not captured。

317包，客户端向服务端重复发送ack=126951的包，第一次重发，#后边带1。

318包，客户端收到seq=126951的TCP包。

319包，截止到seq=129471的所有TCP包全部收到，因此客户端回复了ack=129471的反馈。

![](https://image.3001.net/images/20210808/1628429758_610fddbe0a75c547c3d57.png!small)

## 7\. TCP window update

TCP窗口更新。

当接收方的TCP window发生突变时，接收方通过TCP window update消息告知对方当前的接收窗口大小。如下图，TCP window
Update同时携带了反馈ack，ack序列号与前一个反馈ack序列号相同，但这并不是重复ack。

![](https://image.3001.net/images/20210808/1628429780_610fddd493f89aca81f98.png!small)

## 8\. TCP acked unseen segment

反馈ACK指向了一个未知的TCP片段。

这个意思是说ACK反馈的是一个wireshark上不存在的TCP包。很可能是wireshark漏抓了这个包，但却抓到了对端反馈的该报的ack包。如下图，标记为ack
unseen
segment的包反馈的ack=2721，看着像是反馈的seq=1361的包，但其实这个ack还反馈了seq=1的包，由于seq=1的包没有抓到，因此wireshark将反馈ack标记为ack
unseen
segment。从下面的图还可知，由于对端已经反馈了ack=2721，说明发端发送的seq=1的包，对端也收到了，只不过wireshark可能漏抓了而已。

![](https://image.3001.net/images/20210808/1628429887_610fde3fda32afa5e75bd.png!small)

## 9\. TCP ZeroWindow

TCP滑动窗口为0。

当发送端发包速率大于接收端的接收速率时，会造成接收端TCP window越来越小，当接收端在反馈ack时携带的window
size=0时，wireshark标记TCP Zero window。此时发送端将暂停发送数据，直到收到接收端window size!=0的标志。

![](https://image.3001.net/images/20210808/1628429910_610fde5642e62d0b946cb.png!small)

## 10\. TCP window full

TCP window满。

是指的发送端发送的数据已经达到的接受窗口的上限。发送端暂停发送，等待新的接收窗口的通告。

如下图，客户端向服务端发送的ack反馈，期望下一包收到的seq=288961，但接收窗口仅有960，服务端在收到ack后发送了960字节的数据，TCP
window full。注意，len=1004是整个IP包的长度，需要减去IP头44字节，即960字节。

![](https://image.3001.net/images/20210808/1628429930_610fde6a9f3440a498c92.png!small)

## 11\. TCP RST

TCP 重置。

是TCP协议结束异常连接的一种方式，通过flog中的reset=1标记。当TCP连接无法通过正常的4次挥手结束时，一方可以通过发送携带reset标志的TCP包结束TCP连接。

如下图，发送方通过2个TCP流发送数据，截图中，接收方首先向发送方反馈了TCP window=0，让发送方暂缓发送数据，之后紧接着发送了TCP
RST标记，释放了TCP连接。猜测可能接收方程序突然崩溃了，导致缓存区数据没法清空，之后接收方系统发送了TCP reset释放TCP连接。
![](https://image.3001.net/images/20210808/1628429952_610fde8071beea5b1ac4f.png!small)

