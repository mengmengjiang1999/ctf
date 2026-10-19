原创： Xiaoleung 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

SQL注入漏洞

  * SQL注入漏洞产生原因及危害  

  * 在sql查询中很多程序员会将变量拼接入sql语句后再进行查询，这样如果黑客在参数中插入其他sql语句就可能导致我们网站的密码被被黑客查询出来或者被拖取大量数据，如果在开发中使用了字符串拼接进SQL语句就必须进行严格的过滤，任何用户输入的内容都不可信任，以下列举几种防御方法。  

## 数字型查询注入防护  

查询例子如下

如果是这样的数字型注入我们可以强制将传入参数转换为整数，以剔除黑客拼接的SQL语句。修改如下

这是这个网页正常查询的返回的结果。

![v2-3ff3e7df8fe24a0b317d9ade6c97de89_hd.j](https://pic1.zhimg.com/80/v2-3ff3e7df8fe24a0b317d9ade6c97de89_hd.jpg)

这是一个典型的数字型注入，我们输入注入语句可见注入成功

![v2-b725e1f772ddfad715f307dda80cfcfc_hd.j](https://pic2.zhimg.com/80/v2-b725e1f772ddfad715f307dda80cfcfc_hd.jpg)

我们强制转换类型到代码中：

![v2-b77fcd480536ee785ae3fdcbe45dbab7_hd.j](https://pic3.zhimg.com/80/v2-b77fcd480536ee785ae3fdcbe45dbab7_hd.jpg)

我们再执行注入可以看到恢复正常查询，注入失败。

![v2-b030dd697c6e9a01e2c29093d1e63ebb_hd.j](https://pic4.zhimg.com/80/v2-b030dd697c6e9a01e2c29093d1e63ebb_hd.jpg)

## 非数字型注入防护-通用防护  

如果查询参数不是数字，那么我们该如何防护呢，那么这里可以使用通用型防护，对数字型和非数字型同样适用，我们知道web中获取参数的方式主要有三种分别是get、post、cookie。那么我们防护的主要方面也是这三个方面，我们可以对网站的所有流量进行黑名单过滤。当然这个也可以拦截xss漏洞。具体流程如下：

![v2-c808de7b9adb4e4a701d815151cb5793_hd.j](https://pic4.zhimg.com/80/v2-c808de7b9adb4e4a701d815151cb5793_hd.jpg)

具体实现代码：

测试

同样我们在原先的网站上将我们的waf.php文件包含进去，在执行注入操作，可见我们已经将非法操作拦截。

![v2-fdac4f30c4535ec4b7c9290e56f9d5b9_hd.j](https://pic2.zhimg.com/80/v2-fdac4f30c4535ec4b7c9290e56f9d5b9_hd.jpg)

![v2-4463eb172746edb770ec25ff985fac7f_hd.j](https://pic2.zhimg.com/80/v2-4463eb172746edb770ec25ff985fac7f_hd.jpg)

## 使用预处理对注入进行防护  

PHP预处理查询的例子

  * 预处理的优点  

  * 预处理语句大大减少了分析时间，只做了一次查询（虽然语句多次执行）。  

  * 绑定参数减少了服务器带宽，你只需要发送查询的参数，而不是整个语句。  

  * 预处理语句针对SQL注入是非常有用的，因为参数值发送后使用不同的协议，保证了数据的合法性。  

XSS漏洞的防护

  * xss漏洞产生的原因及危害  

  * xss漏洞和sql注入一样也是注入型漏洞，主要是黑客在网页中注入恶意的js代码，可以导致我们的cookie被盗取，黑客通过cookie欺骗就能轻松登陆我们的后台，黑客也可以利用js进行挂马、黑帽seo、攻击客户计算机等操作危害十分严重。那么如何防御呢，我将讲解两种主要防御方法。  

  * xss分类  

  * xss主要分为反射型，储存型、和DOM型  

## 转义 htmlspecialchars()  

我们知道在数据库查询出来的数据可以打印到网页上，但是数据可能是用户在注册或者输入其他表单输入的，那么这里用户可能输入的是js或者html代码，这里就可能导致，用户输入的代码在浏览器中被解析并执行，那么我们这就可以通过
htmlspecialchars()将其转义为不可解析的字符串，从而避免此类攻击。

这是一个模拟存在xss漏洞的网页。我们进行模拟攻击和修复。

我们传入一个xss攻击代码，可见直接获取了当前网页的cookie内容

![v2-e2d259d9deb4a4689ca7e31e4d5fd663_hd.j](https://pic1.zhimg.com/80/v2-e2d259d9deb4a4689ca7e31e4d5fd663_hd.jpg)

那我们在输出时候给$id加上htmlspecialchars()呢

我们可以明显看到浏览器不再解析我们传入的js代码，而是将它当做普通字符串输出。

![v2-539c22d20dfd33f6d102d259627ef791_hd.j](https://pic4.zhimg.com/80/v2-539c22d20dfd33f6d102d259627ef791_hd.jpg)

## 通用型防护  

将我们sql注入的通用型防护waf.php包含到该网页同样可以实现过滤。

![v2-40e10d56e86d7dfae029b9e9749bdede_hd.j](https://pic2.zhimg.com/80/v2-40e10d56e86d7dfae029b9e9749bdede_hd.jpg)

CSRF漏洞的防御

  * CSRF漏洞产生的原因和危害  

  * CSRF漏洞主要是我们的网站没有对表单验证，这个表单是不是我们网站自己本身提交的，如果有一个改密码的表单被人构造并放在了其他人的网站上，我们在打开这个黑客精心构造的域外表单时候就导致了我们本身的密码被修改，黑客也可以通过CSRF漏洞进行蠕虫式传播，新浪微博就曾遭遇过此类攻击，黑客精心构造表单，当你打开这个表单的链接时候就会自动发送一条微博，其他人打开同样进行这样的操作。  

## TOKEN防护  

我们如何验证这个表单是不是我们自己网站本身提交的呢，那么我们可以在每个表单下生成一个隐藏的input表单存放一个TOKEN，在进行表单提交时会验证这TOKEN是否在SESSION上，如果在就执行这个表单的操作，如果TOKEN不在或者根本没提交TOKEN那么说明表单是伪造的,我们直接截断操作。具体流程如下：

![v2-c7cfa6585d5312939cf4f7f7774bcb87_hd.j](https://pic3.zhimg.com/80/v2-c7cfa6585d5312939cf4f7f7774bcb87_hd.jpg)

防护代码编写：

测试

  * 我们分别写两个文件分别是index.php用于提交表单，xss.php用于验证表单  

  * index.php  

xss.php

可以看到我们代码非常简单，只要我们通过动态的TOKEN验证，那就会输出check success，否则输出NO-TOKEN!

首先我们直接提交表单是没有问题的直接返回成功

![v2-34bc47f3727888620bc0f9e725537d5d_hd.j](https://pic4.zhimg.com/80/v2-34bc47f3727888620bc0f9e725537d5d_hd.jpg)

但是我们F12将TOKEN值删除再提交呢？

![v2-291194621d4348fe68c8b64d7b7646ea_hd.j](https://pic2.zhimg.com/80/v2-291194621d4348fe68c8b64d7b7646ea_hd.jpg)

可以看到会直接截断

![v2-7ada929d93765eae261c6566bb23a83b_hd.j](https://pic2.zhimg.com/80/v2-7ada929d93765eae261c6566bb23a83b_hd.jpg)

web防御中的代码安全：

http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182015120317290200001

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关!

  

