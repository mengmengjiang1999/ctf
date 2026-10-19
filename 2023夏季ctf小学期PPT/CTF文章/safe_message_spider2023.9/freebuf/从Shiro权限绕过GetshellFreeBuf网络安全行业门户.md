## 引言

此次为授权渗透，但客户就丢了一个链接啥都没了。这种情况不好搞，分享这篇文章的原因主要是过程曲折，给大家提供下一些思路，当然大佬有更好的思路也可以分享下。

PS：本文仅用于技术讨论与分享，严禁用于任何非法用途，违者后果自负。

## 正文

![1609829781_5ff40d95c9baf3d74c5f6.png!small](https://image.3001.net/images/20210105/1609829781_5ff40d95c9baf3d74c5f6.png!small)

打开登录页面，第一反应是先试试错误次数有没有限制，用户名可否枚举。然后有个记住我，尝试下shiro。

![1609829801_5ff40da9bf09157ac60f1.png!small](https://image.3001.net/images/20210105/1609829801_5ff40da9bf09157ac60f1.png!small)

提示用户名或密码错误，多错误几次也没弹窗验证，Intruder安排上，直接爆破的是admin账号，不然交叉爆破太费时间，爆破同时shiro也去试试。

![1609829815_5ff40db78ad93804445e1.png!small](https://image.3001.net/images/20210105/1609829815_5ff40db78ad93804445e1.png!small)

确实是使用的shiro，虽然没有爆破出来，但有这个也是不错的。

![1609829828_5ff40dc4b217c1323f9a5.png!small](https://image.3001.net/images/20210105/1609829828_5ff40dc4b217c1323f9a5.png!small)

毫不客气的打开了紫霞大佬的shiro工具。

![1609829834_5ff40dca5a632d083a082.png!small](https://image.3001.net/images/20210105/1609829834_5ff40dca5a632d083a082.png!small)

换了个shiro工具也没跑出来key。

爆破不行，shiro反序列化也没有，也没看出来是什么cms特征，到这点上了，直接宣布渗透结束？

要是这样那我岂不是被开除了

先收集一波信息吧。

查看js发现如果账号密码正确会跳转到index这个页面

![1609829848_5ff40dd87db16bac67348.png!small](https://image.3001.net/images/20210105/1609829848_5ff40dd87db16bac67348.png!small)

直接访问index页面提示302跳转

![1609829853_5ff40ddd3353457f69535.png!small](https://image.3001.net/images/20210105/1609829853_5ff40ddd3353457f69535.png!small)

看到这里我突然想起了shiro还有个权限绕过，反手就是一个/;/index

![1609829860_5ff40de4d7cb32b5f6cdc.png!small](https://image.3001.net/images/20210105/1609829860_5ff40de4d7cb32b5f6cdc.png!small)

果然shiro默认key是改了但权限绕过还是存在，随知而来得还有一个坏消息站点得目录怎么获得呢？

把js找遍了也没有看见其他路径了，最后掏出目录爆破工具试试，加上/;/去爆破。

![1609829884_5ff40dfc9c11ba9fe2b53.png!small](https://image.3001.net/images/20210105/1609829884_5ff40dfc9c11ba9fe2b53.png!small)

这站的swagger既然对外网开放，真是绝处逢生。

![1609829896_5ff40e08c5d9b335d3a0f.png!small](https://image.3001.net/images/20210105/1609829896_5ff40e08c5d9b335d3a0f.png!small)

之前有朋友问 **swagger** 是什么，我这里就顺便说下。

 **Swagger** 是一个规范和完整的框架，用于生成、描述、调用和可视化RESTful 风格的Web 服务。
总体目标是使客户端和文件系统作为服务器以同样的速度来更新。 文件的方法，参数和模型紧密集成到服务器端的代码，允许API来始终保持同步。
**Swagger** 让部署管理和使用功能强大的API从未如此简单  
  
---  
  
Swagger里面没有找到能getshell的接口，只能从后台下手，swagger只是一些api接口信息，而且增加用户修改密码这些就扣会验证登录账号也无法使用，在后台或许还能有机会。

果然皇天不负有心人，最后找到了用户名和密码。

![1609829947_5ff40e3b6dc27e1f5c3c6.png!small](https://image.3001.net/images/20210105/1609829947_5ff40e3b6dc27e1f5c3c6.png!small)

把加密的密码拿去各个网站解都无果（一开始以为是强口令，没有去尝试爆破）

![1609829958_5ff40e464c4a3c8e2a2c7.png!small](https://image.3001.net/images/20210105/1609829958_5ff40e464c4a3c8e2a2c7.png!small)

然后去日志查询接口逛了一圈，确定了管理员账号是jwj。并不是admin，难怪最开始跑字典没跑出来，估计这也是一个原因，只能再试试爆破了。

![1609829969_5ff40e517a1863f280f5e.png!small](https://image.3001.net/images/20210105/1609829969_5ff40e517a1863f280f5e.png!small)

果然爆破出来了，成功进入后台。

进入后台翻了个遍，找到个上传，而且还没有任何过滤，那不得送他个好的马子

![1609830025_5ff40e89e9ae178de794d.png!small](https://image.3001.net/images/20210105/1609830025_5ff40e89e9ae178de794d.png!small)。![1610011682_5ff6d422bec3aa0ee5419.png!small](https://image.3001.net/images/20210107/1610011682_5ff6d422bec3aa0ee5419.png!small)

![1609830050_5ff40ea2320bac3c6ae0f.png!small](https://image.3001.net/images/20210105/1609830050_5ff40ea2320bac3c6ae0f.png!small)

蚁剑连上，完工。

## 总结

此次渗透虽然技术含量不好，但非常有趣。从爆破后台账号密码开始，兜兜转转又回到了爆破后台账号密码。重新验证了那句话，渗透的本质就是信息收集。

