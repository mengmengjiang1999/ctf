![](https://image.3001.net/images/20210428/1619610514_60894b924d39bd1c62819.png!small)

## IPCDump

IPCDump这款工具可以帮助广大研究人员在Linux操作系统上跟踪进程间通信（IPC）。该工具覆盖了大多数常见的IPC机制，比如说管道、FIFO、Unix套接字、基于环回的网络和伪终端等等。

该工具有助于研究和调试多进程引用程序，而且还可以帮助了解操作系统通信过程中不同组件之间的关联。IPCDump可以跟踪此通信的元数据和内容，它特别适合在短生命周期的进程之间跟踪IPC，而这种任务对于传统的调试工具来说比较困难，如strace或gdb。它还有一些基本的过滤功能，可以帮助你筛选大量的事件。IPCDump收集的大部分信息来自放置在内核中关键函数的kprobes和跟踪点上的BPF钩子。为此，IPCDump使用了gobpf，它可以为bcc框架提供Golang绑定功能。

## 功能介绍

  * 支持管道和FIFO；
  * 回环IPC；
  * 信号（常规和实时）；
  * Unix流和数据图表；
  * 基于伪终端的IPC；
  * 基于进程PID或进程名的事件过滤器；
  * 可读性高或JSON格式的输出数据；

## 工具要求&使用

  * Golang >= 1.15.6

### 已测试平台和内核

软件版本

|

Ubuntu 18.04 LTS

|

Ubuntu 20.04 LTS  
  
---|---|---  
  
4.15.0

|

已测试

|

未测试  
  
5.4.0

|

未测试

|

已测试  
  
5.8.0

|

未测试

|

已测试  
  
## 工具构建

### 依赖组件

首先，我们需要安装Golang：

    
    
    snap install go --classic

接下来，在操作系统上安装好BCC即可。

### 构建IPCDump

    
    
    git clone https://github.com/guardicore/IPCDump
    
    cd IPCDump/cmd/ipcdump
    
    go build

## 工具使用

    
    
    ./ipcdump -h
    
    Usage of ./ipcdump:
    
      -B uint
    
            max number of bytes to dump per event, or 0 for complete event (may be large). meaningful only if -x is specified.
    
      -D value
    
            filter by destination comm (can be specified more than once)
    
      -L    do not output lost event information
    
      -P value
    
            filter by comm (either source or destination, can be specified more than once)
    
      -S value
    
            filter by source comm (can be specified more than once)
    
      -c uint
    
            exit after <count> events
    
      -d value
    
            filter by destination pid (can be specified more than once)
    
      -f string
    
            <text|json> output format (default is text) (default "text")
    
      -p value
    
            filter by pid (either source or destination, can be specified more than once)
    
      -s value
    
            filter by source pid (can be specified more than once)
    
      -t value
    
            filter by type (can be specified more than once).
    
            possible values: a|all  k|signal  u|unix  ud|unix-dgram  us|unix-stream  t|pty  lo|loopback  lt|loopback-tcp  lu|loopback-udp  p|pipe
    
      -x    dump IPC bytes where relevant (rather than just event details).

### One-liner

以Root权限运行：

    
    
    # 导出目标系统中所有的IPC
    
    ./ipcdump
    
     
    
    # 导出任意两个进程间的通信信号
    
    ./ipcdump -t kill
    
     
    
    # 导出跟PID 1337相关的所有回环TCP连接
    
    ./ipcdump -t loopback-tcp -p 1337
    
     
    
    # 导出Unix套接字IPC元数据和内容
    
    ./ipcdump -t unix -x -S Xorg
    
     
    
    # 导出JSON格式的管道I/O元数据和前64字节的数据内容
    
    ./ipcdump -t pipe -x -B 64 -f json

## 项目地址

 **IPCDump：** https://github.com/guardicore/IPCDump

## 参考资料

  * https://www.guardicore.com/labs/ipcdump-guardicores-new-open-source-tool-for-linux-ipc-inspection/
  * https://github.com/iovisor/gobpf
  * https://github.com/iovisor/bcc
  * https://golang.org/dl/
  * https://github.com/iovisor/bcc/blob/master/INSTALL.md

