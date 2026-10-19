内网渗透一直以来都是一个热门话题，试想在一个大型的内网环境下，当我们拿到了内网windows机器后，我们该如何通过他们去获取更多的所需资源，这就需要我们进行内网渗透了。然而在内网渗透中，除了kali、metasploit等高能的存在以外，还有一款神器也常常容易遭到忽略
----PowerShell，因此本次学习将从PowerShell基础语法切入以及利用PowerShell脚本实现的PowerSploit框架演示内网渗透实例s。  

 **0x01 PowerShell简介及特性**

Windows Powershell是一种命令行外壳程序和脚本环境，使命令行用户和脚本编写者可以利用.NET
Framework的强大功能（因此也支持.NET对象）。

Windows Powershell具备以下特性：

操作便捷----可识别单位（如GB、MB、KB等）Cmdlet命令结构简单（动名词形式）

面向对象----同面向过程相比，更容易描述现实事物

结合.NET Framework环境----借助.NET Framework平台的强大的库

兼容性强----完全兼容windows平台上其他调用，如exe文件执行、bat脚本执行等

基于平台的可扩展性----powershell俨然已形成一个平台，并且向各类平台管理提供对应管理组件

接下来开始简单过一下基础语法（推荐学习网站<https://www.pstips.net/>）

  

 **0x02 PowerShell基础语法**

 **0x00交互式**

a) 命令：cmdlet命令—动词+名词（通过get-command –commandtype cmdlet可查看）

![查看.png](https://image.3001.net/images/20180514/15262810793991.png!small)

b) 别名机制：如常见的powershell命令----Get-ChildItem，windows的CMD命令----dir和linux的shell命令
----ls，他们的功能都是列出当前文件或目录的命令，三个不同平台的命令，在powershell中均可使用，即别名机制。同样地，别名机制也适用于函数。（可通过Get-Alias –name 命令名）

![命令名.png](https://image.3001.net/images/20180514/1526281114619.png!small)

c) 惯用帮助文档：通过Get-Help（别名：Help）-Name 命令名，如查询IEX的使用方法。

![方法.png](https://image.3001.net/images/20180514/15262811667916.png!small)

  

 **0x01变量**

a) 定义变量：Powershell不需要声明变量，可自动创建变量，变量值可以是字符也可以是命令，但是变量名前必须有$

