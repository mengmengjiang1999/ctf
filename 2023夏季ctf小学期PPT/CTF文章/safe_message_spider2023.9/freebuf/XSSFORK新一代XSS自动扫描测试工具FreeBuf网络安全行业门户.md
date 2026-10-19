**什么是XSS漏洞呢 ？**

> XSS（Cross-site
> scripting）译为跨站脚本攻击，在日常的web渗透测试当中，是最常见的攻击方法之一，并占有很高的地位。它是通过对网页注入可执行代码且成功地被浏览器
> 执行，达到攻击的目的，形成了一次有效XSS攻击，一旦攻击成功，它可以获取用户的联系人列表，然后向联系人发送虚假诈骗信息，可以删除用户的日志等等，有时候还和其他攻击方式同时实
> 施比如SQL注入攻击服务器和数据库、Click劫持、相对链接劫持等实施钓鱼，它带来的危害是巨 大的，是web安全的头号大敌。

 **传统的 xss 探测工具：**

> 一般都是采用 payload in response 的方式，即在发送一次带有 payload 的 http 请求后，通过检测响应包中 payload
> 的完整性来判断，这种方式缺陷，很多。

![](https://image.3001.net/images/20191218/1576659332_5df9e9848ba88.jpg!small)

## 0x001 前言

 **xssfork是一款新一代xss漏洞探测工具，其开发的目的是帮助安全从业者高效率的检测xss安全漏洞。与传统检测工具相比xssfork使用的是
webkit内核的浏览器phantomjs，其可以很好的模拟浏览器。工具分为两个部分，xssfork和xssforkapi，其中xssfork在对网站fuzz
xss的时候会调用比较多的payload。话不多说，一起来研究下这款工具吧 ？**

github地址：<https://github.com/bsmali4/xssfork>

## 0x002 环境依赖

Python 2.x

相关python库（存在于项目requestments.txt中）

## 0x003安装教程

> git clone <https://github.com/bsmali4/xssfork>
>
> python2 -m pip install -rrequestments.txt
>
> python2 xssfork.py -h

出现以下显示，代表安装成功

![](https://image.3001.net/images/20191218/1576661179_5df9f0bb7cb5d.png!small)

## 0x004内置Payload

工具的开发者收集了目前流行的xss
payload，丰富的一批欧（目前内置存在的payload数量为70个），payload文件存在于xssfork\thirdparty\fuzz_dic\payloads.dic文件里面

![](https://image.3001.net/images/20191218/1576681249_5dfa3f21748a1.png!small)

并且会添加上各种闭合的情况

![](https://image.3001.net/images/20191218/1576681925_5dfa41c5bfe4a.png!small)

## 0x005内置编码方式

为了进行更加智能的进行测试，作者在测试时同时加入了绕过方式，提供了四种编码方式，供大家进行使用

现阶段提供了10进制，16进制，随机大小写，关键字叠加四个脚本

> [0]10hex_encode 10进制
>
> [1]16hex_encode 16进制
>
> [2]addkeywords 关键字叠加
>
> [3]uppercase 随机大小写

查看命令为：python xssfork.py --list

![](https://image.3001.net/images/20191218/1576681990_5dfa42062f593.png!small)

使用编码命令为：-t 脚本名称即可

![](https://image.3001.net/images/20191218/1576682096_5dfa427079353.png!small)

## 0x006 使用场景

场景1 反射型xss

操作命令如下：

    
    
    python2 xssfork.py -u "http://xssfork.codersec.net/xssdemo.php?id=23"

![](https://image.3001.net/images/20191219/1576685018_5dfa4dda82def.gif!small)

场景2 带大小写绕过

操作命令如下：

    
    
    python2 xssfork.py -u "http://xssfork.codersec.net/xssdemo.php?id=23" -t uppercase

![](https://image.3001.net/images/20191219/1576685535_5dfa4fdf1a2b7.gif!small)

![](https://image.3001.net/images/20191219/1576685726_5dfa509ece9c9.gif!small)

场景3 dom型xss

操作命令如下：

    
    
    python2 xssfork.py -u "http://xssfork.codersec.net/xssdemo.php?id=23"

![](https://image.3001.net/images/20191219/1576686624_5dfa54203cc8e.gif!small)

场景4 post型xss

操作命令如下：

    
    
    python2 -u "http://xssfork.codersec.net/xssdemo.php" -d "name=123"

![](https://image.3001.net/images/20191219/1576685891_5dfa51437289b.gif!small)

场景5 验证cookie型xss

操作命令如下：

    
    
    python2 xssfork.py -u "http://xssfork.codersec.net/xssdemo.php?id=23" -c "user=fdsfds;pass=123"

![](https://image.3001.net/images/20191219/1576686371_5dfa532373fd2.gif!small)

![](https://image.3001.net/images/20191219/1576686457_5dfa5379ac211.gif!small)

![](https://image.3001.net/images/20191219/1576686511_5dfa53afc9667.gif!small)

## 总结

xssfork感觉还是很不错的工具，希望能够在工作中给你一些帮助，最后感谢工具作者！谢谢

 ***本文作者：fuckerbox，转载请注明来自FreeBuf.COM**

