![](https://image.3001.net/images/20210309/1615299058_604781f2138470c498b94.png!small)

## 概述

Pillager旨在提供一种简单的方法，利用Go的强并发模型递归地搜索目录中的敏感信息。Pillager基于目前
_几个功能强大的项目_实现其功能，一旦Pillager找到与指定模式匹配的文件，就会使用一系列并发工作线程扫描该文件，每个并发工作线程从作业队列中提取一行文件，并查找敏感模式匹配项。所有可用的模式过滤器可以在一个rules.toml文件中定义，或者广大研究人员也可以选择使用默认的规则集。

## 工具安装

### Go

如果你已经在系统中安装好了Go环境，我们就可以使用go get来安装Pillager了：

    
    
    go get github.com/brittonhayes/pillager

### Scoop（Windows）

    
    
    scoop bucket add pillager https://github.com/brittonhayes/pillager-scoop.git
    
    scoop install pillager

### Homebrew（macOS/Linux）

    
    
    brew tap brittonhayes/homebrew-pillager
    
    brew install pillager

## 工具使用

我们可以使用pillager命令来查看该工具所有支持的命令：

    
    
    # To see instructions for the entire application
    
    pillager
    
     
    
    # From any subcommand
    
    pillager [cmd] --help

## 工具配置

### Gitleaks规则

Pillager提供了针对Gitleaks规则的完整支持，我们可以通过一个rules.toml文件来传递规则，或者直接使用默认规则：

    
    
    # rules.toml
    
    title = "pillager rules"
    
     
    
    [[rules]]
    
    description = "AWS Access Key"
    
    regex = '''(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'''
    
    tags = ["key", "AWS"]
    
    [[rules.entropies]]
    
    Min = "3.5"
    
    Max = "4.5"
    
    Group = "1"
    
     
    
    [[rules]]
    
    description = "Email Address"
    
    regex = '''(?i)([A-Za-z0-9!#$%&'*+\/=?^_{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)'''
    
    tags = ["email", "User Info"]

### 内置输出格式

Pillager拥有一系列内置的输出格式，我们可以自行选择。

 **基本格式：**

    
    
    pillager hunt .

 **JSON：**

    
    
    pillager hunt ./example -f json | jq .

 **YAML：**

    
    
    pillager hunt . -f yaml

 **HTML：**

    
    
    pillager hunt . -f html > results.html

 **HTML Table：**

    
    
    pillager hunt . -f html-table > results.html

 **Markdown：**

    
    
    pillager hunt . -f markdown > results.md

 **Markdown Table：**

    
    
    pillager hunt . -f table > results.md

 **自定义Go模板：**

    
    
    pillager hunt . --template "{{ range .Leaks}}Leak: {{.Line}}{{end}}"

 **来自文件的自定义Go模板：**

    
    
    pillager hunt . -t "$(cat templates/simple.tmpl)"

## 自定义模板

Pillager允许我们使用功能强大的go text/template来自定义开发输出格式。

 **基础风格：**

    
    
    {{/*basic.tmpl*/}}
    
    {{ range .Leaks -}}
    
    File: {{ .File }}
    
    Line: {{.LineNumber}}
    
    Offender: {{ .Offender }}
    
    {{ end -}}

 **Markdown风格：**

    
    
    {{/*markdown.tmpl*/}}
    
    # Results
    
    {{ range .Leaks}}
    
    ## {{ .File }}
    
    - Location: {{.LineNumber}}
    
    {{end}}

## 关于Gitleaks

你是否将未加密的密码、机密和任何其它不需要的数据类型存储在你的git源代码存储库中？Gitleaks为你提供了一种方法来扫描你的git存储库，以查找这些不需要的数据，这些数据应该是私有的，扫描可以自动化，以完全适合CI/CD工作流程，以便在密码识别更深入到代码库之前进行识别。

### Gitleaks的一些很酷的功能包括：

> 支持私有存储库扫描以及需要基于密钥的身份验证的存储库。
>
> 支持Gitlab批量组织和存储库所有者（用户）存储库扫描，并提取请求扫描以在常见CI工作流中使用。
>
> 可以输出JSON和CSV格式的扫描结果以及其他报告工具和框架中的消费格式。
>
> 用于特定于环境的自定义的外部化配置，包括正则表达式规则。
>
> 可自定义的存储库名称，文件类型，提交ID，分支机构和正则表达式白名单，以减少误报。
>
> 通过使用src-d的go-git框架实现高性能。

## 工具运行截图

![](https://image.3001.net/images/20210309/1615299191_60478277ca46b7a4be9d0.png!small)

## 项目地址

Pillager：【[ _GitHub传送门_](https://github.com/brittonhayes/pillager)】

