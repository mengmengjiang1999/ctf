一名合格的Web安全工程师要具备很多的技能，不但要对网站架构熟悉，通讯协议，测试流程与测试工具使用，漏洞利用脚本编写，还要有丰富的经验积累等，每一项能力中都需要精心雕琢，深度研究，才能进阶到更高的程度，这个过程中少不了前辈的引导、个人的努力和坚持。  

![1.jpg](https://image.3001.net/images/20200115/1579076482_5e1ecb827ece8.jpg!small)  

网安学习绝非一朝一夕，这期间我们除了知识的积累，更重要的是进行实践，只有在实践中学会发现问题，解决问题，才能让我们所学的知识真正做到学以致用！

今天 i 春秋与大家分享的是一篇关于环境搭建的文章：WebGoat课程通关之搭建WebGoat8.0，希望对大家所有帮助！

注：i 春秋公众号旨在为大家提供更多的学习方法与技能技巧，仅供学习参考。

 **WebGoat介绍**

WebGoat是OWASP维护的，用于进行WEB漏洞测试和学习的JAVA应用程序。

 **运行环境**

WebGoat8.0运行需要在java环境下，java版本至少需要>=1.8，所以首先要安装配置好java。

 **下载**

WebGoat8.0下载的地址：

https://github.com/WebGoat/WebGoat/releases

WebGoat-server-8.0.0.M26.jar用于启动WebGoat

WebWolf-8.0.0.M26.jar用于启动WebWolf（类似于一个邮件系统，接收cookie，token等）

![2.jpg](https://image.3001.net/images/20200115/1579076534_5e1ecbb6e4515.jpg!small)  

 **启动**

启动WebGoat8.0&WebWolf：首先，打开cmd命令窗口，切换到WebGgoat-server-8.0.0.M26.jar的目录。

这里使用的是WebGgoat-server-8.0.0.M21.jar，区别应该不大。

![3.jpg](https://image.3001.net/images/20200115/1579076568_5e1ecbd820789.jpg!small)然后使用java
-jar webgoat-server-8.0.0.M21.jar
--server.port=9091，来启动webgoat；server.port=9091，这个参数是设置端口为9091，不加该参数，默认使用8080端口。  

![4.jpg](https://image.3001.net/images/20200115/1579076598_5e1ecbf616a09.jpg!small)出现如下提示后，基本可以确定WebGoat成功启动了：  

![5.jpg](https://image.3001.net/images/20200115/1579076618_5e1ecc0a1822e.jpg!small)打开127.0.0.1:9091/WebGoat/login.html，看看是不是真的启动成功了：  

![6.jpg](https://image.3001.net/images/20200115/1579076644_5e1ecc242cac2.jpg!small)通过下面的【Register
new user】，注册一个新用户，登录进入WebGoat后，就可以开始学习了。  

![7.jpg](https://image.3001.net/images/20200115/1579076763_5e1ecc9ba1b70.jpg!small)  

WebWolf的启动方式基本一致，WebWolf的默认端口为9090，登录地址：127.0.0.1:9090/WebWolf/login.html，WebWolf的账户与WebGoat是相通的，使用WebGoat的账户可以直接登录WebWolf。

 **技巧**

在抓WebGoat包的时候，因为WebGoat启动在本地，即127.0.0.1，所以可以设置BurpSuite里面只展示127.0.0.1的流量。

![8.jpg](https://image.3001.net/images/20200115/1579076801_5e1eccc163e68.jpg!small)![9.jpg](https://image.3001.net/images/20200115/1579076801_5e1eccc1ab4a7.jpg!small)  

在WebGoat运行的时候，会有两个请求不断的在请求，可以把他们剔除掉，以免影响后续的操作。  

![10.jpg](https://image.3001.net/images/20200115/1579076829_5e1eccdd28091.jpg!small)![11.jpg](https://image.3001.net/images/20200115/1579076829_5e1eccdd2e790.jpg!small)以上是今天分享的内容，大家看懂了吗？

