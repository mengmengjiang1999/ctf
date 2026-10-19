# 序

### 可执行程序/共享库文件的产生过程

![11image.png](https://image.3001.net/images/20221020/1666273033_63514f09d798c2976ec01.png!small)

### 现代操作系统如何装载可执行文件

  * 给进程分配独立的虚拟地址空间

  * 建立虚拟地址空间和可执行文件之间的映射关系

  * 把CPU指令寄存器设成可执行文件的入口地址，启动执行

# 总体构成

![12image.png](https://image.3001.net/images/20221020/1666273043_63514f13a760c5bda7084.png!small)

一共由 **4** 部分组成，自上而下分别为

  *  **ELF 头部**

  *  **程序头表**

  *  **节** （区段）

  *  **节头表** （区段表）

# ELF文件的种类

> 哪些文件的结构是 ELF 文件结构

ELF 的全名为`Executable and Linkable Fromat`可链接可执行文件格式，所以以下文件为 ELF 文件格式

  * 可执行文件

  * `.o`\--- 目标文件（可重定位文件）

  * `.so`\--- 共享文件

他们之间的关系为：

目标文件 被 **链接器** 链接为 可执行文件/共享文件，之后再由 **加载器** 将其读进内存并执行

##  **ELF的双重特性**

ELF 格式具有不寻常的 **双重特性**

### 编译器/汇编器/链接器

将 **文件** 看作`ELF header`、`Sections`以及`Section header table`的集合

### 加载器

系统加载器将 **文件** 看作`ELF header`、`Program header table`、`Segment`的集合

其中 一个`Segment`通常由多个`Section`（节）组成

比如：一个 **"可加载只读" **段可以** 由可执行代码(`.text`) Section、只读数据(`.rodata`)
Section和动态链接器需要的符号组成**

![13image.png](https://image.3001.net/images/20221020/1666273064_63514f28683ab4cd09472.png!small)

节（`section`）是从链接器的视角来看`ELF`文件，而 段（`segment`）是从执行的视角来看`ELF`文件，也就是 **它会被映射到内存中**

# ELF 四部分介绍

##  **基础程序**

 **共享库**`libmymath.c -> libmymath.so`

    
    
    int fnAdd(int a,int b)
    {
        return a + b;
    }
    

**目标文件**`main.c -> main.o`

    
    
    #include <stdio.h>
    extern int fnAdd(int a,int b)
    
    int main()
    {
        int i = 1;
        int j = 2;
        int k = fnAdd(i,j);
    
        fprintf(stdout,"k = %d \n",k);
    }
    

![14image.png](https://image.3001.net/images/20221020/1666273076_63514f34226790efdd6d6.png!small)

这里由于 **可能需要安装32位的依赖** ，所以直接以一个简单`shell`的命令集合给出

    
    
    #!/bin/bash
    sudo apt install gcc-multilib # 由于当前的gcc是64位，为了支持编译32位的文件需要安装依赖
    gcc -m32 -no-pie --shared libmymath.c -o libmymath.so
    gcc -m32 -no-pie main.c -o main ./libmymath.so
    

通过`gcc -v`可以在编译时会默认加上`-enable-default-pie`所以要关闭该选项

由于我们主要的目的是观察`ELF`文件的结构，所以 **静态链接/动态链接** 都可以，无所谓，为了方便观察地址，关闭位置无关`PIE`  
![100Untitled.png](https://image.3001.net/images/20221020/1666273146_63514f7a092fc5a2a296a.png!small)

##  **ELF header(ELF 头部)**

首先先来看位于`/usr/include/elf.h`中的定义

此处主要关注 32 位下 ELF header，64 位下结构基本一致

![15image.png](https://image.3001.net/images/20221020/1666273154_63514f82a235b0ad786c9.png!small)

###  **作用**

ELF header的 **主要作用** 有如下几点：

  * 表明文件格式（告诉读取该文件的程序这是一个 ELF 文件）

  * 记录一些该文件与环境的基本信息

    * 文件类型

    * 机器架构

    * 版本

  * 程序的入口地址

  * `Program header table`的 **起始地址** 与其 **结构表项的基本信息**

  * `Section header table`的起始地址与其结构表项的基本信息

### 观察 ELF header

`readelf -h main`  
![16image.png](https://image.3001.net/images/20221020/1666273163_63514f8b7b1fed8296772.png!small)

如图所示便是`ELF header`的全部信息

先来看`ELF header`的大小，如图中第 15 行的信息，`ELF header`的总大小为`52 bytes`，也就是该文件的前 52
字节，16进制下显示为：

![17image.png](https://image.3001.net/images/20221020/1666273172_63514f943ecd7b6b6ec24.png!small)  
`od -Ax -t x1 -N 52 main`

### 各字段含义

> 由于 freebuf 对 markdow n的支持有亿点点差，所以下面可能不美观，谅解谅解。。。

  *  **第一行 ： 前 16 字节**  
`7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00`

    * `7f`—文件标识

    * `45 4c 46`—ELF 三个字母的`ASCII`数值

    * `01 File class byte index`—文件类型位

      * `00`—非法

      * `01`—32位目标

      * `02`—64位目标

    * `01 Data encoding byte index`—数据编码位

      * `00`—非法

      * `01`—小端格式

      * `02`—大端格式

    * `01 File version byte index`—文件版本

    * `00 OS ABI identification`—ELF 文件操作系统的二进制接口的版本标识符

      * `00 UNIX System V ABI`

    * `00 ABI version`—ELF 文件的 ABI 版本。该位置一般值为零

    * `00 Byte index of padding bytes`—标识从该字节开始后面的内容都是用于填充的

    * 为什么`ELF header`第一个字段占`16`字节，回看之前对于`ELF header`可以发现其起一个字段为一个`unsigned char e_ident[EI_NIDENT]`数组，而其中的`EI_NIDENT`正是在该结构体上面定义的宏`#define EI_NIDENT (16)`，所以第一个字段就占`16`字节了

  *  **第二行： 第 16 ~ 31 字节**  
`02 00 03 00 01 00 00 00 70 90 04 08 34 00 00 00`

    * `02 00 e_type`—这是一个可执行文件

    * `03 00 e_machine`—机器架构位`intel 80386`

    * `01 00 00 00`—`e_version`—当前版本

      * `01`—非法 ELF 版本

      * `02`—当前版本

    * `70 90 04 08`—`e_entry`—程序入口地址`0x08049070`

    * `34 00 00 00 e_phoff`—`Program header table`的偏移地址（在该`ELF`文件中）  
0x34 = 52 字节，由于 ELF header 的大小正好是 52 字节，所以说明紧接着 ELF header 的就是 Program header
table

  *  **第三行：第 32 ~ 49 字节（附带第四行的前两字节）**  
`80 35 00 00 00 00 00 00 34 00 20 00 0b 00 28 00 1d 00`

    * `80 35 00 00`—`e_shoff`—`Section header table`的偏移地址（在该`ELF`文件中）  
0x3580 = 13696字节

    * `00 00 00 00`—`e_flags`—处理相关标志

    * `34 00`—`e_ehsize`—`ELF header`的长度 52字节

    * `20 00`—`e_phentsize`—`Program header table`中每个表项`Entry`的长度

    * `0b 00`—`e_phnum`—`Program header table`表中，一共有多少个`Entry`  
一个Program header table表项长度为32字节(0x20)，一共有11(0x0b)个表项，所以一共占 32 * 11 = 352字节

    * `28 00`—`e_shentsize`—`Section header table`中，每个表项`Entry`的长度

    * `1d 00`—`e_shnum`—`Section header table`表中，一共有多少个`Entry`  
一个Section header table表项的长度为40字节(0x28)，所以一共有29个表项，所以一共占 29 * 40 = 1160字节

  *  **第四行：ELF header 的最后两字节**

    * `1c 00`—`e_shstrndx`字符传表表项在`Section header table`中的索引  
此处为第`28(0x1c)`个表项，也就是`Section`中的倒数第二个表项

### 总结

经过上面每个字段的介绍，会觉得哇塞好复杂好麻烦，但其实只要理解每个字段的含义即可，在实际中需要我们一个字节一个字节看`ELF
header`头的场景很少，通过`readelf -h`看即可，其中也会显示每个字段的含义，何乐而不为捏~~~

## 利用 Section header table 查看 Section 的内容

### 字符串表表项

> 就从字符串位于`ELF`文件末尾的字符串表项说起

为什么要单独建立该表项而且在`ELF header`中专门给该表象留一个位置出来？

这些字符串通常是 **符号的名字或者节的名字** 当`ELF`文件的其它部分需要引用某个字符串时， **只需要提供该字符串在字符串表中的序号即可**

下面我们来算出`.shstrtab`在文件中的位置，并通过`od`命令来查看他

首先 **查看`ELF`文件中所有`Section`的信息**  
![18image.png](https://image.3001.net/images/20221020/1666273195_63514fab428dfcd682f37.png!small)

可以看出，`.shstrtab`的偏移地址为`0x00347d(13437)`表项的大小为`0x000101(257)`字节

那么该信息是如何计算出来的呢？

首先由刚刚 ELF header 的信息可以得知 Section header table 的起始偏移地址为 13696字节，每个表项的大小为 40
字节，所以对于处于第 28 个表项的`.shstrtab`来说其偏移就是：

`13696 + 28 * 40 = 14816`

这个就是`.shstrtab`在`Section header table`的位置，现在来查看这个表项：

`od -Ad -t x1 -j 14816 -N 40 main`

![19image.png](https://image.3001.net/images/20221020/1666273206_63514fb6616ff04baca4e.png!small)

对照参考`.shstrtab`表项的结构体

    
    
    typedef struct
    {
      Elf32_Word    sh_name;                /* Section name (string tbl index) */
      Elf32_Word    sh_type;                /* Section type */
      Elf32_Word    sh_flags;               /* Section flags */
      Elf32_Addr    sh_addr;                /* Section virtual addr at execution */
      Elf32_Off     sh_offset;              /* Section file offset */
      Elf32_Word    sh_size;                /* Section size in bytes */
      Elf32_Word    sh_link;                /* Link to another section */
      Elf32_Word    sh_info;                /* Additional section information */
      Elf32_Word    sh_addralign;           /* Section alignment */
      Elf32_Word    sh_entsize;             /* Entry size if section holds table */
    } Elf32_Shdr;
    

**可以看出其偏移为：`0x0000347d`大小为`0x000101`正好对应刚刚`readelf`读出的内容**

其中绿色方框圈出的 0x00000011 便是该字符串（`.shstrtab`这个字符串）在其所指向的字符串表中的偏移地址

用这个偏移地址和大小来查看 **字符串表**

![20image.png](https://image.3001.net/images/20221020/1666273218_63514fc247ff17e77f739.png!small)  
放入文件中，利用 vim 将第一列删除，并去掉其空格后

`%s/ //g`

![22image.png](https://image.3001.net/images/20221020/1666273226_63514fcae4a2a44630aea.png!small)

可以看出第`17(0x11)`字节开始正是`.shstrtab`字符串

### 总结

 **利用相同的方法我们便可以算出任意`Section`的位置并查看其中的内容**

## 利用 Program header table 查看 Segment 的内容

利用`readelf -l`查看`Program header table`

![23image.png](https://image.3001.net/images/20221020/1666273234_63514fd2277581ceb7d0d.png!small)

    
    
    上图中说的有点小问题（下面那段话是 R W 权限，少写了一个…..）
    

**这表明`Program header table`将多个`Sections`分为了11个段，有些段不止有一个`Section`**

 **其中`LOAD`表示可加载的段，程序执行时会由加载器将其加载进行内存**

![24image.png](https://image.3001.net/images/20221020/1666273242_63514fda5b9f12d1b8e70.png!small)

### 为什么32位下程序的默认入口为`0x0804800`

可能是因为它从`System V i386 ABI`借用了该地址

为什么`System V`使用`0x08048000`？

因为，通过将`text`段放置在该地址和它正下方（但在`0x08000000`上方）的堆栈，一个进程可以只使用一个二级页表。换句话说，您必须选择一个默认地址，并且该地址提供了潜在的性能优势，因为最小化页表占用空间意味着优化`TLB`命中率。

`0x08048000`下面有什么吗？堆栈可能在它下面，尽管很可能什么都没有。那个地址只有128M。

# 总结

至此`ELF`文件基本结构就介绍完毕，至于其中各个段的作用，将在后面的静态/动态链接过程的介绍中继续说明其用意

