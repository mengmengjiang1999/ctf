# NPS的介绍和使用

## NPS介绍

nps是一款轻量级、高性能、功能强大的内网穿透代理服务器。目前支持tcp、udp流量转发，可支持任何tcp、udp上层协议（访问内网网站、本地支付接口调试、ssh访问、远程桌面，内网dns解析等等……），此外还支持内网http代理、内网socks5代理、p2p等，并带有功能强大的web管理端。

NPS的下载地址：`https://github.com/ehang-io/nps/releases`

![图片.png](https://image.3001.net/images/20230825/1692917550_64e7df2e373caab68d139.png!small)

NPS的使用手册：`https://ehang-io.github.io/nps/#/`

![图片.png](https://image.3001.net/images/20230825/1692917565_64e7df3d0dd9d1e054e23.png!small)

NPS也分为客户端和服务端两个,我们这里举个列子，我们现在正在进行渗透攻击内网服务器，如果我们想要把内网机器穿透到我们位于公网的机器上，那么 客户端
Client 就是运行在内网中的机器上，而 服务端 Server 就是运行在公网的机器上

![图片.png](https://image.3001.net/images/20230825/1692917576_64e7df48764f67c323840.png!small)

## NPS启动

假设现在我们遇到了攻防场景，需要将一台位于内网的机器B代理到位于官网的黑客机器A上，场景如下：

![图片.png](https://image.3001.net/images/20230825/1692917588_64e7df54081440b64b92c.png!small)

### 服务端启动

NPS Server 服务端工具打开以后，有如下几个文件：

![图片.png](https://image.3001.net/images/20230825/1692917601_64e7df610cd294adfc8ed.png!small)

我们输入如下的命令打开 NPS Server服务端：

    
    
    nps.exe
    

![图片.png](https://image.3001.net/images/20230825/1692917612_64e7df6c1a26dc699e9a4.png!small)

然后我们就可以在浏览器输入当前运行NPS Server服务端的机器的8080端口，就可以进入NPS的配置界面

    
    
    http://IP:8080/login/index
    

![图片.png](https://image.3001.net/images/20230825/1692917625_64e7df79aab6e9010e087.png!small)

默认账号是：admin，默认密码是：123，输入账号和密码后，我们点击登陆，就会进入NPS的配置界面

![图片.png](https://image.3001.net/images/20230825/1692917639_64e7df870da4b6eb53666.png!small)

我们点击客户端，点击新增按钮

![图片.png](https://image.3001.net/images/20230825/1692917652_64e7df943691c0288ff95.png!small)

可以输入验证用的用户名和认证密码，由于我们这里仅用于展示测试功能，这一步就略过了，点击新增

![图片.png](https://image.3001.net/images/20230825/1692917665_64e7dfa1eef44bbada1f3.png!small)

如图完成添加后的效果如图所示

![图片.png](https://image.3001.net/images/20230825/1692917677_64e7dfadd25a5e5cbc79d.png!small)

我们点击隧道，配置代理隧道

![图片.png](https://image.3001.net/images/20230825/1692917689_64e7dfb94d165d44fd216.png!small)

然后我们点击新增按钮

![图片.png](https://image.3001.net/images/20230825/1692917700_64e7dfc47a41c18c1cf52.png!small)

选择隧道的代理模式和端口，NPS所支持的代理模式有很多，包括
TCP、UDP、SOCK5、HTTP、P2P和私密代理，这里我们选择SOCK5代理，服务端端口为5000，点击新增

![图片.png](https://image.3001.net/images/20230825/1692917713_64e7dfd11d66a1c05eee8.png!small)

到此，我们的隧道搭建好了

![](https://image.3001.net/)

