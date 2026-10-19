**2020年4月28日，GitLab的一个任意文件读取漏洞的漏洞细节被公开。该漏洞补丁于2020年3月26号由GitLab官方发布。**

## 相关组件介绍

GitLab
是一个用于仓库管理系统的开源项目，使用Git作为代码管理工具，并在此基础上搭建起来的web服务。GitLab是由GitLabInc.开发，使用MIT许可证的基于网络的Git仓库管理工具，且具有wiki和issue跟踪功能。

## 漏洞分析

当GitLab的项目之间发生issue移动时，UploadsRewriter模块会将本地的issue及issue引用的文件移动到新的项目中。执行该操作的部分代码如下所示:

![](https://image.3001.net/images/20200507/1588852278_5eb3f63696f67.png!small)

该部分代码没有对issue引用的文件做任何路径限制，因此存在一个目录穿越漏洞。通过该目录穿越漏洞可以从GitLab服务器上拷贝任意文件到新的issue中。此过程存在一个查找引用文件的判断:

    
    
    MARKDOWN_PATTERN=%r{\!?\[.*?\]\(/uploads/(?<secret>[0-9a-f]{32})/(?<file>.*?)\)}.freeze

该正则表达式用于匹配issue中引用的文件。尽管此处对引用的文件路径有一定的限制，但是并没有解决目录穿越的问题，从而导致攻击者可以利用该漏洞从服务器主机上下载任意文件。

## 受影响版本

> GitLab GitLab EE >=8.5，<=12.9
>
> GitLab GitLab CE >=8.5，<=12.9

## 检测方式

使用如下命令检测当前GitLab版本：

> cat /opt/gitlab/embedded/service/gitlab-rails/VERSION

若检测当前版本在受影响范围内，则存在上述安全风险。

## 修复建议

官方已在最新版本的GitLab修复了上述漏洞，用户可从官网下载并升级软件到最新版本。

链接：<https://packages.gitlab.com/gitlab/gitlab-ce>

## 时间轴

> 2020/3/26 GitLab发布更新补丁
>
> 2020/4/28 漏洞细节被公开
>
> 2020/5/7 深信服千里目安全实验室发布漏洞分析文章。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

