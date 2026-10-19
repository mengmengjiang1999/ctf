McAfee 的移动研究人员最近在一款应用程序中发现了新的 Android 恶意软件，旨在增加 Instagram 关注者。

Instagram 已经成为一个拥有超过 10 亿月活用户的平台。Instagram
的许多用户都希望增加他们的关注者数量，因为关注者数量已经成为一个人受欢迎程度的象征。Instagram 的庞大用户群是不容被网络犯罪分子忽视的。

## 增加关注者

互联网上有很多增加 Instagram 关注者数量的应用程序。其中一些应用程序是需要用户提供账号密码的，有些应用程序只需要提供账户即可，这些应用程序安全吗？

![image.png-881.9kB](https://image.3001.net/images/20220712/1657627695_62cd642fe41f721f49ded.png!small)可疑的应用程序

许多 YouTube 视频都录制教程教授用户如何使用这些应用程序，视频中使用自己的账户登陆应用程序，就能够看到关注者的数量正在明显增长。

使用方式一般都比较简单：

> 使用账户与密码进行登录
>
> 通过 Instagram API 检查凭据
>
> 登录成功后即可使用对应功能，如增加关注者、增加喜欢、增加评论等
>
> 输入想要获得多少关注者

![image.png-84.6kB](https://image.3001.net/images/20220712/1657627696_62cd6430e550b638f02fa.png!small)增加关注者

执行后，每隔几秒就会对应增加关注者。

![image.png-225.8kB](https://image.3001.net/images/20220712/1657627699_62cd6433137b3cf447bfa.png!small)新增关注

## 如何推广

在 Telegram 频道中就会存在推广的 YouTube 视频：

![image.png-362.9kB](https://image.3001.net/images/20220712/1657627700_62cd6434b39e2eae4d3ff.png!small)Telegram
推广

甚至还有超过 19 万订阅者的大 V 博主也发布此类视频，评论区部分人表示他们的凭据被盗。

![image.png-526.3kB](https://image.3001.net/images/20220712/1657627701_62cd6435a8b71f936b941.png!small)评论区

## 恶意软件行为

恶意软件并不申请很多权限，看起来似乎没有什么危害。用户启动程序后，只能通过 Android Webview 看到以下网站：

![image.png-278.2kB](https://image.3001.net/images/20220712/1657627702_62cd6436946d29dc8aa56.png!small)恶意网站重定向

![image.png-237.1kB](https://image.3001.net/images/20220712/1657627703_62cd6437aeebc2335157d.png!small)恶意网站重定向

应用程序本身不包含很多功能，展示完广告后就会立即显示恶意网站。所有的恶意行为都在网站后台执行，而不在应用程序中执行。

![image.png-50.5kB](https://image.3001.net/images/20220712/1657627704_62cd6438c60f24311e504.png!small)部分代码

该网站声称使用 Instagram 的 API
保证凭据安全的，但实际上并不是这样。研究人员发现使用该应用程序几分钟后，就收到了来自土耳其的异常登录尝试，而且尝试登录的设备并不是 Instagram
的服务器而是一台型号为 LON-L29 的安卓手机。

![image.png-166.5kB](https://image.3001.net/images/20220712/1657627705_62cd64398aa3df0598683.png!small)异常登录通知

实际上，应用程序使用用户的凭据来增加其他用户的关注者数量，让每个使用应用程序的用户之间互相关注。

## 影响范围

被发现的最多的推广是印地语，其次是英语与葡萄牙语，印地语的大多数视频浏览量都超过了 100
次。安全研究人员测试的账号一天就增长了四百个关注，这意味着有四百个用户向攻击者发送了凭据。

## 结论

许多 Instagram
用户希望增加他们的关注者和喜欢，攻击者也就利用了这一点来发动攻击。凭据泄露后很可能会存在二次攻击，例如通过相同的凭据登录其他网站等。

## IOC

> e292fe54dc15091723aba17abd9b73f647c2d24bba2a671160f02bdd8698ade2  
> 6f032baa1a6f002fe0d6cf9cecdf7723884c635046efe829bfdf6780472d3907  
> hxxps://insfreefollower.com

## 参考来源

> [McAfee](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/instagram-> credentials-stealers-free-followers-or-free-likes/)

