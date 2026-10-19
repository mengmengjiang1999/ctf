## 关于溯光

 **溯光（TrackRay）是一个由Java语言编写的服务式插件化渗透测试框架，项目是一个WEB服务，提供了调用插件和扫描的接口，并且使用了
Websocket 技术实现命令行风格交互，启动后只需要通过浏览器即可使用，有着多数开源渗透测试框架不具备的特点。**

 **自更新 2.0 版本后，项目数据库采用嵌入式数据库hsqldb，使用 SpringBoot
框架开发，用maven管理依赖，使开发和使用更为简单方便。**

## 特点

> 提供WEB服务接口；
>
> 使用只需要一个浏览器；
>
> 第一个使用Java集成MSF & AWVS的开源项目；
>
> 内置插件式扫描器

## 如何使用

    
    
    git clone <https://github.com/iSafeBlue/TrackRay.git>
    
    安装nmap，写入环境变量
    
    启动SQLMAP API
    
    启动msfrpc服务 msfrpcd -U msf -P msf -S -f
    
    启动AWVS
    
    在application.properties配置文件中修改 database.dir及以上有变更的配置参数
    
    编译并运行SpringBoot启动类WebApplication.java

## 功能展示

### 交互式插件控制台

![](https://image.3001.net/images/20190228/15513446844853.gif!small)

### MSF 控制台

![](https://image.3001.net/images/20190228/15513446962025.gif!small)

### 无交互插件调用

![](https://image.3001.net/images/20190228/15513447258233.png!small)

![](https://image.3001.net/images/20190228/15513447381614.gif!small)

### 扫描器展示

![](https://image.3001.net/images/20190228/15513447483498.gif!small)

> 项目主页：<https://github.com/iSafeBlue/TrackRay>。

 ***本文作者：浅蓝，转载请注明来自FreeBuf.COM**

