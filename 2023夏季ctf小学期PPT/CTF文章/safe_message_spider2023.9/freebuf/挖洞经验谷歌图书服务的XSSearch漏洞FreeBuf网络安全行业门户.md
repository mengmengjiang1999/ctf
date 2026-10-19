***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **** **作者在最近参与的一些漏洞众测项目中，着重关注了跨站搜索攻击漏洞（Cross-Site Search Attacks），也可称之为XS-Search，最终发现了谷歌图书服务 - books.google.com存在的跨站搜索攻击漏洞，获得了谷歌奖励的$1337美金。**

 ** **![o-google-books-lawsuit-facebook.jpg](https://image.3001.net/images/20190325/1553505126_5c989b66ab3a5.jpg!small)****

## 漏洞发现

发现该漏洞的灵感起源于35c3CTF比赛中一道针对搭建环境的[Filemanager类型题目](https://youtu.be/HcrQy0C-hEA)，其中提到，利用
Chromium XSS Auditor 和XS-Search攻击，可以提取获得目标用户的阅读记录和个人藏书列表。

在检查Google
Books的网站页面时（<https://books.google.com/>），我发现了其源码存在一些有意思的差异变化，其中一个就是，当图书搜索查询导致了至少只有一本书的搜索结果时，其会在页面源码中添加一段特定的JavaScript脚本代码，该代码从以下部份开始：

    
    
    <script>if (window['_OC_registerHover']){_OC_registerHover({"title":"<title>"

其中<title>为搜索结果中显示在第一的书名名称。所以，如果给定一个书名名称<title>和用户ID <uid>，那么就可以创建出以下访问链接:

[](https://books.google.com/books?uid=)

    
    
    <https://books.google.com/books?uid=><uid>#=1&q=<title>&x=<script>if (window['_OC_registerHover']){_OC_registerHover({"title":"<title>"

然而，这个链接最终是会被谷歌XSS Auditor给拦截了，因为即使uid=<uid>#=1&q=<title>是合法的，但是x=<script>if
(window['_OC_registerHover']){_OC_registerHover({"title":"<title>"却会被当成XSS参数被过滤。

另外一点值得关注的是，当XSS
Auditor对上述链接进行拦截时，其window.length的值就相当于0了，也就是说其中没有书目元素iframe。但由于谷歌会使用frame元素对书目进行存储分类，所以实际的frame元素值肯定是大于0的，因此，存在这种可能，那就是可以通过跨站方式来读取window.length属性来查看其中的frame元素值。当然，也可利用[XS-Leaks Github](https://github.com/xsleaks/xsleaks/wiki/Browser-Side-Channels)中的error page 方法来探测出我们所需要的frame值。

基于以上分析来说，这种攻击中必须知道受害者用户的<uid>
，所以其攻击面就相对变窄了。为此，还需要深入测试<uid>相关参数，看看其是否能有更加直接的利用方法，我们一起来观察以下Google
Books的跳转测试，请认真查看其中的uid值：

[](https://books.google.com/books?uid=vulnerability)

    
    
    <https://books.google.com/books?uid=vulnerability> -  跳转到Google Books自身；
    
    <https://books.google.com/books?uid=%2B> - 跳转到<https://books.google.com/books?uid=><uid>&hl=en；
    
    <https://books.google.com/books?uid=%2B1> - 服务端抛出404响应；
    
    <https://books.google.com/books?uid=1%2B1> - 跳转到<https://books.google.com/books?uid=><uid>&hl=en；
    
    <https://books.google.com/books?uid=>'&q=hack - 跳转到[https://www.google.com/search?tbo=p&tbm=bks&q=hack](https://www.google.com/search?tbo=p&tbm=bks&q=hack)；
    
    [https://books.google.com/books?uid=vulnerability&q=hack](https://books.google.com/books?uid=vulnerability&q=hack) - 以登录用户身份显示搜索结果。

上述一系列的跳转有些奇怪，但是综合最后两条重定向跳转，我们可以构造出一种XS-Search攻击，这种攻击中无需知道受害者用户的<uid>，就能以其身份显示出搜索结果。

## 攻击场景

恶意攻击者可利用上述方法构造出这种攻击场景：

当Google Books的普通用户访问了某个攻击者控制的恶意网站时，其中发生的任何交互行为，可能会在恶意网站后台触发窗口打开，通过控制cross-origin属性，可以非常容易地利用上述存在的漏洞获得受害者的Google
Books相关敏感个人信息。这些信息包括用户搜索过的书目名称、个人收藏书单、购买书单和阅读过的书籍记录。

## 漏洞复现

作者创建了一个PoC页面 - <https://terjanq.github.io/Bug-Bounty/Google/books-xs-search-enpgws9jw5mb/poc.html> 来复现上述XS-search攻击漏洞，在此之前，需要有以下操作前提：

1、开启了XSS-Auditor的Chromium浏览器；

2、创建两个名为s1和s2的书架，记住它们的<id>号，后续可在URL中用as_coll=<id>对它们进行访问；

3、从链接 <https://terjanq.github.io/Bug-Bounty/Google/books-xs-search-enpgws9jw5mb/urls.html>中选择一本书放入书架s1；

4、从链接 <https://terjanq.github.io/Bug-Bounty/Google/books-xs-search-enpgws9jw5mb/urls.html>中选择5本书放入书架s2；

5、访问PoC页面 - <https://terjanq.github.io/Bug-Bounty/Google/books-xs-search-enpgws9jw5mb/poc.html>，点击其中的“Click here to start the Poc”，

6、按其中的要求进行选择性填空；

7、等待查询响应结果。

针对我的上述漏洞报告，谷歌通过了一系列综合防护措施来进行了安全改进，以防止XS-Search攻击。谷歌也强调，如果此类漏洞不能对其防护机制造成实质性影响，之后不会再接收类似的XS-Search漏洞，会统一当成重复报。

## 漏洞上报进程

> 2019.1.27 漏洞初报
>
> 2019.1.28 漏洞分类
>
> 2019.1.30 漏洞被承认
>
> 2019.2.5 谷歌奖励$500
>
> 2019.3.5 漏洞修复
>
> 2019.3.19 谷歌继续奖励$837，总共$1337

* **参考来源：** **[medium](https://medium.com/@terjanq/google-books-x-hacking-29c249862f19) ，clouds编译，转载请注明来自FreeBuf.COM**  

