![](https://image.3001.net/images/20210312/1615557172_604b72344880fb12072ff.png!small)

## 关于GitLab Watchman

GitLab Watchman这款应用程序可以帮助广大研究人员使用GitLab API来审查GitLab内部暴露的敏感数据和凭据。

## 功能介绍

GitLab Watchman可以搜索GitLab中的内部共享项目，并查看下列内容：

  * 代码；
  * 提交内容；
  * WiKi页面；
  * 问题；
  * 合并请求；
  * 项目里程碑；

GitLab Watchman支持搜索下列内容：

  * GCP密钥和服务帐户文件；
  * AWS密钥；
  * Azure密钥和服务帐户文件；
  * Google API密钥；
  * Slack API令牌&webhooks；
  * 私钥（SSH、PGP、任何其他杂项私钥）；
  * 公开的令牌（Bearer令牌、访问令牌和client_secret等）；
  * S3配置文件；
  * Heroku、PayPal等服务的令牌；
  * 明文密码；
  * ...

## 基于事件的搜索

我们还可以运行GitLab Watchman并搜索下列时间间隔返回的数据结果:

  * 24小时；
  * 7天；
  * 30天；
  * 所有时间；

这也就意味着，在一次深度扫描之后，我们可以安排GitLab Watchman定期运行，并且只返回所选时间段的结果。

## 规则

GitLab Watchman使用自定义YAML规则来检测GitLab中的匹配数据项。

 **规则格式如下所示：**

    
    
    ---    
    filename:
    
    enabled: #[true|false]
    
    meta:
    
      name:
    
      author:
    
      date:
    
      description: #what the search should find#
    
      severity: #rating out of 100#
    
    scope: #what to search, any combination of the below#
    
    - blobs
    
    - commits
    
    - milestones
    
    - wiki_blobs
    
    - issues
    
    - merge_requests
    
    test_cases:
    
      match_cases:
    
      - #test case that should match the regex#
    
      fail_cases:
    
      - #test case that should not match the regex#
    
    strings:
    
    - #search query to use in GitLab#
    
    pattern: #Regex pattern to filter out false positives#

项目中引入了Python测试来确保规则格式的正确性，项目目录中的tests目录下还包含正则匹配模式。关于检测规则的更多内容，请查看项目下的docs/rules.md文件。

## .conf文件

配置选项可以在watchman.conf文件中进行配置，该文件必须存储在项目的根目录下。该文件必须遵循YAML格式：

    
    
    gitlab_watchman:
    
      token: abc123
    
      url: https://gitlab.example.com
    
      logging:
    
        file_logging:
    
          path:
    
        json_tcp:
    
          host:
    
          port:

GitLab
Watchman将会在运行时查询该配置文件，并使用其中的配置信息。除此之外，本项目还提供了一份配置文件样本，路径为docs/example.conf。

## 工具要求

### GitLab版本

GitLab Watchman使用了v4 API，支持GitLab企业版：

  * GitLab.com
  * 13.0及其以上版本
  * 12.0-12.10版本

## 工具安装

广大研究人员可以使用下列命令安装GitLab Watchman：

    
    
    pip install gitlab-watchman

## 工具使用

GitLab Watchman将以全局命令的形式进行安装，可以通过下列方式使用：

    
    
    usage: gitlab-watchman [-h] --timeframe {d,w,m,a} --output
    
                       {file,stdout,stream} [--version] [--all] [--blobs]
    
                       [--commits] [--wiki-blobs] [--issues] [--merge-requests]
    
                       [--milestones] [--comments]
    
     
    
    Monitoring GitLab for sensitive data shared publicly
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      --version             show program's version number and exit
    
      --all                 Find everything
    
      --blobs               Search code blobs
    
      --commits             Search commits
    
      --wiki-blobs          Search wiki blobs
    
      --issues              Search issues
    
      --merge-requests      Search merge requests
    
      --milestones          Search milestones
    
      --comments            Search comments
    
     
    
    required arguments:
    
      --timeframe {d,w,m,a}
    
                            How far back to search: d = 24 hours w = 7 days, m =
    
                            30 days, a = all time
    
      --output {file,stdout,stream}
    
                            Where to send results

我们可以使用GitLab Watchman来查询所有支持的数据项，并将结果输出至默认Stdout：

    
    
    gitlab-watchman --timeframe a --all

或者，我们也可以将参数一起提交给搜索命令：

    
    
    gitlab-watchman --timeframe m --commits --milestones --output stream

## 项目地址

GitLab Watchman：【[ _GitHub传送门_](https://github.com/PaperMtn/gitlab-watchman)】

