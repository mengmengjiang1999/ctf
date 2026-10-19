**今天给大家介绍的是一款名叫 HeapViewer 的 IDA Pro 插件，它是一款专注于漏洞利用开发的工具，可用于对 glibc 堆进行测试。**

![](https://image.3001.net/images/20180513/15262226087497.png!small)

##  工具要求

IDA PRO>= 6.9

glibc<= 2.27（x86，x64）

注：HeapViewer 当前仅支持 glibc malloc（ptmalloc2）。

##  功能介绍

> 1\. 堆栈跟踪（malloc/free/calloc/realloc）
>
> 2\. 查看区块分配信息
>
> 3\. Bin 信息查看（fastbins,unsortedbin, smallbins y largebins）
>
> 4\. Tcache 信息查看（glibc >= 2.26）
>
> 5\. 图形化信息查看（bins/tcache）
>
> 6\. 等等…

##  工具安装

直接将 heap_viewer.py 文件和 heap_viewer 文件夹拷贝到 IDA 的插件目录（plugin）中即可。

因为 IDA 并不会在调试会话中加载 libc-dbg 符号，所以在使用该插件之前需要生成一份配置文件（config.json）。首先，需要在远程
Linux 设备中安装 libc6-dbg 包，并执行脚本 utils\get_config.py。接下来，将生成的内容拷贝到
heap_viewer\config.json 文件中。

    
    
    get_config.py
    
        $python get_config.py
    
        [*]config.json:
    
        {
    
          "libc_offsets": {
    
            "32": {
    
              "mp_": 1921312,
    
              "main_arena": 1922976,
    
            },
    
            "64": {
    
              "mp_": 3883648,
    
              "main_arena": 3886144,
    
            }
    
          },
    
          "libc_version": "2.27"
    
        }

如果你没有给定 libc 的 dbg 符号，你可以选择使用 get_main_arena 工具，然后拿到给定 libc 的 main_arena
偏移量，最后把 main_arena 偏移量写入 config.json 文件即可，这样就可以保证插件能够正常工作了。

###  样本：

    
    
    $./main_arena_offset
    [*]libc version:       2.27
    [*]libc file:         /lib/i386-linux-gnu/libc-2.27.so
    [*]libc address:       0xf7ceb000
    [*]main_arena:         0xf7ec07a0
    [*]main_arena offset:  0x1d57a0
    $LD_PRELOAD=./libc_64.so.6 ./main_arena_offset
    ...  
    

##  工具截图

堆栈跟踪器：

![](https://image.3001.net/images/20180513/15262226652645.png!small)

Arena&区块信息：

![](https://image.3001.net/images/20180513/15262226652817.png!small)

Tcache 实体：

![](https://image.3001.net/images/20180513/15262226655867.png!small)

Bins 信息查看：

![](https://image.3001.net/images/20180513/15262226662114.png!small)

Bin 数据图

![](https://image.3001.net/images/20180513/15262226667319.png!small)

Fastbin 数据图：

![](https://image.3001.net/images/20180513/1526222666163.png!small)

Tcache 信息图

![](https://image.3001.net/images/20180513/15262226665995.png!small)

查看 fake fastbin：

![](https://image.3001.net/images/20180513/1526222666352.png!small)

合并信息查看：

![](https://image.3001.net/images/20180513/15262226661338.png!small)

有用的 libc 偏移量：

![](https://image.3001.net/images/20180513/15262226662285.png!small)

##  工具开发者

Daniel García Gutiérrez - @danigargu

###  工具下载

HeapViewer：【[点我下载](https://github.com/danigargu/heap-viewer)】

 *** 参考来源：[heap-viewer](https://github.com/danigargu/heap-viewer)，FB 小编
Alpha_h4ck 编译，转载请注明来自 FreeBuf.COM**

