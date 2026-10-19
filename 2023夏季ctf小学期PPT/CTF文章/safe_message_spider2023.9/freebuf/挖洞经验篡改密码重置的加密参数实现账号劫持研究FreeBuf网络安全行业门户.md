**![Account_Takeover_Knowledge_base.jpg](https://image.3001.net/images/20200608/1591607935_5ede027f26288.jpg!small)**

**想必大家都对参数篡改攻击有所了解，今天作者分享的是对RSA加密参数的篡改从而实现账号劫持的简单测试，漏洞原因在于Web应用在客户端缺乏安全的防护机制。一起来看看。**

出于保密，目标Web应用暂且叫它为target.com，在接触该目标时，经测试发现，其上所有的参数操作都是加密传输的，在Burp的抓包配合下，可见其大概的加密形式如下：

>
> userName=8cfe39943d6e08e505531ddfd90c66f47c2f55ce140e5770fef58d3bec826f52490a089d1942aaed74a9f6ed0fd8890cef6c36e31220c9859a3ab423062wxbeea480d94850d95374ab3a7a47de3e9f89b3250a58397044817069c6a17109cc27408b0c53f94q34a5878270ff6random8c96b916bb9594af648e6dc6851685a9d41cdb868761c4d36d49389150840af05a277530dd191464befc79a46d418a4e4f12b2dec0c5cc01097efed4b2a6608c2c2f076a27fe0ce62a70a4fe2f02b558abae6f4a4757fb34a593ccd04f2356c2c521758b0e59c017087121d63c1b002fc794953e690290489f8af87d17359ba0fc59b832f972d80293fe8d2aafcb4faca

接下来，我把关注点放到了其“忘记密码”功能上，其大概流程如下：

> 1、访问target.com/signin页面，输入需要重置密码的邮箱号；
>
> 2、Web服务端会向邮箱发送一个6位数授权码；
>
> 3、访问target.com/forgotPasswd，输入需要重置密码的邮箱号、授权码和重置后的密码，提交即可完成密码重置操作。

现在，我以邮箱“attacker@email.com”向Web服务端发起密码重置请求，在收到授权码之后，访问target.com/forgotPasswd，重复上述密码重置操作，该过程用Burp抓包的数据如下：

![1_1asM7G226C3noJURinTROg.png](https://image.3001.net/images/20200608/1591607816_5ede020853895.png!small)

从上图中可以看到，其中包含4个参数：Email, Username, Encrypted Password 和
Code，但是所有这些参数都是加密的。我尝试着把参数数值替换成明文数值，如用“attacker@email.com”
或“victim@email.com”替换掉其中的邮箱，但提交的请求却不成功。

接着，我用另外的浏览器访问target.com/forgotpasswd，以“victim@email.com”身份发起密码重置请求，抓包，复制其中的email
和 username加密数值，到之前的浏览器请求包中，提交，但请求还是无效。

因此，总结来看，忘记密码的请求格式如下：

>
> email=encryptedattackeremail&userName=encryptedattackerusername&passwd=encryptedattackerpasswd&code=encryptedcode

我度过把其中的encryptedattackeremail替换为encryptedvictimemail，encryptedattackerusername替换为encryptedvictimusername，但都不可行。

我依然没有气馁。经过一番分析，根据加密长度，我发现其加密方式为RSA。同时，我对目标Web应用的源代码分析后发现，其中多个js脚本中包含了rsa方法名称，因此，我确信其为RSA加密无疑了。

后来我意识到Burp抓包时参数值已经被加密了，这是一种客户端加密，所以我尝试把浏览器中调用的js脚本执行关闭，看看加密功能是否还可行，但之后，密码重置请求就完全不起效。

我又考虑到，由于这是客户端加密，RSA函数肯定是在某个js脚本中被定义，且被浏览器调用的，于是我点击Chrome浏览器的Inspect
Element按钮，来到了其Console一栏下，输入“rsa” ，让我吃惊的是其中匹配出了“rsaEncrypt”方法函数名。

![1_okgC2FhWjYJYu5bILd0JCQ.png](https://image.3001.net/images/20200608/1591607836_5ede021caa256.png!small)

经过测试发现，只要为该方法函数提供一个参数名，其就能生成相应的加密数值，因此，我以参数s定义了数值“victim@email.com”，即s=“victim@email.com“，执行rsaEncrypt，它即生成了如下相应的加密串：

![1_5TBd_uTCrBcYCB_8_R2fjQ.png](https://image.3001.net/images/20200608/1591607847_5ede0227a30bb.png!small)

需要注意的是，可能是其与会话参数相关，所以在端点/forgotpasswd上每次刷新页面，上述的加密串都会发生变化。

按照前述的密码重置操作，我以“attacker@email.com”身份发起密码重置请求，提交授权码和新密码，并进行Burp抓包，其相应界面如下：

![1_OROqZKQ6EE08-KTHfqpq7Q.png](https://image.3001.net/images/20200608/1591607858_5ede0232aa193.png!small)

在Burp的请求包中，除了
把其中的“username”替换成浏览器端rsaEncrypt方法生成的“rsaencryptedvictimemail”加密串之外，其它的都无需更改，也即：

email=encryptedattackeremail& **username=rsaencryptedvictimemail**
&passwd=encryptedattackerpasswd&code=encryptedcode

请求提交后，奇迹发生了，victim@email.com对应的账号密码被成功更改，实现了账户劫持！

参 **考来源**

>  **[medium](https://medium.com/@imayankraheja/tampering-encrypted-parameter-> to-account-takeover-a5fec7dde360)**

 ** ***** 本文作者：clouds ，转载请注明来自 FreeBuf.COM **  

