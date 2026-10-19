**作者：崎山松形@RainSec**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

## 前言

最近在搞Iot的时候接触到Qiling框架，用了一段时间后感觉确实模拟功能挺强大的，还支持Fuzz，于是开始学习对Iot
webserver这样的程序进行Fuzz。

官方给出了类似的例子如Tenda AC15 的httpd的fuzz脚本，但是也就光秃秃一个脚本还是需要自己来一遍才能学到一些东西；因为面向的是Iot
webserver的Fuzz因此需要对嵌入式设备中常用web开源框架有一些了解，这里是对于Boa框架的fuzz案例。

**环境准备** ：

  * qiling-dev branch：这里并没有选择直接pip安装，方便修改源码

  * AFL++：在python中可以`import unicornafl`就行

    
    
        git clone https://github.com/AFLplusplus/AFLplusplus.git
        make -C AFLplusplus
        cd AFLplusplus/unicorn_mode ; ./build_unicorn_support.sh

  * 一个坑是最好获取版本高于3.15的`cmake`要不然编译的时候有些cmake参数识别有问题，我遇到的就是:`cmake -S unicorn/ -B unicorn/build -D BUILD_SHARED_LIBS=no`问题

  * 需要对Qiling，AFL有些了解

**Fuzz思路** ：

Iot设备就连环境模拟都比较棘手就就更别说Fuzz了，但是Qiling提供的`进程快照(snapshot)`功能给了我们一个不错的思路，这也是Qiling官方Fuzz案例的一个思路：
**即对某函数部分Fuzz(Partial Fuzz)**

## Tenda-AC15

Qiling使用4个脚本来实现对该款路由器上httpd程序的Fuzz

