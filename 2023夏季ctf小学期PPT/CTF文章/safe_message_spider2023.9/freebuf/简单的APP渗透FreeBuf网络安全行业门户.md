**APP渗透**

app渗透测试和web渗透测试在服务端基本没有区别

web => 通过浏览器访问目标 [HTTP HTTPS]  
app => 通过app访问目标 [HTTP HTTPS]  
EXE程序 => 向目标发送数据包

探索的漏洞。出现在服务端 客户端  
app登录账户 => 应该数据库语句都是差不多  
web登录账户 => 应该数据库语句都是差不多

最早的app就是浏览器套一层皮(网页加壳)

app[客户端] / 浏览器[客户端] / 应用程序[客户端] => 服务沟通 HTTP协议

web容器就不会变

手机设置本地代理：  
1、用真实手机设置代理抓包 [连接同个wifi]  
2、用安卓模拟器进行抓包  
[手机版的虚拟机ldinst_3.102]

 **app渗透测试，最好不要装安卓7.0以上版本** （安装7.0以上只能带安卓自己的证书）

安装证书 cer的证书 不支持der  
把der的证书装了，然后再导出  
PortSwigger CA

    
    
    模拟器硬盘：
    	第一部分：手机专有
    	第二部分：公共区
    
    
    
    找到wifi长按（设置代理） -> 
    装CA证书(第一步：把burp的证书转换为cer) ->
    装CA证书(把证书文件拖入其中) -> 
    然后找到安全-SD卡安装 ->
    设置密码结束。
    
    办公OA系统
    
    安卓端、有网页端
    
    
    写工单、提交工单(XSS SQL注入 越权)
    

1.设置代理burp抓包

![图片.png](https://image.3001.net/images/20220427/1651062408_6269368887fed41418e03.png!small)

2.然后设置

![图片.png](https://image.3001.net/images/20220427/1651062427_6269369b3f8e3aea1ff03.png!small)  
3.这里长时间点击然后修改网络

![图片.png](https://image.3001.net/images/20220427/1651062446_626936aea6458c436e79c.png!small)

![图片.png](https://image.3001.net/images/20220427/1651062469_626936c56c12288765af0.png!small)  
4.这里缺证书burp支持der证书，app支持cer证书  
 **把der的证书装了，然后再导出** （ PortSwigger CA是burp证书） **没有证书不能抓https包**

模拟器硬盘：  
第一部分：手机专有  
第二部分：公共区

我们先把证书移进去到了公共区，然后在选取到了手机专有

 **在设置—安全—从SD卡安装—然后再内部存储空间里面选择它—然后重新启动**

5.我们可以先在时间设置这里打xss

![图片.png](https://image.3001.net/images/20220427/1651062493_626936dddc082d5787107.png!small)  
6.我们如果可以在本地安装，那么我们就可以在MySQL管理器里面去查看admin表，然后有可能会出现一些密码和账号 然后就可以登录

7.然后爆破账号密码 （开发先将账号密码只加密为`base64`，然后`遍历值`，将``等于号，替换为`冒号`）

![图片.png](https://image.3001.net/images/20220427/1651062514_626936f2621c111c61da0.png!small)  
8.这里我们要爆破,deviceid的意思就是可以实现爆破 因为如果这个值不变的话他就不能爆破了

![图片.png](https://image.3001.net/images/20220427/1651062533_626937056b10d768aefa0.png!small)  
9.我们这里是deviceid里面的
我们要让数值变动起来![图片.png](https://image.3001.net/images/20220427/1651062777_626937f91f5d9ab377c20.png!small)  
另外一个是加载 base64的字典

![图片.png](https://image.3001.net/images/20220427/1651062901_62693875f343a7efa6e3d.png!small)

10.然后我们在外出出差里面写工单和提交工单(XSS SQL注入 越权) 上传图片马

![图片.png](https://image.3001.net/images/20220427/1651062834_62693832d21c965272013.png!small)  
11.上传数据包抓住，设置一个抓返回包Do intercepd->Response to this
request然后点击forward出现200就是成功的返回包，查看上传路径

![图片.png](https://image.3001.net/images/20220427/1651062923_6269388be0f792eca2026.png!small)  
12.然后我们去访问图片地址查看图片 发现可以访问

![图片.png](https://image.3001.net/images/20220427/1651062949_626938a5298986eeb0c6f.png!small)

13.然后我们在图片马这里看/.php代码被执行 这里是CGI解析漏洞

![图片.png](https://image.3001.net/images/20220427/1651062982_626938c6e01a50a8eba0b.png!small)

14.发现是CGI解析漏洞，?8=phpinfo();我们去连接webhell工具

![图片.png](https://image.3001.net/images/20220427/1651063025_626938f116dcde71695bb.png!small)  
15.我们连接webhell工具  
APP进阶

    
    
    单向认证:我用XP框架的JustTrustMe来进行绕过
    	自动化检测是否存在单向认证，如果有他帮你hook[他会帮你卡住让app不进入检测证书的环节]
    
    	动态调试： 程序在运行，然后你给他上断点。
    	<?php
    	echo 1;
    	echo 2; （断点）
    	echo 3;
    	?>
    
    	https://www.jianshu.com/p/3382cc765b39
    
    	https://www.bilibili.com/video/BV1xh411a7h3?from=search&seid=12354466957407980525&spm_id_from=333.337.0.0
    
    /storage/sdcard0/Pictures/224.
    cp -r /storage/sdcard0/Pictures/224 /system
    chmod -R 777
    
    mount -o remount -w /system
    

**常见的防御手段:**  
1、证书校验(其实就是https，我们用burp的证书就可以绕过)  
2、代理屏蔽(使用okhttp框架，里面可以设置无代理模式，不走系统代理)最常见  
3、单向认证，证书绑定(SSL pinning 单边校验)  
4、双向认证(安卓并不是很常见)双向认证会影响服务器的性能，其实在安卓中并不常见，代理屏蔽是现在最常见的情况。

解密需要证书。证书是个密码，有密码才能解密  
app->目标[他们都有各自的密码]  
app -> burp -> 目标[burp是看不懂他们沟通的东西  
装证书的核心:让app用burp的证书进行通信  
app-> Burp [burp的证书]  
burp-> 目标通信[正常的证书]  
单向认证:  
app会检测和我通信的人的证书是否合法[他内置一本证书]  
Burp生成一本和app内置证书一样的证书[工具]

双向认证:(双向认证或者是其他协议)  
客户端检测、服务端检测

我们使用charles在Proxy里面把window Proxy取消 然后再Proxy setting里面设置代理

![图片.png](https://image.3001.net/images/20220427/1651063067_6269391b7a64f2819069c.png!small)  
2.然后配置代理

![图片.png](https://image.3001.net/images/20220427/1651063114_6269394a6b513dccefdf8.png!small)  
3.然后在配置规则这里我们要http的给代理，socks也分出来

![图片.png](https://image.3001.net/images/20220427/1651063146_6269396a21ac449a7adb2.png!small)  
4.然后开启

![图片.png](https://image.3001.net/images/20220427/1651063157_62693975193c4ea80ba31.png!small)

