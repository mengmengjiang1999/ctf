![](https://image.3001.net/images/20191222/1576975743_5dfebd7f7c105.jpg!small)

**如果你一走进某个房间就能让里面的所有iPhone或iPad设备无法使用，会怎么样？是不是听起来非常邪恶？有什么好的方法让那些老是低头刷苹果手机的人停下来？**

最近作者发现了一个存在于iOS系统中的DoS问题，暂且把它命名为AirDoS（隔空DoS），该bug能让攻击者一直用AirDrop共享弹出窗口向附近的iOS设备发送垃圾消息。此共享弹出窗口会阻止用户界面，因此设备所有者将无法在设备上执行任何操作，只有选择弹出窗口上的接受或是拒绝按钮，而且弹出窗口会反复再现，即使设备在锁定后，也一样会持续发生。

![](https://image.3001.net/images/20191222/1576975597_5dfebcedaa7df.gif!small)该Bug受AirDrop接收设置限制，也就是说如果你把AirDrop设置为Everyone，那么周围任何人都可能会攻击你，但如果设置为“仅限联系人”（Contacts
Only），则只有你通讯录里面的人才能对你发起攻击。如果有人在附近发起这种攻击，那么你就无法使用iPhone或iPad设备了，但我不确定这种攻击效果在飞机上如何。

大多数情况下，这种攻击者很难识别，除了避开攻击者之外，你可以把AirDrop/WiFi/Bluetooth三者都关了。如果你未禁用控制中心的话，可以从锁屏界面访问控制中心来关闭AirDrop/WiFi/Bluetooth，当然还可以让SIRI来执行WiFi/Bluetooth的关闭。另外就是重启设备，也会在攻击持续发生前，能有稍许时间关掉AirDrop。要防止这种攻击的话，仅在需要AirDrop的时候打开它，而且不要把它的接收限制设置为"Everyone"。

我于2019年8月向Apple上报了该漏洞，之后苹果在后续的iOS
13.3版本中进行了修复，在其中加入了一个速率限制，即只要用户拒绝了同一用户3次隔空投送后，就会自动拒绝其它后续请求。

##  PoC

我在GitHub上发布了[该Bug的PoC脚本](https://github.com/KishanBagaria/AirDoS)，为了减少公众安全影响，该PoC仅只支持AirDrop设置为仅限联系人"Contacts
Only"的设备。PoC中加入了OpenDrop支持，也是由于OpenDrop的启发，我尝试发现了该问题。

OpenDrop是一个命令行工具，它允许你在设备之间通过Wi-Fi直接共享文件。它的独特之处在于，它与Apple的AirDrop兼容，AIrDrop功能允许用户与运行iOS和macOS的Apple设备共享文件。目前，OpenDrop只支持发送给所有人都可发现的Apple设备，因为默认的“仅限联系人”模式需要Apple签发的证书。

这是一个简单的Bug，可以用opendrop构造一个简单的无限循环命令来实现：

    
    
    while true; do opendrop send -r 0 -f totally-random-file; done

macOS

macOS的AirDrop共享和iOS有点不同，而且不会阻塞用户界面。虽然攻击者可以一直用上述Bug向受害者发送大量垃圾请求消息，但是由于无法拥塞用户界面，所以受害者用户可以选择关闭AirDrop或WiFi/Bluetooth来阻止攻击。但在macOS
Catalina 10.15.2中，该反复发送垃圾共享消息的问题已经得到修复。

##  漏洞上报和处理进程

> 2019.8.19 向苹果上报该Bug
>
> 2019.10.3 咨询苹果处理情况，苹果回复“仍在调查”
>
> 2019.11.14 苹果告知已在下一版本更新中对该问题加入了缓解措施，但无法获得CVE编号，希望我测试验证
>
> 2019.11.14 经过测试我确定问题修复
>
> 2019.12.10 iOS 13.3发布 漏洞公开

***参考来源：[kishanbagaria](https://kishanbagaria.com/airdos/)，clouds 编译整理，转载请注明来自
FreeBuf.COM**

  

