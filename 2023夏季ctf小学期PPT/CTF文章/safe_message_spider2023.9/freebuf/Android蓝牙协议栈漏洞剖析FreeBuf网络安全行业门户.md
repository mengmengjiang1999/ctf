## 1 背景介绍

蓝牙协议相对于其他通信协议如WIFI(802.11)、传统TCP/IP议协等来说，更为复杂，目前蓝牙核心规范（5.3）高达3085页。蓝牙的这种复杂性使得对蓝牙的各个协议的实现进行安全测试与审计变得相对困难，从而导致协议的实现和使用容易出现较多的安全漏洞。但是从另一方面来说，它的复杂性也会要求研究员或攻击者进行漏洞挖掘的技术门槛变得相对更高，需要突破的难点也会更多。

![](https://image.3001.net/images/20220721/1658387171_62d8fae3b7f96077a1a00.png!small)

图1 蓝牙核心规范说明书封面

![](https://image.3001.net/images/20220721/1658387216_62d8fb10f3dd4167659cb.png!small)

图2 蓝牙协议栈架构

如图2所示，蓝牙协议栈主要分为两个部分：Host和Controller。Host主要包含链路层之上的整个蓝牙协议栈，包含传输层L2CAP以及在它之上的多种应用层协议，是蓝牙协议栈的核心部分。Controller主要与硬件驱动打交道，偏底层。本文主要关注的是Host层各协议的实现安全。

从Android系统发展历史上来看，其蓝牙协议栈也一直是安全研究的重点目标。2017年Armis安全团队公布BlueBorne组合漏洞攻击链可以通过蓝牙对智能手机进行远程攻击，危害性极大。2020年Android爆出BlueFrag漏洞，攻击者可以通过该漏洞实现远程零交互的远程代码执行。

OPPO安珀实验室一直致力于参与维护整个Android系统生态安全，因此也对Android蓝牙协议栈展开了深入的研究。至今我们已向Google
Android安全团队提报了多个蓝牙协议栈实现安全漏洞，这次将依次介绍我们团队发现的三个不同Android蓝牙协议模块漏洞：CVE-2020-27024（SMP协议）、CVE-2021-0918（GATT协议）、CVE-2021-39805（L2CAP协议）。

## 2 CVE-2020-27024

### 2.1 SMP协议简介

SMP（Security Manage
Protocol）安全管理协议定义了配对和密钥分发的过程实现，然后使用密钥对链路通信数据进行加密。SMP被用在LE设备或蓝牙双模设备中。如图3所示，SMP协议工作流程大致分为几个阶段：

 **Step1** **：特征交换**

配对特征交换，即交换各自都支持哪些配对特性，比如支不支持Secure Connection(安全连接)，支不支持MITM，支不支持OOB（Out of
Band：带外），以及它的输入输出能力(IO capabilities)等。

 **Step2** **：密钥产生**

该阶段双方将协商生成产生STK/LTK：

LE Legacy pairing：产生Short Term Key（短期密钥）。

LE Secure Connection：产生Long Term Key（长期密钥）。

 **Step3** **：密钥分发**

该阶段分发一些其他用途的Key，像Identity Resolving Key（IRK），这个Key是用于Random
Address解析。当分发这些Key时，此阶段链路是必须要加密的，若不加密，将导致密钥直接泄漏。加密使用的密钥是用第二阶段产生的STK或LTK，或者双模下直接共享使用BR/EDR配对产生的Key。

 **Step4** **：链路加密**

通过使用STK/LTK密钥对整个蓝牙通信链路进行加密。

SMP协议整个配对流程如下图所示，其中配对发起方角色为主设备类型（MASTER），接收方为角色为从设备类型（SLAVE）。

![](https://image.3001.net/images/20220721/1658387316_62d8fb74c0f43fdfbb940.png!small)

图3 SMP协议工作流程

### 2.2 漏洞剖析

CVE-2020-27024是SMP协议中一个数组越界漏洞。SMP协议使用预定义的L2CAP_SMP_CID（0x06）、L2CAP_SMP_BR_CID（0x07）通道，位于L2CAP协议层之上。如图4所示，SMP协议栈smp_l2cap_if_init()函数负责注册SMP数据报文接收回调处理函数，分别为处理BLE蓝牙SMP报文的smp_data_received()函数，以及处理BR蓝牙SMP报文的smp_br_data_received()函数。

![](https://image.3001.net/images/20220721/1658387469_62d8fc0d0264b0b9d3c83.png!small)

图4 Android蓝牙协议栈SMP协议的初始化代码段

由BR蓝牙通信链接传入的SMP数据包将交由smp_br_data_received()函数[
代码位于/system/bt/stack/smp/smp_l2c.cc]处理。当SMP协议栈接收到对端发起的配对请求SMP数据包SMP_OPCODE_PAIRING_REQ（0x01）时，报文处理流程则将到达以下图5的代码段。

![](https://image.3001.net/images/20220721/1658387519_62d8fc3f9040130006b67.png!small)

图5 smp_br_data_received()函数代码段

当smp_br_data_received()函数处理完成后，它调用smp_br_state_machine_event()函数
[代码位于/system/bt/stack/smp/smp_br_main.cc ]，该函数代码实现如图6所示。

![](https://image.3001.net/images/20220721/1658387565_62d8fc6d83ac59adb37d4.png!small)

图6 smp_br_state_machine_event()函数代码段

首先我们可从图7中看到全局变量smp_br_entry_table数组的SIZE其实为2。

![](https://image.3001.net/images/20220721/1658387598_62d8fc8e056685c38ac83.png!small)

图7 smp_br_entry_table数组定义

从图6中的代码段我们可以看到由于smp_br_state_machine_event()函数在一开始执行tSMP_BR_ENTRY_TBL
entry_table =
smp_br_entry_table[p_cb->role]语句时并未对p_cb->role的最大值进行合法性判断，反而是取值后再判断p_cb->role的合法性。当攻击者恶意造成p_cb->role出现取值大于2的情况时，将导致smp_br_state_machine_event()函数entry_table赋值语句出现内存OOB越界读的异常。

## 3 CVE-2021-0918

### 3.1 GATT协议简介

GATT是 Generic
Attributes的缩写，中文是通用属性，它是低功耗蓝牙BLE设备之间进行通信的协议。GATT定义了一种多层的数据结构，已连接的低功耗蓝牙设备用它来进行通信，其定义的多层数据结构简要概括起来就是服务（service）可以包含多个特征（characteristic），每个特征包含属性（properties）和值（value），还可以包含多个描述（descriptor）。

GATT基于ATT协议（属性协议）来承载的，属性协议主要用来发现、读写、通知和指示属性。

![](https://image.3001.net/images/20220721/1658387676_62d8fcdcd67654273977f.png!small)

图8 GATT协议交互图

在ATT层协议框架内，拥有一组属性的设备称为服务端（Server），读写该属性值的设备称为客户端（Client），Server和Client通过ATT
PDU进行交互；

其中Attribute Protocol PDU报文格式如图9所示。其中Opcode：操作码（消息类型，1字节大小）； Attribute
Parameters：ATT参数（变长）； Authentication Signature：身份验证签名。

![](https://image.3001.net/images/20220721/1658387707_62d8fcfbe1f0301053303.png!small)

图9 Attribute Protocol PDU报文格式

ATT消息各种类型多达30多种，其中常见的消息类型包含表1中的6种类型，如下表所示。后续介绍的Android蓝牙协议栈GATT漏洞也就是存于Notification消息类型处理函数代码当中的。

表1 Attribute Protocol PDU的类型表

 **PDU** **类型**

|

 **发送方**

|

 **描述信息**  
  
---|---|---  
  
请求/Request

|

Client

|

客户端向服务器请求数据  
  
回复/Response

|

Server

|

服务器对上面请求的回复  
  
命令/Command

|

Client

|

客户端向服务器发送命令-无回复  
  
通知/Notification

|

Server

|

服务器对特征数值向客户端发起通知-无回复  
  
指示/Indication

|

Server

|

服务器对特征数值指示发送给客户端  
  
确认/Confirmation

|

Client

|

客户端对指示的应答  
  
### 3.2 漏洞剖析

CVE-2021-0918是Android系统GATT蓝牙协议栈处理Notification类型报文时存在的一个内存OOB越界读写安全漏洞。

蓝牙协议GATT报文数据核心处理函数位于gatt_data_process()函数[system\bt\stack\gatt\gatt_main.cc]。如图10所示，该函数通过op_code值类型判断，决定该报文是来自client端还是server端，然后分别调用不同的函数处理接口gatt_server_handle_client_req及gatt_client_handle_server_rsp函数。

![](https://image.3001.net/images/20220721/1658387778_62d8fd4293020533e6e18.png!small)

图10 gatt_data_process()代码段

通过分析该代码我们发现可以通过精心构造opcode值（如GATT_HANDLE_VALUE_IND：0x1D、GATT_HANDLE_VALUE_NOTIF：0x1B、GATT_HANDLE_MULTI_VALUE_NOTIF：0x23）来控制函数执行调用到gatt_client_handle_server_rsp()函数。其中GATT_HANDLE_MULTI_VALUE_NOTIF类型是后续触发漏洞的报文类型。

![](https://image.3001.net/images/20220721/1658387806_62d8fd5e130e583437258.png!small)

图11 gatt_client_handle_server_rsp()代码段

最后gatt_client_handle_server_rsp()将调用到gatt_process_notification()函数。该漏洞问题代码是就位于[system](https://android.googlesource.com/platform/system/)/[bt](https://android.googlesource.com/platform/system/bt/)/[stack](https://android.googlesource.com/platform/system/bt/+/a430f5183c9836302f19d793a13e3670b21cc489/stack)/[gatt](https://android.googlesource.com/platform/system/bt/+/a430f5183c9836302f19d793a13e3670b21cc489/stack/gatt)/gatt_cl.cc文件内的gatt_process_notification()函数，该函数是负责对接收到的gatt协议notification类型通知报文进行解析处理。

![](https://image.3001.net/images/20220721/1658387857_62d8fd9110fbf46a6f24a.png!small)

图12 gatt_process_notification()代码段

首先介绍下Android蓝牙协议栈里常用的解析报文内容的宏定义：STREAM_TO_INT8(u8,
p)从p指向的报文中读取1个字节，保存到u8类型变量当中，p指针加1；STREAM_TO_UINT16(u16,
p)每次从p指向报文中读取2个字节，保存到u16类型变量当中，p指针加2。STREAM_TO_ARRAY(a, p,
len)负责从p指向的报文内容读取len字节长度的数据，保存到数组变量a空间中，p指针加len长度。另外tGATT_VALUE
value变量类型的结构体构造如图13所示。

![](https://image.3001.net/images/20220721/1658387888_62d8fdb0854de40e4899e.png!small)

图13 tGATT_VALUE结构体

我们可以看到gatt_process_notification()函数内当op_code值为GATT_HANDLE_MULTI_VALUE_NOTIF类型时，value.len变量值是可以通过报文内长度字段来控制的，此时如果value.len长度大于实际数据长度len时且小于GATT_MAX_ATTR_LEN（固定值为600），后续STREAM_TO_ARRAY(value.value,
p,
value.len)这行代码将导致一个OOB越界读的异常内存拷贝操作。如图14所示，后续gatt_process_notification函数在循环解析报文内的多个notification消息时，由于未对解析出的value.len的长度做最大长度(不能超过GATT_MAX_ATTR_LEN)合法性校验，将导致STREAM_TO_ARRAY(value.value,
p, value.len)出现内存OOB越界写的风险。

![](https://image.3001.net/images/20220721/1658387927_62d8fdd7f402f3f9181d6.png!small)

图14 gatt_process_notification()后续代码段

## 4 CVE-2021-39805

### 4.1 L2CAP协议简介

L2CAP（Logical Link Control and Adaptation
Protocol）称为逻辑链路和适配协议，是蓝牙系统中的核心协议。L2CAP通过协议多分复用、分段和重组，向高层提供面向连接和无连接的数据服务。

![](https://image.3001.net/images/20220721/1658387972_62d8fe0463c56b95a7b2e.jpg!small)

图15 L2CAP协议交互图

L2CAP基于信道的概念，信道的每一个端点被称为信道标识符(CID)，同设备间CID可复用，但本地设备CID不可复用。
L2CAP是基于分组的，但也遵循信道传输的通信模型。对端设备上两个L2CAP实体间传递的信号命令(Signaling
Commands)这些信号命令通过Signaling Channel来传输，对于ACL-U逻辑链路应该使用CID 0x0001, 而对于LE-U则应该使用CID 0x0005。如L2CAP LE Signalling
Channel信令通道,用于控制LE面向连接的数据信道，并可对这些LE信道的特性变化进行协商(LE-U)，后续介绍的漏洞就位于L2CAP LE
Signalling Channel通道信令的处理代码中。蓝牙规范定义的CID如图16所示。

![](https://image.3001.net/images/20220721/1658388006_62d8fe2692c2c511db2f2.png!small)

图16 BLE信道CID

L2CAP数据包的格式如下图所示。

![](https://image.3001.net/images/20220721/1658388035_62d8fe43a9e1b01c69d87.jpg!small)

图17 L2CAP数据包的格式

L2CAP信令报文格式如下所示。

![](https://image.3001.net/images/20220721/1658388069_62d8fe653b2a7a81e3a94.jpg!small)

图18 L2CAP信令报文格式

### 4.2 漏洞剖析

CVE-2021-39805是L2CAP协议中一个数组越界读漏洞。问题代码位于l2cap蓝牙协议栈system\bt\stack\l2cap\l2c_ble.cc文件中的l2cble_process_sig_cmd函数。该函数主要负责解析处理LE的信令通道控制报文。

![](https://image.3001.net/images/20220721/1658388117_62d8fe95df9d5a4c188a0.png!small)

图19 l2cble_process_sig_cmd()代码段

当L2CAP层处理基于信用的增强型流控模式的重新配置的回复（L2CAP_CMD_CREDIT_BASED_RECONFIG_RES，0x1A）报文时，其未进行包长度判断，导致内存信息泄露。顾名思义，这个回复就是响应重新配置的请求(request)报文，这个(request)请求是为了重新配置该通道的MTU和MPS的，其结构如图18。图19就是响应的回复报文。

![](https://image.3001.net/images/20220721/1658388157_62d8febd6ec67168fba54.png!small)

图20基于信用的增强型流控模式的重新配置请求

![](https://image.3001.net/images/20220721/1658388179_62d8fed3857ca63ad727d.png!small)

图21基于信用的增强型流控模式的重新配置回复

Android在2020年8月左右添加了对基于信用的增强型流控模式的支持，此漏洞代码就从那时起一直存在，如图22所示。这段代码段中，STREAM_TO_UINT16从回复报文去取result字段的值，但是取之前未判断此时回复的报文是否已经没有多余的数据了。因此，若精心构造一个该回复数据包，那么就会触发到这个地方导致OOB
Read。且这个被赋值的result字段后续会返回给发送方，导致内存信息泄露。

![](https://image.3001.net/images/20220721/1658388212_62d8fef4140095dedb3db.png!small)

图22 l2cble_process_sig_cmd()后续代码段

## 5 总结与展望

Android系统中蓝牙协议栈演进分为几个阶段，最早android使用是Linux蓝牙协议栈BlueZ。从Android
4.2开始，Google便在Android源码中推出了它和博通公司一起开发的BlueDroid以替代BlueZ。当前Android使用的蓝牙协议栈版本名为Fluoride，而Google正在开发的下一代蓝牙协议栈叫做Gabeldorsh，并使用Rust编程语言进行开发。
目前Fluoride蓝牙协议栈基本上还是使用C/C++语言来实现的，由于蓝牙报文的协议解析处理涉及大量的内存操作，加上蓝牙协议的多样性和复杂性，以及历史上多家公司代码融合等各类原因，导致安卓蓝牙协议栈爆出过很多严重RCE漏洞。而Gabeldorsh可以利用Rust语言本身的特性减少内存型漏洞的产生。这就导致今后对蓝牙协议栈的漏洞挖掘更会集中于逻辑性漏洞，如协议本身的逻辑问题、条件竞争、设计缺陷等方面，这就更加要求该领域的漏洞挖掘研究员具有更加深厚的蓝牙技术知识栈，漏洞挖掘的技术门槛也会更高、需要突破的难点也会更多。

## 6 参考链接

《Bluetooth核心规范》：<https://www.bluetooth.com/specifications/specs/core-specification-5-3/>

《Pixel 更新公告 - 2020 年 12
月》：<https://source.android.com/security/bulletin/pixel/2020-12-01?hl=zh-cn>

《Android 安全公告 - 2021 年 11
月》：<https://source.android.com/security/bulletin/2021-11-01>

《Android 安全公告 - 2022 年 4
月》：<https://source.android.com/security/bulletin/2022-04-01>

