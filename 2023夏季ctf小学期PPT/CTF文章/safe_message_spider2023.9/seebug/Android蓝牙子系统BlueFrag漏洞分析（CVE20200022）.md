**作者：启明星辰ADLab  
公众号：<https://mp.weixin.qq.com/s/MgttHkorVd5UrW1Cnlc5Xw>**

## 一、漏洞背景

2020年2月，Android安全公告中披露并修复了一个严重漏洞，漏洞编号为CVE-2020-0022，又称BlueFrag，可影响Android蓝牙子系统。该漏洞是一个远程代码执行漏洞，出现在Bluedroid蓝牙协议栈的HCI层，当无线模块处于活动状态时，攻击者可以利用蓝牙守护程序提升权限进而在设备上执行代码。该漏洞影响Android
Oreo（8.0和8.1）、Pie（9），但无法在Android 10上进行利用，仅能触发DoS攻击。

## 二、协议简介

### 2.1 HCI

HCI
层位于蓝牙协议栈高层协议和低层协议之间，提供了对基带控制器和链路管理器的命令以及访问蓝牙硬件的统一接口方法，其接口适用于BR/EDR控制器、BR/EDR/LE控制器、LE控制器、AMP控制器，与底层的结构关系如下图：

![](https://images.seebug.org/content/images/2020/02/325369a0-4dae-4be0-8cee-ac9ef5d2f568.png-w331s)

主机系统上的HCI驱动程序和控制器中的HCI层之间会存在中间层，
这些中间层即是主机控制器传输层，这些传输层是透明的，只需完成传输数据的任务，不必清楚数据的具体格式。两个蓝牙设备点对点HCI层的交互过程如下图所示：

![](https://images.seebug.org/content/images/2020/02/8cf0f0fd-032e-4bfb-8bed-7688e243faff.png-w331s)

#### 2.1.1 HCI包格式

HCI通过包的方式来传送数据、命令和事件的，所有在主机和主机控制器之间的通信都以包的形式进行。包括每个命令的返回参数都通过特定的事件包来传输。HCI有数据、命令和事件三种类型的包。命令包COMMAND（0x01）只能从主机发往主机控制器，其中数据包是双向的，分为两类：ACL（0x02）、SCO（0x03），而事件包EVENT（0x04）始终是主机控制器发向主机的。主机发出的大多数命令包都会触发主机控制器产生相应的事件包作为响应，在传输过程中会有一个句柄，用于识别主机之间的逻辑通道和控制器，共有三种类型的句柄：连接句柄、逻辑链路句柄和物理链路句柄。

根据需要，这里只介绍ACL数据包格式，ACL 数据用于主机和控制器之间的非同步数据交换，如播放音乐数据的数据包，格式如下图：

![](https://images.seebug.org/content/images/2020/02/7594aa87-6638-41be-8ee2-8b1e99f19d1b.png-w331s)

每个字段的说明如下所示：

**字段** | **说明**  
---|---  
**Handle** | Connection_Handle用于在主控制器上传输数据包或段  
**PB Flag** | 包边界和适应范围  
**BC Flag** | 广播标志  
**Data Total Length** | 以八位位组为单位的数据长度，包含高层协议data  
  
其中，PB Flag的描述如下：

![](https://images.seebug.org/content/images/2020/02/d393a050-c084-427c-a372-ed0316da23c9.png-w331s)

设置为 00'b 的时候，代表 Host -> Contoller 的 L2CAP 的首包。设置为 01’b 的时候，代表 Host ->
Contoller 或者 Contoller -> Host 的 L2CAP 的续包（中间的）。设置为 10'b 的时候，代表 Contoller ->
Host 的 L2CAP 的首包。

#### 2.1.2 分段（Fragmentation）和重组（Reassembly ）

分段是将PDU分解成较小的部分，以便从L2CAP传递到较低层。重组是根据从下层传递来的片段重组PDU的过程。分段和重组可以应用于任何L2CAP PDU。

![](https://images.seebug.org/content/images/2020/02/4cee3202-6af1-49c9-9aaf-24f3726d0c68.png-w331s)

### 2.2 L2CAP数据包格式

L2CAP是基于分组的，但也遵循信道传输的通信模型。L2CAP支持的信道有两种：面向连接的信道和面向无连接的信道。在面向连接的信道中，L2CAP数据包的格式如下图所示。

![](https://images.seebug.org/content/images/2020/02/30a3751f-3cf3-477e-a2ab-647d5d9e4335.png-w331s)

数据包中每个字段的说明如下所示：

**字段** | **说明**  
---|---  
**Length** | 2字节，表示信息有效负载的大小，不包括长度L2CAP头  
**Channel ID（CID）** | 2字节，用于标识目的信道的终端。通道ID的范围与正在发送数据包的设备相关  
**Information（Payload）** | 信息负载，长度为0到65535字节  
  
## 三、漏洞原理分析

CVE-2020-0022漏洞位于HCI层，漏洞补丁代码位于hci/src/packet_fragmenter.cc（以8.1.0_r33为例）中的reassemble_and_dispatch()函数中，该函数是用于数据包分片的重组。对于过长的ACL数据包需要进行包的重组，主要是根据ACL包中的PB
Flag标志位进行重组，如果当前是起始部分并且是不完整的，则生成一个部分包（partial_packet）放到map里，等下次收到它的后续部分进行拼装，拼装完毕后就分发出去。详细分析reassemble_and_dispatch()函数如下：

![](https://images.seebug.org/content/images/2020/02/80453de5-1325-40b6-820e-b291b0285c9d.png-w331s)

首先，处理第一个packet，代码127行到129行，分别读取handle、acl_length和l2cap_length。handle为本次链路的Connection_Handle。根据前文数据包格式的介绍，acl_length为Data
Total Length，该data数据域中存放着L2CAP数据包分片（也可能是一个完整的L2CAP数据包）。然后，直接读取data中L2CAP
Length，该l2cap_length是一个完整的L2CAP数据包中payload的长度。行131，校验packet包长度是否正常。行133，通过handle获取boundary_flag，即是PB
Flag。

![](https://images.seebug.org/content/images/2020/02/948948aa-892f-4bef-bbea-2af13f8ab3ae.png-w331s)

行136，判断boundary_flag是否为2，二进制表示为10’b，即判断当前packet是否为 Contoller -> Host 的 L2CAP
的首包，如果是，进入if语句。行137到行147，判断当前packet是否已经被处理，保证本次处理的packet都是最新的。行149到行154，判断L2CAP数据包长度是否正常，不正常直接报错返回。

![](https://images.seebug.org/content/images/2020/02/56381b23-1683-4e3f-97ff-0b03115b3a8a.png-w331s)

接下来，行156到行157，计算full_length，其中包括一个完整的L2CAP数据包中的payload的长度，一个L2CAP头部长度和一个HCI头部长度。行161到行168，判断full_length是否超过BT_DEFAULT_BUFFER_SIZE，如果超过直接报错返回。行170到行178，判断当前头包packet是否还有续包，如果没有续包直接调用callbacks->reassembled处理当前packet并返回。

![](https://images.seebug.org/content/images/2020/02/c59a1cfa-d2e0-4321-93c0-01fe6cd3b07f.png-w331s)

如果当前头包packet后面还有续包，那就开始重新分配一块新的内存用于packet中数据包重组。行180到184，分配并设置partial_packet，将partial_packet->len设置为full_length，将partial_packet->offset设置为packet->len即当前头包packet->data的长度。行186，调用memcpy，将头包packet中HCI数据包整体拷贝到partial_packet中。行189到行191，先找到HCI数据包头部，并跳过handle，更新acl_length为一个完整的L2CAP数据包长度。行193，将partial_packet存放到容器中。行196，释放当前头包packet，表示已经处理完第一个packet，不再需要它了。行197，else语句开始处理后续packet，即boundary_flag不等于2的packet。

![](https://images.seebug.org/content/images/2020/02/cf294609-ea9c-439d-82b4-d9ebcc53f7e5.png-w331s)

行198到行205，首先通过handle判断当前后续packet是否属于本次链路的，如果不属于，直接返回。行206，获取前一轮生成的partial_packet。行208，将当前后续packet->offset赋值为HCI_ACL_PREAMBLE_SIZE即4字节，此时packet->offset指向HCI包中的data域，里面存放着L2CAP数据包分片。行209和行210，计算projected_offset，projected_offset为partial_packet->offset与本次L2CAP数据包分片的长度之和。

![](https://images.seebug.org/content/images/2020/02/a1d23275-1fda-43c9-baaa-95af3a9a9dac.png-w331s)

行211和行219，判断projected_offset是否大于partial_packet->len,即判断projected_offset是否大于full_length。如果大于，则修改packet->len为partial_packet->len减去partial_packet->offset，即packet->len为partial_packet剩余空间的长度。然后，将projected_offset设置为partial_packet->len。具体数据包重组如下图所示：

![](https://images.seebug.org/content/images/2020/02/2ef58060-83c7-405b-ac4c-fc52a8f9a41d.png-w331s)

修正好实际要拷贝的长度后，行221，调用memcpy进行拷贝，漏洞点到了,第一个参数为partial_packet->data +
partial_packet->offset,目的地址是正确的，第二个参数为packet->data +
packet->offset，源地址也是正确的，第三个参数是要拷贝的长度len为packet->len -packet->offset，这个值是有问题的，分两种情况。第一种情况是projected_offset小于partial_packet->len，packet->len
-packet->offset为L2CAP数据包片段总长度，并且是个正数。第二种是行211的情况，packet->len已经被修正过，不需要再一次packet->len
- packet->offset的操作，如果partial_packet剩余空间长度小于4字节，那packet->len - packet->offset
是小于零的，是一个负数。由于memcpy()函数第三个参数类型是一个无符号整型类型，因此整数溢出导致堆溢出。漏洞补丁如下：

![](https://images.seebug.org/content/images/2020/02/f30a4f29-fdad-41a0-ba59-715ef157cdd0.png-w331s)

可以看到，补丁代码中将packet->len加上了一个packet->offset，用于后面抵消减packet->offset的操作。

## 四、影响版本

  1. Android Oreo（8.0和8.1）

  2. Android Pie（9）

  3. Android 10

## 五、安全建议

  1. 尽快更新最新的Android安全补丁

  2. 仅在绝对必要时启用蓝牙

  3. 保持蓝牙设备不可发现

参考文献:

  1. <https://insinuator.net/2020/02/critical-bluetooth-vulnerability-in-android-cve-2020-0022/>
  2. <https://akhozo.blogs.com/2020/02/critical-android-bluetooth-flaw-cve.html?spref=tw>
  3. <https://android.googlesource.com/platform/system/bt/+/3cb7149d8fed2d7d77ceaa95bf845224c4db3baf%5E%21/#F0](#F0)>
  4. <https://source.android.com/security/bulletin/2020-02-01.html>
  5. <http://androidxref.com/8.1.0_r33/xref/system/bt/hci/src/packet_fragmenter.cc>
  6. Bluetooth_Core_v4.2蓝牙官方文档

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1121/>

