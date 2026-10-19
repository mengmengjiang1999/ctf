***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

DependencyTrack
是一个开源的软件供应链组件分析平台，使组织能够识别和减少使用第三方和开源组件的风险。它通过利用软件物料清单（SBOM，Software Bill-of-Materials）的功能采取了独特方法。这种方法提供了传统软件组成分析（SCA）解决方案无法实现的功能。Dependency-Track
监视产品组合中每个应用程序所有版本的组件使用情况，以便主动识别整个组织的风险。该平台采用API优先设计，非常适合在持续集成和持续交付（CI/CD）环境中使用。

DependencyTrack 官方地址：<https://dependencytrack.org/>

##  **安装部署**

DependencyTrack支持Docker方式部署，可以快速搭建使用环境。

![](https://image.3001.net/images/20210609/1623226639_60c0790fbcd88e4bbd396.png!small)

##  ** **初始化启动****

首次启动 Dependency-Track 时，会发生多项任务，包括：

> 生成默认对象，例如用户，团队和权限。
>
> 生成用于 JWT 令牌创建和验证的密钥。
>
> 填充 CWE 和 SPDX 许可证数据。
>
> 初始化镜像所有受支持的漏洞数据源。

初始化镜像可能需要 10 到 30 分钟或更长时间。不要中断该过程。在关闭系统之前，请等待所有镜像任务的完成。可以通过查看 “dependency-track.log” 来监视这些任务。初始化完成后查看_data/.dependency-track/目录，已经生成数据库文件（*.db）和一些漏洞库文件（nist/*.json）。

![1623226875_60c079fb5e328ef00461a.png!small](https://image.3001.net/images/20210609/1623226875_60c079fb5e328ef00461a.png!small)

##  **Dependency-Track使用**

1\. 检查软件依赖的基本步骤

1）生成SBOM（软件物料清单）

2）提交SBOM到DependencyTrack

3）在DependencyTrack中查看分析结果

2\. 生成SBOM（软件物料清单）

以json-iterator项目为例（Java和Go中可用的快速灵活的JSON解析器 ）根据官方的推荐使用CycloneDX
BOMs，本次实验使用cyclonedx-maven-plugin 插件生成bom.xml文件。

1）json-iterator目录结构如下，使用pom.xml（项目对象模型）生成Bom.xml.

![1623227180_60c07b2ca99993279f2cc.png!small](https://image.3001.net/images/20210609/1623227180_60c07b2ca99993279f2cc.png!small)

2）在pom.xml中<plugins>标签中添加cyclonedx-maven-plugin 插件。内容如下：

    
    
    <plugin>
    
    <groupId>org.cyclonedx</groupId>
    
    <artifactId>cyclonedx-maven-plugin</artifactId>
    
    <version>2.5.1</version>
    
    <executions>
    
    <execution>
    
    <phase>package</phase>
    
    <goals>
    
    <goal>makeAggregateBom</goal>
    
    </goals>
    
    </execution>
    
    </executions>
    
    <configuration>
    
    <projectType>library</projectType>
    
    <schemaVersion>1.3</schemaVersion>
    
    <includeBomSerialNumber>true</includeBomSerialNumber>
    
    <includeCompileScope>true</includeCompileScope>
    
    <includeProvidedScope>true</includeProvidedScope>
    
    <includeRuntimeScope>true</includeRuntimeScope>
    
    <includeSystemScope>true</includeSystemScope>
    
    <includeTestScope>false</includeTestScope>
    
    <includeLicenseText>false</includeLicenseText>
    
    <outputFormat>all</outputFormat>
    
    <outputName>bom</outputName>
    
    </configuration>
    
    </plugin>

3）mvn命令生成bom.xml

 **
**![1623227513_60c07c794b2b9fb3e6598.png!small](https://image.3001.net/images/20210609/1623227513_60c07c794b2b9fb3e6598.png!small)****

3\. 提交SBOM到DependencyTrack

1）创建项目

![1623227770_60c07d7a0dba2aacec76b.png!small](https://image.3001.net/images/20210609/1623227770_60c07d7a0dba2aacec76b.png!small)

2）. 上传bom.xml

![1623227908_60c07e04ef4d683fb568c.png!small](https://image.3001.net/images/20210609/1623227908_60c07e04ef4d683fb568c.png!small)

4\. DependencyTrack中查看分析结果

通过Audit Vulnerabilities查看分析结果，严重：22个，高危35个，中危3个，低危0个。

![1623228048_60c07e9029bb3c347ac33.png!small](https://image.3001.net/images/20210609/1623228048_60c07e9029bb3c347ac33.png!small)

