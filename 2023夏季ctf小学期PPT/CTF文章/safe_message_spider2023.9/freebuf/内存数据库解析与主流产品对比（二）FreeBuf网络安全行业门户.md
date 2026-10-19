作者：实验室小陈/大数据开放实验室

在上一篇文章[《内存数据库解析与主流产品对比（一）》](http://mp.weixin.qq.com/s?__biz=MzIzNzU0ODEwOA==&mid=2247487789&idx=1&sn=7872b03b049c600c8ef3123c0b36de89&chksm=e8c7b60edfb03f1894e6e7b2ec2d8d90a96ba001ceb379bb3723c09391b74409a5a1fcab2d83&scene=21#wechat_redirect)中，我们介绍了基于磁盘的数据库管理系统相关知识，并简述了内存数据库的技术发展。本篇文章将从数据组织和索引的角度来介绍内存数据库的特点，并介绍几款产品实际的技术实现。

##  **数据库管理系统中的数据组织**

###  **定长Block VS 变长Block**

内存数据库在内存中对数据进行管理时，虽然不再需要通过Slotted
Page的形式对数据进行组织，但也不能在内存中任意为数据分配地址空间，依然需要把数据组织成块（Block/Page）的形式。传统基于磁盘的DBMS采用Slotted
Page的形式组织数据是为了读写性能的考虑，因为磁盘接口是以Block/Page为读写单位。而内存数据库采用块的方式组织数据是为了便于寻址和管理，通常会将数据块分为定长数据块（Fixed-Length Data Block）和变长数据块(Variable-Length Data Block)两种。

假设一个数据集已经全部被加载进内存，为了使用方便，内存数据库在进行数据组织时会把记录的定长的属性全部分出来，放到定长数据块；所有变长的属性保存在另外的变长数据块中。例如，通常将数据表中所有小于8个字节的属性都放在定长数据块中，将变长属性和超过8个字节的属性单独放在变长数据块中，并在定长数据块中放一个指向其地址的指针。采用定长数据块管理数据的好处是寻址快，可以通过记录长度和编号确定记录在数据块中存储的位置；记录地址指针所需要的空间少，使得索引结构或其他结构中存放这条记录的内存地址最为精简，并且CPU做Pre-Fetch时预测较准。

在传统基于磁盘的DBMS中，索引叶子节点保存的记录地址是Page ID + Offset，Page Table负责将Page
ID映射到Buffer的Frame；内存数据库中，索引的叶子节点保存的记录地址则是直接的内存地址。在传统基于磁盘的DBMS中，访问Buffer中的Page时需要对Page进行加锁/解锁/修改锁的操作，由于现实系统中锁（Latch）的类型可能会很多，一个线程如果要访问一个Page，往往要加好几种类型的Latch。现在内存数据库中没有了Buffer，因此就省去了Latch的开销，性能上有很大提升。

 **数据组织：数据分区、多版本、行/列存储**

在多核或多CPU共享内存的系统中，对数据的并发访问冲突是始终存在的。目前的内存数据库系统可以分为 **Partition System** 和 **Non-Partition System** 两种。Partition
System是把所有的数据切分成互不相交的多个Partition，每一个Partition被分配给一个核（或分布式系统中的一个节点），所有操作都是串行执行，没有并发的数据访问，理想情况下可以获得最好的性能。但这类系统的缺点也很明显，例如如何划分Partition以及跨Partition的事务怎么处理等。对于Non-Partition
System，所有的核以及所有的线程都可以访问所有的数据，因此一定会存在并发访问冲突，必须采用支持并发访问的数据结构。目前，通用数据库更多的是采用Non-Partition System设计，之所以不采用Partition设计的主要原因是：通用场景下很难对数据进行有效分区，Partition数据库无法使用。

在Non-Partition System中，如果两个线程访问同一个数据项会发生冲突，这时可以考虑Multi-Version的解决方案。Multi-Version的优势在于可以提高并发程度，其基本的思想是通过多版本的数据让所有的读操作不阻塞写操作，从而提高整个系统的性能。对于那些读多写少的系统，Multi-Version性能会很好，但对于一些Write Heavy的系统，性能并不理想。

数据组织还有一个需要考虑的是Row和Column的组织形式。传统数据库系统在磁盘上维护数据时，分为行式存储和列式存储。顾名思义，行式存储是按行存储数据，列式存储是按列存储数据。如果对少量记录的所有属性进行操作，行式存储更加合适，如果只读大量记录的部分列数据，则列式存储性能比较好。比如一条记录有100个属性，本次读操作需要读取所有记录的其中一个属性，如果按行存储，Block读进来后还需要再筛选列；如果按列存储，可以只读取这列数据所对应的Block，所以性能会比较好，适合去做统计分析。但内存数据库不会有这个问题，所有数据都放在内存，无论行存还是列存，访问的代价是差不多的。所以在内存数据库中，行存/列存是可以做交换或任意选择的。当然对于TP应用而言，更多的还是用行存，因为可以一次性把所有属性都读出来。但即使是列存，性能也并没有在基于磁盘的数据库系统中那么糟糕。比如SAP
HANA就是一个行列混合的存储，前端的事务引擎是行存储，通过合并整合以后，后端转为了列存储。

##  **内存数据库系统对比**

接下来从数据组织的角度，简要介绍一下4个具有代表性的系统：SQL
Server的内存数据库引擎Hekaton、慕尼黑工业大学的内存数据库系统HyPer、SAP的HANA、图灵奖获得者Michael
Stonebraker的H-Store/VoltDB。

![1606443335_5fc06147c19ba5e240381.png!small?1606443338855](https://image.3001.net/images/20201127/1606443335_5fc06147c19ba5e240381.png!small?1606443338855)

###  **Hekaton**

Hekaton是一个Non-Partition的系统，所有线程都可以访问任意数据。Hekaton的并发控制不采用基于锁的协议，而是利用多版本机制实现，每条记录的每个版本都有开始时间戳和结束时间戳，用于确定该版本的可见范围。

Hekaton中每一张表最多有8个索引，可以是Hash或者Range索引。同时，所有记录版本在内存中不要求连续存储，可以是非连续存储（No-Clustering），通过指针（Pointer Link）将同一记录的不同版本关联起来。

![1606443360_5fc06160569385d203388.png!small?1606443363411](https://image.3001.net/images/20201127/1606443360_5fc06160569385d203388.png!small?1606443363411)

上图所示，图中有一个包含姓名、城市和金额字段的表，姓名字段上有一个Hash索引，城市字段上有一个B-Tree索引。黑色箭头代表姓名索引对应的指针，名字John对应的第一条记录，指向下一个具有相同开头字母名字的记录。每条记录包含有开始和结束时间戳，红色表示存在一个事务正在更新记录，事务提交后会替换结束的时间戳。B-Tree索引也是同理，蓝色箭头指针按照城市值串联。

###  **H-Store/VoltDB**

H-Store/VoltDB是Partition
System，每个Partition部署在一个节点，每个节点上的任务串行执行。H-Store/VoltDB没有并发控制，但有简单的锁控制。一个Partition对应一把锁，如果某事务要在一个Partition上执行，需要先拿到这个Partition的锁，才能开始执行。为了解决跨Partition执行问题，H-Store/VoltDB要求Transaction必须同时拿到所有相关Partition的锁才能开始执行，相当于同时锁住所有与事务相关的Partition。

H-Store/VoltDB采用两层架构：上层是 **Transaction Coordinator**
，确定Transaction是否需要跨Partition执行；下层是 **执行引擎** 负责数据的存储、索引和事务执行，采用的是单版本的行存结构。

H-Store/VoltDB中的数据块分为定长和变长两类：定长数据块的每条记录长度都相同，索引中采用8字节地址指向每条记录在定长数据块中的位置；变长属性被保存在变长数据块中，在定长数据块的记录中对应一个指针（Non-Inline Data），指向其在变长数据块中具体的位置。在这种数据组织方式下，可以用一个压缩过的Block Look-Up
Table来对数据记录进行寻址。

![1606443388_5fc0617c04d18d170e11a.png!small?1606443391168](https://image.3001.net/images/20201127/1606443388_5fc0617c04d18d170e11a.png!small?1606443391168)

###  **HyPer**

HyPer是多版本的Non-Partition
System，每个Transaction可以访问任何数据。同时HyPer是针对于HTAP业务建立的TP和AP混合处理系统。HyPer通过 **Copy on
Write**
机制实现TP和AP混合处理。假设当前系统正在对数据集做事务处理，此时如果出现AP请求，HyPer会通过操作系统的Fork功能对数据集做Snapshot，随后在快照上面做分析。Copy
on
Write机制并不会对内存中的所有数据进行复制，只有因OLTP业务导致数据发生变化时，快照才会真正拷贝出原数据，而没有变化的数据则通过虚拟地址引用到相同的物理内存地址。

![1606443408_5fc0619033b8d7e5f66a4.png!small?1606443411305](https://image.3001.net/images/20201127/1606443408_5fc0619033b8d7e5f66a4.png!small?1606443411305)

此外，Hyper采用多版本控制，所有更新都是基于原记录的，每条记录都会维护一个Undo Buffer存储增量更新数据，并通过Version
Vector指出当前最新版本。因此，可以通过Transaction找到被修改过的记录，同时可以通过反向应用增量数据来找回修改前的版本，当然也可以对数据版本进行定期融合或恢复等操作。

![1606443430_5fc061a6dc690f0d34a8d.png!small?1606443434448](https://image.3001.net/images/20201127/1606443430_5fc061a6dc690f0d34a8d.png!small?1606443434448)

###  **SAP HANA**

SAP HANA是一个Non-Partition的混合存储系统，物理记录在存储介质中会经过三个阶段：1.
事务处理的记录存储在L1-Delta（行存方式）；2. 随后记录转化为列式并存储在L2-Delta（列式存储、未排序字典编码）；3. SAP
HANA的主存是列存（高度压缩并采用排序字典编码）。每条记录经历着从行存到列存的映射合并，相当于一个多版本设计。

![1606443456_5fc061c0e4a0fea52f410.png!small?1606443459980](https://image.3001.net/images/20201127/1606443456_5fc061c0e4a0fea52f410.png!small?1606443459980)

##  **数据库管理系统中的索引技术**

内存数据库领域在设计索引时，主要是从面向缓存的索引技术（Cache-Awareness）和多核多CPU的并行处理（Multi-Core and Multi-Socket Parallelism）两方面进行考虑。

由于内存数据库不再有磁盘的I/O限制，因此索引目的转变为加速CPU和内存之间的访问速度。虽然现在内存价格较低，但是内存速度的增速与CPU主频的增速相差依然较多，因此对于内存数据库，索引技术的目的是及时给CPU供数，以尽量快的速度将所需数据放入CPU的Cache中。

对于多核多CPU的并行处理，80年代就开始考虑如果数据结构和数据都放在内存中，应该如何合理的构造索引。其中，1986年威斯康星大学的MM-DBMS项目提出了自平衡的二叉搜索树T-Tree索引，每个二叉节点中存储取值范围内的数据记录，同时有两个指针指向它的两个子节点。T-Tree索引结构内存开销较小，因为在80年代内存昂贵，所以主要的度量不在于性能是否最优，而是是否占用最小内存空间。T-Tree的缺点是性能问题，需要定期地做负载平衡，并且扫描和指针也会对其性能产生影响。早期商业系统如Times
Ten中，采用的便是T-Tree的数据结构。

那么索引的设计为什么需要考虑Cache-Awareness呢？1999年有研究发现内存访问中的Cache Stall或者Cache
Miss是内存系统最主要的性能瓶颈。该研究进行了一项性能测试，通过对A/B/C/D
4个系统评测，测试以下过程的时间占比：Computation、Memory Stalls、Branch Mispredicitons和Resource
Stalls。Computation表示真正用于计算的时间；Memory Stall是等待内存访问的时间；Branch
Mispredicitons是指CPU指令分支预测失败的开销；Resource Stalls是指等待其他资源的时间开源，如网络、磁盘等。

![1606443513_5fc061f993ced15d46d9c.png!small?1606443516659](https://image.3001.net/images/20201127/1606443513_5fc061f993ced15d46d9c.png!small?1606443516659)

可以看到Memory Stall在不同的测试场景都会占据较大比例开销。因此对于内存索引结构来说，发展面向缓存的索引的主要目的就是为了减少Memory
Stall的开销。

###  **CSB+-Tree**

这里介绍几个典型的内存索引结构例子。第一个是CSB+-Tree，它在逻辑上仍然是B+-Tree，但是做了一些变化。首先每个Node的大小是一个Cache
Line长度的倍数；同时CSB+-Tree将一个节点的所有的子节点组织成Children Group，一个父节点通过一个指针指向它的Children
Group，目的是减少数据结构中的指针数量。因为CSB+-Tree的节点与Cache Line长度相匹配，只要依序读取，就可以达到较好的pre-fetche性能。当树分裂时，CSB+-Tree会对内存中的Group重新分配位置，因为CSB+-Tree节点在内存中不需要连续，排好后再创建新的指针链接就可以。

![1606443540_5fc06214e98627a86e8e6.png!small?1606443544058](https://image.3001.net/images/20201127/1606443540_5fc06214e98627a86e8e6.png!small?1606443544058)

###  **PB+-Trees**

另一个例子是PB+-Trees（Pre-fetching B+-Tree）。它并不是新的结构，只是在内存中实现了B+-Tree，每个节点的大小等于Cache
Line的长度倍数。PB+-Trees比较特殊的是在整个系统实现过程中，引入了Pre-fetching，通过加入一些额外信息帮助系统预取数据。

PB+-Trees倾向于采用扁平的树来组织数据，论文中给出了它Search和Scan的性能，其中Search性能提高1.5倍，Scan上提高了6倍。处理Search时的性能相比CSB+-Tree，PB+-Trees的Data
Cache Stalls占比更小。

另外一个性能对比是，当没有采用预取时，读取一个Node大小等于两个Cache
Line的三级索引需要900个时钟周期，而加了预取后仅需要480个周期。PB+-Trees还有一个实现是，它会在每个节点加上Jump Pointer
Array，用来判断做扫描时要跳过多少Cache Line以预取下一个值。

![1606443566_5fc0622e348573512e575.png!small?1606443569353](https://image.3001.net/images/20201127/1606443566_5fc0622e348573512e575.png!small?1606443569353)

###  **Bw-Tree**

Bw-Tree是Hekaton系统中使用的索引，基本思想是通过Compare-and-Swap指令级原子操作比较内存值，如果新旧值相等就更新，如果不等则不更新。比如原值为20（存储在磁盘），而内存地址对应30，那么要是把30更新成40就不会成功。这是一个原子操作，可用于在多线程编程中实现不被打断的数据交换操作。

Bw-Tree中存在Mapping Table，每一个节点都在Mapping Table中有一个存储位置，Mapping
Table会存储节点在内存中的地址。对于Bw-Tree来讲，从父节点到子节点的指针并不是物理指针，而是逻辑指针，也就是记录在Mapping
Table中的位置并不是真正的内存位置。

![1606443592_5fc062486de6523b42dd6.png!small?1606443595508](https://image.3001.net/images/20201127/1606443592_5fc062486de6523b42dd6.png!small?1606443595508)

Bw-Tree采用的设计是节点的更新并不是直接修改节点，而是通过增加Delta Record（增量记录）来保存修改的内容，然后在Mapping
Table中指向Delta Record，如果有新的更新就继续指向新的Delta Record。在读取一个节点的内容时，实际上是合并所有的Delta
Record。因为对Bw-Tree的更新是通过一个原子操作来实现的，发生竞争时只有一个改动能成功，因此是一种Latch-Free结构，只需要靠Compare-and-Swap就能够解决竞争问题，不再需要依赖锁机制。

###  **Adaptive Radix Tree**

Hyper的索引树的设计采用了Adaptive Radix Tree。传统Radix
Tree是一个前缀树，其优势是树的深度不依赖于被索引的值的个数，而是靠Search
Key的长度来决定。它的缺点是每一个节点都要维护可能取值的子节点的信息，导致每个节点的存储开销较大。

而在Adaptive Radix
Tree中，为每个节点提供了不同类型长度的格式，分别可以保存4/16/48/256等不同个数的子节点。Node4为最小的节点类型，最多可存储4个子节点指针，
Key用来表示节点所存储的值，指针可以指向叶子节点，也可以指向下一层内部节点。Node16 和Node4 结构上一致，但 Node16 可以存放16个
unsigned char 和16个指针，在存放第17个key时则需要将其扩大为 Node48。Node48结构上和 Node4/16
有所不同，有256个索引槽和48个指针，这256个索引槽对应 unsigned char 的0-255，每个索引槽的值对应指针的位置，分别为
1-48，如果某个字节不存在的话，那么它的索引槽的值就是0。当存放第49个key byte 时需要将其扩大为
Node256。Node256结果较为简单，直接存放256个指针，每个指针对应 unsigned char 的0-255 区间。

比如说在这个例子里，我们要索引一个整数（+218237439），整数的二进制表示形式为32位，随后将32位bit转换为4个Byte，这4个byte十进制表示为13、2、9、255，这就是它的Search
Key。在索引树中，第一层为Node 4，13符合这一层的存储要求，于是就保留在第一层节点上，后面的位数则进入下一层存储，下一层为Node
48，用来存储2；接下来的每一位都存储到下面的每一层。由于本例子中整数为4个字节表示，故共有4层。可以看到，每个节点的结构是不一样的，根据字节位数和顺序逐一存储，数值在这一层目前有多少个不同的值，就选择什么类型的节点。如果当前类型的不够用，可以再增加个数，每个节点可以容纳的
key 是动态变化的，这样既可以节省空间，又可以提高缓存局部性。

![1606443623_5fc0626767bba3e2dead2.png!small?1606443628427](https://image.3001.net/images/20201127/1606443623_5fc0626767bba3e2dead2.png!small?1606443628427)

另外Adaptive Radix还采用了路径压缩机制，如果一条路径的父节点只有一个子节点就会将之压缩合并。Adaptive
Radix之所以采用这样的索引结构，是因为每个节点的大小都等于一个Cache Line，所有操作可以在一个Cache Line的基础上实现。

###  **OLFIT on B+-Trees**

OLFIT on B+-Trees（Optimistic Latch Free Index Access
Protocol）是HANAP*Time采用的索引技术，能够在多核数据库上保证CPU的Cache
Coherence。在多处理器计算机的体系结构中，多个CPU的Cache会缓存同一内存的数据。在内存数据库中，存储的数据会先读到对应Cache再处理；如果缓存数据处理过程中内存数据发生变化，那Cache的数据会因与内存数据不一致而失效，Cache
Coherence就是解决这个不同步的问题。

考虑这样一个场景：如下图所示，内存中有一个树形数据结构，由4个CPU处理，每个CPU有自己的Cache。假设CPU-P1先读了n1、n2、n4，Cache中便有了n1、n2、n4。随后CPU-P2读n1、n2和n5时，假设这个数据结构不是Latch-Free，如果在读的同时且允许修改，就需要一个Latch来在读的时候上锁，读完再释放。因为内存数据库中Latch和数据放在一起，数据虽然没有变化，但是Latch的状态发生了改变，计算机的硬件结构会认为内存发生了变化。所以，当多个CPU读同样的数据时，只有最后一次读取状态是有效的，前序的读取会被认为失效。这就会出现即使都是进行读操作，但是因为Latch状态改变导致CPU的Cache失效。因此OLFIT设计了一套机制，要求写操作申请Latch，读操作不需要。OLFIT通过版号维护读写事务，每个CPU读前先把版本号拷贝到本地寄存器，然后等读完数据后，再判断此时版本号跟读前的是否一样。如果一样就继续正常执行，不一样就说明Cache失效。因此，读请求不会引起其他CPU的Cache失效。

![1606443656_5fc06288965db1074c41e.png!small?1606443659807](https://image.3001.net/images/20201127/1606443656_5fc06288965db1074c41e.png!small?1606443659807)

通过这个例子可以看到，内存数据库考虑的问题和基于磁盘的数据库是不一样的，没有了磁盘I/O的因素，就需要考虑其他方面对性能的限制。

###  **Skiplists**

Skiplists是MemSQL的数据处理引擎所用到的技术，它的最底层是一个有序的列表，上层按照一定的概率（P-value）抽取数据，再做一层列表。进行大列表搜索时，从最上层开始一层层递进，类似于二分查找，粒度可以根据实际情况自定义。之所以这样设计是因为所有对列表的插入操作，都是可以通过Compare-and-Swap原子操作完成，从而省去了锁的开销。

![1606443680_5fc062a0f0da2ce227a65.png!small?1606443684074](https://image.3001.net/images/20201127/1606443680_5fc062a0f0da2ce227a65.png!small?1606443684074)

##  **本文小结**

本文首先介绍了内存数据库的数据组织，分别从数据划分，Partition/Non-Partition的系统差异和存储方式进行介绍，并对比了四款产品的实际实现。随后，介绍了六种内存数据库系统的索引技术，并通过例子简述了索引查询原理。下一篇文章将继续对内存数据库进行剖析，从并发控制、持久化存储和编译查询的角度，讨论内存数据库对于查询性能和可用性的优化设计。

 **注：本文相关内容参照以下资料：**

1\. Pavlo, Andrew & Curino, Carlo & Zdonik, Stan. (2012). Skew-aware automatic
database partitioning in shared-nothing, parallel OLTP systems. Proceedings of
the ACM SIGMOD International Conference on Management of Data. DOI:
10.1145/2213836.2213844.

2\. Kemper, Alfons & Neumann, Thomas. (2011). HyPer: A hybrid OLTP&OLAP main
memory database system based on virtual memory snapshots. Proceedings -International Conference on Data Engineering. 195-206. DOI:
10.1109/ICDE.2011.5767867.

3\. Faerber, Frans & Kemper, Alfons & Larson, Per-Åke & Levandoski, Justin &
Neumann, Tjomas & Pavlo, Andrew. (2017). Main Memory Database Systems.
Foundations and Trends in Databases. 8. 1-130. DOI: 10.1561/1900000058.

4\. Sikka, Vishal & Färber, Franz & Lehner, Wolfgang & Cha, Sang & Peh, Thomas
& Bornhövd, Christof. (2012). Efficient Transaction Processing in SAP HANA
Database –The End of a Column Store Myth. DOI: 10.1145/2213836.2213946.

5\. Diaconu, Cristian & Freedman, Craig & Ismert, Erik & Larson, Per-Åke &
Mittal, Pravin & Stonecipher, Ryan & Verma, Nitin & Zwilling, Mike. (2013).
Hekaton: SQL server's memory-optimized OLTP engine. 1243-1254. DOI:
10.1145/2463676.2463710.

——————————————————————————————————————————————

