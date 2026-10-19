作者：天启@涂鸦智能安全实验室

## 0x01简介

[官方](https://codeql.github.com/docs/codeql-overview/about-codeql/#about-codeql)的定义是:CodeQL 是开发人员用来自动化安全检查的分析引擎，安全研究人员用来执行变体分析。在 CodeQL 中，代码被视为数据。
安全漏洞、错误和其他错误被建模为可以针对从代码中提取的数据库执行的查询。 您可以运行由 GitHub 研究人员和社区贡献者编写的标准 CodeQL
查询，也可以编写自己的查询以用于自定义分析。 查找潜在错误的查询直接在源文件中突出显示结果。

按照我的理解:CodeQL其实就是一个自动化的代码审计扫描器,不过他保存了代码中所有的代码变量以及结构化信息!并且官方提供了很多现成的接口,你可以使用这些接口像写脚本一样,非常灵活地查询这些结构化的数据并且从中挖掘漏洞!我遇到挺多同学,他们都以为codeQL只能在线运行查询!所以就有了这篇文章!下面我就介绍一下,如何在本地安装使用codeQL。

## 0x02本地安装

GitHub没有完全开源codeQL,所以我们无法在网上找到源码,只能下载已经编译好的二进制文件!接下来我们需要下载两个仓库:二进制文件的仓库,以及包含规则的CodeQL仓库:

<https://github.com/github/codeql-cli-binaries/releases>

<https://github.com/github/codeql>

### 0x021 本地安装 Visual Studio Code

由于CodeQL是GitHub开源的,而GitHub又被微软全资收购了,且Visual Studio
Code又是微软开源的,所以CodeQL只对Visual Studio
Code做了全面友好的支持,我们如果需要本地使用CodeQL,那就不得不下载Visual Studio Code!

<https://code.visualstudio.com/>

### 0x022 本地安装CodeQL

直接在插件市场搜索CodeQL插件并安装

![1663226477_6322d26d4de6e8244110b.png!small?1663226478555](https://image.3001.net/images/20220915/1663226477_6322d26d4de6e8244110b.png!small?1663226478555)

配置CodeQL插件

![1663226926_6322d42e3d1d92e2cf8ee.png!small?1663226927708](https://image.3001.net/images/20220915/1663226926_6322d42e3d1d92e2cf8ee.png!small?1663226927708)

配置前面下载的二进制文件的绝对路径

![1663227035_6322d49b24e9540f2ab35.png!small?1663227036083](https://image.3001.net/images/20220915/1663227035_6322d49b24e9540f2ab35.png!small?1663227036083)

至此本地CodeQL安装完成

## 0x03如何使用

VSCode打开前面下载的包含规则的CodeQL仓库文件夹,界面如下所示

![1663228471_6322da37e1e338316bdee.png!small?1663228473428](https://image.3001.net/images/20220915/1663228471_6322da37e1e338316bdee.png!small?1663228473428)

进入/Users/tools/scanner/codeql/java/ql/src/Security/CWE/这个文件夹下,该文件夹下面是所有官方已经写好的通用的查询脚本,如下所示

![1663228598_6322dab69eb9e1d5e1c81.png!small?1663228599293](https://image.3001.net/images/20220915/1663228598_6322dab69eb9e1d5e1c81.png!small?1663228599293)

我们如何才能快速找到我们需要的脚本呢?比如我想找到xss的相关查询脚本,这么多CWE-文件夹总不可能一个一个点开查找吧?有没有更好的办法呢?其实是有的!我们直接在命令行中使用 tree
/Users/tools/scanner/codeql/java/ql/src/Security/CWE/ 命令并且直接搜索 xss
如下所示,这样就找到了这个查询文件,直接鼠标右键-选择CodeQL:Run Queries in select files 就可以执行查询了

![1663230829_6322e36d1d068710d279a.png!small?1663230829732](https://image.3001.net/images/20220915/1663230829_6322e36d1d068710d279a.png!small?1663230829732)

![1663231277_6322e52d3e82b0f58f2db.png!small?1663231278369](https://image.3001.net/images/20220915/1663231277_6322e52d3e82b0f58f2db.png!small?1663231278369)

如果没有漏洞,结果如下图所示

![1663231533_6322e62d980ecf9274840.png!small?1663231534495](https://image.3001.net/images/20220915/1663231533_6322e62d980ecf9274840.png!small?1663231534495)

## 0x04.后言

该篇文章简单介绍一下CodeQL本地的安装使用.下一篇文章将介绍一下一些进阶的玩法!

本文作者能力有限,文章若有纰漏请读者不吝赐教!  
WeChat:5ed0c42e63c9c2145990351ccaec4da5

 **漏洞悬赏计划：涂鸦智能安全响应中心（https://src.tuya.com）欢迎白帽子来探索。  
招聘内推计划：涵盖安全开发、安全测试、代码审计、安全合规等所有方面的岗位，简历投递sec#tuya.com，请注明来源。**

