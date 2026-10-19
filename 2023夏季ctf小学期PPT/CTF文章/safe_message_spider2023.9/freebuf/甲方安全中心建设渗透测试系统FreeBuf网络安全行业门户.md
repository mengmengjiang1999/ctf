> 上一篇代码审计系统：<https://www.freebuf.com/sectool/176414.html>

源码下载地址：<https://github.com/yingshang/banruo.git>

 **在甲方公司内部中存在着很多业务系统，作为安全工程师如果每天都去渗透测试的话，这样就显得非常没有效率。于是，决定自己写一个可以自动化渗透系统。**

程序的架构是py3.6+django，其中核心基础的就是mitmproxy这个库，不懂这个库的人，你可以理解为这是一个python版的burpsuite。这段时间我重构了程序，把库给更新，架构更加细化。

首先，我们需要配置好代理文件，监听网卡和端口，排除静态文件。

    
    
    "PROXY": {
      "PROXY_LISTEN_HOST": "0.0.0.0",  "PROXY_LISTEN_PORT": 9999,  "PROXY_LISTEN_MODE": "regular",  "EXCLUDE_STATIC_FILE": [
        ".js",    ".txt",    ".mp3",    ".css",    ".jpg",    ".png",    ".gif",    ".woff",    ".ico",    ".pdf",    ".mp4"  ]
    },
    

启动成功之后，可以看到代理处于关闭状态

    
    
    python3 manage.py runserver 0.0.0.0:8000
    

![image.png](https://image.3001.net/images/20191203/1575381732_5de66ae4c0a17.png!small)点击开始监听按钮，就可以看见右边端口已经启动了

![image.png](https://image.3001.net/images/20191203/1575381969_5de66bd121233.png!small)端口启动

![image.png](https://image.3001.net/images/20191203/1575382420_5de66d94148d3.png!small)设置代理

![image.png](https://image.3001.net/images/20191204/1575436879_5de7424f0083a.png!small)我设置了两个数据包显示页面，一个是显示全部数据包，一个是过滤重复数据包之后的页面

![image.png](https://image.3001.net/images/20191204/1575437035_5de742eb9c54e.png!small)

点击过滤数据包按钮，在过滤数据包一栏可以看到去重之后的数据包

![image.png](https://image.3001.net/images/20191204/1575437212_5de7439c8386e.png!small)

查看数据包选项可以查看完整的数据包

![image.png](https://image.3001.net/images/20191204/1575437311_5de743ff22b9c.png!small)

整个数据包处理的流程就到这里， **下面你就可以对这些数据包为所欲为** 。

来到被动注入位置

![image.png](https://image.3001.net/images/20191204/1575437483_5de744ab92f5e.png!small)sqlmap配置文件

    
    
    "SQLMAP": {
      "SQLMAP_LIMIT_RUN": 15,  "SQLMAP_DBMS": "",  "SQLMAP_REQUESTFILE_PATH": "/opt/taskid/",  "SQLMAP_VERBOSE": 1,  "SQLMAP_PROXY": "",  "SQLMAP_LEVEL": 5,  "SQLMAP_RISK": 3,  "SQLMAP_THREADS": 1,  "SQLMAP_PARMEXCLUDE": "Host,User-Agent,Accept-Language,Referer,Cookie",  "SQLMAP_PROXYFILE": "",  "SQLMAP_RETRIES": 5,  "SQLMAP_API_SERVER": [
        "http://127.0.0.1:55000",    "http://127.0.0.1:55001",    "http://127.0.0.1:55002",    "http://127.0.0.1:55003"  ]
    },
    

可以选择运行状态和漏洞状态

![image.png](https://image.3001.net/images/20191204/1575437691_5de7457bbf44c.png!small)启动api![image.png](https://image.3001.net/images/20191204/1575450477_5de7776d1b9be.png!small)

![image.png](https://image.3001.net/images/20191204/1575450457_5de777592ea24.png!small)我写了一个更新会话功能，主要面向于两种情况，一种是cookie失效，一种是token失效

![image.png](https://image.3001.net/images/20191204/1575450531_5de777a343a28.png!small)注入可以对过滤之后的数据包全部注入测试，也可以只跑没有测试的数据包，还可以选择域名进行测试注入![image.png](https://image.3001.net/images/20191204/1575450715_5de7785bcc83d.png!small)

刷新一下页面，就可以看到注入状态

![image.png](https://image.3001.net/images/20191204/1575450787_5de778a3e765a.png!small)查看实时日志，如果运行的时候，查看完整的日志是无法查看的

![image.png](https://image.3001.net/images/20191204/1575452467_5de77f333a486.png!small)![image.png](https://image.3001.net/images/20191204/1575452510_5de77f5e3e216.png!small)等到SQLMAP跑完之后，刷新页面就可以看到结果

![image.png](https://image.3001.net/images/20191204/1575466091_5de7b46b5a150.png!small)

ps：请大家关注我的[专栏](https://zhuanlan.freebuf.com/column/index/?name=%E5%B9%BB%E5%BD%B1%E5%AE%89%E5%85%A8)和star我的[项目](https://github.com/yingshang/banruo)，你的支持就是我的动力~~

