## 信息搜集

某日接到项目上的渗透目标，先用subDomainsBrute进行一波域名搜集，好家伙41个子域名，结果看了老半天大多都禁止访问，没办法，只能考虑看有没有敏感信息泄露，想办法搞它。

![1646360561_622177f13798885b56205.png!small](https://image.3001.net/images/20220304/1646360561_622177f13798885b56205.png!small)

搞资产搜集，想到Freebuf开发的灯塔系统，在自己在服务器上直接搭建一套，把目标域名放进去扫了一圈，终于还是有所发现。这不是Springboot
Actuator的未授权访问漏洞么，之前某大佬直接用这个洞打穿了内网，看来有戏。

![1646360596_622178147a12287393cf4.png!small](https://image.3001.net/images/20220304/1646360596_622178147a12287393cf4.png!small)

GET第一个漏洞：路由地址及接口调用详情泄漏。

![1646360608_6221782053e276d3f897f.png!small](https://image.3001.net/images/20220304/1646360608_6221782053e276d3f897f.png!small)

![1646360615_6221782703b96bb17cd4e.png!small](https://image.3001.net/images/20220304/1646360615_6221782703b96bb17cd4e.png!small)

利用未授权的接口，通过构造参数获取了一些敏感未授权信息。

进行下一步操作，在ARL中还有env目录，访问 /env 接口时，spring actuator 会将一些带有敏感关键词(如
password、secret)的属性名对应的属性值用 * 号替换达到脱敏的效果，但是可以使*变成明文，先尝试看看redis的密码。

![1646360627_62217833d870dc786a60c.png!small](https://image.3001.net/images/20220304/1646360627_62217833d870dc786a60c.png!small)

通过访问目录/actuator/env接口可知，属于spring 2.x版本的，通过构造

spring 2.x的payload来尝试获取*的值。

返回了错误，难搞哦！

![1646360634_6221783a1dc35093fdccd.png!small](https://image.3001.net/images/20220304/1646360634_6221783a1dc35093fdccd.png!small)

最后尝试了几个接口都不太能搞定，只能再想其他方法了。

在ARL扫描结果中还有heapdump目录，GET请求目标的 /heapdump，下载了1.7G的文件。

使用 MAT 获得 jvm heap 中的密码明文。经过分析，终于在MemoryAnalyzer工具中找到了几个密码。

![1646360641_62217841a911d161d5a7c.png!small](https://image.3001.net/images/20220304/1646360641_62217841a911d161d5a7c.png!small)

通过env泄露的主机信息，在公网尝试连接数据库，不过还是失败了，工作到此，有数据库密码泄露的高危，基本就可以交差了，今天还是认真工作的一天！！！

个中不足之处，还请各位表哥赐教！

