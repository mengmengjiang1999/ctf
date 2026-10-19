**近日，安全专家再度爆出一个存在于Adobe Flash Player中的新的0day漏洞，此次发现源于一起针对俄罗斯的医疗保健机构的网络袭击事件。**

该漏洞被编号为CVE-2018-15982，攻击者可通过漏洞在目标用户的计算机上执行任意代码，最终可取得系统的完全控制权。漏洞最早在一个Office的恶意文档中被发现，目前漏洞细节已上传至了VirusTotal。

## 漏洞原理

该漏洞通过在word文档中嵌入一个Flash Active X的控件来实现，当用户打开文档时，会触发该漏洞导致Flash播放器出现故障。

但研究人员解释，Office文件（22.docx）和其中的Flash漏洞本身都不包含控制系统的最终有效负载。而真正起到作用的部分反而是隐藏在其中的一个图像文件（scan042.jpg），该文件本身就是一个存档文件，与word文档一起打包存在压缩包中，然后通过鱼叉式网络钓鱼电子邮件分发出去，视频演示如下：

用户收到并打开文档后，Flash漏洞利用程序便会在系统上执行命令来取消归档映像文件并运行恶意程序（backup.exe），该程序收到VMProtect的保护，并会自主安装后门程序。随后可获得用户系统中如下权限：

1.监控用户活动（键盘或鼠标记录）；

2.收集系统信息并将其发送至远程命令和控制（C&C）服务器；

3.执行shellcode；

4.将PE加载至内存中；

5.下载文件；

6.执行代码；

7.自我“毁灭”。

来自Gigamon Applied Threat
Rearch的研究人员将该恶意软件命名为“操作毒针”，但目前并没有确定该软件或攻击行为的来源。然而根据此前针对俄罗斯的攻击事件来看，研究人员认为攻击者可能来自乌克兰。

该漏洞会对Adobe Flash Player 31.0.0.153以及其之前的版本产生影响，Google Chrome、Microsoft
Edge以及Internet Explorer 11等浏览器均会受到影响，Adobe Flash Player
31.0.0.108之前版本的安装程序也会受到影响。

研究人员已于11月29日将漏洞上报与Adobe公司，目前也已发布了针对Windows、macOS、Linux和Chrome等系统的升级补丁。

 ***参考来源：[thehackernews](https://thehackernews.com/2018/12/flash-player-vulnerability.html)，Karunesh91编译，转载请注明来自FreeBuf.COM**

