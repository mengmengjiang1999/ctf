## 说明

myscan是参考awvs的poc目录架构，pocsuite3、sqlmap等代码框架，以及搜集互联网上大量的poc，由python3开发而成的被动扫描工具。
此项目源自个人开发项目，结合个人对web渗透，常见漏洞原理和检测的代码实现，通用poc的搜集，被动扫描器设计，以及信息搜集等思考实践。

## 安装

### 环境

python 3.7.x  
redis

### 安装步骤

1、下载githuub中相关文件github地址：https://github.com/amcai/myscan

2、进入cd myscan安装依赖

    
    
    pip3 install -r requirements.txt
    

3、打开burpsuite中Extender->Extensions 在Burp
Extension中添加myscan下的myscan_burp_extension.jar，burpsuite中增加Myscan

## 使用

1、启动redis

    
    
    redis-server # 起一个redis服务，默认监听127.1:6379
    

2、打开burpsuite中Myscan

  * myscan Configure 分别设置为open ture

  * 点击set redis  
日志中出现以下信息即可关联成功

    
    
    Change proxymode from close to open
        Redis connect using args: pwd:null host:127.0.0.1 port:6379 db:0
        Create redis pool success
        Ping redis success
        Connect redis-server success!
    

4、在myscan下运行

    
    
    python cli.py -h #获取更多参数
    

建议大批量测试时候禁用未授权,baseline，cors，jsonp等插件，指定输出:

    
    
    python3 cli.py webscan --disable power baseline cors jsonp sensitive_msg_transfer host_inject --html-output test.html
    

大批量测试时只测试严重rce的poc，可在--enable筛选出来的的poc上再次通过--level 3，筛选严重等级的poc

    
    
    python3 cli.py webscan --enable poc_ struts2 --level 3
    

注意：  
1、python一定要在3.7.x版本，3.8版本会出现语法问题.  
2、/pocs/perfolder/solarwinds/poc_solarwinds_cve-2020-10148_fileleak.py  
目前暂时有问题，最好删除再运行

## 相关命令解释

    
    
    positional arguments:
      {webscan,hostscan,reverse}
                            选择一个模式，接受 webscan , hostscan, reverse
    
    optional arguments:
      -h, --help            show this help message and exit
      --version             显示版本号并退出
    
    Connect:
      At least one of these options has to be provided to define the target(s)
    
      --redis REDIS         连接redis主机 (e.g. "--redis password@host:port:db"),默认:
                            null@127.0.0.1:6379:0
    
    Common:
      一般配置
    
      -v {0,1,2,3}, --verbose {0,1,2,3}
                            0 ==> Show :all(debug,info,error,critical .1 ==> Show:
                            info,error,critical 2 ==> Show: error,critical3 ==>
                            Show :critical
      --html-output HTML_OUTPUT
                            默认myscan_result_{num}.html 指定漏洞输出文件
      --clean               使用此参数可清除Redis所有数据
      --check-reverse       检测reverse service 是否正常
    
    hostscan:
      Config hostscan
    
      --input-nmapxml INPUT_NMAPXML
                            从nmap -oX 报告输入
      --input-nmaptext INPUT_NMAPTEXT
                            从nmap -oN 报告输入
      --input-jsonfile INPUT_JSONFILE
                            从指定文件格式输入,格式参考 'docs/Class3-hostscan开发指南.md'
    
    pocs:
      Config pocs args and pocs to targets
    
      --disable DISABLE [DISABLE ...]
                            默认全部开启POC，使用此参数代表禁止的POCS，根据POC文件名包含字符串判断，e.g.
                            --disable xss sqli un_auth，可使用--disable all
                            代表关闭全部，此时常配合--plugins 使用
      --enable ENABLE [ENABLE ...]
                            默认全部开启POC，使用此参数代表仅开启的POCS，根据POC文件名包含字符串判断，e.g.
                            --enable xss sqli
                            un_auth则POC名字包含xss,sqli,un_auth则都会开启,如果同时使用 --enable
                            --disable ， --enable将不会起作用
      --dishost DISHOST [DISHOST ...]
                            使用此参数代表不扫描主机 .默认"baidu.com","google.com","firefox.com"
                            ,"mozilla.org","bdstatic.com","mozilla.com"
      --host HOST [HOST ...]
                            只扫描的主机,主机名不携带端口
      --level LEVEL         再次筛选poc的level等级，可选择-1，1，2，3，分别代表-1:Info 0:Low 1:Medium
                            2:High 3:Critical，poc的level>=level则保留poc，常用与只测试高危poc，则
                            --level 2，default:-1
    
    Controller:
    
      --threads {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20}
                            某些POC的线程数，默认3
      --process {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60}
                            myscan的POC进程数，默认5
      --process-plugins {1,2,3,4,5,6,7,8,9}
                            myscan的Plugin进程数，默认5
    
    Request:
      配置请求参数
    
      --retry RETRY         定义全局request出错后重新尝试请求次数，默认0
      --ipv6                需网络支持ipv6，使用此参数优先ipv6地址,ipv6无记录再使用ipv4地址
    
    Plugin:
      对流量进行收集的插件
    
      --plugins PLUGINS [PLUGINS ...]
                            指定插件
    
    Proxy:
      Proxy accept: http,https
    
      --proxy PROXY         网络代理,接受host:port形式,e.g:127.0.0.1:8080
    

参考文献：

<https://www.bilibili.com/video/BV1tV411f7p6>  
<https://github.com/amcai/myscan>

