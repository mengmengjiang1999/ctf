题目只给出nc端口没有附件 连接发现

Pwntools is such an awesome python module, right?

Tell you a secret (only smart baby can see it) :

Maybe I will tell you again when you clever than ELSEpush ......

最后面有省略号我猜测应该是没有输出完所以我们使用pwntools攻击 recvline() 接受没有显示出来的内容

然后发现有一个base64加密的字符串 结合题目说聪明得人才能发现解密出来就是flag{n0tf4stert6an_y0u}

![](https://image.3001.net/images/20201102/1604307430_5f9fc9e6923418302aec4.png!small)

##  **ret2text**

拿到题目我一般的做题思路是首先checksec一下看到附件之打开了NX保护所以程序中不能直接使用shellcode执行任意代码 以及32位的elf
linux程序

![](https://image.3001.net/images/20201102/1604307570_5f9fca72bd06ae24026ca.png!small)

然后通过看到的文件基本信息选择64位或者32位的IDA Pro 这个ret2text我们选择用32位的来静态分析它的源代码

![](https://image.3001.net/images/20201102/1604307621_5f9fcaa57a1d934fd7a4a.png!small)

用IDA打开之后它自动停在main函数处首先展现出来的是汇编代码
我们要将汇编代码转成我们能通俗易懂的c语言代码按F5进行反汇编发现这个函数的主函数并没有什么漏洞但是main的子函数vulnerable里面定义了缓冲区有8字节然后gets函数这里是一个栈溢出的基本漏洞
gets函数可以有栈溢出的漏洞对读入的数据不受限制 所以可以借助溢出的漏洞来到它的返回地址
我们从静态调试中得到栈里与ebp距离为16字节而缓冲区只定义了8字节 然后我们就用gets函数执行可读多个字节来覆盖栈里的程序

![](https://image.3001.net/images/20201102/1604307677_5f9fcadd4dbab4f7b49f7.png!small)

在ida中我们还发现有一个system函数这就是一般pwn题的后门函数当我们用垃圾数据写出的payload成功劫持了程序的执行流时
需要写一个指针的返回地址来执行我们需要的恶意代码 这个system地址就是8048522

![](https://image.3001.net/images/20201102/1604307707_5f9fcafb6284124bbfa3d.png!small)

根据综上分析exp如下 python 1.from pwn import * 2.c=remote('...', )
3.#c=process(./ret2text) 4.py=b'A'*16+b'BBBB'+p32(0x8048522) 5.c.sendline(py)
6.c.interactive()

##  **总结此题型的思路以及做法**

首先了解pwntools，pwntools是一个二进制利用框架。 下面我给大家介绍下pwntools的使用方法 pwntools脚本 python
1.from pwn import * 2.c = remote("127.0.0.1", 8080) 3.sendline("AAAA" * 18 +
p32(0x8048522) 4.c.interactive() remote("一个域名或者ip地址", 端口) 会连接到我们指定的地址及端口。
然后该函数会返回remote对象 (这里，我们将该对象保存到了变量 c). remote对象主要用来进行对远程主机的输入输出. 它有如下几个方法：

send(payload) 发送payload

sendline(payload) 发送payload，并进行换行（末尾\n）

sendafter(some_string, payload) 接收到 some_string 后, 发送你的 payload

recvn(N) 接受 N(数字) 字符

recvline() 接收一行输出

recvlines(N) 接收 N(数字) 行输出

recvuntil(some_string) 接收到 some_string 为止

