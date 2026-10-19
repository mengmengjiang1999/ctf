![](./img/8686614761849118392.png)

### 基本概念

**PE** (Portable Execute)文件是Windows下可执行文件的总称，常见的有 DLL，EXE，OCX，SYS 等。它是微软在 UNIX
平台的 COFF(通用对象文件格式)基础上制作而成。最初设计用来提高程序在不同操作系统上的移植性，但实际上这种文件格式仅用在 Windows
系列操作系统下。PE文件是指 32 位可执行文件，也称为PE32。64位的可执行文件称为 PE+ 或
PE32+，是PE(PE32)的一种扩展形式(不是PE64)。

事实上，一个文件是否是 PE 文件与其扩展名无关，PE文件可以是任何扩展名，系统通过PE结构判断其是否合法。

地址 | 是 “ **虚拟地址** ” 而不是“ **物理地址**
”。不是“物理地址”的原因shi数据在内存的位置经常在变，这样可以节省内存开支、避开错误的内存位置等的优势。同时用户并不需要知道具体的“真实地址”，因为系统自己会为程序准备好内存空间的(只要内存足够大)  
---|---  
节 | 节 是 PE 文件中 代码 或 数据 的基本单元。原则上讲，节只分为 “代码节” 和 “数据节” 。  
镜像文件 | 包含以 EXE 文件为代表的 “可执行文件”、以DLL文件为代表的“动态链接库”。因为他们常常被直接“复制”到内存，有“镜像”的某种意思。  
RVA | Relatively Virtual Address。偏移(又称“相对虚拟地址”)。相对镜像基址的偏移。  
VA | Virtual Address。基址  
  
#### PA(物理地址)/VA(虚拟地址)/RVA(相对虚拟地址)

##### 概念

当一个 PE 文件被加载到内存中以后，我们称之为"映象"(image)

每个程序拥有自己的地址空间，这个地址空间被分割成多个块，每一块称作一页或 **页面**
(page)。每一页有连续的地址范围。这些页被映射到物理内存，但并不是所有的地址空间必须在内存中才能运行程序。当程序引用一部分在物理内存中的地址空间时，有硬件立刻执行必要的映射。当程序引用的到一部分不在物理内存中的地址空间时，由操作系统负责将缺的部分装入物理内存并重新执行失败的指令。

从某个角度来讲，虚拟内存是对基址寄存器和界限寄存器的一种综合。虚拟存储器的基本思想是程序，数据，堆栈的总的大小可以超过物理存储器的大小，
**操作系统把当前使用的部分保留在内存中，而把其他未被使用的部分保存在磁盘上** 。

**线性地址** （Linear Address）
是逻辑地址到物理地址变换之间的中间层。程序代码会产生逻辑地址，或说是段中的偏移地址，加上相应段的基地址就生成了一个线性地址。如果启用了分页机制，那么线性地址能再经变换以产生一个物理地址。若没有启用分页机制，那么线性地址直接就是物理地址。Intel
80386 的线性地址空间容量为 4G（2的32次方即32根地址总线寻址）

**逻辑地址** （Logical Address） 是指由程式产生的和段相关的偏移地址部分。例如，你在进行 C 语言指针编程中，能读取指针变量本身值(
&操作 )，实际上这个值就是逻辑地址，他是相对于你当前进程数据段的地址，不和绝对物理地址相干。只有在 Intel
实模式下，逻辑地址才和物理地址相等（因为实模式没有分段或分页机制，cpu不进行自动地址转换）；逻辑也就是在Intel保护模式下程式执行代码段限长内的偏移地址（假定代码段、数据段如果完全相同）

##### 分页

![](./img/3014528889249588935.png)

大部分虚拟内存中使用一种 **分页** (paging)的技术。

当程序执行下面的指令时，它把地址为1000的内存单元的内容复制到REG中。地址可以通过索引、基址寄存器、段寄存器或其他方式产生。

    
    
    MOV REG, 1000

由程序产生的这些地址称为 **虚拟地址** (VA)，他们构成了一个 **虚拟地址空间**
。在没有虚拟内存的计算机上，系统直接将虚拟地址送到内存总线上，读写操作使用具有同样地址的物理内存字；在使用虚拟内存的情况下，虚拟地址不是被直接送到内存的总线上，而是被送到
**内存管理单元（MMU）,MMU把虚拟地址映射为物理内存地址** 。

**MMU的主要作用** ：实现VA到PA的映射（因此实现方便的动态内存管理）； 实现不同的访问权限。

![](./img/6091984491454040587.png)

虚拟地址空间按照固定大小划分称为 **页面** （page）的若干单元。在物理内存中对应的单元称为 **页框** （page
frame）。页面和页框的大小通常是一样的。实际系统中的页面大小从512字节到1GB。

**转换检测缓冲区（Translation Lookaside Buffer，TLB）** ：虚拟地址到物理地址的映射必须非常快，所以采用TLB，
**将虚拟地址直接映射到物理地址** 。

**多级页表** ：如果虚拟地址空间很大，页表也会很大。这种情况可以采取 **多级页表** 或者 **倒排页表** 。

##### 相对虚拟地址(RVA)

一般来说，PE文件在硬盘上和在内存里是不完全一样的。各个节在硬盘上是连续的，而在内存中是按页对齐的，所以加载到内存以后节之间会出现一些
“空洞”，这样占用的空间就会大一些 。

因为存在这种对齐，所以在 PE 结构内部，表示某个位置的地址采用了两种方式：

  1. 针对在硬盘上存储文件中的地址，称为 **原始存储地址** 或 **物理地址** ， **表示距离文件头的偏移。**
  2. 针对加载到内存以后映象中的地址，称为 **相对虚拟地址(RVA)，表示相对内存映象头的偏移** 。

RVA 是当PE 文件被装到内存中后，某个数据位置相对于文件头的 **偏移量** 。

举个例子：如果 Windows 装载器将一个PE 文件装入到 00400000h 处的内存中，而某个区块中的某个数据被装入0040xxxxh
处，那么这个数据的 RVA 就是 (0040xxxxh - 00400000h ) = xxxxh，反过来说，将
RVA的值加上文件被装载的基地址，就可以找到数据在内存中的实际地址。

##### 定位失效

如果PE文件无法加载到预期的地址，那么系统会帮他重新选择一个合适的基地址将他加载到此处。

这时原有的VA就全部失效了，NT头保存了PE文件加载所需的信息，在不知道PE会加载到哪个基地址之前，VA是无效的，所以在 PE 文件头中大部分是使用 RVA
来表示地址的，而在代码中是用VA表示全局变量和函数地址的。

对于这时的VA，系统会通过重定位(Relocation)的方式修正这些值（在早期的exe中没有重定位）

因而PE 头内部信息大多是 RVA 形式存在。

#### 基地址和偏移地址

cpu和内存之间通过20条地址总线相连接，地址总线就是cpu通过地址找到对应的内存的物理数据的传递工具

例如：有20根地址总线的，总共能拥有
2^20=1048576个不相同的地址，一个地址代表一个存储单元，一个存储单元能够存储1byte数据，总共能存储1M数据。即20根地址总线一共能够处理1M的内存数据

CPU的地址使用16进制表示，最多能够找到2^16=65536个地址（64k内存数据）

这样就要引入段地址的概念，每一个段也就是每一个64K就是一个基地址，段内的数据的地址就是当前基地址的偏移地址。此时通过段地址+偏移地址就能够找到真正的内存数据了

cpu表示的地址为：基地址：偏移地址 （2个16位的地址 2byte）

例如：0BAC:0100

0BAC是基地址，0100是偏移地址，必须要转换成 20位（也就是5位的16进制）才能在20位地址总线中传递，才能达到 1G的数据访问范围：
**内存的物理地址 =基地址*16+偏移地址** ，即`0BAC*16+0100=0BAC0+0100=0BBC0H`，实际传递二进制就是：0000
1011 1011 1100 0000

32位汇编 32根地址总线总共能够直接找到2的32次方个地址,也就是4294967296 byte数据 也就是 4G的内存,而且不在将内存分成一段一段
所有的内存区域都是连续的

#### pe文件与内存映像

![](./img/7752341085206015421.png)

在执行一个PE文件的时候，windows并不在一开始就将整个文件读入内存的，而是采用与内存映射文件类似的机制。也就是说，windows
装载器在装载的时候仅仅建立好虚拟地址和PE文件之间的映射关系。

当且仅当真正执行到某个内存页中的指令或者访问某一页中的数据时，这个页面才会被从磁盘提交到物理内存，这种机制使文件装入的速度和文件大小没有太大的关系。

文件中使用偏移(offset)，内存中使用VA来表示位置。VA 与 RVA 满足下面的换算关系： **RVA + ImageBase = VA**

当 PE 文件被执行时，PE 装载器会为进程分配 4GB
的虚拟地址空间，然后把程序所占用的磁盘空间作为虚拟内存映射到这个4GB的虚拟地址空间中。一般情况下，exe文件默认会映射到虚拟地址空间中的0X400000h的位置，而dll文件默认会定到10000000h。

**ImageBase字段**

ImageBase字段作用是指出文件的优先装入地址。也就是说当文件被执行时,如果可能的话,Windows优先将文件装入
到由ImageBase字段指定的地址中,只有指定的地址已经被其他模块使用时,文件才被装入到其他地址中。链接器产生可执行文件的时候对应这个地址来生成机器码,所以当文件被装入这个地址时不需
要进行重定位操作,装入的速度最快,如果文件被装载到其他地址的话,将不得不进行重定位操作, 这样就要慢一点。

对于EXE文件来说,由于每个文件总是使用独立的虚拟地址空间,优先装入地址不可能被其他模
块占据,所以EXE总是能够按照这个地址装入,这也意味着EXE文件不再需要重定位信息。对于DLL
文件来说,由于多个DLL文件全部使用宿主EXE文件的地址空间,不能保证优先装入地址没有被其他
的DLL使用,所以DLL文件中必须包含重定位信息以防万一。因此,在IMAGE_FILE_HEADER结构的 Characteristics
字段中,DLL文件对应的IMAGE_FILE_RELOCS_STRIPPED 位总是为0,而EXE文件的这个标志位总是为1。

#### 扩展：虚拟地址空间

