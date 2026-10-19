原创： EDI-VOID  合天智汇

  

格式化字符串漏洞是因为c语言中printf的参数个数不是确定的，参数的长度也不是确定的，当printf把我们的输入当作第一个参数直接输出的时候，我们输入若干格式化字符串，会增加与格式化字符串相对应的参数，会泄露出栈中的内容

Canary的工作原理就是子函数在做自己的事情之前，在自己的栈帧里返回地址之前插入一个随机的cookie，从gs:0x14的地方取出来，然后在函数返回之前对比栈中的这个随机值和gs:0x14来断定是否发生栈溢出，常用的对canary的绕过方法有通过格式化字符串泄露canary，劫持__stack_chk_fail，覆盖argv[0]等等，这里我们有格式化字符串漏洞，就直接用格式化字符串泄露出canary

 **思路**

  
![图片.png](https://image.3001.net/images/20181129/1543492157_5bffd23d93e2c.png!small)

  

![图片.png](https://image.3001.net/images/20181129/1543492165_5bffd24516e3e.png!small)  

用ida简单看了一下逻辑，就是让你输入名字，然后调用get_message函数输出你的名字，然后让你留言，留言有溢出漏洞，显然用了printf，也有格式化字符串漏洞

检查一下程序开启的保护措施以及其他一些常规的东西

  
32位程序，只开启了Canary，所以我们可以用格式化字符串漏洞泄露出栈上保存的Canary  
，没有开启NX，说明堆栈可执行，我们可以在第二次输入中直接把shellcode布置到栈里面

然后返回到栈里面

下面是get_message函数的反汇编代码

![图片.png](https://image.3001.net/images/20181129/1543492195_5bffd2635af2b.png!small)  

chars到返回地址之前一共是0x70+4即116个字节即29个dword  
不要问我为啥，我喜欢以四字节为单位  
payload可以构造为如下形式

![图片.png](https://image.3001.net/images/20181129/1543492202_5bffd26a60078.png!small)  

这是第二步溢出的思路  
在这之前我们要先通过格式化字符串漏洞泄漏出canary和我们shellcode的地址

这里计算canary相对于printf第一个参数的偏移的话，不用算，有技巧  
  

先生成格式化字符串

![图片.png](https://image.3001.net/images/20181129/1543492209_5bffd2715ddc5.png!small)  

再附加调试器，在moveax,gs:0x14处下一句下断点，运行以后输入生成的格式化字符串  
会断在下一句，这时候记下eax的值，然后输入c继续运行，复制输出的字符串

  
![图片.png](https://image.3001.net/images/20181129/1543492216_5bffd27817c84.png!small)  

![图片.png](https://image.3001.net/images/20181129/1543492222_5bffd27eae829.png!small)  

![图片.png](https://image.3001.net/images/20181129/1543492229_5bffd285c5a80.png!small)  

mov eax,gs:0x14  
mov DWORD PTR [ebp-0xc],eax

  
![图片.png](https://image.3001.net/images/20181129/1543492236_5bffd28cb036f.png!small)  

0x2a8-0x218=0x90

exploit

  
![图片.png](https://image.3001.net/images/20181129/1543492243_5bffd2932796a.png!small)  

![图片.png](https://image.3001.net/images/20181129/1543492248_5bffd298b5aac.png!small)  

题目放在了百度网盘，

链接:https://pan.baidu.com/s/1jDVh637xVIBvu8RhgB9Umw

提取码:g7bx

  

