**01 前言**

通常情况下用户认为将数据和业务分离，只将业务A服务器对外开放，让数据服务器B不对外开放，那么即使用户的A服务器失陷，数据依然保存在内网中，不会被黑客直接访问。用户认为这种方式可以尽可能降低风险内网中其它终端资产的受害风险。如下图：

![777fcd3bb91145338451c28a92d5a3e8.png](https://image.3001.net/images/20221025/1666696452_6357c50426a8b5bab31f9.png!small)

今天介绍的这款渗透工具，在已经获取到服务器A的shell权限前提下，可以直接穿过防火墙限制，在服务器A上开通信道，访问服务器B的相关信息。

 **02 攻击复现**

 **环境准备**

本次攻击复现需要三台机器，一台作为攻击机名为attacker（X.X.100.190）、一台名为跳板机victim1（X.X.100.203）、一台名为目标机器victim2（X.X.43.109）。

  *  **目前的环境是attacker可以直接访问100.203的webshell木马，如下图：**

![4b760eead295425bafb7844735889ad8.png](https://image.3001.net/images/20221025/1666696452_6357c504b4834506f6189.png!small)

  *  **attacker无法直接访问victim2的web服务。**

![4a3dc447fba34d20b0c9991dd0c9376b.png](https://image.3001.net/images/20221025/1666696453_6357c5054a62ed3d65e46.png!small)

  *  **但是victim1可以正常访问victim2的web服务。**

![815a1ee00b6c48f0bbd26b61e364511e.png](https://image.3001.net/images/20221025/1666696453_6357c505d1bf3a63bb900.png!small)

 **工具搭建**

首先需要在github上面找到reGeorg项目并下载下来。相关链接如下：

 **https://github.com/sensepost/reGeorg**

![165dc933071c4bd29e26ea4eeb460939.png](https://image.3001.net/images/20221025/1666696454_6357c5066a2685d14efb9.png!small)

将tunnel.jsp上传到跳板机victim1上面。

将reGeorgSocksProxy.py下载到攻击机上面，并且在攻击机上面搭建代理privoxy，设置监听端口为8118，转发端口为9999。如下图：

![0ea343df37c043029e57b1d57953ecb5.png](https://image.3001.net/images/20221025/1666696455_6357c5070bc24022e16ed.png!small)

此时开始在attacker上面尝试连接victim1（100.203）的webshell木马，如下图：

![2e0d78708915443cbbe3abbf910cd110.png](https://image.3001.net/images/20221025/1666696455_6357c507c5834b0cda0bc.png!small)

在attacker设备上面使用curl
//127.0.0.1:8080/tunnel.jsp命令直接获取victim1的本地tunnel.jsp文件，如下图：

![49c100d6f30b4f9e95582b5dc2753917.png](https://image.3001.net/images/20221025/1666696456_6357c5084d3e7e2e71bdd.png!small)

可以发现，此时attacker已经可以访问victim1使用127.0.0.1和X.X.100.203了。

继续通过attacker访问victim2，效果如下图：

![0ffc56fd0a0145808371ed0a2e69351e.png](https://image.3001.net/images/20221025/1666696456_6357c508cb32508b73c28.png!small)

该现象说明，此时在攻击机上的所有http和https服务请求，都会直接被代理到victim1上面进行执行，X.X.43.109的8443端口的服务器实现了attacker对victim2的远控。

 **原理解析**

![b2f5c0b4c6794a9bac1c2fc04ec8aaaf.png](https://image.3001.net/images/20221025/1666696457_6357c5096c06ced01f0a4.png!small)

用户输入命令curl http://127.0.0.1:8080/tunnel.jsp

被privoxy代理工具代理到regeorg工具里面，regeorg工具会将上面命令产生的报文作为请求体，发送给victimA。报文如下图：

![bd13023cb18c470e8fb9a1323f7ad6d8.png](https://image.3001.net/images/20221025/1666696457_6357c509ec86e58466c4d.png!small)

服务器victimA收到攻击机attacker的请求以后，tunnel.jsp的forward模块会直接将其转发到内网环境victimB中。

tunnel.jsp的read模块再将victimB的内容转发到attacker攻击机上，如下图所示：

![68799a6821324540818fa7dac426b960.png](https://image.3001.net/images/20221025/1666696458_6357c50a8d203419f788a.png!small)

Regeorg工具会将上述红框的内容进行处理，返回给前端命令显示页面。

 **03 防护措施**

目前聚铭网络流量智能分析审计系统 （iNFA）已经支持对该工具的检测，如下图：

![d2720445de5345bb94b4b51aa46ab652.png](https://image.3001.net/images/20221025/1666696459_6357c50b43305648727e5.png!small)

iNFA可实时监控内网环境，避免因为内网安全的疏忽，导致内部资产失陷。

