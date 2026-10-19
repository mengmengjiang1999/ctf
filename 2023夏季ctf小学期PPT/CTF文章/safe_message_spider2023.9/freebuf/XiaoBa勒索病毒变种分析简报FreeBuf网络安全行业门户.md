## 概述

**XiaoBa勒索病毒，是一种新型电脑病毒，是一款国产化水平极高的勒索病毒，主要以邮件，程序木马，网页挂马的形式进行传播。这种病毒利用各种加密算法对文件进行加密，被感染者一般无法解密，必须拿到解密的私钥才有可能破解。倒计时200秒还不缴赎金，被加密的文件就会被全部销毁。**

以上说明摘自百度百科，但是我分析的这个XiaoBa变种并没有以上行为特征，不过它拥有很强的隐蔽性和感染性，并且具有文件加密，文件删除和挖矿三项主要功能。

## 样本分析

此样本经过微步云沙箱分析（相关链接请参见《参考链接》），确认为恶意样本

![image.png](https://image.3001.net/images/20180425/15246354556652.png!small)

## 行为简图  

![执行简图.png](https://image.3001.net/images/20180425/15246356207756.png!small)

## 权限调整

样本运行之后，首先调整进程权限，确保自己有足够的权限进行后续的操作

![image.png](https://image.3001.net/images/20180425/15246356355388.png!small)

路径判断：样本会判断当前的执行路径是否在%systemroot%\360\360Safe\deepscan目录下，如果不在此目录下则拷贝自身到此目录并执行。如果在此路径下，将会首先进行一些修改系统设置相关的操作：

### 修改文件属性

将文件属性设置为受保护的系统文件，需要在“文件夹和搜索选项”中取消“隐藏受保护的操作系统文件（推荐）”选项才可看到

### 禁用UAC

![image.png](https://image.3001.net/images/20180425/1524635658181.png!small)

### 设置自启动，创建快捷方式

![image.png](https://image.3001.net/images/20180425/15246356697332.png!small)

### 禁用注册表

![image.png](https://image.3001.net/images/20180425/15246356796445.png!small)

### 不显示隐藏的文件

![image.png](https://image.3001.net/images/20180425/15246356884503.png!small)

### 禁用文件夹和搜素选项

![image.png](https://image.3001.net/images/20180425/15246356991193.png!small)

### 创建自启动

![image.png](https://image.3001.net/images/20180425/15246357086313.png!small)

### 删除SafeBoot选项

![image.png](https://image.3001.net/images/20180425/15246357175440.png!small)

### 磁盘遍历

遍历磁盘，在磁盘根目录下创建autorun.inf文件，写入如下数据，尝试进行U盘感染，并且少不了的将此文件设置为隐藏

创建文件夹RECYCLER\S-5-4-62-7581032776-5377505530-562822366-6588，并且将自身文件拷贝进来重写hosts文件，重定向安全厂商网址

  

### 正题

最后创建线程，在线程函数中，XiaoBa会遍历所有文件，查找扩展名为.exe，.com，.scr，.pif，.html，.htm，.gho，.iso的文件，
针对不同的扩展名执行不同的操作.exe，.com，.scr，.pif

重写这些文件，将自身文件写入这些文件的开头，后期如果再运行这些文件的话，就会运行ZhuDongFangYu.exe

![1.png](https://image.3001.net/images/20180425/15246360425921.png!small)

.html，.htm

在这些文件的末尾添加挖矿脚本

.gho，.iso

对于这些文件，直接删除

![2.png](https://image.3001.net/images/20180425/15246360992917.png!small)

一个有意思的点是这个样本的图标是360杀毒的图标，创建的文件夹名也是360，而且经过它重写的可执行程序的图标都换成了360的图标……

![360.png](https://image.3001.net/images/20180425/15246361371863.png!small)

## 参考链接

>
> <https://s.threatbook.cn/report/win7_sp1_enx86_office2013/11abb44de53807e32980a010a473514694f901841e63ab33f5e0ff8754009b47/?sign=history>

 ***本文作者：，转载请注明来自FreeBuf.COM**

