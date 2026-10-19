本文中提供的例子均来自网络已公开测试的例子，仅供参考。

本期带来绕过验证漏洞。为了保障业务系统的安全，几乎每个系统都会存在各种各样的验证功能。常见的几种验证功能就包括账号密码验证、验证码验证、JavaScript数据验证及服务端数据验证等等，但程序员在涉及验证方法时可能存在缺陷导致被绕过，于是斗哥总结了以下几种绕过验证的姿势和大家一起讨论讨论~

![image.png](https://image.3001.net/images/20181130/1543559992_5c00db386e9ea.png!small)

客户端校验绕过

客户端校验是常见的一种校验方式，也就是在客户端校验用户的输入，将校验结果作为参数发送至服务端，或利用前端语言限制用户的非法输入和操作。面对此类的校验方法可以通过修改前端语言或者在传输中对参数进行篡改来绕过验证。

举个栗子：

a). 某系统需要购买才能观看视频，不同的课程以ID划分。

![image.png](https://image.3001.net/images/20181130/1543560007_5c00db47055fd.png!small)

b). 发现是否付费只靠前端js控制，更改courseID就可以看到不同的课程，recordURL就是视频播放的链接，无需登录即可播放。

![image.png](https://image.3001.net/images/20181130/1543560023_5c00db57815de.png!small)

c). 根据播放地址中的videoCode，可获取视频下载地址:

http://*.*.*.*/v3/resource/video/queryurl?jsoncallback=cb&quality=3&audioIndex=0&types=1&videoCode={videoCode}

所得urls为视频下载地址。

![image.png](https://image.3001.net/images/20181130/1543560038_5c00db66f279e.png!small)

d). 通过脚本，可将全站视频下载下来。

![image.png](https://image.3001.net/images/20181130/1543560050_5c00db724d7fe.png!small)

客户端验证信息泄露

程序员在编写验证程序时有可能会将验证信息直接泄露到客户端，攻击者就可以通过分析服务端的返回数据直接获得关键的验证信息从而完成验证。

举个栗子：

某免费wifi连接时需要使用发送到手机的密码进行验证，抓取发送密码的数据包时，发现密码返回客户端，导致任意全网账号可以登录联网。

![image.png](https://image.3001.net/images/20181130/1543560065_5c00db817a487.png!small)

客户端流程控制绕过

程序员在编写验证程序时有可能会验证结果返回到客户端，由客户端根据服务端提供的验证结果进行下一步操作，攻击者可以通过篡改验证结果或直接执行下一步操作实现绕过。

举个栗子：

a). 某系统重置密码需要三个步骤，首先要输入图片验证码。

![image.png](https://image.3001.net/images/20181130/1543560079_5c00db8fefeb5.png!small)

b). 然后需要通过短信验证码验证身份。

![image.png](https://image.3001.net/images/20181130/1543560090_5c00db9a8e45d.png!small)

c).访问http://*.*.*.*/a/user/findPasswordSetp 直接跳到重置密码的页面。

![image.png](https://image.3001.net/images/20181130/1543560111_5c00dbaf2b12d.png!small)

d). 可成功修改密码密码。

![image.png](https://image.3001.net/images/20181130/1543560120_5c00dbb8e78fd.png!small)

操作目标篡改绕过

如果某操作采用了连续身份校验机制或身份校验过程与操作过程分离，可以尝试在身份验证过程中替换身份校验对象或操作对象实现绕过验证。

举个栗子：

a). 修改某系统的绑定手机。

![image.png](https://image.3001.net/images/20181130/1543560138_5c00dbcad966e.png!small)

b). 选择免费接收短信校验码修改。

![image.png](https://image.3001.net/images/20181130/1543560149_5c00dbd519619.png!small)

c). 将修改的手机号改为自己的手机号码。

![image.png](https://image.3001.net/images/20181130/1543560158_5c00dbde9c3ba.png!small)

d). 通过修改的手机号码收到的校验码修改手机号。

![image.png](https://image.3001.net/images/20181130/1543560168_5c00dbe88d303.png!small)

e). 发现可以成功修改成新的手机号。

![image.png](https://image.3001.net/images/20181130/1543560186_5c00dbfaa7e27.png!small)

参数篡改

程序猿小哥哥在编写验证程序时有可能会对验证码字段进行正确性校验，但当验证码字段不存在或为空时就直接通过校验。

举个栗子：

a).某系统存在绕过验证漏洞，抓取登录的数据包。

![image.png](https://image.3001.net/images/20181130/1543560203_5c00dc0b609d8.png!small)

b).删除验证码字段（securityCode）进行爆破。

![image.png](https://image.3001.net/images/20181130/1543560212_5c00dc1427144.png!small)

c). 爆破成功，并可以使用爆破出来的账号密码进行登录。

![image.png](https://image.3001.net/images/20181130/1543560222_5c00dc1e8bd31.png!small)

![image.png](https://image.3001.net/images/20181130/1543560231_5c00dc277d778.png!small)

辅助验证功能绕过

为了验证用户身份或者避免攻击者使用自动化工具进行批量操作，应用程序可能会采用辅助验证功能，常见的辅助验证功能包括图片验证码、短信验证码、邮箱验证，这些功能在设计时如果存在缺陷则可以被绕过，导致辅助验证功能失效。

举个栗子：

a). 访问某系统，一开始页面无验证码。

![image.png](https://image.3001.net/images/20181130/1543560242_5c00dc32f113b.png!small)

b). 输错一次之后，出现验证码。

![image.png](https://image.3001.net/images/20181130/1543560256_5c00dc400b218.png!small)

c). 尝试进行爆破，抓取第一次无验证码的数据包，发现会提示需要验证码。

![image.png](https://image.3001.net/images/20181130/1543560303_5c00dc6fedc82.png!small)

d). 多次尝试之后发现，验证码是通过cookie中的PHPSESSID来判断的。

![image.png](https://image.3001.net/images/20181130/1543560324_5c00dc84e2d4f.png!small)

e). 修改PHPSESSID后成功绕过验证码限制。

![image.png](https://image.3001.net/images/20181130/1543560405_5c00dcd563cf4.png!small)

f). 成功爆出账号。

![image.png](https://image.3001.net/images/20181130/1543560418_5c00dce2c4990.png!small)

好啦，斗哥对于绕过验证的总结就到这里啦，对于绕过验证的修复斗哥有一点点建议：

1.所有验证在服务端进行，验证问题的答案不能以任何形式返回客户端中（如图片验证码答案、短信验证码、验证问题答案等）。

2.验证结果及下一步跳转操作由服务端直接进行。

3.应尽可能避免采用连续身份验证机制，无论采用何种验证机制，只有当所有的数据输入以后，才进行身份验证数据的验证。

##  

