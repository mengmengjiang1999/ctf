## 一、背景

最近在几个微信群里看到好些人在讨论这个QingScan扫描器，听他们聊得火热我也去GitHub上看了看，GitHub的介绍说集合了各类安全工具，只需要输入一个URL,便会自动调用近30款安全工具对目标进行扫描，于是我下载了一个试试效果咋样。

    
    
    项目地址：https://github.com/78778443/QingScan
    

![fd766652431c49a18ea177571fa0b3e5.png](https://image.3001.net/images/20211214/1639487743_61b898ffc24d5ffee3d8a.png!small)

## 二、 开启插件

按照提示安装完成后，用浏览器访问`http://ip:8000/`，默认账号密码`test1``123456`，

进入系统设置→守护进程管理，进入后打开本次想要使用的插件，听说这个功能是因为插件太多了，全开启电脑CPU会非常高，我开启了我所需要的一些插件。

![c4533f2a5e014205827fa0326e0084a8.png](https://image.3001.net/images/20211214/1639487771_61b8991b69dc3bca32aab.png!small)  
开启所需要的插件，接下来去添加URL让它自动扫描。

## 三、 添加扫描

点击黑盒扫描→添加，输入“应用名称，URL地址”，需要登陆扫描的就是输入账号和密码，不需要则不用填，其他默认就好，点击提交，会自动进行扫描。

![8d481810420d4a15a84cf2a8a6bf0373.png](https://image.3001.net/images/20211214/1639487790_61b8992e74467032b0494.png!small)

## 四、查看扫描结果

点击“查看详情”去查看漏洞详细信息，可以看到app信息、指纹识别、子域名等等。

![9cf94a474e8d467b8a6687069af4e3c0.png](https://image.3001.net/images/20211214/1639487847_61b899678e62bfae640d3.png!small)

下图是项目的app信息、whatweb指纹识别、子域名、主机暴力破解、扫后台、SQL注入、vulmap漏洞，如下图所示：

![b8160ffb86fd4c1d86d0cb7435555a2f.png](https://image.3001.net/images/20211214/1639487905_61b899a1010b92a5faeba.png!small)

### 4.1 nmap

点击信息收集→nmap列表，查询到了当前主机所开放了哪些端口以及对应的服务名称。  
![293dc503b76042939f48a959ddabcd94.png](https://image.3001.net/images/20211214/1639489150_61b89e7e0253c1d89a02b.png!small)

点击信息收集→主机列表，主机列表会自动检测IP所在地址国家、省份。

![47707aebff3e4cb5a4fe5c1f4904b8fa.png](https://image.3001.net/images/20211214/1639489166_61b89e8eefdfa0b589d61.png!small)

### 4.2 指纹识别

点击信息收集→whatweb列表，可以看到各个项目的指纹信息。

![5e406d6327344be0acf598d1e81313c7.png](https://image.3001.net/images/20211214/1639489174_61b89e96c153ef673ef31.png!small)

### 4.3 URL爬虫

点击黑盒扫描→URL列表，可以看见爬虫爬取到的url。

![43e9be4e037e49abaeae21286966c78b.png](https://image.3001.net/images/20211214/1639489247_61b89edf08e10f3126fec.png!small)

### 4.4 SQLMap

点击黑盒扫描→SqlMap列表，sqlmap会根据URL列表里的链接去扫描，将有漏洞的链接展示在下图。

![cb6af0b6c5354953929443935c9f7c7f.png](https://image.3001.net/images/20211214/1639489300_61b89f14a7fa9f171ed21.png!small)

### 4.5 Xray

点击黑盒扫描→Xray列表，可以看见Xray扫出来的漏洞。

![903fed72254d4624b06511a3b33ea906.png](https://image.3001.net/images/20211214/1639489227_61b89ecb0df11f6d193fc.png!small)

## 四、总结

信息收集和黑盒扫描已经测试的差不多了，总体来说QingScan确实很方便，我只输入了URL,他会帮我去调用各种工具，这一点简直不要太爽，就像有人将他的渗透经验通过这种方式传递给你，有一说一，这个界面展示效果做的实在是不太好看。

