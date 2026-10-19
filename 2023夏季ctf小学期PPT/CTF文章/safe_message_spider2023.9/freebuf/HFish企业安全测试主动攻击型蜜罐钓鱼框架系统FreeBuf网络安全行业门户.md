***本工具仅供技术分享、交流讨论，严禁用于非法用途**

![](https://image.3001.net/images/20190804/1564931274_5d46f4cac05de.png!small)

## 介绍

 **HFish是一款基于 Golang 开发的跨平台多功能主动攻击型蜜罐钓鱼平台框架系统，为了企业安全防护测试做出了精心的打造。**

> 多功能不仅仅支持 HTTP(S) 钓鱼，还支持 SSH、SFTP、Redis、Mysql 等
>
> 扩展性提供 API 接口，使用者可以随意扩展钓鱼模块 ( WEB、PC、APP )
>
> 便捷性使用 Golang 开发，使用者可以在 Win + Mac + Linux 上快速部署一套钓鱼平台

## 快速部署

### 部署说明

> 下载当前系统二进制包
>
> cd 到程序根目录，修改 config.ini 配置文件
>
> 执行 ./HFish run 启动服务
>
> 浏览器输入[http://localhost:9001](http://localhost:9001/)打开

### 帮助页面

![](https://image.3001.net/images/20190804/1564931250_5d46f4b2836fb.png!small)

### 启动服务

###
![](https://image.3001.net/images/20190804/1564931288_5d46f4d8b0487.png!small)

### 部分界面展示

![](https://image.3001.net/images/20190804/1564931315_5d46f4f3abaaa.png!small)

![](https://image.3001.net/images/20190804/1564931325_5d46f4fd75d70.png!small)

## 部分功能使用演示

### WEB 钓鱼

![](https://image.3001.net/images/20190804/1564931345_5d46f5110d015.png!small)

### Redis 钓鱼

![](https://image.3001.net/images/20190804/1564931358_5d46f51e04d3d.png!small)

### Mysql 钓鱼

![](https://image.3001.net/images/20190804/1564931370_5d46f52ab5dc8.png!small)

## TODO

> [x] 登录模块
>
> [x] 仪表盘模块
>
> [x] 上钩列表
>
> [x] 邮件群发
>
> [x] 命令行优化
>
> [x] 支持自定义 WEB 模板
>
> [x] 支持 Mysql 服务端获取连接客户端电脑任意文件
>
> [x] 支持 HTTP(S)、SSH、SFTP、Redis、Mysql 协议
>
> [ ] 支持 FTP、Telnet、SMTP、POP3、TFTP、Oracle、VPN 等
>
> [ ] 暗网钓鱼支持
>
> [ ] 自动化钓鱼支持
>
> [ ] 钓鱼报告生成
>
> [ ] 支持更多的 WEB 模块
>
> [ ] 日记完善优化
>
> [ ] 规划更多的功能...

## 关于

> Team: HackLC
>
> URL:[https://hack.lc](https://hack.lc/)

## 地址

> 码云：<https://gitee.com/lauix/HFish>
>
> 下载：<https://gitee.com/lauix/HFish/releases>
> [](https://gitee.com/lauix/HFish/releases)

***本文作者：天才小三斤，转载请注明来自FreeBuf.COM**

