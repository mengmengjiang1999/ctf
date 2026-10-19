![](https://image.3001.net/images/20220107/1641527226_61d7b7baa74ebf498b522.png!small)

## 关于PoW-Shield

PoW-Shield是一款功能强大的网络安全防御工具，该工具可以帮助广大研究人员和用户抵御DDoS攻击和垃圾邮件攻击。除此之外，PoW-Shield还带有Web应用防火墙功能，并提供了Docker镜像以方便实现快速轻量级部署。

PoW-Shield可以通过充当代理的形式，并利用后端服务和最终用户之间的工作证明，在OSI应用层提供DDoS保护。该项目旨在提供针对通用验证码方法的替代方案，比如说Google的ReCaptcha，而这一点对于社区来说一直都是一个难题。访问受PoW-Shield保护的Web服务也非常简单，直接打开浏览器并填写目标站点URL，浏览器将会自动为我们完成剩余的安全验证。

 **PoW-Shield旨在通过一个单一Web应用或Docker镜像提供下列服务：**

> 工作证明验证
>
> 访问频率限制和IP黑名单
>
> Web应用程序防火墙

## 功能介绍

> Web服务结构
>
> 代理功能
>
> PoW实现
>
> Docker化部署
>
> IP黑名单功能
>
> 访问频率限制
>
> 单元测试
>
> Web应用程序防火墙实现
>
> 多实例同步（Redis）

![](https://image.3001.net/images/20220107/1641527239_61d7b7c79bf8d9e7a37a2.png!small)

## 工具下载&使用

### Node.js

首先，我们可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/RuiSiang/PoW-Shield.git

接下来，安装该工具所需的依赖组件：

    
    
    npm install

然后配置工具相关信息：

    
    
    cp -n .env.example .env
    
    # edit .env
    
    nano .env

运行下列命令执行代码构建：

    
    
    npm run build

执行并同时启动数据库（建议使用轻量级的Redis）：

    
    
    # install redis first
    
    # sudo apt-get install redis-server
    
    npm start

执行但不启动数据库：

    
    
    npm run start:standalone # linux
    
    npm run start:standalone-win # windows

测试工具功能（可选）：

    
    
    npm test

### Docker（[ _库_](https://hub.docker.com/repository/docker/ruisiang/pow-shield)）

Docker带Redis数据库运行：

    
    
    docker run -p 3000:3000 -e BACKEND_URL="http://example.com" -d ruisiang/pow-shield

Docker不带数据库运行：

    
    
    docker run -p 3000:3000 -e BACKEND_URL="http://example.com" -e NODE_ENV="standalone" -d ruisiang/pow-shield

### Docker-Compose

首先我们需要使用下列命令配置docker-compose.example.yaml：

    
    
    cp -n docker-compose.example.yaml docker-compose.yaml
    
    # edit docker-compose.yaml
    
    nano docker-compose.yaml

接下来，我们就可以启动容器了：

    
    
    docker-compose up

## 工具配置

### 配置方法

    
    
    nodejs：（样例：.env.example）
    
    docker-compose：docker-compose.yaml（样例：docker-compose.example.yaml）
    
    docker run：-e参数

## 环境变量

### 常用配置

> PORT：待监听端口，默认为3000
>
> SESSION_KEY：cookie签名所需的密钥
>
> BACKEND_URL：代理验证流量的目的地址，接受IP和URL

### 数据库选项（Redis）

> DATABASE_HOST：Redis服务主机地址，默认为127.0.0.1
>
> DATABASE_PORT：Redis服务端口，默认为6379
>
> DATABASE_PASSWORD：Redis服务密码，默认为空

### PoW选项

> POW：是否开启PoW功能，默认为on（开）
>
> NONCE_VALIDITY：指定Nonce生成后多久才发送至服务器，默认为60000
>
> INITIAL_DIFFICULTY：初始难度，生成的哈希中前导0位的数量，默认为13

### 访问频率选项

> RATE_LIMIT：是否开启频率限制，默认为on（开）
>
> RATE_LIMIT_SAMPLE_MINUTES：指定会话/ip的统计信息重置间隔分钟数，默认为60
>
> RATE_LIMIT_SESSION_THRESHOLD：单个会话在触发令牌撤销之前能发送的请求数量，默认为100
>
> RATE_LIMIT_BAN_IP：是否开启IP黑名单功能，默认为on（开）
>
> RATE_LIMIT_IP_THRESHOLD：指定会话/ip在地址被拉黑之前发送的请求数量，莫尔奈威500
>
> RATE_LIMIT_BAN_MINUTES：IP地址拉黑时间，默认为15分钟

### WAF选项

> WAF
>
> WAF_URL_EXCLUDE_RULES：是否开启Web应用防火墙，默认为on（开）
>
> WAF_HEADER_EXCLUDE_RULES：在扫描请求URL时引入额外规则
>
> WAF_BODY_EXCLUDE_RULES：在扫描请求Body时引入额外规则

## 许可证协议

本项目的开发与发布遵循BSD 3-Clause开源许可证协议。

## 功能演示视频

 **视频地址：** https://you*tu.be/zeNKUDR7_Jc

## 项目地址

 **PoW-Shield：** 【[ _GitHub传送门_](https://github.com/RuiSiang/PoW-Shield)】

## 参考资料

> [ _https://ruisiang.medium.com/pow-shield-application-layer-proof-of-work-> ddos-filter-4fed32465509_](https://ruisiang.medium.com/pow-shield-> application-layer-proof-of-work-ddos-filter-4fed32465509)
>
> [ _https://hub.docker.com/repository/docker/ruisiang/pow-> shield_](https://hub.docker.com/repository/docker/ruisiang/pow-shield)

