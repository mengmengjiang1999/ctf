网上有很多文章介绍多个扫描器之间进行联动扫描漏洞，组合无非是：awvs+burp，awvs+xray，xray+burp，但很少把它们三个都整合到一起的，今天就来说一下这个组合。

有人会说，直接用awvs开扫不就完了，还用burp或xray干嘛？首先awvs是收费的，我们大部分是用的破解版，扫描功能不可能实时更新，我们这里主要是用到它的scan
speed和user-agent以及登陆会话功能，相比xray来说更方便操作；burp的作用：我们可以在http历史记录查看每一个数据包，更加直观；xray的作用：长亭公司一直在维护升级，而且xray是被动扫描。好了，不多说，开干！

测试环境：

本地两台虚拟机： 靶机：192.168.1.123/pikachu 攻击机：192.168.1.125

先启动burp，设置好代理，就是awvs的扫描数据会通这个代理被burp获取到

![](https://image.3001.net/images/20210907/1631003661_6137240d58e1f444ecb17.png!small)

在burp中找到用户选项(user options)，再添加一层代理，和xray进行联动

![](https://image.3001.net/images/20210907/1631003746_61372462e8ac279c84692.png!small)

![](https://image.3001.net/images/20210907/1631003774_6137247ed69edc31f449e.png!small)

使用xray时要安装证书，网上很多文章有介绍，可自行百度，启动xray，对应好端口

![](https://image.3001.net/images/20210907/1631003804_6137249cebcc60b96fb08.png!small)

开启awvs，添加目标网站的域名

![](https://image.3001.net/images/20210907/1631003836_613724bc4224d09752480.png!small)

扫描速度这里可设置慢一点，因为目标网站上的安全狗有防CC攻击

![](https://image.3001.net/images/20210907/1631003873_613724e1aea2a8907c338.png!small)

在user-agent这里设置成百度的搜索引擎，伪装成百度爬虫

![](https://image.3001.net/images/20210907/1631003898_613724fab80c8136482c7.png!small)

在http代理这里把代理设置成127.0.0.1:8080，也就是挂到burp上。

![](https://image.3001.net/images/20210907/1631003939_61372523b34360783d46d.png!small)

设置好后，启动全扫描

![](https://image.3001.net/images/20210907/1631003972_6137254467e831e1501d1.png!small)

现在三个工具都已经启动了，整个过程不需要人工参与，直接等待结果就行。

Awvs:

![](https://image.3001.net/images/20210907/1631004014_6137256ec3085914a7fa3.png!small)

Xray:

![](https://image.3001.net/images/20210907/1631004032_61372580c272074d9abf0.png!small)

Burp:

![](https://image.3001.net/images/20210907/1631004053_6137259537dc939ef15f2.png!small)

好了，就介绍到这里，感兴趣的小伙伴可以试下

