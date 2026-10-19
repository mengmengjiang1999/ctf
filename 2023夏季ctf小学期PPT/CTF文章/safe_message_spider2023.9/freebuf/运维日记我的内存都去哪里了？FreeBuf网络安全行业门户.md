在疫情期间，一位客户给美创运维中心工作人员发来了一条消息：张工，好像我这个数据库服务器的内存使用率有点高啊，你帮我看看？

随即发了个linux环境下的free -g的截图过来：

![](https://image.3001.net/images/20200817/1597631503.png!small)

按照这个截图的显示，的确在总共62Gb的内存里，可使用内存只剩1Gb了。但是，我们也可以观察到，cached显示的是55Gb，我们再获取了一下top命令的截图：

![](https://image.3001.net/images/20200817/1597631521.png!small)

那为什么cached的内存使用这么大呢？这样的内存使用情况是正常的吗？

要回答这些问题，我们需要了解一下buffer与cache的含义。buffer 和 cache
是两个在计算机技术中被用滥的名词，放在不同语境下会有不同的意义。我们这里都将其放在linux内存这个语境中解释。

在 Linux 的内存管理中，这里的buffer 指 Linux 内存的：Buffer cache，中文可以解释为： **缓冲区缓存** 。Buffer
cache 主要是设计用来在系统对块设备进行读写的时候，对块进行数据缓存的系统来使用。

在Linux的内存管理中，这里的 cache 指 Linux 内存中的：Page cache，中文可以解释为： **页面缓存**
。主要用来作为文件系统上的文件数据的缓存来用，尤其是针对当进程对文件有 read／write 操作的时候。在当前的系统实现里， page cache
也被作为其它文件类型的缓存设备来用，所以事实上 page cache 也负责了大部分的块设备文件的缓存工作。

##  **自动回收 cache机制**

Linux 内核会在内存将要耗尽的时候，触发内存回收的工作，以便释放出内存给急需内存的进程使用。一般情况下，在内存压力较大的情况下，
buffer/cache 空间可以被释放，以作为 free 空间分给相关进程使用。

但是由于要回收缓存必须保证 cache 中的数据跟对应文件中的数据一致，才能对 cache
进行释放。所以在回收缓存时一般会造成IO使用较高的现象。因为内核要对比 cache
中的数据和对应硬盘文件上的数据是否一致，如果不一致需要写回，之后才能回收。

所以一般情况下不需要特意去释放已经使用的cache。这些cache起来的内容本来就是为了增加文件以及的读写速度。

除了系统自己触发回收缓存机制外，我们也可以通过下面这个脚本来清理缓存：

1\. 查看目前内存使用：

![](https://image.3001.net/images/20200817/1597631565.png!small)

2\. 执行sync同步数据，防止数据或操作丢失（重要），将未写的系统缓冲区写到磁盘中。包含已修改的 i-node、已延迟的块 I/O 和读写映射文件

3\. 使用/proc/sys/vm/drop_caches 清理cache

![](https://image.3001.net/images/20200817/1597631637.png!small)

4\. 查看清理后内存使用情况

![](https://image.3001.net/images/20200817/1597631655.png!small)

可以看到一大部分cached已被回收。

drop_caches详细文档如下：

该文件可以设置的值分别为1、2、3。它们所表示的含义为：

echo 1 > /proc/sys/vm/drop_caches：表示清除 page cache。

echo 2 > /proc/sys/vm/drop_caches：表示清除回收 slab 分配器中的对象（包括目录项缓存和 inode 缓存）。slab
分配器是内核中管理内存的一种机制，其中很多缓存数据实现都是用的 page cache。

echo 3 > /proc/sys/vm/drop_caches：表示清除 page cache 和 slab 分配器中的缓存对象。

（只有内核在2.6.16以上的才支持）

内核版本查看方法如下：

![](https://image.3001.net/images/20200817/1597631672.png!small)

"Slab"表示内核Slab所占用的内存大小，slab有的可回收有的不可回收，其中可回收的通过"SReclaimable"表示，不可回收的通过"SUnreclaim"表示。

我们可以查看/proc/meminfo获取它的值：

![](https://image.3001.net/images/20200817/1597631690.png!small)

所以一般情况下，人工drop_caches操作是不能回收所有page cache的，它有三块缓存是无法回收的：

1\. dirty pages

2\. Slab中的不可回收缓存

3\. 共享内存和tmpfs，即free命令中的shared部分

在正常的业务数据库系统中，cached较高是一件比较普遍的事情，尽量不要去手动清缓存，毕竟它是为了提高效率而产生的，如果冒然释放缓存会造成IO使用率变高，业务系统的效率也会受影响。

