![](https://image.3001.net/images/20200415/1586880250_5e95defa6005b.png!small)

##  GitHound

**GitHound可以利用模式匹配、提交历史楼所和一个独特的结果评分系统来精确定位GitHub上的公开API密钥，从本质上来说，GitHound就是一款基于批量爬取、模式匹配和补丁攻击的敏感数据搜索工具。**

值得一提的是，目前为止在GitHound的帮助下，我已经成功拿到了超过7500美元的漏洞奖金了。

##  功能介绍

> 1、GitHub/Gist代码搜索。这个功能将允许GitHound搜索GitHub中用户上传的所有代码库，并准确定位到敏感信息所在的位置。
>
> 2、通用APK密钥检测，该功能使用了模式匹配、上下文检索和香农熵。
>
> 3、提交历史搜索，该功能可以找到没有正确删除的敏感信息。
>
> 4、评分系统，可以返回更加准确的结果，过滤常见的误报，并优化密集型代码库挖掘结果。
>
> 5、Base64检测和解码。
>
> 6、可将GitHound构建整合进我们自己的工作流中。

##  工具下载

广大研究人员可以使用下列命令将GitHound项目源码克隆至本地：

    
    
    git clone https://github.com/tillson/git-hound.git

##  工具安装

使用我们自己的GitHub用户名和密码创建一个./config.yml或~/.githound/config.yml文件，目前还不支持使用开启了双因素身份验证的账号。

样本config.example.yml文件格式如下：

    
    
    # Required
    
        github_username: tillson
    
        github_password: a8ueifjq4jkasdfoiulk

然后运行下列命令：

    
    
    echo "tillsongalloway.com" | git-hound

##  工具使用

    
    
    echo "tillsongalloway.com" | git-hound or git-hound --subdomain-file subdomains.txt

##  使用样例

###  搜索公开的用户API密钥

通过了解特定服务的API密钥的模式，我们将能够使用GitHound来搜索GitHub中的这些公开用户API密钥。然后，我们可以将自定义的密钥正则表达式整合进我们的脚本中，然后针对目标服务API密钥来标识有风险的账户。

    
    
    echo "api.halcorp.biz" | githound --dig --many-results --regex-file halcorp-api-regexes.txt --results-only | python halapitester.py

###  漏洞奖励：搜索泄露的员工API令牌

对于我个人来说，GitHound的主要用途就是针对漏洞奖励计划来搜索敏感信息。对于某些重要目标，我们可以使用--many-results和--languages来搜索>100页得结果。

    
    
    echo "uberinternal.com" | githound --dig --many-results --languages common-languages.txt --threads 100

##  工具选项

> \--subdomain-file - 包含子域名的文件；
>
> \--dig-files - 克隆并搜索目标代码库中的文件以获取结果；
>
> \--dig-commits - 克隆并搜索目标代码库中的提交历史以获取结果；
>
> \--many-results - 使用结果排序和过滤搜索超过100页的结果；
>
> \--results-only - 仅将正则匹配得结果打印到stdout，用于将自定义正则表达式匹配项管道化到另一个脚本中；
>
> \--no-repos - 指定不需要搜索的代码库；
>
> \--no-gists - 指定不需要搜索的Gist；
>
> \--threads -指定提交挖掘程序要使用的最大线程数；
>
> \--regex-file - 提供自定义正则表达式文件；
>
> \--language-file - 提供带有要搜索的语言的自定义文件；
>
> \--config-file - 自定义配置文件（默认为config.yml）；
>
> \--pages - 要搜索的最大页面数（默认值为100）；
>
> \--no-scoring - 不使用评分来过滤假阳性；
>
> \--no-api-keys -> 不执行通用api密钥搜索。GitHound使用常见的API密钥模式、上下文检索和香浓熵过滤器来查找潜在的公开API密钥；
>
> \--no-files - 不标记感兴趣的文件扩展名；
>
> \--only-filtered - 仅搜索筛选查询（语言）；
>
> \--debug - 打印详细的调试消息；

##  项目地址

> GitHound：【[GitHub传送门](https://github.com/tillson/git-hound)】

 *** 参考来源：[tillson](https://github.com/tillson/git-hound)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

