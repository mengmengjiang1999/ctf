**作者：SungLin@知道创宇404实验室  
时间：2019年9月18日 **

### 0x00 信道的创建、连接与释放

通道的数据包定义在MCS Connect Inittial PDU with GCC Conference Create
Request中，在rdp连接过程如下图所示：

![
](https://images.seebug.org/content/images/2019/09/875ffe2f-8970-4a71-944a-8e57e66419c9.png-w331s)

信道创建数据包格式如下：

![
](https://images.seebug.org/content/images/2019/09/67bfb853-923a-4713-b454-eedcedfe8690.png-w331s)

在MCS Connect Inittial中属于Client Network
Data数据段，`MS_T120`将会在连接一开始的时候通过函数`termdd!_IcaRegisterVcBin`创建一个虚拟通道id是0x1f大小为0x18的结构体，之后就调用`termdd!IcaCreateChannel`开始创建大小为0x8c的信道结构体之后将会与虚拟通道id是0x1f绑定，也就是这个结构体将会被我们利用

![
](https://images.seebug.org/content/images/2019/09/3da4ddff-9147-425a-98cb-63fd18817561.png-w331s)

信道的定义字段主要是名字加上配置，配置主要包括了优先级等

![
](https://images.seebug.org/content/images/2019/09/4c684559-17fb-4ada-8783-119605ab21d6.png-w331s)

在server对MCS Connect Inittial应答包，将会依次给出对应虚拟通道的id值：

![
](https://images.seebug.org/content/images/2019/09/8399d56d-a63c-4e5e-9379-ac1ed5f75f1b.png-w331s)

在rdp内核中依次注册的值对应应该是0、1、2、3,
MS_T120信道将会通过我们发送的用户虚拟id为3的值再一次绑定，首先通过`termdd!_IcaFindVcBind`找到了刚开始注册的虚拟通道id是0x1f，如下所示：

![
](https://images.seebug.org/content/images/2019/09/30c7c24c-e2f6-4a9e-834f-5ffcff061b0b.png-w331s)

但是在`termdd!_IcaBindChannel`时，却将我们自定义的id值为3与信道结构体再一次绑定在一起了,此信道结构体就是MS_T120

![
](https://images.seebug.org/content/images/2019/09/37334a80-917c-42c6-bc32-7b32a95c471a.png-w331s)

同时我们自己的用户id将内部绑定的0x1f给覆盖了

![
](https://images.seebug.org/content/images/2019/09/ef13896d-dd82-44a4-afd4-61baed01c3f1.png-w331s)

我们往信道MS_T120发送数据主动释放其分配的结构体，其传入虚拟通道id值为3通过函数`termdd!IcaFindChannel`在channeltable中查找返回对应的信道结构体：

![
](https://images.seebug.org/content/images/2019/09/37329360-87ff-41e8-be59-d1cdb08a3367.png-w331s)

下图为返回的MS_T120信道结构体，其中0xf77b4300为此信道可调用的函数指针数组：

![
](https://images.seebug.org/content/images/2019/09/48865276-a416-4b76-b675-a827b0c52d05.png-w331s)

在这个函数指针数组中主要存放了三个函数，其中对应了`termdd!IcaCloseChannel`、`termdd!IcaReadChannel`、`termdd!IcaWriteChannel`

![
](https://images.seebug.org/content/images/2019/09/1fbba492-81a0-4a02-87a3-f1e326df08fd.png-w331s)

我们传入释放MS_T120信道的数据如下，字节大小为0x12，主要数据对应了0x02

![
](https://images.seebug.org/content/images/2019/09/761329ec-0f71-429f-bb19-dbc3c654e38c.png-w331s)

之后将会进入`nt! IofCompleteRequest`函数，通过apc注入后，将会通过`nt!
IopCompleteRequest`和`nt!IopAbortRequest`进行数据请求的响应，最终在`termdd!IcaDispatch`完成我们发送数据的的请求，`_BYTE
v2`就是我们发送的数据，所以我们发送的数据0x02将会最终调用到IcaClose函数进入IcaCloseChannel函数，最后主动释放掉了`MS_T120`信道结构体

![
](https://images.seebug.org/content/images/2019/09/7f6414b9-4ee6-441f-85c6-c13c6b55472e.png-w331s)
![
](https://images.seebug.org/content/images/2019/09/f6022d24-1974-483c-812a-1df106db9f8c.png-w331s)

### 0x01 通过RDPDR信道进行数据占位

我们先来了解下rdpdr信道，首先rdpdr信道是文件系统虚拟通道扩展，该扩展在名为rdpdr的静态虚拟通道上运行。目的是将访问从服务器重定向到客户端文件系统，其数据头部将会主要是两种标识和PacketId字段组成：

![
](https://images.seebug.org/content/images/2019/09/215c851b-d7fa-4a8b-aa41-71fa873ff775.png-w331s)

在这里我们刚好利用到了rdpde客户端name响应的数据来进行池内存的占位

![
](https://images.seebug.org/content/images/2019/09/e73ccc73-c729-4d99-9ac5-1a5600cf1643.png-w331s)

在完全建立连接后，将会创建rdpdr信道的结构体

![
](https://images.seebug.org/content/images/2019/09/722a1a88-0a55-47f2-86d9-4891684a6709.png-w331s)

在window7中，在建立完成后接收到server的rdpdr请求后，通过发送客户端name响应数据，将会调用到`termdd!
IcaChannelInputInternal`中的ExAllocatePoolWithTag分配非分页池内存，并且其长度是我们可以控制的，基本满足了UAF利用的需求：

![
](https://images.seebug.org/content/images/2019/09/91286064-8fb6-4a7a-9ef8-e8f6f4fcf946.png-w331s)

可是在windowsxp中，直接发送client name request将会导致内存分配失败，直接进入`termdd!
_IcaCopyDataToUserBuffer`,并且在Tao Yan and Jin Chen[1]一文中也提到了通过发送client name
request在触发一定的条件后将会绕过`termdd!_IcaCopyDataToUserBuffer`而进入ExAllocatePoolWithTag分配我们想要的非分页内存，而打破条件如下：

![
](https://images.seebug.org/content/images/2019/09/1770153a-ffc4-4ea6-b942-733b048f43cd.png-w331s)

我们先来看看最开始信道结构体的创建，我们可以发现从一开始创建信道结构体的时候，将会出现两个标志，而这两个标志是按照地址顺序排列的，而在上面需要打破的条件中，只要channelstruct
+0x108的地址存放的是同一个地址，循环就会被break

![
](https://images.seebug.org/content/images/2019/09/572d112f-67e0-468c-9097-8616677a57b5.png-w331s)

我们发送一个正常的rdpdr的name request数据包，头部标识是0x7244和0x4e43

![ ](https://images.seebug.org/content/images/2019/09/3cd78eb7-58df-40dc-bb85-ba78a8d22c6e.png-w331s)

经过`termdd!_IcaCopyDataToUserBuffer`之后，将会进入`nt!IofCompleteRequest`，在响应请求后进入`rdpdr!DrSession::ReadCompletion`,此函数处理逻辑如下，其将会遍历一个链表，从链表中取出对应的vftable函数数组

![
](https://images.seebug.org/content/images/2019/09/de5be446-bf47-4c39-b6fa-496a298bdb5e.png-w331s)

遍历第一次取出第一张函数数组

![
](https://images.seebug.org/content/images/2019/09/23900530-fba5-4302-b509-7877abb13ea6.png-w331s)
![
](https://images.seebug.org/content/images/2019/09/6b6be4bd-c053-404f-872e-10328d4149f1.png-w331s)

传入我们发送的数据后，通过函数数组调用`rdpdr!DrSession::RecognizePacket`进行读取

![
](https://images.seebug.org/content/images/2019/09/6f5e5ff7-614f-4eb4-90c2-c70b4db7af61.png-w331s)

判断头部标志是否为（RDPDR_CTYP_CORE）0x7244

![
](https://images.seebug.org/content/images/2019/09/181261d4-46e3-4297-acbd-c94914406e8c.png-w331s)

接着将会读取函数vftable第二个地址，进行转发

![
](https://images.seebug.org/content/images/2019/09/c7603d2b-45f7-4f2f-aeb4-fbef6dd7e897.png-w331s)

如下图可以看到rdpdr的数据包处理逻辑

![
](https://images.seebug.org/content/images/2019/09/7e33ca52-2bc8-4e9d-8128-8086442b99b8.png-w331s)

rdpdr经过一系列数据包处理后最终进入了我们关心的地方，将会传入channelstruct通过调用`termdd!
_IcaQueueReadChannelRequest`进行标志位的处理

![
](https://images.seebug.org/content/images/2019/09/a0bf25fe-5fda-456c-9c0f-47511855f53f.png-w331s)

最初rdpdr的channelstruct的标志位如下

![
](https://images.seebug.org/content/images/2019/09/b6235f61-e054-4480-b38e-fcf46568495f.png-w331s)

经过函数`termdd!
_IcaQueueReadChannelRequest`对此标志的处理后变成如下，所以下一个数据依然会进入`termdd!_IcaCopyDataToUserBuffer`，导致我们进行池喷射的失败

![
](https://images.seebug.org/content/images/2019/09/0fa6fa69-256e-4d0d-b1f1-95feec938229.png-w331s)

回到rdpdr头部处理函数`rdpdr!DrSession::RecognizePacket`，我们发现在链表遍历失败后将会进行跳转，最后将会进入读取失败处理函数`rdpdr!DrSession::ChannelIoFailed`，然后直接return了

![
](https://images.seebug.org/content/images/2019/09/83bc202f-7751-4e61-bb03-17f10a07e884.png-w331s)
![
](https://images.seebug.org/content/images/2019/09/8778d2de-c15d-4345-852f-2fba56509e0a.png-w331s)

我们构造一个头部异常的数据包发送，头部标志我们构造的是0x7240，将会导致`rdpdr!DrSession::RecognizePacket`判断失败，之后将会继续遍历链表依次再取出两张函数数组

![
](https://images.seebug.org/content/images/2019/09/66d3c183-76d0-4ac1-b363-7c71a6240008.png-w331s)

最后两个函数数组依次调用`rdpdr!DrExchangeManager::RecognizePacket`和`rdpdr!DrDeviceManager::RecognizePacket`，都会判断错误的头部标志0x7240，最后导致链表遍历完后进行错误跳转，直接绕过了`termdd!
_IcaQueueReadChannelRequest`对标志位的修改，将会打破循环

![
](https://images.seebug.org/content/images/2019/09/b9df7ddf-76d9-442d-8c1f-49f3a98506fa.png-w331s)
![
](https://images.seebug.org/content/images/2019/09/e3f58def-e74e-43bc-9c71-ce123cbb46c0.png-w331s)

最后我们连续构造多个错误的数据包后将会进入`ExAllocatePoolWithTag`，分配到我们需要的非分页内存！

![ ](https://images.seebug.org/content/images/2019/09/2b1efaea-b7f8-4179-b7ca-ee2ed88aff1d.png-w331s) ![
](https://images.seebug.org/content/images/2019/09/3d61f243-08c0-4057-a5e4-1c40ef462bd5.png-w331s)

### 0x02 win7 EXP 池喷射简要分析

首先被释放的MS_T120池大小包括是0x170,池的标志是TSic

![
](https://images.seebug.org/content/images/2019/09/c1956b9b-ff90-469d-a174-4a724f6f81fc.png-w331s)

分析Win7 exp
可以知道数据占位是用的rdpsnd信道，作者没有采用rdpdr信道，应该也和喷射的稳定性有关，rdpsnd喷射是再建立完了rdpdr初始化后开始的，在free掉MS_T120结构体前，发送了1044个数据包去申请0x170大小的池内存，这样做可以说应该是为了防止之后被free掉的内存被其他程序占用了，提高free后内存被我们占用的生存几率

![
](https://images.seebug.org/content/images/2019/09/8a2e70ca-8ac4-40bf-b549-28b9101ef206.png-w331s)

占位被free的实际数据大小为0x128,利用的中转地址是0xfffffa80ec000948

![
](https://images.seebug.org/content/images/2019/09/b1cdaa40-460f-4ccc-b00c-48b97257b0fd.png-w331s)

之后开始池喷射，将payload喷射到可以call [rax] ==
0xfffffa80ec000948的地方，喷射的payload大小基本是0x400，总共喷射了200mb的数据大小，我们先来看下喷射前带标志TSic总共占用池内存大小是58kib左右

![
](https://images.seebug.org/content/images/2019/09/bdbffa6a-6b0e-49a5-9cfd-444e4728ebff.png-w331s)
![
](https://images.seebug.org/content/images/2019/09/7c52de99-c79d-445d-be20-45fab5e57ede.png-w331s)

喷射完后带TSic标志池内存大小大约就是201mb，池内存喷射基本是成功的，我的win7是sp1，总共内存大小是1GB，再喷射过程中也没有其他干扰的，所以喷射很顺利

![
](https://images.seebug.org/content/images/2019/09/96856048-421f-4c67-9737-0a504d62b0d1.png-w331s)
![
](https://images.seebug.org/content/images/2019/09/d16d25b1-12e6-438f-87f7-0b576bac3875.png-w331s)

图中可以发现基本已经很稳定的0x400大小的池喷射payload，地址越高0x400大小的内存基本就很稳定了

![
](https://images.seebug.org/content/images/2019/09/8cc4c922-8d96-49ac-910b-4a37a865d0b6.png-w331s)

最后断开连接时候，被free的内存已经被我们喷射的0x128大小的数据给占用了
![](https://images.seebug.org/content/images/2019/09/32f764c0-cd0c-4344-bec4-00d3343f8947.png-w331s)

执行call指令后稳定跳转到了我们的payload，成功执行！

![
](https://images.seebug.org/content/images/2019/09/1baf39cf-8334-4bdb-9942-d773a393c780.png-w331s)

参考链接：  
[0] <https://github.com/rapid7/metasploit-framework/pull/12283>  
[1] <https://unit42.paloaltonetworks.com/exploitation-of-windows-cve-2019-0708-bluekeep-three-ways-to-write-data-into-the-kernel-with-rdp-pdu/>  
[2]
<https://wooyun.js.org/drops/%E7%BE%8A%E5%B9%B4%E5%86%85%E6%A0%B8%E5%A0%86%E9%A3%8E%E6%B0%B4%EF%BC%9A%20%E2%80%9CBig%20Kids%E2%80%99%20Pool%E2%80%9D%E4%B8%AD%E7%9A%84%E5%A0%86%E5%96%B7%E6%8A%80%E6%9C%AF.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1035/>

