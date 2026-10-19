作者：绿盟科技  
来源：<http://blog.nsfocus.net/cve-2018-804-analysis/>

#### CVE-2018-8045 漏洞简介

漏洞具体情况可参见[绿盟科技安全威胁周报-201812周](http://blog.nsfocus.net/nsfocus-201812/
"绿盟科技安全威胁周报-201812周")

Joomla! Core SQL注入漏洞：

NSFOCUS ID：39158  
CVE ID：CVE-2018-8045  
受影响版本：Joomla! Joomla! 3.5.0-3.8.5  
漏洞点评：Joomla是一套网站内容管理系统,使用PHP语言和MySQL数据库开发。Joomla! 3.5.0
-3.8.5版本对SQL语句内的变量缺少类型转换，导致User Notes列表视图内SQL注
入漏洞，可使攻击者访问或修改数据等。目前厂商已经发布了升级补丁，修复了这个 安全问题，请用户及时到厂商的主页下载。

#### CVE-2018-8045 漏洞详情

我们先看下joomla官网怎么说的：

<https://developer.joomla.org/security-centre/723-20180301-core-sqli-vulnerability.html>

![](https://images.seebug.org/content/images/2018/03/dae57f06-19fe-431d-978f-57ce06d53251.png-w331s)

User Notes模块由于缺少变量类型转换，导致sql注入的产生。这个漏洞在3.8.6版本被解决。

漏洞介绍很模糊，单从介绍来看，根本不知道这个sql注入产生的位置。

但是既然是3.8.6版本解决的，那我们就来从3.8.6版本的update包中找找思路。

如下是github上joomla的releases列表

<https://github.com/joomla/joomla-cms/releases>

找到Update from Joomla!
3.8.5升级包下载，打开下载好的升级包，根据notes这个线索搜索下。果然，在升级包中看到了一个notes.php文件。

![](https://images.seebug.org/content/images/2018/03/93080ab4-81c8-4395-a3ed-9dcfb6e50a2d.png-w331s)

我们回到github上，看下这个notes.php改动了什么。

![](https://images.seebug.org/content/images/2018/03/899478ec-c31e-4266-bc0d-05c644802b22.png-w331s)

很明显，升级包中的notes.php中，对$categoryId的值进行了限制，强制转换为int类型，可以确定，这个漏洞就出在这里。

在这里说个题外话，notes.php中getState方法出现过很多次，分别有

  * getState(‘filter.search’)
  * getState(‘filter.published’)
  * getState(‘filter.category_id’)
  * getState(‘filter.user_id’)
  * getState(‘filter.level’)

但是唯有getState(‘filter.category_id’)方法没有进行(int)类型转换，存在着漏洞隐患，这可能是开发者一时的疏忽吧。

#### CVE-2018-8045 漏洞分析

来看下存在漏洞的代码：

    
    
    // Filter by a single or group of categories.
    $categoryId = $this->getState('filter.category_id');
    
    if ($categoryId && is_scalar($categoryId))
    {
       $query->where('a.catid = ' . $categoryId);
    }

$categoryId未经过滤直接拼接sql语句进行查询，造成了sql注入。

但是$categoryId参数如何控制呢？

存在漏洞的文件位于\administrator\components\com_users\models\notes.php，是一个joomla的模型文件，它的控制器是\administrator\components\com_users\controllers\notes.php

我们登录joomla后台来看一下在哪里触发这个漏洞。

访问[http://xxx/joomla/administrator/index.php?option=com_users&view=notes](http://xxx/joomla/administrator/index.php?option=com_users&view=notes)
即可触发该控制器。

![](https://images.seebug.org/content/images/2018/03/ff2f1711-1b5f-4d69-8938-c4c2e1bfc2e5.png-w331s)

但是如何控制$categoryId参数呢？如果只访问

[http://xxx/joomla/administrator/index.php?option=com_users&view=notes](http://xxx/joomla/administrator/index.php?option=com_users&view=notes)

只会向服务器发送一个get请求，请求中根本不包含我们想要的categoryId参数

先看下出问题的这行代码

    
    
    $categoryId = $this->getState('filter.category_id');

从getState(‘filter.category_id’)不难看出来，它的作用是一个过滤器，用来选择category_id的

因此想向它传参，一定和高级搜索之类功能的有关。

选择Search Tools选项 Select Category选项。

![](https://images.seebug.org/content/images/2018/03/05c064f2-bc6e-4060-91f3-de00df968eeb.png-w331s)

此时joomla的发包情况

![](https://images.seebug.org/content/images/2018/03/a889a9ed-c53c-46cd-8fcc-2260ceba6b88.png-w331s)

此时我们需要的filter[category_id]参数出现在了post参数中，通过这个参数的值，即可畅通无阻的进行注入。

下面验证下这个filter[category_id]参部分可以直接传递给后台的$categoryId参数

我们修改了filter[category_id]参数内容为’kingsguard_test’，并发包

![](https://images.seebug.org/content/images/2018/03/f638fb3d-b36a-4968-9fd3-a9ecea2cfc1c.png-w331s)

后台下断点，抓取categoryId参数，并拼接sql语句进行查询。

![](https://images.seebug.org/content/images/2018/03/eb22e94c-c672-4741-9f28-f82c513c3b0b.png-w331s)

#### 利用验证

![](https://images.seebug.org/content/images/2018/03/83e8a226-9b5b-4273-af26-06543d45c77e.png-w331s)

#### 漏洞修复

升级joomla至最新版本

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/553/>

