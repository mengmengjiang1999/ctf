文章主要内容是有参CALL如何分析参数，在写汇编时如何把参数写进去以及如何调用。

以喊话CALL为例，喊话CALL是用代码来调用，打印任意的话。

1.打开x86dbg，文件-附加-打开游戏

  
![](https://image.3001.net/images/20220623/1655953365_62b3d7d5b1098174a9707.jpg!small)

2.bp
send（设置send函数的断点）回车，断点，再运行![](https://image.3001.net/images/20220623/1655953366_62b3d7d61cf8561856664.png!small)

3.在游戏中，点击“当前”，输入123456，再运行x86dbg

![](https://image.3001.net/images/20220623/1655953366_62b3d7d679cf596187561.png!small)

4.点击调用堆栈，找到断点，复制整个表格![](https://image.3001.net/images/20220623/1655953366_62b3d7d6cc6b383903aac.jpg!small)

5.新建分析文本，粘贴整个表格，只留下主线程，在第三层74开始分析

![](https://image.3001.net/images/20220623/1655953367_62b3d7d79e600e63018b9.png!small)

6.运行，然后断点禁用或删除![](https://image.3001.net/images/20220623/1655953370_62b3d7da0a71756dce6eb.jpg!small)

7.Ctrl+G返回到这里，确定

![](https://image.3001.net/images/20220623/1655953370_62b3d7da8c2f0c8338abd.png!small)

8.返回到是Nop，它的上一层就是调用的call，可以看到有三个参数rdx、r8d（r8的32位）、rcx（在64位类似fastcall，它的前四个参数分别是rcx、rdx、r8、r9)![](https://image.3001.net/images/20220623/1655953370_62b3d7dacf73555164818.jpg!small)

喊话CALL是会带一个发送的文本，有文本参数，所以先找一下参数。

9.1 点击call的地方下断点，在游戏内-当前-发送文本![](https://image.3001.net/images/20220623/1655953371_62b3d7db4327e7de767b3.jpg!small)

9.2来看一下参数，发现其他rax、rsi、r10、r11里有文本，但在r8、r9、rcx、rdx里没有

  
![](https://image.3001.net/images/20220623/1655953371_62b3d7dba087c64da47ff.jpg!small)

因此判断不是我们要找的CALL，是底层或上一层call，取消断点

9.3文本参数应该前四个参数里![](https://image.3001.net/images/20220623/1655953372_62b3d7dc10713eb61ec8c.jpg!small)

9.4 Ctrl+G返回到这里，确定

![](https://image.3001.net/images/20220623/1655953372_62b3d7dcc29f27b69e964.png!small)

9.5下个断点，走动一下（防止是其他call），再说一句话，回车![](https://image.3001.net/images/20220623/1655953373_62b3d7dd2c50df6342217.png!small)

9.6断下来，发现r8符合要求![](https://image.3001.net/images/20220623/1655953374_62b3d7dee6198085c523e.png!small)

9.7把参数记下来，然后断点运行![](https://image.3001.net/images/20220623/1655953375_62b3d7df958f2ad1934b3.png!small)

9.8复制寄存器，只留通用寄存器![](https://image.3001.net/images/20220623/1655953376_62b3d7e00cc0f7f29012a.png!small)

9.9把rcx、rdx、r8、r9参数复制下来，可以确定r8是字符串地址

10.找rdx参数

10.1
Ctrl+G返回到这里，确定![](https://image.3001.net/images/20220623/1655953376_62b3d7e0b9520dce854d3.png!small)

10.2测试rdx，在当前多喊几次话，发现寄存器没有值，所以认为rdx是写死的值-0![](https://image.3001.net/images/20220623/1655953377_62b3d7e1242f757f5862a.png!small)

10.3再切换主队，发现rdx有变化，所以判定rdx是说话的方式![](https://image.3001.net/images/20220623/1655953377_62b3d7e1b40f7bc05b697.png!small)

10.4当前模式是0，组队模式是2，团队模式是12

11.找r9参数

11.1测试r9，多喊几遍，r9没有变化，r9是写死的值-FFFFFFFF![](https://image.3001.net/images/20220623/1655953378_62b3d7e247db25f940b30.png!small)

12.找rcx参数

12.1复制rcx，重启游戏并重新打开x86dbg，文件-附加-打开游戏![](https://image.3001.net/images/20220623/1655953379_62b3d7e300b12c7f6defb.jpg!small)

12.2喊话-断点，发现rcx的值变了，所以需要找一下值

  
![](https://image.3001.net/images/20220623/1655953379_62b3d7e359cfdf135c1e6.png!small)

12.3返回调用，发现rcx来自与rbp+620，然后找一下620![](https://image.3001.net/images/20220623/1655953379_62b3d7e3da67e68d57991.png!small)

使用x64dbg继续调也可以，使用ida看起来更方便

12.4把64位客户端在64ida里打开![](https://image.3001.net/images/20220623/1655953380_62b3d7e4e92da4c6a3d0e.png!small)

12.5
CTRL+G跳转到返回的位置上，发现没有rcx赋值![](https://image.3001.net/images/20220623/1655953383_62b3d7e7770b662b2666a.png!small)

13.因为很难找到rcx，所以找到另一个突破点

13.1在寄存器里发现rbx和rcx一样，就以rbx为突破点，找到了rbx对rcx的赋值![](https://image.3001.net/images/20220623/1655953383_62b3d7e7df0b9db578747.png!small)

13.2怀疑没有通过src对rcx赋值，而是通过rbx对rcx赋值之后，通过跳转到参数传递，直接调用喊话CALL![](https://image.3001.net/images/20220623/1655953386_62b3d7ea8639d1225e71b.png!small)

13.3 若是上述情况，需要先找rbx的值

13.3.1发现是变量Var
EB0给rbx赋值![](https://image.3001.net/images/20220623/1655953388_62b3d7ec865029873c7aa.png!small)

13.3.2再寻找变量Var EB0，发现是rax赋值给变量Var EB0

![](https://image.3001.net/images/20220623/1655953389_62b3d7edd13a6e2dc6854.jpg!small)

13.3.3
rax值来源于上面的call，call的返回值是rax![](https://image.3001.net/images/20220623/1655953390_62b3d7ee6fdbffd03e6fc.png!small)

13.4 Rcx=那个call的返回值

13.4.1进一层，Rax就是call的返回值+48，然后取值![](https://image.3001.net/images/20220623/1655953390_62b3d7eed3fefec360dc2.png!small)

13.4.2再进去一层，发现一个基址放在rax里![](https://image.3001.net/images/20220623/1655953391_62b3d7ef793f75cc6877f.png!small)​

13.4.3
Rcx=[0x基址+0x48]![](https://image.3001.net/images/20220623/1655953391_62b3d7efdd421ca56e8e0.png!small)

到此数据分析的四个参数已经都找到了

