![](https://image.3001.net/images/20230605/1685957455_647dab4f0f2880d864409.png!small)  

## 关于NoseyParker

NoseyParker是一款功能强大的命令行工具，该工具可以帮助广大研究人员在文本数据中寻找敏感信息，可以用于网络安全攻防两端的安全测试过程中。

## 关键功能

> 1、支持扫描Git代码库中的文件、目录和整个历史记录；
>
> 2、使用了正则表达式与一组包含了99种预定义模式的记录相匹配，这些模式是根据网络安全攻防两端行动的经验和反馈而生成的，具有高信噪比特征；
>
> 3、支持将共享相同敏感数据的匹配组合在一起；
>
> 4、运行速度非常快，可以在单核CPU上以每秒数百兆字节的速度扫描，并且能够在不到2分钟的时间内在旧版MacBook
> Pro上扫描100GB的Linux内核源历史记录；

## 工具安装

### 预构建代码

本项目提供了针对x86_64 Linux和x86_64/ARM64 macOS操作系统的预构建代码，可以直接访问该项目的【[
_Releases页面_](https://github.com/praetorian-inc/noseyparker/releases/latest)】获取最新版本的NoseyParker，这种方式也是最简单最直接的使用方法了，能够实现较好的运行性能。

### Docker镜像

该项目提供了针对多平台预构建的Docker镜像，支持x86_64和ARM64架构：

    
    
    docker pull ghcr.io/praetorian-inc/noseyparker:latest

或

    
    
    docker pull ghcr.io/praetorian-inc/noseyparker:edge

## 工具使用

    
    
    docker run -v "$PWD":/opt/ ghcr.io/praetorian-inc/noseyparker:latest <ARGS>

### 扫描文件系统内容以识别敏感数据

比如说，你将CPython项目克隆到了本地，我们就可以使用scan命令来扫描整个历史记录，并创建一个新的数据存储（--datasotre）来存储扫描结果（np.cpython）：

    
    
    $ noseyparker scan --datastore np.cpython cpython.git
    
    Found 28.30 GiB from 18 plain files and 427,712 blobs from 1 Git repos [00:00:04]
    
    Scanning content  ████████████████████ 100%  28.30 GiB/28.30 GiB  [00:00:53]
    
    Scanned 28.30 GiB from 427,730 blobs in 54 seconds (538.46 MiB/s); 4,904/4,904 new matches
    
     
    
     Rule                      Distinct Groups   Total Matches
    
    ───────────────────────────────────────────────────────────
    
     PEM-Encoded Private Key             1,076           1,192
    
     Generic Secret                        331             478
    
     netrc Credentials                      42           3,201
    
     Generic API Key                         2              31
    
     md5crypt Hash                           1               2
    
     
    
    Run the `report` command next to show finding details.

### 通过URL、GitHub用户名或GitHub组织名称扫描Git库

比如说，下列命令可以直接扫描NoseyParker的Git代码库：

    
    
    $ noseyparker scan --datastore np.noseyparker --git-url https://github.com/praetorian-inc/noseyparker

或者，扫描属于octocat组织的所有公开可访问的代码库：

    
    
    $ noseyparker scan --datastore np.noseyparker --github-user octocat

### 扫描结果概览

    
    
    $ noseyparker summarize --datastore np.cpython
    
     
    
     Rule                      Distinct Groups   Total Matches
    
    ───────────────────────────────────────────────────────────
    
     PEM-Encoded Private Key             1,076           1,192
    
     Generic Secret                        331             478
    
     netrc Credentials                      42           3,201
    
     Generic API Key                         2              31
    
     md5crypt Hash                           1               2

### 报告详细发现

    
    
    $ noseyparker report --datastore np.cpython
    
    Finding 1/1452: Generic API Key
    
    Match: QTP4LAknlFml0NuPAbCdtvH4KQaokiQE
    
    Showing 3/29 occurrences:
    
     
    
        Occurrence 1:
    
        Git repo: clones/cpython.git
    
        Blob: 04144ceb957f550327637878dd99bb4734282d07
    
        Lines: 70:61-70:100
    
     
    
            e buildbottest
    
     
    
            notifications:
    
              email: false
    
              webhooks:
    
                urls:
    
                  - https://python.zulipchat.com/api/v1/external/travis?api_key=QTP4LAknlFml0NuPAbCdtvH4KQaokiQE&stream=core%2Ftest+runs
    
                on_success: change
    
                on_failure: always
    
              irc:
    
                channels:
    
                  # This is set to a secure vari
    
     
    
        Occurrence 2:
    
        Git repo: clones/cpython.git
    
        Blob: 0e24bae141ae2b48b23ef479a5398089847200b3
    
        Lines: 174:61-174:100
    
     
    
            j4 -uall,-cpu"
    
     
    
            notifications:
    
              email: false
    
              webhooks:
    
                urls:
    
                  - https://python.zulipchat.com/api/v1/external/travis?api_key=QTP4LAknlFml0NuPAbCdtvH4KQaokiQE&stream=core%2Ftest+runs
    
                on_success: change
    
                on_failure: always
    
              irc:
    
                channels:
    
                  # This is set to a secure vari
    
    ...

### 枚举GitHub代码库

    
    
    $ noseyparker github repos list --user octocat
    
    https://github.com/octocat/Hello-World.git
    
    https://github.com/octocat/Spoon-Knife.git
    
    https://github.com/octocat/boysenberry-repo-1.git
    
    https://github.com/octocat/git-consortium.git
    
    https://github.com/octocat/hello-worId.git
    
    https://github.com/octocat/linguist.git
    
    https://github.com/octocat/octocat.github.io.git
    
    https://github.com/octocat/test-repo1.git

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2_ _._ _0_](https://github.com/praetorian-inc/noseyparker/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **NoseyParker** ：【[ _GitHub传送门_](https://github.com/praetorian-inc/noseyparker)】

## 参考资料

> [ _https://praetorian.com/_](https://praetorian.com/)
>
> [ _https://www.praetorian.com/blog/nosey-parker-ai-secrets-scanner-> release/_](https://www.praetorian.com/blog/nosey-parker-ai-secrets-scanner-> release/)
>
> [ _https://www.praetorian.com/blog/six-months-of-finding-secrets-with-nosey-> parker/_](https://www.praetorian.com/blog/six-months-of-finding-secrets-> with-nosey-parker/)

