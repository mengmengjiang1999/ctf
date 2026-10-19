越权漏洞越权分为两种：一种为水平越权，一种为垂直越权。

水平越权：指同权限之间能相互修改或查看对方的资料（比如：同为用户 用户A可以查看用户B的资料）

垂直越权：指低权限用户能够修改或查看高权限用户的资料（比如：用户组A能够拥有管理组B的权限）

进入靶场

[http://117.41.229.122:8002](http://117.41.229.122:8002/)![e798c0f314b58ed0b6c30c6b0e52a53d.png](https://image.3001.net/images/20210927/1632749798_6151c8e683bd9005357f0.png!small)

此处提供注册（不能提供注册的利用信息收集）

先注册两个账号 用户1：twalone 用户2: twalone1

先进行两个号的水平越权

使用BurpSuite抓包 配置好BurpSuite
在此页面F5刷新后![0f5e3eb43e6f8e7f586cdffa51b373b6.png](https://image.3001.net/images/20210927/1632749799_6151c8e793f8dec3b8584.png!small)

查看twalone账号报修的信息![1456a0e567e2b63580a649abf6dccdfd.png](https://image.3001.net/images/20210927/1632749800_6151c8e864c4d8edef61a.png!small)

抓到的包![97687138adbbbcc65a2ccdee02d9a087.png](https://image.3001.net/images/20210927/1632749801_6151c8e914d28c6e7fc38.png!small)

![00e548985f3df9d436de12fbbb4f231e.png](https://image.3001.net/images/20210927/1632749801_6151c8e9e57a2f69ff477.png!small)

这里twalone 的信息就能看到了 这里就达到了水平越权

既然能水平越权，而且刚刚抓到的包里面有admin的值尝试修改其值最后发现当shenfen=1能进入管理界面![3d4ddcf1de6f16f69d2781dd96d91cd1.png](https://image.3001.net/images/20210927/1632749802_6151c8ea84347b10da479.png!small)

![f37ff0b2bbcf2d6cde9cf2815bc3fc65.png](https://image.3001.net/images/20210927/1632749803_6151c8eb2bd6da26f5014.png!small)

点击后台管理提示不是管理 又继续尝试

当发现admin=1和shenfen=1时 这时服务器会认为当前账号为管理员账号
可以进入管理界面![29727b71a00f211ca961363bbf5147cf.png](https://image.3001.net/images/20210927/1632749803_6151c8eba52429a68cb53.png!small)

![db6a9adfbe7ea90af112710df4d041d1.png](https://image.3001.net/images/20210927/1632749804_6151c8ec469d186755dbd.png!small)

![63ef31c16c415a767fcc8f3c8a15f89e.png](https://image.3001.net/images/20210927/1632749804_6151c8ecca81e2a525b1b.png!small)

管理界面就出来了 这里是垂直越权

发现有用户组是不是就想干点啥，没错就是添加用户而且还是是管理员权限的。![588682169d38cd2970c836fbd29d8fc7.png](https://image.3001.net/images/20210927/1632749805_6151c8ed56963501f328e.png!small)

通过改包成功添加twalone2管理员账号
登录twalone2![ea8b83321411bbfd4f54c4e7dd780894.png](https://image.3001.net/images/20210927/1632749806_6151c8ee00cfeebca41d4.png!small)

![52ea2966b217b9468118e81ba6c4a52a.png](https://image.3001.net/images/20210927/1632749806_6151c8eebb7f8557bc4b6.png!small)

越权漏洞到此结束 有不足的地方请各位大佬多多指教。

