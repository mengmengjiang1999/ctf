这节课主要通过以下实验来学习IDA Pro(静态分析神器)的使用。  
![image](https://image.3001.net/images/20210908/1631067018_61381b8adc99f90b0f6b7.png!small)

## Lab05-01题目：

题目及实验例子下载：[点我传送](https://github.com/Vxer-Lee/MalwareAnalysis/tree/master/4.%20IDA%20Pro%E7%A5%9E%E5%99%A8%E7%9A%84%E4%BD%BF%E7%94%A8/Labs)  
这节课的题目有点多，大家一定要认真做完每个题目，然后根据文章解析进行学习。

> 题目1：DllMain的地址是什么？
>
> 题目2：使用Imports窗口并浏览到的gethostbyname，导入函数定位到什么地址？
>
> 题目3：有多少函数调用了gethostbyname？
>
> 题目4：将精力集中在位于0x10001757处的对gethostbyname的调用，你能找出哪个DNS请求将被触发吗？
>
> 题目5：IDA Pro识别了在0x10001656处的子过程中的多少个局部变量？
>
> 题目6：IDA Pro识别了在0x10001656处的子过程中的多少个参数？
>
> 题目7：使用Strings窗口，来在反汇编中定位字符串\cmd.exe /c 。它位于哪？
>
> 题目8：在引用\cmd.exe /c的代码所在的区域发生了什么？
>
>
> 题目9：在同一的区域，在0x100101C8处，看起来好像是dword_1008E5C4是一个全局变量，它帮助决定走哪条路径。那恶意代码是如何设置dword_1008E5C4的呢？(提示：使用dword_1008E5C4的交叉引用。)
>
> 实验对象：Lab05-01.dll
    
    
    使用工具：
    1. IDA Pro
    

### 题目1：利用IDA Pro分析dll的入口点并显示地址

按照如下步骤打开IDA Pro并且加载dll文件进行分析。

![image-20210816104447048](https://image.3001.net/images/20210907/1631003855_613724cf211a55546f78a.png!small)

![image-20210816104555256](https://image.3001.net/images/20210907/1631003855_613724cf9cbbfd07ca15d.png!small)

![image-20210816104634494](https://image.3001.net/images/20210907/1631003856_613724d055b7ff2142f25.png!small)

等待分析完毕后，IDA Pro自动的会显示出dll的入口点函数`dllmain`，如图。

题目1让我们显示出dllmain函数的地址，这里有两种方法，第一种方法是直接按空格切换成文本视图，第二种方法是在设置中显示带地址的图形显示。  
![image-20210816104746502](https://image.3001.net/images/20210907/1631003856_613724d0d70e17190b317.png!small)

#### 空格切换文本视图：

![image-20210816105000976](https://image.3001.net/images/20210907/1631003857_613724d1580609ddf22a1.png!small)

#### 带地址显示图形界面

点击菜单 Options->General...->勾上 Line prefixes (graph)

![image-20210816105345486](https://image.3001.net/images/20210907/1631003857_613724d1e8a89e38496fa.png!small)

![image-20210816105414962](https://image.3001.net/images/20210907/1631003858_613724d263163e68a6d03.png!small)

### 题目2：IDA Pro导入表窗口

在`Imports`窗口中按`ctrl+f`进行搜索输入`gethostbyname`，定位到gethostbyname后双击过去调到文本视图界面看到其地址。

![image-20210816110307586](https://image.3001.net/images/20210907/1631003859_613724d30ebedf799878e.png!small)

![image-20210816110608131](https://image.3001.net/images/20210907/1631003859_613724d383c0062f9de86.png!small)

### 题目3：交叉应用，看多少处函数调用了

在`gethostbyname`处按`ctrl+x`调出`交叉引用`，能看到所有对gethostbyname处有调用读取写入等的所有地方。

点击`Type`进行类型排序，然后我们仔细来看这里有两个Type，一个是`p`代表的是函数,`r`代表的是读取属性，

所以这里一共有9个p，但是这9个p并不能代码是9个函数调用了，我们在仔细来看图2，其中他有很多地址重复的，所以我们按照地址来分一共可以分析出是4处函数调用了gethostbyname。

![image-20210816111105632](https://image.3001.net/images/20210907/1631003860_613724d42f1db9e38821d.png!small)

![image-20210816111304620](https://image.3001.net/images/20210907/1631003860_613724d4b6c02928b74fa.png!small)

### 题目4：利用ctrl+g跳转地址

将精力集中在位于0x10001757处的对gethostbyname的调用，你能找出哪个DNS请求将被触发吗？

首先我们用ctrl+c拷贝`0x10001757`这个地址，然后在IDA Pro文本视图或界面视图，按`g`按键，跳转到对应的地址处。

![image-20210816112256669](https://image.3001.net/images/20210907/1631003861_613724d53c6afb932df0c.png!small)

![image-20210816112341517](https://image.3001.net/images/20210907/1631003861_613724d59ef93be0f5c14.png!small)

切换到界面视图，然后对题目4的问题进行分析：你能找出哪个DNS请求将被触发吗？，我们找找gethostbyname的参数，一般call的意思就是调用函数，这里call
gethostbyname就是调用gethostbyname这个api函数，然后call上面挨着的push就是函数参数，可以看到这里就一个参数`push
eax`，参数是eax，所以我们来看看是什么给eax进行了赋值，往上可以看到有一句`mov
eax,off_10019040`，这种带off_或者dword_下划线后面加个地址的可能都是`全局变量`，在后面有个注释是IDA
Pro自动加上的，他这里分析出来off_10019040是一个字符串`[This is RDO]pics.praticalmalwareanalys`

![image-20210816112956670](https://image.3001.net/images/20210907/1631003862_613724d637279d4953de7.png!small)

我们也可以直接双击全局变量过去，跳到他的定义处，在图一中还有一句`add
eax,0Dh`，意思是将eax字符串的指针指向从开头后0xD也就是后13处，那么正好是`pics.praticalmalwareanalys`这个域名被解析。（答案）

![image-20210816113033143](https://image.3001.net/images/20210907/1631003862_613724d6991e91522b471.png!small)

### 题目5：局部变量分析

IDA Pro识别了在0x10001656处的子过程中的多少个局部变量？

首先跳转到地址处，不再重复如何跳转。然后我们在汇编代码的上面可以看到这些东西，红色标记的地方，这些都是局部变量和参数，其中`带负号的`都是局部变量，这里一共有23个带负号的，也就是23个局部变量。

![image-20210816114619883](https://image.3001.net/images/20210907/1631003863_613724d71366ec51259cf.png!small)

### 题目6：函数参数分析

IDA Pro识别了在0x10001656处的子过程中的多少个参数？

看上面的图，其中`正数`的就是参数，这里只有一个参数`lpThreadParameter`，其实也可以看函数头注释那里，IDA
Pro自动分析出了`DWORD __stdcall sub_10001656(LPVOID lpThreadParameter)`,可以看出是一个参数。

### 题目7：Strings字符串窗口

使用Strings窗口，来在反汇编中定位字符串\cmd.exe /c 。它位于哪？

我们可以按`shift+f12`来打开字符串窗口，可以在菜单中点击`View->Open subviews->Strings`打开字符串窗口。

![image-20210816115335485](https://image.3001.net/images/20210907/1631003863_613724d7a15015a5f042b.png!small)

![image-20210816115422773](https://image.3001.net/images/20210907/1631003864_613724d845d5487311d5b.png!small)

双击过去之后点击这个地方，然后在图2中可以看到是`0x100101D0`位置的反汇编`push offset aCmdExeC`处。

![image-20210816115504628](https://image.3001.net/images/20210907/1631003864_613724d8b6e0c21da3122.png!small)

![image-20210816115756935](https://image.3001.net/images/20210907/1631003865_613724d95ffe930a882f0.png!small)

### 题目8：代码分析

在引用\cmd.exe /c的代码所在的区域发生了什么？

我们在`100101D0`地址处，按一下按键`F5`进入反编译`C++伪代码`进行代码分析。

首先我们在函数开头的地方开始逐步分析，可以看到一些敏感的字符串，这里有个关键字`Remote Shell
Session`，所以这个程序应该是一个恶意远程Shell程序。

![image-20210816131035431](https://image.3001.net/images/20210907/1631003865_613724d9f3cec00e7043e.png!small)

接着就是用控制命令，远程创建cmd命令来达到执行Shell的目的。

![image-20210816131140039](https://image.3001.net/images/20210907/1631003866_613724da86e44eb6a1933.png!small)

![image-20210816132027587](https://image.3001.net/images/20210907/1631003867_613724db11a595a66e606.png!small)

![image-20210816132157267](https://image.3001.net/images/20210907/1631003867_613724db8cbac05f028ac.png!small)

![image-20210816132317331](https://image.3001.net/images/20210907/1631003868_613724dc0c55ee9c6ebe2.png!small)

### 题目9：进阶分析

在同一的区域，在0x100101C8处，看起来好像是dword_1008E5C4是一个全局变量，它帮助决定走哪条路径。那恶意代码是如何设置dword_1008E5C4的呢？(提示：使用dword_1008E5C4的交叉引用。)

跳转到地址，然后点击全局变量，在全局变量位置处按`ctrl+x`调出交叉引用，然后可以看到有w
和r两种属性，其中我们可以知道w就是写入属性，而题目中需要我们来`cmp`走哪条分支，还有如何设置dword_1008E5C4全局变量，那么肯定是要看w属性看是什么东西写入到了全局变量`dword_1008E5C4`。

![image-20210816133055222](https://image.3001.net/images/20210907/1631003868_613724dc72dd7a78ad55b.png!small)

![image-20210816133213139](https://image.3001.net/images/20210907/1631003868_613724dced072b22d3358.png!small)

可以看到代码处是eax复制给了全局变量`dword_1008E5C4`,而eax来源于上一句call的返回值，所以我们需要继续跟入Call来看他的返回值是什么？

![image-20210816133907012](https://image.3001.net/images/20210907/1631003869_613724dda2f63fcb4a929.png!small)

sub_10003695函数功能是获取系统版本信息，并且判断系统版本是否为NT系统，如果是返回true,否则返回false。

![image-20210816134131308](https://image.3001.net/images/20210907/1631003870_613724de3d6352e53201a.png!small)

![image-20210816134330714](https://image.3001.net/images/20210907/1631003870_613724dea8928181be466.png!small)

根据上面的分析我们可以得出结论，dword_1008E5C4的值应该是true也就是不为0，所以他不会跳转到loc_1001d7处，而是继续执行"cmd.exe
/c"处。

![image-20210816134724611](https://image.3001.net/images/20210907/1631003871_613724df238f99c2bf99f.png!small)

## 总结：

这一节我们学习了IDA Pro的很多知识，主要学会了IDA Pro

> 文本视图和界面视图的切换（用空格按键）
>
> 在界面视图显示地址
>
> 查看IDA Pro的导入表窗口
>
> 交叉引用，查看被多少处函数调用(ctrl + x)
>
> 地址的跳转(ctrl + g)
>
> 函数内局部变量的分析（带负号的）
>
> 函数参数分析(push xx,call xxx)、(正数的)
>
> Strings 字符串窗口的查看(shift + f12)
>
> 代码分析(f5)
>
> 静态分析流程分支，追溯(利用ctrl +x) 看w和r属性，分析函数返回值

有兴趣的可加QQ群：1145528880 （一起学习 逆向、PWN二进制安全、Web信息安全、IoT安全、游戏逆向分析原理交流）

