# CVE-2018-7600 Drupal核心远程代码执行漏洞分析

阅读量 **255463**

发布时间 : 2018-04-13 18:26:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01be7ae638011f751a.png)

## 0x01 漏洞介绍

Drupal是一个开源内容管理系统（CMS），全球超过100万个网站（包括政府，电子零售，企业组织，金融机构等）使用。两周前，Drupal安全团队披露了一个非常关键的漏洞，编号CVE-2018-7600
Drupal对表单请求内容未做严格过滤，因此，这使得攻击者可能将恶意注入表单内容，此漏洞允许未经身份验证的攻击者在默认或常见的Drupal安装上执行远程代码执行。

## 0x02 漏洞分析

Drupal渲染数组的情况有页面加载和Ajax表单发出的请求，在这里Ajax
API调用是攻击者最佳的选择。那么作为用户注册表单的一部分，图片字段使用Ajax API将图片上传到服务器，并且生成缩略图

![](https://p2.ssl.qhimg.com/t01bd8fd7aa6fbfe493.png)

查阅了相关文档资料现在，我们所要做的就是注入一个恶意渲染数组，该数组使用Drupal的渲染回调方法在系统上执行代码。有几个属性我们可以注入：

  * #access_callback  
由Drupal使用来确定当前用户是否有权访问元素。

  * #pre_render  
在渲染之前操作渲染数组。

  * #post_render  
接收渲染过程的结果并在其周围添加包装。

  * #lazy_builder  
用于在渲染过程的最后添加元素。

  * #access_callback 标签虽然callback回调函数可控，但需要回调处理的字符串不可控，导致无法利用。以下场景以post_render和lazy_builder为例

### 2.1、漏洞场景1：引入#post_render

**#post_render**

这个API标签可以被所有的元素和表单使用，它是在drupal_render()方法中调用，可以渲染当前元素和子元素，也可对内容进行修改。

例子中$
element通过调用admin_form_html_cleanup函数处理返回处理后的结果。再来看可以触发攻击载荷的代码，在渲染的过程中调用了call_user_func进行回调处理，但$callable
回调函数通过表单伪造，$elements的子元素同样也是通过表单可控

![](https://p4.ssl.qhimg.com/t0106b47be54cd00725.png)

攻击者利用攻击载荷
mail[#post_render][]=passthru&mail[#type]=markup&mail[#markup]=whoami
，这里的#markup是当前元素#type的子元素，通过数组的方式传入值，执行过程如图

![](https://p3.ssl.qhimg.com/t01b4546e8e52e791a2.png)

魔术方法__toString得到$this->string 等于whoami
，带入到call_user_func中交给passthru函数执行，导致漏洞触发

PHP内置函数pasthru执行后会回显结果

### 2.2、漏洞场景2：引入#lazy_builder

  * #lazy_builder 可选，数组值，必须有且只有两个元素，一个是回调函数名，一个回调的参数，参数只能是NULL或者标量类型

  * $callable变量取#lazy_builder元素标签数组下标0的值作为回调函数名，取数组下标1的值当回调方法的参数， 下面攻击载荷调用PowerShell 远程下载文件到本地保存为php网页后门，代码如下图

![](https://p5.ssl.qhimg.com/t01159c6c09649dff48.png)

我们传入的lazy_builder[0]和lazy_builder[1]的值在渲染的时候用call_user_func_array完成整个攻击过程

整个漏洞的产生过程都是因为call_user_func或者call_user_func_array等回调函数导致的任意代码执行，API元素标签中可能还会触发漏洞的标签有#theme
、#create_placeholder、#theme_wrappers等等。

## 0x04 缓解措施

官方在最新版本8.5.1中增加了下图方法

对请求的GET、POST、COOKIE 进行过滤处理

希望广大用户尽快升级到最新版本Drupal 8.5.1 ，
下载地址：<https://www.drupal.org/project/drupal/releases/8.5.1>

## 0x05 Reference

<https://research.checkpoint.com/uncovering-drupalgeddon-2/>

<https://github.com/g0rx/CVE-2018-7600-Drupal-RCE/blob/master/exploit.py>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **云影实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/104697](/post/id/104697)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Drupal](/tag/Drupal)
  * [CVE-2018-7600](/tag/CVE-2018-7600)
  * [远程代码执行漏洞](/tag/远程代码执行漏洞)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t012b723966029ed2c4.png) 云影实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

