# 【漏洞分析】CVE-2017-14596：Joomla! LDAP注入导致登录认证绕过漏洞（含演示视频）

阅读量 **208435**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-21 14:17:03

 **x**

##### 译文声明

本文是翻译文章，文章来源：ripstech.com

原文地址：<https://blog.ripstech.com/2017/joomla-takeover-in-20-seconds-with-ldap-injection-cve-2017-14596/>

译文仅供参考，具体内容表达以及含义原文为准。

****

**前言**

拥有超过[8400万次的下载量](https://downloads.joomla.org/)，Joomla!是当今互联网上最流行的内容管理系统（CMS）之一。其承载了网络世界全部网站内容和文章的3.3％。使用代码分析工具RIPS在login
controller中 **检测到以前未曾发现的LDAP注入漏洞。**
这一个漏洞可以导致远程攻击者使用盲注技术爆出超级用户的密码，使其可以通过LDAP认证在短时间内接管Joomla！<=3.7.5的站点。目前Joomla！官方已经在3.8版本中修复了该问题。

  

**漏洞利用条件**

安装以下版本的应用将会受到该问题的影响：

Joomla! 1.5 <= 3.7.5

Joomla!配置通过LDAP认证

该漏洞不是由配置缺陷造成，攻击者不需要任何权限就可以利用此漏洞。

  

**漏洞危害**

通过利用登录页面中的漏洞，无权限的远程攻击者可以获取通过LDAP进行身份验证服务的Joomla！的认证凭据。这些认证凭证包括超级用户的用户名和密码。然后，攻击者可以使用或得到的信息登录到管理员控制面板并通过上传自定义的Joomla!插件拿到Web服务的权限实现远程代码执行。

  

**漏洞分析**

首先，在LoginController中Joomla!从登录表单接收用户输入的用户认证凭据。

/administrator/components/com_login/controller.php

    
    
    class LoginController extends JControllerLegacy
    {
        public function login()
        {
            ⋮
            $app = JFactory::getApplication();
            ⋮
            $model = $this->getModel('login');
            $credentials = $model->getState('credentials');
            ⋮
            $app->login($credentials, array('action' => 'core.login.admin'));
        }
    }

认证凭据传递给login方法，然后调用authenticate方法。

/libraries/cms/application/cms.php

    
    
    class JApplicationCms extends JApplicationWeb
    {
        public function login($credentials, $options = array())
        {
            ⋮
            $authenticate = JAuthentication::getInstance();
            $authenticate->authenticate($credentials, $options);
        }
    }
    /libraries/joomla/authentication/authentication.php
    class JAuthentication extends JObject
    {
        public function authenticate($credentials, $options = array())
        {
        ⋮
            $plugin->onUserAuthenticate($credentials, $options, $response);
        }
    }

基于用于认证的插件，authenticate方法将认证凭据传递给onUserAuthenticate方法。如果Joomla!被配置为使用LDAP进行身份验证，LDAP插件的方法将会被调用。

/plugins/authentication/ldap/ldap.php

    
    
    class PlgAuthenticationLdap extends JPlugin
    {
        public function onUserAuthenticate($credentials, $options, &$response)
        {
            ⋮
            $userdetails = $ldap->simple_search(
                str_replace(
                    '[search]',
                    $credentials['username'],
                    $this->params->get('search_string')
                )
            );
        }
    }

在LDAP插件中，用户名凭据嵌入到search_string选项中指定的LDAP查询中。根据[官方Joomla!文档](https://docs.joomla.org/LDAP_Authentication)显示，search_string配置选项是“用于搜索用户的查询字符串，其中[search]由登录字段中的搜索文本直接替换”，例如“uid
= [search]”。然后将LDAP查询传递给连接到LDAP服务并执行ldap_search的LdapClient的simple_search方法。

/libraries/vendor/joomla/ldap/src/LdapClient.php

    
    
    class LdapClient
    {
        public function simple_search($search)
        {
            $results = explode(';', $search);
            foreach ($results as $key => $result)
            {
                $results[$key] = '(' . $result . ')';
            }
            return $this->search($results);
        }
        public function search(array $filters, ...)
        {
            foreach ($filters as $search_filter)
            {
                $search_result = @ldap_search($res, $dn, $search_filter, $attr);
                ⋮
            }
        }
    }

用户输入与LDAP查询标记混合，并将其传递给敏感的ldap_search函数。

  

**PoC**

LDAP查询中使用的用户名缺乏对输入内容的过滤，允许构造恶意内容进行LDAP查询。通过使用通配符和通过观察不同的身份验证错误消息，攻击者可以逐字地搜索登录凭据，方法是逐个发送一行有意义的字符串去不断猜测。

    
    
    XXX;(&(uid=Admin)(userPassword=A*))
    XXX;(&(uid=Admin)(userPassword=B*))
    XXX;(&(uid=Admin)(userPassword=C*))
    ...
    XXX;(&(uid=Admin)(userPassword=s*))
    ...
    XXX;(&(uid=Admin)(userPassword=se*))
    ...
    XXX;(&(uid=Admin)(userPassword=sec*))
    ...
    XXX;(&(uid=Admin)(userPassword=secretPassword))

每一个测试用例会之后返回2种不同的结果，以此结果判断每一位的正确与否。当然我们还要考虑到绕过filter的问题，这里就不详细展开介绍了。利用优化后的payload，可以高效的实现LDAP盲注。

**演示视频**

**修复建议**

升级至3.8版本

**时间线**

2017/07/27 向厂商提交漏洞详情及PoC

2017/07/29 厂商确认该安全问题

2017/09/19 厂商发布修复版本

本文翻译自ripstech.com [原文链接](https://blog.ripstech.com/2017/joomla-takeover-in-20-seconds-with-ldap-injection-cve-2017-14596/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **童话** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86899](/post/id/86899)

安全客 - 有思想的安全新媒体

本文转载自: [ripstech.com](https://blog.ripstech.com/2017/joomla-takeover-in-20-seconds-with-ldap-injection-cve-2017-14596/)

如若转载,请注明出处： <https://blog.ripstech.com/2017/joomla-takeover-in-20-seconds-with-ldap-injection-cve-2017-14596/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t01708a2424ae9882be.jpg) 童话

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

