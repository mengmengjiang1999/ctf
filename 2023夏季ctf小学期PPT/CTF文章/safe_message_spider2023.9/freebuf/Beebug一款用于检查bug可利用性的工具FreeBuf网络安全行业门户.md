****

**![Beebug：一款用于检查bug可利用性的工具](https://image.3001.net/images/20180912/1536705728_5b9844c00be32.png!small)**

**beebug是一款用于检查bug可利用性的工具。该工具发布于上周在巴塞罗那举行的[r2con
2018](https://rada.re/con/2018/)会议上。**

 **以下是一些已实现的功能：**

> libc堆栈溢出
>
> 程序计数器崩溃
>
> branch崩溃
>
> 写内存崩溃
>
> 堆漏洞
>
> 读取访问冲突（一些可利用的用例）
>
> 崩溃分析（视图）

 **依赖包**

> r2pipe
>
> pydot
>
> graphviz
>
> pyqtgraph

## 安装

    
    
    ~ $ wget https://github.com/radare/radare2/archive/2.7.0.tar.gz
    ~ $ tar xzvf 2.7.0.tar.gz
    ~ $ cd radare2-2.7.0/
    ~/radare2-2.7.0 $ ./configure --prefix=/usr
    ~/radare2-2.7.0 $ make -j8
    ~/radare2-2.7.0 $ sudo make install
    # apt-get install graphviz
    # pip3 install -r requirements.txt

## 使用

    
    
    # python3 ./beebug.py -h
    usage: beebug.py [-h] -t TARGET [-a TARGETARGS] [-f FILE] [-g GRAPH]
    
    optional arguments:
      -h, --help            显示帮助信息并退出
      -t TARGET, --target TARGET
                            分析的目标程序
      -a TARGETARGS, --targetargs TARGETARGS
                            目标程序参数
      -f FILE, --file FILE  输入文件
      -g GRAPH, --graph GRAPH
                            生成视图

 **示例**

    
    
    # python3 ./beebug.py -t tests/crash_on_pc
    Process with PID 7691 started...
    File dbg:///home/invictus1306/Documents/r2conf/beebug/beebug/tests/crash_on_pc  reopened in read-write mode
    = attach 7691 7691
    child stopped with signal 11
    [+] SIGNAL 11 errno=0 addr=0x00601038 code=2 ret=0
    Crash on PC - Generally it is exploitable, the PC could be tainted
    backtrace
    0  0x601038           sp: 0x0                 0    [??]  obj.foo obj.foo0
    1  0x4004f1           sp: 0x7ffdfa75d8e8      0    [sym.main]  main+27 
    2  0x7f2669d00830     sp: 0x7ffdfa75d908      32   [??]  r11+240 
    3  0x7f266a0ba7cb     sp: 0x7ffdfa75d998      144  [??]  sym.dl_rtld_di_serinfo+29051 
    4  0x400409           sp: 0x7ffdfa75d9c8      48   [??]  entry0+41
    registers
    rax = 0x00601038
    rbx = 0x00000000
    rcx = 0x00000000
    rdx = 0x7ffdfa75d9f8
    r8 = 0x00400570
    r9 = 0x7f266a0baab0
    r10 = 0x00000846
    r11 = 0x7f2669d00740
    r12 = 0x004003e0
    r13 = 0x7ffdfa75d9e0
    r14 = 0x00000000
    r15 = 0x00000000
    rsi = 0x7ffdfa75d9e8
    rdi = 0x0000000a
    rsp = 0x7ffdfa75d8e8
    rbp = 0x7ffdfa75d900
    rip = 0x00601038
    rflags = 0x00010206
    orax = 0xffffffffffffffff

 **生成视图**

    
    
    # python3 ./beebug.py -t tests/crash_on_pc -g crash_on_pc
    ...
    # display crash_on_pc.png

**![Beebug：一款用于检查bug可利用性的工具](https://image.3001.net/images/20180912/1536705755_5b9844dba7c79.png!small)**

 **未来计划**

> 支持不同的架构
>
> 改进视图（基于radare2）
>
> 分析核心转储（基于radare2）
>
> 使用instrumentation生成视图

 ** *参考来源：[GitHub](https://github.com/invictus1306/beebug)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

