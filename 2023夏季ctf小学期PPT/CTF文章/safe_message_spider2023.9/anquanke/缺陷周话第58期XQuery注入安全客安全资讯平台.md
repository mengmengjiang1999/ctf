# 【缺陷周话】第58期：XQuery注入

阅读量 **858033**

发布时间 : 2019-11-05 17:15:46

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01649690fcb193fd32.jpg)

## 1、XQuery 注入

XQuery是一种函数式语言，可用于检索以XML格式存储的信息，负责从XML文档中查找和提取元素及属性。常用于在网络服务中提取信息，生成摘要报告，数据转换等。类似于
XPath 注入，XQuery 注入攻击利用了 XQuery 解析器的松散输入和容错特性，能够在
URL、表单或其它信息上附带恶意代码进入程序,当包含恶意代码的信息参与动态构造XQuery查询表达式，会造成XQuery
注入，攻击者可以利用漏洞获得权限信息的访问权并更改这些信息。本文以JAVA语言源代码为例，分析“XQuery注入”缺陷产生的原因以及修复方法。该缺陷的详细介绍请参见CWE
ID 652: Improper Neutralization of Data within XQuery Expressions (‘XQuery
Injection’) (http://cwe.mitre.org/data/definitions/652.html)。

## 2、“XQuery 注入”的危害

XQuery 注入可能会访问存储在敏感数据资源中的信息，获得被入侵服务器的配置信息。

## 3、示例代码

### 3.1 缺陷代码

![](https://p3.ssl.qhimg.com/t01f549cab18c292d02.png)

上述代码操作是获取到用户输入的用户名、密码并在XML文档中查询该条数据是否存在。首先第23行获取 XML
的数据源对象，第24~25行获取用户输入的用户名和密码，第26行进行 XML 的数据源连接。第27行动态构造 XQuery 查询表达式。第29行通过
XQExpression 执行 XQuery 查询。由于用户名密码来自不可信任的数据源，在正常情况下诸如搜索用户名和密码的对应帐户，该代码执行的表达式如下：

> for $user in doc(users.xml)//user[username=’test_user’ and pass=’pass123′]
> return $user

但是，这个表达式是由一个常数查询字符串和用户输入的字符串连接动态构造而成，因此只有在 username 或 password
不包含单引号字符时，才会正确执行这一查询。如果攻击者为 username 输入字符串 admin’ or 1=1 or ”=’，则该查询会变成：

> for $user in doc(users.xml)//user[username=’admin’ or 1=1 or ”=” and
> password=’x’ or ”=”] return $user

添加条件 admin’ or 1=1 or ”=’ 会使 XQuery 表达式永远评估为 true。因此，该查询在逻辑上等同于更简单的查询：

> //user[username=’admin’]

无论输入什么样的密码，查询结果集都会返回文档中存储的管理用户，这样的查询会使攻击者绕过用户名与密码同时匹配的要求。

使用代码卫士对上述示例代码进行检测，可以检出“XQuery注入”缺陷，显示等级为中，从跟踪路径中可以分析出数据的污染源以及数据流向。在代码行第29报出缺陷，如图1所示：

![](https://p4.ssl.qhimg.com/t01e48ea03677ff3c63.png)

图1：“XQuery 注入”检测示例

### 3.2 修复代码

![](https://p0.ssl.qhimg.com/t01ff4c4cc28dfa9fe0.png)

在上述修复代码中，在第27行中使用 declare 语法声明字符串变量username和password。第34~37行使用 XQExpression
对象的 bindString() 方法把变量绑定到查询。类似于SQL查询中的占位符，这里使用声明变量来模拟参数化查询。

使用代码卫士对修复后的代码进行检测，可以看到已不存在“XQuery注入”缺陷。如图2所示：

![](https://p1.ssl.qhimg.com/t01ef8ea2729632637b.png)

图2：修复后检测结果

## 4、如何避免“XQuery 注入”

（1）使用参数化的查询，/root/element[@id=$ID]  
（2）创建一份安全字符串列表，限制用户只能输入该列表中的数据。  
（3）净化用户输入，fn:doc()、fn:collection()、xdmp:eval() 和xdmp:value() 这些函数需要特别注意，过滤掉
’、[、= 和 &等特殊字符。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信代码卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/190240](/post/id/190240)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码安全](/tag/代码安全)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhimg.com/t015a32ce3696fa7636.png) 奇安信代码卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

