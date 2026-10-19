![a](https://image.3001.net/images/20230704/1688468907_64a3fdabd679dc1659deb.png!small)

#### 是一款基于YAML语法模板的定制化快速漏洞扫描器

 **官网** : https://nuclei.projectdiscovery.io/  
 **项目地址** : https://github.com/projectdiscovery/nuclei  
 **项目脚本** : https://github.com/projectdiscovery/nuclei-templates  
 **脚本文档** : https://nuclei.projectdiscovery.io/templating-guide/

## 一、安装流程

    
    
    # kali/ubuntu go语言 安装
    
    sudo apt update
    sudo apt install golang-go
    
    go version
    
    

![a](https://image.3001.net/images/20230704/1688468908_64a3fdac6ddc4e83115e6.png!small)

    
    
    # 快速安装（需要先安装go环境）
    go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest  
    
    
    
    # 编译安装（需要先安装go环境）
    git clone https://github.com/projectdiscovery/nuclei.git; \
    cd nuclei/v2/cmd/nuclei; \
    go build; \
    mv nuclei /usr/local/bin/; \
    nuclei -version;
    
    
    
    # docker 环境安装 不需要安装Go语言
    docker pull projectdiscovery/nuclei:latest
    
    
    
    # 直接下载releases，下载即用
    https://github.com/projectdiscovery/nuclei/releases
    

安装完成之后

    
    
    nuclei -version
    

![a](https://image.3001.net/images/20230704/1688468909_64a3fdad1129e4e300796.png!small)  
**更新**

    
    
    nuclei -up  # 更新 nuclei
    nuclei -ut  # 更新脚本
    

## 二、常用操作

    
    
    nuclei -up  # 更新 nuclei
    nuclei -ut  # 更新脚本
    

![a](https://image.3001.net/images/20230704/1688468909_64a3fdad914249ec2d076.png!small)

    
    
    nuclei -h
    
    
    
    用法：
      nuclei [命令]
     
    命令：
    目标：
       -u, -target string[]                 指定扫描的URL/主机
       -l, -list string                     指定需要扫描的URL/主机文件（一行一个）
     
    模板：
       -t, -templates string[]              指定需要扫描的模板或者模板的路径
       -nt, -new-templates                  只扫描最新版本中添加的模板
       -w, -workflows string[]              指定扫描中的工作流或者工作流目录
       -validate                            验证通过的模板
       -tl                                  列出所有可用的模板
     
    过滤：
       -tags string[]                       执行有标记的模板子集
       -etags, -exclude-tags string[]       执行标记为排除的模板
       -itags, -include-tags string[]       不执行具有攻击性的模板
       -et, -exclude-templates string[]     要排除的模板或者模板目录
       -it, -include-templates string[]     执行默认或配置中排除的模板
       -s, -severity value[]                根据严重性运行模板，允许的值有：info,low,medium,high,critical   
       -es, -exclude-severity value[]       根据严重性排除模板，允许的值有：info,low,medium,high,critical   
       -a, -author string[]                 执行指定作者的模板
     
    输出：
       -o, -output string                   输出发现的问题到文件
       -silent                              只显示结果
       -nc, -no-color                       禁用输出内容着色（ANSI转义码）
       -json                                输出为jsonL（ines）
       -irr, -include-rr                    在JSONL中输出对应的请求和相应（仅结果）
       -nm, -no-meta                        不显示匹配的元数据
       -nts, -no-timestamp                  不在输出中显示时间戳
       -rdb, -report-db string              本地的Nuclei结果数据库（始终使用该数据库保存结果）       
       -me, -markdown-export string         以markdown导出结果
       -se, -sarif-export string            以SARIF导出结果
     
    配置：
       -config string                       指定Nuclei的配置文件
       -rc, -report-config string           指定Nuclei报告模板文件
       -H, -header string[]                 指定报告中的标题：value格式
       -V, -var value                       通过var=value指定var值
       -r, -resolvers string                指定Nuclei的解析文件
       -sr, -system-resolvers               当DNS错误时使用系统DNS
       -passive                             启用被动扫描处理HTTP响应
       -ev, env-vars                        在模板中使用环境变量
     
    交互：
       -inserver, -ineractsh-server string  使用interactsh反连检测平台（默认为"https://interact.sh"）
       -itoken, -interactsh-token string    指定反连检测平台的身份凭证
       -interactions-cache-size int         指定保存在交互缓存中的请求数（默认：5000）
       -interactions-eviction int           聪缓存中删除请求前等待的时间（默认为60秒）
       -interactions-poll-duration int      每个轮询前等待时间（默认为5秒）
       -interactions-cooldown-period int    退出轮询前的等待时间（默认为5秒）
       -ni, -no-interactsh                  禁用反连检测平台，同时排除基于反连检测的模板
     
    限速：
       -r1, -rate-limit int                 每秒最大请求量（默认：150）
       -rlm, -rate-limit-minute int         每分钟最大请求量
       -bs, -bulk-size int                  每个模板最大并行检测数（默认：25）
       -c, -concurrency int                 并行执行的最大模板数量（默认：25）
     
     
    优化：
       -timeout int                         超时时间（默认为5秒）
       -retries int                         重试次数（默认：1）
       -mhe, -max-host-error int            某主机扫描失败次数，跳过该主机（默认：30）
       -project                             使用项目文件夹避免多次发送同一请求
       -project-path string                 设置特定的项目文件夹
       -spm, -stop-at-first-path            得到一个结果后停止（或许会中断模板和工作流的逻辑）
       -stream                              流模式 - 在不整理输入的情况下详细描述
     
    无界面浏览器：
        -headless                           启用需要无界面浏览器的模板
        -page-timeout int                   在无界面下超时秒数（默认：20）
        -sb, -show-brower                   在无界面浏览器运行模板时，显示浏览器
        -sc, -system-chrome                 不使用Nuclei自带的浏览器，使用本地浏览器
     
    调试：
        -debug                              显示所有请求和响应
        -debug-req                          显示所有请求
        -debug-resp                         显示所有响应
        -proxy, -proxy-url string           使用HTTP代理
        -proxy-socks-url string             使用SOCK5代理
        -tlog, -trace-log string            写入请求日志到文件
        -version                            显示版本信息
        -v, -verbose                        显示详细信息
        -vv                                 显示额外的详细信息
        -tv, -templates-version             显示已安装的模板版本
     
    升级：
        -update                             更新Nuclei到最新版本
        -ut, -update-templates              更新Nuclei模板到最新版
        -ud, -update-directory string       覆盖安装模板
        -duc, -disable-update-check         禁用更新
     
    统计：
        -stats                              显示正在扫描的统计信息
        -sj, -stats-json                    将统计信息以JSONL格式输出到文件
        -si, -stats-inerval int             显示统计信息更新的间隔秒数（默认：5）
        -m, -metrics                        显示Nuclei端口信息
        -mp, -metrics-port int              更改Nuclei默认端口（默认：9092）
    

扫描单个目标

    
    
    nuclei -u https://example.com
    

扫描多个目标

    
    
    nuclei -list urls.txt
    

Example of `urls.txt`:

    
    
    http://example.com
    http://app.example.com
    http://test.example.com
    http://uat.example.com
    

根据 **tags** **cve** 扫描目标

    
    
    nuclei -u https://example.com -tags cve
    

用exposures目录下所有 tags是config的脚本扫描目标

    
    
    nuclei -u https://example.com -tags config -t exposures/
    

可以设置选择脚本的安全等级以及作者

    
    
    nuclei -u https://example.com  -severity critical,high -author geeknik
    

也同样可以根据 dsl表达式运行模板

    
    
    nuclei -tc "contains(id,'xss') || contains(tags,'xss')"
    nuclei -tc "contains(tags,'cve') && contains(tags,'ssrf')"
    nuclei -tc "contains(name, 'Local File Inclusion')"
    

将结果保存到res.txt

    
    
    nuclei -l urls.txt -o results.txt
    

nuclei 可以通过管道标准的输入 (STDIN) 传递 URL 列表

    
    
    cat urls.txt | nuclei -o results.txt
    

docker 调用

    
    
    cat urls.txt | docker run -v /path/to/nuclei-templates:/app/nuclei-templates -v /path/to/nuclei/config:/app/.nuclei-config.json -i projectdiscovery/nuclei -t /app/nuclei-templates/files/git-config.yaml > results.txt
    

## 三、使用优化

 **速率限制**

Nuclei 有多种控制速率的方法，包括并行执行多个模板、并行检查多个主机，以及使 nuclei 限制全局的请求速率，下面就是示例。

  * `-c`参数 - 限制并行的模板数

  * `-bulk-size`参数 - 限制并行的主机数

  * `-rate-limit`参数 - 全局速率限制

如果你想快速扫描或者控制扫描，请使用这些标志并输入限制数，`速率限制`只保证控制传出的请求，与其他参数无关。  
 **排除模板**

[Nuclei模板](https://github.com/projectdiscovery/nuclei-templates)包含多种检查，其中有许多对攻击有用的检查，但并不是都有用的。如果您只希望扫描少数特定的模板或目录，则可以使用如下的参数筛选模板，或将某些模板排除。

  *  **排除模板运行**

我们不建议同时运行所有的 nuclei 模板，如果要排除模板，可以使用 `exclude`参数来排除特定的目录或模板。

    
        nuclei -l urls.txt -t nuclei-templates -exclude panels/ -exclude technologies -exclude files/wp-xmlrpc.yaml
    

注意：如上述示例中显示的那样，目录和特定模板都将不会扫描

 **挂代理**

    
    
    nuclei -l xxx.txt -t xxx.yaml -proxy-url http://192.168.1.1:8080
    

**调试**

    
    
    nuclei -l xxx.txt -t xxx.yaml -v -duc
    nuclei -l xxx.txt -t xxx.yaml -debug -duc
    nuclei -l xxx.txt -t xxx.yaml -debug-req -duc
    

**其他**

    
    
    # 断网环境
    # -ni -stats -si 20 -rate-limit 500 -timeout 3
    
    # 报错跳过(2.5.0 开始支持)
    # -max-host-error 10
    
    # 速率
    # -rate-limit 500
    
    # 超时时间
    # -timeout 3
    
    # 不更新
    # -duc
    
    # 无网络环境下
    # -ni
    
    # 监控
    # -stats -si 60
    
    # 无颜色
    # -nc
    

**参考链接** ：

[nuclei](https://github.com/projectdiscovery/nuclei)

[nuclei-doc](https://nuclei.projectdiscovery.io/templating-guide/)

[学习笔记-nuclei ](https://www.cnblogs.com/haidragon/p/16852363.html)

