## 0x01 背景

个别网站需要导入客户端的XX.P12证书，如果没有导入直接访问网站，浏览器会提示：400 Bad Request , 出现：No required SSL
certificate was sent等提示，如下图

![1662646969_6319fab98115f92e0117d.png!small?1662646970593](https://image.3001.net/images/20220908/1662646969_6319fab98115f92e0117d.png!small?1662646970593)

此时需要在burpsuite中导入证书

## 0x02 网站客户端证书

如果是正常的业务测试，甲方会提供xx.P12的文件

在burp导入网站客户端xx.p12证书的会提示要求输入密码，如果我们知道密码当然就直接输入，

![1662647123_6319fb53ed3d3c403a2df.png!small?1662647125294](https://image.3001.net/images/20220908/1662647123_6319fb53ed3d3c403a2df.png!small?1662647125294)

![1662647001_6319fad96e22c99aa5fd8.png!small?1662647002636](https://image.3001.net/images/20220908/1662647001_6319fad96e22c99aa5fd8.png!small?1662647002636)

## 0x03 不知道网站客户端证书的密码时

网站客户端xx.p12证书的会提示要求输入密码，但是有时候生成XX.p12证书时候，网站根本没有设置密码或者用户不知道密码。

证书生成的代码：

openssl pkcs12 -export -clcerts -out %s -in %s -inkey %s -password pass:%s

openssl pkcs12 -export -in user.pem -caname user alias -nokeys -out user.p12
-passout pass:pkcs12
password因为burp导入网站用户证书p12是一定要密码的，所以先在firefox导入这网站的客户端证书，然后再备份出来，备份出来的时候，自己输入密码a

![1662647017_6319fae92e6c919d7fbfa.png!small?1662647018228](https://image.3001.net/images/20220908/1662647017_6319fae92e6c919d7fbfa.png!small?1662647018228)

![1662647025_6319faf1b45e04ba6d1b5.png!small?1662647026898](https://image.3001.net/images/20220908/1662647025_6319faf1b45e04ba6d1b5.png!small?1662647026898)

![1662647033_6319faf979e561995a76c.png!small?1662647034603](https://image.3001.net/images/20220908/1662647033_6319faf979e561995a76c.png!small?1662647034603)

如果没有密码就为空。

备份

![1662647048_6319fb084e86869771ef7.png!small?1662647049460](https://image.3001.net/images/20220908/1662647048_6319fb084e86869771ef7.png!small?1662647049460)

输入密码：a

![1662647061_6319fb15bd28e0586f904.png!small?1662647063171](https://image.3001.net/images/20220908/1662647061_6319fb15bd28e0586f904.png!small?1662647063171)

把新备份证书导入burp 就可以了，这个时候输入密码a就可以成功导入客户端证书了

![1662647075_6319fb23343411239c7f0.png!small?1662647076307](https://image.3001.net/images/20220908/1662647075_6319fb23343411239c7f0.png!small?1662647076307)

注意事项：如果在user options 配置了证书，记得不要勾选project options 的Client SSL Certificates
的override user options

![1662647087_6319fb2f95c4c6e91761b.png!small?1662647088737](https://image.3001.net/images/20220908/1662647087_6319fb2f95c4c6e91761b.png!small?1662647088737)

此时就可以访问之前400的网页了，此时不再是400了。（图中为404是因为没有加路径）

![1662647100_6319fb3ca5b764132b88b.png!small?1662647101710](https://image.3001.net/images/20220908/1662647100_6319fb3ca5b764132b88b.png!small?1662647101710)

## 参考链接

<https://blog.csdn.net/qq_29277155/article/details/106024344>

