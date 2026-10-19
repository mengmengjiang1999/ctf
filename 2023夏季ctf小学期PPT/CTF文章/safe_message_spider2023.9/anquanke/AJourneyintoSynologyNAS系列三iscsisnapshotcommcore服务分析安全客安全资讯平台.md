# A-Journey-into-Synology-NAS-系列三-iscsi_snapshot_comm_core服务分析

阅读量 **197613**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-20 14:30:13

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0114a0d4fa50481a90.jpg)

## A Journey into Synology NAS 系列三: iscsi_snapshot_comm_core服务分析

上一篇[文章](https://www.anquanke.com/post/id/251909)主要对群晖`NAS`设备上的`findhostd`服务进行了分析。本篇文章将继续对另一个服务`iscsi_snapshot_comm_core`进行分析，介绍其对应的通信流程，并分享在其中发现的几个安全问题。

## iscsi_snapshot_comm_core服务分析

`iSCSI (Internet small computer system interface)`，又称`IP-SAN`，是一种基于块设备的数据访问协议。`iSCSI`可以实现在`IP`网络上运行`SCSI`协议，使其能够在诸如高速千兆以太网上进行快速的数据存取/备份操作。

群晖`NAS`设备上与`iSCSI`协议相关的两个进程为`iscsi_snapshot_comm_core`和`iscsi_snapshot_server`，对应的通信流程示意图如下。具体地，`iscsi_snapshot_comm_core`首先接收并解析来自外部`socket`的数据，之后再通过`pipe`发送给自己，对接收的`pipe`数据进行处理后，再通过`pipe`发送数据给`iscsi_snapshot_server`。`iscsi_snapshot_server`接收并解析来自`pipe`的数据，根据其中的`commands`来执行对应的命令，如`init_snapshot`、`start_mirror`、`restore_lun`等。

![](https://p0.ssl.qhimg.com/t01ed605918dd20c6e0.png)

对于通过`socket`和`pipe`进行数据的发送与接收，在`libsynoiscsiep.so.6`中存在着2个对应的结构体`socket_channel_transport`和`pipe_channel_transport`，其包含一系列相关的函数指针，如下。其中，部分函数最终是通过调用`PacketRead()`和`PacketWrite()`这2个函数来进行数据的读取和发送。

    
    
    LOAD:00007FFFF7DD9F40                 public pipe_channel_transport
    LOAD:00007FFFF7DD9F40 pipe_channel_transport dq 2             ; DATA XREF: LOAD:off_7FFFF7DD7F48↑o
    LOAD:00007FFFF7DD9F40                                         ; LOAD:transports↑o
    LOAD:00007FFFF7DD9F48                 dq offset synocomm_pipe_construct
    LOAD:00007FFFF7DD9F50                 dq offset synocomm_pipe_destruct
    LOAD:00007FFFF7DD9F58                 align 20h
    LOAD:00007FFFF7DD9F60                 dq offset synocomm_pipe_stop_service
    LOAD:00007FFFF7DD9F68                 dq offset synocomm_pipe_internal_request
    LOAD:00007FFFF7DD9F70                 dq offset synocomm_pipe_internal_response
    LOAD:00007FFFF7DD9F78                 dq offset synocomm_pipe_internal_request_media
    LOAD:00007FFFF7DD9F80                 dq offset synocomm_pipe_internal_response_media
    LOAD:00007FFFF7DD9F88                 dq offset synocomm_base_external_request
    LOAD:00007FFFF7DD9F90                 dq offset synocomm_base_external_response
    LOAD:00007FFFF7DD9F98                 dq offset synocomm_base_write_msg_pipe
    LOAD:00007FFFF7DD9FA0                 dq offset synocomm_base_read_msg_pipe
    LOAD:00007FFFF7DD9FA8                 dq offset synocomm_base_send_msg
    LOAD:00007FFFF7DD9FB0                 dq offset synocomm_base_recv_msg
    LOAD:00007FFFF7DD9FB8                 align 20h
    
    LOAD:00007FFFF7DD9FC0                 public socket_channel_transport
    LOAD:00007FFFF7DD9FC0 socket_channel_transport dq 1           ; DATA XREF: LOAD:off_7FFFF7DD7F68↑o
    LOAD:00007FFFF7DD9FC0                                         ; LOAD:00007FFFF7DD9F18↑o
    LOAD:00007FFFF7DD9FC8                 dq offset synocomm_socket_construct
    LOAD:00007FFFF7DD9FD0                 dq offset synocomm_socket_destruct
    LOAD:00007FFFF7DD9FD8                 dq offset synocomm_socket_start_service
    LOAD:00007FFFF7DD9FE0                 dq offset synocomm_socket_stop_service
    LOAD:00007FFFF7DD9FE8                 dq offset synocomm_socket_internal_request
    LOAD:00007FFFF7DD9FF0                 dq offset synocomm_socket_internal_response
    LOAD:00007FFFF7DD9FF8                 dq offset synocomm_socket_internal_request_media
    LOAD:00007FFFF7DDA000                 dq offset synocomm_socket_internal_response_media
    LOAD:00007FFFF7DDA008                 dq offset synocomm_base_external_request
    LOAD:00007FFFF7DDA010                 dq offset synocomm_base_external_response
    LOAD:00007FFFF7DDA018                 dq offset synocomm_base_write_msg_socket
    LOAD:00007FFFF7DDA020                 dq offset synocomm_base_read_msg_socket
    LOAD:00007FFFF7DDA028                 dq offset synocomm_base_send_msg
    LOAD:00007FFFF7DDA030                 dq offset synocomm_base_recv_msg
    

在了解了大概的通信流程后，接下来将仔细看一下其中的每一步。

## 安全问题

###  非法内存访问

![](https://p4.ssl.qhimg.com/t01f0769c7fd1c2357e.png)

在阶段`1`，`iscsi_snapshot_comm_core`进程接收来自外部`socket`的数据，其最终会调用`PacketRead()`函数来完成对应的功能，部分代码如下。可以看到，在`(4)`处存在一个有符号数比较：如果`v7`为负数的话，`(4)`处的条件将会为真，同时会将`v7`赋值给`v4`。之后`v4`会作为`size`参数传入`memcpy()`，
如果`v4`为负数，后续在`(5)`处调用`memcpy()`时将会造成溢出，同时由于`size`参数过大，也会出现非法内存访问。而`v7`的值来自于`(3)`处`a2()`函数的返回值，可以看到在`(6)`处如果函数`a2()`的第三个参数为0，则会返回-1。而函数`a2()`的第三个参数来自于`(2)`处的`v6[6]`，而`v6`指向的内容为`(4)`处接收的`socket`数据。也就是说，`v6[6]`是外部可控的。因此，通过构造并发送一个伪造的数据包，可造成在`(5)`处调用`memcpy()`时出现溢出(或非法内存访问)。

    
    
    __int64 PacketRead(__int64 a1, signed int (__fastcall *a2)(__int64, __int64, signed __int64), void *a3, unsigned int a4)
    {
      dest = a3;
      v4 = a4;      // max_length: 0x1000
      v5 = ___tzalloc(32LL, 1LL, "synocomm_packet_cmd.c", "ReadPacketHeader", 136LL);
      v6 = (_DWORD *)v5;
      if ( a2(a1, v5, 32LL) < 0 || memcmp(v6, &qword_7FFFF7DDA2B0, 8uLL) )   // (1) recv socket data
      {
        // ...
      }
      v7 = ___tzalloc(32LL, 0LL, "synocomm_packet_cmd.c", "GetPacket", 168LL);
      // ...
      v8 = v6[6];       // (2) v8 = 0
      v9 = ___tzalloc(v6[6], 0LL, "synocomm_packet_cmd.c", "GetPacket", 174LL);
      v7[1] = (const void *)v9;
      v10 = a2(a1, v9, v8);     // (3) recv socket data: return -1
      *(_DWORD *)v7 = v10;
        // ...
      if ( (signed int)v4 > *(_DWORD *)v7 )  // (4) signed comparison
        v4 = *(_DWORD *)v7;
      memcpy(dest, v7[1], (signed int)v4);   // (5) overflow
        // ...
    }
    
    ssize_t a2(__int64 a1, void *a2, int a3)
    {
      // ...
      if ( a3 == 0 || a2 == 0LL || !a1 )    // (6)
        result = 0xFFFFFFFFLL;
      else
        result = recv(*(_DWORD *)(a1 + 4), a2, a3, 0);
      return result;
    }
    

###  越界读

![](https://p2.ssl.qhimg.com/t01c2ea65b9ce3fd02b.png)

假设我们忽略了阶段`1`中的问题，在阶段`2`，`iscsi_snapshot_comm_core`接收来自`pipe`的数据并进行解析，然后调用对应的处理函数，对应的部分代码如下。其中，在`(1)`处会读取数据并将其保存在大小为`0x1000`的缓冲区中。之后会根据读取的数据，调用类似`Handlexxx`的函数，如`HandleSendMsg()`、`HandleRecvMsg()`。根据程序中存在的某个结构体，会发现这两个函数和其他函数不太一样，比较特别。

    
    
    signed __int64 StartEngCommPipeServer@<rax>(__int64 *a1@<rdi>, __int64 a2@<rbx>, __int64 a3@<rbp>, __int64 a4@<r12>)
    {
      // ...
      v5 = (char *)___tzalloc(4096LL, 1LL, "synocomm.c", "PipeServerHandler", 458LL);
      while ( 1 )
      {
        v6 = (*(__int64 (__fastcall **)(__int64, char *, __int64))(*(_QWORD *)(v4 + 56) + 112LL))(v4, v5, 4096LL); // (1) recv msg
        // ...
        v7 = v5[1];
        if ( v5[1] == 1 || *v5 == 16 || *v5 == -1 )
        {
          switch ( *v5 + 1 )
          {
            case 0:
              HandleRejectMsg(v5);  continue;
            // ...
            case 33:
              HandleSendMsg(v5);  continue;        // (2)
            case 34:
              HandleRecvMsg(v5);  continue;        // (3)
            case 49:
              HandleBindMsg(v5);    continue;
            // ...
    

以`HandleRecvMsg()`函数为例，它会调用`AppSendControl()`。其中，函数`AppSendControl()`的第`3`个参数为`(unsigned
int)(*(_DWORD *)(a1 + 76) + 84)`，而`a1`指向前面接收的数据，因此其第`3`个参数是外部可控的。

    
    
    __int64 HandleRecvMsg(__int64 a1)
    {
      v1 = SearchAppInLocalHostSetByUUID(a1 + 36);
      v2 = (void *)v1;
      if ( v1 )
      {
        v3 = -((int)AppSendControl(v2, a1, (unsigned int)(*(_DWORD *)(a1 + 76) + 84)) <= 0);    // (4) controllable
      }
      // ...
    }
    

![](https://p1.ssl.qhimg.com/t014347d08d4d03a7e7.png)

在阶段`3`，`AppSendControl()`函数会通过`pipe`发送数据给`iscsi_snapshot_server`，其最终会调用`PacketWrite()`来完成数据的发送，部分代码如下。函数`PacketWrite()`的第`3`个参数来自于`AppSendControl()`函数的第`2`个参数，第`4`个参数来自于`AppSendControl()`函数的第`3`个参数。

    
    
    __int64 PacketWrite(__int64 a1, __int64 (__fastcall *a2)(__int64, void *, _QWORD), __int64 a3, unsigned int a4)
    {
      // ...
      v4 = a1;
      ptr = 0LL;
      if ( a1 && a2 && a3 && a4 )
      {
        v5 = CreatePacket(&ptr, a3, a4);    // (1)
        v6 = ptr;
        if ( (signed int)v5 > 0 && ptr )
        {
          v7 = a2(v4, ptr, v5);
          if ( v7 >= 0 )
            v7 -= 32;
          v6 = ptr;
        }
       // ...
    

在`PacketWrite()`函数内，在`(1)`处会调用`CreatePacket()`来构建包，`CreatePacket()`函数的部分代码如下。其中，在`(2)`处先调用`tzalloc()`申请大小为`a3+32`的堆空间，在`(3)`处调用`memcpy()`将数据拷贝到指定偏移处。

    
    
    __int64 CreatePacket(__int64 *a1, const void *a2, int a3)
    {
      if ( a1
        && (v3 = a3 + 32,
            v4 = a3,
            v5 = (void *)___tzalloc((a3 + 32), 0LL, "synocomm_packet_cmd.c", "CreatePacket", 57LL),  // (2)
            (*a1 = (__int64)v5) != 0) )
      {
        memset(v5, 0, v3);
        v6 = *a1;
        *(_QWORD *)v6 = qword_7FFFF7DDA2B0;
        v7 = *a1;
        *(_DWORD *)(v6 + 24) = v4;
        memcpy((void *)(v7 + 32), a2, v4);  // (3) out-of-bounds read
      }
      // ...
    }
    

需要说明的是，在`(3)`处调用`memcpy()`时，其第`2`个参数`a2`指向前面保存接收数据的缓冲区，大小为`0x1000`，而第3个参数`v4`外部可控。因此在调用`memcpy()`时会存在如下`2`个问题：

  * `v4`为一个`small large value` 如`0x1100`，由于`a2`的大小为`0x1000`，故会出现越界读；
  * `v4`为一个`big large value` 如`0xffffff90`，由于在调用`tzalloc(a3+32)`时会出现整数上溢，造成分配的堆空间很小，而`memcpy()`的`size`参数很大，故会出现非法内存访问。

因此，通过构造并发送伪造的数据包，可以造成在调用`memcpy()`时出现越界读或者非法内存访问。

> 在`Pwn2Own Tokyo
> 2020`上，`STARLabs`团队利用`HandleSendMsg()`中的越界读漏洞，并组合其他漏洞，在群晖`DS418play`型号的`NAS`设备上实现了任意代码执行。

前面提到过，`HandleSendMsg()`与`HandleRecvMsg()`和其他`Handlexxx`函数不太一样。根据下面的内容可知，只有`SendMsg`和`RecvMsg`这`2`个预定义的长度为`0`(未定义)，其他都有预定义的长度，因而造成后续处理时存在上述问题。

    
    
    LOAD:00007FFFF7DDA120                 dq offset aGetappipack  ; "GetAppIPAck"
    LOAD:00007FFFF7DDA128                 dq 0Ch    ; pre-defined length
    LOAD:00007FFFF7DDA130                 dq 20h
    LOAD:00007FFFF7DDA138                 dq offset aSendmsg      ; "SendMsg"
    LOAD:00007FFFF7DDA140                 dq 0
    LOAD:00007FFFF7DDA148                 dq 21h
    LOAD:00007FFFF7DDA150                 dq offset aRecvmsg      ; "RecvMsg"
    LOAD:00007FFFF7DDA158                 dq 0                    ; 只有这2个未定义长度,后面对应的函数中存在漏洞
    LOAD:00007FFFF7DDA160                 dq 30h
    LOAD:00007FFFF7DDA168                 dq offset aFailToBind+8 ; "Bind"
    LOAD:00007FFFF7DDA170                 dq 0D4h    ; pre-defined length
    LOAD:00007FFFF7DDA178                 dq 31h
    

###  访问控制不当

![](https://p4.ssl.qhimg.com/t01939afa47d061f3f1.png)

假设我们同样忽略了上述问题，在阶段`4`，`iscsi_snapshot_server`从`pipe`读取数据并进行处理，对应的代码如下。在`sub_401BA0()`中，在`(1)`处调用`CommRecvEvlp()`读取数据，在`(2)`处调用`HandleProtCommand()`。

    
    
    signed __int64 sub_401BA0()
    {
      // ...
      v0 = (_QWORD *)CreateSynoCommEvlp();
      v1 = CreateSynoComm("ISS-SERVER");
      // ...
      while ( 1 )
      {
        while ( 1 )
        {
          v2 = CommRecvEvlp(v1, v0);    // (1) recv data
          // ...
          ExtractFromUUIDByDataPacket(*v0, v64);
          ExtractToUUIDByDataPacket(*v0, v65);
          v4 = (const char *)CommGetEvlpData(v0);
          // ...
          v5 = CommGetEvlpData(v0);
          v6 = HandleProtCommand(v1, v5, &s, v64);  // (2)
          // ...
    

在`HandleProtCommand()`中，先将读取的数据转换为`json对象`，解析其中的`command`、`command_sn`和`plugin_id`等，然后根据`command`值查找对应的处理函数，并进行调用。

    
    
    __int64 HandleProtCommand(__int64 a1, __int64 a2, const char **a3, __int64 a4)
    {
      // ...
      v5 = GetJSONFromString(a2);    // (3)
      // ...
      v9 = (const char *)SYNOCPBJsonGetString(v5, "command", 0LL);
      // ...
      v10 = 0;
      v11 = (const char *)*((_QWORD *)pCmdPatterns_ptr + 1);
      v12 = (char *)pCmdPatterns_ptr + 32;
      // ...
      v25 = (unsigned int *)((char *)pCmdPatterns_ptr + 24 * v10);
      v26 = *v25;
      if ( !(unsigned int)json_object_object_get_ex(v6, "command", &v33) ) v33 = 0LL;
      if ( !(unsigned int)json_object_object_get_ex(v6, "command_sn", &v34) ) v34 = 0LL;
      if ( !(unsigned int)json_object_object_get_ex(v6, "plugin_id", &v35) ) v35 = 0LL;
      if ( !(unsigned int)json_object_object_get_ex(v6, "key", &v36) ) v36 = 0LL;
      if ( !(unsigned int)json_object_object_get_ex(v6, "protocol_version", &v37) ) v37 = 0LL;
      // ...
      v38 = json_object_get_string(v33, "protocol_version");
      // ...
      if ( v42 && *v42 == 50 )
      {
        v29 = (*((__int64 (__fastcall **)(__int64, const char *, __int64 *, const void **, __int64))pCmdPatterns_ptr + 3 * v24 + 2))( a1, v6, &v38, &v32, a4);    // (4)
        // ...
    
    LOAD:00007FFFF7DDA340 pCmdPatterns    dq 1                    ; DATA XREF: LOAD:pCmdPatterns_ptr↑o
    LOAD:00007FFFF7DDA348                 dq offset aUnregister_0+2 ; "register"
    LOAD:00007FFFF7DDA350                 dq offset HandleProtRegister
    LOAD:00007FFFF7DDA358                 dq 2
    LOAD:00007FFFF7DDA360                 dq offset aDisconnect+3 ; "connect"
    LOAD:00007FFFF7DDA368                 dq offset HandleProtConnect
    ; ...
    LOAD:00007FFFF7DDA3D8                 dq offset aStartMirror  ; "start_mirror"
    LOAD:00007FFFF7DDA3E0                 dq offset HandleProtStartMirror
    ; ...
    LOAD:00007FFFF7DDA460                 dq 0Dh
    LOAD:00007FFFF7DDA468                 dq offset aBadDeleteLun+4 ; "delete_lun"
    LOAD:00007FFFF7DDA470                 dq offset HandleProtDeleteLun
    ; ...
    LOAD:00007FFFF7DDA4C0                 dq 11h
    LOAD:00007FFFF7DDA4C8                 dq offset aTpTaskReady  ; "tp_task_ready"
    LOAD:00007FFFF7DDA4D0                 dq offset HandleProtTPTaskReady
    

根据`pCmdPatterns`的内容可知，有很多支持的`command`，如`register`、`connect`、`start_mirror`和`delete_lun`等。以`delete_lun`为例，其对应的处理函数为`HandleProtDeleteLun()`。

在`HandleProtDeleteLun()`函数内，获取必要的参数后，在`(5)`处调用`SYNOiSCSILunDelete()`来删除对应的`lun`，而整个过程是无需认证的。因此通过构造并发送伪造的数据包，可实现删除设备上的`lun`，对数据造成威胁。

    
    
    signed __int64 HandleProtDeleteLun(__int64 a1, __int64 a2, __int64 a3, _QWORD *a4)
    {
      v16[0] = 0LL;
      if ( !(unsigned int)json_object_object_get_ex(a2, "data", v16) )
      {
        // ...
      }
      v7 = SYNOCPBJsonGetInteger(v16[0], "type");
      v8 = v7;
      // ...
      v9 = SYNOCPBJsonGetString(v16[0], "lun", 0LL);
      // ...
      v10 = v9;
      v11 = SYNOCPBGetLun(v8, v9);
      v12 = (unsigned int *)v11;
      // ...
      if ( (unsigned int)SYNOiSCSILunDelete(v11, v10) )        // (5)
      {
        // ...
    

## 小结

本文从局域网的视角出发，对群晖`NAS`设备上的`iscsi_snapshot_comm_core`服务进行了分析，并分享了在`iscsi_snapshot_comm_core`与`iscsi_snapshot_server`之间的通信流程中发现的部分问题。当然，`iscsi_snapshot_comm_core`服务的功能比较复杂，这里只是涉及了其中很小的一块，感兴趣的读者可以对其他部分进行分析。

## 相关链接

  * [(Pwn2Own) Synology DiskStation Manager StartEngCommPipeServer HandleSendMsg Out-Of-Bounds Read Information Disclosure Vulnerability](https://www.zerodayinitiative.com/advisories/ZDI-21-339/)
  * [Synology-SA-20:26 DSM](https://www.synology.com/zh-hk/security/advisory/Synology_SA_20_26)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **cq** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/263203](/post/id/263203)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [NAS](/tag/NAS)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t037e042cf93164b03c.jpg) cq

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

