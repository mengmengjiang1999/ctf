***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  0x01 概述

###  1.1 前言

 **2019 年 3 月 13 号，RIPS 又放了一个 WordPress 的 CSRF，与此同时 WordPress 官方也提交相应的
Commit，算是一个比较新的洞。问题出在文章的评论上，其实是有防 CSRF 相应的 wpnonce，熟悉 wp 的人肯定不会陌生 wpnonce，这是
wp 的防御机制，动作和postid构成的token，用来验证reference，而且 wordpress 对标签的过滤机制比较严格的。白名单机制，列如 a
标签的名单为：**

![](https://image.3001.net/images/20190315/1552634492_5c8b527c0c98d.png!small)

看起来是比较严格的，基本带动作的标签不可能出现，插不进 js。比较有趣是两个对评论的 filter 组合起来造成了，a 标签中的属性逃逸。RIPS
文章也说的比较简单，接下来看看具体的实现过程，其实存在利用条件的，RIPS 也没有指出来，总结时详细说明。

###  1.2 背景介绍

1.2.1 漏洞描述

漏洞存在于 5.1.1 之前的 WordPress 版本中，可以使用默认设置进行利用。

根据其 WordPress 官方下载页面，超过 33％的互联网网站正在使用
WordPress。文章评论是博客的核心功能并且默认情况下已启用，该漏洞会影响数百万个网站。

1.2.2 受影响版本

WordPress <= 5.1.1

###  1.3 测试环境

Kali 4.19.0 WordPress 5.1.1

##  0x02 漏洞实现过程

环境最新是 5.1.1 昨天才官方刚 commit 的修复过程，算是比较新。既然是是 CSRF，表单提交点在于每篇文章的评论处。wp-comments-post.php:25, wp_handle_comment_submission(wp_unslash( $_POST ))，进入
comment_handler 函数 做了一些简单的赋值过程：

![](https://image.3001.net/images/20190315/1552634549_5c8b52b5b72c6.png!small)

来看看上面对于用户身份判断的过程。评论需要用户为登录态。关键处：

![](https://image.3001.net/images/20190315/1552634580_5c8b52d421445.png!small)

其中判断用户能否不需要过滤 html，到下面的判断提交 comment 过程中的 wpnonce 验证，若是没有通过身份验证会重新定义 **kses**
处理过程的中的 filter，具体看一下 kses_init_filters

![](https://image.3001.net/images/20190315/1552634593_5c8b52e1298c2.png!small)

这里为什么会重新删减 filter，在前面初始化的过程中在 **init** 标签的注册了一个 kses_init()

![](https://image.3001.net/images/20190315/1552634603_5c8b52ebdfcb7.png!small)

仅仅判断通过用户身份 Session 身份判断了，需不要添加过滤 html 的 filter。管理员用户在操作的时候，即默认是没有插入对
pre_comment_content 的过滤 html 的钩子，但是在判断添加评论的时候又因为在想要的 wpnonce 验证不通过的时候，又添加上了相应的
filter，官方还是考虑到了相应的安全问题，但是为什么又要加一层身份判断，添加不同的处理函数呢，直接插入 wp_filter_kses 不好吗？

正是因为 wp_filter_kses 和 wp_filter_post_kses 不同上造成了后面的 js 执行
他们的不同在于过滤的严格度上，其实都一样是白名单过滤。但是跟 pre_comment_content 的钩子函数组合起来，就发送了属性逃逸。

看一下这个两个函数的定义。

![](https://image.3001.net/images/20190315/1552634665_5c8b53293a3db.png!small)

传入的第二参数不同，决定了后面允许使用的标签和属性的白名单不同。影响第二个钩子函数。即使这里 addslashes
转义了字符内容，紧接着下一个钩子涉及到对属性的处理，会恢复被转义字符内容。

![](https://image.3001.net/images/20190315/1552634682_5c8b533ac244e.png!small)

pre_comment_content 标签的钩子有默认的 4 个钩子 (我习惯叫钩子函数)，分别是
convert_invalid_entities，wp_targeted_link_rel，wp_rel_nofollow，balance
根据优先级排序。第一个把€ 及以后的实体转成相应的合法的 unicode 实体，第二个处理 a 标签 中 **target**
属性的，第三个是重点了两个重要钩子中的第二个，给 a 标签添加 rel 属性为 nofollow，如果存在 rel 属性则在其属性值中添加
nofollow，并去掉原来的 rel 属性值，其过程会重新拼接 a 标签。

![](https://image.3001.net/images/20190315/1552634710_5c8b53562f1e5.png!small)

wp_rel_nofollow 钩子在 pre_comment_content 中优先级为 15，当插入 wp_filter_post_kses
钩子时使用的默认值是 10，在 wp 中执行钩子时会有优先级判断，刚好 wp_filter_post_kses
也在前，所以也不涉及到对后面溢出的属性重新处理。

前面说了 wp_filter_post_kses 和 wp_filter_kses 的不同在于使用的白名单不同。前者传入的是 post，后者传入是
current_filter(), 这个值很好理解，这一系列钩子都在 pre_comment_content 标签下。所以理所当然是
pre_comment_content, 选择过程如下：

![](https://image.3001.net/images/20190315/1552634747_5c8b537b40e4a.png!small)

看当 post 的情况下，默认是没有注册 wp_kses_allowed_html 标签的，即每一步的 apply_filters()
返回输入的第一个值，post 的$allowedpostags 包含的标签及其属性是比较多的，pre_comment_content 只能走到默认
$allowedtags. 其中\$allowedtags 包含情况如下：

![](https://image.3001.net/images/20190315/1552634777_5c8b539913eb1.png!small)

可以看到 a 标签中的只允许 href 和 title，而 post 的$allowedpostags 是允许包含 rel 属性的

![](https://image.3001.net/images/20190315/1552634803_5c8b53b363ffa.png!small)

在第二部重要的钩子 wp_rel_nofollow 中，其中存在 rel 属性时才会去重新拼接，造成额外的属性溢出。所以这就是差异之处，确实考虑到了
**XSS** 的执行，都是用的白名单，但经过重新拼接会出现额外的属性。列如

> <a title= ' maple " onmouseover=alert(1) id=" ' rel="anything">，通过拼接变成<a
> title = " maple" onmouseover=alert(1) id="" rel ="anythingnofollow">。

在后面的过程中属性里面的特殊字符会被转义成实体。涉及到写 js 的可能需要绕一下不能用引号和双引号，可以这样绕一下：

![](https://image.3001.net/images/20190315/1552634870_5c8b53f6ad9e9.png!small)

playload 如下：

![](https://image.3001.net/images/20190315/1552634885_5c8b5405e41d1.png!small)

##  0x03 总结

###  3.1 利用条件

其实这个洞再利用条件的有一定限定 RIPS 也没有指出来，我在刚做时候，我添加了一个评论，我没有去文章页面看，我去的后台管理界面评论管理处看，发现并没有出现
**xss** 的情况，我很诧异不应该是一样吗？而后发现在输出评论前

![](https://image.3001.net/images/20190315/1552634939_5c8b543bd5a5e.png!small)

进行了标签为 **comment_text** 的过滤器，其中包含了 **wp_kses_post** 钩子
这也是为什么后台不行。但是应该这个思路，文章显示处也肯定用了这个标签的过滤器，但是理论上是没有使用的，因为使用以后溢出的属性会被过滤掉。

在仔细跟一下，发现确实有存在使用这个标签的情况，对 comment_text 过滤器的使用在 check_comment() 中

![](https://image.3001.net/images/20190315/1552634957_5c8b544d47cc7.png!small)

是个判断，看到这里你是否明白了这个使用的限定的条件？也就是说用户评论自己的文章时是不需要 check
的，所以这里存在一定使用条件，在进行添加评论的时候必须是管理员发布的文章才行。

这个洞其实一眼真的很难看出来。白名单验证，直接就放弃了。可不曾想存在一个弄巧的钩子。

官方修复在验证 **wpnonce** 不成立时给强制加了 wp_filter_kses 完全限定死了。当然了这个 csrf 依然存在。因为涉及到 wp
的特性 **pingback/trackback** 。总的来说还是非常细节的，在挖洞只能拼细节在这种流行的框架下。

##  0X04 修复建议

wp 默认是开启自动更新的，最新版本中已经得到修复，若关闭自动更新的环境，请及时检查更新。
<https://wordpress.org/news/2019/03/wordpress-5-1-1-security-and-maintenance-release/>

可手动修复：

![](https://image.3001.net/images/20190315/1552634974_5c8b545e06d32.png!small)

##  0x05 参考连接

<https://blog.ripstech.com/2019/wordpress-csrf-to-rce/>

***本文作者：alphalab，转载请注明来自FreeBuf.COM**

