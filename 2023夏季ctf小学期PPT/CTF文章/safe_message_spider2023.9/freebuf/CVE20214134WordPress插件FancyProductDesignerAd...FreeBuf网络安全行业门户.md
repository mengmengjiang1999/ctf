## 前言

大家好，我是WordPress！我是世界上使用最广泛的博客系统之一。我有丰富的插件模板资源，这让我能强大深受好评，但开放的生态同时也带来更多安全隐患。

Sucuri 的报告显示， WordPress
是全球恶意黑客入侵最严重的CMS平台，让人很头大。但面对手持利刃的攻击者，我不是孤军奋战，来自全球各地的白帽都在协助我修复漏洞，修建更安全的护城河。

最近认识了武艺高强的宁静之盾斩月安全实验室，已经协助我发现并修补多个插件漏洞。小盾团队发现的 0day
漏洞CVE-2021-4134已在Wordfence官网公开披露。（此处应有掌声！）

![](https://image.3001.net/images/20220315/1647315652_62300ac42e268315a0b15.gif!small)

![](https://image.3001.net/images/20220315/1647315664_62300ad0b1690af218775.png!small)

漏洞挖掘是一条充满未知的探索之路，下一步可能是更大的问号，也可能是柳暗花明的另一村，我们希望与大家分享挖掘之路，一起共建更安全的生态。

接下来有请小盾闪亮登场，为大家分享吧！

![](https://image.3001.net/images/20220315/1647315711_62300aff09866cad30e22.jpg!small)

![](https://image.3001.net/images/20220315/1647315733_62300b1502f33fdb94639.jpg!small)

## 01 关于Fancy Product Designer

Fancy Product
Designer是WordPress、WooCommerce和Shopify的一个可视化产品配置插件，它允许客户使用自己的图形和内容定制产品。据统计，Fancy
Product Designer已在超过 18,000 个网站上安装使用。

小盾团队在研究我的插件Fancy Product
Designer时，发现了后台的SQL注入漏洞，但好在该漏洞的利用需要WordPress后台管理员权限，这提升了利用的难度，但仍不能掉以轻心。

## 02 漏洞描述

WordPress 插件Fancy Product Designer 易受 SQL 注入攻击，因为~/inc/api/class-product.php
文件中对参数id过滤不足，允许具有管理级别权限的攻击者注入任意 SQL 查询以获取敏感信息。

 **影响范围：Fancy Product Designer <= 4.7.4**

## 03 漏洞分析

首先，漏洞的URL为：[http://example.com/wp-admin/admin-ajax.php?action=fpd_export&_ajax_nonce=&id=1，URL中存在SQL注入漏洞的参数为“id”。](http://example.com/wp-admin/admin-ajax.php?action=fpd_export&_ajax_nonce=&id=1%EF%BC%8CURL%E4%B8%AD%E5%AD%98%E5%9C%A8SQL%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%8F%82%E6%95%B0%E4%B8%BA%E2%80%9Cid%E2%80%9D%E3%80%82)

经过代码调试，跟进到“wp-content/plugins/fancy-product-designer/admin/class-admin-ajax.php”文件中的函数“export_product()”，并且发现代码将参数“id”的值赋给“$product_id”：![](https://image.3001.net/images/20220315/1647315891_62300bb3a019f123d9b28.png!small)钛合金慧眼继续扫射，发现函数“export_product()”中创建了一个类“FPD_Product”，并将变量“$product_id"的值作为参数进行初始化：![](https://image.3001.net/images/20220315/1647315915_62300bcb33c143193002f.png!small)而上图中创建的类在“wp-content/plugins/fancy-product-designer/inc/api/class-product.php”文件中被定义：![](https://image.3001.net/images/20220315/1647315940_62300be49302ca82d942e.png!small)接下来继续跟进“class-admin-ajax.php”文件中的函数“export_product()”，发现其调用了类“FPD_Product”中的”get_title()“函数：![](https://image.3001.net/images/20220315/1647315968_62300c005ce8a4c83e98f.png!small)小脑瓜如同上了发条一般飞速运转，我决定停下来看看”get_title()“函数是怎样编写的。从下图可以看到该函数写得较为简单，来自金牌小盾团队的我忍不住呵呵，竟然直接将变量“id”的值用来进行SQL查询，并且未对其进行过滤，从而导致SQL注入漏洞：![](https://image.3001.net/images/20220315/1647315990_62300c16250177d9871ef.png!small)一顿分析可以看出，URL中的参数“id”的值在整个传递过程中都没有进行过滤，最终传入了SQL语句中。令人窒息的是该插件不止这一处SQL注入漏洞，几乎所有涉及SQL语句中，都未对传入的值进行过滤。

例如本文分析的:“wp-content/plugins/fancy-product-designer/inc/api/class-product.php”文件，以及另外一个文件”wp-content/plugins/fancy-product-designer/inc/api/class-view.php“，这两个文件的部分代码如下图所示。![](https://image.3001.net/images/20220315/1647316022_62300c36f3f559b4ca7ba.png!small)![](https://image.3001.net/images/20220315/1647316034_62300c422650b4d745a88.png!small)

## 04 漏洞验证

### 环境搭建

![](https://image.3001.net/images/20220315/1647316083_62300c73db264b31156c6.png!small)

### 验证步骤

1、以管理员权限登录WordPress后台，点击到Fancy Product Designer插件管理处，点击Templates Library添加模板：

![](https://image.3001.net/images/20220315/1647316093_62300c7de8406fdbe0ceb.png!small)2、添加一个免费模板![](https://image.3001.net/images/20220315/1647316135_62300ca715b203935a474.png!small)3、添加模板之后，点击导出，然后抓取请求包，注入点就位于GET参数id中：![](https://image.3001.net/images/20220315/1647322579_623025d35276247dcdf92.png!small)

###
![](https://image.3001.net/images/20220315/1647322592_623025e06cfc4f1291c8b.png!small)POC

> [http://example.com/wp-admin/admin-> ajax.php?action=fpd_export&_ajax_nonce=00144c25c7&id=1%20OR%20sleep(1)](http://example.com/wp-> admin/admin-> ajax.php?action=fpd_export&_ajax_nonce=00144c25c7&id=1%20OR%20sleep\(1\))

###  **Sqlmap截图**

![](https://image.3001.net/images/20220315/1647322666_6230262abd87302d6e60c.png!small)

## 05 漏洞危害

恶意攻击者可以利用该漏洞执行任意SQL语句，如查询数据、下载数据、写入webshell、执行系统命令以及绕过登录限制等，但是该SQL注入漏洞存在于WordPress后台，需要管理员权限才能利用，利用难度相对较大。

## 06 解决方案

目前开发者已发布修补版本，建议更新到 4.7.5 版本或更新版本。

### 参考链接

https://codecanyon.net/item/fancy-product-designer-woocommercewordpress/6318393

### 修复建议：

（1）所有查询语句都使用数据库提供的参数化查询接口，参数化的语句使用参数而不是将用户输入变量嵌入到SQL语句中。当前几乎所有的数据库系统都提供了参数化SQL语句执行接口，使用此接口可以非常有效地防止SQL注入攻击。

（2）对进入数据库的特殊字符（’”<>&*;等）进行转义处理，或编码转换。

（3）确认每种数据的类型，比如数字型的数据就必须是数字，数据库中的存储字段必须对应为int型。

（4）数据长度应该严格规定，能在一定程度上防止比较长的SQL注入语句无法正确执行。

（5）网站每个数据层的编码统一，建议全部使用UTF-8编码，上下层编码不一致可能导致一些过滤模型被绕过。

（6）严格限制网站用户的数据库操作权限，给用户提供刚好能够满足其需求的权限，从而最大限度地减少注入攻击对数据库的危害。

（7）避免网站显示SQL错误信息，比如类型错误、字段不匹配等，防止攻击者利用这些错误信息进行一些判断。

## 07 CVE-2021-4134漏洞时间线

> 2021-12-15：漏洞报告给厂商  
> 2021-12-17：厂商确认漏洞  
> 2022-2-8：厂商发布4.7.5版本修复该漏洞  
> 2022-2-8：报送网络安全威胁和漏洞信息共享平台（NVDB）

