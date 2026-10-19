审计系统：dedeCMS v5.7

目标：篡改cookie实现任意登录并分析原理。

我觉得这个漏洞主要是对于用户ID的处理方式不当，以及把敏感的东西放到了cookie中进行传输。

分析流程图：

![](https://image.3001.net/images/20220330/1648642431_6244497facae1b4e4abaa.png!small)

 **细致分析** ：  
首先，当我们访问member/index.php?uid=00001时，触发了Putcookie()，而Putcookie()中的last_vid就是我们url里面的uid，同时，还设置了last_vid以及last_vid_ckMd5两个cookie进行传输，这个地方就造成了cookie泄露，我们可以通过抓包得到。

![](https://image.3001.net/images/20220330/1648642432_6244498021dffb3aa8920.png!small)

![](https://image.3001.net/images/20220330/1648642432_62444980984e793159e53.png!small)

获得了后面需要用到的两个东西：last_vid和last_vid_ckMd5。

其次，当我们登陆成功后，会进行IsLogin()判断，判断是否是登录状态。

![](https://image.3001.net/images/20220330/1648642433_624449819eb689e4d35ee.png!small)

![](https://image.3001.net/images/20220330/1648642434_624449820bfb00c2275a5.png!small)而M_ID又是来源于memberlogin.class.php中170行，通过GetNum(GetCooke("DedeUserID"))来获得；

![](https://image.3001.net/images/20220330/1648642434_6244498265be9063c154a.png!small)

期间我们可以观察cookie.helper.php中的GetCookie()和PutCookie()，发现生成cookie的方法都一样。

![](https://image.3001.net/images/20220330/1648642434_62444982c666e8a7ca203.png!small)

然后继续memberlogin.class.php得到了M_ID往下走，我们发现，在判断M_ID是否为空时，运用了intval()函数。这个函数有一个特点，就是在处理一些特殊数据进行取整处理时会进行一定转换，而也就是这些转换为我们提供了机会。下面引用菜鸟论坛对于intval()对于一些数据的处理说明：

![](https://image.3001.net/images/20220330/1648642435_624449833b8982e5fc3ce.png!small)

![](https://image.3001.net/images/20220330/1648642435_62444983b60783b330c02.png!small)

而之前我们提到在获取cookie的时候也有一个GetNum()方法，这个方法其实也就是对M_ID做一个只取数字的处理，所以我们也可以通过修改正则表达式来达到想要的效果，避免使用intval()的而出现这个问题。

![](https://image.3001.net/images/20220330/1648642436_624449841cb320dae6cb6.png!small)

因此，我们设置M_ID=00001时，会通过intval()变为1，而1恰好就是admin的ID。那么我们得到了admin的M_ID之后，回到index.php进行后续的数据获取操作，从而进入了对应的空间。

 **操作及结果：**

首先，注册一个username是00001的用户，类似能通过intval()换为1的就行，而这个username也就是我们的uid：

![](https://image.3001.net/images/20220330/1648642436_6244498462d490834cb50.png!small)

然后用00001用户登陆后，刷新进行抓包，用之前我们访问00001主界面抓取到的cookie进行修改再发包过去：

![](https://image.3001.net/images/20220330/1648642436_62444984c002f6f5b81b4.png!small)

得到：

![](https://image.3001.net/images/20220330/1648642437_624449854d59323785f71.png!small)

 **作者** | 枫涧

 **编辑** | 楌橪

