4月6日，深信服官方发表《关于境外非法组织利用深信服SSL VPN设备下发恶意文件并发起APT攻击活动的说明》（详见参考文献），称境外黑客组织利用其SSL
VPN设备发起恶意攻击，绿盟科技威胁情报中心对该事件密切关注，对该事件做了整体的梳理和分析，提请广大用户关注自己的SSL
VPN设备，注意自查（受该事件影响的深信服SSL VPN设备版本号为M6.3R1、M6.1版本），并及时更新相关补丁。

绿盟科技威胁情报中心已支持对该事件的检测（网址：<https://nti.nsfocus.com>）。

# 事件概况  

境外黑客组织通过非法手段控制部分深信服SSL VPN设备，并利用客户端升级漏洞（本次漏洞为SSL
VPN设备Windows客户端升级模块签名验证机制的缺陷）下发恶意文件到客户端，从而进行APT攻击活动，绿盟威胁情报中心已支持对该事件的IOC检测，详情如下：

涉及到该事件的C&C服务器的威胁知识图谱如下：

![图片1.png](https://image.3001.net/images/20200407/1586237746_5e8c1132797a1.png!small)![图片2.png](https://image.3001.net/images/20200407/1586237746_5e8c11327c4fd.png!small)

涉及到该事件的几个典型恶意文件详情如下：

![图片3.png](https://image.3001.net/images/20200407/1586237817_5e8c1179be161.png!small)![图片4.png](https://image.3001.net/images/20200407/1586237817_5e8c1179bf314.png!small)![图片5.png](https://image.3001.net/images/20200407/1586237817_5e8c1179ca99a.png!small)

# 处置建议  

1、
依照深信服官方给出的处置建议（详见参考文献），建议用户限制外网或非信任IP访问VPN服务器的4430控制台管理端口，阻断黑客针对VPN服务器管理后台进行的攻击；并尽快从官方渠道安装相关补丁

2、 使用绿盟威胁情报中心发布的IOC进行检测，采用专杀工具对木马文件彻底查杀。

# 相关威胁情报  

完整IOC（持续更新中）：

1、C&C：103.216.221.19

2、文件名：SangforUD.EXE，MD5：a32e1202257a2945bf0f878c58490af8,

3、文件名：SangforUD.EXE，MD5：967fcf185634def5177f74b0f703bdc0

4、文件名：SangforUD.EXE，MD5：c5d5cb99291fa4b2a68b5ea3ff9d9f9a

5、文件名：e58b8de07372b9913ca2fbd3b103bb8f.virus，

MD5：e58b8de07372b9913ca2fbd3b103bb8f

6、文件名：m.exe，MD5：429be60f0e444f4d9ba1255e88093721

7、文件名：93e9383ae8ad2371d457fc4c1035157d887a84bbfe66fbbb3769c5637de59c75，

MD5：18427cdcb5729a194954f0a6b5c0835a

8、文件名：SANARISOR.EXE，MD5：a93ece16bf430431f9cae0125701f527

# 参考文献

<https://mp.weixin.qq.com/s/lKp_3kPNEycXqfCnVPxoDw>

