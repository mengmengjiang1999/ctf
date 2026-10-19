![](https://image.3001.net/images/20210821/1629529267_6120a4b3dec18d3fc86b6.png!small)

## 关于Lazyrecon

Lazyrecon是一款功能强大的网络侦察自动化工具，在该工具的帮助下，广大研究人员能够轻松以有组织的形式实现网络侦察的自动化。

从本质上来说，Lazyrecon是一款子域名发现工具，它能够查找并解析有效子域名，然后执行SSRF/LFI/SQLi模糊测试、暴力破解和端口扫描等任务。该工具拥有简单的模块化体系架构，经过优化之后运行速度非常快。

## 功能介绍

超快速异步执行；

支持CI/CD工作流；

提供HTML/PDF格式报告；

Discord整合；

提供后台监听服务器；

域名、域列表、IP、CIDR输入-符号支持；

完整的程序管理；

## 工具运行流程

![](https://image.3001.net/images/20210821/1629529278_6120a4be2a34d48241dc6.png!small)

## 工具安装

注意：该工具目前仅在Linux和macOS操作系统上进行过测试。

### 工具要求

> python >= 3.7
>
> pip3 >= 19.0
>
> go >= 1.14

### CI/CD方法

首先，填写./lazyconfig中所要求的环境变量：

    
    
    export HOMEUSER= # your normal, non root user: e.g.: kali
    
    export HOMEDIR= # user's home dir e.g.: /home/kali
    
    export STORAGEDIR= # where output saved, e.g.: ${HOMEDIR}/lazytargets
    
    export GITHUBTOKEN=XXXXXXXXXXXXXXXXXX # a personal access token here
    
    export DISCORDWEBHOOKURL= # https://discord.com/api/webhooks/{webhook.id}/{webhook.token}
    
    export GOPATH=$HOMEDIR/go
    
    export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin:$GOROOT/bin:$HOME/.local/bin:$HOME/go/bin:$HOMEDIR/go/bin
    
    export GO111MODULE=on

接下来，启用新的环境变量：

    
    
    source ./lazyconfig

启用后，调用工具安装脚本：

    
    
    sudo -E ./install.sh

最后，执行下列命令即可使用Lazyrecon：

    
    
    sudo -E ./lazyrecon.sh "hackerone.com"

### GitHub Actions方法

使用DISCORDWEBHOOKURL和GITHUBTOKEN密钥对.github/workflows/test-recon-action.yaml进行自定义配置，并启用--discord来接收报告：

    
    
    - name: Install & Recon
    
        env:
    
          GO111MODULE: on
    
          DISCORDWEBHOOKURL: ${{ secrets.DISCORDWEBHOOKURL }}
    
          GITHUBTOKEN: ${{ secrets.GITHUBTOKEN }}
    
        run: |
    
          export HOMEDIR=$HOME
    
          export HOMEUSER=$RUNNER_USER
    
          export STORAGEDIR="${HOMEDIR}"/lazytargets
    
          sudo -E ./install.sh
    
          sudo -E ./lazyrecon.sh "hackerone.com" --quiet --discord

### 测试

如果需要判断工具依赖组件是否已经成功正确安装，可以运行下列命令：

    
    
    ./test/test_nuclei_templates.sh "./test/nuclei_templates_list.txt"
    
    ./test/test_install.sh "./test/dependencies_list.txt"

## 工具使用

    
    
    ▶ sudo -E ./lazyrecon.sh tesla.com --wildcard

 ** **参数****

|

 ** **描述****

|

 ** **样例****  
  
---|---|---  
  
\--wildcard

|

针对'*.tesla.com'执行子域名网络侦察扫描 (默认)

|

./lazyrecon.sh tesla.com --wildcard  
  
\--single

|

指定目标实例 'tesla.com'

|

./lazyrecon.sh tesla.com --single  
  
\--ip

|

指定目标设备单个IP地址

|

./lazyrecon.sh 192.168.0.1 --single --ip  
  
\--list

|

待处理的子域名列表

|

./lazyrecon.sh "./testa.txt" --list  
  
\--cidr

|

执行网络侦察（CIDR）

|

./lazyrecon.sh "192.168.0.0/16" --cidr  
  
\--fuzz

|

SSRF/LFI/SQLi模糊测试

|

./lazyrecon.sh tesla.com --mad --fuzz  
  
\--brute

|

几乎目录暴力破解

|

./lazyrecon.sh tesla.com --single --brute  
  
\--discord

|

向Discord发送通知

|

./lazyrecon.sh tesla.com --discord  
  
\--quiet

|

启用静默模式

|

./lazyrecon.sh tesla.com --quiet  
  
## 项目地址

 **Lazyrecon：** 【[ _GitHub传送门_](https://github.com/storenth/lazyrecon)】

## 参考资料

[ _https://www.aon.com/cyber-solutions/aon_cyber_labs/finding-more-idors-tips-and-tricks/?utm_source=newsletter
&utm_medium=email&utm_campaign=bug_bytes_110_scope_based_recon_finding_more_idors_how_to_hack_sharepoint&utm_term=2021-02-17_](https://www.aon.com/cyber-solutions/aon_cyber_labs/finding-more-idors-tips-and-tricks/?utm_source=newsletter&utm_medium=email&utm_campaign=bug_bytes_110_scope_based_recon_finding_more_idors_how_to_hack_sharepoint&utm_term=2021-02-17)

[ _https://rez0.blog/hacking/2019/11/29/rce-via-imagetragick.html﻿_](https://rez0.blog/hacking/2019/11/29/rce-via-imagetragick.html)

[ _https://sidxparab.gitbook.io/subdomain-enumeration-guide/active-enumeration/dns-bruteforcing﻿_](https://sidxparab.gitbook.io/subdomain-enumeration-guide/active-enumeration/dns-bruteforcing)

