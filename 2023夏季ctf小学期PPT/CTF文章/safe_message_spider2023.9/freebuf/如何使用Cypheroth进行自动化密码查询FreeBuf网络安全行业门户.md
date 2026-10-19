![](https://image.3001.net/images/20210421/1619011136_60802640a82b09f0fc659.png!small)

## Cypheroth介绍

Cypheroth是一款自动化可扩展工具套件，在该工具的帮助下，广大研究人员可以针对Bloodhound的Neo4j后端执行自动化密码查询，并将输出数据存储至电子表格之中。

Cypheroth是一个Bash脚本，它能够自动对存储在Neo4j数据库中的Bloodhound数据执行密码查询。

待运行的密码查询列表是完全可扩展的，本文后面的章节还会介绍如何添加自己的密码查询格式。

当前版本的Cypheroth经过了充分的测试，可以在Linux、macOS和Windows上正常使用。

## 依赖组件

cypher-shell命令是跟Neo4j绑定的，它是Cypheroth所必须的。如果已经安装了Neo4j，但是找不到cypher-shell命令的话，你可能需要更新Neo4j的版本。

如果使用了ssconvert命令的话，该脚本将会将所有的.csv输出整合到一个.xls文件中。

在Windows系统上，我们建议大家使用WSL来运行该脚本，此时我们只需要在WSL中安装好cypher-shell包就行了。

## 工具使用

 **可用的参数选项：**

    
    
    -u Neo4J用户名（必须）
    
      -p Neo4J密码（必须）
    
      -d 全限定域名（必须）（大小写敏感）
    
      -a 本地地址（可选）（默认：localhost:7687）
    
      -t 查询超时（可选）（默认：30s）
    
      -v Verbose模式（可选）（默认：FALSE）
    
      -h 显示帮助信息和使用样例（可选）

 **默认配置运行：**

    
    
    ./cypheroth.sh -u neo4j -p BloodHound -d TESTLAB.LOCAL

 **全选项运行样例：**

    
    
    ./cypheroth.sh -u neo4j -p hunter2 -d BigTech.corp -a 10.0.0.1:7687 -t 5m -v true

文件会被添加进子目录中，以FQDN命令。

## 密码查询

该脚本当前支持60种查询方式，下面给出的是用户能接收到的数据样例：

> 完整用户属性列表
>
> 完整的计算机属性列表
>
> 完整域属性列表
>
> 完整的OU属性列表
>
> 完整GPO属性列表
>
> 完整组属性列表
>
> 具有管理员权限的计算机
>
> 没有管理员权限的计算机
>
> Kerberoastable用户以及具备管理员权限的计算机

如需添加额外查询，请编辑cypheroth.sh中的queries数组，并使用下列格式添加数据：

    
    
    Description;Cypher Query;Output File

如果添加的查询需要域名值的话，需要将其存储为$DOMAIN。

 **样例一：**

    
    
    All Usernames;MATCH (u:User) RETURN u.name;usernames.csv

 **样例二：**

    
    
    All Domain Admins;MATCH (u:User) MATCH (g:Group {name:'DOMAIN ADMINS@$DOMAIN'}) RETURN u.displayname;domainAdmins.csv

## 分析多个域名

如果你需要分析多个域名，你可以同时运行多个Cypheroth实例，并分别分析多个域名。你可以使用下列格式的脚本，同时运行10个实例：

    
    
    #!/usr/bin/env bash
    
    DOMAINS=(domA.example.net domB.example.net [...])
    
    parallel -j10 --lb ./cypheroth.sh <args> -d {} ::: "${DOMAINS[@]}"

## 疑难问题

如果你运行的并非最新版本的Cypheroth，你可能会遇到下列错误信息：

    
    
    DateTime is not supported as a return type in Bolt protocol version 1.
    
    Please make sure driver supports at least protocol version 2.
    
    Driver upgrade is most likely required.

如需解决，请将Neo4j更新至最新版本。

## 工具演示

**演示地址：**<https://github.com/seajaysec/cypheroth/blob/master/img/demo_v1_4.svg>

## 项目地址

 **Cypheroth：**<https://github.com/seajaysec/cypheroth>

