## **漏洞描述**

Lanproxy 0.1 存在路径遍历漏洞，该漏洞允许目录遍历读取/../conf/config.properties来获取到内部网连接的凭据。

 **Lanproxy**

lanproxy是一个将局域网个人电脑、服务器代理到公网的内网穿透工具，支持tcp流量转发，可支持任何tcp上层协议（访问内网网站、本地支付接口调试、ssh访问、远程桌面...）

 **漏洞版本**

Lanproxy 0.1

 **修复前：**

![](https://image.3001.net/images/20221027/1666850723_635a1fa3e6abeb6a63ab0.jpeg!small)

**修复补丁：**<https://github.com/ffay/lanproxy/commit/7787a143f9abf31ada4588e11741c92f0e145240>

![](https://image.3001.net/images/20221027/1666850954_635a208a2e06b1f890947.jpeg!small)

 **修复方式：** 如果在路径中检测到`../`，直接返回 Forbidden。

 **漏洞成因：** 对用户输入的路径、没有进行过滤、攻击者可以使用该漏洞去访问任意文件。

##  **环境搭建**

![](https://image.3001.net/images/20221027/1666851055_635a20ef46c0d0b17e137.png!small)

##  **漏洞复现**

 **拉取源码**

git clone https://github.com/ffay/lanproxy.git

 **回退到漏洞修复之前**

cd lanproxy/

git reset --hard f768adb1fca4dbcb83c16778d9f3407bb8b2f524

 **maven编译项目**

mvn package

项目编译完成后、会在项目根目录下创建distribution目录、包含服务端、客户端。

![](https://image.3001.net/images/20221027/1666851096_635a211813d532e424979.jpeg!small)

 **config.properties**

###
![](https://image.3001.net/images/20221027/1666851116_635a212c829eace7b9e6e.png!small)![](https://image.3001.net/images/20221027/1666851129_635a213976d6a031e44c2.jpeg!small)

###  **漏洞测试**

1、运行启动命令：

sh distribution/proxy-server-0.1/bin/startup.sh

2、访问http://127.0.0.1:8090端口、出现如下界面、环境启动成功：

![](https://image.3001.net/images/20221027/1666851176_635a21689b10d04c1722a.jpeg!small)3、测试Payload：/%2F..%2F/conf/config.properties  

![](https://image.3001.net/images/20221027/1666851193_635a21795ce128cc5451e.jpeg!small)

在使用Payload后、获取到config.properties 配置文件。该文件中包含：管理页面用户名、密码、以及ssl相关配置。

###  **漏洞分析**

 **开启debug模式**

Lanproxy 的启动脚本 distribution/proxy-server-0.1/bin/startup.sh 、 debug
参数可以开启调试模式。调试端口为8000。

![](https://image.3001.net/images/20221027/1666851234_635a21a2a91cbd30ab776.jpeg!small)

sh distribution/proxy-server-0.1/bin/startup.sh debug

###  **IDEA 配置**

![](https://image.3001.net/images/20221027/1666851258_635a21baa76292a3121b5.jpeg!small)

###  **动态调试**

将断点打到
src/main/java/org/fengfei/lanproxy/server/config/web/HttpRequestHandler.java#outputPages，先通过URI实例，获取到uriPath(请求路径)：/%2F..%2Fconf%2Fconfig.properties

![](https://image.3001.net/images/20221027/1666851295_635a21df4e6c47cd25013.jpeg!small)

接下来，会判断该路径是否为/，是/返回 index.html，否则返回获取到的uriPath。

PAGE_FOLDER 是获取当前程序所在的目录。

![](https://image.3001.net/images/20221027/1666851317_635a21f5614beeb7575b4.jpeg!small)紧接着、会拼接PAGE_FOLDER与uriPath。  

![](https://image.3001.net/images/20221027/1666851341_635a220de33f253dc9130.jpeg!small)然后、生成一个新的File实例，rfile，然后判读是否是目录、还会检查该文件是否存在。  

![](https://image.3001.net/images/20221027/1666851358_635a221e428d5220d0870.jpeg!small)最后，使用
RandomAccessFile() 去读取文件。到这一步，已经可以读取到 config.properties 文件。  

![](https://image.3001.net/images/20221027/1666851374_635a222e154895ea68ecf.jpeg!small)  

##  **修复建议**

安装最新Lanproxy版本，可以通过源码或者最新的安装包进行更新。

 **源码：** https://github.com/ffay/lanproxy

 **安装包：** https://file.nioee.com/d/2e81550ebdbd416c933f/