Windows官方文档:[虚拟地址空间 - Windows drivers | Microsoft
Learn](https://learn.microsoft.com/zh-tw/windows-hardware/drivers/gettingstarted/virtual-address-spaces)

在早期的计算机中，程序都直接运行在物理内存中，当计算机同时运行多个程序时，必须保证这些程序用到的内存总量要小于计算机实际物理内存的大小。当程序同时运行多个程序时，操作系统会直接在内存中给程序划分区域，这样带来了三个问题：
**进程地址空间不隔离** 、 **内存使用效率低** 、 **程序运行的地址不确定**

**虚拟内存** ：windows下的 虚拟内存 指的是在硬盘上建一个文件，用来放置系统非活跃性内存数据或交换数据 (
怎么放，放多少由操作系统决定)。虚拟内存通常只在系统物理内存用完时，才会使用到，但这个时候系统已经非常卡了。但也不是一点用处没有，非活跃性进程的部分数据，系统是完全可以放在虚拟内存中的。

**虚拟地址空间** ：指
windows下每个进程的私有内存空间，大小是4G，能访问的是不到2G的空间，其余是系统保留的。这2G是能访问的，但并不是立即分配的，当进程使用多少时，才从物理内存中划分给它多少，划分的的方式是
"映射"，操作系统将虚拟内存的起始地址做个标记，标记成对应的物理内存的某个地址上。在这里，只有操作系统知道，进程是没有任何办法知道的，这是由 WINDOWS
的高级内存管理机制决定的。物理内存的地址空间，只有操作系统才能访问(硬件驱动也可以) 。进程虚拟内存空间和物理内存空间的关系仅仅是映射关系.

在多任务操作系统中，每个进程都运行在属于自己的内存沙盘中，这个沙盘就是 **虚拟地址空间** (virtual address space)。虚拟地址空间由
**内核空间** (kernel space)和 **用户模式空间** (user mode space)两部分组成。虚拟地址会通过页表(page
table)映射到物理内存，页表由操作系统维护并被处理器引用，每个进程都有自己的页表。内核空间在页表中拥有较高特权级，因此用户态程序试图访问这些页是会导致一个页错误(page
fault)。其中内核空间是持续存在的，并且在所有进程中都映射到同样的物理内存。与此相反，用户模式空间的映射随进程切换的发生而不断变化。

  * 程序一旦被执行就成为一个 **进程** ，内核就会为每个运行的进程提供了大小相同的虚拟地址空间，这使得多个进程可以同时运行而又不会互相干扰
  * 具体来说一个进程对某个地址的访问，绝不会干扰其他进程对同一地址的访问。
  * 进程访问内核空间的唯一途径为 **系统调用** 。
  * 在每个进程眼中，它们各自拥有4GB大小的地址空间；而在CPU眼中，任意时刻，一个CPU上只存在一个虚拟地址空间。 **虚拟地址空间随着进程间的切换而变化。**

通过虚拟地址访问内存有下列优点 ：

  * 程序可以使用连续的虚拟地址范围来访问物理内存中不连续的大型内存缓冲区。
  * 程序可以使用各种虚拟地址来访问大于可用物理内存的内存缓冲区。 当物理内存的供应量变小时，内存管理器会将实体内存分页储存（大小通常为4 KB）磁盘档案。 资料或代码的页面会视需要在物理内存和磁盘之间移动。
  * 不同进程所使用的虚拟地址彼此隔离。 一个进程中的代码无法改变另一个进程或操作系统所使用的物理内存。

##### 分段和分页

**分段**
：程序访问虚拟内存地址，由操作系统将这个虚拟地址映射到适当的物理内存地址上。在虚拟地址空间和物理地址空间之间做一一映射的思想就是分段（Sagmentation）。这样就解决了进程地址空间不隔离和程序运行的地址不确定的两个问题

**分页** ：分页的基本方法是，将地址空间分成许多的页。每页的大小由 CPU 决定，然后由操作系统选择页的大小。（目前 Inter 系列的 CPU 支持
4KB 或 4MB 的页大小，而 PC上目前都选择使用
4KB）分页的思想是程序运行时用到哪页就为哪页分配内存，没用到的页暂时保留在硬盘上。当用到这些页时再在物理地址空间中为这些页分配内存，然后建立虚拟地址空间中的页和刚分配的物理内存页间的映射。

##### 用户空间和系统空间

每个用户模式进程都有自己的私人虚拟地址空间，但核心模式中执行的所有代码都会共享称为 系统空间的单一虚拟地址空间。 用户模式进程的虚拟地址空间称为 用户空间。

在 32 位 Windows 中，可用虚拟地址空间总计为 2^32 个字节（4 GB）。通常，较低的 2 GB 用于用户空间（最大可调整到3GB），而上层
2 GB 则用于系统空间

在 64 位 Windows 中，虚拟地址空间的理论上数量是 2^64 个字节，但实际上只会使用 16 个字节范围的一小部分（128 TB
的范围，0x000'00000000 到 0x7FFF'FFFFFFFF）

**分区** ：在 Windows 系统下，虚拟地址空间被分成了 4 部分： NULL 指针区、用户区、 64KB 禁入区、内核区

1. **NULL指针区** （0x00000000~0x0000FFFF）: 如果进程中的一个线程试图操作这个分区中的数据，CPU就会引发非法访问。他的作用是，调用 malloc 等内存分配函数时，如果无法找到足够的内存空间，它将返回 NULL。而不进行安全性检查。它只是假设地址分配成功，并开始访问内存地址 0x00000000（NULL）。由于禁止访问内存的这个分区，因此会发生非法访问现象，并终止这个进程的运行

2. **用户模式分区** ( 0x00010000~0xBFFEFFFF)：这个分区中存放进程的私有地址空间。一个进程无法以任何方式访问另外一个进程驻留在这个分区中的数据 （相同 exe，通过 copy-on-write 来完成地址隔离）。（在windows中，所有 .exe 和动态链接库都载入到这一区域。系统同时会把该进程可以访问的所有内存映射文件映射到这一分区）

3. **隔离区** (0xBFFF0000~0xBFFFFFFF)：这个分区禁止进入。任何试图访问这个内存分区的操作都是违规的。微软保留这块分区的目的是为了简化操作系统的现实

4. **内核区** (0xC0000000~0xFFFFFFFF)：这个分区存放操作系统驻留的代码。线程调度、内存管理、文件系统支持、网络支持和所有设备驱动程序代码都在这个分区加载。这个分区被所有进程共享

##### 标签集区和非分页集区

在用户空间中，所有物理内存分页都可以视需要标签到磁盘档案。 在系统空间中，某些实体页面可以分页，而其他页面则无法分页。
系统空间有两个区域可动态配置内存：分页集区和非分页集区。

标签集区中配置的内存可以视需要标签到磁盘文件。 在非标签集区中配置的内存永远无法分页到磁盘档案。

##### Linux的内存管理

linux的虚拟内存与Windows基本相同

  * 程序一旦被执行就成为一个进程，内核就会为每个运行的进程提供了大小相同的虚拟地址空间，这使得多个进程可以同时运行而又不会互相干扰
  * 具体来说一个进程对某个地址的访问，绝不会干扰其他进程对同一地址的访问。
  * 每个进程都拥有4GB（32位）大小的虚拟地址空间，每个进程都拥有私有的前3G空间，即“用户空间”；而后1G空间被每个进程所共享，即“内核空间”。
  * 进程访问内核空间的唯一途径为系统调用。
  * 在每个进程眼中，它们各自拥有4GB大小的地址空间；而在CPU眼中，任意时刻，一个CPU上只存在一个虚拟地址空间。虚拟地址空间随着进程间的切换而变化。

![](./img/4629821413485401800.png)

###### 进程地址空间分布

![](./img/8662906884049176737.png)

![](./img/8447405899984535388.png)

  * Linux把进程的地址空间划分为多个区间，这些区间称为虚拟内存区域（VMA）
  * 可以通过cat /proc/进程号/maps来查看进程的地址空间布局

详细组成:

**内核地址空间** :其中高1G为内核空间，所有进程共享内核地址空间，内核空间分三部分：DMA映射区，一致映射区、高端内存区

​
一致映射区的虚拟地址均一一对应了物理页框，因此此区间虚拟地址的访问可以直接通过偏移量得到物理内存而不需进行页表的转换，其中的高128M空间为高端内存，当物理内存大于4G时内核用128M的地址空间作为高端内存，扮演着临时映射的作用。

**Temporary Kernel Mapping 为固定映射空间**
:在这个空间中，有一部分用于高端内存的临时映射。当要进行一次临时映射的时候，需要指定映射的目的，根据映射目的，可以找到对应的小空间，然后把这个空间的地址作为映射地址。  
**Persistent Kernel Mapping 永久映射空间** :从PKMAP_BASE 到 FIXADDR_START用于映射高端内存  
**Vmalloc Area loremap Area 动态映射空间**

**用户地址空间**
:从小到大（从下往上）依次为保留区（受保护的地址）、代码段、数据段（.data段）、.bss段、堆空间、内存映射段、栈空间、命令行参数和环境变量。

**1.保留区**
：保留区即为受保护的地址，大小为0~4K，位于虚拟地址空间的最低部分，未赋予物理地址（不会与内存地址相对应，因此其不会放任何内容）。任何对它的引用都是非法的，用于捕捉使用空指针和小整型值指针引用内存的异常情况。

大多数操作系统中，极小的地址通常都是不允许访问的，如NULL。C语言将无效指针赋值为0也是出于这种考虑，因为0地址上正常情况下不会存放有效的可访问数据。

**2.代码段**
：代码段也称正文段或文本段，通常用于存放程序执行代码(即CPU执行的机器指令)。代码段通常属于只读，以防止其他程序意外地修改其指令(对该段的写操作将导致段错误)（某些架构也允许代码段为可写）。代码段还存放一些只读数据如字符串常量。

代码段指令中包括操作码和操作对象(或对象地址引用)。若操作对象是立即数(具体数值)，将直接包含在代码中；若是局部数据，将在栈区分配空间，然后引用该数据地址；若位于BSS段和数据段，同样引用该数据地址

在代码段和数据段之间还包括其它段：只读数据段和符号段等。

**3.数据段（.data段）**
：数据段通常用于存放程序中已初始化且初值不为0的全局变量和静态局部变量。数据段属于静态内存分配(静态存储区)，可读可写。数据段保存在目标文件中，其内容由程序初始化。

由于全局变量未初始化时，其默认值为0，因此值为0的全局变量位于.bbs段。对于未初始化的局部变量，其值是不可预测的。

**4..bbs段** ：数据段和.bbs段又称为全局数据区，前者初始化，后者未初始化。bbs段存放程序的以下符号：

  * 程序中的未初始化的全局变量和静态局部变量
  * 初始值为0的全局变量和静态局部变量(依赖于编译器实现)
  * 未定义且初值不为0的符号

程序加载时，BSS会被操作系统清零，所以未赋初值或初值为0的全局变量都在BSS中。BSS段仅为未初始化的静态分配变量预留位置，在目标文件中并不占据空间，这样可减少目标文件体积。但程序运行时需为变量分配内存空间，故目标文件必须记录所有未初始化的静态分配变量大小总和(通过start_bss和end_bss地址写入机器代码)。当加载器(loader)加载程序时，将为BSS段分配的内存初始化为0

**数据段与BSS段的区别如下：**  
1.BSS段不占用物理文件尺寸，但占用内存空间；数据段占用物理文件，也占用内存空间。  
对于大型数组如int ar0[1000] = {1, 2, 3, …}和int
ar1[1000]，ar1放在BSS段，只记录共有1000*4个字节需要初始化为0，而不是像ar0那样记录每个数据1、2、3…，此时BSS为目标文件所节省的磁盘空间相当可观。

2.当程序读取数据段的数据时，系统会出发缺页故障，从而分配相应的物理内存；当程序读取BSS段的数据时，内核会将其转到一个全零页面，不会发生缺页故障，也不会为其分配相应的物理内存。

**ELF段** 包括：代码段、其它段（只读数据段和符号段等）、.data段（数据段）和.bbs段，都属于可执行程序部分。

**5.堆空间** ：new( )和malloc(
)函数分配的空间就属于堆空间，用于内存空间的分配，其从下往上扩张。堆用于存放进程运行时动态分配的内存段，可动态扩张或缩减。堆中内容是匿名的，不能按名字直接访问，只能通过指针间接访问。

当进程调用malloc(C) 和new
(C++)等函数分配内存时，新分配的内存动态添加到堆上(扩张)；当调用free(C)/delete(C++)等函数释放内存时，被释放的内存从堆中剔除(缩减)
。  
**6.内存映射段（共享库）** ：此处，内核将硬盘文件的内容直接映射到内存,
任何应用程序都可通过Linux的mmap()系统调用请求这种映射。内存映射是一种方便高效的文件I/O方式（内核直接将硬盘文件映射到虚拟内存中），
因而被用于装载动态共享库， 同时可以用于映射可执行文件用到的动态链接库。

如C标准库函数（fread、fwrite、fopen等）和Linux系统I/O函数，它们都是动态库函数，其中C标准库函数都被封装在了/lib/libc.so库文件中，都是二进制文件。这些动态库函数都是与位置无关的代码，即每次被加载进入内存映射区时的位置都是不一样的，因此使用的是其本身的逻辑地址，经过变换成线性地址（虚拟地址），然后再映射到内存。而静态库不一样，由于静态库被链接到可执行文件中，因此其位于代码段，每次在地址空间中的位置都是固定的。

**7.栈空间** ： 用于存放局部变量（非静态局部变量，C语言称为自动变量），分配存储空间时从上往下。栈和堆都是后进先出的数据结构。

进程栈的初始化大小是由编译器和链接器计算出来的，但是栈的实时大小并不是固定的，Linux
内核会根据入栈情况对栈区进行动态增长（其实也就是添加新的页表）。但是并不是说栈区可以无限增长，它也有最大限制 RLIMIT_STACK (一般为 8M)。

_Random stack offset和Random mmap
offset等随机值意在防止恶意程序。Linux通过对栈、内存映射段、堆的起始地址加上随机偏移量来打乱布局，以免恶意程序通过计算访问栈、库函数等_

**8.命令行参数** ：该段用于存放命令行参数的内容：argc和argv。

**9.环境变量** ：用于存放当前的环境变量，在Linux中用env命令可以查看其值。

在32位X86架构的Linux系统中，用户进程可执行程序一般从虚拟地址空间0x08048000开始加载。该加载地址由ELF文件头决定，可通过自定义链接器脚本覆盖链接器默认配置，进而修改加载地址。0x08048000以下的地址空间通常由C动态链接库、动态加载器ld.so和内核VDSO(内核提供的虚拟共享库)等占用。通过使用mmap系统调用，可访问0x08048000以下的地址空间。

###### 进程用户空间的描述

一个进程的用户地址空间主要由mm_struct结构和vm_area_structs结构来描述：mm_struct结构对进程整个用户空间进行描述，mm_area_structs结构对用户空间中各个内存区进行描述

mm_struct内存描述符基本字段：

![](./img/5645566123366451698.png)

vm_area_structs主要字段：

![](./img/5462463323508539132.png)

相关数据结构之间的关系

![](./img/8969913927755117709.png)

  * 进程在内核中通过task_struct结构体进行描述
  * task_struct->mm指向与该进程用户空间对应的mm_struct结构体
  * mm_struct->mmap指向VMA双链表
  * 使用current->mm->mmap可获得VMA链表的头指针
  * current->mm->mmap->vm_next获得指向该VMA双链表的下一个结点的指针

###### 新建虚拟内存区域

![](./img/6370988969509792771.png)

  * 在内核空间通过do_mmap()创建一个新的虚拟内存区域
  * 在用户空间通过mmap()系统调用获取do_mmap()的功能

###### 内存映射

把文件从磁盘映射到进程用户空间的一个虚拟内存区域中，对文件的访问转化为对虚存区的访问。当从这段虚拟内存中读数据时，就相当于读磁盘文件中的数据，将数据写入这段虚拟内存时，则相当于将数据直接写入磁盘文件。这样就可以在不使用基本I/O操作函数read和write的情况下执行I/O操作。

有共享的、私有的虚存映射和匿名映射。

mmap函数说明

![](./img/3451802651107542542.png)

#### PE 文件的执行顺序

1.当一个 PE 文件 被执行时，PE 装载器 首先检查 DOS header 里的 PE header 的偏移量。如果找到，则直接跳转到 PE
header 的位置。

2.当 PE装载器 跳转到 PE header 后，第二步要做的就是检查 PE header 是否有效。如果该 PE header 有效，就跳转到 PE
header 的尾部/

3.紧跟 PE header 尾部的是节表。PE装载器执行完第二步后开始读取节表中的节段信息，并采用文件映射(
在执行一个PE文件的时候，Windows并不在一开始就将整个文件读入内存，而是采用与内存映射的机制，也就是说，Windows装载器在装载的时候仅仅建立好虚拟地址和PE文件之间的映射关系，只有真正执行到某个内存页中的指令或者访问某一页中的数据时，这个页面才会被从磁盘提交到物理内存，这种机制使文件装入的速度和文件大小没有太大的关系
)的方法将这些节段映射到内存，同时附上节表里指定节段的读写属性。

4.PE文件映射入内存后，PE装载器将继续处理PE文件中类似 import table (输入表)的逻辑部分。

#### 堆和栈

![](./img/7131977029689363296.png)

##### 堆

**堆的特点：**  
1.堆管理器通过链表管理堆，由于申请和释放堆内存是无序的因此会产生内存碎片，堆的释放由程序员完成，回收的内存可以重新使用，
如果不释放只有在程序结束时才会统一释放。  
2.堆的末端由break指针标识，当堆管理器需要更多内存时，可通过系统调用brk()和sbrk()来移动break指针以扩张堆(向上生长并且32位Linux系统中堆内存理论上可达2.9G空间)，一般由系统自动调用。  
3.操作系统为堆维护一个记录空闲内存地址的链表。当系统收到程序的内存分配申请时，会遍历该链表寻找第一个空间大于所申请空间的堆结点，然后将该结点从空闲结点链表中删除，并将该结点空间分配给程序。若无足够大小的空间(可能由于内存碎片太多)，有可能调用系统功能去增加程序数据段的内存空间，以便有机会分到足够大小的内存，然后进行返回。，大多数系统会在该内存空间首地址处记录本次分配的内存大小，供后续的释放函数(如free/delete)正确释放本内存空间。此外，由于找到的堆结点大小不一定正好等于申请的大小，系统会自动将多余的部分重新放入空闲链表中。

**使用堆时经常出现两种问题** ：  
1.释放或改写仍在使用的内存(“内存破坏”)；  
2.未释放不再使用的内存(“内存泄漏”)。当释放次数少于申请次数时，可能已造成内存泄漏。泄漏的内存往往比忘记释放的数据结构更大，因为所分配的内存通常会圆整为下个大于申请数量的2的幂次(如申请212B，会圆整为256B)。

##### 栈

栈可以被称为堆栈，由编译器进行管理(自动释放和分配)并且是先入后出，这里说的堆栈是进程栈（栈分为进程栈，内核栈，线程栈， 中断栈）  
进程栈的初始化大小是由编译器和链接器计算出来的，但是栈的实时大小并不是固定的，Linux
内核会根据入栈情况对栈区进行动态增长（其实也就是添加新的页表）。但是并不是说栈区可以无限增长，它也有最大限制 RLIMIT_STACK (一般为 8M)。  
栈的特点和用途：

1.进程调用函数产生的栈帧建立在栈区（首先压入主调函数中下条指令(函数调用语句的下条可执行语句)的地址，然后是函数实参，然后是被调函数的局部变量。本次调用结束后，局部变量先出栈，然后是参数，最后栈顶指针指向最开始存的指令地址，程序由该点继续运行下条可执行语句）

2.临时存储区，用于暂存长算术表达式部分计算结果或alloca()函数分配的栈内内存，或者c++的临时对象。

3.栈由计算机底层提供支持：分配专门的寄存器存放栈地址，压栈出栈由专门的指令执行， 其相比堆效率较高

进程栈的动态增长实现  
进程在运行的过程中，通过不断向栈区压入数据，当超出栈区容量时，就会耗尽栈所对应的内存区域，这将触发一个 缺页异常 (page
fault)。通过异常陷入内核态后，异常会被内核的 expand_stack() 函数处理，进而调用 acct_stack_growth()
来检查是否还有合适的地方用于栈的增长。  
如果栈的大小低于
RLIMIT_STACK（通常为8MB），那么一般情况下栈会被加长，程序继续执行，感觉不到发生了什么事情，这是一种将栈扩展到所需大小的常规机制。然而，如果达到了最大栈空间的大小，就会发生
栈溢出（stack overflow），进程将会收到内核发出的 段错误（segmentation fault） 信号。  
动态栈增长是唯一一种访问未映射内存区域而被允许的情形，其他任何对未映射内存区域的访问都会触发页错误，从而导致段错误。一些被映射的区域是只读的，因此企图写这些区域也会导致段错误。

### PE 文件结构说明

PE文件的简化结构如下图

![](./img/3776643706057965810.png)

从起始位置开始依次是 **DOS头** ， **NT头** ， **节表** 以及 **具体的节** 。

DOS头 是用来兼容 MS-DOS 操作系统的，目的是当这个文件在 MS-DOS 上运行时提示一段文字，大部分情况下是：This program
cannot be run in DOS mode. 还有一个目的，就是指明 NT 头在文件中的位置。  
NT头 包含 windows PE 文件的主要信息，其中包括一个 'PE' 字样的签名，PE文件头(IMAGE_FILE_HEADER)和
PE可选头(IMAGE_OPTIONAL_HEADER32)。  
节表：是 PE 文件后续节的描述，windows 根据节表的描述加载每个节。  
节：每个节实际上是一个容器，可以包含 代码、数据
等等，每个节可以有独立的内存权限，比如代码节默认有读/执行权限，节的名字和数量可以自己定义，未必是上图中的三个。

官方文档[Winnt.h 标头 - Win32 apps | Microsoft
Learn](https://learn.microsoft.com/zh-cn/windows/win32/api/winnt/)

[PE结构数值查表](https://blog.csdn.net/qiming_zhang/article/details/7309909#3.2.2)

下面通过一个helloworld.exe来展示PE文件结构

#### DOS 头

##### Header 结构 IMAGE_DOS_HEADER

MZ文件头实际是一个结构体 00000000 - 0000003F，共 64 个字节

![](./img/2510432406501107524.png)

注意 Win+Intel 的电脑上大部分采用 ”小端法”，字节在内存中储存方式是倒过来的。

    
    
    typedef struct _IMAGE_DOS_HEADER {   // DOS .EXE header
      WORD  e_magic;           // Magic number
      WORD  e_cblp;           // Bytes on last page of file
      WORD  e_cp;            // Pages in file
      WORD  e_crlc;           // Relocations
      WORD  e_cparhdr;          // Size of header in paragraphs
      WORD  e_minalloc;         // Minimum extra paragraphs needed
      WORD  e_maxalloc;         // Maximum extra paragraphs needed
      WORD  e_ss;            // Initial (relative) SS value
      WORD  e_sp;            // Initial SP value
      WORD  e_csum;           // Checksum
      WORD  e_ip;            // Initial IP value
      WORD  e_cs;            // Initial (relative) CS value
      WORD  e_lfarlc;          // File address of relocation table
      WORD  e_ovno;           // Overlay number
      WORD  e_res[4];          // Reserved words
      WORD  e_oemid;           // OEM identifier (for e_oeminfo)
      WORD  e_oeminfo;          // OEM information; e_oemid specific
      WORD  e_res2[10];         // Reserved words
      LONG  e_lfanew;          // File address of new exe header 
     } IMAGE_DOS_HEADER, *PIMAGE_DOS_HEADER;

e_magic保存“MZ”字符（4D5A），e_lfanew保存PE文件头地址，通过这个地址找到PE文件头，得到PE文件标识“PE”。

e_magic和e_lfanew是验证PE指纹的重要字段，其他字段现基本不使用（可填充任意数据）

##### DOS存根 IMAGE_DOS_STUB

00000040 - 000000BF，共128字节

![](./img/1048750670953631009.png)

DOS存根是一段简单的DOS程序，主要用来输出“This program cannot be run in DOS
mode.”的提示语句。然后退出程序，表示该程序不能在DOS下运行。即使没有DOS存根，程序也能正常执行。

#### **NT头** IMAGE_NT_HEADERS32

![](./img/6780640279237582800.png)

    
    
    typedef struct _IMAGE_NT_HEADERS {
      DWORD                   Signature;         **重要成员 PE签名 相对该结构的偏移0x00**
      IMAGE_FILE_HEADER       FileHeader;        **重要成员 结构体 相对该结构的偏移0x04**
      IMAGE_OPTIONAL_HEADER32 OptionalHeader;    **重要成员 结构体 相对该结构的偏移0x18**
    } IMAGE_NT_HEADERS32, *PIMAGE_NT_HEADERS32;

这个结构体是整个PE文件的核心，由一个Signature、一个IMAGE_FILE_HEADER结构体、一个IMAGE_OPTIONAL_HEADER32结构体组成，占用4B
+ 20B + 224B

##### Signature字段

![](./img/251952864360597113.png)

Signature字段设置为0x00004550，ANCII码字符是“PE00”，标识PE文件头的开始，PE标识不能破坏。

##### IMAGE_FILE_HEADER 标准PE头

![](./img/2377807241428026713.png)

    
    
    typedef struct _IMAGE_FILE_HEADER {
      WORD  Machine;        // 可运行在什么样的CPU上。0代表任意，Intel 386及后续：0x014C， x64: 0x8664
      WORD  NumberOfSections;   // 文件的区块（节）数
      DWORD  TimeDateStamp;     // 文件的创建时间。1970年1月1日以GMT计算的秒数,编译器填充的，不重要的值
      DWORD  PointerToSymbolTable; // 指向符号表（用于调试）
      DWORD  NumberOfSymbols;    // 符号表中符号的个数（用于调试）
      WORD  SizeOfOptionalHeader; // IMAGE_OPTIONAL_HEADER32结构的大小，可改变，32位为E0,64位为F0
                                  // PE32+格式文件中使用的是IMAGE_OPTIONAL_HEADER64结构体，
                                  // 这两个结构体尺寸是不相同的，所以需要在SizeOfOptionalHeader中指明大小。
      WORD  Characteristics;    // 文件属性
    } IMAGE_FILE_HEADER, *PIMAGE_FILE_HEADER;

**Machine**
:表示的是计算机的体系结构类型，也就是说这个成员可以指定该PE文件能够在32位还是在64位CPU上执行。如果强行更改该数值程序就会报错。

**NumberOfSections** :当前PE文件的节区数量，虽然它是大小是两个字节，但是在windows加载程序时会将节区的最大数量限制为96个。

**TimeDateStamp**
:时间戳，表示该PE文件创建的时间，时间是从国际协调时间也就是`1970年1月1日00:00`起开始计数的，计数单位是秒。其计算方法如下

    
    
    通过计算，从1970年到2019年一共有12个闰年(通过闰年计算器获得)，到6月有151天。
    
    秒：0x5CFBB225 % 60 = 33
    分：0x5CFBB225 / 60 % 60 = 3
    时：0x5CFBB225 / 3600 % 24 = 13
    日：0x5CFBB225 / 3600 / 24 - (365 * 49 + 12) - 151 + 1 = 8
    月：(0x5CFBB225 / 3600 / 24 - (365 * 49 + 12)) / 30 + 1 = 6
    年：0x5CFBB225 / 3600 / 24 / 365 + 1970 = 2019
    结果为：2019年6月8日 13:03:33

**SizeOfOptionalHeader**
：存储该PE文件的可选PE头的大小，在32位PE文件中可选头大小为0xE0，64位可选头大小为0xF0。正因为如此，所以就必须通过该成员来确定可选PE头的大小。

**Characteristics** ：描述了PE文件的一些属性信息，比如是否可执行，是否是一个动态连接库等。该值可以是一个也可以是多个值的和。

IMAGE_FILE_HEADER.Characteristics 属性位的含义

数据位 | 常量符号 | 为1时的含义  
---|---|---  
0 | IMAGE_FILE_RELOCS_STRIPPED | 文件中不存在重定位信息  
1 | IMAGE_FILE_EXECUTABLE_IMAGE | 文件是可执行的  
2 | IMAGE_FILE_LINE_NUMS_STRIPPED | 不存在行信息  
3 | IMAGE_FILE_LOCAL_SYMS_STRIPPED | 不存在符号信息  
4 | IMAGE_FILE_AGGRESSIVE_WS_TRIM | 调整工作集  
5 | IMAGE_FILE_LARGE_ADDRESS_AWARE | 应用程序可处理大于2GB的地址  
6 |  | 此标志保留  
7 | IMAGE_FILE_BYTES_REVERSED_LO | 小尾方式  
8 | IMAGE_FILE_32BIT_MACHINE | 只在32位平台上运行  
9 | IMAGE_FILE_DEBUG_STRIPPED | 不包含调试信息  
10 | IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP | 不能从可移动盘运行  
11 | IMAGE_FILE_NET_RUN_FROM_SWAP | 不能从网络运行  
12 | IMAGE_FILE_SYSTEM | 系统文件(如驱动程序)不能直接运行  
13 | IMAGE_FILE_DLL | 这是一个 DLL 文件  
14 | IMAGE_FILE_UP_SYSTEM_ONLY | 文件不能在多处理器计算机上运行  
15 | IMAGE_FILE_BYTES_REVERSED_HI | 大尾方式  
  
以helloworld.exe为例，其中，0x014C说明运行于x86
CPU；0x000E说明当前exe有14个节，0x00E0说明IMAGE_OPTIONAL_HEADER32为224字节，0x0107(100000111)代表文件属性

##### IMAGE_OPTIONAL_HEADER 可选映像头/扩展PE头

![](./img/2059959244797217035.png)

32位下是IMAGE_OPTIONAL_HEADER32，而在64位下是IMAGE_OPTIONAL_HEADER64。是一个可选的结构（
**其实一点都不能少**
），是IMAGE_FILE_HEADER结构的扩展，大小由IMAGE_FILE_HEADER结构的SizeOfOptionalHeader字段记录(可能不准确)

    
    
    typedef struct _IMAGE_OPTIONAL_HEADER { 
            WORD    Magic;                     '// 魔数 32位为0x10B，64位为0x20B，ROM镜像为0x107'
            BYTE    MajorLinkerVersion;         // 链接器的主版本号 -> 05
            BYTE    MinorLinkerVersion;         // 链接器的次版本号 -> 0C
            DWORD   SizeOfCode;                 // 代码节大小，一般放在“.text”节里，必须是FileAlignment的整数倍 -> 40 00 04 00
            DWORD   SizeOfInitializedData;      // 已初始化数大小，一般放在“.data”节里，必须是FileAlignment的整数倍 -> 40 00 0A 00
            DWORD   SizeOfUninitializedData;    // 未初始化数大小，一般放在“.bss”节里，必须是FileAlignment的整数倍 -> 00 00 00 00
            DWORD   AddressOfEntryPoint;       '// 指出程序最先执行的代码起始地址(RVA) -> 00 00 10 00'
            DWORD   BaseOfCode;                 // 代码基址，当镜像被加载进内存时代码节的开头RVA。必须是SectionAlignment的整数倍 -> 40 00 10 00
    
            DWORD   BaseOfData;                 // 数据基址，当镜像被加载进内存时数据节的开头RVA。必须是SectionAlignment的整数倍 -> 40 00 20 00
                                                // 在64位文件中此处被并入紧随其后的ImageBase中。
    
            DWORD   ImageBase;                 '// 当加载进内存时，镜像的第1个字节的首选地址。
                                                // WindowEXE默认ImageBase值为00400000，DLL文件的ImageBase值为10000000，也可以指定其他值。
                                                // 执行PE文件时，PE装载器先创建进程，再将文件载入内存，
                                                // 然后把EIP寄存器的值设置为ImageBase+AddressOfEntryPoint'
    
                                               '// PE文件的Body部分被划分成若干节段，这些节段储存着不同类别的数据。'
            DWORD   SectionAlignment;          '// SectionAlignment指定了节段在内存中的最小单位， -> 00 00 10 00'
            DWORD   FileAlignment;             '// FileAlignment指定了节段在磁盘文件中的最小单位，-> 00 00 02 00
                                                // SectionAlignment必须大于或者等于FileAlignment'
    
            WORD    MajorOperatingSystemVersion;// 主系统的主版本号 -> 00 04
            WORD    MinorOperatingSystemVersion;// 主系统的次版本号 -> 00 00
            WORD    MajorImageVersion;          // 镜像的主版本号 -> 00 00
            WORD    MinorImageVersion;          // 镜像的次版本号 -> 00 00
            WORD    MajorSubsystemVersion;      // 子系统的主版本号 -> 00 04
            WORD    MinorSubsystemVersion;      // 子系统的次版本号 -> 00 00
            DWORD   Win32VersionValue;          // 保留，必须为0 -> 00 00 00 00
    
            DWORD   SizeOfImage;               '// 当镜像被加载进内存时的大小，包括所有的文件头。向上舍入为SectionAlignment的倍数。
                                                // 一般文件大小与加载到内存中的大小是不同的。 -> 00 00 50 00'
    
            DWORD   SizeOfHeaders;             '// 所有头的总大小，向上舍入为FileAlignment的倍数。
                                                // 可以以此值作为PE文件第一节的文件偏移量。-> 00 00 04 00'
    
            DWORD   CheckSum;                   // 镜像文件的校验和 -> 00 00 B4 99
    
            WORD    Subsystem;                 '// 运行此镜像所需的子系统 -> 00 02 -> 窗口应用程序
                                                // 用来区分系统驱动文件(*.sys)与普通可执行文件(*.exe，*.dll)，
                                                // 参考：https://blog.csdn.net/qiming_zhang/article/details/7309909#3.2.3'
    
            WORD    DllCharacteristics;         // DLL标识 -> 00 00
            DWORD   SizeOfStackReserve;         // 最大栈大小。CPU的堆栈。默认是1MB。-> 00 10 00 00
            DWORD   SizeOfStackCommit;          // 初始提交的堆栈大小。默认是4KB -> 00 00 10 00
            DWORD   SizeOfHeapReserve;          // 最大堆大小。编译器分配的。默认是1MB ->00 10 00 00
            DWORD   SizeOfHeapCommit;           // 初始提交的局部堆空间大小。默认是4K ->00 00 10 00
            DWORD   LoaderFlags;                // 保留，必须为0 -> 00 00 00 00
    
            DWORD   NumberOfRvaAndSizes;       '// 指定DataDirectory的数组个数，由于以前发行的Windows NT的原因，它只能为16。 -> 00 00 00 10'
            IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES]; '// 数据目录数组。详见下文。' 
        } IMAGE_OPTIONAL_HEADER32, *PIMAGE_OPTIONAL_HEADER32;
    
    typedef struct _IMAGE_DATA_DIRECTORY {  
        DWORD   VirtualAddress;  
        DWORD   Size;  
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;

**Magic** ：这个无符号整数指出了镜像文件的状态，这个用来识别程序是32位还是64位

32位为0x10B，64位为0x20B，ROM镜像为0x107

**SizeOfCode** ：代码段的长度，如果有多个代码段，则是代码段长度的总和。

**SizeOfInitializedData** ：初始化的数据长度。

**SizeOfUninitializedData** ：未初始化的数据长度。

**AddressOfEntryPoint**
：保存着文件被执行时的入口地址，它是一个RVA。如果想要在一个可执行文件中附加了一段代码并且要让这段代码首先被执行，就可以通过更改入口地址到目标代码上，然后再跳转回原有的入口地址。

**BaseOfCode** ：代码段起始地址的RVA。

**BaseOfData** ：数据段起始地址的RVA。

**ImageBase**
：指定了文件被执行时优先被装入的地址，如果这个地址已经被占用，那么程序装载器就会将它载入其他地址。当文件被载入其他地址后，就必须通过重定位表进行资源的重定位。而装载到ImageBase指定的地址就不会进行资源重定位。

对于EXE文件来说，由于每个文件总是使用独立的虚拟地址空间，优先装入地址不可能被其他模块占据，所以EXE总是能够按照这个地址装入，这也意味着EXE文件不再需要重定位信息。对于DLL文件来说，由于多个DLL文件全部使用宿主EXE文件的地址空间，不能保证优先装入地址没有被其他的DLL使用，所以
**DLL文件中必须包含重定位信息** 以防万一。在 IMAGE_FILE_HEADER 结构中，DLL
文件对应的`IMAGE_FILE_RELOCS_STRIPPED`位（第一位）总是为0，而EXE文件的这个标志位总是为1。

**SectionAlignment** ： **内存对齐**
，指定了文件被装入内存时，节区的对齐单位。节区被装入内存的虚拟地址必须是该成员的整数倍，以字节为单位，并且该成员的值必须大于等于FileAlignment的值。该成员的默认大小为系统的页面大小。

**FileAlignment** ： **文件对齐**
，指定了文件在硬盘上时，节区的对齐单位。节区在硬盘上的地址必须是该成员的整数倍，以字节为单位，并且该成员的值必须大于等于FileAlignment的值。

该值应为200h到10000h(含)之间的2的幂。默认为200h。如果SectionAlignment的值小于系统页面大小，则FileAlignment的值必须等于SectionAlignment的值。

**MajorOperatingSystemVersion、MinorOperatingSystemVersion**
：所需操作系统的版本号，随着操作系统版本越来越多，这个好像不是那么重要了。

**MajorImageVersion、MinorImageVersion** ：映象的版本号，这个是开发者自己指定的，由连接器填写。

**MajorSubsystemVersion、MinorSubsystemVersion** ：所需子系统版本号。

**Win32VersionValue** ：保留，必须为0。

**SizeOfImage**
：指定了文件载入内存后的总体大小，包含所有的头部信息。并且它的值必须是`SectionAlignment`的整数倍。整个PE文件在内存中展开后的大小

**SizeOfHeaders** ：指定了PE文件头的大小，并且向上舍入为FileAlignment的倍数，值的计算方式为：

    
    
    SizeOfHeaders = (e_lfanew/*DOS头部*/ +　4/*PE签名*/ +
                    sizeof(IMAGE_FILE_HEADER) +
                    SizeOfOptionalHeader + /*NT头*/
                    sizeof(IMAGE_SECTION_HEADER) * NumberOfSections) / /*节表*/
                    FileAlignment  *
                    FileAlignment +
                    FileAlignment;    /*向上舍入 一般该结果不可能是FileAlignment的整数倍，所以直接加上FileAlignment还是没问题的 */

**CheckSum** ：映象文件的校验和。

**Subsystem** ：运行该PE文件所需的子系统，可以是下面定义中的某一个：

    
    
    #define IMAGE_SUBSYSTEM_UNKNOWN              0   // Unknown subsystem.
    #define IMAGE_SUBSYSTEM_NATIVE               1   // Image doesn't require a subsystem.
    #define IMAGE_SUBSYSTEM_WINDOWS_GUI          2   // Image runs in the Windows GUI subsystem.
    #define IMAGE_SUBSYSTEM_WINDOWS_CUI          3   // Image runs in the Windows character subsystem.
    #define IMAGE_SUBSYSTEM_OS2_CUI              5   // image runs in the OS/2 character subsystem.
    #define IMAGE_SUBSYSTEM_POSIX_CUI            7   // image runs in the Posix character subsystem.
    #define IMAGE_SUBSYSTEM_NATIVE_WINDOWS       8   // image is a native Win9x driver.
    #define IMAGE_SUBSYSTEM_WINDOWS_CE_GUI       9   // Image runs in the Windows CE subsystem.
    #define IMAGE_SUBSYSTEM_EFI_APPLICATION      10  //
    #define IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER  11   //
    #define IMAGE_SUBSYSTEM_EFI_RUNTIME_DRIVER   12  //
    #define IMAGE_SUBSYSTEM_EFI_ROM              13
    #define IMAGE_SUBSYSTEM_XBOX                 14
    #define IMAGE_SUBSYSTEM_WINDOWS_BOOT_APPLICATION 16
    DllCharacteristics：DLL的文件属性，只对DLL文件有效，可以是下面定义中某些的组合：
    #define IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE 0x0040     // DLL can move.
    #define IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY    0x0080     // Code Integrity Image
    #define IMAGE_DLLCHARACTERISTICS_NX_COMPAT    0x0100     // Image is NX compatible
    #define IMAGE_DLLCHARACTERISTICS_NO_ISOLATION 0x0200     // Image understands isolation and doesn't want it
    #define IMAGE_DLLCHARACTERISTICS_NO_SEH       0x0400     // Image does not use SEH.  No SE handler may reside in this image
    #define IMAGE_DLLCHARACTERISTICS_NO_BIND      0x0800     // Do not bind this image.
    //                                            0x1000     // Reserved.
    #define IMAGE_DLLCHARACTERISTICS_WDM_DRIVER   0x2000     // Driver uses WDM model
    //                                            0x4000     // Reserved.
    #define IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE     0x8000

**SizeOfStackReserve** ：运行时为每个线程栈保留内存的大小。

**SizeOfStackCommit** ：运行时每个线程栈初始占用内存大小。

**SizeOfHeapReserve** ：运行时为进程堆保留内存大小。

**SizeOfHeapCommit** ：运行时进程堆初始占用内存大小。

**LoaderFlags** ：保留，必须为0。

**NumberOfRvaAndSizes** ：指定了可选头中目录项的具体数目，由于以前发行的Windows NT的原因，它只能为10h。

**DataDirectory[] 数据目录数组** ：数组每项都有被定义的值，不同项对应不同数据结构。重点关注的 IMPORT 和 EXPORT，后面详解

**VirtualAddress** ：是一个RVA。

**Size** ：是一个大小。

上面的VirtualAddress和Size定义了DataDirectory[] 的区域

    
    
    #define IMAGE_DIRECTORY_ENTRY_EXPORT          0   // Export Directory 
    #define IMAGE_DIRECTORY_ENTRY_IMPORT          1   // Import Directory 
    #define IMAGE_DIRECTORY_ENTRY_RESOURCE        2   // Resource Directory 
    #define IMAGE_DIRECTORY_ENTRY_EXCEPTION       3   // Exception Directory 
    #define IMAGE_DIRECTORY_ENTRY_SECURITY        4   // Security Directory 
    #define IMAGE_DIRECTORY_ENTRY_BASERELOC       5   // Base Relocation Table 
    #define IMAGE_DIRECTORY_ENTRY_DEBUG           6   // Debug Directory 
    //      IMAGE_DIRECTORY_ENTRY_COPYRIGHT       7   // (X86 usage) 
    #define IMAGE_DIRECTORY_ENTRY_ARCHITECTURE    7   // Architecture Specific Data 
    #define IMAGE_DIRECTORY_ENTRY_GLOBALPTR       8   // RVA of GP 
    #define IMAGE_DIRECTORY_ENTRY_TLS             9   // TLS Directory 
    #define IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG    10   // Load Configuration Directory 
    #define IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT   11   // Bound Import Directory in headers 
    #define IMAGE_DIRECTORY_ENTRY_IAT            12   // Import Address Table 
    #define IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT   13   // Delay Load Import Descriptors 
    #define IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR 14   // COM Runtime descriptor

#### 区块

在 **PE文件头** 与 **原始数据** 之间存在一个 **区块表** (Section
Table)。区块表中包含每个块在映像中的信息，分别指向不同的区块实体。

比如有一个 exe 的区块表含有3个块的描述，分别是.text.rdata和.data，则其每个块对应于一个IMAGE_SECTION _HEADER结构

##### IMAGE_SECTION_HEADER(IMAGE_SECTION_TABLE节表)

![](./img/1951734828597321495.png)

*这只代表一个结构，实际会有多个

节表是一个IMAGE_SECTION_HEADER的结构数组，每个IMAGE_SECTION_HEADER结构40字节。

每个IMAGE_SECTION_HEADER结构包含了它所关联的区块的信息，例如位置、长度、属性。

    
    
    #define IMAGE_SIZEOF_SHORT_NAME       8
    
    typedef struct _IMAGE_SECTION_HEADER {
      BYTE  Name[IMAGE_SIZEOF_SHORT_NAME]; //块名。多数块名以一个“.”开始（例如.text），这个“.”不是必需的
      union {
          DWORD  PhysicalAddress; //常用第二个字段
          DWORD  VirtualSize;   //加载到内存实际区块的大小（对齐前），为什么会变呢？可能是有时未初始化的全局变量不放bss段而是通过扩展这里
      } Misc;
      DWORD  VirtualAddress;  //该块装载到内存中的RVA（内存对齐后，数值总是SectionAlignment的整数倍）
      DWORD  SizeOfRawData;  //该块在文件中所占的空间(文件对齐后)，VirtualSize的值可能会比SizeOfRawData大 例如bss节（SizeOfRawData为0），data节（关键看未初始化的变量放哪）
      DWORD  PointerToRawData; //该块在文件中的偏移（FOA）
    
      /*调试相关，忽略*/
      DWORD  PointerToRelocations; //在“.obj”文件中使用，指向重定位表的指针
      DWORD  PointerToLinenumbers;
      WORD  NumberOfRelocations;  //重定位表的个数（在OBJ文件中使用）。
      WORD  NumberOfLinenumbers;
    
      DWORD  Characteristics; //块的属性 该字段是一组指出块属性（例如代码/数据、可读/可写等）的标志
    } IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;

**Name**
：这是一个8字节的ASCII字符串，长度不足8字节时用0x00填充，该名称并不遵守必须以"\0"结尾的规律，如果不是以"\0"结尾，系统会截取8个字节的长度进行处理。可执行文件不支持长度超过8字节的节名。对于支持超过字节长度的文件来说，此成员会包含斜杠(/)，并在后面跟随一个用ASCII表示的十进制数字，该数字是字符串表的偏移量。

**Misc.PhysicalAddress** ：文件地址。和下面的Misc.VirtualSize在一个结构体中

**Misc.VirtualSize**
：指定了该节区装入内存后的总大小，以字节为单位，如果此值大于SizeOfRawData的值，那么大出的部分将用0x00填充。这个成员只对可执行文件有效，如果是obj文件此成员的值为0。

**VirtualAddress**
：指定了该节区装入内存虚拟空间后的地址，这个地址是一个相对虚拟地址(RVA)，它的值一般是SectionAlignment的整数倍。它加上ImageBase后才是真正的虚拟地址。

**SizeOfRawData**
：指定了该节区在硬盘上初始化数据的大小，以字节为单位。它的值必须是FileAlignment的整数倍，如果小于Misc.VirtualSize，那么该部分的其余部分将用0x00填充。如果该部分仅包含未初始化的数据，那么这个值将会为零。

**PointerToRawData**
：指出零该节区在硬盘文件中的地址，这个数值是从文件头开始算起的偏移量，也就是说这个地址是一个文件偏移地址(FOA)。它的值必须是FileAlignment的整数倍。如果这个部分仅包含未初始化的数据，则将此成员设置为零。

**Characteristics** ：指出了该节区的属性特征。其中的不同数据位代表了不同的属性，这些数据位组合起来就是这个节的属性特征。详情查表

节表在PE文件头中的排列位置比较特殊，节表是紧跟在NT头(也可以说是可选PE头后)后的，它实际上是一个IMAGE_SECTION_HEADER类型的数组，数组的成员个数被定义在IMAGE_FILE_HEADER中的NumberOfSections成员上，需要注意的是在最后一个节表后最好应该有一个与节表同样大小的用0x00填充的空白数据。

##### 常见区块与区块合并

区块中的数据逻辑通常是关联的。PE文件一般至少有两个区块，一个是代码块另一个是数据块。每个区块都有特定的名字，这个名字用于表示区块的用途。例如，一个区块叫作.rdata，表明它是一个只读区块。区块在映像中是按起始地址(RVA)排列的，而不是按字母表顺序排列的。使用区块名只是为了方便，它对操作系统来说是
**无关紧要** 的。微软给这些区块分别取了有特色的名字但这不是必需的。Borland链接器使用的是像“CODE”和“DATA”这样的名字。

exe和obj文件常见区块定义：

![](./img/4865650955750970799.png)

注意:在编程过程中，读取 PE 文件中的相关内容(例如输入表、输出表等)时，不能将区块名称作为参考。正确的方法是按照数据目录表中的字段进行定位。

区块并非全部在链接时形成，更准确地说，它们一般是 **从OBJ文件开始** 被编译器放置的。链接器的工作就是 **合并** 所有 OB]
和库中需要的块，使其最终成为一个合适的区块。这样可以节省内存和磁盘空间（每个区块至少占用一个内存页，缩小合并一个就有可能减少一个内存页的占用）

**OBJ文件** ：obj文件一般是Object的简写,是程序编译后的二进制文件,在通过链接器和资源文件链接就成exe文件了。

##### 区块的对齐值

区块的大小是要对齐的。有两种对齐值，一种用于磁盘文件内，另一种用于内存中。PE 文件头指出了这两个值，它们可以不同。

在PE文件头里， **FileAlignment**
定义了磁盘区块的对齐值。每一个区块从对齐值的倍数的偏移位置开始，而区块的实际代码或数据的大小不一定刚好是这么多，所以在不足的地方一般以00h来填充，这就是区块的间隙。例如在PE
文件中一个典型的对齐值是 **200h**
，这样每个区块从200h的倍数的文件偏移位置开始。假设区块的第1个节在40h处长度为90h，那么400h——490h为这一区块的内容而文件对齐值是200h，为了使这一节的长度为FileAlignment的整数倍490~600h会被0填充，这段空间称为区块间隙，下一个区块的开始地址为600h。

在PE文件头里， **SectionAligrment**
定义了内存中区块的对齐值。当PE文件被映射到内存中时区块总是至少从一个页边界处开始。也就是说，当一个 PE
文件被映射到内存中时，每个区块的第1个字节对应于某个内存页。在x86系列CPU中内存页是按 **4KB** (1000h)排列的;在x64中内存页是按
**8KB** (2000h)排列的。所以，在x86系统中PE文件区块的内存对齐值一般为1000h每个区块从1000h的倍数的内存偏移位置开始。

##### 文件偏移与虚拟地址的转换

些PE文件为减小体积，磁盘对齐值不是一个内存页 1000h，而是200h。当这类文件被映射到内存中后
**，同一数据相对于文件头的偏移量在内存中和磁盘文件中是不同的**
，这样就出现了文件偏移地址与虚拟地址的转换问题。而那些磁盘对齐值(1000h)与内存页相同的区块，同一数据在磁盘文件中的偏移与在内存中的偏移相同，因此不需要转换。

虚拟地址和虚拟大小是指该区块在内存中的地址和大小。物理地址和物理大小是指该区块在磁盘文件中的地址和大小。由于其磁盘对齐值为200h，与内存对齐值不同故其磁盘映像和内存映像不同，如下图所示。

![](./img/37445284380899540.png)

文件被映射到内存中时，MS-DOS头部，PE文件头和块表的偏移位置与大小均没有变化。而当各区块被映射到内存中后。其偏移位置就发生了变化。例如，磁盘文件中text块起始端与文件头的偏移量为add1，映射到内存后text块起始端与文件头(基地址的偏移量为add2同时，text块与块表之间形成了一大段空隙，这部分数据全是以0填充的。在这里，add1的值就是文件偏移地址(File
Offset)add2的值就是相对虚拟地址(RVA)。假设它们的差值为则文件偏移地址与虚拟地址的关系如下。

![](./img/8852639401055242052.png)

**在同一区块中各地址的偏移量是相等的** ，可用上面的公式对此区块中的任意FileOset与VA进行转换。但
**在整个文件里FileOset与VA的差值不是Δk**
，因为各区块在内存中是以一个页边界开始的，从第1个区块的结束到第2个区块的开始(1000h)对齐处全以数据0填充，所以不同区块在磁盘与内存中的差值不同。

在实际操作中使用lordpe等工具转换

### IMAGE_DATA_DIRECTORY 详解

IMAGE_DATA_DIRECTORY即DataDirectory[]
数据目录数组中的数据，是IMAGE_OPTIONAL_HEADER（可选映像头/扩展PE头）的一部分

    
    
    typedef struct _IMAGE_DATA_DIRECTORY {
        DWORD   VirtualAddress;
        DWORD   Size;
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;

通过函数获取数组中的项可以用RtlImageDirectoryEntryToData函数。DataDirectory中的每一项都可以用一个函数获取，函数原型如下：

    
    
    PVOID NTAPI RtlImageDirectoryEntryToData(PVOID Base, BOOLEAN MappedAsImage, USHORT Directory, PULONG Size);
            Base：模块基地址
            MappedAsImage：是否映射为映象
            Directory：数据目录项的索引
    
    
    #define IMAGE_DIRECTORY_ENTRY_EXPORT          0   // Export Directory
    #define IMAGE_DIRECTORY_ENTRY_IMPORT          1   // Import Directory
    #define IMAGE_DIRECTORY_ENTRY_RESOURCE        2   // Resource Directory
    #define IMAGE_DIRECTORY_ENTRY_EXCEPTION       3   // Exception Directory
    #define IMAGE_DIRECTORY_ENTRY_SECURITY        4   // Security Directory
    #define IMAGE_DIRECTORY_ENTRY_BASERELOC       5   // Base Relocation Table
    #define IMAGE_DIRECTORY_ENTRY_DEBUG           6   // Debug Directory
    //      IMAGE_DIRECTORY_ENTRY_COPYRIGHT       7   // (X86 usage)
    #define IMAGE_DIRECTORY_ENTRY_ARCHITECTURE    7   // Architecture Specific Data
    #define IMAGE_DIRECTORY_ENTRY_GLOBALPTR       8   // RVA of GP
    #define IMAGE_DIRECTORY_ENTRY_TLS             9   // TLS Directory
    #define IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG    10   // Load Configuration Directory
    #define IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT   11   // Bound Import Directory in headers
    #define IMAGE_DIRECTORY_ENTRY_IAT            12   // Import Address Table
    #define IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT   13   // Delay Load Import Descriptors
    #define IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR 14   // COM Runtime descriptor

IMAGE_DATA_DIRECTORY 只包含两个内容，VirtualAddress和Size定义了DataDirectory[] 的区域

这两个成员(主要是VirtualAddress)成为了定位各种表的关键，所以一定要知道每个数组元素所指向的数据块类型，以下表格就是它的对应关系：

描述 | **数组下标** | **中文描述**  
---|---|---  
Export table address and size | 0x00 | 导出表的地址和大小  
Import table address and size | 0x01 | 导入表的地址和大小  
Resource table address and size | 0x02 | 资源表的地址和大小  
Exception table address and size | 0x03 | 异常表的地址和大小  
Certificate table address and size | 0x04 | 证书表的地址和大小  
Base relocation table address and size | 0x05 | 基址重定位表的地址和大小  
Debugging information starting address and size | 0x06 | 调试信息的起始地址和大小  
Architecture-specific data address and size | 0x07 | 特定于体系结构数据的地址和大小  
Global pointer register relative virtual address | 0x08 | 全局指针寄存器相对虚拟地址  
Thread local storage (TLS) table address and size | 0x09 | (线程本地存储)TLS表的地址和大小  
Load configuration table address and size | 0x0A | 加载配置表地址和大小  
Bound import table address and size | 0x0B | 绑定导入表的地址和大小  
Import address table address and size | 0x0C | 导入地址表的地址和大小  
Delay import descriptor address and size | 0x0D | 延迟导入表的地址和大小  
The CLR header address and size | 0x0E | CLR运行时头部数据地址和大小  
Reserved | 0x0F | 保留  
  
#### PE导出表 IMAGE_DIRECTORY_ENTRY_EXPORT

**动态链接库**
：动态链接库是被映射到其他应用程序的地址空间中执行的，它和应用程序可以看成是"一体”的，动态链接库可以使用应用程序的资源，它所拥有的资源也可以被应用程序使用，它的任何操作都是代表应用程序进行的，当动态链接库进行打开文件、分配内存和创建窗口等操作后，这些文件、内存和窗口都是为应用程序所拥有的。

**导出表** 就是记载着动态链接库的一些导出信息。通过导出表，DLL 文件可以向系统提供导出函数的名称、序号和入口地址等信息，以便Windows
加载器通过这些信息来完成动态连接的整个过程

提示: 扩展名为.exe 的PE 文件中一般不存在导出表，而大部分的.dl 文件中都包合导出表。但注意，这并不是绝对的。例如纯粹用作资源的.dll
文件就不需要导出函数啦，另外有些特殊功能的.exe 文件也会存在导出函数。

当PE 文件被执行的时候，Windows 加载器将文件装入内存并将导入表(Export Table) 登记的动态链接库(一般是DLL
格式)文件一并装入地址空间，再根据DLL 文件中的函数导出信息对被执行文件的IAT 进行修正。

**导出表是用来描述模块(dll)中的导出函数的结构** ，如果一个模块导出了函数，那么这个函数会被 **记录在导出表中**
，这样通过GetProcAddress函数就能动态获取到函数的地址。导出表就是一个 " 表格 "

##### Windows 装载器的工作步骤:

1.定位到PE 文件头

2.从PE 文件头中的IMAGE OPTIONAL HEADER32 结构中取出数据目录表，并从第一个数据目录中得到导出表的RVA

3.从导出表的 Base 字段得到起始序号

4.将需要查找的导出序号减去起始序号，得到函数在入口地址表中的索引

5.检测索引值是否大于导出表的 NumberOfFunctions 字段的值，如果大于后者，说明输入的序号是无效的

6.用这个索引值在 AddressoffFunctions 字段指向的导出函数入口地址表中取出相应的项目，这就是函数入口地址的RVA
值，当函数被装入内存的时候，这个RVA 值加上模块实际装入的基地址，就得到了函数真正的入口地址

函数导出的方式有两种：按 **名字** 导出，按 **序号** 导出。

    
    
    //系统中获取函数地址的两种方法：
    HMODULE hModule = LoadLibraryA("User32.dll");
    //1、函数名获取
    DWORD FuncAddress = GetProcAddress(hModule, "MessageBoxA");
    //2、序号获取
    DWORD FuncAddress = GetProcAddress(hModule, 12);

##### 导出表

    
    
    typedef struct _IMAGE_EXPORT_DIRECTORY {
        DWORD   Characteristics;
        DWORD   TimeDateStamp;
        WORD    MajorVersion;
        WORD    MinorVersion;
        DWORD   Name;
        DWORD   Base;
        DWORD   NumberOfFunctions;
        DWORD   NumberOfNames;
        DWORD   AddressOfFunctions;     // RVA from base of image
        DWORD   AddressOfNames;         // RVA from base of image
        DWORD   AddressOfNameOrdinals;  // RVA from base of image
    } IMAGE_EXPORT_DIRECTORY, *PIMAGE_EXPORT_DIRECTORY;

**Characteristics** ：现在没有用到，一般为0。

**TimeDateStamp** ：导出表生成的时间戳，由连接器生成。

**MajorVersion，MinorVersion** ：看名字是版本，实际貌似没有用，都是0。

**Name** ：模块的名字。

**Base** ：序号的基数，按序号导出函数的序号值从Base开始递增。

**NumberOfFunctions** ：所有导出函数的数量。

**NumberOfNames** ：按名字导出函数的数量。

**AddressOfFunctions** ：一个RVA，指向一个DWORD数组，数组中的每一项是一个导出函数的RVA，顺序与导出序号相同。

**AddressOfNames** ：一个RVA，依然指向一个DWORD数组，数组中的每一项仍然是一个RVA，指向一个表示函数名字。

**AddressOfNameOrdinals**
：一个RVA，还是指向一个WORD数组，数组中的每一项与AddressOfNames中的每一项对应，表示该名字的函数在AddressOfFunctions中的序号。

###### 功能实现

![](./img/3249551638997197880.png)

在上图中，AddressOfNames 指向一个数组，数组里保存着一组
RVA，每个RVA指向一个字符串，这个字符串即导出的函数名，与这个函数名对应的是AddressOfNameOrdinals中的对应项。获取导出函数地址时，先在AddressOfNames中找到对应的名字，比如Func2，他在AddressOfNames中是第二项，然后从AddressOfNameOrdinals中取出第二项的值，这里是2，表示函数入口保存在AddressOfFunctions这个数组中下标为2的项里，即第三项，取出其中的值，加上模块基地址便是导出函数的地址。如果函数是以序号导出的，那么查找的时候直接用序号减去Base，得到的值就是函数在AddressOfFunctions中的下标。代码实现如下：

    
    
    DWORD* CEAT::SearchEAT( const char* szName)
    {
        if (IS_VALID_PTR(m_pTable))
        {
            bool bByOrdinal = HIWORD(szName) == 0;
            DWORD* pProcs = (DWORD*)((char*)RVA2VA(m_pTable->AddressOfFunctions));
            if (bByOrdinal)
            {
                DWORD dwOrdinal = (DWORD)szName; 
                if (dwOrdinal < m_pTable->NumberOfFunctions && dwOrdinal >= m_pTable->Base)
                {
                    return &pProcs[dwOrdinal-m_pTable->Base];
                }
            }
            else
            {
                WORD* pOrdinals = (WORD*)((char*)RVA2VA(m_pTable->AddressOfNameOrdinals));
                DWORD* pNames = (DWORD*)((char*)RVA2VA(m_pTable->AddressOfNames));
                for (unsigned int i=0; i<m_pTable->NumberOfNames; ++i)
                {
                    char* pNameVA = (char*)RVA2VA(pNames[i]);
                    if (strcmp(szName, pNameVA) != 0)
                    {
                        continue;
                    }
                    return &pProcs[pOrdinals[i]];
                }
            }
        }
        return NULL;
    }
    

#### PE导入表 IMAGE_DIRECTORY_ENTRY_IMPORT

**输入函数** ：输入函数(Import
Functions，也称导入函数)，输入函数就是被程序调用但其执行代码又不在程序中的函数，这些函数的代码位于相关的DLL
文件中，在调用者程序中只保留相关的函数信息(如函数名、DLL 文件名等)就可以。对于磁盘上的PE 文件来说，它无法得知这些输入函数在内存中的地址，只有当PE
文件被装入内存后，Windows 加载器才将相关DLL
装入，并将调用输入函数的指令和函数实际所处的地址联系起来。这就是“动态链接”的概念。动态链接是通过PE
文件中定义的”输入表”来完成的，输入表中保存的正是函数名和其驻留的DLL 名等。

导入表在PE文件加载时，会根据这个表里的内容加载依赖的DLL，并填充所需函数的地址。

##### 四个导入表

在 IMAGE_DATA_DIRECTORY
中，有几项的名字都和导入表有关系，其中包括：IMAGE_DIRECTORY_ENTRY_IMPORT，IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT，IMAGE_DIRECTORY_ENTRY_IAT
和 IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT。他们之间的关系如下 ：

1 **.IMAGE_DIRECTORY_ENTRY_IMPORT** 就是我们通常所知道的 **导入表** ，在 PE
文件加载时，会根据这个表里的内容加载依赖的 DLL ( 模块 )，并填充所需函数的地址。

2. **IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT** 叫做 **绑定导入表** ，在第一种导入表导入地址的修正是在PE加载时完成，如果一个PE文件导入的DLL或者函数多那么加载起来就会略显的慢一些，所以出现了绑定导入，在加载以前就修正了导入表，这样就会快一些。

3. **IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT** 叫做 **延迟导入表** ，一个PE文件也许提供了很多功能，也导入了很多其他DLL，但是并非每次加载都会用到它提供的所有功能，也不一定会用到它需要导入的所有DLL，因此延迟导入就出现了，只有在一个PE文件真正用到需要的DLL，这个DLL才会被加载，甚至于只有真正使用某个导入函数，这个函数地址才会被修正。

4. **IMAGE_DIRECTORY_ENTRY_IAT** 是 **导入地址表** ，前面的三个表其实是导入函数的描述，真正的函数地址是被填充在导入地址表中的。

DataDirectory(数据目录表)的第二个成员就是指向输入表的。而输入表是以一个IMAGE_IMPORT_DESCRIPTOR(简称IID)的数组（大小为20字节）开始。每个被
PE文件链接进来的 DLL文件都分别对应一个 IID数组结构。在这个
ID数组中，并没有指出有多少个项(就是没有明确指明有多少个链接文件)，但它最后是以一个全为NULL(O)的 IID 作为结束的标志。

导入表IMAGE_IMPORT_DESCRIPTOR定义如下：

    
    
    typedef struct _IMAGE_IMPORT_DESCRIPTOR {
        union {
            DWORD   Characteristics;
            DWORD   OriginalFirstThunk;             //导入名称表(INT)的RVA地址
        } DUMMYUNIONNAME;
        DWORD   TimeDateStamp;                      //时间戳多数情况可忽略  如果是0xFFFFFFFF表示IAT表被绑定为函数地址
        DWORD   ForwarderChain;
        DWORD   Name;                               //导入DLL文件名的RVA地址
        DWORD   FirstThunk;                         //导入地址表(IAT)的RVA地址
    } IMAGE_IMPORT_DESCRIPTOR;
    typedef IMAGE_IMPORT_DESCRIPTOR UNALIGNED *PIMAGE_IMPORT_DESCRIPTOR;

使用 RtlImageDirectoryEntryToData 并将索引号传 1，会得到一个如上结构的指针，实际上指向一个上述结构的数组，每个导入的 DLL
都会成为数组中的一项，也就是说，一个这样的结构对应一个导入的 DLL。

**Characteristics，OriginalFirstThunk** ：一个联合体，如果是数组的最后一项 Characteristics 为
0，否则 OriginalFirstThunk 保存一个 RVA，指向一个 IMAGE_THUNK_DATA 的数组，这个数组中的每一项表示一个导入函数。

**TimeDateStamp** ：映象绑定前，这个值是0，绑定后是导入模块的时间戳。

**ForwarderChain** ：转发链，如果没有转发器，这个值是 -1 。

**Name** ：一个 RVA，指向导入模块的名字，所以一个 IMAGE_IMPORT_DESCRIPTOR 描述一个导入的DLL。

**FirstThunk** ：也是一个 RVA，也指向一个 IMAGE_THUNK_DATA 数组。

OriginalFirstThunk 与 FirstThunk 都指向一个 IMAGE_THUNK_DATA 数组，但是它们之间有区别

###### IMAGE_THUNK_DATA

IMAGE_THUNK_DATA——INT(导入名称表)、IAT(导入地址表)的结构体定义如下:

    
    
    typedef struct _IMAGE_THUNK_DATA32 {
        union {
            DWORD ForwarderString;     
            DWORD Function;            
            DWORD Ordinal;
            DWORD AddressOfData;        // PIMAGE_IMPORT_BY_NAME 的地址RVA
        } u1;
    } IMAGE_THUNK_DATA32;
    typedef IMAGE_THUNK_DATA32 * PIMAGE_THUNK_DATA32;
    
    //注：这个结构体是联合类型的，每一个成员都是4字节，所以为了编程方便，完全可以用一个4字节的数组取代它。

Function 表示函数地址，如果是按序号导入 Ordinal 就有用了，若是按名字导入AddressOfData
便指向名字信息。可以看出这个结构体就是一个大的union。

union虽包含多个域，但是在不同时刻代表不同的意义，使用名字还是序号通过Ordinal判断，如果Ordinal的最高位是1，就是按序号导入的，这时候，低16位就是导入序号，如果最高位是0，则AddressOfData是一个RVA，指向一个IMAGE_IMPORT_BY_NAME结构，用来保存名字信息，由于Ordinal和AddressOfData实际上是同一个内存空间，所以AddressOfData其实只有低31位可以表示RVA，但是一个PE文件不可能超过2G，所以最高位永远为0，这样设计很合理的利用了空间。

实际编写代码的时候微软提供两个宏定义处理序号导入：IMAGE_SNAP_BY_ORDINAL 判断是否按序号导入，IMAGE_ORDINAL
用来获取导入序号。

所以，二者的 **区别** 就是：

**OriginalFirstThunk** 指向的 IMAGE_THUNK_DATA 数组包含导入信息，在这个数组中只有 Ordinal 和
AddressOfData 是有用的，因此可以通过 OriginalFirstThunk 查找到函数的地址。

**FirstThunk** 则略有不同，在PE文件加载以前或者说在导入表未处理以前，他所指向的数组与 OriginalFirstThunk
中的数组虽不是同一个，但是内容却是相同的，都包含了导入信息。而在加载之后，FirstThunk 中的 Function
开始生效，他指向实际的函数地址，因为FirstThunk 实际上指向 IAT 中的一个位置，IAT 就充当了 IMAGE_THUNK_DATA
数组，加载完成后，这些 IAT 项就变成了实际的函数地址，即 Function 的意义。

加载前：

![](./img/4091356526687848187.png)

加载后：

![](./img/7850902214993203751.png)

###### IMAGE_IMPORT_BY_NAME

结构体定义如下：

    
    
    typedef struct _IMAGE_IMPORT_BY_NAME {
        WORD    Hint;          //可能为空，编译器决定，如果不为空是函数在导出表中的索引
        CHAR   Name[1];        //函数名称，以0结尾
    } IMAGE_IMPORT_BY_NAME, *PIMAGE_IMPORT_BY_NAME;
    
    //注：这个结构体由两个成员组成，大致一看它的大小是3个字节，其实它的大小是不固定的，
    //因为无法判断函数名的长度，所以最后一个成员是一个以0结尾的字符串。

总结：导入表其实是一个 IMAGE_IMPORT_DESCRIPTOR 的数组，每个导入的 DLL 对应一个
IMAGE_IMPORT_DESCRIPTOR。  
IMAGE_IMPORT_DESCRIPTOR 包含两个 IMAGE_THUNK_DATA 数组，数组中的每一项对应一个导入函数。  
加载前 OriginalFirstThunk 与 FirstThunk 的数组都指向名字信息，加载后 FirstThunk 数组指向实际的函数地址。

###### IMAGE_BOUND_IMPORT_DESCRIPTOR——绑定导入表

绑定导入是一个 **文件快速启动**
的技术，但是只能起到辅助的效果，它的存在只会影响到PE文件的加载过程，并不会影响PE文件的运行结果。如果把绑定导入的信息从PE文件中清除，这个PE文件的运行结果
**不会受到任何影响** 。

从导入表部分我们可以知道，FirstThunk这个成员指向了IAT表，在程序加载时加载器会通过INT表来修复IAT表，使里面存放上对应函数的地址信息，但是如果导入的函数太多在加载过程中就会使程序启动变慢，绑定导入就是为了减少IAT表的修复时间。它会在程序加载前修复IAT表，然后在PE文件中声明绑定导入的数据信息，让操作系统知道这些事情已经提前完成。

    
    
    typedef struct _IMAGE_BOUND_IMPORT_DESCRIPTOR {
        DWORD   TimeDateStamp;                    //时间戳
        WORD    OffsetModuleName;                 //DLL名的地址偏移
        WORD    NumberOfModuleForwarderRefs;      //该结构后IMAGE_BOUND_FORWARDER_REF数组的数量
    // Array of zero or more IMAGE_BOUND_FORWARDER_REF follows
    } IMAGE_BOUND_IMPORT_DESCRIPTOR,  *PIMAGE_BOUND_IMPORT_DESCRIPTOR;

**TimeDateStamp**
：时间戳，这个值只有和导入DLL的IMAGE_FILE_HEADER中的TimeDateStamp值相同才能起到绑定导入的效果，如果不一致加载器就会重新计算IAT表中的函数地址。(由于DLL文件的版本不同或者DLL文件的ImageBase被重定位时，IAT绑定的函数的地址就会发生变化)

**OffsetModuleName**
：这个偏移不是RVA页不是FOA，所以模块名的定位与之前的方法不同，它的定位方式是以第一个IMAGE_BOUND_IMPORT_DESCRIPTOR的地址为基址，加上OffsetModuleName的值就是模块名所在的地址了，这个模块名是以0结尾的ASCII字符串。

**NumberOfModuleForwarderRefs**
：这个值是在IMAGE_BOUND_IMPORT_DESCRIPTOR结构后跟随的IMAGE_BOUND_FORWARDER_REF结构的数量。在每一个IMAGE_BOUND_IMPORT_DESCRIPTOR结构后都会跟随着大于等于0个
**IMAGE_BOUND_FORWARDER_REF** 结构，然后在其后面又会跟上绑定表结构体，直至全部用0填充的绑定表结构。

**IMAGE_BOUND_FORWARDER_REF**

    
    
    typedef struct _IMAGE_BOUND_FORWARDER_REF {
        DWORD   TimeDateStamp;               //时间戳
        WORD    OffsetModuleName;            //DLL名的地址偏移
        WORD    Reserved;                    //保留
    } IMAGE_BOUND_FORWARDER_REF, *PIMAGE_BOUND_FORWARDER_REF;
    //注：
    //    该结构中的成员和绑定导入表的成员含含义一致，所以不再过多叙述。
    //    由于IMAGE_BOUND_IMPORT_DESCRIPTOR和IMAGE_BOUND_FORWARDER_REF的大小结构相同，所以可以相互转型，方便编程。

![](./img/618071177439965062.png)

#### 延迟导入表 IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT

**延迟导入** (Delay
Import)，这种导入机制导入其他DLL的时机比较“迟”。原因是有些导入函数可能使用的频率比较低，或者在某些特定的场合才会用到，而有些函数可能要在程序运行一段时间后才会用到，这些函数可以等到他实际使用的时候再去加载对应的DLL，而没必要再程序一装载就初始化好，这样可以可以加快启动速度。

在IMAGE_DATA_DIRECTORY 中，有一项为
IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT，这一项便是延迟导入表，IMAGE_DATA_DIRECTORY.VirtualAddress
就指向延迟导入表的起始地址。既然是表，肯定又是一个数组，每一项都是一个ImgDelayDesc r结构体，和导入表一样，每一项都代表一个导入的DLL。

定义：

    
    
    [cpp] view plaincopy
    
    typedef struct ImgDelayDescr {  
        DWORD           grAttrs;        // attributes  
        RVA             rvaDLLName;     // RVA to dll name  
        RVA             rvaHmod;        // RVA of module handle  
        RVA             rvaIAT;         // RVA of the IAT  
        RVA             rvaINT;         // RVA of the INT  
        RVA             rvaBoundIAT;    // RVA of the optional bound IAT  
        RVA             rvaUnloadIAT;   // RVA of optional copy of original IAT  
        DWORD           dwTimeStamp;    // 0 if not bound,  
                                        // O.W. date/time stamp of DLL bound to (Old BIND)  
    } ImgDelayDescr, * PImgDelayDescr;  
    typedef const ImgDelayDescr *   PCImgDelayDescr;

**grAttrs** ：用来区分版本，1是新版本，0是旧版本，旧版本中后续的rvaxxxxxx域使用的都是指针，而新版本中都用RVA，我们只讨论新版本。

**rvaDLLName** ：一个RVA，指向导入DLL的名字。

**rvaHmod** ：一个RVA，指向导入DLL的模块基地址，这个基地址在DLL真正被导入前是NULL，导入后才是实际的基地址。

**rvaIAT** ：一个RVA,表示导入函数表，实际上指向IAT，在DLL加载前，IAT里存放的是一小段代码的地址，加载后才是真正的导入函数地址。

**rvaINT** ：一个RVA，指向导入函数的名字表。

**rvaUnloadIAT** ：延迟导入函数卸载表。

**dwTimeStamp** ：延迟导入DLL的时间戳。

延迟导入函数的实例：

    
    
    [cpp] view plaincopy
    
    .text:75C7A363 __imp_load__InternetConnectA@32:        ; InternetConnectA(x,x,x,x,x,x,x,x)  
    .text:75C7A363                 mov     eax, offset __imp__InternetConnectA@32  
    .text:75C7A368                 jmp     __tailMerge_WININET
    
    //第一行把导入函数IAT项的地址放到eax中，然后用一个jmp跳转走

追一下

    
    
    [cpp] view plaincopy
    
    __tailMerge_WININET proc near             
    .text:75C6BEF0                 push    ecx  
    .text:75C6BEF1                 push    edx  
    .text:75C6BEF2                 push    eax  
    .text:75C6BEF3                 push    offset __DELAY_IMPORT_DESCRIPTOR_WININET  
    .text:75C6BEF8                 call    __delayLoadHelper  
    .text:75C6BEFD                 pop     edx  
    .text:75C6BEFE                 pop     ecx  
    .text:75C6BEFF                 jmp     eax  
    .text:75C6BEFF __tailMerge_WININET endp

push 了一个 **DELAY_IMPORT_DESCRIPTOR_WININET** ，这个就是上文中看到的 ImgDelayDescr 结构，他的
DLL 名字是 **wininet.dll** 。之后，CALL了一个 **delayLoadHelper**
，在这个函数里，执行了加载DLL，查找导出函数，填充导入表等一系列操作，函数结束时IAT中已经是真正的导入函数的地址，这个函数同时返回了导入函数的地址，因此之后的eax里保存的就是函数地址，最后的
jmp eax 就跳转到了真实的导入函数中。

参数中为什么没有要导入函数的名字？？

**__DELAY_IMPORT_DESCRIPTOR_WININET** 中有一项是 **rvaIAT** ，这里实际上就是指向了IAT，而且是该模块
**第一个导入函数的IAT的偏移**
，现在我们有两个偏移，即将导入的函数IAT项的偏移(记作RVA1)和要导入模块第一个函数IAT项的偏移(记作RVA0)， **(RVA1-RVA0)/4 =
导入函数IAT项在rvaIAT中的下标**
，rvaINT中的名字顺序与rvaIAT中的顺序是相同的，所以下标也相同，这样就能获取到导入函数的名字了。有了模块名和函数名，用
GetProcAddress 就可以获取到导入函数的地址了。

![](./img/1024389229231623486.png)

ps：延迟导入的加载只发生在函数第一次被调用的时候，之后IAT就填充为正确函数地址，不会再走 __delayLoadHelper了。

延迟导入一次只会导入一个函数，而不是一次导入整个模块的所有函数。

#### 重定位表 IMAGE_BASE_RELOCATION

重定位相关信息见本文第一部分

Windows 使用重定位机制：

  1. 编译的时候由编译器识别出哪些项使用了模块内的直接VA，比如 push 一个全局变量、函数地址，这些指令的操作数在模块加载的时候就需要被重定位。
  2. 链接器生成PE文件的时候将编译器识别的重定位的项纪录在一张表里，这张表就是重定位表，保存在 DataDirectory中，序号是 IMAGE_DIRECTORY_ENTRY_BASERELOC。
  3. PE文件加载时，PE 加载器分析重定位表，将其中每一项按照现在的模块基址进行重定位。

存储方式：Windows采用了分组的方式，按照重定位项所在的页面分组，每组保存一个页面其实地址的RVA，页内的每项重定位项使用一个WORD保存重定位项在页内的偏移，这样就大大缩小了重定位表的大小。

定义：

    
    
    typedef struct _IMAGE_BASE_RELOCATION {
        DWORD   VirtualAddress;
        DWORD   SizeOfBlock;
    //  WORD    TypeOffset[1];
    } IMAGE_BASE_RELOCATION;
    typedef IMAGE_BASE_RELOCATION UNALIGNED * PIMAGE_BASE_RELOCATION;

**VirtualAddress** ：页起始地址RVA。

**SizeOfBlock** ：表示该分组保存了几项重定位项。

**TypeOffset** ： TypeOffset 是一个数组，数组每项大小为两个字节(16位)，它由高 4位和低 12位组成，高4位代表重定位类型，低
12位是重定位地址，它与 VirtualAddress 相加即是指向 PE 映像中需要修改的那个代码的地址。

符号 | 意义  
---|---  
IMAGE_REL_BASED_ABSOLUTE | 使块按照32位对齐,位置为0  
IMAGE_REL_BATED_HIGH | 高16位必须应用于偏移量所指高字16位  
IMAGE_REL_BASED_LOW | 低16位必须应用于偏移量所指低字16位  
IMAGE_REL_BASED_HIGHLOW | 全部32位应用于所有32位  
IMAGE_REL_BASED_HIGHADJ |
需要32位,高16位位于偏移量,低16位位于下一个偏移量数组元素,组合为一个带符号数,加上32位的一个数,然后加上8000然后把高16位保存在偏移量的16位域内  
IMAGE_REL_BASED_MIPS_JMPADDR |  
IMAGE_REL_BASED_SECTION |  
IMAGE_REL_BASED_REL32  
  
需要被重定位的项目：

  1. 代码中使用全局变量的指令，因为全局变量一定是模块内的地址，而且使用全局变量的语句在编译后会产生一条引用全局变量基地址的指令。
  2. 将模块函数指针赋值给变量或作为参数传递，因为赋值或传递参数是会产生mov和push指令，这些指令需要直接地址。
  3. C++中的构造函数和析构函数赋值虚函数表指针，虚函数表中的每一项本身就是重定位项

![](./img/3616978930316128270.png)

### PE文件资源

Windows程序的各种界面称为资源，包括加速键（Accelerator）、位图（Bitmap）、光标（Cursor）、对话框（Dialog
Box）、图标（Icon）、菜单（Menu）、串表（String Table）、工具栏（Toolbar）和版本信息（Version
Information）等。定义资源时，既可以使用字符串作为名称来标识一个资源，也可以通过ID号来标识资源

查看资源：resource_hacker

#### 资源分类

标准资源类型

![](./img/8554384084986516913.png)

非标准资源类型

若资源类型的高位如果为1，说明对应的资源类别是一个非标准的新类型

#### 资源结构

资源的组织方式比较复杂，采用类似磁盘目录结构的方式保存。PE 文件中的资源是按照 资源类型 -> 资源ID -> 资源代码页
的3层树型目录结构来组织资源的，通过层层索引才能够进入相应的子目录找到正确的资源。

资源表是一个四层的二叉排序树结构。每一个节点都是由资源目录结构和紧随其后的数个资源目录项结构组成的，两种结构组成了一个资源目录结构单元（目录块）

![](./img/5947943470936509945.png)

数据目录表中的IMAGE_DIRECTORY_ENTRY _RESOURCE 条目包含资源的RVA和大小。资源目录结构中的每一个节点都是由IMAGE_
RESOURCE_DIRECTORY 结构和紧跟其后的数个IMAGE_RESOURCE_DIRECTORY_ENTRY 结构组成的。

一级目录是按照资源类型分类的，如位图资源、光标资源、图标资源。

二级目录是按照资源编号分类的，同样是菜单资源，其子目录通过资源ID编号分类，例如：IDM_OPEN的ID号是2001h，IDM_EXIT的ID号是2002h等多个菜单编号。

三级目录是按照资源的代码页分类的，即不同语言的代码页对应不同的代码页编号，例如：简体中文代码页编号是2052。  
三级目录下是节点，也称为资源数据，这是一个IMAGE_RESOURCE_DATA_ENTRY的数据结构，里面保存了资源的RVA地址、资源的大小，对所有资源数据块的访问都是从这里开始的。

注：资源表的一级目录、二级目录、三级目录的目录结构是相同的都是由一个资源目录头加上一个资源目录项数组组成的，可以将这个结构称作资源目录结构单元。

##### IMAGE_RESOURCE_DIRECTORY

    
    
    typedef struct _IMAGE_RESOURCE_DIRECTORY {
        DWORD   Characteristics;      //属性，一般为0
        DWORD   TimeDateStamp;        //资源的产生时刻，一般为0
        WORD    MajorVersion;         //主版本号，一般为0
        WORD    MinorVersion;         //次版本号，一般为0
        WORD    NumberOfNamedEntries; //以名称(字符串)命名的资源数量
        WORD    NumberOfIdEntries;    //以ID(整型数字)命名的资源数量
    } IMAGE_RESOURCE_DIRECTORY, *PIMAGE_RESOURCE_DIRECTORY;

**NumberOfNamedEntries**
：表示在该资源目录头后跟随的资源目录项中以IMAGE_RESOURCE_DIR_STRING_U结构命名的资源目录项数量。

**NumberOfIdEntries** ：表示在该资源目录头后跟随的资源目录项中以ID命名的资源目录项数量。

在资源目录头结构中这两个字段是最为重要的，其他字段大部分为0。

两个字段加起来就是本资源目录头后的资源目录项的数量总和。也就是后面IMAGE_RESOURCE_DIRECTORY_ENTRY结构的总数量。

##### IMAGE_RESOURCE_DIRECTORY_ENTRY

    
    
    typedef struct _IMAGE_RESOURCE_DIRECTORY_ENTRY {
        union {
            struct {
                DWORD NameOffset:31;
                DWORD NameIsString:1;
            };
            DWORD   Name;
            WORD    Id;
        };
        union {
            DWORD   OffsetToData;
            struct {
                DWORD   OffsetToDirectory:31;
                DWORD   DataIsDirectory:1;
            };
        };
    } IMAGE_RESOURCE_DIRECTORY_ENTRY, *PIMAGE_RESOURCE_DIRECTORY_ENTRY;

**Name** ：目录项的名称字符串指针或ID

Name
字段定义的是目录项的名称或ID。当结构用于第一层目录时，定义的是资源类型，当结构定义于第二层目录时，定义的是资源的名称，当结构用于第三层目录时，定义的是代码页编号。  
注意:当最高位为 0 的时候，表示字段的值作为 ID 使用，而最高位为 1 的时候，字段的低位作为指针使用(资源名称字符串是使用
UNICODE编码)，但是这个指针不是直接指向字符串哦，而是指向一个IMAGE_RESOURCE_DIR_STRING_U 结构的。

**OffsetToData** ：目录项指针

OffsetOfData 字段是一个指针，当最高位为 1 时，低位数据指向下一层目录块的其实地址，当最高位为 0 时，指针指向IMAGE RESOURCE
DATA ENTRY 结构。  
注意:将 Name 和 OffsetToData 用做指针时需要注意，该指针是从资源区块开始的地方算起的偏移量 (即根目录的起始位置的偏移量)，不是 RVA
。

###### 第一层

起始于一个 IMAGE_RESOURCE_DIRECTORY 头，后面紧接着是 IMAGE_RESOURCE_DIRECTORY_ENTRY 数组。
**数组个数** = **NumberOfNamedEntries** \+ **NumberOfIdEntries** 。

IMAGE_RESOURCE_DIRECTORY_ENTRY 使用的是 Name 与
OffsetToDirectory，分别代表了资源类型与第二层的数据偏移地址。Name 与资源类型的匹配如下：

![](./img/6313182306603588145.png)

OffsetToDirectory 数据偏移地址是相对整个资源结构来说的，也就是说首个第一层的起始偏移地址加上 OffsetToDirectory
就是第二层的偏移地址。

###### 第二层

与第一层一样，第二层起始于一个IMAGE_RESOURCE_DIRECTORY头，后面紧接着是IMAGE_RESOURCE_DIRECTORY_ENTRY
数组。数组个数=NumberOfNamedEntries+NumberOfIdEntries。

IMAGE_RESOURCE_DIRECTORY_ENTRY使用的是N
**ameIsString、NameOffset、Id与OffsetToDirectory**
。其中OffsetToDirectory与第一层一样，代表了第三层的数据偏移地址，同样是相对整个资源结构来说的。如果NameIsString=1，说明该资源以名称(UNICODE编码的字符串)定义的，NameOffset是名称的相对整个资源结构的偏移地址。相反，如果NameIsString=0，说明该资源以ID(整型数字)定义的，ID号为Id。

NameOffset相对地址指向的是IMAGE_RESOURCE_DIR_STRING_U结构体，该结构体定义如下：

    
    
    typedef struct _IMAGE_RESOURCE_DIR_STRING_U {
        WORD    Length;           //字符串的长度
        WCHAR   NameString[ 1 ];  //UNICODE字符串，由于字符串是不定长的。由Length 制定长度
    } IMAGE_RESOURCE_DIR_STRING_U, *PIMAGE_RESOURCE_DIR_STRING_U;

###### 第三层

与前两层一样，第二层起始于一个IMAGE_RESOURCE_DIRECTORY头，后面紧接着是IMAGE_RESOURCE_DIRECTORY_ENTRY数组，但不同的是数组个数=1。

IMAGE_RESOURCE_DIRECTORY_ENTRY使用的是Name与OffsetToData，分别代表了资源语言类型与资源数据相对地址。Name是指语言内码，比如936代表简体中文。

OffsetToData是相对整个资源结构的偏移地址，指向一个IMAGE_RESOURCE_DATA_ENTRY结构体，该结构体定义如下：

    
    
    typedef struct _IMAGE_RESOURCE_DATA_ENTRY {
        DWORD   OffsetToData;  //资源数据的RVA
        DWORD   Size;          //资源数据的长度
        DWORD   CodePage;      //代码页, 一般为0
        DWORD   Reserved;      //保留字段
    } IMAGE_RESOURCE_DATA_ENTRY, *PIMAGE_RESOURCE_DATA_ENTRY;

