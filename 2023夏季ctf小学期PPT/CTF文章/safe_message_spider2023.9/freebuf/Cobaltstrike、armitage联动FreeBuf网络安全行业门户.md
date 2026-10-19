i 春秋作家：fengzi

原文来自：Cobaltstrike、armitage联动

在使用Cobaltstrike的时候发现他在大型或者比较复杂的内网环境中，作为内网拓展以及红队工具使用时拓展能力有些不足，恰恰armitage可以补充这点，利用metasploit的拓展性能、高性能的内网扫描能力，来进一步的拓展内网，达到最大化的成果输出。

  
  
0x001、环境说明：  

  * A Os:Ubuntu18.04 ip:192.168.1.163 Cobaltstrike3.8 teamserver团队服务器 armitage 团队服务器  

  * B1 Os:Windows 2008r2x64 ip:192.168.1.62 虚拟目标内网入口 （Symantec企业版14）  

  * 3\. B2 Os:Windwos10x64 ip:192.168.1.56 虚拟目标内网个人 PC （无杀软）  

  
0x002、具体流程  
powershell绕过杀软使B1回弹一个beacon，然后通过A的Cobaltstrike spawn
给armitage一个beacon，使用armitage扫描内网、利用漏洞，获取权限，然后再转给Cobaltstrike使团队可以共同协作。0x003、具体过程  
  
0x003.  
1 powershell脚本制作、回弹beacon  
如下图所示,很显然,我们当前拿到的这个webshell,只是个 web 服务器权限。

[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[链接文字](http://www.example.com)

![134008vbw82ynn5y9kdq2t.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134008vbw82ynn5y9kdq2t.png.thumb.jpg)

为了演示效果，这里在本地搭建了一个简单的php站点，使用的webshell链接程序是weevely。

Weevely是一款python编写的webshell管理工具，作为编写语言使用python的一款工具，它最大的优点就在于跨平台，可以在任何安装过python的系统上使用。

使用Cobaltstrike制作powershell脚本回弹beacon。

![134026e1hxq44ph55uxuzr.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134026e1hxq44ph55uxuzr.png.thumb.jpg)

使用Invoke-Obfuscation对ps文件进行混淆，加密操作以及重新编码地址

地址：

<https://github.com/fengziHK/Invoke-Obfuscation>

命令：

1、 Import-Module.\Invoke-Obfuscation.psd1; Invoke-Obfuscation

2、set scriptblock “powershell命令” 或者 set path ps1文件

3、接着选择encoding 进行编码

4、然后out文件

![143208usbbtsljmgmmg3lb.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/143208usbbtsljmgmmg3lb.png.thumb.jpg)![143209tyhz69zv99nbm98y.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/143209tyhz69zv99nbm98y.png.thumb.jpg)在B1机器中执行加过混淆的ps脚本。Powershell
./2.ps1![134029nkhqbeyfk6hkmdkj.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134029nkhqbeyfk6hkmdkj.png.thumb.jpg)

0x003.2 绕过UAC

使用Cobaltstrik的elevate自动bypassuac功能脚本注入或者dll劫持绕过uac这是利用的是dll劫持

![134030mzs6ro6ek2oov6un.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134030mzs6ro6ek2oov6un.png.thumb.jpg)![134031b3f0lzifhj0lzh3i.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134031b3f0lzifhj0lzh3i.png.thumb.jpg)

0x003.3 spawn会话

接下来是重点，打开armitage设置监听监听的payload要和cs一致，不然接收不到会话

![134031sz03h0hh991n143h.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134031sz03h0hh991n143h.png.thumb.jpg)![134032p10z0kv792qnp1wq.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134032p10z0kv792qnp1wq.png.thumb.jpg)![134033oo1j4o9avsho7vov.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134033oo1j4o9avsho7vov.png.thumb.jpg)![134034kdzr8r3grd4gv9pp.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134034kdzr8r3grd4gv9pp.png.thumb.jpg)看到这里，由cs的控制台可以看出他已经发出指令给目标机器，要求连接armitage。同时armitage在几秒钟内接收了会话，在实战当中不会这么快，内网转发网络延迟还是很高的。![134036tk1q8uouzz1fnnzi.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134036tk1q8uouzz1fnnzi.png.thumb.jpg)![134036u9io9z8lwo0lziuh.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134036u9io9z8lwo0lziuh.png.thumb.jpg)

0x003.4 扫描漏洞

这里我们先把armitage添加到对方内网，使用meterpreter的pivoting功能自动添加路由。

![134037eibbzxivfk229xya.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134037eibbzxivfk229xya.png.thumb.jpg)路由添加，使用armitage的默认扫描功能扫描目标内网机器B2![134038mt1udxli555uz6t1.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134038mt1udxli555uz6t1.png.thumb.jpg)识别B2的操作系统版本、端口开放情况。![134038zkek07knanakacay.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134038zkek07knanakacay.png.thumb.jpg)

执行armitage 查找漏洞功能，并利用。

Attacks -findattacks- 会自动识别当前端口所包含的漏洞。这里不做过多的演示。

0x003.5 利用漏洞

![134039t0ixdyad7wzl0cd5.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134039t0ixdyad7wzl0cd5.png.thumb.jpg)

0x003.6 获取权限、并转发会话给Cobaltstrike。

看到B2机器已经上线，提取权限并转发会话给Cobaltsrike

![134040e1hql8dm80nsn8ql.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134040e1hql8dm80nsn8ql.png.thumb.jpg)![134041i0u1n600nbnudjd4.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134041i0u1n600nbnudjd4.png.thumb.jpg)会话转发成功。![134041puz6ke4sjj179djl.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201808/13/134041puz6ke4sjj179djl.png.thumb.jpg)0x004
总结

团队要的比较急、临时赶出来，有不对的地方请大家指正！。

主要就是以armitage和cobaltstrike 互相协作，达到内网最大化利用

  

