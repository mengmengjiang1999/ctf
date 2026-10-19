前言：最近在入门pwn的栈溢出，做了一下jarvisoj里的一些ctf
pwn题，感觉质量都很不错，难度循序渐进，把自己做题的思路和心得记录了一下，希望能给入门pwn的朋友带来点帮助和启发，大牛轻喷  

  

题目链接：<https://www.jarvisoj.com/challenges>

1、level0（64位）

代码

![image.png](https://image.3001.net/images/20180910/1536561517_5b96116d8f5c5.png!small)  

也就是输出Hello World以后接收一个输出，仔细看会发现一个system函数

  
![image.png](https://image.3001.net/images/20180910/1536561528_5b96117843ee9.png!small)  

那么思路就很清晰，在read函数接收输入的时候直接覆盖返回地址为system函数即可

在IDA中可以看到，buf距离EBP为0x80，但是这个是64位的程序，一个EBP占8bytes，那么payload：

  
![image.png](https://image.3001.net/images/20180910/1536561539_5b96118306779.png!small)  

  * p32也就是pack32，把地址的hex值转化为32小端地址存储的方法进行发送  

脚本如下：

  
![image.png](https://image.3001.net/images/20180910/1536561613_5b9611cd5679e.png!small)  

运行脚本得到shell

![image.png](https://image.3001.net/images/20180910/1536561618_5b9611d2631f3.png!small)

2、level1

0x00 代码

main函数

  
![image.png](https://image.3001.net/images/20180910/1536561626_5b9611da71316.png!small)  

vulnerable_function函数

  
![image.png](https://image.3001.net/images/20180910/1536561633_5b9611e12abe8.png!small)  

可以看到buf的偏移是0x88，那么需要的填充：'a'*0x88+'a'*4（EBP）+返回地址

0x01 第一种解法

使用pwntools自带的工具checksec查看程序的保护机制，发现是NX disabled，可以直接往栈上写汇编语句来执行来达到溢出的目的

> 保护机制的解释：<https://blog.csdn.net/nibiru_holmes/article/details/61209297>

基本思路：这里printf给出了buf的首地址，所以可以填充返回地址为接收到的buf的首地址，用asm模块向上面写数据，这个也是pwntools自带的模块

使用方法：

  
![image.png](https://image.3001.net/images/20180910/1536561643_5b9611eb69287.png!small)  

运行以后可以看到，打印出来的地址的值就是buf的首地址，我们用pwntools接收

  
![image.png](https://image.3001.net/images/20180910/1536561650_5b9611f2240e5.png!small)  

  * 这里接收到的buf_addr一定要进行int16进制的转换( int(buf,16) )，才能用p32封包进行发送  

  

最后的脚本：

  
![image.png](https://image.3001.net/images/20180910/1536561658_5b9611fa18d7a.png!small)  

E:/%E6%9C%89%E9%81%93/qq987FE2B65EC068C281254890044944CD/f76f4bc855a34842a1163a96af15d769/clipboard.png

  
![image.png](https://image.3001.net/images/20180910/1536561672_5b96120809ac7.png!small)  

0x02 第二种解法

这种方法算是一个通法，也就是使用dynelf的方法来动态的泄露system函数的地址，这里先记住这个方法，后面还会说到

> dynelf使用的条件：栈溢出、有输入输出函数（gets、puts、read、write）、无PIE保护

这里在第一输入点进行栈溢出，leak出system函数的地址并返回主函数

  
![image.png](https://image.3001.net/images/20180910/1536561678_5b96120e8482f.png!small)  

这里的leak函数计算出libc的基地址，并查找libc库来泄露system函数的地址

调用read函数向bss可写段写入/bin/sh字符串，接着调用system拿到shell

  
![image.png](https://image.3001.net/images/20180910/1536561684_5b961214c19ed.png!small)  

  * 这里使用gdb的vmmap的方法找到可写段，使用后面的数据段不容易出错  

  
![image.png](https://image.3001.net/images/20180910/1536561692_5b96121c5ba22.png!small)  

3、level2

main函数

  
![image.png](https://image.3001.net/images/20180910/1536561697_5b961221c0c64.png!small)  

vulnerable_function函数

  
![image.png](https://image.3001.net/images/20180910/1536561703_5b961227e8209.png!small)  

存在栈溢出，而且可以直接调用system函数，搜索字符串还可以发现有/bin/sh字符串

  
![image.png](https://image.3001.net/images/20180910/1536561709_5b96122d9abdb.png!small)  

思路：通过溢出到返回地址修改为system函数的地址，参数为/bin/sh字符串

此时栈的分布情况：

  
![image.png](https://image.3001.net/images/20180910/1536561720_5b9612381eb88.png!small)  

  

最后的脚本：

![image.png](https://image.3001.net/images/20180910/1536561761_5b9612618ed84.png!small)  

payload = 'a' *0x88 + 'a'*4 + p32(system_addr) + p32(1) + p32(bin_addr)

  * p32(1)为无效的填充的返回地址，这里我们调用完system函数就行了，不用管这个地址
  * 这里使用elf的search方法来搜索字符串，next方法取到第一个匹配到的字符串  
  

  

这里的ELF方法可以打印输出基本的plt、got表中函数的地址，就不需要我们手动进行查找了，具体的可以看下面的文章

<https://blog.csdn.net/weixin_41400278/article/details/78819950>

  

这里也可以通过read函数来向可写段写入/bin/sh字符串，思路就是先调用read函数写入字符，之后返回主函数，再向栈内写入system函数，这是在没有/bin/sh字符串的时候使用。在这里就显得多此一举了

  
![image.png](https://image.3001.net/images/20180910/1536562028_5b96136cbec2b.png!small)  

4、level3

代码：

  
![image.png](https://image.3001.net/images/20180910/1536562038_5b961376c2e5a.png!small)![image.png](https://image.3001.net/images/20180910/1536562366_5b9614be9425c.png!small)

  

这里有read、write函数，但是没有system函数，这题还给了libc库，所以这题就是使用比较标准的got表泄露system函数的方法来getshell

  
![image.png](https://image.3001.net/images/20180910/1536562376_5b9614c806f8a.png!small)  

思路：使用write函数将got表中write地址作为参数，调用plt表中的write函数，得到基地址后加上system函数在程序中的偏移，就得到了system函数的实际地址，进行调用即可

（1）、使用ELF函数获取plt、got表的地址

  
![image.png](https://image.3001.net/images/20180910/1536562382_5b9614cec02b1.png!small)  

（2）、构造payload

  
![image.png](https://image.3001.net/images/20180910/1536562437_5b96150571c81.png!small)  

  

因为这里的plt_write的地址是将jmp语句传入栈中，后面还传入了三个参数，所以为了平衡栈需要pop三次（使用ROPgadget查找，rop方法的一种）

<https://blog.csdn.net/weixin_40850881/article/details/80216764>

  

在qira中看到的情况是这样的

  
![image.png](https://image.3001.net/images/20180910/1536562444_5b96150c7585b.png!small)  

（3）、减去write函数在libc库中的偏移得到基地址

  
![image.png](https://image.3001.net/images/20180910/1536562452_5b9615144bc69.png!small)  

  

write函数的偏移地址的查找：

先使用ldd命令找到libc库的名字

  
![image.png](https://image.3001.net/images/20180910/1536562457_5b961519f2773.png!small)  

然后用readelf方法找到函数的相对偏移位置

  
![image.png](https://image.3001.net/images/20180910/1536562462_5b96151e3f2f6.png!small)  

（4）、构造system函数并调用

payload1： payload = "A" * 0x88 + "A" * 4 + p32(plt_write) + p32(main_addr) +
p32(1) + p32(elf.got["write"]) + p32(4)

  

也就是先调用write(1,write函数地址,4)，第一个参数文件描述符等于1表示输出，4代表输出的长度，中间的就是输出的内容，调用完成后返回主函数，得到基地址后为泄露system函数的地址做准备

  

先leak出write函数的libc地址，从而计算出libc的基地址，sendline之后返回主函数

  
![image.png](https://image.3001.net/images/20180910/1536562469_5b961525b4d74.png!small)![image.png](https://image.3001.net/images/20180910/1536562473_5b96152962500.png!small)

leak出system函数的地址

![image.png](https://image.3001.net/images/20180910/1536562480_5b961530a8e77.png!small)

  

运行脚本的结果：

  
![image.png](https://image.3001.net/images/20180910/1536562489_5b961539dcba4.png!small)  

在input输入后调用system函数

payload2 = "A" * 0x88 + "A" * 4 + p32(system_addr) + p32(1) + p32(binsh_addr)

  

找到字符串/bin/sh在libc库中的位置（注意这里是偏移地址），可以在IDA中直接找到，也可以用上面说的search方法

![image.png](https://image.3001.net/images/20180910/1536562495_5b96153fb4c31.png!small)![image.png](https://image.3001.net/images/20180910/1536562499_5b9615436e972.png!small)

  

根据libc的基地址，得到system函数的地址，/bin/sh字符串的地址，sendline出payload以后就会执行system函数

![image.png](https://image.3001.net/images/20180910/1536562505_5b961549a01f9.png!small)  

  * 这里最后用sleep函数暂停一下  

运行脚本getshell

  
![image.png](https://image.3001.net/images/20180910/1536562574_5b96158e7fc00.png!small)  

0x03 level4

代码

![image.png](https://image.3001.net/images/20180910/1536562594_5b9615a2314f7.png!small)  
![image.png](https://image.3001.net/images/20180910/1536562578_5b961592a67cb.png!small)

思路：这题和上面的level3几乎一样，但是这道题没有给出libc库，所以这里使用的是pwntools工具包里的DynELF，利用DynELF工具来泄漏system函数的地址，再往bss段写入"/bin/sh"字符串，接着调用system函数

具体可以看下这里：

<https://blog.csdn.net/guiguzi5512407/article/details/52752909>

dynelf : 用于远程符号泄漏，需要提供leak方法，简单来说就是将原来需要输出的got表的地址处替换成了需要寻找的system函数的地址

  
![image.png](https://image.3001.net/images/20180910/1536562603_5b9615abd8d74.png!small)  

按照前面的思路，正常的写法是先leak出write函数的地址

  
![image.png](https://image.3001.net/images/20180910/1536562612_5b9615b43ea72.png!small)  

得到的write地址：0xf76da900

  
![image.png](https://image.3001.net/images/20180910/1536562619_5b9615bb114e0.png!small)  

  

使用leak方法泄露出system函数的地址，脚本会从github上下载相应的libc库

  
![image.png](https://image.3001.net/images/20180910/1536562645_5b9615d5d2ab2.png!small)  

system函数的地址：0xf75a2e70

  

  
![image.png](https://image.3001.net/images/20180910/1536562649_5b9615d9cf422.png!small)  

调用read函数向bss段填充/bin/sh字符串，这里为了不影响程序的正常执行

  
![image.png](https://image.3001.net/images/20180910/1536562655_5b9615df561f1.png!small)  

这里为了平衡栈（不影响程序的正常执行）需要pop三个参数，再传入read的三个参数：0，/bin/sh字符串写入的地址，8（/bin/sh的长度，末尾为\x00

接着直接调用system函数，传入的参数为/bin/sh字符串的地址，发送payload之后，sendline内容为"/bin/sh"的字符串

  

运行脚本拿到shell

  
![image.png](https://image.3001.net/images/20180910/1536562670_5b9615ee1d71d.png!small)  

0x04 结束语

所有的脚本下载：<https://github.com/H4lo/jarvisoj_pwn>

这几道题虽然算是ROP的入门题，但是正常的解法也就是这些方法，再掌握一些进阶的ROP技巧，比如绕过canary保护之类的，再加上多刷点题，那么CTF比赛中的栈溢出几乎就没有问题了。  
总的来说就是多刷题，在刷题中学习思路和技巧，但是最基本的pwn知识要掌握，比如栈的结构，基本的程序运行机制和流程，最后再推荐几个学习和刷题的网站：

[http://www.whaledu.com](http://www.whaledu.com/)

[http://pwnable.kr](http://pwnable.kr/)

###  

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

