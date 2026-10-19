![](./img/4142541870026223545.png)

## 简介

Chunsou（春蒐），Python3编写的多线程Web指纹识别工具，适用于安全测试人员前期的资产识别、风险收敛以及企业互联网资产摸查。目前主要功能为针对Web资产进行指纹识别，目前指纹规则条数约
10000+，辅助功能包括子域名爆破和FOFA资产收集。工具开发初衷为辅助网络安全人员开展测试工作，提高资产识别和管理的效率。`项目地址：https://github.com/Funsiooo/chunsou`

## 选项

Chunsou（春蒐）支持多线程扫描，默认线程为50，可根据需求指定线程数；可联动oneforall进行子域名爆破；支持调用 fofa api
进行资产收集；自定义流量代理；指定输出结果路径

![](./img/2453514683743045614.png)

    
    
    usage: python3 chunsou.py [options]
    
    target:
      -u , --url            scan for a single url
      -f , --file           specify a file for multi scanning
    
    subdomain:
      -du , --domain        subdomain blasting of a single domain name
      -df , --domains       subburst the domain name in the specified file
    
    api:
      -fo , --fofa          call the fofa api for asset collection
    
    others:
      -p , --proxy          proxy scan traffic
      -t , --threads        specify the number of scanning threads, default 50
      -h, --help            show this help message and exit
      -o , --output         specified output file
    
    example:
      -u , --url            python3 chunsou.py -u http://example.com
      -f , --file           python3 chunsou.py -f urls.txt
      -p  , --proxy         python3 chunsou.py -u http://example.com -p http://127.0.0.1
      -t  , --threads       python3 chunsou.py -f urls.txt -t 100
      -o  , --output        python3 chunsou.py -f -o results.txt
      -du , --domain        python3 chunsou.py -du example.com
      -df , --domains       python3 chunsou.py -df domains.txt
      -fo , --fofa          python3 chunsou.py -fo domain="example.com"

## 使用

> 说明

目前输出文件默认保存在 `results` 目录下，现仅支持`txt`格式，指纹识别输出信息顺序 `| 已匹配到的指纹 | 网站标题 | 网站所用的技术栈`

> 单目标指纹识别 python3 chunsou.py -u <http://example.com>

![](./img/6683430024265016340.png)

> 多目标指纹识别 python3 chunsou.py -f urls.txt

![](./img/5214388347848817433.png)

> 单目标子域名爆破 python3 chunsou.py -du example.com

目前调用 oneforall 进行子域名爆破

![](./img/8320171770047500572.png)

> 多目标子域名爆破 python3 chunsou.py -df domains.txt

![](./img/6516258492214575470.png)

> 调用 fofa api 进行资产收集 python3 chunsou.py -fo domain="example.com"

需要在 `chunsou/modules/config/config.ini` 进行 fofa api 配置

![](./img/8496329114812935867.png)

> 指定线程（默认50） python3 chunsou.py -u <http://example.com> -t 100

![](./img/7352257577656627566.png)

> 代理流量（http、https、socks5） python3 chunsou.py -f urls.txt -p
> <http://127.0.0.1:8080>

![](./img/8894981844397790880.png)

## 指纹

部分指纹来源于优秀开源项目 [Ehole](https://github.com/EdgeSecurityTeam/EHole) 、
[dismap](https://github.com/zhzyker/dismap)、 以及部分自收集，目前指纹规则条数约 10000+
(指纹条数，非程序个数)

指纹规则，目前支持`网站关键字`、`网页 title`、`网站 header`、`网站 ico hash` 四种指纹匹配方式，相应规则如下：

    
    
    {
        "cms": "亿赛通电子文档安全管理系统",
        "method": "keyword",
        "location": "body",
        "keyword": ["电子文档安全管理系统", "CDGServer3"]
    }, {
        "cms": "禅道",
        "method": "icon_hash",
        "location": "body",
        "keyword": ["3514039281"]
    }, {
        "cms": "ecology",
        "method": "keyword",
        "location": "header",
        "keyword": ["ecology_JSessionid"]
    }, {
        "cms": "Nacos",
        "method": "keyword",
        "location": "title",
        "keyword": ["Nacos"]
    }
    

## FQA

    
    
    1、后续加强对现有指纹的适配以及不定期更新自收集的指纹
    2、bug反馈：https://github.com/Funsiooo/Chunsou/issues

