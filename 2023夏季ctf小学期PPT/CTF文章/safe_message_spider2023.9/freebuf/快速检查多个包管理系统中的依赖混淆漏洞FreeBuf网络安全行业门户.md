![](https://image.3001.net/images/20210321/1616317576_60570c88935e043ba76c4.jpg!small)

## 关于Confused

Confused是一款功能强大的依赖混淆漏洞检测工具，广大研究人员可以使用Confused跨多个包管理器检测其中存在的依赖混淆漏洞。Confused能够检测Python（pypi）
requirements.txt、JavaScript (npm) package.json、PHP (composer)
composer.json或MVN (maven) pom.xml等依赖配置文件中引用的私有包名称和命名空间，并帮助检测潜在的依赖混淆漏洞。

## 解释工具输出

Confused只会读取应用程序的依赖项定义文件，并检查公共包存储库中该文件中的每个依赖项条目。除此之外，它还会继续报告在公共存储库中找不到的所有包名—这种状态意味着包可能容易受到此类攻击，而此向量尚未被利用。

然而，这并不意味着应用程序没有受到攻击，或仍然是安全的。如果你发现你的应用程序正在使用私有包存储库，则应该确保你的私有包的命名空间已由受信任的一方（通常是你自己或你的公司）声明。

## 已知假阳性

一些包存储库生态系统（比如说npm）都会有一种名为“范围”的概念，也就是说其中的代码包可以是私有的也可以是公共的。简而言之，它意味着一个命名空间会有一个更高的级别-范围。这些作用域本质上不是公开可见的，这意味着Confused无法可靠地检测目标代码包是否已声明。如果应用程序使用作用域内的包名称，则应确保受信任方已在公共存储库中声明了作用域名称。

## 工具安装

广大研究人员可以选择访问该项目的【[ _Releases页面_](https://github.com/visma-prodsec/confused/releases/latest)】来下载预编译好的项目代码，然后解压并运行即可。

或者，你也可以在本地安装并配置好Go语言环境，然后使用Go编译器来进行安装（安装和更新命令相同）：

    
    
    go get -u github.com/visma-prodsec/confused

除此之外，广大研究人员也可以使用下列命令将该项目源码克隆至本地，然后使用Go命令进行代码编译和构建：

    
    
    git clone https://github.com/visma-prodsec/confused
    
    cd confused
    
    go get
    
    go build

## 工具使用

    
    
    Usage:
    
     ./confused [-l LANGUAGENAME] depfilename.ext
    
     
    
    Usage of ./confused:
    
      -l string
    
            代码包存储库系统，可选的值有："pip", "npm", "composer", "mvn" (默认为"npm")
    
      -s string
    
            已知安全的命名空间，提供以逗号分隔的列表，支持通配符
    
      -v    Verbose模式输出

## 工具使用样例

### Python（PyPI）

    
    
    ./confused -l pip requirements.txt
    
     
    
    Issues found, the following packages are not available in public package repositories:
    
     [!] internal_package1

### JavaScript（npm）

    
    
    ./confused -l npm package.json
    
     
    
    Issues found, the following packages are not available in public package repositories:
    
     [!] internal_package1
    
     [!] @mycompany/internal_package1
    
     [!] @mycompany/internal_package2
    
     
    
    # Example when @mycompany private scope has been registered in npm, using -s
    
    ./confused -l npm -s '@mycompany/*' package.json
    
     
    
    Issues found, the following packages are not available in public package repositories:
    
     [!] internal_package1

### Maven（mvn）

    
    
    ./confused -l mvn pom.xml
    
     
    
    Issues found, the following packages are not available in public package repositories:
    
     [!] internal
    
     [!] internal/package1
    
     [!] internal/_package2

## 项目地址

Confused：【[ _GitHub传送门_](https://github.com/visma-prodsec/confused)】

## 参考资料

> [ _https://medium.com/@alex.birsan/dependency-> confusion-4a5d60fec610_](https://medium.com/@alex.birsan/dependency-> confusion-4a5d60fec610)
>
> [ _https://azure.microsoft.com/en-gb/resources/3-ways-to-mitigate-risk-> using-private-package-feeds/_](https://azure.microsoft.com/en-> gb/resources/3-ways-to-mitigate-risk-using-private-package-feeds/)
>
> [ _https://github.com/visma-> prodsec/confused/releases/latest_](https://github.com/visma-> prodsec/confused/releases/latest)

