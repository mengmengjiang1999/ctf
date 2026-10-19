Java的WEB框架是Java进阶课程,当要进行Spring的漏洞分析，要有一定的Java代码知识储备。

 **Java后端标准的学习路线：JavaSE- >JavaEE->Java Web框架**

**![框架.webp.jpg](https://image.3001.net/images/20180815/1534316947_5b73d1934dbc4.jpg!small)**

Spring是Java最核心，最重要的框架。

 **0X01 审计环境准备**

当进行Spring的代码审计（Spring某一个组件包进行分析）时，首先要有相应Spring项目源码，要让没有编写代码经验的朋友从头编写一个Spring的漏洞环境还是有一点难度的，所以要学习Spring代码审计第一步要知道如何查找环境，复现环境。

 **1\. 方法一(spring-messaging为例)**

在docker中获取Spring漏洞环境源码（默认已有docker环境）

docker漏洞环境靶场(<http://vulhub.org/#/environments/>)

![ts.webp.jpg](https://image.3001.net/images/20180815/1534317003_5b73d1cbd5c8b.jpg!small)

查看Spring漏洞信息：

docker漏洞环境（<https://hub.docker.com/u/vulhub/>）

查看你要拉取镜像与方法（或docker中使用搜索 docker search spring-messaging）。

![ing.webp.jpg](https://image.3001.net/images/20180815/1534317028_5b73d1e47591d.jpg!small)![00.webp.jpg](https://image.3001.net/images/20180815/1534317097_5b73d229223ee.jpg!small)![01.webp.jpg](https://image.3001.net/images/20180815/1534317109_5b73d235ac510.jpg!small)

拉取镜像：

docker pull vulhub/spring-messaging:5.0.4。

![504.webp.jpg](https://image.3001.net/images/20180815/1534317133_5b73d24d5105b.jpg!small)

查看拉取的镜像。

![查看.webp.jpg](https://image.3001.net/images/20180815/1534317161_5b73d269985c3.jpg!small)

运行镜像（容器）。

![运行.webp.jpg](https://image.3001.net/images/20180815/1534317183_5b73d27f477d9.jpg!small)

访问主机的8080，这一步已拿到漏洞的环境，可以进行POC的验证。

![poc.webp.jpg](https://image.3001.net/images/20180815/1534317237_5b73d2b5af5d2.jpg!small)  

查看容器ID与启动时运行的命令，可以看到使用命令为java -jar，就能知道环境里面的源码是个jar包。

![jar.webp.jpg](https://image.3001.net/images/20180815/1534317352_5b73d328c0185.jpg!small)

进入容器并且找到源码。

![进入.webp.jpg](https://image.3001.net/images/20180815/1534317418_5b73d36ab4afb.jpg!small)

将容器中的文件复制到本地。

![本地
1.webp.jpg](https://image.3001.net/images/20180815/1534317447_5b73d387912a1.jpg!small)![本地
2.webp.jpg](https://image.3001.net/images/20180815/1534317457_5b73d3910e9d4.jpg!small)

将jar放入jd-gui就能看到相应的源代码。

![相应.webp.jpg](https://image.3001.net/images/20180815/1534317499_5b73d3bb1a65b.jpg!small)

同样在本地也可以使用java -jar运行打包成jar的项目。

![项目.webp.jpg](https://image.3001.net/images/20180815/1534318361_5b73d719785be.jpg!small)

 **扩展：**

如果复制出来的是个war，则只要放入tomcat下的webapps目录，运行tomcat就能生成相应的源代码，并且部署了项目，根据tomcat加war名可访问项目。

![目
1.webp.jpg](https://image.3001.net/images/20180815/1534318419_5b73d75317811.jpg!small)

![目2.webp.jpg](https://image.3001.net/images/20180815/1534318432_5b73d76018937.jpg!small)![目3.webp.jpg](https://image.3001.net/images/20180815/1534318446_5b73d76e9c3d4.jpg!small)  

 **2\. 方法二**

如果再未接触过docker情况下，可以到github（<https://github.com>）搜索环境源码（此方法搜索的源码准确性低），不一定存在相应的漏洞，要修改相应的代码，才能复现漏洞。

![复现.webp.jpg](https://image.3001.net/images/20180815/1534318654_5b73d83ecb9a8.jpg!small)

  

 **0X02 Spring框架审计思路**

 **先熟悉Spring已爆出的各个影响版本、漏洞造成原因、漏洞流程。**

 **第一步：**
审计时先查看项目是否使用有漏洞的jar包版本（查看Spring的配置文件，但现在的项目都是Maven管理jar包，所以先查看Maven的配置文件pom.xml与.iml文件）。

![文件.webp.jpg](https://image.3001.net/images/20180815/1534318891_5b73d92b8eafc.jpg!small)

从图中可以看出项目使用Spring Framework 5.0.4并且使用spring-websockets 模块所以猜测可能存在Spring
Messaging 远程命令执行漏洞。

 **第二步：** 再查看项目是否使用了造成漏洞类与方法或可能造成漏洞的危险类与方法（项目导入IDE搜索问题类、问题方法）

IDEA中

Ctrl+Shift+T（全局搜索类，包括jar包）。

![包.webp.jpg](https://image.3001.net/images/20180815/1534319018_5b73d9aa4ec88.jpg!small)

回车就能进入类所在的位置。

Ctrl+Shift+A\t+N（全局搜索方法，包括jar包）。

![N.webp.jpg](https://image.3001.net/images/20180815/1534319092_5b73d9f493e0a.jpg!small)

 **第三步：**
满足前两步，接下来就可以运行初步的POC动态调试确定是否可以利用漏洞（使用IDEA的Debug），在造成漏洞的类与方法处打上断点进行流程分析。

![分析.webp.jpg](https://image.3001.net/images/20180815/1534319138_5b73da225d11c.jpg!small)

分析和调试数据流程，构造poc。

![构造.webp.jpg](https://image.3001.net/images/20180815/1534319162_5b73da3a51426.jpg!small)

 **0X03 小小总结**

此篇讲述如何得到Spring审计的Demo，审计源码，提供Spring框架审计思路初步判定是否存在漏洞，剩下就是构造POC，动态调试分析修改POC。下期斗哥将带来Java代码审计Spring框架知识篇将讲述Spring框架构造POC要必备的知识。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180815/1534319200_5b73da60de47d.jpg!small)

