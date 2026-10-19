朋友叫我帮忙，对一个网站做一下测试。主要目标是看看能不能进入服务器，收集一些建站者信息。

朋友平时待我不薄，此时怎可出言拒绝？经过授权后，直接开搞！

（情景发生时间距今较久，请各位读者酌情参考）

##  **简单的尝试**

用扫描器扫了一下，没有发现漏洞。发现网站存在CDN：![图片](https://image.3001.net/images/20220418/1650280152_625d46d89fbd95eaae4dd.png!small)看了下历史解析记录，还好不多。通过判断，确定最后一条为真实IP：![图片](https://image.3001.net/images/20220418/1650280161_625d46e1efa7933a8e05d.png!small)查看下IP绑定的网站，查到3个域名，其中一个无法访问，另一个是个后台：![图片](https://image.3001.net/images/20220418/1650280169_625d46e947ba7e44873e6.png!small)我们先来看这个后台：![图片](https://image.3001.net/images/20220418/1650280175_625d46ef74dd34623b4ad.png!small)随便输入一个账号和密码，提示数据不存在：![图片](https://image.3001.net/images/20220418/1650280187_625d46fb5d783d2823d0f.png!small)扫了下目录，只扫出个upload目录。存在列目录：![图片](https://image.3001.net/images/20220418/1650280194_625d4702d89702eaef96d.png!small)简单看了下，没有敏感信息，都是图片：![图片](https://image.3001.net/images/20220418/1650280201_625d47091f02ad00b1a63.png!small)回到后台，先爆破一波。挂服务器爆破了不知道多久，成功爆破到管理员密码，登录后台：![图片](https://image.3001.net/images/20220418/1650280207_625d470f801adf2abfacf.png!small)通过后台可以看出这个数据应该是APP注册数据，有50多万条记录。用户名应该是随机取名的，后来拿下权限后验证猜测没错：![图片](https://image.3001.net/images/20220418/1650280214_625d4716278dbc8af9d8f.png!small)回到正题。尝试拿shell，发现可以上传任意文件，但是都不解析。直接下载，最后没能突破成功。![图片](https://image.3001.net/images/20220418/1650280221_625d471d71d43c06ce74e.png!small)![图片](https://image.3001.net/images/20220418/1650280227_625d4723843a43334dd58.png!small)![图片](https://image.3001.net/images/20220418/1650280233_625d47299846b1323f9a5.png!small)

##  **简单的审计**

就在一筹莫展的时候，上帝为我开了一扇窗。翻后台功能，发现系统配置处配置了几个域名。叫PC的这个域名引起了我的注意。对这个PC站进行渗透，扫描无果，手工渗透无果。![图片](https://image.3001.net/images/20220418/1650280242_625d47321714a838640af.png!small)通过查看源码，可以看出这套程序是用了某CMS程序：![图片](https://image.3001.net/images/20220418/1650280251_625d473b092b43c48cd2f.png!small)根据CMS名字，很快找到了官网，并且下载了一份下来本地搭建，准备审计：![图片](https://image.3001.net/images/20220418/1650280258_625d4742b5ad0fbc72d4b.png!small)本地搭建好后，查看了下使用说明，发现网站后台存在默认账号和密码：![图片](https://image.3001.net/images/20220418/1650280266_625d474a91370e48a69e2.png!small)使用默认账号和密码尝试登录目标站后台，成功登录。简单看了下后台，功能很简单，除了设置网站标题，基本上没什么有用的功能。![图片](https://image.3001.net/images/20220418/1650280274_625d47522cd518da917ce.png!small)看官网介绍，经验令我立刻感觉到，在密码修改这里可能会有问题。密码直接明文保存在boss.php文件：![图片](https://image.3001.net/images/20220418/1650280281_625d4759dda978d81edcb.png!small)![图片](https://image.3001.net/images/20220418/1650280290_625d4762cbc2053dfe2c0.png!small)在本地测试发现，修改密码处内容是直接写到boss.php文件，并且没有过滤：![图片](https://image.3001.net/images/20220418/1650280299_625d476b3bf58042a2074.png!small)接下来我们尝试拿Shell。在账号处插入phpinfo()函数，文件内容变成了这样：![图片](https://image.3001.net/images/20220418/1650280307_625d4773d886e27f51d5b.png!small)![图片](https://image.3001.net/images/20220418/1650280315_625d477be6c8882dc564d.png!small)本地测试执行成功：![图片](https://image.3001.net/images/20220418/1650280324_625d47840f1e6efa6003f.png!small)用如上方法，在目标站中成功写入Shell，开心！！！![图片](https://image.3001.net/images/20220418/1650280333_625d478ddfe15fa299857.png!small)![图片](https://image.3001.net/images/20220418/1650280342_625d4796afbf7b24b7967.png!small)发现是System权限，但是执行系统命令的时候发现执行不了。再一次火大：![图片](https://image.3001.net/images/20220418/1650280350_625d479ed58cb8f004b33.png!small)![图片](https://image.3001.net/images/20220418/1650280358_625d47a64acbbc107ff4c.png!small)

##  **巧用宝塔配置文件**

PHP版本5.3.29看下disable_functions是怎么配置的。果然不出所料，禁用了不少函数：![图片](https://image.3001.net/images/20220418/1650280366_625d47aed9b6af9093f92.png!small)由于是Windows系统，利用Windowcom组件绕过限制需要满足php5.4。由于版本太低，谷歌了半天没找到方法，无奈只能放弃，翻翻看看有没有敏感文件之类的。

运气不错，发现网站居然是使用宝塔搭建的，之前居然没反应过来，而且宝塔目录权限还挺高，能看到配置文件内容：![图片](https://image.3001.net/images/20220418/1650280378_625d47ba891a7dd76721c.png!small)Windows下宝塔配置文件在/BtSoft/panel/data/目录下：![图片](https://image.3001.net/images/20220418/1650280386_625d47c2d9127b9747e63.png!small)宝塔数据库是用的sqlite3，我们下载下来后直接用navicat打开即可：![图片](https://image.3001.net/images/20220418/1650280393_625d47c9ae7e8b8a6c010.png!small)获取到宝塔登录密码，成功解密md5：![图片](https://image.3001.net/images/20220418/1650280400_625d47d09a88d50eace47.png!small)成功登录到宝塔界面：![图片](https://image.3001.net/images/20220418/1650280410_625d47da697dff906bbda.png!small)通过计划任务添加管理员：![图片](https://image.3001.net/images/20220418/1650280418_625d47e236c30d2e829c9.png!small)成功登录服务器：![图片](https://image.3001.net/images/20220418/1650280425_625d47e9d279c805e953a.png!small)通过服务器找到刚刚那个网站的目录，才知道是因为网站被打包成jar，所以解析不了脚本：![图片](https://image.3001.net/images/20220418/1650280434_625d47f23fd84d7915a3e.png!small)

##  **获取管理员密码**

因为服务器是Windowsserver2012，所以需要修改：

    
    
    HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest

其中的"UseLogonCredential"设置为1，类型为DWORD32，然后下次用户再登录的时候才能记录到明文密码。使用mimikatz成功获取管理员密码：![图片](https://image.3001.net/images/20220418/1650280441_625d47f90fb194ff6be60.png!small)在半夜的时候，成功利用管理员账号登录上服务器：![图片](https://image.3001.net/images/20220418/1650280448_625d48008d2998394d12a.png!small)

##  **管理员信息收集**

查看谷歌浏览器发现管理员记住了谷歌密码，直接登录谷歌，利用谷歌获取管理员真实姓名，电话，邮箱，qq，地址等敏感信息：![图片](https://image.3001.net/images/20220418/1650280455_625d4807beaa4f8c31224.png!small)![图片](https://image.3001.net/images/20220418/1650280463_625d480f302055e3850f1.png!small)通过谷歌密码安全检查，获取到管理员所有保存在谷歌的账号密码：![图片](https://image.3001.net/images/20220418/1650280469_625d4815927286df150eb.png!small)建站人的信息收集得差不多了，渗透到此也就结束了。

##  **总结**

渗透要细心，入口点不止一个，多尝试。

比如遇到Shell解析不了，可以尝试其他方法。多翻翻敏感目录，配置文件，说不定管理员就在配置文件里面。

在获取目标账号后，不要在自己本地登录，以免留下登录日志和IP，尽量在目标服务器登录。

