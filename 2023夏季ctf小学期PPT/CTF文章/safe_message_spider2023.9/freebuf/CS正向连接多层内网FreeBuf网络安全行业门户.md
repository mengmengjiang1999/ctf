# 一、前言

本次文章只用于技术讨论，学习，切勿用于非法用途，用于非法用途与本人无关！

所有环境均为本地环境分析，且在本机进行学习。

这章写的比较简单，主要就是使用cobalt strike工具在多层内网中进行正向连接。作者：rkabyss

# 二、CS正向连接多层内网

使用cobalt strike工具在多层内网中进行正向连接，在内网渗透中也是会用到的。

![1658545421_62db650d3ff6502156460.png!small](https://image.3001.net/images/20220723/1658545421_62db650d3ff6502156460.png!small)

启动cobalt strike进行连接。

![1658545444_62db6524ae79ae408a3dc.png!small](https://image.3001.net/images/20220723/1658545444_62db6524ae79ae408a3dc.png!small)

![1658545459_62db65334db6c1042d6f8.png!small](https://image.3001.net/images/20220723/1658545459_62db65334db6c1042d6f8.png!small)

创建一个HTTP的监听器。

![1658545479_62db65479e17eb1f01792.png!small](https://image.3001.net/images/20220723/1658545479_62db65479e17eb1f01792.png!small)

在Attacks->Web Drive-by->Scripted Web Delivery选项，生成powershell。

![1658545501_62db655d9fa282b1b7d57.png!small](https://image.3001.net/images/20220723/1658545501_62db655d9fa282b1b7d57.png!small)

到代理机中运行powershell木马。

![1658545530_62db657a7b637d81cef53.png!small](https://image.3001.net/images/20220723/1658545530_62db657a7b637d81cef53.png!small)

cobalt strike会发现代理机已经上线。

![1658545549_62db658da13b14dd1a5e4.png!small](https://image.3001.net/images/20220723/1658545549_62db658da13b14dd1a5e4.png!small)

接着创建一个TCP监听器，端口随便设。

![1658545568_62db65a0d48e3bc9a36d4.png!small](https://image.3001.net/images/20220723/1658545568_62db65a0d48e3bc9a36d4.png!small)

目前设置了两个代理

![1658545591_62db65b7112fe6ea32981.png!small](https://image.3001.net/images/20220723/1658545591_62db65b7112fe6ea32981.png!small)

在Attacks-Packages-WindowsExecutable（Stageless）生成一个windows的exe可执行文件，放到目标机上运行。

![1658545609_62db65c9810905accdf9a.png!small](https://image.3001.net/images/20220723/1658545609_62db65c9810905accdf9a.png!small)

在上线代理机interact中输入connect 目标机ip 端口 ，进行正向连接目标机。

![1658545632_62db65e03496eb33f3ecc.png!small](https://image.3001.net/images/20220723/1658545632_62db65e03496eb33f3ecc.png!small)

![1658545643_62db65eb8b62456365d96.png!small](https://image.3001.net/images/20220723/1658545643_62db65eb8b62456365d96.png!small)

接着就可以进一步的内网渗透了。

![1658545662_62db65fe51408f1aecacc.png!small](https://image.3001.net/images/20220723/1658545662_62db65fe51408f1aecacc.png!small)

