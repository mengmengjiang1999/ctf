## 背景

2020年4月5日晚，消息称深信服的VPN设备存在漏洞被黑客组织用来执行有限的针对性攻击。目前，这一信息已经得到深信服的官方确认。内容详见：

<https://mp.weixin.qq.com/s/lKp_3kPNEycXqfCnVPxoDw>

经奇安信对相关细节分析确认，至少有2波不同来源的攻击者执行过类似路径的攻击，已观察到少量受影响用户。先将奇安信对可能的攻击路径分析和处置建议通告如下。

## 攻击路径

1、 攻击者利用深信服VPN设备的已知远程漏洞或弱口令获取对设备的控制。

2、 修改VPN的升级配置文件，篡改升级包下载相关的配置信息，指向攻击者控制的恶意文件和对应文件MD5。

3、 装有深信服VPN客户端的电脑更新程序检测到有更新，会调用命令行参数升级，命令行参数如下：

从设备取回来配置文件和更新包文件后，恶意代码会得到执行。

4、 攻击者电脑上植入了木马文件，使用的路径如下：

%userprofile%\appdata\roaming\sangfor\ssl\sangforupd.exe

## 处置建议

1\. 厂商称影响的设备版本为SSL
VPN设备版本M6.3R1和M6.1，用户如果使用了受影响的VPN设备，建议用户下线替换设备，检查该设备是否已经被利用，如果没有被利用，则按参考链接中深信服公告所建议联系厂商处置。清查网络安全设备日志，检查是否已经渗透到相应使用VPN的客户端或者是否进入到内网；

2\. 天擎和天眼用户基于我们在IOCs节中给出的IOC进行受攻击迹象排查，或报送如下路径的文件：

%userprofile%\appdata\roaming\sangfor\ssl\sangforupd.exe

到奇安信对口销售人员或对接运营人员，也可发送到邮箱
[ti_support@qianxin.com](mailto:ti_support@qianxin.com) ，我们会反馈检测判定结果。

## 参考链接

<https://mp.weixin.qq.com/s/lKp_3kPNEycXqfCnVPxoDw>

## IOCs

文件MD5

a32e1202257a2945bf0f878c58490af8  
c5d5cb99291fa4b2a68b5ea3ff9d9f9a  
967fcf185634def5177f74b0f703bdc0

IP

103.216.221.19

