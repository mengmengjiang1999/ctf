## **一、数据库审计的意义**

数据库审计是对数据库访问行为进行监管的系统，一般采用旁路部署的方式，通过镜像或探针的方式采集所有数据库的访问流量，并基于SQL语法、语义的解析技术，记录下数据库的所有访问和操作行为，例如访问数据的用户（IP、账号、时间），操作（增、删、改、查）、对象（表、字段）等。

数据库审计平台一般用来发现非法操作、数据泄露或篡改、及可疑入侵行为等，二是支持实时告警，及时发现可疑操作，及时处理和阻断可能发生的各类风险。

##  **二、数据库审计的方法**

数据库审计需要采集到数据库的流量才可以进行审计，如何才能收集数据库的流量呢。一般有几种方式：端口镜像（旁路模式）、探针(监听网卡）和应用插件(docker环境）。

> 端口镜像是指通过旁路部署的镜像方式获取数据库的所有访问流量，传统IT架构会使用这种方式。

> 探针是指在应用主机或数据库主机上，部署agent，监听网卡的数据库流量，然后将流量发给数据库审计的服务实现审计的目的，云端使用这种方式较多。

> 对于docker环境，在应用端部署时，一般使用插件方式，类似探针一样将获取的数据库请求，直接发给审计服务。

##  **二、数据库审计平台的搭建**

在这里我们使用开源的数据库审计平台来实现，下载审计服务：  
[https://github.com/jixindatech/sqlaudit
](https://github.com/jixindatech/sqlaudit)

如果需要agent，下载agent:

[https://github.com/jixindatech/sqlpacket
](https://github.com/jixindatech/sqlpacket)

也可以从gitee下载，分别是：

[https://gitee.com/chengfangang/sqlaudit
](https://gitee.com/chengfangang/sqlaudit)

https://gitee.com/chengfangang/sqlpacket

**使用前请详细阅读README中的说明。**

这里支持代码编译和docker方式，代码编译依赖go vue 还有一些依赖组件，这里直接用docker方式来演示，可以本地 docker build -t
sqlaudit . 编译镜像或 直接 docker pull chengfangang/sqlaudit 下载(40M左右)。

下面是直接docker pull 的镜像， 注意： 需要事先准备好配置文件， 放于对应的文件夹下，
同时审计存储用的是ES，需要提前启动ES服务，对应的settings文件是 etc/mapping.json，db
目录不用处理，程序自己生成，方便保存。运行之间，需要仔细阅读README.md中的如何修改配置文件选项。

    
    
    docker run -d  \
      --name sqlaudit \
        -p 9696:9696 \
        -p 9797:9797 \
        -p 9898:9898 \
        -v /docker/sqlaudit/etc:/opt/sqlaudit/etc \
        -v /docker/sqlaudit/db:/opt/sqlaudit/db \
        chengfangang/sqlaudit:1.0
    

docker logs -f sqlaudit 查看输出，是否存在错误

 **三、使用数据库审计平台**  
如果没有任何错误，就可以直接登陆了

1 访问http://ip:9797/ 页面，出现登陆页面，输入配置文件中的用户名和密码即可登陆。

2
进入系统之后![](https://image.3001.net/images/20210922/1632309160_614b0fa8e2c643be8a352.png!small)

3 有三个菜单项， 首个是Dashboard，
显示了最近一周的审计情况，可以根据时间查询相关的数据库情况，下面的图表信息会显示出对应时间段和相关数据库的统计信息，其中每条规则都会对应一种请求类型，允许、拒绝或者未知。
同时，下面有两个表，分别对应sql请求类型和规则类型。![](https://image.3001.net/images/20210922/1632309190_614b0fc6a7d373b4b2317.png!small)4
先打开第二项SQL配置， 点击 **新增** 按钮，即可加入新的审计规则，其中： 操作类型 分别对应相应的sql操作，UNKNOWN
为sql解析失败的情况， 在操作类型之下，可以对sql进行详细的匹配，字符串查找或正则方式，
优先级是按照从大到小进行匹配的，一旦匹配一条规则，剩余的规则均跳过，
同时可以选择该条规则是否告警，目前只支持邮件告警的方式，添加之后，即可显示所有规则。![](https://image.3001.net/images/20210922/1632309220_614b0fe4dd2155275b0b8.png!small)

5
第三项是SQL日志，可以根据相应的条件进行查询，可以对规则配置进行补充。![](https://image.3001.net/images/20210922/1632309242_614b0ffacd5f9b81823d5.png!small)

##  **四、使用帮助**

可以加入对应的QQ群获取更多帮助。

