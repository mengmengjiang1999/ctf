## **前言：**

本期技术分享，小星将与大家以“Windows令牌的窃取”为题展开讨论，从令牌分类、Access Token的窃取与利用以及CS利用三个方面展开叙述。

###  **（一）令牌**

令牌是系统的临时密钥，相当于账号和密码，用来决定是否允许此次请求和判断是属于哪一个用户的。它允许用户在不提供密码或者其他凭证的前提下，访问网络和资源。这些令牌将持续存在于系统之中，除非系统重新启动。令牌最大的特点是随机性、不可预测，黑客和软件均无法猜测出令牌。

令牌的种类有很多，如：

（1）访问令牌(Access Tokem)：表示访问控制操作系统的对象。

（2）会话令牌(Session Token)：是交互会话中唯一身份标识符。

（3）密保令牌(Scecurity Token)：又称认证令牌或硬件令牌，是一种计算机身份检验的物理设备。

Windows的Access Token也有两种类型，如：

（1）授权令牌(Delegation Tokens)：它支持交互式登录，例如远程桌面、用户桌面访问。

（2）模拟令牌(Impersonation Tokens)：它支持非交互式的绘画，例如访问目标共享文件。

两种令牌会在系统重启后才会清除。授权令牌在用户注销后，该令牌会变为模拟令牌，依然起效。

###  **（二）Access Token** **的窃取与利用**

列举令牌只能列出当前用户和比当前用户权限更低的用户令牌，例如当前用户权限是system或administrator时，我们可以看到系统中的所有令牌。根据权限名或者进程名进行token窃取，利用token窃取可以进行nt提权、普通降权、域(管)用户权限获取等操作。

 **01 exe利用**

（1）incognito.exe可用于有杀毒、不出网、防火墙限制等无法cs或msf上线情况，但是需要管理员的权限运行。

![1671690063_63a3f74f1b0264a3e617a.png!small](https://image.3001.net/images/20221222/1671690063_63a3f74f1b0264a3e617a.png!small)

（2）列举token。

![1671690071_63a3f757045fc319127d1.png!small](https://image.3001.net/images/20221222/1671690071_63a3f757045fc319127d1.png!small)

（3）窃取system。

![1671690077_63a3f75d7dd08b830f7f6.png!small](https://image.3001.net/images/20221222/1671690077_63a3f75d7dd08b830f7f6.png!small)

（4）获取远程主机本地的token。

![1671690088_63a3f768f2d0cd9cfe27b.png!small](https://image.3001.net/images/20221222/1671690088_63a3f768f2d0cd9cfe27b.png!small)

（5）调用远程机器中本地system权限的cmd.exe以执行命令。

![1671690098_63a3f7724ab345e7b0ab2.png!small](https://image.3001.net/images/20221222/1671690098_63a3f7724ab345e7b0ab2.png!small)

 **02 MSF利用**

（1）msf中内置的incognito模块，可用于meterpreter上线后的机器在msf中能够使用incognito实现对目标机器的token窃取。

![1671690115_63a3f7839541300a2d2ae.png!small](https://image.3001.net/images/20221222/1671690115_63a3f7839541300a2d2ae.png!small)

（2）尝试直接使用getsystem来窃取system权限。

![1671690121_63a3f789b23f04b1596c0.png!small](https://image.3001.net/images/20221222/1671690121_63a3f789b23f04b1596c0.png!small)

（3）加载load incognito，以查看当前系统中token模拟system用户的权限。

![1671690134_63a3f79636d0d885b8310.png!small](https://image.3001.net/images/20221222/1671690134_63a3f79636d0d885b8310.png!small)

（4）窃取指定进程。

![1671690143_63a3f79fd216bf0e72d4e.png!small](https://image.3001.net/images/20221222/1671690143_63a3f79fd216bf0e72d4e.png!small)

##  **（三）CS利用**

![1671690162_63a3f7b2e4c76777f8104.png!small](https://image.3001.net/images/20221222/1671690162_63a3f7b2e4c76777f8104.png!small)

  

