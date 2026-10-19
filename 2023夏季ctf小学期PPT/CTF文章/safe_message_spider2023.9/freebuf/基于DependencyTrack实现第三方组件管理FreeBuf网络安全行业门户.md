### 本文作者：Pamela@涂鸦智能安全实验室

# 前言

在日常安全工作中，我们可能会经常遇到以下两个比较典型的场景：

场景1:如果某天某个第三方组件爆出了安全漏洞，那么如何在最短的时间里确认：

> 我们有这么多开发组，有没有哪个团队在用这个第三方组件？
>
> 用了这个第三方组件的团队，他们使用的组件的版本是否受此次漏洞影响？

场景2：各个团队当前使用的第三方组件的情况各不相同，从全局风险的角度来看，当前这些被使用的第三方组件的安全状况如何？例如：

> 是否有团队在使用含有已知安全漏洞的组件？
>
> 是否某个被使用的第三方组件已经过时？
>
> 是否某个或某些组件不合规或者存在风险？

基于以上场景，DependencyTrack应运而生。第三方组件管理在是开发安全中非常重要的一环，在上篇文章《浅谈软件成分分析（SCA）在企业开发安全建设中的落地思路》中，我们介绍过开源软件的风险以及在企业开发安全建设中的落地思路，并且在里面也有提到开源工具Dependency
Track，不过只是简单提了一下，没有过多深入。而在这篇文章中，我们将重点介绍DependencyTrack的概念、以及使用。

# Dependency Track

### 基本概念

Dependency-Track是OWASP推出的一个智能供应链组件分析平台，它集成了4种漏洞数据库：NPM Public
Advisories、National Vulnerability Database、Sonartype OSS
Index和VulnDB，帮助组织识别和减少使用第三方和开源组件的风险。

### Dependency Track VS Dependency check

可能你听说过甚至用过开源社区OWASP出品的DependencyCheck这款开源工具来扫描软件中的第三方组件（也叫‘依赖’）的安全性，可是今天我们要讲的不是这个工具，而是另一款名字和它非常相似的工具：DependencyTrack，同样也是OWASP出品。

这两个工具就一字之差，Dependency **Check** 和Dependency **Track** ，都是做依赖安全检查的，有啥本质区别？简单讲，
**如果说DependencyCheck是给开发团队使用的工具，那么DependencyTrack更多的是给安全团队使用的工具。企业或者组织中的安全团队可以借助DependencyTrack实现第三方组件的统一安全管理。**

