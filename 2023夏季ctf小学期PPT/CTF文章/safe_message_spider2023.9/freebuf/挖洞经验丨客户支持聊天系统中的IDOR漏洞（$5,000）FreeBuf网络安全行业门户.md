***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![2019-04-17_165229.jpg](https://image.3001.net/images/20190417/1555492325_5cb6ede57dbeb.jpg!small)**
**大家好，今天分享的writeup是一个关于客户支持系统（Customer
Support）的IDOR漏洞（不安全的直接对象引用），该漏洞可以导致目标系统的访问控制功能失效，实现客户支持平台内的任意消息读取和发送，还能下载任意用户的相关文件。**

 **最终，该漏洞被厂商评定为严重级别（Critical），给予了$5000美金的奖励，我们一起来看看。**

## 漏洞发现端倪

在目标系统的客户支持聊天窗口中，用户发送消息后，聊天窗口后台会产生如下请求：

![01.png](https://image.3001.net/images/20190417/1555491993_5cb6ec996bddd.png!small)如上图所示，用户在聊天窗口中发送了包含有字段——“testing
by john wick2!”的消息，该字段赋值给了“text”参数。另外，还可以看到一个“user_id”、“email”
、user_hash、“anonymous_id” 和blocks。

请求发送出去之后，目标系统服务端会及时做出以下响应：

![02.png](https://image.3001.net/images/20190417/1555492005_5cb6eca5b2826.png!small)可以看到，响应中也包含有用户的发送消息，以及另外一个由服务端分配的参数“id”。

有了这些测试样例，我们自然会想到——不安全的直接对象引用漏洞（Insecure Direct Object Reference
Vulnerability，IDOR），那就动手测试吧！

## 测试IDOR漏洞

### 测试1——替换请求中的user_id

非常直接的了，我们在请求消息中的“user_id”参数，把它替换成其他用户对应的数值，会是什么情况呢？一换，服务端解析错误：

###
![03.png](https://image.3001.net/images/20190417/1555492067_5cb6ece386cfb.png!small)测试2——删除请求中与用户对应的user_hash
参数串值

这里，我们不动“user_id”参数，只是简单地把与用户对应的“user_hash”参数值删除，在聊天窗口中发送消息之后，得到了以下服务端响应：

![04.png](https://image.3001.net/images/20190417/1555492093_5cb6ecfdaea32.png!small)其中提示：基于用户身份验证机制，必须对用户进行哈希值验证。也就是说，哈希验证是强制的，且与user_id值是映射关系。那我们再看看其它参数。

### 测试3——删除请求中的user_id和user_hash参数值

把请求中的user_id和user_hash参数值同时删除后，在聊天窗口中发送消息之后，服务端响应：User hash is
invalid，与上一个测试响应相同。

### 测试4——删除请求中的user_id 、user_hash和anonymous_id参数值

现在，只剩下“email”和“anonymous_id”参数了，那就在上一测试步骤的基础上，我们再把anonymous_id参数值也删除看看。在聊天窗口中发送消息后（hello
this jaya222），这一删，惊喜就来了：

![05.png](https://image.3001.net/images/20190417/1555492171_5cb6ed4b6cdb6.png!small)IDOR，这绝对是一个IDOR！从这里可以看出，目标系统的Web后端出现了配置错误，未对“email”参数做出有效的过滤检查措施，也就是说，服务端只需要“email”参数值就能验证用户身份，并做出有效响应！

## PoC测试

如下，在聊天窗口消息发送的对应请求中，我们把其中的user_id 、user_hash和anonymous_id参数值都删除了，如下：

![06.png](https://image.3001.net/images/20190417/1555492235_5cb6ed8b090f2.png!small)聊天窗口消息发送之后，在缺失这么多与用户相关的重要参数请求中，我们竟然能收到目标系统客户支持平台的有效响应，如下：

##
![07.png](https://image.3001.net/images/20190417/1555492253_5cb6ed9dac6a0.png!small)漏洞隐患

基于此，如果我把其中的“email”参数值更改为其他用户对应的注册邮箱地址，就能读取该用户所有的发送消息，也能以该用户身份进行消息发送和文件上传，而且还能下载与该用户对应的文件资料。

在上述PoC那步，我只要把POST请求中的URL缩短为/messenger/web/conversations，只发送带有其他用户email地址的参数，就能在服务器响应中轻松获取Web后端为该用户分配的用户id。之后，我就可以把该id号添加到POST请求URL末尾，形成/messenger/web/conversations/[conversation-id]，实现对该用户的完全会话内容获取。

## 测试总结

在测试1阶段中，修改user_id不成功后，可能我们大多数人都会认为目标系统不存在IDOR漏洞，然后选择放弃测试。但是，IDOR漏洞不仅限于参数数值更改，它还包括参数数值删除，以及其他与个人信息相关的字段替换等。就像在该例中，email参数值导致了IDOR漏洞，只要把其更改为与其他用户对应的注册邮箱，就能轻松获取到该用户的对话消息内容和相关个人文件。所以，IDOR漏洞不只是参数数值的替换或增加，它还可以有其它形式的测试实现，我们在具体测试过程中要多动手多思考。

***参考来源：[medium](https://medium.com/@mr_hacker/a-5000-idor-f4268fffcd2e)，clouds编译，转载请注明来自FreeBuf.COM**  

