**Pown Recon是一个基于图论的目标侦察框架，使用图论代替flat
table的好处是更容易找到不同类型信息之间的关系，这在许多情况下将为我们带来便利。此外，图论算法还有助于我们完成许多其它有用的任务，如寻找最短路径等，以进一步的为我们发现信息和收集情报。**

 **注：** 该工具为[secapps.com](https://secapps.com/)开源计划的一部分。

    
    
     ___ ___ ___   _   ___ ___  ___
    / __| __/ __| /_\ | _ \ _ \/ __|
    \__ \ _| (__ / _ \|  _/  _/\__ \
    |___/___\___/_/ \_\_| |_|  |___/
     https://secapps.com

Pown Recon几乎是SecApps优秀的[Recon](https://recon.secapps.com/)工具直接复制的结果。

## 快速入门

该工具为Pown.js项目的一部分，但你也可以单独使用它。

首先，让我们先来安装Pown：

    
    
    $ npm install -g pown@latest

直接从Pown调用：

    
    
    $ pown recon

从项目的根目录在本地安装此模块：

    
    
    $ npm install @pown/recon --save

安装完成后，调用pown cli：

    
    
    $ ./node_modules/.bin/pown-cli recon

你还可以使用全局pown在本地调用该工具：

    
    
    $ POWN_ROOT=. pown recon

## 使用

 **注意：** 此pown命令当前正处在开发中，因此后续可能会发生较大的变动。

    
    
    pown recon <command>
    
    Target recon
    
    Commands:
      pown recon transform <transform>        执行内联转换 [简写：t]
      pown recon select <selectors...>        选择节点 [简写：s]
      pown recon add <nodes...>               添加节点 [简写：a]
      pown recon remove <selectors...>        删除节点 [简写：r]
      pown recon merge <files...>             在至少两个recon文件之间执行合并 [简写：m]
      pown recon diff <fileA> <fileB>         对比两个recon文件之间的差异性 [简写：d]
      pown recon group <name> <selectors...>  组节点 [简写：g]
      pown recon ungroup <selectors...>       取消组节点 [简写：u]
    
    Options: 
      --version  显示版本号 [boolean]
      --help     查看帮助 [boolean]

 **pown recon transform**

    
    
    pown recon transform <transform>
    
    Perform inline transformation
    
    Commands:
      pown recon transform archiveindex [options] <nodes...>                  Obtain archive.org index for specific URL.  [aliases: archive_index, arci]
      pown recon transform awsiamendpoints [options] <nodes...>               Enumerate AWS IAM endpoints.  [aliases: aws_iam_endpoints, awsie]
      pown recon transform builtwithscraperelationships [options] <nodes...>  Performs scrape of builtwith.com relationships  [aliases: builtwith_scrape_relationships, bwsr]
      pown recon transform cloudflarednsquery [options] <nodes...>            Query CloudFlare DNS API.  [aliases: cloudflare_dns_query, cfdq]
      pown recon transform commoncrawlindex [options] <nodes...>              Obtain a CommonCraw index for specific URL.  [aliases: commoncrawl_index, cci]
      pown recon transform crtshdomainreport [options] <nodes...>             Obtain crt.sh domain report which helps enumerating potential target subdomains.  [aliases: crtsh_domain_report, crtshdr]
      pown recon transform dockerhublistrepos [options] <nodes...>            List the first 100 DockerHub repositories.  [aliases: dockerhub_list_repos, dhlr]
      pown recon transform githublistrepos [options] <nodes...>               List GitHub repositories.  [aliases: github_list_repos, ghlr]
      pown recon transform githublistgists [options] <nodes...>               List GitHub gists.  [aliases: github_list_gists, ghlg]
      pown recon transform githublistmembers [options] <nodes...>             List the first 100 GitHub members in org  [aliases: github_list_members, ghlm]
      pown recon transform gravatar [options] <nodes...>                      Get gravatar.
      pown recon transform hackertargetreverseiplookup [options] <nodes...>   Obtain reverse IP information from hackertarget.com.  [aliases: hackertarget_reverse_ip_lookup, htril]
      pown recon transform hibpreport [options] <nodes...>                    Obtain haveibeenpwned.com breach report.  [aliases: hibp_report, hibpr]
      pown recon transform pkslookupkeys [options] <nodes...>                 Look the the PKS database at pool.sks-keyservers.net which pgp.mit.edu is part of.  [aliases: pks_lookup_keys, pkslk]
      pown recon transform riddleripsearch [options] <nodes...>               Searches for IP references using F-Secure riddler.io.  [aliases: riddler_ip_search, rdis]
      pown recon transform riddlerdomainsearch [options] <nodes...>           Searches for Domain references using F-Secure riddler.io.  [aliases: riddler_domain_search, rdds]
      pown recon transform securitytrailssuggestions [options] <nodes...>     Get a list of domain suggestions from securitytrails.com.  [aliases: securitytrails_domain_suggestions, stds]
      pown recon transform securitytrailsdomainreport [options] <nodes...>    Get a domain report from securitytrails.com.  [aliases: securitytrails_domain_report, stdr]
      pown recon transform threatcrowddomainreport [options] <nodes...>       Obtain threatcrowd domain report which helps enumerating potential target subdomains and email addresses.  [aliases: threatcrowd_domain_report, tcdr]
      pown recon transform threatcrowdipreport [options] <nodes...>           Obtain threatcrowd ip report which helps enumerating virtual hosts.  [aliases: threatcrowd_ip_report, tcir]
      pown recon transform urlscanliveshot [options] <nodes...>               Generates a liveshot of any public site via urlscan.  [aliases: usls]
      pown recon transform nop [options] <nodes...>                           Does not do anything.
      pown recon transform splitemail [options] <nodes...>                    Split email.  [aliases: split_email, se]
      pown recon transform buildemail [options] <nodes...>                    Build email.  [aliases: build_email, be]
      pown recon transform splituri [options] <nodes...>                      Split URI.  [aliases: split_uri, su]
      pown recon transform builduri [options] <nodes...>                      Build URI.  [aliases: build_uri, bu]
      pown recon transform analyzeip [options] <nodes...>                     Analyze IP.  [aliases: analyze_ip, ai]
      pown recon transform wappalyzerprofile [options] <nodes...>             Enumerate technologies with api.wappalyzer.com.  [aliases: wappalyzer_profile, wzp]
      pown recon transform whatsmynamereport [options] <nodes...>             Find social accounts with the help of whatsmyname database.  [aliases: whatsmyname_report, whatsmyname, wmnr, wmn]
      pown recon transform zoomeyescrapesearchresults [options] <nodes...>    Performs first page scrape on ZoomEye search results  [aliases: zoomeye_scrape_search_results, zyssr]
      pown recon transform auto [options] <nodes...>                          Select the most appropriate methods of transformation
    
    Options:
      --version    Show version number  [boolean]
      --help       Show help  [boolean]
      --read, -r   Read file  [string]
      --write, -w  Write file  [string]

 **pown recon select**

    
    
    pown recon select <selectors...>
    
    Select nodes
    
    Options:
      --version            Show version number  [boolean]
      --help               Show help  [boolean]
      --read, -r           Read file  [string]
      --write, -w          Write file  [string]
      --output-format, -o  Output format  [string] [choices: "table", "grid", "csv", "json"] [default: "table"]
      --output-fields      Output fields  [string] [default: ""]
      --output-ids         Output ids  [boolean] [default: false]
      --output-labels      Output labels  [boolean] [default: false]
      --output-parents     Output parents  [boolean] [default: false]
      --output-tags        Output tags  [boolean] [default: false]

 **pown recon diff**

    
    
    pown recon diff <fileA> <fileB>
    
    Perform a diff between two recon files
    
    Options:
      --version            Show version number  [boolean]
      --help               Show help  [boolean]
      --subset, -s         The subset to select  [choices: "left", "right", "both"] [default: "left"]
      --write, -w          Write file  [string]
      --output-format, -o  Output format  [string] [choices: "table", "grid", "csv", "json"] [default: "table"]
      --output-fields      Output fields  [string] [default: ""]
      --output-ids         Output ids  [boolean] [default: false]
      --output-labels      Output labels  [boolean] [default: false]
      --output-parents     Output parents  [boolean] [default: false]
      --output-tags        Output tags  [boolean] [default: false]

 **pown recon merge**

    
    
    pown recon merge <files...>
    
    Perform a merge between at least two recon files
    
    Options:
      --version    Show version number  [boolean]
      --help       Show help  [boolean]
      --write, -w  Write file  [string]

 **pown recon add**

    
    
    pown recon add <nodes...>
    
    Add nodes
    
    Options:
      --version            Show version number  [boolean]
      --help               Show help  [boolean]
      --group, -g          Group nodes  [string] [default: ""]
      --node-type          The type for new nodes from the command line  [string] [default: "string"]
      --read, -r           Read file  [string]
      --write, -w          Write file  [string]
      --output-format, -o  Output format  [string] [choices: "table", "grid", "csv", "json"] [default: "table"]
      --output-fields      Output fields  [string] [default: ""]
      --output-ids         Output ids  [boolean] [default: false]
      --output-labels      Output labels  [boolean] [default: false]
      --output-parents     Output parents  [boolean] [default: false]
      --output-tags        Output tags  [boolean] [default: false]

 **pown recon remove**

    
    
    pown recon remove <selectors...>
    
    Remove nodes
    
    Options:
      --version            Show version number  [boolean]
      --help               Show help  [boolean]
      --read, -r           Read file  [string]
      --write, -w          Write file  [string]
      --output-format, -o  Output format  [string] [choices: "table", "grid", "csv", "json"] [default: "table"]
      --output-fields      Output fields  [string] [default: ""]
      --output-ids         Output ids  [boolean] [default: false]
      --output-labels      Output labels  [boolean] [default: false]
      --output-parents     Output parents  [boolean] [default: false]
      --output-tags        Output tags  [boolean] [default: false]

 **pown recon group**

    
    
    pown recon group <name> <selectors...>
    
    Group nodes
    
    Options:
      --version            Show version number  [boolean]
      --help               Show help  [boolean]
      --read, -r           Read file  [string]
      --write, -w          Write file  [string]
      --output-format, -o  Output format  [string] [choices: "table", "grid", "csv", "json"] [default: "table"]
      --output-fields      Output fields  [string] [default: ""]
      --output-ids         Output ids  [boolean] [default: false]
      --output-labels      Output labels  [boolean] [default: false]
      --output-parents     Output parents  [boolean] [default: false]
      --output-tags        Output tags  [boolean] [default: false]
    

**pown recon ungroup**

    
    
    pown recon ungroup <selectors...>
    
    Ungroup nodes
    
    Options:
      --version            Show version number  [boolean]
      --help               Show help  [boolean]
      --read, -r           Read file  [string]
      --write, -w          Write file  [string]
      --output-format, -o  Output format  [string] [choices: "table", "grid", "csv", "json"] [default: "table"]
      --output-fields      Output fields  [string] [default: ""]
      --output-ids         Output ids  [boolean] [default: false]
      --output-labels      Output labels  [boolean] [default: false]
      --output-parents     Output parents  [boolean] [default: false]
      --output-tags        Output tags  [boolean] [default: false]
    

## 预览

由于该工具基于Recon，因此为方便起见，你可以在[SecApps
Recon](https://recon.secapps.com/)中预览生成的图形。你可以从浏览器访问SecApps Recon，也可以从命令行调用它。

首先，你需要安装@pown/apps：

    
    
    $ pown modules install @pown/apps

这将为你安装可选的apps命令包。

使用write选项生成图形：

    
    
    $ pown recon transform auto -w path/to/file.network --node-type brand target

完成后，在SecApps Recon中打开以及预览图形：

    
    
    $ pown apps recon < path/to/file.network

你将看到类似于以下呈现的内容：

![02.png](https://image.3001.net/images/20190314/1552529707_5c89b92b02d5b.png!small)

## Pown Script

[Pown Script](https://github.com/pownjs/pown-script)是一个简单的脚本环境。相比起bash、python、perl等，Pown
Script的优点在于所有命令都在同一个VM上下文（同一进程）中执行。这意味着你可以构建图形，而无需保存和恢复到中间文件。

使用你喜欢的编辑器创建一个名为example.pown的文件，内容如下：

    
    
    echo This is script
    recon add --node-type brand target
    recon t auto

从pown执行脚本：

    
    
    $ pown script path/to/example.pown

有关更多信息，请参阅示例。

## 演示

为了演示Pown Recon和基于图形的OSINT（开源智能）的强大功能，让我们看一下下面的简单示例。

让我们来查询下哪些人是谷歌工程团队的成员以及他们的GitHub帐户。

    
    
    pown recon t -w google.network ghlm google

此命令将生成一个类似于下面的表：

    
    
    github:member
    ┌─────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┐
    │ uri                                                     │ login                                                   │ avatar                                                  │
    ├─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┤
    │ https://github.com/3rf                                  │ 3rf                                                     │ https://avatars1.githubusercontent.com/u/1242478?v=4    │
    ├─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┤
    │ https://github.com/aaroey                               │ aaroey                                                  │ https://avatars0.githubusercontent.com/u/31743510?v=4   │
    ├─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┤
    │ https://github.com/aarongable                           │ aarongable                                              │ https://avatars3.githubusercontent.com/u/2474926?v=4    │
    ...
    ...
    ...
    │ https://github.com/alexpennace                          │ alexpennace                                             │ https://avatars1.githubusercontent.com/u/2506548?v=4    │
    ├─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┤
    │ https://github.com/alexv                                │ alexv                                                   │ https://avatars0.githubusercontent.com/u/30807372?v=4   │
    ├─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┤
    │ https://github.com/alexwhouse                           │ alexwhouse                                              │ https://avatars3.githubusercontent.com/u/1448490?v=4    │
    └─────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────┘

以下是一个模型，节点间的关系有浅红色的线连接表示。如果你想知道它是什么样的，你可以使用SecApps Recon。

使用-w google.network命令将network导出到文件。你可以使用文件打开功能，将文件直接加载到SecApps Recon中。 结果如下：

![01.png](https://image.3001.net/images/20190314/1552529737_5c89b949ef429.png!small)

假设现在我们想要查询这些Google工程师正在处理的存储库。这很简单，我们只需选择图中的节点，然后使用“GitHub List
Repositories”对它们进行转换即可。以下是在命令行中执行此操作的方式：

    
    
    pown recon t ghlr -r google.network -w google2.nework -s 'node[type="github:member"]'

如果你没有触发GitHub API速率限制，你将看到以下内容：

    
    
     github:repo
    ┌──────────────────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────┐
    │ uri                                                                                  │ fullName                                                                             │
    ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
    │ https://github.com/3rf/2015-talks                                                    │ 3rf/2015-talks                                                                       │
    ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
    │ https://github.com/3rf/codecoroner                                                   │ 3rf/codecoroner                                                                      │
    ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
    │ https://github.com/3rf/DefinitelyTyped                                               │ 3rf/DefinitelyTyped                                                                  │
    ...
    ...
    ...
    │ https://github.com/agau4779/ultimate-tic-tac-toe                                     │ agau4779/ultimate-tic-tac-toe                                                        │
    ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
    │ https://github.com/agau4779/worm_scraper                                             │ agau4779/worm_scraper                                                                │
    ├──────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
    │ https://github.com/agau4779/zsearch                                                  │ agau4779/zsearch                                                                     │
    └──────────────────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────┘

现在我们已拥有了两个文件：google.network和google2.network。你可能想知道它们之间存在的区别，有一个工具可以帮助我们做到这一点。

    
    
    pown recon diff google.network google2.network

到这里你应该就明白了，如果你想构建大型侦察地图，并且想知道它们间的主要差异，这个功能是非常有用和必要的。想象一下，你的cron
job每天执行相同的侦察任务，但你想知道是否发现了一些新的有价值的信息。因此，差异性对比功能的重要性不言而喻。

 ***参考来源：[GitHub](https://github.com/pownjs/pown-recon)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

