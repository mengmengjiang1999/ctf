![](https://image.3001.net/images/20221129/1669725896_6385fec8105a2b1dac3ce.png!small)

## 关于EvilTree

EvilTree是一款功能强大的文件内容搜索工具，该工具基于经典的“tree”命令实现其功能，本质上来说它就是“tree”命令的一个独立Python
3重制版。但EvilTree还增加了在文件中搜索用户提供的关键字或正则表达式的额外功能，而且还支持突出高亮显示包含匹配项的关键字/内容。

## 工具特性

>
> 1、当在嵌套目录结构的文件中搜索敏感信息时，能够可视化哪些文件包含用户提供的关键字/正则表达式模式以及这些文件在文件夹层次结构中的位置，这是EvilTree的一个非常显著的优势；
>
>
> 2、“tree”命令本身就是分析目录结构的一个神奇工具，而提供一个单独的替代命令用于后渗透测试是非常方便的，因为它并不是每一个Linux发行版都会预安装的，而且在Windows操作系统上功能还会有部分受限制。

## 工具下载

由于该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/t3l3machus/eviltree.git

## 工具使用样例

 **样例一-执行一次正则表达式搜索，在/var/www中寻找匹配“password = something”的字符串：**

**![](https://image.3001.net/images/20221129/1669725922_6385fee24ed477d88356a.png!small)**

 **样例二-使用逗号分隔的关键字搜索敏感信息：**

**![](https://image.3001.net/images/20221129/1669725929_6385fee92864d91506c66.png!small)**

 **样例三-使用“-i”参数只显示匹配的关键字/正则式内容（减少输出内容长度）：**

![](https://image.3001.net/images/20221129/1669725937_6385fef13e9ff40533bb1.png!small)

## 有用的关键字/正则表达式模式

### 搜索密码可用的正则表达式

    
    
    -x ".{0,3}passw.{0,3}[=]{1}.{0,18}"

### 搜索敏感信息可用的关键字

    
    
    -k passw,db_,admin,account,user,token

## 项目地址

 **EvilTree** ：【[ _GitHub传送门_](https://github.com/t3l3machus/eviltree)】

## 参考资料

> [
> _https://twitter.com/intent/tweet?text=A%20standalone%20python3%20remake%20of%20the%20classic%20%22tree%22%20command%20with%20the%20additional%20feature%20of%20searching%20for%20user%20provided%20keywords%2Fregex%20in%20files%2C%20highlighting%20those%20that%20contain%20matches.
> &url=https://github.com/t3l3machus/eviltree&via=t3l3machus&hashtags=cybersecurity,pentesting,redteaming,hacking,github﻿_](https://twitter.com/intent/tweet?text=A%20standalone%20python3%20remake%20of%20the%20classic%20%22tree%22%20command%20with%20the%20additional%20feature%20of%20searching%20for%20user%20provided%20keywords%2Fregex%20in%20files%2C%20highlighting%20those%20that%20contain%20matches.&url=https:/github.com/t3l3machus/eviltree&via=t3l3machus&hashtags=cybersecurity,pentesting,redteaming,hacking,github)

