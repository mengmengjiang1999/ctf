本文首发于“合天智汇” 作者：xiaoyuer

本次是实现一个木马下载器（Trojan
Downloader），从某个指定的URL中下载一个文件，并将其在后台偷偷运行起来。主要使用的API函数是URLDownloadToFile和WinExec。

这次分两步开发，第一步开发一个复制自身到C盘windows目录的程序，然后再开发一个木马下载器，同时进行逆向分析。

# 一、开发复制自身的程序

![](https://image.3001.net/images/20201028/1603871662_5f9923ae00cc23fe7ed53.jpg!small)

VC6.0默认情况下代码高亮效果不好，安装VC++6.0助手后效果会变好很多，当然也可以使用visual
studio。这个看个人喜好。![](https://image.3001.net/images/20201028/1603871678_5f9923be07782089713bd.jpg!small)

这段代码首先定义了一个copyself的函数，在copyself函数中首先定义了三个变量，其中前两个变量的数组长度为MAX_PATH，它是一个宏定义，大小为260。之后调用GetModuleFileName这个API函数，将当前运行程序的文件路径存入之前定义好的szSelfFileName变量，同理获得windows的路径。之后使用strcat函数将windows路径与“\\\backdoor.exe”拼接，之后使用CopyFile将自身复制到C:\windows\backdoor.exe。

运行效果：![](https://image.3001.net/images/20201028/1603871689_5f9923c982e3cdca85bfb.jpg!small)

查看运行前后的C盘windows内容：

![](https://image.3001.net/images/20201028/1603871701_5f9923d5a10d5644ba9c0.jpg!small)

![](https://image.3001.net/images/20201028/1603871713_5f9923e18b1f93d2ae3f3.jpg!small)

运行后发现多了一个backdoor.exe。

# 二、逆向分析复制自身的程序

使用ida打开，发现会弹出该对话框：![](https://image.3001.net/images/20201028/1603871723_5f9923ebd775102669c5e.jpg!small)

这是pdb调试文件，这是开发的时候发布的为debug版。如果修改为release版就没有pdb文件了：

![](https://image.3001.net/images/20201028/1603871732_5f9923f4a6161f702cfdb.jpg!small)

这个pdb文件通常有时可以作为一个特征来筛选一个恶意软件，有时还会被设置IOC情报。所以有时需要关注pdb的相关信息。

main函数：![](https://image.3001.net/images/20201028/1603871746_5f99240213502734e0c7c.jpg!small)

双击进入第一个call，这个call对应的就是copyself函数：

由于汇编语言太长，这里用VC6.0调试界面来展示：![](https://image.3001.net/images/20201028/1603871755_5f99240bf18d151fc3ce4.jpg!small)

直接看0040103E处开始的汇编语言，乍一看很复杂，看不懂。其中rep stos指令是repeat和store
string的缩写，它循环执行stos指令，循环次数由ecx控制。stos的作用是将eax中的值复制到es:edi指向的地址。再看0040103E处的汇编语言就清晰易懂了，先给ebp-104h赋值0，给ecx赋值40h（十进制的64），然后eax清零，之后edi设置为ebp-103h，使用rep
stos指令循环64次将eax赋值给edi指向的地址，由于是以dword进行循环，所以一共64*4=256个字节，再加上0040103E处的1个字节，加上0040105和00401056处，1+256+2+1=260个字节，刚好等于MAX_PATH。

之后查看GetModuleFileName对应的汇编语言：

![](https://image.3001.net/images/20201028/1603871765_5f992415558ebbe33c574.png!small)

三个参数从右往左，第一个参数104h为十进制的260，第二个参数eax为初始化的变量ebp-104h，对应的是szSelfFileName，第三个参数为0，之后调用GetModuleFileName
API函数。

![](https://image.3001.net/images/20201028/1603871783_5f992427201b98c519ea5.png!small)![](https://image.3001.net/images/20201028/1603871799_5f9924377ebd7c39aa25c.jpg!small)

使用VC6.0和使用ida的结果进行对比，虽然看起来不是很一样，但本质都是一样的。同理接下来调用GetWindowsDirectory，strcat和CopyFileA。对应的汇编基本上都相对容易看懂，此处就不再过多赘述了。之后就是if和else为一个分支判断：

![](https://image.3001.net/images/20201028/1603871812_5f99244419d911a345de6.png!small)

最终结束运行。

# 三、开发木马下载器

C语言代码如下：

![](https://image.3001.net/images/20201028/1603871824_5f9924509f3adfe176bf9.jpg!small)

由于URLDownloadToFile需要Urlmon.lib，所以需要使用#pragma comment
(lib,"urlmon")。URLDownloadToFile关键参数有两个，一个是要访问的URL，一个是要保存的文件路径。之后使用winexec函数运行下载后的程序，代码的实现很简单，主要就是两个api的调用。

使用另外一个机子，作为服务器，它的IP也就是URLDownloadToFile中的URL，我们将第一步开发的程序改名为test2.jpg，上传到该服务器上，然后使用如下命令开启web服务：

![](https://image.3001.net/images/20201028/1603871834_5f99245a85df718f1c67d.png!small)

然后执行编译后的程序：

![](https://image.3001.net/images/20201028/1603871896_5f9924987cd49857a0a1a.jpg!small)

![](https://image.3001.net/images/20201028/1603871911_5f9924a711f8f1ce89040.jpg!small)

下载成功，并且会将其复制到c盘windows目录下。这里需要注意的是，需要先删除第一步复制自身到windows目录的程序执行后生成的backdoor.exe，否则会报错，错误码为80，使用VC6.0的工具查询：

![](https://image.3001.net/images/20201028/1603871926_5f9924b64458774a83be3.jpg!small)

# 四、逆向分析木马下载器

![](https://image.3001.net/images/20201028/1603871937_5f9924c1dd0cd874c769f.png!small)

与之前类似，使用rep movs指令对一个数组循环赋值：之所以将ecx赋值为7，是因为我这里整个URL为28个字符。然后对剩余的全部赋值为0。

再调用URLDownloadToFile，然后使用cmp对比返回结果与800C0008h：

![](https://image.3001.net/images/20201028/1603871959_5f9924d7d9ea469e16cb1.png!small)

那么为什么要与800C0008h这个常量对比呢？按照我们开发时是INET_E_DOWNLOAD_FAILURE，当URLDownloadToFile返回结果为它时表示下载失败：

![](https://image.3001.net/images/20201028/1603871978_5f9924ea2bb3e6509f42e.jpg!small)

使用ida可以将其转换回来，操作步骤如下：选中这个常量，然后右键：

![](https://image.3001.net/images/20201028/1603871988_5f9924f420af39bf563ea.jpg!small)

然后便弹出这个：

![](https://image.3001.net/images/20201028/1603872018_5f992512cbf80b75140da.png!small)

选中合适的符号命名常量，然后点击OK即可：

![](https://image.3001.net/images/20201028/1603872029_5f99251d72330647a2923.jpg!small)

然后执行WinExec：

![](https://image.3001.net/images/20201028/1603872044_5f99252cec4b14d4a4d94.png!small)

其中push 5为WinExec的第二个参数，使用同样的方法将其转换为常量：

![](https://image.3001.net/images/20201028/1603872054_5f99253692de7b498b520.jpg!small)

转换后为SW_SHOW，与我们开发的一样。

# 五、总结：

这次实现了木马下载器，思路和实现很简单，主要就是调用URLDownloadToFile和WinExec函数。被下载的木马主要是调用了GetModuleFileName和CopyFile等函数将自身复制到windows目录。目前市面上的杀软应该都会对URLDownloadToFile这些敏感的函数进行查杀，所以本次案例仅供学习逆向分析使用。

#  **六、相关实验**

IDA逆向分析实例

[实验:IDA逆向分析实例(合天网安实验室)](https://sourl.cn/PFSmHB)

![](https://image.3001.net/images/20201028/1603872065_5f9925412d1ba7ba89e4c.jpg!small)

本实验首先通过一个简单的破解实验和大家一起熟悉逆向工具的使用，接着借助一道0Ctf中的逆向题目和大家一起对一个二进制程序进行逆向分析

