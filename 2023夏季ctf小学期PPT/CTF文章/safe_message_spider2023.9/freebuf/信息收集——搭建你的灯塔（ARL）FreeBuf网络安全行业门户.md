​真的很好用，每次攻防都用它，会发现一些意想不到的惊喜

## 灯塔安装

我这边是使用docker安装，这个灯塔的说明文档里这么写的[doge]

github地址：<https://github.com/TophantTechnology/ARL>

安装命令：

    
    
    git clone https://github.com/TophantTechnology/ARL
    cd ARL/docker/
    docker volume create arl_db
    docker-compose pull
    docker-compose up -d

灯塔就安装完成了，在浏览器中访问https://ip:5003 其中ip为Linux的ip 可通过ifconfig命令查询，登陆界面如下

![](https://image.3001.net/images/20221114/1668388766_6371979e94c9d8ccc4e94.png!small)​编辑

默认账号密码为：admin/arlpass ，登陆后界面如下

原谅我的厚码，还没来得及删除任务

![](https://image.3001.net/images/20221114/1668388767_6371979f947cf289d097d.png!small)​编辑

## 具体功能：

1| 任务名称| 任务名称  
---|---|---  
2| 任务目标| 任务目标，支持IP，IP段和域名。可一次性下发多个目标  
3| 域名爆破类型| 对域名爆破字典大小, 大字典：常用2万字典大小。测试：少数几个字典，常用于测试功能是否正常  
4| 端口扫描类型| ALL：全部端口，TOP1000：常用top 1000端口，TOP100：常用top 100端口，测试：少数几个端口  
5| 域名爆破| 是否开启域名爆破  
6| DNS字典智能生成| 根据已有的域名生成字典进行爆破  
7| 域名查询插件| 已支持的数据源为11个，`alienvault`, `certspotter`,`crtsh`,`fofa`,`hunter`等  
8| ARL 历史查询| 对arl历史任务结果进行查询用于本次任务  
9| 端口扫描| 是否开启端口扫描，不开启站点会默认探测80,443  
10| 服务识别| 是否进行服务识别，有可能会被防火墙拦截导致结果为空  
11| 操作系统识别| 是否进行操作系统识别，有可能会被防火墙拦截导致结果为空  
12| SSL 证书获取| 对端口进行SSL 证书获取  
13| 跳过CDN| 对判定为CDN的IP, 将不会扫描端口，并认为80，443是端口是开放的  
14| 站点识别| 对站点进行指纹识别  
15| 搜索引擎调用| 利用搜索引擎结果爬取对应的URL  
16| 站点爬虫| 利用静态爬虫对站点进行爬取对应的URL  
17| 站点截图| 对站点首页进行截图  
18| 文件泄露| 对站点进行文件泄露检测，会被WAF拦截  
19| Host 碰撞| 对vhost配置不当进行检测  
20| nuclei 调用| 调用nuclei 默认PoC 对站点进行检测 ，会被WAF拦截，请谨慎使用该功能  
  
其中文件泄露经常会找到一些敏感文件（可能是我运气好[doge]）

## 解除限制

灯塔默认是无法扫描edu,org,gov网站的，但是可以解除限制

首先打开 /ARL/docker目录下的config-docker.yaml，注释掉这三行

![](https://image.3001.net/images/20221114/1668388768_637197a07943d67ba4f37.png!small)​编辑

然后进入 /ARL/app目录，打开config.py和config.yaml.example文件，相应位置修改为

![](https://image.3001.net/images/20221114/1668388769_637197a15a33499a65525.png!small)​编辑

![](https://image.3001.net/images/20221114/1668388770_637197a24779228d4ed57.png!small)​编辑

之后进入web容器中修改配置，使用命令docker ps查看，找到NAME为arl_web的一行复制CONTAINER ID，如图圈中的参数

![](https://image.3001.net/images/20221114/1668388771_637197a331d694a0fb192.png!small)​编辑

输入命令docker exec -it (你的CONTAINER ID值) /bin/bash

![](https://image.3001.net/images/20221114/1668388772_637197a427d5e6e1d4de0.png!small)​编辑

cd app 进入路径，修改其中的config-docker.yaml、config.py和config.yaml.example三个文件，具体修改内容和上面的方法一致

重启灯塔就无限制了

