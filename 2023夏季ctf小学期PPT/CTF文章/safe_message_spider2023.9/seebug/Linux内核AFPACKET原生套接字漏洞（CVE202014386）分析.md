**作者：启明星辰ADLab  
原文链接：<https://mp.weixin.qq.com/s/uv3BiznUCUy8do_ullnXUw>**

### 一、漏洞背景

近日，Openwall社区上公开了一个Linux内核AF_PACKET原生套接字内存破坏漏洞。根据细节描述，该漏洞出现在net/packet/af_packet.c中，由整数溢出导致越界写，可以通过它进行权限提升。该漏洞危害评级为高，编号为CVE-2020-14386。

### 二、受影响产品和缓解措施

**1、受影响产品**

该漏洞影响Linux发行版高于4.6的内核版本，包括：

  * Ubuntu Bionic (18.04) and newer
  * Debian 9
  * Debian 10
  * CentOS 8/RHEL 8

**2、缓解措施**

（1）修补系统

上游内核补丁如下：

<https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=acf69c946233259ab4d64f8869d4037a198c7f06>

（2）关闭CAP_NET_RAW功能 针对RHEL8，具体关闭步骤如下：

# echo "user.max_user_namespaces=0" > /etc/sysctl.d/userns.conf

# sysctl -p /etc/sysctl.d/userns.conf

（3）针对一些受影响的容器产品，同样采取关闭CAP_NET_RAW功能进行缓解。  
Kubernetes
Pod安全策略：配置Pod安全策略以删除运行容器中的CAP_NET_RAW功能，参考链接：<https://cloud.google.com/kubernetes-engine/docs/security-bulletins>

### 三、相关概念

**1、AF_PACKET套接字**

网络协议栈中，原始套接字是一个特殊的套接字类型，从实现上可以分为两类，一类为链路层原始套接字；另一类为网络层原始套接字。链路层原始套接字可直接用于接收和发送链路层的MAC帧，在发送时需要调用者自行构造和封装MAC首部。链路层原始套接字调用socket()函数创建。第一个参数指定地址簇类型为AF_PACKET，第二个参数套接字类型为SOCK_RAW或SOCK_DGRAM，当类型指定为SOCK_RAW时，套接字接收和发送的数据都是从MAC首部开始的。在发送时需要由调用者从MAC首部开始构造和封装报文数据。

**2、PACKET_MMAP**

仅依靠AF_PACKET过滤数据包是非常低效的，内核又提供了PACKET_MMAP支持。PACKET_MMAP在内核空间中分配一块环形内核缓冲区，用户空间通过mmap将该内核缓冲区映射出来。收到的数据包拷贝到环形内核缓冲区中，用户层可以直接操作数据，通过内核空间和用户空间共享的缓冲区起到减少数据拷贝的作用，提高处理效率。

### 四、PACKET_MMAP实现过程

通过setsockopt()函数设置环形缓冲区，option参数设置为PACKET_RX_RING或PACKET_TX_RING。为了方便内核与用户层管理和交互环形缓冲区中的数据帧，内核定义了TPACKET_HEADER结构体，该结构体存储着一些元信息如套接字地址信息、时间戳以及环形缓冲区管理信息等。如果通过setsockopt()函数设置了PACKET_VNET_HDR选项，还需添加一个virtio_net_hdr结构体。一个数据帧包含两个部分，第一部分为TPACKET_HEADER，第二部分为Data，而且要保证页面对齐，如下图所示：