![image-20221213114209793](https://images.seebug.org/content/images/2023/01/31/1675145737000-1nlfix.png-w331s)

首先是`saver_tendaac15_httpd.py`用于保存fuzz的起始状态快照，主要代码如下：

    
    
    def save_context(ql, *args, **kw):
        ql.save(cpu_context=False, snapshot="snapshot.bin")
    
    def check_pc(ql):
        print("=" * 50)
        print("Hit fuzz point, stop at PC = 0x%x" % ql.arch.regs.arch_pc)
        print("=" * 50)
        ql.emu_stop()
    
    
    def my_sandbox(path, rootfs):
        ql = Qiling(path, rootfs, verbose=QL_VERBOSE.DEBUG)
        ql.add_fs_mapper("/dev/urandom","/dev/urandom")
        ql.hook_address(save_context, 0x10930)        #<=======
        ql.hook_address(patcher, ql.loader.elf_entry)
        ql.hook_address(check_pc, 0x7a0cc)            #<=======
        ql.run()

ql.hook_address(save_context,
0x10930)：表示当程序跑到0x10930地址时调用save_context函数将保存此刻模拟状态

但需要输入来触发程序按照预想的跑到0x10930位置，带上面脚本跑起来后使用`addressNat_overflow.sh`触发

    
    
    #!/bin/sh
    
    curl -v -H "X-Requested-With: XMLHttpRequest" -b "password=1234" -e http://localhost:8080/samba.html -H "Content-Type:application/x-www-form-urlencoded" --data "entrys=sync" --data "page=CCCCAAAA" http://localhost:8080/goform/addressNat

那么我们就获得了模拟进程快照`snapshot.bin`之后fuzz就重复利用该文件启动就行，对应`fuzz_tendaac15_httpd.py`

    
    
    def main(input_file, enable_trace=False):
        ql = Qiling(["rootfs/bin/httpd"], "rootfs", verbose=QL_VERBOSE.DEBUG, console = True if enable_trace else False)
    
        # save current emulated status
        ql.restore(snapshot="snapshot.bin")
    
        # return should be 0x7ff3ca64
        fuzz_mem=ql.mem.search(b"CCCCAAAA")
        target_address = fuzz_mem[0]
    
        def place_input_callback(_ql: Qiling, input: bytes, _):
            _ql.mem.write(target_address, input)
    
        def start_afl(_ql: Qiling):
            """
            Callback from inside
            """
            ql_afl_fuzz(_ql, input_file=input_file, place_input_callback=place_input_callback, exits=[ql.os.exit_point])
    
        ql.hook_address(callback=start_afl, address=0x10930+8)
    
        try:
            ql.run(begin = 0x10930+4, end = 0x7a0cc+4)
            os._exit(0)
        except:
            if enable_trace:
                print("\nFuzzer Went Shit")
            os._exit(0)        
    
    if __name__ == "__main__":
        if len(sys.argv) == 1:
            raise ValueError("No input file provided.")
    
        if len(sys.argv) > 2 and sys.argv[1] == "-t":
            main(sys.argv[2], enable_trace=True)
        else:
            main(sys.argv[1])

  * 恢复快照：ql.restore(snapshot="snapshot.bin")

  * 变异数据缓存定位：fuzz_mem=ql.mem.search(b"CCCCAAAA")

  * 以hook方式从起始地址附近的开始fuzz：ql.hook_address(callback=start_afl, address=0x10930+8)

最后开始Fuzz

    
    
    #!/usr/bin/sh
    
    AFL_DEBUG_CHILD_OUTPUT=1 AFL_AUTORESUME=1 AFL_PATH="$(realpath ./AFLplusplus)" PATH="$AFL_PATH:$PATH" ./AFLplusplus/afl-fuzz -i afl_inputs -o afl_outputs -U -- python3 ./fuzz_tendaac15_httpd.py @@

**说实话这样连最关键的fuzz范围`0x10930`，`0x7a0cc`怎么来的都不知道当时逆向定位这两个地址也是一头雾水毫无特征，还是得自己实操**

因此选定了Boa框架(之前了解过源码)从零开始对其进行Fuzz

## Boa Fuzz

选择一个网上有许多漏洞分析的设备：vivetok
摄像头，固件[链接](https://objects.githubusercontent.com/github-production-repository-file-5c1aeb/84257798/3128058?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20221208%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20221208T052257Z&X-Amz-Expires=300&X-Amz-Signature=9a257e351faa9f25e49c6ddc70e3fe94bc94eed63d940d5c70fe1f71570f4120&X-Amz-SignedHeaders=host&actor_id=57476305&key_id=0&repo_id=84257798&response-content-disposition=attachment%3Bfilename%3DCC8160-VVTK-0100d.flash.zip&response-content-type=application%2Fx-zip-compressed)；而且webservre为Boa框架

Poc：

    
    
    echo -en "POST /cgi-bin/admin/upgrade.cgi HTTP/1.0\nContent-Length:AAAAAAAAAAAAAAAAAAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIXXXX\n\r\n\r\n"  | ncat -v 192.168.57.20 80

**_Boa框架_** ：

主要处理逻辑在`process_requests`函数中：

    
    
               /*获取就绪队列并处理*/
        current = request_ready;
    
        while (current) {
            time(&current_time);
            if (current->buffer_end && /* there is data in the buffer */
                current->status != DEAD && current->status != DONE) {
                retval = req_flush(current);
                /*
                 * retval can be -2=error, -1=blocked, or bytes left
                 */
                if (retval == -2) { /* error */
                    current->status = DEAD;
                    retval = 0;
                } else if (retval >= 0) {
                    /* notice the >= which is different from below?
                       Here, we may just be flushing headers.
                       We don't want to return 0 because we are not DONE
                       or DEAD */
    
                    retval = 1;
                }
            } else {/*主要处理请求部分在这里*/
                switch (current->status) {
                case READ_HEADER:
                case ONE_CR:
                case ONE_LF:
                case TWO_CR:
                    retval = read_header(current);    //解析request头部，该函数类似与FILE_IO
                    break;                            //函数request内部有8192+1字节的buffer，data的头尾指针等，最终调用
                case BODY_READ:                       //bytes = read(req->fd, buffer + req->client_stream_pos, buf_bytes_left);读取
                    retval = read_body(current);
                    break;
                case BODY_WRITE:
                    retval = write_body(current);
                    break;
                case WRITE:
                    retval = process_get(current);
                    break;
                case PIPE_READ:
                    retval = read_from_pipe(current);
                    break;
                case PIPE_WRITE:
                    retval = write_from_pipe(current);
                    break;
                case DONE:
                    /* a non-status that will terminate the request */
                    retval = req_flush(current);
                    /*
                     * retval can be -2=error, -1=blocked, or bytes left
                     */
                    if (retval == -2) { /* error */
                        current->status = DEAD;
                        retval = 0;
                    } else if (retval > 0) {
                        retval = 1;
                    }
                    break;
                case DEAD:
                    retval = 0;
                    current->buffer_end = 0;
                    SQUASH_KA(current);
                    break;
                default:
                    retval = 0;
                    fprintf(stderr, "Unknown status (%d), "
                            "closing!\n", current->status);
                    current->status = DEAD;
                    break;
                }
            }

主要看中间的Switch case：

  * read_header：解析request头部，该函数类似FILE_IO函数
  * request内部有8192+1字节的buffer，data的头尾指针等，最终调用bytes = read(req->fd, buffer + req->client_stream_pos, buf_bytes_left);读取client发送的请求
  * 会提取并解析头部信息
  * 对于GET传参，主要使用read_header, read_from_pipe, write_from_pipe完成cgi的调用
  * 对于POST传参，主要调用read_header, read_body, write_body完成cgi调用

就拿read_header函数来说，厂商应该会在里面增加一些url过虑以及响应处理，在这个摄像头中漏洞也确实出在这个函数：

![image-20221213133117933](https://images.seebug.org/content/images/2023/01/31/1675145744000-2xxsiq.png-w331s)

没有对`Content-Length`成员做限制； **根据源码中提示字符串`Unknown status (%d),
closing`可以轻松定位到这几个函数**:

![image-20221213133545416](https://images.seebug.org/content/images/2023/01/31/1675145755000-3ybsfw.png-w331s)

那么接下来就尝试利用Qiling 启动这个程序并且Partial Fuzz函数"read_header"

### 模拟启动

**模拟启动的宗旨(我的)是遇到啥错误修最后一个报错点**

启动模板：

    
    
    import os, sys
    sys.path.append('/home/iot/workspace/Emulator/qiling-dev')
    from qiling import Qiling
    from qiling.const import QL_INTERCEPT, QL_VERBOSE
    
    
    def boa_run(path: list, rootfs: str, profile: str = 'default'):
        ql = Qiling(path, rootfs, profile=profile, verbose=QL_VERBOSE.OFF, multithread=False)
        """setup files"""
        ql.add_fs_mapper('/dev/null', '/dev/null')
    
        """hooks"""
    
        ql.run()
    
    
    if __name__ == '__main__':
        os.chdir('/home/iot/workspace/Emulator/qiling-dev/vivetok')
        path = ['./rootfs/usr/sbin/httpd', "-c", "/etc/conf.d/boa", "-d"]
        rootfs = './rootfs'
        profile = './boa_arm.ql'
        boa_run(path=path, rootfs=rootfs, profile=profile)

* * *

**尝试启动**

首先遇到的是：gethostbyname:: Success

在IDA中定位到：

![image-20221213134138571](https://images.seebug.org/content/images/2023/01/31/1675145758000-4hsllg.png-w331s)

函数原型：

    
    
    struct hostent *gethostbyname(const char *hostname);
    struct hostent{
        char *h_name;  //official name
        char **h_aliases;  //alias list
        int  h_addrtype;  //host address type
        int  h_length;  //address lenght
        char **h_addr_list;  //address list
    }

获取返回的结构体还挺复杂的，问题的原因是 在调用`gethostname`将获得 **ql_vm**
作为主机名所以当以此调用`gethostbyname`无法获得主机信息，所以hook这个函数，并提前开辟空间存放伪造信息：

    
    
    """
    struct hostent{
        char *h_name;  //official name
        char **h_aliases;  //alias list
        int  h_addrtype;  //host address type
        int  h_length;  //address lenght
        char **h_addr_list;  //address list
    }
    """
    def hook_memSpace(ql: Qiling):
        ql.mem.map(0x1000, 0x1000, info='my_hook')
        data = struct.pack('<IIIII', 0x1100, 0x1100, AF_INET, 4, 0x1100)
        ql.mem.write(0x1000, data)
        ql.mem.write(0x1100, b'qiling')
    
    def lib_gethostbyname(ql: Qiling):
        args = ql.os.resolve_fcall_params({'name':STRING})
        print('[gethostbyname]: ' + args['name'])
        ql.arch.regs.write('r0', 0x1000)

还有一个严重问题就是模拟过程中程序自动采用`ipv6`协议，这就很烦因为qiling的ipv6协议支持的不是很好

#### ipv6 socket

**_AttributeError: 'sockaddr_in' object has no attribute 'sin6_addr'_**

问题处在对ipv6的系统调用bind：

    
    
    elif sa_family == AF_INET6 and ql.os.ipv6:
        sockaddr_in6 = make_sockaddr_in(abits, endian)
        sockaddr_obj = sockaddr_in6.from_buffer(data)
    
        port = ntohs(ql, sockaddr_obj.sin_port)
        host = inet6_ntoa(sockaddr_obj.sin6_addr.s6_addr)
    
        if ql.os.bindtolocalhost:
            host = '::1'
    
        if not ql.os.root and port <= 1024:
            port = port + 8000
    
    def make_sockaddr_in(archbits: int, endian: QL_ENDIAN):
        Struct = struct.get_aligned_struct(archbits, endian)
    
        class in_addr(Struct):
            _fields_ = (
                ('s_addr', ctypes.c_uint32),
            )
    
        class sockaddr_in(Struct):
            _fields_ = (
                ('sin_family', ctypes.c_int16),
                ('sin_port',   ctypes.c_uint16),
                ('sin_addr',   in_addr),
                ('sin_zero',   ctypes.c_byte * 8)
            )
    
        return sockaddr_in
    
    def make_sockaddr_in6(archbits: int, endian: QL_ENDIAN):
        Struct = struct.get_aligned_struct(archbits, endian)
    
        class in6_addr(Struct):
            _fields_ = (
                ('s6_addr', ctypes.c_uint8 * 16),
            )
    
        class sockaddr_in6(Struct):
            _fields_ = (
                ('sin6_family',   ctypes.c_int16),
                ('sin6_port',     ctypes.c_uint16),
                ('sin6_flowinfo', ctypes.c_uint32),
                ('sin6_addr',     in6_addr),
                ('sin6_scope_id', ctypes.c_uint32)
            )
    
        return sockaddr_in6

make_sockaddr_in,
make_sockaddr_in6基于`ctypes`构造严格的sockaddr结构体，因为是ipv6所以得用`make_sockaddr_in6`

还有就是函数`(function) inet6_ntoa: (addr: bytes) ->
str`需要bytes对象而sockaddr_obj.sin6_addr.s6_addr是cbytes类型所以得 **bytes转**

    
    
    sockaddr_in6 = make_sockaddr_in6(abits, endian)
    sockaddr_obj = sockaddr_in6.from_buffer(data)
    port = ntohs(ql, sockaddr_obj.sin6_port)
    host = inet6_ntoa(bytes(sockaddr_obj.sin6_addr.s6_addr))

**_OSError: [Errno 98] Address already in use_**

还是在调用bind时候，因为qiling会对低于1024的端口bind进行修改：

    
    
    if not ql.os.root and port <= 1024:
            port = port + 8000

而后面还对8080端口进行一次bind，所以这里得改，然后其实就能进入核心处理逻辑了 ：

![image-20221213134113202](https://images.seebug.org/content/images/2023/01/31/1675145769000-5mlbea.png-w331s)

当然还得看看链接有没有问题：尝试访问又出现问题

    
    
    $ echo -en "GET /index.html HTTP/1.0\n\rContent-Length:20\n\r\n\r"  | nc -v ::1 9080
    Connection to ::1 9080 port [tcp/*] succeeded!
    
    File "/home/iot/workspace/Emulator/qiling-dev-stb/qiling/os/posix/syscall/socket.py", line 669, in ql_syscall_accept
        host, port = address
    ValueError: too many values to unpack (expected 2)

**_ValueError: too many values to unpack (expected 2)_**

经调试原来在python中accept ipv6的连接后会返回一个长度为4的元组的address：

![image-20221213134207632](https://images.seebug.org/content/images/2023/01/31/1675145771000-6pvtvd.png-w331s)

同样的问题还发生在ql_syscall_getsockname：`sockname = sock.getsockname()`

**_TypeError: expected c_ubyte_Array_16 instance, got int_**

    
    
    [x]     Syscall ERROR: ql_syscall_accept DEBUG: expected c_ubyte_Array_16 instance, got int
    Traceback (most recent call last):
      File "/home/iot/workspace/Emulator/qiling-dev-stb/qiling/os/posix/posix.py", line 280, in load_syscall
        retval = syscall_hook(self.ql, *params)
      File "/home/iot/workspace/Emulator/qiling-dev-stb/qiling/os/posix/syscall/socket.py", line 674, in ql_syscall_accept
        obj.sin6_addr.s6_addr = inet6_aton(str(host))
    TypeError: expected c_ubyte_Array_16 instance, got int

解决：bytes转cbyts类

    
    
    obj.sin6_addr.s6_addr = (ctypes.c_ubyte * 16).from_buffer_copy(inet6_aton(str(host)).to_bytes(16, 'big'))

主要问题就这些(修了挺久的)，然后就可以对一些函数进行fuzz了

### Fuzz Partial

确定Fuzz范围，这个范围主要是给到ql_afl_fuzz函数，这里是打算Fuzz read_header函数(sub_17F80)，那么从数据入口下手：

![image-20221213135606979](https://images.seebug.org/content/images/2023/01/31/1675145772000-7gyqop.png-w331s)

读取POST或者GET方法的http包那么肯定要解析处理的，处理完成返回一个状态(源码中retval)来指示下一步处理，找到退出点：

![image-20221213135843221](https://images.seebug.org/content/images/2023/01/31/1675145772000-8eqtoi.png-w331s)
因此要从`0x180F8`附近开始Fuzz，然后`0x18398`表示函数正常退出将执行下一轮fuzz

脚本模板：

    
    
    import os, sys
    sys.path.append('/home/iot/workspace/Emulator/qiling-dev')
    from qiling.const import QL_INTERCEPT, QL_VERBOSE
    from qiling import Qiling
    
    from qiling.extensions.afl import ql_afl_fuzz
    
    
    def main(input_file: str, trace: bool = False):
        ql = Qiling(['./rootfs/usr/sbin/httpd', "-c", "/etc/conf.d/boa", "-d"], rootfs='./rootfs', profile='./boa_arm.ql', verbose=QL_VERBOSE.OFF, console = True if trace else False)
        ql.restore(snapshot='./context.bin')
    
        def place_input_callback(_ql: Qiling, input: bytes, _):
            # print(b"**************** " + input)
            _ql.mem.write(target_addr, input)
    
        def start_afl(_ql: Qiling):
            """
            Callback from inside
            """
            ql_afl_fuzz(_ql, input_file=input_file, place_input_callback=place_input_callback, exits=[0x018398])
    
        ql.hook_address(callback=start_afl, address=0x180F8)
    
        try:
            # ql.debugger = True
            ql.run(begin=0x180F8)
            os._exit(0)
        except:
            if trace:
                print("\nFuzzer Went Shit")
            os._exit(0)  
    
    if __name__ == "__main__":
        if len(sys.argv) == 1:
            raise ValueError("No input file provided.")
    
        os.chdir('/home/iot/workspace/Emulator/qiling-dev/vivetok')
        if len(sys.argv) > 2 and sys.argv[1] == "-t":
            main(sys.argv[2], trace=True)
        else:
            main(sys.argv[1])

  * ql.hook_address(callback=start_afl, address=0x180F8)：在执行到`0x180F8`这个位置时调用start_afl函数
  * ql.run(begin=0x180F8)：从`0x180F8`开始执行
  * ql_afl_fuzz：就是unicornafl提供的fuzz接口`uc_afl_fuzz_custom`的一个wrapper
  * place_input_callback：ql_afl_fuzz会调用的回调函数，负责写入fuzz数据

### Fuzz buf

根据网上的漏洞分析比对源码框架，利用:

    
    
    cho -en "POST /cgi-bin/admin/upgrade.cgi HTTP/1.0nContent-Length:AAAAAAAAAAAAAAAAAAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIXXXXnrnrn"  | nc -v ::1 9080

可以触发漏洞，具体位于框架中http头部解析函数：read_header，位于httpd中17F80位置

那么该如何fuzz呢，根据网上unicorn-afl官方用例和qiling官方用例：buf-fuzz，即定位代码中读取数据位置，然后读取完后劫持搜索特定字符串定位fuzz的buff_addr，当然需要状态保存(当然这个方法肯定不是很严谨，因此后面还会介绍劫持read函数方法)

#### 快照

    
    
    import os, sys, struct
    from socket import AF_INET
    sys.path.append('/home/iot/workspace/Emulator/qiling-dev')
    from qiling import Qiling
    from qiling.const import QL_INTERCEPT, QL_VERBOSE
    from qiling.os.const import STRING
    from unicorn.unicorn import UcError
    """
    struct hostent{
        char *h_name;  //official name
        char **h_aliases;  //alias list
        int  h_addrtype;  //host address type
        int  h_length;  //address lenght
        char **h_addr_list;  //address list
    }
    """
    def hook_memSpace(ql: Qiling):
        ql.mem.map(0x1000, 0x1000, info='my_hook')
        data = struct.pack('<IIIII', 0x1100, 0x1100, AF_INET, 4, 0x1100)
        ql.mem.write(0x1000, data)
        ql.mem.write(0x1100, b'qiling')
    
    def lib_gethostbyname(ql: Qiling):
        args = ql.os.resolve_fcall_params({'name':STRING})
        print('[gethostbyname]: ' + args['name'])
        ql.arch.regs.write('r0', 0x1000)
    
    
    def saver(ql: Qiling):
        print('[!] Hit Saver 0x%X'%(ql.arch.regs.arch_pc))
        ql.save(cpu_context=False, snapshot='./context.bin')
        print(ql.mem.search(b'fuck'))
    
    
    #[read(5,  0x4edca,  0x2000)] locate buf
    def read_syscall(ql: Qiling, fd: int, buf: int, size: int, *args) -> None:
        print(f'[read({fd}, {buf: #x}, {size: #x})]')
    
    def boa_run(path: list, rootfs: str, profile: str = 'default'):
        ql = Qiling(path, rootfs, profile=profile, verbose=QL_VERBOSE.OFF, multithread=False)
        """setup files"""
        ql.add_fs_mapper('/dev/null', '/dev/null')
    
        """set ram"""
        hook_memSpace(ql)
    
        """hooks"""
        ql.os.set_api('gethostbyname', lib_gethostbyname, QL_INTERCEPT.CALL)
        ql.os.set_syscall('read', read_syscall, QL_INTERCEPT.ENTER)
    
        """setup saver"""
        ql.hook_address(saver, 0x0180FC)        #read finish
    
        ql.run()
    
    if __name__ == '__main__':
        os.chdir('/home/iot/workspace/Emulator/qiling-dev/vivetok')
        path = ['./rootfs/usr/sbin/httpd', "-c", "/etc/conf.d/boa", "-d"]
        rootfs = './rootfs'
        profile = './boa_arm.ql'
        boa_run(path=path, rootfs=rootfs, profile=profile)

然后使用poc触发就行

#### fuzz

    
    
    import os, sys, struct
    import capstone as Cs
    sys.path.append('/home/iot/workspace/Emulator/qiling-dev')
    from qiling.const import QL_INTERCEPT, QL_VERBOSE
    from qiling import Qiling
    from qiling.extensions.afl import ql_afl_fuzz
    
    
    def simple_diassembler(ql: Qiling, address: int, size: int, md: Cs) -> None:
        buf = ql.mem.read(address, size)
    
        for insn in md.disasm(buf, address):
            ql.log.debug(f':: {insn.address:#x} : {insn.mnemonic:24s} {insn.op_str}')
    
    def main(input_file: str, trace: bool = False):
        ql = Qiling(['./rootfs/usr/sbin/httpd', "-c", "/etc/conf.d/boa", "-d"], rootfs='./rootfs', profile='./boa_arm.ql', verbose=QL_VERBOSE.OFF, console = True if trace else False)
        ql.restore(snapshot='./context.bin')
    
        fuzz_mem = ql.mem.search(b'fuck')
    
        target_addr = fuzz_mem[0]
    
        def place_input_callback(_ql: Qiling, input: bytes, _):
            # print(b"**************** " + input)
            _ql.mem.write(target_addr, input)
    
    
        def start_afl(_ql: Qiling):
            """
            Callback from inside
            """
            ql_afl_fuzz(_ql, input_file=input_file, place_input_callback=place_input_callback, exits=[0x018398])
    
        ql.hook_address(callback=start_afl, address=0x0180FC+4)
        # ql.hook_code(simple_diassembler, begin=0x0180FC, end=0x018600, user_data=ql.arch.disassembler)
    
        try:
            # ql.debugger = True
            ql.run(begin=0x0180FC+4, end=0x018600)    #注意arm函数返回地址比较奇怪，不一定在函数末尾
            os._exit(0)
        except:
            if trace:
                print("\nFuzzer Went Shit")
            os._exit(0)  
    
    if __name__ == "__main__":
        if len(sys.argv) == 1:
            raise ValueError("No input file provided.")
    
        os.chdir('/home/iot/workspace/Emulator/qiling-dev/vivetok')
        if len(sys.argv) > 2 and sys.argv[1] == "-t":
            main(sys.argv[2], trace=True)
        else:
            main(sys.argv[1])

这里很坑的一点是，在漏洞中因为`Content-Length`成员不以\n结尾时就会让v31等于0会让strncpy报错但是不一定是pc指针错误，而是某些指令地址操作数问题

    
    
    v30 = strstr(haystack, "Content-Length");
    v31 = strchr(v30, '\n');
    v32 = strchr(v30, ':');
    strncpy(dest, v32 + 1, v31 - (v32 + 1));

在源码中AFL模块调用以下函数完成fuzz执行：

    
    
    def _dummy_fuzz_callback(_ql: "Qiling"):
                if isinstance(_ql.arch, QlArchARM):
                    pc = _ql.arch.effective_pc
                else:
                    pc = _ql.arch.regs.arch_pc
                try:
                    _ql.uc.emu_start(pc, 0, 0, 0)
                except UcError as e:
                    os.abort()              #添加部分
                    return e.errno

因此添加`os.abort`通知AFL程序崩溃

#### 效果

![image-20221213140214049](https://images.seebug.org/content/images/2023/01/31/1675145774000-9zqbmr.png-w331s)

### Fuzz sys_read

上面直接对buf写入Fuzz数据肯定不是一个很理想的办法(比如Fuzz数据超出读取长度)，当然人家给的例子就是这么Fuzz的也不失一种方法；之后

就尝试利用Qiling的系统调用劫持功能让Fuzz效果更好。

从read函数调用处开始执行，在这之前劫持read函数调用让程序直接读取文件输入：

    
    
    def read_syscall(ql: Qiling, fd: int, buf: int, size: int, *args) -> int:
        # print(fd, buf, size)
        data = ql.os.stdin.read(size)
        # print(data)
        ql.mem.write(buf, data)
        return len(data)
    
    def place_input_callback(_ql: Qiling, input: bytes, _):
        # print(b"**************** " + input)
        ql.os.stdin.write(input)
    
        return True
    
    
    def start_afl(_ql: Qiling):
        """
        Callback from inside
        """
        ql_afl_fuzz(_ql, input_file=input_file, place_input_callback=place_input_callback, exits=[0x018398])

#### 效果

同样写个脚本把服务并且设置debugger等待gdb连接：

![image-20221213143927097](https://images.seebug.org/content/images/2023/01/31/1675145776000-10cokax.png-w331s)

然后将crash中的数据发送：

![image-20221213144007558](https://images.seebug.org/content/images/2023/01/31/1675145778000-11nfrez.png-w331s)

也确实触发到了漏洞：

    
    
    0x900a5d74 in strncpy () from target:/lib/libc.so.0
    gef?  backtrace 
    #0  0x900a5d74 in strncpy () from target:/lib/libc.so.0
    #1  0x0001853c in ?? ()
    Backtrace stopped: previous frame identical to this frame (corrupt stack?)
    gef?  

#### 技巧

fuzz过程中不好调试连写的harness有没有效果都不知道，可以使用capstone同步解析执行汇编情况：

    
    
    def simple_diassembler(ql: Qiling, address: int, size: int, md: Cs) -> None:
        buf = ql.mem.read(address, size)
    
        for insn in md.disasm(buf, address):
            ql.log.debug(f':: {insn.address:#x} : {insn.mnemonic:24s} {insn.op_str}')

## 参考

  * [Demo - Qiling Framework Documentation](https://docs.qiling.io/en/latest/demo/)
  * [IOT Fuzz 两种思路](https://blog.csdn.net/jazrynwong/article/details/117228447)
  * [vivetok 摄像头远程栈溢出漏洞分析-安全客 - 安全资讯平台 (anquanke.com)](https://www.anquanke.com/post/id/185336#h2-2)
  * [Vivotek远程栈溢出漏洞分析与复现 - 先知社区 (aliyun.com)](https://xz.aliyun.com/t/5054)
  * [基于Unicorn和LibFuzzer的模拟执行fuzzing](http://galaxylab.com.cn/%e5%9f%ba%e4%ba%8eunicorn%e5%92%8clibfuzzer%e7%9a%84%e6%a8%a1%e6%8b%9f%e6%89%a7%e8%a1%8cfuzzing/)
  * [基于 unicorn 的单个函数模拟执行和 fuzzer 实现](http://galaxylab.pingan.com.cn/%E5%9F%BA%E4%BA%8E-unicorn-%E7%9A%84%E5%8D%95%E4%B8%AA%E5%87%BD%E6%95%B0%E6%A8%A1%E6%8B%9F%E6%89%A7%E8%A1%8C%E5%92%8C-fuzzer-%E5%AE%9E%E7%8E%B0/)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2043/>

