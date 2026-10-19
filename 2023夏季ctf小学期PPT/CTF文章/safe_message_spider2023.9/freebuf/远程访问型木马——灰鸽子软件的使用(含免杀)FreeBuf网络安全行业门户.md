## 远程访问型木马——灰鸽子

先来了解下什么是远程访问型木马：

1.它在受害者主机上运行一个服务端，监听某个特定端口；入侵者则使用木马的客户端连接到该端口上，向服务端发送各种指令，访问受害者计算机资源。

2.使用这类木马，只需有人运行了服务端程序，如果客户知道了服务端的IP地址，就可以实现远程控制。

3.这类程序可以实现观察受害者正在干什么。

再来了解下灰鸽子：

1.自2001年，灰鸽子诞生之日起，就被反病毒专业人士判定为最具危险性的后门程序，并引发了安全领域的高度关注。2004年、2005年、2006年，灰鸽子木马连续三年被国内各大杀毒厂商评选为年度十大病毒。

2.灰鸽子在出现的时候使用了当时讨论最多的“反弹端口”连接方式，用以躲避大多数个人网络防火墙的拦截。

反弹端口连接方式：

[![](https://image.3001.net/images/20210517/1621245315_60a23d833c4dfaf2017a0.png!small)](https://image.3001.net/images/20210517/1621245315_60a23d833c4dfaf2017a0.png!small)

3.由于灰鸽子栏截了API调用，在正常模式下服务谜程序文件和它注珊的服务项均被晚藏，也就是说你即使设置了显示所有隐藏文件也看不到它们。此外，灰鸽子服务端的文件名也是可以自定义的。

## 一、实验目的

1、理解远程控制型木马的实现原理，使用灰鸽子木马实现远程控制目标主机；

2、实现木马与图片的捆绑；（两个捆绑软件）

3、实现木马与exe程序的捆绑；

4、将木马注册成系统服务。

## 二、实验设备及环境

计算机1台、虚拟机XP系统、虚拟机2003系统、灰鸽子软件

## 三、实验步骤

### 1.实验环境配置

两个虚拟机配置为NAT模式，配置IP地址为同一网段，并且用ping命令测试连通性。

### 2.安装灰鸽子软件

（1）点击运行灰鸽子软件，将会在C盘保存一份重复的软件。

[![](https://image.3001.net/images/20210517/1621245316_60a23d84cc89fed4b6bd2.png!small)](https://image.3001.net/images/20210517/1621245316_60a23d84cc89fed4b6bd2.png!small)

（2）将原文件夹中的三个文件夹拷贝至C盘。

[![](https://image.3001.net/images/20210517/1621245317_60a23d85be07de1654ac7.png!small)](https://image.3001.net/images/20210517/1621245317_60a23d85be07de1654ac7.png!small)

（3）点击C盘的灰鸽子软件，界面如下。

[![](https://image.3001.net/images/20210517/1621245318_60a23d86dc70e756288e8.png!small)](https://image.3001.net/images/20210517/1621245318_60a23d86dc70e756288e8.png!small)

### 3.服务器配置

（1）点击界面上的“配置服务程序”图标：

[![](https://image.3001.net/images/20210517/1621245320_60a23d880a507327633e7.png!small)](https://image.3001.net/images/20210517/1621245320_60a23d880a507327633e7.png!small)

（2）固定IP上线，填写自己本地主机的IP地址，其他默认更改保存路径和名称，保存生成服务器。

[![](https://image.3001.net/images/20210517/1621245321_60a23d893354e63692b18.png!small)](https://image.3001.net/images/20210517/1621245321_60a23d893354e63692b18.png!small)

[![](https://image.3001.net/images/20210517/1621245322_60a23d8a61b9954f81a51.png!small)](https://image.3001.net/images/20210517/1621245322_60a23d8a61b9954f81a51.png!small)

[![](https://image.3001.net/images/20210517/1621245323_60a23d8b63c7c8f812047.png!small)](https://image.3001.net/images/20210517/1621245323_60a23d8b63c7c8f812047.png!small)

[![](https://image.3001.net/images/20210517/1621245324_60a23d8c4e1cf70daca43.png!small)](https://image.3001.net/images/20210517/1621245324_60a23d8c4e1cf70daca43.png!small)

### 4.木马植入

将木马植入目标主机，点击运行，则灰鸽子软件上会自动显示上线的主机信息。

[![](https://image.3001.net/images/20210517/1621245325_60a23d8d57ffb1506182e.png!small)](https://image.3001.net/images/20210517/1621245325_60a23d8d57ffb1506182e.png!small)

进行远程控制

[![](https://image.3001.net/images/20210517/1621245326_60a23d8edd0b8030b5a4a.png!small)](https://image.3001.net/images/20210517/1621245326_60a23d8edd0b8030b5a4a.png!small)

捕捉屏幕，目标主机在做什么事情你都可以检测得到。

[![](https://image.3001.net/images/20210517/1621245328_60a23d9051bd5f9ae6665.png!small)](https://image.3001.net/images/20210517/1621245328_60a23d9051bd5f9ae6665.png!small)

远程控制命令

通过远程控制命令可以向目标主机发送系统命令。

[![](https://image.3001.net/images/20210517/1621245329_60a23d91ee941231ffbb6.png!small)](https://image.3001.net/images/20210517/1621245329_60a23d91ee941231ffbb6.png!small)

命令广播

通过命令的广播可以远程控制目标主机开关机，以及打开特定网页。

[![](https://image.3001.net/images/20210517/1621245332_60a23d9498a5fd5ff6051.png!small)](https://image.3001.net/images/20210517/1621245332_60a23d9498a5fd5ff6051.png!small)

[![](https://image.3001.net/images/20210517/1621245333_60a23d95c208e6cbc2403.png!small)](https://image.3001.net/images/20210517/1621245333_60a23d95c208e6cbc2403.png!small)

命令广播中的消息广播

[![](https://image.3001.net/images/20210517/1621245334_60a23d96a1a75c740f4bc.png!small)](https://image.3001.net/images/20210517/1621245334_60a23d96a1a75c740f4bc.png!small)

[![](https://image.3001.net/images/20210517/1621245336_60a23d980f89ec91a616a.png!small)](https://image.3001.net/images/20210517/1621245336_60a23d980f89ec91a616a.png!small)

对计算机资源的控制

（1）对文件夹的控制，新建一个文件。

[![](https://image.3001.net/images/20210517/1621245337_60a23d995593c2dbae372.png!small)](https://image.3001.net/images/20210517/1621245337_60a23d995593c2dbae372.png!small)

[![](https://image.3001.net/images/20210517/1621245338_60a23d9a65da9b85ef2eb.png!small)](https://image.3001.net/images/20210517/1621245338_60a23d9a65da9b85ef2eb.png!small)

（2）下载被控方的文件，也可以远程打开，被控方同样操作

[![](https://image.3001.net/images/20210517/1621245339_60a23d9b6283c4c47325b.png!small)](https://image.3001.net/images/20210517/1621245339_60a23d9b6283c4c47325b.png!small)

### 5.木马捆绑

5.1.散人文件捆绑器：

先卸载木马服务端程序，源文件为图片，捆绑文件为木马，点击选择图标可更改显示的图标。

[![](https://image.3001.net/images/20210517/1621245340_60a23d9c7e1f730ebbb88.png!small)](https://image.3001.net/images/20210517/1621245340_60a23d9c7e1f730ebbb88.png!small)

[![](https://image.3001.net/images/20210517/1621245341_60a23d9d3ebb1b9c99cd7.png!small)](https://image.3001.net/images/20210517/1621245341_60a23d9d3ebb1b9c99cd7.png!small)

点击捆绑，生成捆绑文件，点击运行，打开图片，木马上线；

[![](https://image.3001.net/images/20210517/1621245342_60a23d9ea6f90eb52f2b3.png!small)](https://image.3001.net/images/20210517/1621245342_60a23d9ea6f90eb52f2b3.png!small)

[![](https://image.3001.net/images/20210517/1621245344_60a23da00b9670eb149af.png!small)](https://image.3001.net/images/20210517/1621245344_60a23da00b9670eb149af.png!small)

5.2.多文件捆绑器：

先卸载木马服务端程序；打开捆绑软件，将图片与木马进行捆绑；

[![](https://image.3001.net/images/20210517/1621245345_60a23da10d11963cb30e1.png!small)](https://image.3001.net/images/20210517/1621245345_60a23da10d11963cb30e1.png!small)

点击捆绑，生成捆绑文件，点击运行，打开图片，木马上线；

[![](https://image.3001.net/images/20210517/1621245346_60a23da2b1e94f8ee753d.png!small)](https://image.3001.net/images/20210517/1621245346_60a23da2b1e94f8ee753d.png!small)

[![](https://image.3001.net/images/20210517/1621245347_60a23da3e6b96387d7d64.png!small)](https://image.3001.net/images/20210517/1621245347_60a23da3e6b96387d7d64.png!small)

5.3.exe捆绑软件：

1.先卸载木马服务端程序；打开exe捆绑软件，第一个选择你的游戏程序；

[![](https://image.3001.net/images/20210517/1621245348_60a23da4b8966b7db3a90.png!small)](https://image.3001.net/images/20210517/1621245348_60a23da4b8966b7db3a90.png!small)

2.第二个选择你的木马程序；

[![](https://image.3001.net/images/20210517/1621245349_60a23da5dd6693d54083d.png!small)](https://image.3001.net/images/20210517/1621245349_60a23da5dd6693d54083d.png!small)

3.指定保存的路径：

[![](https://image.3001.net/images/20210517/1621245351_60a23da726157748bf19e.png!small)](https://image.3001.net/images/20210517/1621245351_60a23da726157748bf19e.png!small)

4.点击开始捆绑，成功后将木马拷贝被攻击方再测试一遍，即可看到木马上线。

[![](https://image.3001.net/images/20210517/1621245351_60a23da7f231bc2ebb821.png!small)](https://image.3001.net/images/20210517/1621245351_60a23da7f231bc2ebb821.png!small)

[![](https://image.3001.net/images/20210517/1621245352_60a23da8a273531e9486f.png!small)](https://image.3001.net/images/20210517/1621245352_60a23da8a273531e9486f.png!small)

[![](https://image.3001.net/images/20210517/1621245353_60a23da94f3b0e27dde4b.png!small)](https://image.3001.net/images/20210517/1621245353_60a23da94f3b0e27dde4b.png!small)

### 6.木马注册成系统服务

先卸载木马服务端程序；

[![](https://image.3001.net/images/20210517/1621245354_60a23daa4649b9fcfc893.png!small)](https://image.3001.net/images/20210517/1621245354_60a23daa4649b9fcfc893.png!small)

[![](https://image.3001.net/images/20210517/1621245355_60a23dab561192b54373a.png!small)](https://image.3001.net/images/20210517/1621245355_60a23dab561192b54373a.png!small)

工具：instsrv.exe：给系统安装和删除服务

srvany.exe：让程序以服务的方式运行

1、命令：instsrv.exe CQLService C:\srvany\srvany.exe（其中CQL为姓名缩写）

[![](https://image.3001.net/images/20210517/1621245356_60a23dac3fc48bcf1b502.png!small)](https://image.3001.net/images/20210517/1621245356_60a23dac3fc48bcf1b502.png!small)

2、打开注册表目录：命令行输入“regedit”
，回车；HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services

3、找到“CQLService”，鼠标右击新建一个项，将其命名为“Parameters” ；

4、进入Parameters后，在右侧窗口里新建一个命名为“Application” 的字符串值，字符串的值就是木马程序的路径地址。

5、在右侧窗口里再新建一个命名为“AppDirectory” 的字符串值，字符串的值就是存放木马程序的文件夹路径。

[![](https://image.3001.net/images/20210517/1621245357_60a23dad4d9925604d4b9.png!small)](https://image.3001.net/images/20210517/1621245357_60a23dad4d9925604d4b9.png!small)

6、启动服务：命令行输入“services.msc”，回车

[![](https://image.3001.net/images/20210517/1621245358_60a23dae79d8f8384ed43.png!small)](https://image.3001.net/images/20210517/1621245358_60a23dae79d8f8384ed43.png!small)

7、木马上线

[![](https://image.3001.net/images/20210517/1621245359_60a23dafabeb4eb751e2c.png!small)](https://image.3001.net/images/20210517/1621245359_60a23dafabeb4eb751e2c.png!small)

8、卸载服务：卸载之前应停止服务！

instsrv CQLService remove

[![](https://image.3001.net/images/20210517/1621245360_60a23db09908f19a8cf2c.png!small)](https://image.3001.net/images/20210517/1621245360_60a23db09908f19a8cf2c.png!small)

## 四、灰鸽子免杀

谈到免杀的方法，首先就要先弄懂那些杀毒软件到底是如何杀的原理，这里就来讲一讲

### 1.杀毒原理

通常的话，当研究病毒查杀与防御的人收到一个截获或者上报上来的病毒时，先是分析这个病毒文件执行后的动作，即病毒文件执行后会做哪些操作。例如会生成什么样的新文件、会怎样去更改注册表、会怎样去注册服务、会打开什么端口等等。

搞明白这些以后，下一步一般就会开始研究这个病毒的文件结构，然后找出其与众不同的地方，将其定义为特征码。而这个特征码定义的高明与否，就要看他定义的位置到底是怎么样的，例如他如果定义的是病毒文件更改注册表键值那部分代码的话，这显然不会太难，因为只要病毒文件更改键值，大部分的情况下这个文件里一定存在被更改键值的字符串，所以找到这段字符串的位置就可以定义特征码了。但是针对这种特征码制作免杀是非常容易的，其中有一种免杀方法就是把特征码所对应的内容是可识别的英文字母或词组，并且确定其不是相关函数的,将大小写修改一下就可以了。而如果从文件头找出一段特征码已经是非常不容易的事情了。除此之外，所定义的特征码还要有一个分支，即内存特征码。所谓内存特征码就是指木马文件运行后释放到内存时所存在的特征，它的原理大体与上面介绍的文件特征码一样。

当特征码定义出来之后，就会被提交到另外的部门，然后进入病毒库，当用户更新病毒库后，以后杀毒软件在碰到符合要求的文件时就会将其杀掉，也就是说，杀毒软件只认特征码，不认文件。

由此可见，他们寻找特征码的方式也就是这样的。那接下来就来谈谈几种常用的免杀方式吧。

### 2.免杀方法

常见的灰鸽子免杀方法有：加壳压缩、加花指令、修改特征码、修改程序入口点等等，另外，在互联网上也存在着免杀版本的灰鸽子，并且不断更新。因为大多做了免杀汇编处理，所以对其客户端的查杀比较困难，大多数杀毒软件也无法识别它为病毒。

2.1.加花指令

由于黑客网站公布的花指令过不了一段时间就会被杀软辨认出来，所以需要你自己去搜集一些不常用的花指令，另外目前还有几款软件可以自动帮你加花指令，例如花指令添加器等。

常见的花指令有：  
1.Visual C++ 6.0：

    
    
    PUSH EBP 　　MOV EBP,ESP 　　PUSH -1 　　PUSH 0 　　PUSH 0 　　MOV EAX,DWORD PTR FS:[0] 　　PUSH EAX 　　MOV DWORD PTR FS:[0],ESP 　　SUB ESP,68 　　PUSH EBX 　　PUSH ESI 　　PUSH EDI 　　POP EAX 　　POP EAX 　　POP EAX 　　ADD ESP,68 　　POP EAX 　　MOV DWORD PTR FS:[0],EAX 　　POP EAX 　　POP EAX 　　POP EAX 　　POP EAX 　　MOV EBP,EAX 　　JMP 原入口
    

  2. Visual C++ 5.0

    
    
    PUSH EBP 　　MOV EBP,ESP 　　PUSH -1 　　push 515448 　　PUSH 6021A8 　　MOV EAX,DWORD PTR FS:[0] 　　PUSH EAX 　　MOV DWORD PTR FS:[0],ESP 　　ADD ESP,-6C 　　PUSH EBX 　　PUSH ESI 　　PUSH EDI 　　jmp 跳转到程序原来的入口点
    

2.1.1.花指令相关知识

其实花指令就像上面那样，就是一段垃圾代码和一些乱跳转，但这些并不影响程序的正常运行。加了花指令后，可以使一些杀毒软件无法正确识别木马程序，从而达到免杀的效果。

2.1.2.制作过程详解

1.配置一个不加壳的木马程序。  
2.用OllyDbg载入这个木马程序，OllyDbg会自动停在入口点，同时记下入口点的内存地址。  
3.向下拉滚动条，找到零区域（也就是可以插入代码的都是0的空白地方）。并记下零区域的起始内存地址。  
4.从这个零区域的起始地址开始一句一句的写入我们准备好的花指令代码。  
5.花指令写完后，在花指令的结束位置写入一条`JMP`指令，跳转到刚才OD载入时的入口点内存地址。  
6.保存修改结果后，最后用 **PEditor**
这款工具打开这个改过后的木马程序。在入口点处把原来的入口地址改成刚才记下的零区域的起始内存地址，并按应用更改，使更改生效。  
例子：

    
    
    004A2A73 0000     add byte ptr ds:[eax],al
    
    004A2A75 0000     add byte ptr ds:[eax],al
    
    004A2A77 55     push ebp
    
    004A2A78 8BEC     mov ebp,esp
    
    004A2A7A B9 04000000   mov ecx,4
    
    004A2A7F E9 CCF3FFFF   jmp Server.004A1E50
    
    004A2A84 0000     add byte ptr ds:[eax],al
    
    004A2A86 0000     add byte ptr ds:[eax],al
    
    004A2A88 0000     add byte ptr ds:[eax],al
    

上面的`add byte ptr ds:[eax],al`就是所谓的零区域，我们看到改完后的头文件位于004A2A77，所以我们还要用
**PEditor** 改一下入口点，打开 **PEditor** 后载入文件，将入口点处的地址改为我们的新文件头地址004A2A77，保存后即可。  
入口点加1：  
打开PEditor后载入文件，将原来的入口点+1即可，例如我们的入口点为004A2A77，加1后应该是004A2A78，然后点击“应用更改”即可完成更改。

2.2.修改特征码

2.2.1.修改字符串大小写

刚才上文中也有提到，这里再说一下  
这是利用了Windows系统对大小写不敏感，而杀毒软件对大小写非常敏感的这一特性来达到免杀的目的。

它的修改方法就是：把特征码所对应的内容是可识别的英文字母或词组，并且确定其不是相关函数的,将大小写修改一下就可以了。

它的使用条件是特征码所对应的内容必需是字符串,否则不能成功。

2.2.2.ADD指令与SUB指令互换

这是利用了“1+1等于2，而1-（-1）也等于2”的原理。那么ADD指令就是“加”的意思，SUB指令则是“减”的意思。我们这样互换了一下，最终结果还是一样的，但是杀毒软件就不认识了。

它的修改方法是：用OllyDbg载入木马程序，然后假设它的特征码所对应的地址中有ADD指令或者SUB指令，那么就将ADD指令与SUB指令互换，然后后面的十六进制数要自己改成负的。更改完毕后保存为EXE文件即可。

## 五、灰鸽子绕过杀毒软件

现在很多人在使用免杀灰鸽子软件后，遇见过这样一个奇怪的情况，就是明明已经免杀的文件，在导入用户的配置信息以后就立即被某些杀毒软件的数据流功能所查杀。那么下面就说几个方法来解决它。

### 1.修改配置信息

既然是在导入配置信息后才被某些杀毒软件所查杀的，说明问题就出现在配置信息里面。

首先运行修改工具 **Restorator**
（这个工具挺好用的，打造个人版的灰鸽子软件的时候需要用到的软件）,点击工具栏中的“打开文件”来选择服务端程序。

[![](https://image.3001.net/images/20210517/1621245361_60a23db17e2a80e569562.png!small)](https://image.3001.net/images/20210517/1621245361_60a23db17e2a80e569562.png!small)

接着在资源树中选择“RC数据”中的“HACKER”选项，现在从右侧窗口可以看到一串字符串信息，这就是经过服务端加密处理的配置信息内容。  
现在点击工具栏中的“编辑模式”按钮，只需要对加密信息中原有的英文字母改成小写即可。至于要更改多少个英文字母，就完全是凭个人意愿了，既可以改一个也可以改多个。完成操作以后，点击“文件”中的“另存为”命令，将文件重命名为其他的名称即可。

[![](https://image.3001.net/images/20210517/1621245362_60a23db26ed0f543b9491.png!small)](https://image.3001.net/images/20210517/1621245362_60a23db26ed0f543b9491.png!small)

经过这样处理过的灰鸽子软件，就不会被某些杀毒软件查杀了。

### 2.更改调整信息

既然文件可以被查杀就说明其存在特征码，因此还可以按照传统的方法来查杀并修改特征码。运行特征码分析程序 **MYCCL**
，按照以前介绍的方法进行设置，只不过需要点击操作界面中的“正向”按钮，来改变程序默认的分析方式。最终 **MYCCL**
程序得到的特征码位置是`00000100_00000002`。

[![](https://image.3001.net/images/20210517/1621245363_60a23db38df4b510fb6bd.png!small)](https://image.3001.net/images/20210517/1621245363_60a23db38df4b510fb6bd.png!small)

现在运行十六进制工具 **C32Asm**
，点击“文件”菜单的“打开十六进制文件”，选择被杀的灰鸽子程序。接着点击右键菜单中的“跳到”命令，然后在弹出的窗口中输入“00000100”。

[![](https://image.3001.net/images/20210517/1621245365_60a23db52242f4db97359.png!small)](https://image.3001.net/images/20210517/1621245365_60a23db52242f4db97359.png!small)

从搜索结果中我们可以看到，特征码的位置和文件的PE头位置很接近。于是试着通过更改PE头，结果不是被金山给查杀了，就是服务端运行出现错误。于是就想在特征码前后的位置进行更改，因为这些地方有很多代码都是00，这样更改不会引起服务端的错误。于是我就将特征码所在的上一行的最后一个字节由00改成90，保存后发现文件不被查杀。另外，从PE头向下数第八行的最后一个字节在修改后也可以起到免杀的效果。这种方法不但适合于对服务端的修改，也适合于服务端母体的修改。通过“文件”菜单的“另存为”命令，将修改后的文件命名为`CServer.Dat`。然后将生成的母体文件复制到“Cache”文件夹中，替换原来的`CServer.dat`即可，这样用户以后就可以直接配置免杀的服务端。

## 六、安全措施

那么如何发现自己的电脑是否中了该木马呢？下面几点如果有其一你就应该有所重视了。

1.电脑在空闲的时候看到硬盘灯不断的闪烁发亮；

2.电脑的鼠标指针有时候会自动（非自己）移动；

3.电脑开机变得缓慢，运行时无故经常卡机甚至死机；

4.如果你的电脑装有摄像头的话，有时会发觉摄像头会自动开启（非自己）等。如果发现有如上非正常情况，最直接的临时措施就是果断的拔掉网线查找原因，然后升级最新的杀毒软件进行全盘的病毒查杀（最后在安全模式来个重启复查）。

