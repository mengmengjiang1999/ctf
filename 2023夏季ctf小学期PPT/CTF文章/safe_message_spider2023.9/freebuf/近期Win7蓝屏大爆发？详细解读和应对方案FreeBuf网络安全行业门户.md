**近期，深信服接到不少客户咨询关于Win7蓝屏大爆发的问题，大概内容指“Win7服役结束，微软不再更新补丁，电脑集体蓝屏，错误代码为F4，蓝屏与漏洞补丁有关联等等，并呼吁用户不要修复漏洞补丁”。**

![](https://image.3001.net/images/20200225/1582619080_5e54d9c81ee08.png!small)

不过，从深信服收集上来的问题来看，并没有出现企业大规模Win7蓝屏的现象。我们通过追溯，发现比较早出现这一问题的，是个人及网吧环境，确实有部分个人用户及网管向安全厂商求助了。

关于漏洞修复（打补丁）是否会引起Win7蓝屏这一问题，我们进行了反复验证，并没有发现打补丁和Win7蓝屏有必然的关联（也就是说，打补丁并不会一定导致Win7蓝屏），我们也在第一时间咨询了微软官方人员，对方亦表示对此不甚了解。

由于补丁与Win7蓝屏没有必然联系，且企业环境极少发生，而在个人与网吧环境出现一定规模的蓝屏现象，让我们高度怀疑与Windows盗版系统有关系。最终，我们在Ghost系统中发现了一款优惠券插件[CouponUpdate.ex](http://couponupdate.ex/)e，这款插件在更新升级的时候，会导致系统蓝屏。

![](https://image.3001.net/images/20200225/1582619093_5e54d9d56d9c8.png!small)

这里建议广大用户使用微软官方原版镜像安装系统，避免使用各种盗版系统或Ghost系统。下图，是优惠券插件[CouponUpdate.ex](http://couponupdate.ex/)更新程序对应的安装目录。

![](https://image.3001.net/images/20200225/1582619100_5e54d9dcb0877.png!small)

上述文件，在第三方平台上，被多数的安全厂商报恶意了。

![](https://image.3001.net/images/20200225/1582619108_5e54d9e4d0d05.png!small)

我们提醒广大企业级用户，对于近期Win7大规模蓝屏消息，不用过度恐慌，深信服提供了详细解读和解决方案。正常来讲，企业用户遇到这个问题的概率还是比较低的。如果您的内网主机存在这个问题，建议按照下面这个解决方案进行处置。

## 解决方案

手动清理：

如果你的系统盘出现了如下文件：

> C:\ProgramFiles\Coupon\[CouponUpdate.ex](http://couponupdate.ex/)e
>
> C:\ProgramFiles(x86)\Coupon\[CouponUpdate.ex](http://couponupdate.ex/)e
>
>
> C:\Users\Administrator\AppData\Local\Coupon\[CouponUpdate.ex](http://couponupdate.ex/)e

则将双击上述目录中对应[Uninst.ex](http://uninst.ex/)e程序进行卸载，即可解决该蓝屏问题

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

