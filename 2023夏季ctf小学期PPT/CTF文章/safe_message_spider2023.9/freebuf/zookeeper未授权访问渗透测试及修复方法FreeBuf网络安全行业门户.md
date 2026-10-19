# zookeeper未授权访问危害

服务器信息泄露、集群被破坏

## 一、 四字命令未授权使用

工具：netcat ，Linux或Windows都可以测

命令行输入echo envi|nc 10.10.10.10 2181即可查看服务器信息

命令有：<https://www.runoob.com/w3cnote/zookeeper-sc-4lw.html>

修复：不想泄露信息可以修改zookeeper/conf/zoo.cfg（zookeeper为安装目录），注释掉4lw.commands.whitelist相关的行。四字命令用于查询状态，zookeeper默认不开放这些命令，只有在白名单中才能运行。

  

## 二、 未授权连接及节点操作

工具：Linux下安装zookeeper；或Windows下使用Java8运行zktools

<https://blog.csdn.net/rongbaojian/article/details/82078368>

Linux下，输入 zookeeper/bin/zkCli.sh -server 10.10.10.10:2181 即可连接，可使用get /node
watch或set /node 1等命令去操作节点，如果成功，则证明此节点存在未授权访问。

Windows下，只要zktools连接成功，则证明 **所有**
节点存在未授权访问。值得注意的是，如果某个节点有权限控制，那么zktools就无法连接成功，无法访问其他未授权节点了。但是Linux下zkCli.sh仍可访问其他未授权节点。

 **修复：**

1、ip ACL授权策略

可以使用setAcl -R /node ip:127.0.0.1:cdrwa,ip:10.10.11.11:cdrwa
（-R为递归，cdrwa为权限）等操作限制访问节点的IP

2、auth ACL授权策略

即用户模式，制定策略后，访问者必须使用addauth digest user:passwd登录才能进行节点操作。

策略制定方法为，用zkCli.sh连接后，在其中运行addauth digest
user:passwd（digest是固定的）来注册用户，可以有多个用户。然后运行setAcl /node
auth::cdrwa（auth是固定的），之后可运行getAcl
/node查看，能发现之前注册的用户都被配入了节点的权限中。使用quit退出，再连接，可发现只有在addauth登录之后才能操作节点。

3、digest Acl授权策略

不难发现策略2中，所有用户对节点的权限都是一致的，只能统一设置，若想使不同用户对节点的权限不同，可以使用digest
Acl授权策略，参见<https://blog.csdn.net/u014630623/article/details/103749103>

4、防火墙策略

使用以上策略限制节点后，任意用户仍可登录并用ls / 查看节点名字，但是无法获得详细信息和进行操作。若想不让任意用户访问2181端口，可以配置防火墙。

  

(๑•̀ㅂ•́)و✧

