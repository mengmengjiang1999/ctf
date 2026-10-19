# Yara入门——如何通过Yara规则匹配CobaltStrike恶意样本

阅读量 **609871**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-24 14:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01e63e7dfe76d664b0.jpg)

## 0x00 前言

首先，YARA规则是VT的开发人员发布的，用于同类样本的批量检索和查杀。

通过Yara引擎和我们编写的Yara规则，可以快速对一批样本进行扫描和识别，从而找到我们希望得到的样本。

官方的github库地址：<https://github.com/VirusTotal/yara/releases>

官方文档说明：<https://yara.readthedocs.io/en/v3.7.0/index.html>

## 0x01 Yara的安装和使用

###  如何安装Yara

Yara的安装非常简单，在Windows操作系统下，我们可以直接在yara的github库下载可执行文件到本地，配置环境变量即可用

可以看到，当前（2020-07-20）的最新版本是Yara4.0.2

![](https://p0.ssl.qhimg.com/t01920433f0006e255b.png)

这里下载yara-v3.11.0-994-win64.zip，下载到本地之后直接将压缩包中了两个exe解压并到C:\Windows目录下并分别重命名为yarac.exe和yara.exe

![](https://p4.ssl.qhimg.com/t0158bbe497a8a43b2c.png)

然后启动cmd 直接输入yara —help 即可查看yara的参数

![](https://p1.ssl.qhimg.com/t010f13d1f3603ee2aa.png)

在Mac下，可以直接使用pip工具或者brew直接安装。

我是通过brew install yara的方式直接安装的。安装完成之后，使用方式也是一样的。

![](https://p2.ssl.qhimg.com/t013981b3090d6b777b.png)

###  Yara食用

现在，以官方提供的yara规则示例我们来看看yara可以做什么。  
官方给出的示例yara如下：

    
    
    rule silent_banker : banker
    {
        meta:
            description = "This is just an example"
            thread_level = 3
            in_the_wild = true
        strings:
            $a = {6A 40 68 00 30 00 00 6A 14 8D 91}
            $b = {8D 4D B0 2B C1 83 C0 27 99 6A 4E 59 F7 F9}
            $c = "UVODFRYSIHLNWPEJXQZAKCBGMT"
        condition:
            $a or $b or $c
    }
    

首先，第一行的rule silent_banker : banker是声明该规则用于检出banker类型的样本。

meta 后面的是一些描述信息，比如规则说明、作者信息等。

strings 定义了$a $b $c 两个十六进制字符串（十六进制字符串用大括号括起来）和一个文本字符串（文本字符串直接用双引号括起来）

最后condition 规定了匹配的条件，这里写的是or，表明样本中只要匹配到了$a $b $c 三个字符串中的任意一个，那么样本就会被识别为banker

我们新建一个demo1.yara文件，然后将这部分内容复制进去。

![](https://p1.ssl.qhimg.com/t0145168b53d4caa732.png)

然后在当前目录下新建一个文件夹<111> 在该文件夹中分别存放三个文件，一个py文件，一个json文件和一个exe文件。

![](https://p3.ssl.qhimg.com/t01603ba1e65c548a46.png)

现在我们回到demo1.yara所在的目录，执行yara demo1.yara 111/

![](https://p5.ssl.qhimg.com/t0156211d38a73e343a.png)

执行完之后，没有任何输出，根据Unix内核的无回显则运行成功原则，我们可以知道该指令已经成功执行。

而没有输出是因为我们的yara规则没有命中111文件夹下的任何文件。于是我们修改规则如下：

![](https://p0.ssl.qhimg.com/t011486187e673a9108.png)

我们增加了一个十六进制字符串$d 所匹配的值是4D 5A。 而4D
5A是PE文件（包括exe、dll等）的文件头，也就是说一个正常的PE文件中是一定会包含4D 5A这个十六进制的数据的。

且我们在最后的condition中加入了or $d，表示如果$d条件满足，样本也可以成功识别。

demo1.yara保存之后我们重新对111文件夹下的文件进行扫描：

![](https://p3.ssl.qhimg.com/t010869fc269576c5f4.png)

这里可以看到，yara规则已经成功识别到了111/svchost.exe文件命中了我们的yara特征，并且提扫描之后自动标记为silent_banker，这个silent_banker就是我们在最上面定义的检出名称。

现在我们将更多的PE文件拷贝到111文件夹下以及111文件夹下的子目录中。

![](https://p4.ssl.qhimg.com/t01875ee64197e9992c.png)

然后再次对111文件夹进行扫描

![](https://p3.ssl.qhimg.com/t01d7c33ab178346a11.png)

这里可以看到还是只有一条结果，于是我们通过yara —hlep查看一些帮助文档：

    
    
      -t,  --tag=TAG                   print only rules tagged as TAG
      -i,  --identifier=IDENTIFIER     print only rules named IDENTIFIER
      -n,  --negate                    print only not satisfied rules (negate)
      -D,  --print-module-data         print module data
      -g,  --print-tags                print tags
      -m,  --print-meta                print metadata
      -s,  --print-strings             print matching strings
      -L,  --print-string-length       print length of matched strings
      -e,  --print-namespace           print rules' namespace
      -p,  --threads=NUMBER            use the specified NUMBER of threads to scan a directory
      -l,  --max-rules=NUMBER          abort scanning after matching a NUMBER of rules
      -d VAR=VALUE                     define external variable
      -x MODULE=FILE                   pass FILE's content as extra data to MODULE
      -a,  --timeout=SECONDS           abort scanning after the given number of SECONDS
      -k,  --stack-size=SLOTS          set maximum stack size (default=16384)
      -r,  --recursive                 recursively search directories
      -f,  --fast-scan                 fast matching mode
      -w,  --no-warnings               disable warnings
           --fail-on-warnings          fail on warnings
      -v,  --version                   show version information
      -h,  --help                      show this help and exit
    

这些参数很重要，我们可以翻译了之后多看，多用

    
    
    -t、 --tag=tag只打印标记为tag的规则
    -i、 --identifier=identifier只打印名为identifier的规则
    -n、 --negate只打印不满足的规则（negate）
    -D、 --打印模块数据打印模块数据
    -g、 --打印标签打印标签
    -m、 --打印元数据
    -s、 --打印字符串打印匹配的字符串
    -L、 --打印字符串长度打印匹配字符串的长度
    -e、 --打印命名空间打印规则的命名空间
    -p、 --threads=NUMBER使用指定的线程数扫描目录
    -l、 --max rules=NUMBER匹配多个规则后中止扫描
    -d VAR=值定义外部变量
    -x MODULE=文件将文件内容作为额外数据传递到模块
    -a、 --timeout=秒在给定秒数后中止扫描
    -k、 --堆栈大小=插槽设置的最大堆栈大小（默认值=16384）
    -r、 --递归递归搜索目录
    -f、 ——快速扫描快速匹配模式
    -w、 --无警告禁用警告
             --警告失败警告失败
    -v、 --版本显示版本信息
    -h、 --help显示此帮助并退出
    

这里可以看到 -r recursively search directories  
表示递归遍历所有子目录。  
于是我们重新运行，带上-r 参数：yara -r demo1.yara 111/

![](https://p1.ssl.qhimg.com/t0109d57cddc50a74ea.png)

这样就可以对指定目录进行递归扫描了。

我们还可以集合-r和-m参数，在扫描时输出详细信息：

![](https://p2.ssl.qhimg.com/t01d1414361e18a160c.png)

通过上面的例子，我们对Yara有了一个大概的了解，接下来我们来看一下Yara的一些更方便的特性。  
我们上面提到，Yara可以匹配文本字符串、十六进制字符串。其实除了这两种，Yara还支持正则表达式的写法。

在上面，我们已经测试了十六进制字符串的匹配。匹配的方式是扫描文件是否包含了4D
5A。这里都不能算是一条规则，因为这条规则没有意义。其实十六进制还包含了很多高级的写法，包括通配符、可变长度等。这里空讲无用，之后遇到比较好的样本再做分享。

我们来测试一下字符串的写法，我们新建一个demo2.yara，内容如下：

![](https://p0.ssl.qhimg.com/t018f90cd8cba700d24.png)

这条yara的规则很简单，就是扫描的文件中是否包含了if **name** == ‘ **main**
‘:这个字符串，如果有，则将其标记为python_file

然后还是对111目录进行扫描：

![](https://p5.ssl.qhimg.com/t013f6033d0966dd90b.png)

可以看到成功扫描到python文件。这里需要注意，我们在yara中直接写字符串的话，是区分大小写的，如果想要扫描时不区分大小写，可以加入nocase关键字，比如：

![](https://p2.ssl.qhimg.com/t010861b7c9438e9d5a.png)

接下来我们看看yara中的正则是如何写的。  
Yara的正则其实和字符串写法很类似，并且可以用在字符串上的特性都可以用在正则表达式中。

以匹配身份证号为例，我就直接以一个非常简单粗暴的方式来匹配身份证，就是直接查看文件中是否包含了18位连续的数字（我这种匹配当然不标准，只是为了方便测试）。  
此外，我还加上了一个$peflag的标志条件，在condition的地方通过 and not 的方式过滤掉所有的PE文件。  
demo3.yara如下：

![](https://p1.ssl.qhimg.com/t0182b66aed89f95981.png)

扫描结果如下：

![](https://p5.ssl.qhimg.com/t017ac33ec453af1c17.png)

这里出现了一个warning：demo3.yara(11): warning: $reg1 is slowing down scanning
(critical!)

提示demo3.yara规则中的$reg1这个匹配条件写的不好，会引起yara的性能下降。  
这是因为我们直接使用正则表达式瞎匹配，这样肯定是不对的，因为如果扫描一个1M或是2M的脚本文件，这个yara规则一跑，基本上就会卡死。所以在书写yara规则的时候，在可达成目的的情况下，也要考虑扫描的性能。关于yara的优化，我们在后面的实战样本中会提到。

## 0x02 CobaltStrike安装和使用

###  CobaltStrike安装

CobaltStrike的安装非常简单，只需要在本机装好JAVA环境，然后分别运行CobaltStrike的客户端和服务器端即可。  
以3.14为例，3.14版本的CobaltStrike解压后文件结构如下：

![](https://p0.ssl.qhimg.com/t01782ff96f8e9c9a5b.png)

其中的teamserver就是CobaltStrike的服务器端，CobaltStrike文件就是客户端。

只需要  
./teamserver 服务器ip地址 cs密码  
即可成功启动CobaltStrike的服务器。  
然后在客户端使用./cobaltstrike 然后填写服务器的ip地址和密码即可（端口一般不变）成功登录。

4.0的结构稍微有所不同

![](https://p0.ssl.qhimg.com/t018934522a05e3f333.png)

在4.0中不再有CobaltStrike客户端文件，取而代之的是CobaltStrike.bat文件  
所以我们首先启动CobaltStrike服务器，这里的ip地址就是本机的ip地址，后面的123456是登录密码

![](https://p4.ssl.qhimg.com/t01cd58edbf0bd0c699.png)

服务器成功启动之后，我们启动客户端：

![](https://p3.ssl.qhimg.com/t017f7fb7f69cd76e71.png)

成功登录上cs客户端：

![](https://p3.ssl.qhimg.com/t01ae1ea45a4418cbc4.png)

大概介绍一下CobaltStrike各个菜单的的功能：

![](https://p1.ssl.qhimg.com/t01c31b07669bedb519.png)

![](https://p2.ssl.qhimg.com/t01e15000c89e8a62be.png)

CobaltStrike的监听器主要分为beacon和foreign，其中bacon是CobaltStrike内置的，我们使用CobaltStrike生成的payload反弹shell回来直接就可以用  
foreign是外置的，比如想通过CobaltStrike反弹到msf，就可以使用foreign

![](https://p3.ssl.qhimg.com/t0193d23db907329f02.png)

###  CobaltStrike生成马

我们可以通过上面介绍的图标快捷菜单生成木马，也可以通过Attacks菜单栏生成我们想要的木马。

![](https://p3.ssl.qhimg.com/t01416f97cfc248c3fb.png)

我这里分别生成了beacon、foreign、HTML、powershell、VBS、office宏等cs马。接下里先分析分析这些木马尝试提取CobaltStrike特征，生成马如下（3.14）：

![](https://p2.ssl.qhimg.com/t01866363dc446dc4d9.png)

## 0x03 CobaltStrike样本查杀

###  Win32_PE

我们首先来看看32位的PE文件，包括exe和dll。  
为了防止样本在Windows操作系统下被误执行，我这里给所有逇样本都加上了.bin后缀，然后统计这些文件的时候可以发现，通常情况下CobaltStrike默认生成的beacon的PE马大小都在278kb到303kb的样子。红框部分的foreign马的大小却只有十多kb。

![](https://p0.ssl.qhimg.com/t019975e2da2b8c47f6.png)

所以我们可以尝试编写第一个filter来过滤掉其他的样本。

为什么要编写filter呢，因为比如我们扫描Windows的系统目录或是一个程序目录，该目录下有上千，上万甚至上十万的文件，如果我们不写filter，那么Yara在扫描的时候将会每个文件都完整的去匹配我们写的规则，在上面的时候我们提到，yara规则是会全文扫描的，那么这样将会大大降低扫描效率，如果我们能够写一些filter过滤掉大部分的不相关样本，那么yara在扫描的时候将会只对疑似的文件进行有效的扫描而不会浪费资源。

Yara提供了文件大小的变量，标准写法为

rule FileSizeExample  
{  
condition:  
filesize > 200KB  
}

第一个条件写好之后，可以看到基本上就筛选了刚才我们看到的PE我文件，但是多了一个beacon3.ps1，没关系，我们在后面的规则中过滤掉。

![](https://p4.ssl.qhimg.com/t01ca02a177522bf358.png)

现在我们随便加载两个exe到IDA中分析。

![](https://p2.ssl.qhimg.com/t01806deb89d65e60a6.png)

IDA加载之后，一对比发现两个马的入口点是几乎完全一样的，唯一细微的区别就是这里mov语句的参数2不同。

空格转换为汇编代码显示，可以看到样本此时默认是main函数。这里目前至少是说明CobaltStrike的两个beacon马的main函数入口点结构相同。

![](https://p4.ssl.qhimg.com/t01f1fc033f91544294.png)

Ctrl + E ，然后跳转到start函数，看看两个样本的入口点是否相同：

![](https://p3.ssl.qhimg.com/t018d5ed6a99936061a.png)

来到start函数之后，我们可以发现两个CobaltStrike样本的入口点是完全一致的，程序入口点都是004014B0

减去基地址00400000，那么入口点应该就是偏移14B0的位置。

![](https://p3.ssl.qhimg.com/t018318dd62163631df.png)

我们再加载一个beacon的样本，看看入口点是否还是一致，这里发现三个样本的入口点都是14b0的地方，所以我们推测CobaltStrike的样本入口点都在14b0的地方，所以我们编写第二个规则去验证一下。

![](https://p2.ssl.qhimg.com/t01ef978275e8c5668c.png)

在yara3.0以下的版本中，可以直接使用entry_point变量获取入口点，在3.0以上的版本中，该变量已经被弃用。取而代之的是一个pe模块。现在可以使用pe.entry_point来获取入口点，但是需要注意的是，这里是获取到的文件偏移，也就是offset，并不是我们在IDA中看到的entry_point，这里需要注意一下。  
程序的Offset是0x8b0：

![](https://p4.ssl.qhimg.com/t011b17023c3a221f08.png)

所以我们可以将条件写成如下形式：

![](https://p4.ssl.qhimg.com/t0145a3a1b6d01c4db2.png)

官方文档给的写法是用关键字at：

但是需要注意，使用at是取值，并不是匹配地址。  
也就是说上图这种写法是去找一下$a变量的值是否在entrypoint这个地址能找到。  
也就是在我们这条规则中，如果要用at，可以写成如下：

![](https://p0.ssl.qhimg.com/t010941b6ec293618e0.png)

这里的$name中的十六进制值需要大写，匹配的值就是IDA入口点的十六进制数据：

![](https://p3.ssl.qhimg.com/t0103da18afc084f80f.png)

但是我们同时也可以看到，at的写法没有那么有通用性，我们还是使用上面 == 的写法。

那么现在第二条规则就已经写好了，我们继续来看其他的内容。  
我们静态分别看下这个样本的main函数：

![](https://p1.ssl.qhimg.com/t011dff671680093836.png)

在Main函数中可以看到，关键就调用了两个call，分别是4027b0和401800

我们大概看一下就可以知道sub_401800才是关键函数，在sub_401800函数中，程序会通过CreateThread创建一个新线程，并且可以看到有一个奇怪的%c%c%c%c%c%c%c%c%cMSSE-%d-server看起来像是通信协议。

![](https://p4.ssl.qhimg.com/t01ed2f29add6fcb622.png)

这里CreateThread的lpStartAddress是sub_4016D3,在sub_4016D3的sub_401608函数中可以看到正在通过CreateNamedPipeA的方式创建管道准备通信。

![](https://p2.ssl.qhimg.com/t0109c0cdf1cc6b1fee.png)

我们调试器里直接过来可以看到跟我们想的应该一样，这里的确是跟通信相关的内容。

![](https://p2.ssl.qhimg.com/t016231e9e361fb318f.png)

查看多个样本，可以发现%c%c%c%c%c%c%c%c%cMSSE-%d-server 这个值是固定的。  
所以可以直接尝试匹配这个串试试：

![](https://p4.ssl.qhimg.com/t014d89059f9228eb26.png)

可以看到再次成功匹配。到这里，我们关于CobaltStrike的Beacon木马的yara规则基本上就提取完成了。  
最后，我们给规则加上一个PE的判断条件：

![](https://p1.ssl.qhimg.com/t01146c7b02340a3673.png)

现在这个条件就比较完整了。

  1. 通过uint16(0) 的方式取文件的前两个字节，判断是否等于0x5A4D 如果等于则说明是PE，这里用于过滤PE文件
  2. 判断程序的pe.entry_point是否等于0x8B0，这里是文件的file offset，这里也算是一个很好的过滤条件，可以直接过滤掉大部分的文件。
  3. 通过两个filesize的比较限制文件的大小
  4. 最后用一个关键的字符串来做最终的验证。

这里是看到这个串的确是CobaltStrike使用来通信的，且一批CobaltStrike的马都包含了这个串，相对来说，应该不会命中到其他的正常文件，这个通信协议应该是cs专用的，所以可以直接这样写，如果不想误报，想要提高检测的精准性，可以继续找其他的特征提取。  
反正在写yara规则的时候，通用性和精准性，是分析人员需要权衡的条件，如果我们想要提高特征的通用性，势必就需要减少一些匹配条件，精准性就会下降，至于到底是通用性优先还是精准性优先就得看具体的应用场景。

###  powershell马特征

处理了CobaltStrike的PE马，我们再来看看其他类型的木马规则如何提取。  
首先是powershell木马，也就是ps1的文件。  
我这里只生成了两个。  

分别查看一下文件内容。  
32位：

![](https://p1.ssl.qhimg.com/t014d83557a9ccd54f3.png)

64位：

![](https://p3.ssl.qhimg.com/t0173f60d4b66f56cca.png)

这里可以看到，32位和64位的powershell马结构其实是一样的，只是32位的马使用了$DoIt=
@’’的方式来定义两个函数，其实和64位这里是一样的。

这里很明显，程序最后关键执行的数据在24行开始的地方，这里定义了超级大的base64串。经过观察可以发现32为和64执行的串的头部是不一样的：  
32位：

![](https://p1.ssl.qhimg.com/t0197baf1e2dbf0961b.png)

64位：

![](https://p0.ssl.qhimg.com/t01a7a0568fdc0ad180.png)

经过分析我们可以发现，代码的最下面，上面定义的这个$var_code的执行语句，且两个版本的ps马都是这样写的，于是我们直接尝试用字符串匹配这一段试试。

![](https://p0.ssl.qhimg.com/t01d86a741449c50695.png)

就直接在原有yara的基础上增加一个rule即可：

![](https://p1.ssl.qhimg.com/t01664b04db88592646.png)

然后命令行测试，可以看到两个ps1脚本都被成功匹配

![](https://p4.ssl.qhimg.com/t01938eb8b8d40000ad.png)

###  html_pe马特征

CobaltStrike的html木马分为了三种，分别是包含PE文件的hta 包含VBS的hta 包含powers的Hta，我们分别来看看。

首先是包含PE的hta：  
该类别的cs马会直接将一个PE文件的十六进制数据流硬编码到文件中：

![](https://p2.ssl.qhimg.com/t01d62d81cd7669a453.png)

在马最下面，程序会定义一个var_tempexe文件用于接受上面的数据流，将该文件写入到本地并且通过run执行之后删除该文件。这里其实写入的文件应该也是beacon的木马，在14行代码的位置，有着var_tempexe变量的赋值语句，经过与多个样本的对比分析发现，后面的beacon_evil.exe不是固定的，而是攻击者在使用CobaltStrike生成木马的时候给定的文件名。所以我们可以考虑用正则来匹配这一段，作为条件之一。  

编写yara特征之后进行扫描，成功捕获对应的样本

![](https://p4.ssl.qhimg.com/t01a29b3e6689ce0f20.png)

完整的正则表达式如下：  
/var_tempexe = var_basedir & \”\\\” & \”[A-z]{1,20}.exe\”\s*Set var_stream =
var_obj.CreateTextFile(var_tempexe, true , false)/

我们来一点点拆解。  
首先，我们在yara中使用正则表达式要使用  
//  
标识，我们将正则写到两个斜杠之间。  
var_tempexe = var_basedir & 这段是我们直接从原始代码中复制出来的。  
\”\\\” 用于转义匹配中间的 “\”  
由于我们刚刚已经分析过，后面的beacon_evil.exe不是固定的，是又攻击者指定，所以我这里写了一个范围，1-20，然后通过\s*将后面的语句给组合起来进行匹配。

###  html_VBS特征

接下来我们看看html的VBS马，结构如下：

![](https://p2.ssl.qhimg.com/t01687ea3a0c8033aa5.png)

经过分析，我们可以看出来，下面的一大段代码，其实是带轻微混淆的VBA代码。  
混淆方法很简单，就是通过&符号拼接由chr函数转换的ascii  
“&Chr(61)

我们尽量找一个比较通用的地方来提取特征，稍微分析一下，可以发现，上面部分都是一些函数的导入，变量的定义，没有做神什么比较奇怪的操作，在57行的位置，定义了一个很大的数组，数组名为myAr&ray
后面的Chr(61)转换之后是等于符号 = 。 后面的一大段数据都是用于给myArray赋值的。所以我们可以考虑将特征提取到这里。

![](https://p4.ssl.qhimg.com/t01fe1b08d1cec7d378.png)

这里应该可以直接写字符串进行匹配了：

![](https://p4.ssl.qhimg.com/t01e5df62475477e92d.png)

###  html_powershell

最后，html类别的马就只剩下powershell类型的了，还是先来看看代码结构

![](https://p2.ssl.qhimg.com/t01d3281aa89610c5c4.png)

cs的powershell马结构相对来说就很简单了，就是通过powershell执行了超级长一段base64编码的脚本命令。  
直接取这个base64串的头部出来解码看看是是不是常见的语句  
JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8Acg

解码之后发现是$s=New-Object IO.Memor  
结合代码分析，这里是将后面的数据加载到内存中执行，这里是在做准备工作。

结合前面的powershell -nop -w hidden
-encodedcommand本身也不是常见的powershell语句，正经人谁会这样干，所以我们直接尝试提这里的字符串看能否通杀。  
貌似可以

![](https://p2.ssl.qhimg.com/t01c0c51fc46b1d0d58.png)

###  Macro

现在还有一类Macro样本，也就是Office宏代码。这个其实也是简单，但是这里我生成的时候偷了一个懒，没有按照cs的文档将宏代码存储到Office文档中。关于Office文档的查杀，在后面再结合oledump等工具继续介绍。

## 0x04 查杀效果

我们回到上级目录，看看同时查杀3.14和4.0的效果怎样  
我们将结果写入到1.txt中

![](https://p3.ssl.qhimg.com/t013e561c876a9998ff.png)

一共是查杀了24个样本

![](https://p4.ssl.qhimg.com/t016b06635e2212a8e5.png)

可以看到，一共27个文件，除了vba和这里的两个raw没写规则外，全部查杀了。所以，对CobaltStrike木马基本查杀的yara规则就这样写好了。后面我们学习了yara的高级写法或是遇到其他cs的样本可以再继续完善，但是目前这个yara应该可以识别绝大多数的正常cs马了。

![](https://p5.ssl.qhimg.com/t012f4d5aecb189fe24.png)

最后，CobaltStrike解压之后，目录中会有一个CobaltStrike.jar文件

![](https://p3.ssl.qhimg.com/t01bb5fb41c10660e3c.png)

使用解压缩工具将这个文件也解压：

![](https://p0.ssl.qhimg.com/t011889de6fa5550cad.png)

这里面有一个名为resources的文件夹，就是CobaltStrike的配置信息，我们在CobaltStrike控制台生成的木马都来源于这个文件夹。

![](https://p5.ssl.qhimg.com/t013078a2e4db506ff3.png)

![](https://p3.ssl.qhimg.com/t013cf6d4e144f4c135.png)

所以我们也可以直接分析这里面的样本，提取规则进行查杀。

## 0x05 完整yara

    
    
    import "pe"
    rule beacon32
    {
        meta:
            description = "This rule is used for discovery CobaltStrike’s beacon32PE Trojan"
            author = "int3"
            date = "2020-07-21"
            reference = "reference"
            hash = "hash"
        strings:
            $name = "%c%c%c%c%c%c%c%c%cMSSE-%d-server"
        condition:
            uint16(0) == 0x5A4D and pe.entry_point == 0x8b0 and filesize > 277KB and filesize < 304KB and $name
    }
    
    
    rule ps
    {
        meta:
            description = "This rule is used for discovery CobaltStrike’s powershell Trojan"
            author = "int3"
            date = "2020-07-21"
            reference = "reference"
            hash = "hash"
        strings:
            $str1 = "$var_va.Invoke([IntPtr]::Zero, $var_code.Length, 0x3000, 0x40)"
            $str2 = "[System.Runtime.InteropServices.Marshal]::Copy($var_code, 0, $var_buffer, $var_code.length)"
        condition:
           uint16(0) != 0x5A4D and $str1 and $str2
    }
    
    rule CobaltStrike_hta_pe
    {
        meta:
            description = "This rule is used for discovery CobaltStrike’s hta'pe Trojan"
            author = "int3"
            date = "2020-07-21"
            reference = "reference"
            hash = "hash"
        strings:
            $reg1 = /var_tempexe = var_basedir & \"\\\" & \"[A-z]{1,20}.exe\"\s*Set var_stream = var_obj.CreateTextFile\(var_tempexe, true , false\)/
        condition:
           uint16(0) != 0x5A4D and  $reg1
    }
    
    rule hta_VBS
    {
        meta:
            description = "This rule is used for discovery CobaltStrike’s hta'vbs Trojan"
            author = "int"
            date = "2020-07-21"
            reference = "reference"
            hash = "hash"
        strings:
            $str = "myAr\"&\"ray \"&Chr(61)&\" Array\"&Chr(40)&Chr(45)&\"4\"&Chr(44)&Chr(45)&\"24\"&Chr(44)&Chr(45)&\"119\"&Chr(44)"
        condition:
           uint16(0) != 0x5A4D and  $str
    }
    
    
    rule hta_ps1
    {
        meta:
            description = "This rule is used for discovery CobaltStrike’s hta'vbs Trojan"
            author = "int"
            date = "2020-07-21"
            reference = "reference"
            hash = "hash"
        strings:
            $str = "var_shell.run \"powershell -nop -w hidden -encodedcommand JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8A"
        condition:
           uint16(0) != 0x5A4D and  $str
    }
    

## 0x06 总结

本篇是YARA规则的入门篇，通过本节的内容我们可以发现，Yara在恶意样本检测中有着至关重要的作用（虽然本节中写的YARA很简单，但是Yara可以做的远远不止于此）。此外，我们还可以通过别人写好的yara，辅助我们分析恶意软件，阅读大佬写的Yara我们可以知道大佬在分析对应的样本的时候，关注点在哪里，他提取到了目标木马/家族的哪些特征等等。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jux1a** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/211501](/post/id/211501)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Yara](/tag/Yara)
  * [恶意样本](/tag/恶意样本)

 **+1** __11赞

 __收藏

![](https://p0.ssl.qhimg.com/t01c900f6a705a10464.png) jux1a

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

