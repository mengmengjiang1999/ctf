## 前言

**恶意软件开发者总是会寻找新的方法来躲避安全检测，并创造更多的利益。近期，研究人员又发现了一种针对macOS用户的新型攻击技术，接下来我们一起打开虚拟机，看看这一次攻击者又想出了什么高招！**

## 老把戏，新玩法！

SearchPageInstaller（SPI）是一款恶意广告软件，它从2017年就已经开始活跃了，不过在研究人员检测到的最新样本中，我们发现它开始使用[mitmproxy](https://mitmproxy.org/)了，而且这个版本已经是好几个月之前的版本了：

![SearchPageInstaller](https://image.3001.net/images/20181120/1542688952_5bf390b8ef25a.png!small)

这款恶意软件使用了一种新型的方法来通过广告赚取收益，普通的恶意广告软件主要使用的是重定向浏览器页面的方式，但SPI会向用户搜索结果页面的HTML代码顶部注入恶意广告。首先，攻击者需要在受感染主机中启用HTTP和HTTPS代理，系统设置中网络管理面板的代理标签页配置就是证据：

![代理标签页配置](https://image.3001.net/images/20181120/1542688957_5bf390bd9cec8.png!small)

然后在命令行界面通过命令`system_profiler SPNetworkDataType | grep 'Proxy Enabled'`来启用配置：

![启用配置](https://image.3001.net/images/20181120/1542688964_5bf390c4c246b.png!small)

在对受SearchPageInstaller感染的Web页面代码进行审计之后，我们可以看到SPI注入的恶意代码，这里它会替换掉其他所有的广告：

![替换掉其他所有的广告](https://image.3001.net/images/20181120/1542688970_5bf390caabc39.png!small)

脚本源来自于chaumonttechnology.com，VirusTotal的两个检测引擎都已经将该主机标记为了恶意主机：

![恶意主机](https://image.3001.net/images/20181120/1542688977_5bf390d162ea2.png!small)

## 中间人攻击

关于Web代理，SPI使用了mitmproxy（一款开源的HTTPS代理工具）和脚本inject.py来向Web页面的代码注入恶意脚本代码：

![注入恶意脚本代码](https://image.3001.net/images/20181120/1542688991_5bf390df7ac92.png!small)

这是因为mitmproxy能够在客户端与服务器端之间以“中间人”的形式来工作，然后通过创建伪造的证书来让客户端以为它就是服务器，让服务器以为它就是客户端。当用户不小心输入了管理密码之后，SPI的代码将会自动安装mitmproxy
CA证书，下面是我们在macOS 10.14 Mojave上检测到的攻击场景：

![检测到的攻击场景](https://image.3001.net/images/20181120/1542689000_5bf390e81da3e.png!small)

授权之后，mitmproxy CA证书以及其他所需的证书都可以通过中间人攻击来捕捉到，并且会全部写入到隐藏的~/mitmproxy目录中：

![写入到隐藏的~/mitmproxy目录](https://image.3001.net/images/20181120/1542689007_5bf390ef5876e.png!small)

## 恶意软件检测

正如我们所看到的那样，SearchPageInstaller启动之后，它首先会尝试获取安装新证书的权限。接下来，它会尝试修改目标主机上的网络代理设置，这个操作需要管理员权限，因此它会弹出另一个认证请求窗口：

![认证请求窗口](https://image.3001.net/images/20181120/1542689023_5bf390ff38f9d.png!small)

下面给出的是整个攻击的实现过程，我们可以看到恶意软件创建的每一个进程以及对应的生成事件：

![每一个进程以及对应的生成事件](https://image.3001.net/images/20181120/1542689032_5bf391083a34a.png!small)

右侧面板的放大视图可以查看当前选定的事件，比如说我们这里选中的就是mitmdump代码执行情况[20]，它是mitmproxy提供的命令行工具。

Mitmdump工具可以查看、记录和发送HTTP流量。我们可以看到进程调用inject.py脚本并向其提供参数。这些命令可以让mitmproxy在通过HTTPS连接时忽略那些能够匹配正则表达式的特定域名，这样可以绕开那些采用了证书绑定保护机制的特定流量。

接下来，Mitmdump进程会生成一个shell进程[23]，并调用uname工具[21]来获取目标设备的架构信息。

下面给出的是每一个进程的网络通信流量：

![网络通信流量](https://image.3001.net/images/20181120/1542689042_5bf39112b49f5.png!small)

这样一来，当攻击者拿到了目标设备的基础配置之后，就可以在感染完成或攻击结束之后将目标设备还原为之前的配置。

## 总结

实际上，在对SPI的行为进行了分析之后，我们认为它是一个相对来说低风险的恶意广告活动，不过由于它能够修改HTTP明文数据以及加密流量，因此我们仍然需要严肃对待它。需要注意的是，目前很多反病毒软件可能仍然允许mitmproxy进程运行，因为很多开发人员会将其当做一种合法软件来使用。

 *** 参考来源：[sentinelone](https://www.sentinelone.com/blog/inside-searchpageinstaller-macos-malware-deploys-mitm-attack/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

