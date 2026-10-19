### Druid未授权访问实战利用

​
最近身边的同学都开始挖src了，而且身边接触到的挖src的网友也是越来越多。作者也是在前几天开始了挖src之路。惊喜又遗憾的是第一次挖src就挖到了一家互联网公司的RCE，可惜因为权重太小补天不收，最后也是交到了cnvd。

#### 随便找一个后台

​ 发现存在逻辑运算类的验证码，看来是爆破首先无望了。

![image.png](https://image.3001.net/images/20220126/1643198480_61f13810ef46f9a1bf3a7.png!small)

不管三七二十一，先扫下web目录再说，看看有没有什么意外收获

呦西！发现对方用的是swagger框架和druid管理工具

![image.png](https://image.3001.net/images/20220126/1643198498_61f138227b266d4cb855f.png!small)

先来访问下swagger界面，发现并没有预期的暴露api接口路径

![image.png](https://image.3001.net/images/20220126/1643198515_61f13833611de1508e797.png!small)

再来看看Druid界面。捡漏了，直接就进管理界面了。

![image.png](https://image.3001.net/images/20220126/1643198533_61f138451dcd7e0bb56cf.png!small)

### SESSION伪造登录后台

进入session监控界面，碰碰运气看能不能找到一个未过期的session。

​
这里作者用的操作方法是fuzz登录后的界面地址，然后直接将session添加到访问的请求包中，最终找到的是index/home。主要还是URL监控里面的URL没一个看着像是登陆后的后台地址。

![image.png](https://image.3001.net/images/20220126/1643198553_61f13859ad7352c08b1da.png!small)

很不幸运第一个拿到的session是一个过期的session

![image.png](https://image.3001.net/images/20220126/1643198568_61f138685a035f5a931b2.png!small)

随后又试了几个终于是找到了有效的session。成功进入了后台管理界面

![image.png](https://image.3001.net/images/20220126/1643198583_61f1387726702da5467de.png!small)

#### 寻找上传点拿shell

​ 找到一个文件上传的地方

![image.png](https://image.3001.net/images/20220126/1643198601_61f13889b1860d58d34ec.png!small)

经过测试发现是前端js验证白名单上传，本来还以为会需要条件竞争、截断之类的操作

![](https://image.3001.net/images/20220126/1643198819_61f13963c0a5581fd48a0.png!small)

成功上传  
![image.png](https://image.3001.net/images/20220126/1643198615_61f1389721f38fcb6d67f.png!small)  
![]![image.png](https://image.3001.net/images/20220126/1643198637_61f138ad5556627881fd7.png!small)

最后才发现，这个站的百度和移动权重为0，谷歌权重为1。既然不能交补天就交到其他地方去吧

