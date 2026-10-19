![](https://image.3001.net/images/20200104/1578132954_5e1065da895a2.jpeg!small)

**今天分享的Writeup是作者在目标网站漏洞测试中发现的一种简单的人机身份验证（Captcha）绕过方法，利用Chrome开发者工具对目标网站登录页面进行了简单的元素编辑就实现了Captcha绕过。**

人机身份验证（Captcha）通常会出现在网站的注册、登录和密码重置页面，以下是目标网站在登录页面中布置的Captcha机制。

![](https://image.3001.net/images/20200104/1578132792_5e106538c279d.png!small)

从上图中可以看到，用户只有在勾选了Captcha验证机制的“I‘m not a robot”之后，登录按钮（Sign-IN）才会启用显示以供用户点击。因此，基于这点，我右键点击了Sign-In按钮，然后用Chrome开发者工具的“元素检查”（Inspect Element
）功能来查看Sign-In按钮的底层元素，这一看，竟然发现其在“提交”（Submit）动作之后，定义了“禁用”（Disable）属性，好吧，那我就把它改变成“启用”（Enable）试试看。

![](https://image.3001.net/images/20200104/1578132882_5e1065928e472.png!small)

这一改，登录按钮（Sign-IN）显示且可点击了，好吧，我确实不是一个机器人，人机身份验证（Captcha）在这里成了摆设。

![](https://image.3001.net/images/20200104/1578132898_5e1065a28ba80.png!small)

我好奇服务端的验证方式，于是就用BurpSuite对上述过程进行了抓包，发现服务端一开始都不对用户提交的Captcha操作做验证，因此，即使我把提交的Captcha会话内容删除了，一样可以跳转到登录页面，根本不需要触发其中的“启用”（Enable）属性就行。

![](https://image.3001.net/images/20200104/1578132913_5e1065b1ab584.png!small)

我简单做了一个PoC发给了厂商，他们马上就做了反馈和整改。绕过人机身份验证（Captcha）的方法还有很多，这只是一个小技巧而已。

 ***参考来源：[medium](https://medium.com/@abhishake100/bypassing-captcha-17c59d37f459)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

