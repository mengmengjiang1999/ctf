请大家遵守网络安全法，切勿非法渗透。本文漏洞已报告给学校。

最近收集了一些内网的资产，遇到一个有意思的系统，然后就随便搞了玩玩。比较简单，大佬勿喷。

![1678171429754.png](https://image.3001.net/images/20230619/1687178377_64904c891e01b26a08791.png!small)

首先来一手弱口令，提示用户密码错误，哦豁，没戏了，弱口令进不去，直接放弃。 开个玩笑，尝试一下闭合，发现报错，

![1678171482232.png](https://image.3001.net/images/20230619/1687178379_64904c8b2cefbf5ff6202.png!small)

发现报错，

![1678172471978.png](https://image.3001.net/images/20230619/1687178380_64904c8cda44e25d3bd27.png!small)

接着我试了一下admin'-- admin 万能密码，登录成功。

![1678172824898.png](https://image.3001.net/images/20230619/1687178382_64904c8e21ddef582e630.png!small)

成功进入系统那么可以肯定这里是有注入的，直接sqlmap一把梭哈，

![1678171583192.png](https://image.3001.net/images/20230619/1687178383_64904c8f3bd905d07b250.png!small)

发现是sqlserver ，直接--os-shell

![1678171600213.png](https://image.3001.net/images/20230619/1687178384_64904c90462354a82e32b.png!small)

然后web投递上线cs 上线提权

![1678172601321.png](https://image.3001.net/images/20230619/1687178385_64904c91418ae47676740.png!small)

再利用插件获取明文密码 administrator xxxxx

然后登录 这里管理员改了一下登录的端口 27020

![1678172641748.png](https://image.3001.net/images/20230619/1687178386_64904c925f78721f42210.png!small)

登录成功。 但是想了想，没拿到密码，还想进一步，翻了下文件，看到备份文件

![1678171721118.png](https://image.3001.net/images/20230619/1687178387_64904c9393ce15be52d4a.png!small)![1678171750018.png](https://image.3001.net/images/20230619/1687178388_64904c94c17b14d657837.png!small)![1678171758579.png](https://image.3001.net/images/20230619/1687178390_64904c96451c4f597503e.png!small)

看到有密码，但是连接错误

![1678171768470.png](https://image.3001.net/images/20230619/1687178391_64904c976ef4c3b39089d.png!small)

改用windows身份验证，可以直接登录

![1678171780711.png](https://image.3001.net/images/20230619/1687178392_64904c987569ed7128809.png!small)

成功登录，然后选中刚刚的数据库，新建查询，

![1678172990897.png](https://image.3001.net/images/20230619/1687178393_64904c999f9378e13b28c.png!small)

密码md5加密过了，凭经验，可以知道，好几个密码是123456

![1678171814401.png](https://image.3001.net/images/20230619/1687178395_64904c9b0a82d8efcdf31.png!small)

选择登录 登录成功

![1678172749412.png](https://image.3001.net/images/20230619/1687178396_64904c9c959d9bb4b709c.png!small)

