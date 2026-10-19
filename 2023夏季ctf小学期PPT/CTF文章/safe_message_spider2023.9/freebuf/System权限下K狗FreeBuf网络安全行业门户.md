**前言**

过不了狗K不了狗，那么人生还有什么意义。最近遇到好玩的一个东西，拿到Webshell提权后权限为system权限。

![](https://image.3001.net/images/20201126/1606370994_5fbf46b202b16835332d2.png!small)

但是发现某些操作受到了权限，拒绝访问。原本以为自己提权姿势不对，最后查看进程服务才发现，是某狗在干坏事。![](https://image.3001.net/images/20201126/1606371115_5fbf472b595da62885696.png!small)![](https://image.3001.net/images/20201126/1606371136_5fbf4740f1fb8306509d4.png!small)

在我们加用户的时候，不会有任何拦截，当我们添加用户到管理组时发现拒绝访问。

![](https://image.3001.net/images/20201126/1606371204_5fbf47843040fa721e165.png!small)

常规思路1：利用用户克隆administrators，直接登录到administrators用户上去。

常规思路2：抓账号密码。

常规思路3：禁用SafeDogCloudHelper服务，shutdown -f重启服务器。

在该目标克隆账号时发现缺少dll文件，头疼失败，重启服务器动作太大，抓密码成功抓到，但是头铁的我就想kdog，因为之前在某次比赛中，被dog坑惨的经历。于是有了以下思路：

 **正文**

1、通常情况下会使用我们会用takskill /f /pid
进程号强K进程，但是dog进程死活K不掉，原因在于虽然权限为system，但dog驱动仍会拦截你的操作，没办法他是驱动我是用户。那么如果我能控制某驱动，再k掉dog驱动，那么应该就不会受影响了。

![](https://image.3001.net/images/20201126/1606371228_5fbf479cd880c949b6bde.png!small)

2、但是驱动需要签名，虽然TB一大堆，不会内核的我无解。但是常用的一个进程管理软件给了我思路，ProcessHacker。内核大牛说ProcessHacker内自带驱动，自带签名，解决了所有问题。

![](https://image.3001.net/images/20201126/1606371246_5fbf47ae282f0902f1214.png!small)

保护进程K掉后再来加管理组。

![](https://image.3001.net/images/20201126/1606371263_5fbf47bfb7cb16db7abfc.png!small)

成功执行。这里测试K进程是直接在本地管理员cmd打开的，通过拿到的system shell 执行也是一样的效果。

3、只杀进程的方法，有效期较短，服务会停掉后，隔段时间会自启，一劳永逸的方式是直接禁用服务，再k掉进程，在这里不会存在拒绝访问，驱动降维打击。

kill全进程后，stop所有服务后，再利用sc禁用SafeDogGuardCenter服务，保护程序就不会自启了。

![](https://image.3001.net/images/20201126/1606371315_5fbf47f343d8148b1e62d.png!small)![](https://image.3001.net/images/20201126/1606371322_5fbf47fa871f3956ec0bb.png!small)![](https://image.3001.net/images/20201126/1606371331_5fbf48038b7c8b6d50190.png!small)

 **总结**

杀鸡还得用牛刀，体会到了内核级别的降维打击，在dog上测试成功，在一些杀软上未尝试。

