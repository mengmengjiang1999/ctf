HFish是一款基于 Golang 开发的跨平台多功能主动诱导型开源蜜罐框架系统，为了企业安全防护做出了精心的打造，全程记录黑客攻击手段，实现防护自主化。

1、多功能 不仅仅支持 HTTP(S) 蜜罐，还支持 SSH、SFTP、Redis、Mysql、FTP、Telnet、暗网等；  
2、扩展性 提供 API 接口，使用者可以随意扩展蜜罐模块 ( WEB、PC、APP )；  
3、便捷性使用 Golang SQLite 开发，使用者可以在 Windows、Linux上快速部署一套蜜罐平台。  
![image](https://image.3001.net/images/20210511/1620702593_6099f5813e133bd8bd4c3.png!small)  
蜜罐 技术本质上是一种对攻击方进行 欺骗的技术，通过布置一些作为 诱饵的主机、网络服务 或者 信息，诱使攻击方对它们实施攻击，从而可以对攻击行为进行 捕获
和 分析，了解攻击方所使用的工具与方法，推测攻击意图和动机，能够让防御方清晰地了解他们所面对的安全威胁，并通过技术和管理手段来增强实际系统的安全防护能力。

蜜罐 好比是
情报收集系统。蜜罐好像是故意让人攻击的目标，引诱黑客前来攻击。所以攻击者入侵后，你就可以知道他是如何得逞的，随时了解针对服务器发动的最新的攻击和漏洞。还可以通过窃听黑客之间的联系，收集黑客所用的种种工具，并且掌握他们的社交网络。

HFish安装法式有很多种，这次就演示用docker搭建，首先下载镜像。其他平台可在HFish[官方网站](https://hfish.io/download.html)下载后搭建。

  1. 搭建

docker pull imdevops/hfish  
![image.png](https://image.3001.net/images/20210511/1620695804_6099dafc9647381773b4d.png!small)  
主节点管理端部署  
docker images  
docker run -d -it -p 21:21 -p 22:22 -p 23:23 -p 3306:3306 -p 6379:6379 -p
8080:8080 -p 8989:8989 -p 9000:9000 -p 9001:9001 -p 11211:11211 -p 69:69 -p
5900:5900 -p 8081:8081 -p 9200:9200 82eb5b672835  
![image.png](https://image.3001.net/images/20210511/1620695922_6099db7201c5e3a986d40.png!small)

  2. 端口描述

以下端口根据实际需要决定是否打开，并注意端口冲突。

21 为 FTP 端口  
22 为 SSH 端口  
23 为 Telnet 端口  
3306 为 Mysql 端口  
6379 为 Redis 端口  
7879 为集群通信 RPC 端口  
8080 为 暗网 端口  
8989 为 插件 端口  
9000 为 Web 端口  
9001 为 系统管理后台 端口  
11211 为 Memcache 端口

  3. 启动

在Safari中输入localhost:9001  
![image.png](https://image.3001.net/images/20210511/1620696512_6099ddc05e394f8613556.png!small)  
默认初次登陆账号密码为admin/admin

  4. 映入眼帘的是一个世界政区图，有点意思，可以切换显示状态。

![image.png](https://image.3001.net/images/20210511/1620699906_6099eb02ccd39fbb85650.png!small)  
![image.png](https://image.3001.net/images/20210511/1620700114_6099ebd206bc3087b0f20.png!small)

  5. 监测测试

![image.png](https://image.3001.net/images/20210511/1620702331_6099f47b342846ed654cb.png!small)  
![image.png](https://image.3001.net/images/20210511/1620702356_6099f494719ad6438dae8.png!small)![image.png](https://image.3001.net/images/20210511/1620700277_6099ec75d0226a5237f57.png!small)

  6. 注意事项

1、邮箱 SMTP 配置后需要开启方可使用  
2、API 接口 info 字段，&& 为换行符  
3、启动 WEB 蜜罐，请先启动 API 模块  
4、WEB 插件 需在 WEB 目录下 编写  
5、WEB 插件 下面必须存在两个目录  
6、集群 心跳为 60 秒,断开显示会延迟 60 秒

端口自定义  
![image.png](https://image.3001.net/images/20210511/1620741855_609a8edf329b767564aad.png!small)  
![image.png](https://image.3001.net/images/20210511/1620741931_609a8f2bcfcf6f3dedb40.png!small)  
![image.png](https://image.3001.net/images/20210511/1620741955_609a8f43cc8d21cb89e4d.png!small)  
*注重密钥  
防止数据被用。  
![image.png](https://image.3001.net/images/20210511/1620742053_609a8fa5beb45014adc40.png!small)

  7. nmap对HFish的影响  
nmap --scrpit=brute ip 造成系统直接下线，FTP爆破85%，MYSQL10%，TELNET3%，VNC2%  
nmap --scrpit=vuln ip 对MYSQL90%，VNC8%，FTP1%，TELNET1%。  
msfconsole正在路上。。。

