## **一. DevOps概述**

DevOps 是 Development 和 Operations 组合的缩写词，它指的是一种协作方法，使企业的应用程序开发团队（Development
team）和 IT 运营团队（Operations
team）能够更好地沟通工作，DevOps的概念有助于使技术项目与业务需求保持一致，从而提高企业整体的工作效率 [1]。

###  **02.DevOps的价值**

DevOps通过自动化“软件交付”和“架构变更”的流程，使得构建、测试、发布软件能够更加快捷、频繁和可靠[2]。DevOps市场价值更是潜力无限，据GMI（GlobalMarket
Insights）的调查报告显示[3]（如图一）：“DevOps市场规模在2021 年已超过70 亿美元，并有望在2022 年至2028 年间，以超过20%
的复合年增长率增长。”由此可见，DevOps全球化、普遍化的趋势已不可阻挡，企业大规模敏捷开发转型将成为主流旋律。  
![48a491edbc724c02325f1b28539b80cf.png](https://image.3001.net/images/20220724/1658653901_62dd0ccd0018b41e20d92.png!small)图1
DevOps市场的价值

### 03DevOps常用工具

那么DevOps流程具体会涉及到哪些工具呢？通过分析2021年多个平台公布的DevOps工具的排名[4][5][6][7]，为大家总结了18款常用的DevOps工具。

> 项目管理和协作工具：Microsoftteams, Slack, JIRA
>
> 代码管理工具：BitBucket,GitLab, Github
>
> 持续集成工具：Jenkins
>
> 质量测试工具：Junit,Selenium,DATADOG
>
> 监控管理工具：NewRelic, Grafana
>
> 持续部署工具：OctopusDeploy, Spinnaker
>
> 配置管理工具：Chef,Ansible, Puppet,Terraform

结合图2，可以更清晰的了解到DevOps整个生命周期流程和各个工具在其中所充当的角色。  
![24fac9285df3303348af58722ef4c4ac.png](https://image.3001.net/images/20220724/1658653974_62dd0d1620b04672d6703.png!small)图2
DevOps流程示意图

##  **二. DevOps潜在的风险**

DevOps被越来越多企业接纳的同时，DevOps工具的风险也越发突出。我们通过获取了部分常用DevOps工具的指纹，利用网络搜索引擎对这些工具在国内的暴露量进行了调研。得到的具体暴露数据如表1所示：  
![3bdfead97809c969f5394e757de2cae8.png](https://image.3001.net/images/20220724/1658654034_62dd0d521e823cbf2fed3.png!small)

表1 DevOps国内暴露资产数

由此可见，DevOps工具暴露量相当之多，其中Jenkins和GitLab资产的暴露量尤为突出，那么它们背后潜在的风险又究竟是什么情况？下面具体对GitLab和Jenkins两个资产进行了资产风险测绘的研究。

## 三. GitLab资产风险风险

### 1.GitLab简介

GitLab是一个结合了在单个应用程序中开发、保护和操作软件能力的DevOps平台。GitLab最初是作为源代码管理解决方案在软件开发团队内进行协作，后来演变为涵盖整个DevOps
生命周期的集成解决方案，其注册用户已超过3000万人次 [8]

### 02.GitLab国内资产暴露情况

根据网络测绘数据，我们对国内GitLab资产暴露情况进行了统计，共计查询到9035个暴露的资产，下面将从地区分布、暴露端口两个维度分别进行介绍。

如图3所示，国内暴露的GitLab资产中约73.6%来源于北京市、上海市、广东省和浙江省这些省份和城市，其中北京市稳居第一，暴露资产数达到2566个。  
![65a080fd7fd72391a62701fa0cdbb1d1.png](https://image.3001.net/images/20220724/1658654281_62dd0e4905a37cc68ed51.png!small)图3
GitLab国内暴露资产分布图（地区维度）

从图4可见，国内暴露的GitLab资产使用的端口主要为443、8888、8090、8081和80，共占总数的69.5%，其中443端口暴露量最多，共计3201个，占比35.4%。  
![56dea2072305d07abe3b0576fa5bae3d.png](https://image.3001.net/images/20220724/1658654325_62dd0e750e457cdd28751.png!small)图4
GitLab国内暴露资产分布图（端口维度）

###  **03.GitLab国内资产漏洞分析**

GitLab会在官网不定期公布自己存在的CVE漏洞。我们梳理了2020到2021年 CVSSVersion3.x
评分高于或等于7分的GitLab漏洞，共计有86个，且其中9分以上漏洞多达20个，频率较多的漏洞类型有：DDoS、SSRF、未授权、信息泄露等。

由此可见GitLab资产存在较大的安全隐患。下面，以两个漏洞CVE-2021-22205（RCE漏洞）和CVE-2021-22214（SSRF漏洞）为例进行分析。

CVE-2021-22205漏洞

GitLab CVE-2021-22205属于RCE类型漏洞，其影响版本范围包括GitLab社区版和企业版：11.9.0≤ 版本号≤ 13.8.8 ;
13.9.0 ≤ 版本号≤ 13.9.6 ; 13.10.0 ≤ 版本号≤
13.10.3。这个漏洞源于GitLab没有正确验证传递给文件解析器的图像文件，这个疏忽导致了远程命令执行漏洞的可能性。

如图6所示，我们共发现了1051个暴露的GitLab资产存在CVE-2021-22205漏洞，约占暴露资产总数的11.6%，CVE-2021-22205属于远程命令执行漏洞，其在CVSS
Version3.x中评分高达9.8，可见其危害程度之大。

CVE-2021-22214漏洞

GitLab CVE-2021-22214属于SSRF类型漏洞，其影响版本范围包括GitLab社区版和企业版：

10.5 ≤ 版本号≤ 13.10.5 ; 13.11 ≤ 版本号≤ 13.11.5 ; 13.12 ≤ 版本号≤ 13.12.2。当启用对内部网络的
webhook 请求时，请求伪造漏洞可能被未经身份验证的攻击者利用（包括注册受限的GitLab）。

如图6所示，我们共发现了841个暴露的GitLab资产存在CVE-2021-22214漏洞，约占暴露资产总数的9.3%，CVE-2021-22214在CVSSVersion3.x评分中达到8.6分，其危害程度也不可小觑。CVE-2021-22214漏洞本地环境测试情况见图5。  
![684b2ff32ae661f6b8ec6800043bfff3.png](https://image.3001.net/images/20220724/1658654436_62dd0ee4950d33908b4d8.png!small)![2f21cee9a4cfc90be5e4d96653d962ed.png](https://image.3001.net/images/20220724/1658654448_62dd0ef0d556eead739e1.png!small)

### 04.GitLab的安全建议

从以上的分析我们可以看到，国内GitLab资产漏洞层出不穷。如利用CVE-2021-22205，不法分子可以轻松拿到reverse
shell，从而实现任意代码执行，轻松地盗取个人和企业的隐私信息。这里建议大家：

1.请尽快将GitLab资产升级到最新版本

2.在使用GitLab时，尽量监听在内网IP地址，避免直接暴露在互联网中

3.根据官方提供的缓解措施进行临时缓解，GitLab相关的漏洞缓解措施可参考官方网址：https://gitlab.com/gitlab-org/cves

## 四.Jenkins资产风险测绘

### 01.Jenkins简介

Jenkins是一个独立的开源自动化服务器，是一款提供友好操作界面的持续集成(CI)的工具，可用于自动化各种任务，如构建，测试和部署软件等。在cprime公布的CI集成工具排名中[9]，Jenkins排名第一，它也被多个机构评定为DevOps流程中最受欢迎的持续集成工具。

### 02.Jenkins国内资产暴露情况

根据网络测绘数据，我们对国内Jenkins资产暴露情况进行了统计，共计查询到16226个暴露的资产，且我们发现部分暴露的Jenkins资产可以直接跳过登录，进入到操作界面，这样的危险不言而喻，示例如下图7，8所示。

![77f81da2a9fd076965446851512f8854.png](https://image.3001.net/images/20220724/1658654547_62dd0f538d6e8d8d0d323.png!small)图7
Jenkins暴露示例1  
![3ddfcf171611cb17c336b856785e5d94.png](https://image.3001.net/images/20220724/1658654574_62dd0f6edb59af342eaf7.png!small)图8
Jenkins暴露示例2

此外我们将从地区分布、暴露端口、版本三个维度分别对Jenkins国内资产暴露情况进行介绍。

如图9所示，国内暴露的Jenkins资产中约77%来源于北京市、广东省、上海市和浙江省这些一线省份和城市，其中北京市稳居第一，暴露资产数达到4253个。  
![b441ebb42523bf43a1e7a8e80bf460a7.png](https://image.3001.net/images/20220724/1658654664_62dd0fc8e387509f7e719.png!small)图9
Jenkins国内暴露资产分布图（地区维度）

从图10可见，国内暴露的Jenkins资产使用的端口主要为8080、8081、8888、443、9090，共占总数的84%，其中8080端口最多，存在9523个，占比58.7%。  
![d604e17457b3fd21c51ed2b52a194226.png](https://image.3001.net/images/20220724/1658654710_62dd0ff6cde5d75fe9ad1.png!small)图10
Jenkins国内暴露资产分布图（端口维度）

通过特定的指纹信息，我们也获取到了国内暴露的Jenkins资产的版本号。经过匹配，可以获取到10334个资产的版本号信息，大约占总数的63.7%，具体版本号分布如图11所示。  
![245e820321d19219b013819c99a5d9e2.png](https://image.3001.net/images/20220724/1658654759_62dd1027783c611ee9892.png!small)图11
Jenkins国内暴露资产分布图（版本号

###  **03.Jenkins国内资产漏洞分析**

与GitLab类似，我们梳理了 CVSSVersion3.x
评分大于或等于7分的Jenkins漏洞。在包括Jenkins插件漏洞信息中，共计发现了96个高危（评分大于或等于7）的CVE，频率较多的漏洞类型包括：XXE，CSRF，SSRF，未授权，信息泄露，RCE等。

为了进一步分析主版本漏洞对Jenkins资产的影响，在排除了Jenkins插件漏洞信息之后，共计筛选出了18个高危的CVE，依次是：CVE-2021-21685，CVE-2021-21686，CVE-2021-21687，CVE-2021-21688，CVE-2021-21688，CVE-2021-21690，CVE-2021-21691，CVE-2021-21692，CVE-2021-21693，CVE-2021-21694，CVE-2021-21695，CVE-2021-21696，CVE-2021-21697，CVE-2021-21671，CVE-2021-21604，CVE-2021-21605，CVE-2020-2160，CVE-2020-2099。

为了进一步查看脆弱性暴露情况，我们对暴露的Jenkins资产进行了静态匹配，如下图12所示：  
![ccc1645e2b54d5a4cfb4a1b58719639e.png](https://image.3001.net/images/20220724/1658654816_62dd106018d44ad889e28.png!small)图12
Jenkins暴露资产脆弱性

从图中可以看到，暴露资产中CVE-2021-21685到CVE-2021-21697的数量多达9582个，而我们可获取到的版本号的总量也才10334个。为了进一步分析影响面，制作了以下表格（如表2所示），我们可以看到多半的CVE影响面达到了惊人的92.7%，可见暴露的Jenkins资产，其脆弱性风险乃是极其之大，Jenkins存在着严重的安全问题。  
![8034dc81b93003fbe0d5055fc9ef1a34.png](https://image.3001.net/images/20220724/1658654852_62dd1084abf9f3a5c49c2.png!small)

表2 Jenkins暴露资产脆弱性影响面

### 04.Jenkins安全建议

经过上文的分析，我们可以感受到国内Jenkins资产暴露数量不少，且暴露的资产中普遍存在严重的脆弱性问题，其中有13个CVE影响面高达92.7%，且10个CVE评分超过9分（严重高危）。这里温馨建议：

1.请尽快将Jenkins资产升级到最新版本

2.在使用Jenkins时，尽量将相关端口监听在内网IP地址，避免直接暴露在互联网中

3.根据官方提供的缓解措施进行临时缓解，Jenkins相关的漏洞缓解措施可参考官方网址：
https://www.jenkins.io/security/advisory/

## 五.总结

随着DevOps敏捷开发流程被越来越多的人和机构认可，DevOps全球化和普及化将成为发展趋势。但DevOps同时也带来了很多的安全风险，通过上文的分析，我们可以看见GitLab和Jenkins漏洞百出，脆弱性问题不容小视。当大家享受DevOps敏捷化带来红利的同时，或许你的DevOps工具早已被不法分子所利用。上文给出了部分DevOps工具防范的方法，但对于云上风险来说，这仅仅是冰山一角，无论个人还是企业，我们都应该引起重视，加以防范，一同维护网络安全。

参考文献

> https://www.digite.com/blog/introduction-to-devops/
>
> https://zh.m.wiki...pedia.org/wiki/DevOps
>
> https://www.gminsights.com/industry-analysis/devops-market
>
> https://www.kubernetes.org.cn/9538.html
>
> https://www.opsera.io/blog/top-25-devops-tools-that-you-need-to-know
>
> https://dzone.com/articles/50-useful-devops-tools
>
> https://dzone.com/articles/the-devops-toolchain
>
> https://en.wiki..pedia.org/wiki/GitLab
>
> https://cprimestudios.com/blog/top-cicd-tools-2021-most-complete-> guide-33-best-picks-devops

