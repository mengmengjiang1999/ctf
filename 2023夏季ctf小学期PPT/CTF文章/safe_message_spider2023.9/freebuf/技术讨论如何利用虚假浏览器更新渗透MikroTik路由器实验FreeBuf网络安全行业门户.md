## 写在前面的话

**MikroTik是拉脱维亚一家从事路由器和无线ISP系统开发的企业，在过去几个月中处理了许多影响其产品操作系统的漏洞。2018年4月，研究人员发现RouterOS的一个关键漏洞，攻击一直在以惊人的速度发生，当发现一种新发现的CVE-2018-14847开发技术时，情况更糟。问题在于，尽管供应商提供了安全修复程序，但大量的MikroTik路由器仍然没有打补丁并成为自动攻击的牺牲品。犯罪分子迅速利用概念证明代码在短时间内破坏数十万台设备。**

去年夏天，SpiderLabs的研究人员通过被黑客入侵的MikroTik设备发现了可能是最大的恶意Coinhive活动，现在已经演变成一个更广泛的问题。在最新的攻击活动中，攻击者利用虚假的浏览器更新页面来入侵路由器。当运行恶意更新时，研究人员会解包代码到计算机中，计算机可以扫描网络中其他有漏洞的路由器并尝试利用。  

## 可疑的浏览器更新

安全研究人员@VriesHd首先发现一个尝试用社会工程技术来入侵有漏洞的路由器的活动。运行受影响的MikroTik路由器的网络提供商会将关于浏览器的老版本更新重定向给终端用户。

![1.png](https://image.3001.net/images/20181125/1543109834_5bf9fcca40e1c.png!small)根据Censys的搜索，一共有11000个被入侵的MikroTik设备提供该虚假下载页面：

![2.png](https://image.3001.net/images/20181125/1543109843_5bf9fcd3715c5.png!small)该浏览器根系是从一个FTP服务器下载的，如下图所示：

![3.png](https://image.3001.net/images/20181125/1543109850_5bf9fcda1fd5f.png!small)有趣的是，此IP地址也被列为免费和开放的Web代理：

![4.png](https://image.3001.net/images/20181125/1543109857_5bf9fce1970ac.png!small)

## Payload分析

### 行为分析

Payload会伪装成一个名为upd_browser的安装器。

![5.png](https://image.3001.net/images/20181125/1543109864_5bf9fce809e94.png!small)当我们运行它时，它会弹出一个错误：

![6.png](https://image.3001.net/images/20181125/1543109869_5bf9fced688b3.png!small)但如果抓取网络流量，可以看出有很多不同的IP地址尝试连接8291端口（8291是通过winbox应用管理MicroTik路由器的默认端口）：

![7.png](https://image.3001.net/images/20181125/1543109876_5bf9fcf402664.png!small)

### Unpack

释放的payload是一个比较大的可执行文件（7.25MB）。该小节的header和可视化如下图：

![8.png](https://image.3001.net/images/20181125/1543109882_5bf9fcfaa27a7.png!small)通过查看section名，可以看出其打包了一个简单的packer：UPX。重复部分说明提取出的内容太多了。在进行下一步检查后，研究人员发现其将一个python
DLL和其他相关文件解包到%TEMP%文件夹，然后加载这些文件。很容易猜测出exe文件其实是一个python脚本。

![9.png](https://image.3001.net/images/20181125/1543109888_5bf9fd00d529c.png!small)脚本中的entry
point名为upd_browser。反编译脚本发现恶意软件的核心是两个python脚本：upd_browser.py和ups.py。

## 脚本分析

该模块的主要功能非常简单：

![10.png](https://image.3001.net/images/20181125/1543109895_5bf9fd07a721b.png!small)我们可以看到，错误弹出窗口是硬编码的,它不会警告任何实际错误，而是用作诱饵。恶意软件通过查询使用合法服务IP
Logger制作的跟踪器的硬编码地址来记录受害者的IP地址。跟踪器采用一个像素大小的图像形式：

![11.png](https://image.3001.net/images/20181125/1543109902_5bf9fd0ed4bb7.png!small)之后，该地址会在定义的时间间隔内定时查询。最重要的操作在名为“scan”
的函数中执行，该函数部署在多个并行线程中（最大线程数定义为thmax =
600）。函数生成伪随机IP地址并尝试在上述端口8291上连接到它们中的每一个。当连接尝试成功时，它尝试另一个连接，这次是在56778范围内的随机端口上5688.当这个失败时，就继续漏洞利用：
![12.png](https://image.3001.net/images/20181125/1543109910_5bf9fd1640f48.png!small)函数poc是指通过已知的漏洞来感染路由器。开始时尝试利用路径遍历漏洞CVE-2018-14847来获取凭证：![13.png](https://image.3001.net/images/20181125/1543109918_5bf9fd1ed25cb.png!small)user.dat文件应该是M2格式，因此脚本附带一个内置的解析器（函数load_file）：

![14.png](https://image.3001.net/images/20181125/1543109926_5bf9fd263fd0f.png!small)如果从user.dat文件中检索密码成功，它会解密凭据并使用它们来创建后门：具有随机生成密码的帐户。它还设置由路由器执行的计划任务。调度程序中设置的脚本是从硬编码模板生成的（此处提供的已清理版本）。它的作用是操纵路由器的设置并设置加载CoinHive矿工的错误页面。错误页面可以放在两个位置：`“
webproxy/error.html”`或`“flash/webproxy/error.html”`。

![15.png](https://image.3001.net/images/20181125/1543109934_5bf9fd2e14ad5.png!small)只要用户尝试查看拒绝访问的URL，就会向用户显示这样的页面。但路由器中配置的恶意脚本是基于HTTP请求错误。伪造的错误页面是wile欺骗原始流量，以iframe方式展示请求的页面。所以当用户浏览大多数web时并不会注意到这一变化。比如：

![16.png](https://image.3001.net/images/20181125/1543109941_5bf9fd356bf2c.png!small)

## 缓解措施

MikroTik用户应及时对路由器打补丁升级。MikroTik下载页面中说明了如何对RouterOS进行升级。意识到这些漏洞存在且容易被利用是很重要的，因为修补路由器不是很多人习惯做的事情。但是，在许多情况下，用户将无法这样做，除非他们的Internet服务提供商在上游为他们执行此操作。通过这个社工工程手段，我们看到了犯罪分子如何试图感染普通用户并利用他们的计算机扫描互联网以寻找易受攻击的路由器。这种技术很聪明，因为这样的努力需要时间和资源才能有效。恶意软件业务客户和高级消费者用户受到保护，免受此威胁，因为我们的反恶意软件引擎会实时检测并阻止此虚假浏览器更新：

![17.png](https://image.3001.net/images/20181125/1543109948_5bf9fd3c2059b.png!small)

***参考来源：[malwarebytes](https://blog.malwarebytes.com/threat-analysis/2018/10/fake-browser-update-seeks-to-compromise-more-mikrotik-routers/)，周大涛编译，转载请注明来自FreeBuf.COM**

