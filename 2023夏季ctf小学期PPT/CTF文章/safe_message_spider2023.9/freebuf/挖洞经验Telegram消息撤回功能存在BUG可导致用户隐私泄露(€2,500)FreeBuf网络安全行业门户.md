![](https://image.3001.net/images/20190918/1568812710_5d822ea60f56c.jpg!small)

**这不是一个安全漏洞而是一个隐私问题（Privacy
Issue）。Telegram具备强大的聊天记录删除（撤回）功能，可撤回一对一或一对多（群组）聊天中在任意时间发送或分享的任意消息，但作者在研究Telegram和MTProto通信协议时发现，该功能存在隐私泄露问题（Bug），即使消息文档被发送方执行了撤回，但仍然会保存在消息接收方的移动设备存储中。以下是作者的分享。**

##  从Telegram的聊天记录撤回功能中发现问题

Telegram是一个专注于隐私保护的消息发送和聊天APP软件，在手机应用商店中其下载量已经突破1亿多次，可算是当今非常流行的社交APP应用了。

众所周知，Telegram具备一个聊天记录撤回删除功能，那就是允许用户在一对一或一对多（群组）聊天中撤回删除任何消息，重点是支持从聊天双方的设备中撤回删除。2017年，Telegram首次引入"unsend"（撤回）功能时，用户可以删除他们自己在过去48小时内发送的任何消息。但2019年3月起，按照Telegram的官方说法，为了最大程度保护用户隐私，这个"unsend"功能被拓展到了对方已接收到的任何消息中，并不受时间限制，无论过了多长时间，都允许用户在一对一或一对多（群组）聊天中撤回删除任何消息，并将其从发件人和收件人的设备中删除。也就是说，即使一年前我发送给好友的Telegram消息，现在任何时候都可以撤回，而且不会在对方手机设备中留存，完全就是“阅后即焚”的实现功能。

但我在分析Telegram和MTProto协议时发现，如果用户把消息（比如图片）发送给对方后，该图片会保存在对方用户手机设备的内部存储中，其存储路径为
**`/Telegram/Telegram Images/`** 。 **重点是**
：即使用户选择撤回发送给对方的这条图片消息，虽然在双方的聊天窗口中该条图片消息是被删除撤回了，但是，其中的图片仍然保存在对方用户手机设备的
`/Telegram/Telegram Images/`路径之下。

##  技术分析

我们假设一个Telegram消息场景，经典的Bob 和
Alice通信。如果Bob错误或手抖地把一张机密图片，不小心发给了Alice，然后Bob意识到这个问题后，他赶紧使用了Telegram的消息删除撤回功能"Also
delete for Alice" ，撤回了那条发送给Alice的机密图片消息。

![](https://image.3001.net/images/20190918/1568812659_5d822e7397814.gif!small)这就完全没事了吗？很显然，如果按照之前我们发现的问题：图片仍然存储在Alice手机设备的存储路径
`/Telegram/Telegram
Images/`之下。也就是说，在Bob撤回了消息之后，Alice完全可以通过访问该路径来再次查看那张机密图片。所以，照此来看，Telegram的消息删除撤回功能，仅是把聊天窗口中的消息删除撤回了。

同样的问题也存在于Telegram的群组中，尤其是那种成员可超过千人的超级大群"supergroups"
。假设在这种千人超级大群中，你不小心手抖在其中分享了一个并不想公开的文档，之后你使用了"delete for all members"
的Telegram消息撤回功能，就觉得万事大吉了。殊不知，Telegram的这种撤回却未真正的起到作用，接收了该消息的其它群组成员一样可以在其手机设备存储中来再次看到你的分享文档。

除此之外，我发现Telegram已经获得了用户手机设备USB存储的‘读/写/更改’权限，所以从技术上来说，删除接收用户Alice手机上的机密图片完全是可行的啊。

##  该Bug在WhatsApp上的情况

通过对比，我发现Telegram的另一竞争对手WhatsApp应用虽然同样具备"Delete for
everyone"的消息撤回功能，但就不存在上述Bug。当WhatsApp用户选择撤回消息之后，WhatsApp同时也会删除保存在接收用户手机设备`/Whatsapp/Whatsapp
Media/Whatsapp Images/`
路径下的消息文档，而且，WhatsApp同样具备对用户手机存储的‘读/写/更改’权限。所以，从这点来看，与Telegram不同的是，WhatsApp真正做到了保护用户无意泄露的隐私。

##  总结

这个Bug可能会造成更严重的影响和安全风险，目前我无法确定。至少从用户隐私方面来讲，Telegram在这个问题上处理得还不够安全可靠。该Bug在泄露用户的敏感信息的同时，也会降低用户对Telegram的使用信心。

##  BUG信息

影响版本：该Bug在Telegram for Android的最新稳定版(5.10.0 (1684)) 上有效，未对Telegram for
iOS和Telegram for Windows版本APP做过测试，但这些版本估计也存在该Bug。

责任披露：经向security@telegram.org上报了该问题后，Telegram非常重视，在后续的Telegram
5.11版本中修复了该Bug，并奖励了我€2,500欧元。

其它解决方法：可使用Telegram的加密聊天"New Secret Chat"功能，就不会留下任何消息痕迹了。

> 参考：上述Bug被分配了漏洞编号
> [CVE-2019-16248](https://nvd.nist.gov/vuln/detail/CVE-2019-16248)。
>
>
> PoC视频：[https://www.*******.com/watch?v=_S64ApkqH1Y](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=_S64ApkqH1Y)

***参考来源：[inputzero](https://www.inputzero.io/2019/09/telegram-privacy-fails-again.html)，clouds编译整理，转载请注明来自FreeBuf.COM**

  

