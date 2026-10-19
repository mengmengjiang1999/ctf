hello 我是龙爷，今天我们要讲的是kali linux操作系统下的一些常见命令。

众所周知，kali linux自身的官方源是很慢的，所以在学习基础命令之前，我们要学习如何换掉kali linux的官方源。

## 换掉kali linux的官方源

首先我们需要知道源的位置，那么各位请记住，kali源的默认储存位置在 **/etc/apt/sources.list**
。在这个文件内我们可以删掉官方源将其他第三方提供的源安装上去。常见的第三方源有：中科大源，阿里源等等。

我没可以使用vim或者nano等编辑工具来编辑 **/etc/apt/sources.list。**
我个人并不是特别喜欢使用vim编译文本，需要了解vim使用方法的可以去其他freebuf博主那里学习。我这里使用nano去编译该文件。

![](https://image.3001.net/images/20210818/1629253192_611c6e4880d9581a904a9.png!small)如图，然后回车，删掉或者注释掉所有内容，然后将第三方源粘贴上去，如下图：

![](https://image.3001.net/images/20210818/1629253300_611c6eb4553dd72b73d25.png!small)这样，然后Ctrl
O保存，Ctrl X退出。再输入apt-get update跟apt-get upgrade更新一下。

我使用的源：

deb http://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib  
deb-src http://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib

更新完成后我们可以正式开始学习下面的命令了

## kali linux基础和常见命令--具体使用参数请用--help查看

### ifconfig命令：

ifconfig命令用于获取网卡配置与网络状态等信息，输出结果如图：

![](https://image.3001.net/images/20210818/1629253630_611c6ffeccbca0b33a691.png!small)

假如你插上了一个网卡，你可以使用 **ifconfig 网卡名 up** 来激活它

### who命令：

who用于查看当前登入主机的用户终端信息，输出i结果如图：

###
![](https://image.3001.net/images/20210818/1629253847_611c70d7c1f1da707201c.png!small)history命令：

查看你以前用过哪些命令，输出结果如图：

###
![](https://image.3001.net/images/20210818/1629254011_611c717b42c6f73ac85da.png!small)cd命令：

cd命令用于切换工作路径，比如进入某个路径，返回上个路径

进入某个路径 **cd 路径**

返回上个路径 **cd ..**

### pwd 命令：

pwd命令可以显示用户当前所处的工作目录，输出结果如图：

![](https://image.3001.net/images/20210818/1629254450_611c7332a6aa503a70d45.png!small)

### ls命令：

ls命令可以用来查看当前工作路径下所有非隐藏的文件，类似/root/.wine这种文件是无法用无参数的ls看见的

 **cat命令：**  
cat命令用于查看纯文本文件（所含内容略少的，比如几十b的小文件，或者说arping扫描输出的存活主机结果啊等等），输出结果如图：

###
![](https://image.3001.net/images/20210818/1629255091_611c75b3535c48e26a11b.png!small)more命令：

more命令可以用来查看内容更多的文本文件，跟cat差不多，这里面不多做演示

### stat命令：

stat命令可以用来查看文件的具体存储信息和时间等信息，这个我也就不做演示了

### touch名令：

touch命令用于创建空白文件或设置文件的时间，想要具体了解可以使用-h参数查看具体使用方法

### cp命令：

cp命令可以移动一个文件到另一个文件夹

### mv命令：

mv命令用于移动文件或将文件重命名

### 好了，这是1的内容，学会了记得点个赞，破120赞继续下一期。