![1630727301_6132ec85b7611e3bc98e1.png!small?1630727304056](https://image.3001.net/images/20210904/1630727301_6132ec85b7611e3bc98e1.png!small?1630727304056)

通过以上的对比可以知道的是，这两个工具都可以检测出第三方组件的安全问题，不过本质区别在于， **DependencyCheck**
只能对第三方组件做安全检测并生成报告，仅此而已。Dependency **Track**
会保存历次第三方组件安全检测结果，你可以通过Dashboard了解或者追踪第三方组件的安全变化趋势。与此同时，Dependency **Track**
还提供了很多额外的功能，例如漏洞通知、全局审查第三方组件、审计第三方组件软件授权协议、API等等。

### 检测原理

从下图中，可以看到Dependency Track通过接收到生成的Software
BOM(软件物料清单)，然后检查物料清单中的各个组件(以及当前清单中的版本)在漏洞数据库中是否存在已知安全漏洞的记录，并通过Dashboard展示出来。所以你需要先准备好一份SBOM清单，然后发送给Dependency
Track，等待它完成扫描检测之后，然后在管理界面上查看结果。

![1630727392_6132ece0c83a19c6873a8.png!small?1630727394347](https://image.3001.net/images/20210904/1630727392_6132ece0c83a19c6873a8.png!small?1630727394347)

你可能会问，SBOM是什么？SBOM（Software Bill of
Material）翻译之后称为软件物料清单。通俗的解释就是我们用到的所有第三方组件依赖（包括第三方组件自己所依赖的其他第三方组件，换句话讲，依赖的依赖）的信息清单，这些内容包括author、group,
licenses, versions and copyright等数据。

生成SBOM的工具有几个，其中比较有名的是CycloneDX。一旦我们有了BOM文件，我们就可以手动或通过整合CI/CD中的上传功能将其上传到Dependency-Track。Dependency
track相当于一个漏洞库和分析引擎，它基于SBOM，在漏洞库中搜索，这样我们就可以获得比传统组件分析更完整、更复杂的信息。

### 核心架构

如图所示，Dpendency Track可以轻松集成到我们的CI/DC流程中。

![1630727498_6132ed4a693374c4d0958.png!small?1630727505675](https://image.3001.net/images/20210904/1630727498_6132ed4a693374c4d0958.png!small?1630727505675)

Dependency Track默认集成了NVD、NPM Public Advisories、Sonatype OSS Index以及VulnDB
四个漏洞库，相比于其他开源检测工具单一的漏洞库，Dependency
Track出现漏报或者误报的情况会小很多。同时它提供了强大的API集成功能（如openAPI和Jenkins的插件），在开发安全建设过程中我们可以将其整合到我们的pipeline中帮助DevOps团队提高开发流程速度，同时还能控制外部组件的使用和它们可能造成的风险。此外通过maven收集仓库中所有依赖包的信息，记录各个开发团队的应用程序所使用的各种第三方依赖信息，以便进行依赖包管理（版本控制、漏洞管理等）。在开发过程中可以基于soner
bug追踪的组件安全跟踪，甚至fortify这样的代码白盒review介入，并通过邮件、钉钉告警通知安全团队、开发团队。

下面我们将通过简单的使用来感受一下。

## 基本使用

## 部署

DependencyCheck支持3种部署方式，分别是容器化部署、自运行安装包，以及可以直接在Tomcat里运行的WebApp包，此处以docker部署为例。

    
    
    # 下载DependencyTrack镜像
    docker pull owasp/dependency-track
    
    # 创建并使用宿主机上的存储以避免数据丢失
    docker volume create --name dependency-track
    
    # 在8080端口上运行DependencyTrack，默认账户密码admin/admin
    docker run -d -m 8192m -p 8080:8080 --name dependency-track -v dependency-track:/data owasp/dependency-track
    

更换默认数据库（可选）

    
    
    #1.根路径新建dependency-track目录，然后在该目录下新建application.properties文件，在文件中填写下面配置
    alpine.database.mode=external
    alpine.database.url=jdbc:postgresql://localhost:5432/dtrack
    alpine.database.driver=org.postgresql.Driver
    alpine.database.username=dtrack
    alpine.database.password=password
    #2.使用命令docker-compose up重新启动一下，配置就生效了，启动时间可能略长。参考：<https://docs.dependencytrack.org/getting-started/database-support/>
    

这里输入账号和密码之后，会要求更改密码。正常输入账号密码之后就可以进入管理界面了，这里有一丢丢慢。。

![1630727575_6132ed97afe4ca06eb6a1.png!small?1630727576711](https://image.3001.net/images/20210904/1630727575_6132ed97afe4ca06eb6a1.png!small?1630727576711)

进去之后，新建一个项目，如图所示：

![1630727614_6132edbed7ef3d544200e.png!small?1630727616241](https://image.3001.net/images/20210904/1630727614_6132edbed7ef3d544200e.png!small?1630727616241)

接下来我们需要做的就是使用插件对代码项目生成bom.xml，类似pip request requirements，清点出使用的组件。Dependency
track相当于一个漏洞库和分析引擎，这个方法好处就是只需要在客户端直接生成bom.xml，PUT track的REST接口即可。

总结起来分为两步：

  1. 生成bom.xml文件
  2. 将生成的bom.xml文件上传到Dependency-Track

有很多工具可以帮我们生成SBOM，例如CycloneDX Maven Plugin和cyclonedx-gradle-plugin，因为我采用Jenkins做构建工具，故此处使用OWASP Dependency-Track插件来生成SBOM。

首先，需要在jenkins中安装 OWASP Dependency-Track插件，搜索OWASP，第一个便是，选择安装即可。

![1630727658_6132edea1ccdbd5f7e61e.png!small?1630727661412](https://image.3001.net/images/20210904/1630727658_6132edea1ccdbd5f7e61e.png!small?1630727661412)

安装成功后，我们需要新建一个job,点击进入配置里面，可以看到Publish BOM to Dependency-Track这一项，这个插件可以在执行一些操作后，将扫描出的三方依赖相关信息上传到Dependency-Track的服务里面，以便于分析。

接着在jenkins的job配置中做如下事情：

  1. 在源码管理模块配置拉取代码
  2. 在构建模块，选择Excute shell填写如下内容

    
    
    # 打包
    mvn clean install -D mvn.test.skip=true
    # 生成bom.xml文件
    mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom
    

  1. 构建后在操作模块，选择Publish BOM to Dependency-Track，填写生成bom.xml的路径，具体如下

![1630731787_6132fe0bf1753fcd2888e.png!small?1630731793218](https://image.3001.net/images/20210904/1630731787_6132fe0bf1753fcd2888e.png!small?1630731793218)

最后，在配置完成后构建job,构建完成后即可在Dependency-Track的web页面看到上传的结果，包括项目的组件，三方依赖的漏洞信息等等内容，然后可根据分析结果进行针对性修复。其他配置可参考<https://docs.dependencytrack.org/>

这里如果推送失败的话，可以试下这个脚本。

    
    
    try {
        $xml = Get-Content (Join-Path $PSScriptRoot ".\\bom.xml") –Raw
        $ProjectGuid = "xxx"
        $ApiKey = "xxx”
        $Uri = "<http://localhost:8080>"
    
        $Body = ([PSCustomObject] @{
                project = $ProjectGuid
                bom     = ([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($xml)))
            } | ConvertTo-Json)
    
        $Header = @{ 'X-API-Key' = $ApiKey }
    
        Invoke-RestMethod –Method Put –Uri "$Uri/api/v1/bom" –Headers $Header  –ContentType "application/json" –Body $Body
    }
    catch {
        Write-Host $_
    }
    

## 卸载

    
    
    docker rmi owasp/dependency-track
    docker rm dependency-track
    docker volume rm dependency-track:/data
    

# Reference

> [docs.dependencytrack.org](http://docs.dependencytrack.org/)
>
> <https://zhuanlan.zhihu.com/p/269080779>
>
> https://mp.weixin.qq.com/s/_6G3gQHKoTmFKkdiE2gBLg
>
> <https://medium.com/devroot/deploying-dependency-track-as-a-container-in-> azure-and-building-a-pipeline-with-azure-devops-ab1627961114>
>
>  **漏洞悬赏计划：涂鸦智能安全响应中心（https://src.tuya.com）欢迎白帽子来探索。**
>
>
> 招聘内推计划：涵盖安全开发、安全测试、代码审计、安全合规等所有方面的岗位，简历投递[sec@tuya.com](mailto:sec@tuya.com)，请注明来源。

  

  

