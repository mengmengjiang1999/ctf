![Twitter.png](https://image.3001.net/images/20180504/15254174004383.png!small)  

**经过内部审计之后，Twitter今天承认，他们的密码存储机制存在错误，导致内部日志中记录了一些用户的密码。**

在Twitter之前，GitHub本周早些时候也发布了类似的声明。

就像在GitHub事件中一样，密码以明文格式记录在Twitter的内部服务器日志中。

明文密码是饱受诟病的安全措施，如今的网站往往会使用哈希加盐等方式存储用户的密码，避免密码泄露后被黑客知晓用户真正的密码。

Twitter表示，它通常通过将密码传递给bcrypt散列函数来加密密码，这也是顶尖的行业标准。

![TIM截图20180504150304.png](https://image.3001.net/images/20180504/15254175259688.png!small)  

“但是在实际情况中由于存在bug，在完成哈希处理之前密码就被写入内部日志，”Twitter发言人称。
“我们自己发现了这个漏洞，删除了密码，并且正在修复，以防问题再次发生。”

## 让用户决定是否更改密码

GitHub查出明文密码时，给所有受影响的用户发送了电子邮件并且强制让他们重置密码。

![TIM截图20180504150248.png](https://image.3001.net/images/20180504/15254175259512.png!small)  

但是Twitter没有发送邮件提醒，有些用户被强制修改密码，小编登陆Twitter发现，的确出现了一个警告窗口。

![TIM截图20180504130746.png](https://image.3001.net/images/20180504/15254176132794.png!small)  

Twitter并不认为这是非常重大的安全问题，Twitter认为它的系统从未被破坏过，只有少数员工可能看到过泄露的密码。

> “我们的调查显示没有任何人滥用了密码，”Twitter说。

 ***
参考来源：[BleepingComputer](https://www.bleepingcomputer.com/news/security/twitter-admits-recording-plaintext-passwords-in-internal-logs-just-like-github/)，本文作者Sphinx，转载注明来自FreeBuf**  

