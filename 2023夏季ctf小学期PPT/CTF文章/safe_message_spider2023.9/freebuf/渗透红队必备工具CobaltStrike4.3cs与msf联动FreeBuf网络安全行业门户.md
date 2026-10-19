***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

## 前言

前几天，一位师傅让我渗透个他自己搭建的靶机，好家伙，webshell后就没了思路，但师傅提醒我用cs与msf联动，于是就开始搞起来

## 工具下载

CobaltStrike4.3

链接：https://pan.baidu.com/s/1nj8vm6EKqWJ-O_Ah7DAsRw  
提取码：10px

## 主机上线

参考文章https://www.freebuf.com/sectool/281857.html

## cs与msf联动

先生成监听，选择Foreign HTTP 或者 Foreign HTTPS ，用于派生会话

![1628044091_6109fb3bc648636e53bc5.png!small?1628044090807](https://image.3001.net/images/20210804/1628044091_6109fb3bc648636e53bc5.png!small?1628044090807)

这是我设置的

![1628044176_6109fb90a4b27ed4bcff8.png!small?1628044175680](https://image.3001.net/images/20210804/1628044176_6109fb90a4b27ed4bcff8.png!small?1628044175680)

到要接收会话的主机上，打开端口监听（当然选择用kali，因为方便后续进行渗透）

使用 exploit/multi/handler 模块

![1628044188_6109fb9c2de0ddff51f38.png!small?1628044187325](https://image.3001.net/images/20210804/1628044188_6109fb9c2de0ddff51f38.png!small?1628044187325)

注意使用的payload及设置参数

选择payload很重要，cs中选择走HTTP流量派生会话，下面用对应的HTTP payload，否则是监听不到的

![1628044289_6109fc01a27a1278bbc4d.png!small?1628044288798](https://image.3001.net/images/20210804/1628044289_6109fc01a27a1278bbc4d.png!small?1628044288798)

打开监听

![1628044338_6109fc32a4aae9ef2ef7c.png!small?1628044337687](https://image.3001.net/images/20210804/1628044338_6109fc32a4aae9ef2ef7c.png!small?1628044337687)

回到cs上 用Spawn 派生会话到msf

![1628044359_6109fc47c932ecdde4ba7.png!small?1628044358897](https://image.3001.net/images/20210804/1628044359_6109fc47c932ecdde4ba7.png!small?1628044358897)

成功在kali上监听到会话，这时就可以利用meterpreter为所欲为了

![1628044402_6109fc723f8deea7b09c4.png!small?1628044401334](https://image.3001.net/images/20210804/1628044402_6109fc723f8deea7b09c4.png!small?1628044401334)

## msf与cs联动

这边由于找不到靶机的原因，就没办法实现，但是大致的思路到位了

在cs上设置新的监听，这边设置的监听ip和端口要和 kali (攻击机) 上的一致

![1628045707_610a018bf36362298a69b.png!small?1628045707007](https://image.3001.net/images/20210804/1628045707_610a018bf36362298a69b.png!small?1628045707007)

使用 exploit/windows/local/payload_inject 模块

![1628045779_610a01d320c78237b9fd0.png!small?1628045778594](https://image.3001.net/images/20210804/1628045779_610a01d320c78237b9fd0.png!small?1628045778594)

设置参数 disablepayloadhandler 用来禁用 msf 的监听，才能让cs监听到东西，这边session指的是msf上的会话，可以通过
sessions -l 查看，这边没有找到对应靶机，就没有session，运行后会将会话派生到cs上，就可以进行进一步利用

![1628045809_610a01f1bb9cd1f98b14a.png!small?1628045808786](https://image.3001.net/images/20210804/1628045809_610a01f1bb9cd1f98b14a.png!small?1628045808786)

## 结语

将cs上监听到的主机会话派生给msf，其实就是后渗透了，只是使用 meterpreter 还是 beacon
的区别。在cs上监听到的主机比msf中能产生会话的主机 容易得多，总得来说，cs 派生会话给 msf 会常用点。各位师傅切勿进行非法渗透。

  

