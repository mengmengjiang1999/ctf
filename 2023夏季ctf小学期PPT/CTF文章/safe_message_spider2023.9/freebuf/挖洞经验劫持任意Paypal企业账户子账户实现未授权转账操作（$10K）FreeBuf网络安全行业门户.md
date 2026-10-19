***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担**

![paypal-store-1024x512.png](https://image.3001.net/images/20190807/1565169238_5d4a96565a9a1.png!small)

**好久没有发文了，今天分享我近期发现的一个Paypal越权漏洞（IDOR）。利用该漏洞，我可以劫持任意Paypal企业账户的子账户（二级账户），从而可发起从受害者企业账户到攻击者控制账户的未授权转账操作。理论上来说，漏洞原因在Paypal中发生了不安全的直接对象引用行为（IDOR）。**

##  **Paypal企业账户和子账户介绍  
**

Paypal企业账户（Business
Account）也叫PayPal商业账户，是为了方便各种大公司企业用户使用而开发的，具有PayPal高级账户的所有功能和限制，为方便交易和商业行为，企业账户下可以创建隶属于企业员工，但又具备各种权限的子账户（Secondary
Account），如设定其权限为只能查看余额，或者只能退款，或者只能提现等等。

但Paypal企业账户下的子账户还有一项权限，那就是可以把企业账户中的资金转账到任何子账户指定的其他账户中去。所以，基于这种权限，如果能劫持企业账户下的子账户，就可以从企业账户转钱出来，实现任意资金操作了，不是吗？说搞就搞。

## 动手测试

动手之前，我用victim@gmail.com和attacker@gmail.com注册了两个企业账户以便测试。

首先，在受害者邮箱victim@gmail.com绑定的企业账户下，我创建了一个用户名为victim1234的子账户；

接着，在攻击者邮箱attacker@gmail.com绑定的企业账户下，我创建了一个用户名为attacker1234的子账户；

现在，以攻击者一方为例，我们来观察一下企业账户下涉及的子账户（attacker1234）URL情况，我们先从企业账户中点击去到子账户中看看，如下：

> <https://www.paypal.com/businessmanage/users/1660971175791245038>

结尾的id号1660971175791245038代表的就是attacker@gmail.com绑定的企业账户。在此子账户查看操作过程中产生了一个如下的PUT请求：

    
    
    PUT /businessmanage/users/api/v1/users? HTTP/1.1
    
    Host: [www.paypal.com](http://www.paypal.com)
    
    Connection: close
    
    [{"id":"1660971175791245038","accessPoint":{"privileges":["MANUAL_REFERENCE_TXN","VIEW_CUSTOMERS","SEND_MONEY"],"id":"4446113495","accounts":["attacker@gmail.com"]},"roleID":0,"roleName":"CUSTOM","privilegeChanged":true,"privilegeSecondaryName":"ttt ttts"}]

仔细观察并测试一番过后，我发现，上述这个PUT请求中第一个id字段，即1660971175791245038这里可以替换为任意随机数值（如asdfjdsf），第二个id字段，即446113495这里，它代表了子账户id，漏洞就出在这里的第二个id字段。

由于，这第二个id字段只是简单的数字递增或递减，所以它完全是可枚举的，那么，对于攻击者来说，只要把它更改为比如446113496，此时，如果假设该id对应的就是受害者企业账户下的子账户victim1234，那么，攻击者就能轻易在他的企业账户子账户页面中（<https://www.paypal.com/businessmanage/users>），查看到另一企业账户下的受害者子账户信息了。

也就是说，比如，攻击者可以枚举出446113495至446113999的所有子账户，然后在其在其企业账户的子账户管理页面下都能查看到这些子账户，那么，终极招数就是攻击者只需通过这种方式的子账户信息查看，把相应子账户密码进行修改，那就可以实现账户劫持了，完美！

漏洞实现效果就是，攻击者可以通过密码修改方式登录受害者企业账户下的受害者子账户，进行任意未授权的转账操作。

## 漏洞奖励

漏洞上报后，Paypal官方进行了及时的修复，好在经检测未发现任何该漏洞的滥用行为，我也获得了Paypal奖励的$10,500。

![下载.png](https://image.3001.net/images/20190807/1565169174_5d4a9616a4461.png!small)
***参考来源：[whitehathaji](https://whitehathaji.blogspot.com/2019/07/paypal-bug-10k-all-secondary-users.html?m=1)，clouds编译整理，转载请注明来自FreeBuf.COM**

