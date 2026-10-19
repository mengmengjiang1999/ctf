## **极光渗透岗面试真题** _interview question_

已知⽬标内⽹有Host若⼲(有且仅有⼀个公⽹IP)，当前只知道其域名ainfinity.space。（*要求：尽可能多的获取权限，测试过程请做好记录。）

 **以下为极光无限渗透测试团队给出的试题答案，四个步骤进行超全解析，手把手教你getshell。**

## 01 资产信息收集

基于已知域名进⾏信息收集，主要关注旁域名，⼦域名，IP，端⼝等资产信息， 以及开源信息。

相关过程属于基操，这⾥使⽤极光猎⼿进⾏信息收集：

域名

![v2-84afc85e5e031b74df63f4c2d664ee72_720w.jpg](https://image.3001.net/images/20210719/1626662406_60f4e606ac0a9c51cfc10.jpg!small)

端⼝服务

![v2-c24cb996dc5974a9a09736f160cd9e7f_720w.jpg](https://image.3001.net/images/20210719/1626662406_60f4e606e7aa80aaaab79.jpg!small)

泄漏信息

![v2-fe545c51f6114308272698f67508de7f_720w.jpg](https://image.3001.net/images/20210719/1626662407_60f4e60740ee97e4a63fb.jpg!small)

如上已探测出的3个端⼝中，尝试爆破8000端⼝的basic-auth和61616的SSH⽆果， 进⽽专注到8090的API服务。

## 02 打点攻击

针对[http://test2020.ainfinity.space:8090](https://link.zhihu.com/?target=http%3A//test2020.ainfinity.space%3A8090)进⾏渗透测试。

站点⽬录扫描，发现⼏个站点路径，其中存在swagger⽂档。

![v2-9acfaf8566643417dcd670108308fb67_720w.jpg](https://image.3001.net/images/20210719/1626662407_60f4e60781e33497ba107.jpg!small)

打开swagger⽂档，可以看到API的各功能点：

![v2-f4c950b9882184a254808eacfd281e21_720w.jpg](https://image.3001.net/images/20210719/1626662407_60f4e607d09d96e40501d.jpg!small)

参照⽂档说明，对各API功能进⾏测试。

有鉴于不能直接访问/log（提示Unauthorized），故⽽将关注点转移到/user功能上。

 **用户注册**

![v2-20ed0558fcb4022b84ed2e2e366bd798_720w.jpg](https://image.3001.net/images/20210719/1626662408_60f4e60819ce3f5b45a8f.jpg!small)

此处尝试进⾏SQL注⼊测试，未果。

 **用户登录**

![v2-4d2c70f4dbb204c3fdf7630a345b988d_720w.jpg](https://image.3001.net/images/20210719/1626662408_60f4e608595aa48b20cbb.jpg!small)

此处尝试进⾏SQL注⼊测试，亦未果。

登陆后访问各功能模块，发现⼀些值得关注的信息，如：log中包含⽤户密码； 返回数据疑似数据库表数据。

![v2-ed1ffc06879b8f2e186465048631004a_720w.jpg](https://image.3001.net/images/20210719/1626662408_60f4e608a769d320f2ac3.jpg!small)

尝试通过越权和SQL注⼊获取其他⽤户的⽇志失败，推测：后台对⽤户ID做了权限校验，普通⽤户只能获取本⽤户相关⽇志信息。暂时搁置该处。

 **尝试提取**

在修改密码的功能中，提交的字段为userpass，对⽐/user接⼝获取到信息，猜测开发⼈员有可能使⽤⾃动参数绑定，在输⼊中加⼊可能的参数：

![v2-07ab74b9a5fc48fe286a92ab1002a280_720w.jpg](https://image.3001.net/images/20210719/1626662408_60f4e608e7da0eda8f114.jpg!small)

再次查看当前⽤户信息，可观察到⽤户信息的字段被修改，⽤户的isadmin字段改成了true。

![v2-518afae91435cbe1ecd6d89ded35186d_720w.jpg](https://image.3001.net/images/20210719/1626662409_60f4e6093922bb58bfeca.jpg!small)

当前⽤户有了近⼀步的权限后，考虑个别API接⼝的后台逻辑可能与普通⽤户的不同。故重新将关注点转回到/log模块，经测试，发现存在SQL注⼊漏洞。

![v2-7eec9f50c10b2b2a9d41765be57ee221_720w.jpg](https://image.3001.net/images/20210719/1626662409_60f4e6096ba97d2bb9c43.jpg!small)

可以直接⽤Sqlmap跑：![v2-d158ccbae50cec511d123b46ddfb6010_720w.jpg](https://image.3001.net/images/20210719/1626662409_60f4e609a7216cd55d8ce.jpg!small)

得到账号密码对：biubiu / Ainfinity@2o20； user99 /
123987aa。尝试getshell⽆果后，考虑将现有成果应⽤到其他资产上。

## 03 成果拓展

尝试使⽤如上账号密码登录8000端⼝的basic-auth及61616的SSH服务。

经测试，biubiu / Ainfinity@2o20为8000端⼝basic-auth的有效凭证。

![v2-759cf954bebb2b9acf252ab2c59e0f1d_720w.jpg](https://image.3001.net/images/20210719/1626662409_60f4e609eb5683a761e2b.jpg!small)

输⼊凭证后，查看到的⻚⾯如下：

![v2-4ea9198e33fb97ec5d5f4514913ed570_720w.jpg](https://image.3001.net/images/20210719/1626662410_60f4e60a3bc66b4d1b58b.jpg!small)

 **路径探测**

    
    
    python3 dirsearch.py --auth-type=basic --auth="biubiu:Ainfinity@2o20" -u 
    http://test2020.ainfinity.space:8000/

![v2-e1f588fdfcaad10fe574124cc6822f81_720w.jpg](https://image.3001.net/images/20210719/1626662410_60f4e60a7835f62a178fc.jpg!small)

访问[http://test2020.ainfinity.space:8000/jk/](https://link.zhihu.com/?target=http%3A//test2020.ainfinity.space%3A8000/jk/)，发现这是⼀个docker监控(Glances)。

![v2-bdfbee5714769723e4da9cd3fc1b958f_720w.jpg](https://image.3001.net/images/20210719/1626662410_60f4e60ae8cf7b241395c.jpg!small)

其中，有若⼲容器，可以猜测这些就是题⽬中提到的“若⼲host”。glances暂⽆可利⽤的漏洞。

鉴于当前路径名称与容器名称⼀致，故尝试把另外⼏个容器名作为路径名。

发现新应⽤：

[http://test2020.ainfinity.space:8000/onlinevim/](https://link.zhihu.com/?target=http%3A//test2020.ainfinity.space%3A8000/onlinevim/)

![v2-219e2825cd3cf5c8073c692adff0933e_720w.jpg](https://image.3001.net/images/20210719/1626662411_60f4e60b4de869030140f.jpg!small)

vim约等于⼀个bash。输⼊:!bash即可开启⼀个交互式shell。

![v2-1d9e8fa00f448a15307172e799f5b303_720w.jpg](https://image.3001.net/images/20210719/1626662411_60f4e60b8e67b15f93cbe.jpg!small)

在该容器内进行信息枚举，除一个flag外未发现更多的有用信息。

## 04 内网拓展

下⼀步主要考虑对内⽹的扫描⼯作，⼀种⽅式是建⽴代理，通过代理扫描；另外⼀种是在⽬标内⽹的⼀台机器上直接扫描。鉴于效率考量，此处在内⽹机器上扫描，发现如下端⼝：

![v2-5f371b4c544e5f26c99360de69a1e53a_720w.jpg](https://image.3001.net/images/20210719/1626662411_60f4e60bd5f42514b18d5.jpg!small)

逐⼀访问扫描出来的端⼝，发现[http://172.19.217.11:8080](https://link.zhihu.com/?target=http%3A//172.19.217.11%3A8080)，能看到这是⼀个采⽤了shiro框架的应⽤：

![v2-4d8b5019ca676817dfda9f00355d3c0c_720w.jpg](https://image.3001.net/images/20210719/1626662412_60f4e60c3eb72c2313234.jpg!small)

为了便于测试，建⽴socks5代理，此处使⽤nps。

![v2-bd08a863ee899911617f227d85d19ed2_720w.jpg](https://image.3001.net/images/20210719/1626662412_60f4e60c8cd54554a1155.jpg!small)

socks5代理测试：

![v2-e1d07d36793a6cedd5df11a4734c1a5f_720w.jpg](https://image.3001.net/images/20210719/1626662412_60f4e60cc7b9271850cbe.jpg!small)

通过代理进⾏漏洞扫描：

![v2-d58ebd0250909c3791044e2e94b06264_720w.jpg](https://image.3001.net/images/20210719/1626662413_60f4e60d1517014b32f76.jpg!small)

漏洞利⽤：

![v2-4102f09167e872c8b956d26bd73589a2_720w.jpg](https://image.3001.net/images/20210719/1626662413_60f4e60d53fda6890666c.jpg!small)![v2-bee83437382d992072f226e797a3bb96_720w.jpg](https://image.3001.net/images/20210719/1626662413_60f4e60d96d1ccd13d880.jpg!small)

此外，也可以爆破tomcat manager账号密码：tomcat / tomcat，然后上传war包以getshell。

