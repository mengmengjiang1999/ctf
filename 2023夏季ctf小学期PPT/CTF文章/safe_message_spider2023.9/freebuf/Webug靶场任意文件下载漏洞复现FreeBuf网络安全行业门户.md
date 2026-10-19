**漏洞简述：**

一些网站由于业务需求，可能提供文件查看或者下载的功能，如果对用户查看或者下载的文件不做限制，那么恶意用户可以可以查看或者下载一些敏感文件，比如配置信息、源码文件等

 **漏洞成因：**

存在读取文件的函数

读取文件的路径用户可控且未校验或校验不严格

输出了文件内容

 **漏洞危害：**

下载服务器任意文件，如脚本代码、服务及系统配置文件等，进一步利用获取的信息进行更大的危害。

可用得到的代码进一步代码审计，得到更多可利用漏洞

 **实验环境：webug靶场**

![1616332323_60574623911c20d1503d5.png!small](https://image.3001.net/images/20210321/1616332323_60574623911c20d1503d5.png!small)

主页

![1616332333_6057462d51529136ae51c.png!small](https://image.3001.net/images/20210321/1616332333_6057462d51529136ae51c.png!small)

BP抓包

![1616332343_60574637668029bd00f75.png!small](https://image.3001.net/images/20210321/1616332343_60574637668029bd00f75.png!small)

我们把url的路径改为，发送至repeater模块

![1616332357_60574645d3074cab269e5.png!small](https://image.3001.net/images/20210321/1616332357_60574645d3074cab269e5.png!small)

![1616332366_6057464eef83b40930ae7.png!small](https://image.3001.net/images/20210321/1616332366_6057464eef83b40930ae7.png!small)

在repeater模块下send

读取出来了代码

![1616332376_60574658e95379b7be341.png!small](https://image.3001.net/images/20210321/1616332376_60574658e95379b7be341.png!small)

放包，看是否能下载

![1616332388_605746645f1e5a87d33a1.png!small](https://image.3001.net/images/20210321/1616332388_605746645f1e5a87d33a1.png!small)

下载下来，审计一下

![1616332401_60574671810341481ea5e.png!small](https://image.3001.net/images/20210321/1616332401_60574671810341481ea5e.png!small)

发现了一个路径

![1616332417_6057468142a34bbdbab46.png!small](https://image.3001.net/images/20210321/1616332417_6057468142a34bbdbab46.png!small)

用上面的方法下载下来

![1616332428_6057468c9777a5a9f8223.png!small](https://image.3001.net/images/20210321/1616332428_6057468c9777a5a9f8223.png!small)

![1616332445_6057469dde311d535b9ba.png!small](https://image.3001.net/images/20210321/1616332445_6057469dde311d535b9ba.png!small)

发现dbConn.php,前面还有一个DATAPATH

这个有可能是个文件夹名字

我们试一下

![1616332456_605746a8c9a08e4658f49.png!small](https://image.3001.net/images/20210321/1616332456_605746a8c9a08e4658f49.png!small)

没反应，肯定是没有这个文件夹

改为data

![1616332466_605746b24a13e3132dcac.png!small](https://image.3001.net/images/20210321/1616332466_605746b24a13e3132dcac.png!small)

![1616332473_605746b9c31febfe900ce.png!small](https://image.3001.net/images/20210321/1616332473_605746b9c31febfe900ce.png!small)

又发现dbConfig.php

![1616332480_605746c0315aaef179bed.png!small](https://image.3001.net/images/20210321/1616332480_605746c0315aaef179bed.png!small)

下载

![1616332486_605746c6b7b47fd14cdfa.png!small](https://image.3001.net/images/20210321/1616332486_605746c6b7b47fd14cdfa.png!small)

![1616332498_605746d2c4d7c1146e61f.png!small](https://image.3001.net/images/20210321/1616332498_605746d2c4d7c1146e61f.png!small)

发现数据库密码

![1616332509_605746dd3092f3f5d47fb.png!small](https://image.3001.net/images/20210321/1616332509_605746dd3092f3f5d47fb.png!small)

