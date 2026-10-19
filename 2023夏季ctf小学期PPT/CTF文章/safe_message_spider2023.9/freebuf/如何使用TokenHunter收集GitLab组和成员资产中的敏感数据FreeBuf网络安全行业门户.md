![](https://image.3001.net/images/20210130/1612020154_601579ba514d6e987a6bb.jpg!small)

## Token-Hunter

Token-Hunter是一款针对[ _GitLab组_](https://docs.gitlab.com/ee/user/group/)和
_成员_的OSINT开源情报收集工具，该工具基于Python3开发在该工具的帮助下，广大研究人员可以轻松分析组和组成员之间的[
_代码段_](https://docs.gitlab.com/ee/user/snippets.html)、[
_问题_](https://docs.gitlab.com/ee/user/project/issues/)和
_问题讨论_等内容，并从这些资产中收集潜在的敏感信息。收集到的信息旨在补充其他工具使用的相关信息，比如说[
_TruffleHog_](https://github.com/dxa4481/truffleHog)或[
_GitRob_](https://github.com/michenriksen/gitrob)，而这些工具可以使用类似正则表达式匹配技术来搜索git提交历史。

## 工具运行机制

通过提供GitLab中特定组的组ID（我们可以在GitLab UI界面组名称下找到组ID），Token-Hunter将会使用GitLab组ID来查找跟这个组相关的所有项目以及组成员的个人项目。除此之外，我们还可以配置该工具来寻找项目相关资产中的敏感数据。Token-Hunter使用了跟[
_TruffleHog相同的一组正则表达式_](https://github.com/dxa4481/truffleHogRegexes)，并且还可以指定GitLab特定的令牌。Token-Hunter依赖于这些[ _易于配置的正则表达式_](https://gitlab.com/gitlab-com/gl-security/gl-redteam/token-hunter/blob/master/regexes.json)来获得更加准确和有效的搜索结果。目前，该工具支持GitLab代码段、问题以及问题讨论，之后还会增加针对更多资产的支持。该工具允许研究人员进行高度自定义配置，以便在特别感兴趣的资产中高效地发现敏感数据。

## 工具使用

在运行该工具之前，我们需要生成一个GitLab个人访问令牌（PAT），并将其以环境变量的形式导出：

    
    
    export GITLAB_API_TOKEN=xxxxx

接下来，使用下列命令将该项目源码克隆至本地，并完成依赖组件的安装：

    
    
    git clone https://gitlab.com/gitlab-com/gl-security/gl-redteam/token-hunter.git
    
    pip3 install -r ./requirements.txt

然后，我们就可以根据自己的需要来运行该工具并指定执行参数了：

    
    
    usage: token-hunter.py [-h] -g GROUP [-u URL] [-m] [-s] [-i] [-r] [-t]
    
                           [-p PROXY] [-c CERT] [-l LOGFILE]
    
     
    
    Collect OSINT for GitLab groups and members. Optionally search the group and
    
    group members snippets, project issues, and issue discussions/comments for
    
    sensitive data.
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -u URL, --url URL     An optional argument to specify the base URL of your
    
                            GitLab instance. If the argument is not supplied, its
    
                            defaulted to 'https://gitlab.com'
    
      -m, --members         Include group members personal projects and their
    
                            related assets in the searchfor sensitive data.
    
      -s, --snippets        Searches found projects for GitLab Snippets with
    
                            sensitive data.
    
      -i, --issues          Searches found projects for GitLab Issues and
    
                            discussions/comments with sensitive data.
    
      -r, --mergerequests   Searches found projects for GitLab Merge Requests and
    
                            discussions/comments with sensitive data.
    
      -t, --timestamp       Disables display of start/finish times and originating
    
                            IP to the output
    
      -p PROXY, --proxy PROXY
    
                            Proxies all requests using the provided URI matching
    
                            the scheme: http(s)://user:pass@10.10.10.10:8000
    
      -c CERT, --cert CERT  Used in tandem with -p (--proxy), this switch provides
    
                            a fully qualified path to a certificate to verify TLS
    
                            connections. Provide a fully qualified path to the
    
                            dynamic cert. Example:
    
                            /Users/<username>/owasp_zap_root_ca.cer.
    
      -l LOGFILE, --logfile LOGFILE
    
                            Will APPEND all output to specified file.
    
     
    
    required arguments:
    
      -g GROUP, --group GROUP
    
                            ID or HTML encoded name of a GitLab group. This
    
                            option, by itself, will display group projects and
    
                            member names only.

## 工具使用样例

该工具最简单的使用场景就是返回跟目标组ID相关联的所有项目的URL地址，这里使用的是-g选项。我们可以在GitLab
UI界面组名称下找到组ID，该配置下Token-Hunter不会搜索令牌：

    
    
    ./token-hunter.py -g 123456

查找跟组123456相关的所有项目以及组成员的个人项目，该配置下Token-Hunter不会搜索令牌：

    
    
    ./token-hunter.py -g 123456 -m

查找跟组123456相关的所有项目以及组成员的个人项目，-s选项将会让Token-Hunter搜索跟每一个项目相关的GitLab代码段，并查找项目中的敏感数据：

    
    
    ./token-hunter.py -g 123456 -msir

查找跟组123456相关的所有项目以及组成员的个人项目，-s选项将会让Token-Hunter搜索跟每一个项目相关的GitLab代码段，并查找项目中的敏感数据。-i选项将让Token-Hunter搜索跟每一个项目相关的问题以及问题讨论，并查找项目中的敏感数据（该模式下可能会导出大量数据，慎用！）：

    
    
    ./token-hunter.py -g 123456 -msit -u https://mygitlab-instance.com -p http://127.0.01:8080 -c /Users/hacker/owasp_zap_ca_cert.cer -l ./appended-output.txt

## 项目地址

Token-Hunter：【[ _GitHub传送门_](https://github.com/codeEmitter/token-hunter)】