![s  1.png](https://image.3001.net/images/20180514/15262812326167.png!small)

![s  2.png](https://image.3001.net/images/20180514/15262812489586.png!small)

  

注意：输出多个变量时需要使用双引号，单引号是不会取变量中的值的。

也可使用New-Variable定义变量，此时可以指定变量的一些属性，如访问权限：

以下给num变量添加只读属性。

![shuxing.png](https://image.3001.net/images/20180514/15262812853850.png!small)

  

 **0x01数组**

a) 创建数组：常规数组可以使用逗号，连续数字数组可以使用。

![使用.png](https://image.3001.net/images/20180514/15262813402222.png!small)

  

其中有以下两个特例：

空数组：

![空数.png](https://image.3001.net/images/20180514/15262814401742.png!small)

一个元素数组：

![元素.png](https://image.3001.net/images/20180514/15262814716000.png!small)

b) 数组的操作：数组访问同python类似，从0开始；数组的判断：$str –is [array]；数组的追加：$books +=”需要添加的值”

![值.png](https://image.3001.net/images/20180514/15262815246672.png!small)

c) 哈希表的使用：之前创建空数组是使用@()，而创建哈希表用到的是@{}，此处的哈希表同python中的字典类型类似：

![类似.png](https://image.3001.net/images/20180514/15262815836086.png!small)

**0x02管道**

a) Powershell管道：传统的CMD管道是基于文本，而powershell管道则是基于对象：

![对象.png](https://image.3001.net/images/20180514/15262817901013.png!small)

 **0x03 对象（对象=属性+方法）**

a) 创建对象：

![创建.png](https://image.3001.net/images/20180514/15262822256678.png!small)

b) 增加属性（直接添加、通过管道添加）：

![属性.png](https://image.3001.net/images/20180514/15262823656295.png!small)

c) 增加方法（直接添加、通过管道添加）：

![方法 1.png](https://image.3001.net/images/20180514/15262825239215.png!small)

![方法 2.png](https://image.3001.net/images/20180514/15262825433149.png!small)

  

 **0x04 条件判断以及循环**

a) 比较运算符：

-eq：等于

-ne：不等于

-gt：大于

-ge：大于等于

-lt：小于

-le：小于等于

-contains：包含

-notcontains：不包含

![包含.png](https://image.3001.net/images/20180514/15262826604934.png!small)

布尔运算：

-and：和

-or：或

-xor：异或

-not：逆

![逆.png](https://image.3001.net/images/20180514/15262828534421.png!small)

  

b) If-elseif-else：

![else.png](https://image.3001.net/images/20180514/15262830523679.png!small)

c) Switch：

![switich.png](https://image.3001.net/images/20180514/15262838977954.png!small)

d) Foreach：

![ch.png](https://image.3001.net/images/20180514/15262839339679.png!small)

e) While:

![while.png](https://image.3001.net/images/20180514/15262840303975.png!small)

  

f) For:

![for.png](https://image.3001.net/images/20180514/15262840549843.png!small)

  

 **0x05函数**

a) 函数是自定义的powershell代码，有三个原则：

简短：函数名简短，并且显而易见

聚合：函数可以完成多个操作

封装和扩展：将一批powershell语句进行封装，实现全新的功能需求

函数结构：函数名，参数，函数体：

Function FuncName （args[]）

{

code;

}

如:

![ps.png](https://image.3001.net/images/20180514/15262845838994.png!small)

 **0x06脚本**

a) 创建脚本（以.ps1为后缀）

通过重定向创建脚本：

![脚本.png](https://image.3001.net/images/20180514/15262849798325.png!small)

通过编辑器创建脚本：

通过txt来编写

![txt.png](https://image.3001.net/images/20180514/15262850367436.png!small)

通过powershell自带的ISE或者其他编写工具：

![gongju.png](https://image.3001.net/images/20180514/15262870776882.png!small)  

b) 脚本执行策略：并不是每个.ps1后缀的powershell脚本都可以被执行，在powershell中有策略进行严格把控：

Unrestricted: 权限最高，可以不受限制执行任何脚本。

Restricted: 为Powershell默认的策略，不允许任何脚本执行。

AllSigned：所有脚本都必须经过签名才能在运行。

RemoteSigned：本地脚本无限制，但是对来自网络的脚本必须经过签名。

若需要修改脚本执行策略，只有在管理员权限下才可进行更改，否则会报错：

![baocuo.png](https://image.3001.net/images/20180514/15262871634620.png!small)

  

若想在默认策略下执行脚本，可以通过以下两种方法进行绕过：

本地权限绕过执行

![执行.png](https://image.3001.net/images/20180514/15262872049403.png!small)

  

IEX下载远程PS1脚本权限绕过执行（后续Powersploit框架中会用到）：

![用到.png](https://image.3001.net/images/20180514/15262872524248.png!small)

  

 **0x03 Powershell值得学习的理由**

众所周知，Linux的shell相比windows的cmd好用程度不止一点，无论是命令、正则表达式还是管道都挺人性化，不仅可以完成复杂的问题，而且效率还很高。对此，微软平台也发布了“cmd升级版”----windows
powershell。

Windows Powershell为什么强大好用，通过以下几个例子：

轻松比较GB、MB、KB

![KB.png](https://image.3001.net/images/20180514/15262873408733.png!small)

通过命令直接算出距离明年的今天有多少天

![天 天 天.png](https://image.3001.net/images/20180514/15262876667839.png!small)  

通过命令获取当前PC中跑了多少进程

![进程.png](https://image.3001.net/images/20180514/15262875685068.png!small)

查看Windows目录下所有文本文件txt的大小

![大小.png](https://image.3001.net/images/20180514/15262875879787.png!small)

可将数据输出为HTML格式、CSV格式等

![格式
1.png](https://image.3001.net/images/20180514/15262876171451.png!small)![格式
2.png](https://image.3001.net/images/20180514/15262876326275.png!small)

打开文件：

![文件.png](https://image.3001.net/images/20180514/15262877312525.png!small)

  

相比之下，原先的cmd并未有如此便捷的功能命令，在以上powershell不仅可以利用管道，正则表达式。它不仅是一个强大的shell，同时是内网渗透的利器，后续会继续推出Powersploit框架介绍，介绍Powersploit框架并实现简单的内网渗透实例。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180514/15262877656314.jpg!small)

