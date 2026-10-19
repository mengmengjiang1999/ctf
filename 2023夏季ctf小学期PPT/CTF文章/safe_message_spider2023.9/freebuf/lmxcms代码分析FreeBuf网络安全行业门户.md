最近遇到一个lmxcms的网站，发现存在历史漏洞，于是下载源码进行审计

[下载地址](http://www.lmxcms.com/down/xitong/20210530/14.html)

首先，将源码放入到Seay代码审计工具中进行代码审计，并查看整体框架结果

![1651559651_6270cce36bb43b00a217b.png!small?1651559654265](https://image.3001.net/images/20220503/1651559651_6270cce36bb43b00a217b.png!small?1651559654265)

查看index.php文件，可以看到调用了几个文件，这里为了节省篇幅，就不继续分析了，根据自己的个人习惯进行了解

![1651559663_6270ccef82e2a16647a1b.png!small?1651559666558](https://image.3001.net/images/20220503/1651559663_6270ccef82e2a16647a1b.png!small?1651559666558)

### 前端SQL注入漏洞：

发现前端页面存在留言框，会不会有XSS漏洞

![1651559673_6270ccf923f18dc918095.png!small?1651559678070](https://image.3001.net/images/20220503/1651559673_6270ccf923f18dc918095.png!small?1651559678070)

进入到根目录下c/index/BookAction.class.php，查看index方法，发现传入到checkData方法里面

![1651559681_6270cd01af0d4bed3e52f.png!small?1651559684272](https://image.3001.net/images/20220503/1651559681_6270cd01af0d4bed3e52f.png!small?1651559684272)

继续跟进，XSS被过滤死了，但是有提交，那是否存在SQL注入漏洞

![1651559691_6270cd0b183f1304b90f4.png!small?1651559694190](https://image.3001.net/images/20220503/1651559691_6270cd0b183f1304b90f4.png!small?1651559694190)

分析filter_strs，直接跟进该函数，看到遍历的全部参数值(键值对的值)，然后对传入的参数进行解码及去除html标签及替换%为空

![1651559699_6270cd136ed06d7e3414e.png!small?1651559701772](https://image.3001.net/images/20220503/1651559699_6270cd136ed06d7e3414e.png!small?1651559701772)

分析P函数，直接跟进，发现调用filter_sql方法

![1651559708_6270cd1ca0f161c8084e7.png!small?1651559713350](https://image.3001.net/images/20220503/1651559708_6270cd1ca0f161c8084e7.png!small?1651559713350)

filter_sql函数是过滤sql注入的，对一些非法函数进行过滤，基本都过滤完了，但是过滤函数只过滤了值，没有过滤间，也就是$k，继续分析

![1651559716_6270cd24a34c9cd94a83d.png!small?1651559718640](https://image.3001.net/images/20220503/1651559716_6270cd24a34c9cd94a83d.png!small?1651559718640)

直接回到最开始的代码，直接进入add函数

![1651559725_6270cd2d9d72f56419d90.png!small?1651559728262](https://image.3001.net/images/20220503/1651559725_6270cd2d9d72f56419d90.png!small?1651559728262)

跟进查看内容

![1651559732_6270cd34a3876415b50a4.png!small?1651559733930](https://image.3001.net/images/20220503/1651559732_6270cd34a3876415b50a4.png!small?1651559733930)

继续跟进addModel

![1651559739_6270cd3bb7a15994dcdc2.png!small?1651559740397](https://image.3001.net/images/20220503/1651559739_6270cd3bb7a15994dcdc2.png!small?1651559740397)

继续跟进，发现并没有对sql语句过滤

![1651559746_6270cd429b28f49ee8d5d.png!small?1651559748506](https://image.3001.net/images/20220503/1651559746_6270cd429b28f49ee8d5d.png!small?1651559748506)

直接提交留言，抓包

![1651559753_6270cd49c83d4a0fa8529.png!small?1651559755229](https://image.3001.net/images/20220503/1651559753_6270cd49c83d4a0fa8529.png!small?1651559755229)

当在mail后面添加)让sql语句错误时

![1651559761_6270cd516af89e8be30aa.png!small?1651559763701](https://image.3001.net/images/20220503/1651559761_6270cd516af89e8be30aa.png!small?1651559763701)

发现留言姓名处会回显，sql语句进行构造，成功查看用户

![1651559769_6270cd593b2e34276e34a.png!small?1651559770249](https://image.3001.net/images/20220503/1651559769_6270cd593b2e34276e34a.png!small?1651559770249)

![1651559774_6270cd5e67b4ab5518d56.png!small?1651559776325](https://image.3001.net/images/20220503/1651559774_6270cd5e67b4ab5518d56.png!small?1651559776325)

### 前台sql注入：

看到有个搜索，尝试进行sql语句测试，发现存在

![1651559798_6270cd76056711aeb9c5a.png!small?1651559799429](https://image.3001.net/images/20220503/1651559798_6270cd76056711aeb9c5a.png!small?1651559799429)

找到相应代码文件，发现必须存在keywords值，否则程序退出，下面还有几个参数可以增加，我们跟踪程序,将param数组给了$arr数组，然后带入了searchCoutn函数，跟进再跟进

![1651559804_6270cd7cc13e43eec064c.png!small?1651559809337](https://image.3001.net/images/20220503/1651559804_6270cd7cc13e43eec064c.png!small?1651559809337)

跟进该方法，发现调用新的方法，继续跟进

![1651559810_6270cd8295eb1c7d476b5.png!small?1651559811208](https://image.3001.net/images/20220503/1651559810_6270cd8295eb1c7d476b5.png!small?1651559811208)

跟进

![1651559817_6270cd89a0b54712edfd5.png!small?1651559818380](https://image.3001.net/images/20220503/1651559817_6270cd89a0b54712edfd5.png!small?1651559818380)

继续跟进

![1651559824_6270cd90925f2a609c6de.png!small?1651559826213](https://image.3001.net/images/20220503/1651559824_6270cd90925f2a609c6de.png!small?1651559826213)

存在一定的函数过滤

![1651559831_6270cd97332fb51e7ff5f.png!small?1651559832066](https://image.3001.net/images/20220503/1651559831_6270cd97332fb51e7ff5f.png!small?1651559832066)

进行sql语句测试，可以看到成功报错，sqlmap进行测试，这里忘记贴图

###
![1651559838_6270cd9e128970dadeb79.png!small?1651559839245](https://image.3001.net/images/20220503/1651559838_6270cd9e128970dadeb79.png!small?1651559839245)

### 后台任意文件删除：

![1651559851_6270cdabc7dded50dbb13.png!small?1651559854694](https://image.3001.net/images/20220503/1651559851_6270cdabc7dded50dbb13.png!small?1651559854694)

选择一个图片，抓包分析，进行url解密

![1651559860_6270cdb468d9b7f58766c.png!small?1651559863308](https://image.3001.net/images/20220503/1651559860_6270cdb468d9b7f58766c.png!small?1651559863308)

文件位置c/admin/FileAction.class.php，这里使用post传参接收fid的参数，判断是否为空，不为空进入下一步，我们跟进delete函数

![1651559882_6270cdcaa2188047f6aa8.png!small?1651559883474](https://image.3001.net/images/20220503/1651559882_6270cdcaa2188047f6aa8.png!small?1651559883474)

没有什么过滤，只是要求fid接收前面存在#####即可

![1651559889_6270cdd163d0825ae918d.png!small?1651559893899](https://image.3001.net/images/20220503/1651559889_6270cdd163d0825ae918d.png!small?1651559893899)

构造删除文件，成功删除

![1651559895_6270cdd7dc9297833d78f.png!small?1651559898824](https://image.3001.net/images/20220503/1651559895_6270cdd7dc9297833d78f.png!small?1651559898824)

### 后台任意文件写入：

找到后台的模板管理的地方，像这种地方一般都存在漏洞，比如目录遍历，文件写入，文件删除，这里 分析文件写入

![1651559913_6270cde948e5e57f9001a.png!small?1651559916705](https://image.3001.net/images/20220503/1651559913_6270cde948e5e57f9001a.png!small?1651559916705)

查看源码，可以看到并没有任何的目录限制

![1651559919_6270cdefbfccd3a843797.png!small?1651559922795](https://image.3001.net/images/20220503/1651559919_6270cdefbfccd3a843797.png!small?1651559922795)

直接把路径改到根目录的index.php，发现打印处该文件的内容

![1651559926_6270cdf60231ed9da7e42.png!small?1651559928018](https://image.3001.net/images/20220503/1651559926_6270cdf60231ed9da7e42.png!small?1651559928018)

看到seay代码审计工具审计处该处存在漏洞

![1651559932_6270cdfc2dc8ffb2e4951.png!small?1651559932485](https://image.3001.net/images/20220503/1651559932_6270cdfc2dc8ffb2e4951.png!small?1651559932485)

看到调用了file_put_contents危险函数

![1651559938_6270ce025b397c2a96c75.png!small?1651559939539](https://image.3001.net/images/20220503/1651559938_6270ce025b397c2a96c75.png!small?1651559939539)

创建木马文件写入

![1651559944_6270ce08c71048075fb9a.png!small?1651559946545](https://image.3001.net/images/20220503/1651559944_6270ce08c71048075fb9a.png!small?1651559946545)

访问成功

![1651559952_6270ce1037d1fe6dabd18.png!small?1651559955257](https://image.3001.net/images/20220503/1651559952_6270ce1037d1fe6dabd18.png!small?1651559955257)

### 任意文件上传：

这里就没在分析代码，可以自己添加上传类型的后缀，添加成功后自行进行上传

![1651559965_6270ce1d9e2998f230422.png!small?1651559967883](https://image.3001.net/images/20220503/1651559965_6270ce1d9e2998f230422.png!small?1651559967883)

  

