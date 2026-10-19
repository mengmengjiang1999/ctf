**Author: p0wd3r (知道创宇404安全实验室)**

**Date: 2017-05-18**

## 0x00 漏洞概述

### 漏洞简介

Joomla于5月17日发布了新版本3.7.1,（<https://www.joomla.org/announcements/release-news/5705-joomla-3-7-1-release.html>），本次更新中修复一个高危SQL注入漏洞（<https://developer.joomla.org/security-centre/692-20170501-core-sql-injection.html>），成功利用该漏洞后攻击者可以在未授权的情况下进行SQL注入。

### 漏洞影响

未授权状态下SQL注入

影响版本： 3.7.0

## 0x01 漏洞复现

Joomla 在 3.7.0 中新增了一个
`com_field`组件，其控制器的构造函数如下，在`components/com_fields/controller.php`中：
![](https://images.seebug.org/content/images/2017/05/construct.png-w331s)

可以看到当访问的`view`是`fields`，`layout`是`modal`的时候，程序会从`JPATH_ADMINISTRATOR`中加载`com_fields`，这就意味着普通用户可以通过这样的请求来使用管理员的`com_fields`。

接下来我们看管理员的`com_fields`组件，我们来到`administrator/components/com_fields/models/fields.php`，其中的`getListQuery`的部分代码如下：

![Alt
text](https://images.seebug.org/content/images/2017/05/getlistquery.png-w331s)

程序通过`$this->getState`取到`list.fullordering`，然后使用`$db->escape`处理后传入`$query->order`函数，mysqli的`escape`函数代码如下：

![Alt text](https://images.seebug.org/content/images/2017/05/escape.png-w331s)

这里调用`mysqli_real_escape_string`来转义字符，该函数具体作用如下：

![Alt text](https://images.seebug.org/content/images/2017/05/mysqli-escape.png-w331s)

仅对单双引号等字符进行转义，并未做更多过滤。另外`$query->order`函数的作用仅仅是将数据拼接到`ORDER
BY`语句后，也并未进行过滤，所以如果`list.fullordering`可控，那么就可以进行注入。

我们可以看到`list.fullordering`是一个`state`，`state`会在视图的`display`函数中进行设置：

![Alt
text](https://images.seebug.org/content/images/2017/05/display.png-w331s)

跟进这个设置过程，程序会走到`libraries/legacy/model/list.php`中的`populateState`函数中，具体的调用栈如下：

![Alt text](https://images.seebug.org/content/images/2017/05/state-stack.png-w331s)

该函数中有如下一段代码：

    
    
    if ($list = $app->getUserStateFromRequest($this->context . '.list', 'list', array(), 'array'))
    {
        foreach ($list as $name => $value)
        {
            // Exclude if blacklisted
            if (!in_array($name, $this->listBlacklist))
            {
    
                ...
    
                $this->setState('list.' . $name, $value);
            }
        }
    }

程序通过`$app->getUserStateFromRequest`取到一个`$list`数组
，如果数组的key不在黑名单中，则遍历该数组对相应`state`进行注册，`getUserStateFromRequest`的代码如下：

![Alt
text](https://images.seebug.org/content/images/2017/05/getstate.png-w331s)

结合前面的调用来看，我们可以通过请求中的参数`list`来设置`$list`变量，因此我们访问`http://ip/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml(2,concat(0x7e,(version())),0)`并开启动态调试动态调试，结果如下：

![Alt
text](https://images.seebug.org/content/images/2017/05/fullordering.png-w331s)

可以看到`list.fullordering`已经被我们控制。

回到`getListQuery`，该函数会在视图加载时被自动调用，具体函数调用栈如下：

![Alt text](https://images.seebug.org/content/images/2017/05/query-stack.png-w331s)

所以我们的payload也就通过`getState`传入了这个函数，最终导致SQL注入：

![Alt
text](https://images.seebug.org/content/images/2017/05/payload.png-w331s)

![Alt text](https://images.seebug.org/content/images/2017/05/poc.png-w331s)

## 0x02 补丁分析

![Alt text](https://images.seebug.org/content/images/2017/05/patch.png-w331s)

改为取`list.ordering`和`list.direction`作为查询的参数，这两个参数在`populateState`函数中做了如下处理：

![Alt text](https://images.seebug.org/content/images/2017/05/patch-case.png-w331s)

如果值不在指定范围内则将其更改为默认值，因此无法再将payload带入。

## 0x03 参考

<https://www.seebug.org/vuldb/ssvid-93113>

<https://blog.sucuri.net/2017/05/sql-injection-vulnerability-joomla-3-7.html>

<https://developer.joomla.org/security-centre/692-20170501-core-sql-injection.html>

<https://www.joomla.org/announcements/release-news/5705-joomla-3-7-1-release.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/305/>

