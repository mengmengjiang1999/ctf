![](https://image.3001.net/images/20220210/1644492016_6204f4f07dc0d6201acd6.png!small)

## 关于Combobulator

Combobulator全称为Dependency
Combobulator，是一款功能强大的模块化可扩展框架，该工具现已开源，能够帮助广大研究人员检测并防止潜在的依赖混淆攻击风险。

在该工具的帮助下，广大研究人员可以更好地采用一种整体的方法来确保应用程序的安全发布，并可以根据不同的源（例如GitHub包、JForg
Artifactory等）和许多其他包管理方案（例如NDM、Maven等）来对项目安全性进行评估。

## 目标受众

该框架主要为安全审计人员和渗透测试人员设计，甚至还可以以自动化的方式整合进企业的应用程序安全策略以及发布环节中。

## 主要功能

> 1、插件化：支持整合进软件开发生命周期中的提交、构建和发布环节中；
>
> 2、可扩展：允许我们轻松添加自己的包管理方案或选择的代码源；
>
> 3、通用启发式引擎：抽象包数据模型，提供了不可知启发式方法；
>
> 4、支持多种技术；
>
> 5、灵活性：决策树可以根据工具包提供的内容或判断来确定方案；

该项目所提供的扩展能力允许广大研究人员根据自己的需求来进行定制开发。因此，我们可以轻松将其整合进其他来源、公共注册中心和包管理方案，并实现抽象模型扩展。

## 工具安装

Combobulator具备高可用性，广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/apiiro/combobulator.git

接下来，我们还需要通过下列命令安装好该工具所需的依赖组件：

    
    
    pip install -r requirements.txt

## 工具参数

    
    
    -h, --help             显示帮助信息和退出
    
      -t {npm,NuGet,maven}, --type {npm,NuGet,maven}
    
                            包管理器类型，例如npm、Nuget、maven
    
      -l LIST_FROM_FILE, --load_list LIST_FROM_FILE
    
                            从文件加载依赖列表
    
      -d FROM_SRC, --directory FROM_SRC
    
                            从本地源代码库提取依赖
    
      -p--package SINGLE    命名单个包
    
      -c CSV, --csv CSV     将包属性导出至CSV文件
    
      -gh GITHUB_TOKEN, --github GITHUB_TOKEN
    
                            GitHub 访问令牌 (覆盖.env文件设置)
    
      -a {compare,comp,heuristics,heur}, --analysis {compare,comp,heuristics,heur}
    
                            设置分析级别，对比compare和启发式heuristics，默认为compare
    
     
    
    Apiiro <Heart> Community

### 支持的包类型（-t, --t）

> 1、npm
>
> 2、maven

### 支持的源依赖性评估

> 1、从包含依赖项标识符的文件逐行读取（-l, --load_list）；
>
> 2、分析相应代码库的软件材料清单，例如package.json和pom.xml等（-d, --directory）；
>
> 3、命名单个标识符（-p，--package）；

广大研究人员可以通过构建自己的首选分析配置文件来自行设置分析级别，Combobulator提供了几个现成的分析级别，可通过-a或--analysis进行选择。

### 支持的数据输出格式

> 1、STDOU（默认）
>
> 2、CSV导出（-CSV）

## 工具使用样例

 **演示视频：** 【[ _点我观看_](https://user-images.githubusercontent.com/90651458/140915800-c267034b-90c9-42d1-b12a-83e12f70d44e.mp4)】

## 项目地址

 **Combobulator：** 【[ _GitHub传送门_](https://github.com/apiiro/combobulator)】

