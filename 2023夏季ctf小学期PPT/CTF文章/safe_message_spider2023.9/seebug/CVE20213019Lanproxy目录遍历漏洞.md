**作者：李安@星阑科技PortalLab  
原文链接：<https://mp.weixin.qq.com/s/XBsBNAzyciWwCRP3bMZnOw>**

## **漏洞描述**

Lanproxy 0.1 存在路径遍历漏洞，该漏洞允许目录遍历读取/../conf/config.properties来获取到内部网连接的凭据。

**Lanproxy**

lanproxy是一个将局域网个人电脑、服务器代理到公网的内网穿透工具，支持tcp流量转发，可支持任何tcp上层协议（访问内网网站、本地支付接口调试、ssh访问、远程桌面...）

## **漏洞版本**

Lanproxy 0.1

**修复前：**

![](https://images.seebug.org/content/images/2022/10/0768a176-48be-4bb6-ad82-5a4af5656767.jpeg-w331s)

**修复补丁：**<https://github.com/ffay/lanproxy/commit/7787a143f9abf31ada4588e11741c92f0e145240>

![](https://images.seebug.org/content/images/2022/10/d4d0d912-ddac-47f0-a6a9-5dbcc0de493b.jpeg-w331s)

**修复方式：** 如果在路径中检测到`../` ，直接返回 Forbidden。

**漏洞成因：** 对用户输入的路径、没有进行过滤、攻击者可以使用该漏洞去访问任意文件。

## **环境搭建**

![](https://images.seebug.org/content/images/2022/10/5b3a5718-a5df-4afc-a2fc-2e83823e0290.png-w331s)

## **漏洞复现**

**拉取源码**

git clone <https://github.com/ffay/lanproxy.git>

**回退到漏洞修复之前**

cd lanproxy/

git reset --hard `f768adb1fca4dbcb83c16778d9f3407bb8b2f524`

**maven编译项目**

mvn package

项目编译完成后、会在项目根目录下创建distribution目录、包含服务端、客户端。

![](https://images.seebug.org/content/images/2022/10/26af16af-ee65-4c15-a1b8-5077f9785118.jpeg-w331s)

**config.properties**

![](https://images.seebug.org/content/images/2022/10/f0f86420-f3ab-47a4-9e98-a51e1541e362.png-w331s)

![](https://images.seebug.org/content/images/2022/10/b92e5bb7-4746-4b7e-aa8c-cce9ee469b37.jpeg-w331s)

**漏洞测试**

1、运行启动命令：

sh distribution/proxy-server-0.1/bin/startup.sh

2、访问<http://127.0.0.1:8090>端口、出现如下界面、环境启动成功：

![](https://images.seebug.org/content/images/2022/10/4ac02fde-67eb-4864-8328-1c4bf490971b.jpeg-w331s)

3、测试Payload：/%2F..%2F/conf/config.properties

![](https://images.seebug.org/content/images/2022/10/8d8ab0d4-98dc-4590-a4a1-8a813132d6b5.jpeg-w331s)

在使用Payload后、获取到config.properties 配置文件。该文件中包含：管理页面用户名、密码、以及ssl相关配置。

**漏洞分析**

**开启debug模式**

Lanproxy 的启动脚本 distribution/proxy-server-0.1/bin/startup.sh 、 debug
参数可以开启调试模式。调试端口为8000。

![](https://images.seebug.org/content/images/2022/10/2a47f11e-83a1-42bd-8c75-90ba8a6b3867.jpeg-w331s)

sh distribution/proxy-server-0.1/bin/startup.sh debug

**IDEA 配置**

![](https://images.seebug.org/content/images/2022/10/617aa147-4a5a-494c-b29d-e5564af136a9.jpeg-w331s)

**动态调试**

将断点打到
src/main/java/org/fengfei/lanproxy/server/config/web/HttpRequestHandler.java#outputPages，先通过URI实例，获取到uriPath(请求路径)：/%2F..%2Fconf%2Fconfig.properties

![](https://images.seebug.org/content/images/2022/10/12dd18d4-44de-4945-8c24-a66001c6e37d.jpeg-w331s)

接下来，会判断该路径是否为/，是/返回 index.html，否则返回获取到的uriPath。

PAGE_FOLDER 是获取当前程序所在的目录。

![](https://images.seebug.org/content/images/2022/10/e1a993f2-9109-43c5-9510-54e5fe9baafb.jpeg-w331s)

紧接着、会拼接PAGE_FOLDER与uriPath。

![](https://images.seebug.org/content/images/2022/10/574ee9c3-c022-4705-8366-b54f47c9962f.jpeg-w331s)

然后、生成一个新的File实例，rfile，然后判读是否是目录、还会检查该文件是否存在。

![](https://images.seebug.org/content/images/2022/10/b87294a1-af27-4813-b150-28fb72bdb29d.jpeg-w331s)

最后，使用 RandomAccessFile() 去读取文件。到这一步，已经可以读取到 config.properties 文件。

![](https://images.seebug.org/content/images/2022/10/fc53bc96-c405-4aec-847a-3c449fdade00.jpeg-w331s)

## **修复建议**

安装最新Lanproxy版本，可以通过源码或者最新的安装包进行更新。

**源码：**<https://github.com/ffay/lanproxy>

**安装包：**<https://file.nioee.com/d/2e81550ebdbd416c933f/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1997/>