![](https://images.seebug.org/content/images/2020/09/548a80c1-64cf-4cbb-bb9d-cdb4e2a8bf53.png-w331s)

目前TPACKET_HEADER存在三个版本，每个版本长度略有不同。对于v1和v2，收发环形缓冲区用tpacket_req结构体管理，该结构体包含四个数据域：分别为内存块的大小和数量、每个数据帧的大小和数据帧总数。如下图所示：

![](https://images.seebug.org/content/images/2020/09/1b940e84-6e10-4b34-8acb-687b64214e20.png-w331s)

捕获的frame被划分为多个block，每个block是一块物理上连续的内存区域，有tp_block_size/tp_frame_size个frame，block的总数是tp_block_nr。例如，tp_block_size
= 4096，tp_frame_size = 2048，tp_block_nr = 4，tp_frame_nr = 8。得到的缓冲区结构如下图所示：

![](https://images.seebug.org/content/images/2020/09/c24d74b0-a520-44c6-aeac-d9d377e55fb1.png-w331s)

每个frame必须放在一个block中，每个block保存整数个frame，也就是说一个frame不能跨越两个block。在用户层映射环形缓冲区可以直接使用mmap()函数。虽然环形缓冲区在内核中是由多个block组成的，但是映射后它们在用户空间中是连续的。

### 五、漏洞分析

该漏洞具体出现在tpacket_rcv()函数中，该函数是基于PACKET_MMAP的数据包接收函数。具体功能实现如下代码所示：

![](https://images.seebug.org/content/images/2020/09/feb9f6fe-80a4-43b7-b605-757e8592d52a.png-w331s)

行2226到行2228，如果sk_type为SOCK_DGRAM，表示不需要自行构造MAC首部，由内核填充，则macoff等于netoff，大小为TPACKET_ALIGN(tp_hdr_len)
+ 16 +
tp_reserve。如果sk_type为SOCK_RAW，则进入行2230，表示需要自行构造MAC首部。行2231到行2233，首先计算netoff，大小为TPACKET_ALIGN(tp_hdrlen
+(maclen < 16 ? 16 : maclen)) +
tp_reserve。行2234到行2237，如果设置了PACKET_VNET_HDR选项，还需加上一个virtio_net_hdr结构体的大小，然后设置do_vnet为真。行2238，计算macoff。

由于macoff、netoff以及maclen被定义为unsigned short类型，最大值为0xffff。而tp_reserve被定义为unsigned
int类型，最大值为0xffffffff，而且大小可以通过setsockopt()函数进行设置，如下代码所示：

![](https://images.seebug.org/content/images/2020/09/6765eba1-489f-455a-bdaa-5880baa8df9d.png-w331s)

因此，在计算netoff时，可以通过控制tp_reserve造成整数溢出，进而计算出错误的macoff。当执行到如下代码时：

![](https://images.seebug.org/content/images/2020/09/363eb5cb-a074-4394-ada7-4cd5fa144a7f.png-w331s)

行2287，调用virtio_net_hdr_from_skb()函数从sk_buff中拷贝数据，该函数第二个参数为h.raw + macoff –
sizeof(struct
virtio_net_hdr)，h.raw为tpacket_rcv_uhdr类型的指针，指向环形缓冲区的frame，由于macoff是可控的，可以让maoff小于sizeof(struct
virtio_net_hdr)，导致向前越界写，最多可写入sizeof(struct
virtio_net_hdr)个字节。根据提供的PoC，调试代码如下图所示：

![](https://images.seebug.org/content/images/2020/09/e8df2e70-536c-4ad3-8262-dad2d8d969eb.png-w331s)

rdx中存放着TPACKET_ALIGN(tp_hdrlen +(maclen < 16 ? 16 :
maclen))，大小为0x50。rbp+0x4e4处存放着po->tp_reserve，大小为0x0000ffb4。相加后，整数上溢后，rdx为0x0004。当执行到越界访问时，具体如下：

![](https://images.seebug.org/content/images/2020/09/0a379f70-4115-410d-9bb6-45d5d93ad346.png-w331s)

R9存放着h.raw指针，rdx存放着macoff，virtio_net_hdr结构体大小为0xa。如下图所示：

![](https://images.seebug.org/content/images/2020/09/e8d7372b-e8ef-48be-8c05-b94cd0e92f64.png-w331s)
发生内存访问错误，造成系统崩溃。

### 六、参考链接

1、<https://blog.csdn.net/sinat_20184565/article/details/82788387>  
2、<https://www.openwall.com/lists/oss-security/2020/09/03/3>  
3、<https://elixir.bootlin.com/linux/v5.6/source/Documentation/networking/packet_mmap.txt>  
4、<https://sysdig.com/blog/cve-2020-14386-falco/>  
5、<https://bugzilla.redhat.com/show_bug.cgi?id=1875699#c9>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1348/>

