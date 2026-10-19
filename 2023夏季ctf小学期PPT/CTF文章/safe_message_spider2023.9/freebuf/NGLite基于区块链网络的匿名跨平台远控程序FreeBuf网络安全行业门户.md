***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

## 0x00 敬告

本文所阐述内容仅供技术探讨及研究，所有环境均为实验环境，不存在任何违反破坏计算机行为。文中所有工具仅供研究使用，产生一切后果由使用者自负。

该远控程序是方便运维人员使用的运维工具，请大家合理使用，产生一切非法行为及后果由使用者自负。

原创文章，转载请注明原作者及本文链接。

@[TenguG](https://www.t00ls.net/members-profile-13417.html)@[Maka8ka](https://github.com/Maka8ka)

先上项目地址:<https://github.com/Maka8ka/NGLite>

## 0x01 前言

随着网络技术革新，防火墙杀软的层层迭代，远控木马发展了良久，从最早的基于TCP开端口正向链接的木马，到后来有基于TCP的C/S端的反向链接木马，再到各类变种的HTTP/HTTPS/DNS木马。

目前用的最多的cobaltstrike/msf，免杀多要对shellcode进行免杀，各类加载器，进程注入等绕过杀软。但绕过杀软最好的办法就是自己写一个远控程序。

写远控之前我们就要思考一下目前的cobaltstrike和msf在回连的时候主要特征是什么，行为特征？回连特征？包含回连IP/域名/CDN？行为特征可通过自己写远控客户端进行规避，IP/域名/服务器是不是都得使用实名信息/付款方式进行购买，匿名性大大降低。总有暴露的风险。

那么如何实现在无IP/域名/服务器的情况下实现无需任何实名信息的远控才是本文主要探讨的问题。所以需要思考一下，如何无IP/域名实现穿透？P2P？和区块链又有啥关系

## 0x02 基于NKN区块链网络的P2P网络

![Untitled.png](https://image.3001.net/images/20210713/1626162497_60ed454114b165b75c0ab.png!small)

上图来自：[https://nkn.org/wp-content/uploads/2020/12/NKN概览.pdf](https://nkn.org/wp-content/uploads/2020/12/NKN%E6%A6%82%E8%A7%88.pdf)

所有客户端/服务端均直接链接NKN的官方节点/由用户加入NKN网络的挖矿节点，所有节点均只知道相邻的邻居节点。此时客户端和服务端在网络中几乎对等。服务端在无公网IP端口的情况下，仅需能链接外网，有外网访问的权限，即可作为被连接的对象。

![Untitled
1.png](https://image.3001.net/images/20210713/1626162527_60ed455f1177c985409a1.png!small)

上图来自<https://github.com/nknorg/nkn-sdk-go>

利用NKN的sdk即可快速实现具有消息传送功能的客户端，由于在P2P网络中无明显的客户端/服务端区别，在之后的文章中姑且称C2控制端，和受控端。

## 0x03 一般远控执行流程

![Untitled
2.png](https://image.3001.net/images/20210713/1626162544_60ed457077ae3c22e8bd2.png!small)

## 0x04 NGLite执行流程

![Untitled
3.png](https://image.3001.net/images/20210713/1626162567_60ed4587a62869c1e2916.png!small)

透过NKN 的网络，可以实现一个匿名的P2P群组，类似于聊天频道，每个发送端可直接对目的端发送消息，消息经过nkn网络中的不同节点进行传送。

## 0x05 工具优势&劣势

理论上完全的匿名性，当然要是有人监测并分析了所有中间节点除外，目前节点约8W个

无需任何公网资源，只需要通信主机能上网即可

无需实名购买IP/域名/服务器/CDN等等资源

目前免杀性能优

连接稍多，体积较大，大家可通过upx等进行压缩

## 0x06 工具介绍及原理

目前功能单一，仅提供命令执行功能

相较于demo版增加了自定义频道/群组功能，同学们可以自己生成自己的随机频道，在自己的专属频道中进行通信，也可以团队协作，只需要将频道地址告诉你的小伙伴，在小伙伴的机器上同时运行controller指定-g即可。

目前支持参数

    
    
    控制端
    -n new 生成新的频道/群组
    -g 9e8124591f55d27b48ba907f2ad39e790ec589b3942dec2a19e7c2a96b751922 指定9e8124591f55d27b48ba907f2ad39e790ec589b3942dec2a19e7c2a96b751922频道
    $mac$ip shell 对执行主机发送shell命令
    
    被控端
    -g 9e8124591f55d27b48ba907f2ad39e790ec589b3942dec2a19e7c2a96b751922 指定9e8124591f55d27b48ba907f2ad39e790ec589b3942dec2a19e7c2a96b751922频道
    

运行示例

![Untitled.png](https://image.3001.net/images/20210713/1626162644_60ed45d4d606590e528a5.png!small)

免杀效果

![detection.png](https://image.3001.net/images/20210713/1626162706_60ed46127f3cdae6ae854.png!small)

项目地址:<https://github.com/Maka8ka/NGLite>

@[TenguG](https://www.t00ls.net/members-profile-13417.html)@[Maka8ka](https://github.com/Maka8ka)[MyBlog链接](https://maka8ka.github.io/post/nglite-%E5%9F%BA%E4%BA%8E%E5%8C%BA%E5%9D%97%E9%93%BE%E7%BD%91%E7%BB%9C%E7%9A%84%E5%8C%BF%E5%90%8D%E8%B7%A8%E5%B9%B3%E5%8F%B0%E8%BF%9C%E6%8E%A7%E7%A8%8B%E5%BA%8F/)

