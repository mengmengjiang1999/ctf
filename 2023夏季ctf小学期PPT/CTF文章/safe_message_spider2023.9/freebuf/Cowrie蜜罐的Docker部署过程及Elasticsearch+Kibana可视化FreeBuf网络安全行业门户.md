##  引言

**蜜罐是一种刻意让攻击者进入的设备，目前有很多应用场景，比如可以为威胁情报的信息采集提供信息。蜜罐根据交互等级可以分为低交互、中交互、高交互，同时现在已经有开源的蜜罐设备。本文主要研究SSH/Telnet蜜罐Cowrie的搭建及数据可视化。在Freebuf中，有很多文章介绍了这个款蜜罐，同时介绍了相关的部署教程，本文将讲解如何利用docker来部署蜜罐，同时部署elasticsearch和kibana进行数据存储和可视化。利用docker进行部署，可以极大的提高部署效率，不用再搭建复杂的环境。**

##  Cowrie蜜罐简介

根据Cowrie蜜罐文章[1]的介绍，Cowrie是一个中交互的蜜罐，同时可以充当真实机器代理，成为高交互蜜罐。Cowrie提供的服务包括两种，SSH和Telnet。该蜜罐可以记录用户名、密码、操作流程，以及攻击者下载的脚本。Cowrie可以支持多种输出方式，其可以直接输出到elsticsearch，不需要logstash或其他组件帮助。

##  部署方式及环境配置

本文主要介绍一种单机部署的简单方案，实际生产环境中，请考虑自己的需求进行分析。本文的部署方式主要组件分为四部分：1）蜜罐（cowrie）2）elasticsearch
3）kibana
4）nginx。四个组件均使用docker进行启动，同时部署于同一台机器。其中nginx的使用是因为kibana默认没有认证，ELK组件中可以使用x-pack，这里使用nginx作为代替，实现一种简单的用户名密码认证。各组件具体信息如下。

配置  |  
---|---  
阿里云主机  |  配置1核2G内存，带宽1M  
docker  |  19.03.8  
docker-compose  |  version 1.25.4, build 8d51620a  
镜像 cowrie/cowrie  |  latest（dockerhub上只有一个版本，5.12日查看）  
镜像 elasticsearch  |  7.5.2  
kibana  |  7.5.2  
nginx  |  latest  
  
为了保证能够正常运行，例如阿里云默认不开放一些端口，请检查你的配置，开放8001端口（nginx服务）、2222（cowrie
ssh端口）、23（cowrie telnet端口）。

##  安装方式

本文介绍两种安装方式，一种是通过逐步输入命令启动四个组件，一种是利用docker-compose一键启动四个组件。

###  **配置文件设置**

下面先介绍配置文件内容的设置，这部分之后再分别介绍两种启动方案。为了能够保证数据持久化，同时进行相关的参数传递。本文工作路径设置为/opt/docker_ek_cowrie，如果选择了其他路径，请在相关位置进行修改。进入工作路径。

    
    
    mkdir cowrie/downloads -p
    mkdir cowrie/etc -p
    mkdir ek/elasticsearch/data -p
    mkdir nginx/conf -p

cowrie配置内容cowrie中存在可以配置的模板，模板可以通过两种功能获取，一种是通过github下载源码；另一种是从docker镜像中复制出来，配置文件模板位于cowire下的etc文件夹。复制文件cowrie.cfg.dist和userdb.example到刚刚生成的cowrie/etc路径下。userdb.example中包含登录进入SSH/Telnet蜜罐可以使用的用户名/密码对，有需要到的，可以修改。cowrie.cfg.dist是配置文件的模板，如果要进行修改的话，先执行复制命令cp
cowrie.cfg.dist
cowrie.cfg，然后按照需求修改cowire.cfg文件。修改的内容主要包含两个个部分：启动telnet服务，修改elasticsearch输出。1）启动telnet服务

    
    
    [telnet]
    #Enable Telnet support, disabled by default
    enabled = true

位于文件653行处，修改enabled = true2）修改elasticsearch输出

    
    
    [output_elasticsearch]
    enabled = true
    host = elasticsearch
    port = 9200
    index = cowrie
    # type has been deprecated since ES 6.0.0
    # use _doc which is the default type. See
    # https://stackoverflow.com/a/53688626 for
    # more information
    type = _doc
    # set pipeline = geoip to map src_ip to
    # geo location data. You can use a custom
    # pipeline but you must ensure it exists
    # in elasticsearch.
    pipeline = geoip

文件717行处，将内容修改为上述内容，其中host部分是docker启动elasticsearch时设置容器的名字。

配置nginx配置nginx需要两个部分，一个是进行转发的配置文件，一个是认证的密码文件。转发配置文件。

首先是，nginx的转发配置文件，请编辑nginx/conf/nginx.conf文件，内容如下。

    
    
    http{   
        server {
            listen       8001; #监听端口
            location / {                                                                                                                                                          auth_basic "Please input password"; 
                auth_basic_user_file /etc/nginx/passwd.db; #配置密码文件
                proxy_set_header  Host  $http_host;
                proxy_set_header  X-Real-IP  $remote_addr;
                proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_pass   http://kibana:5601;  #以kibana名字作为域名
            }   
    
            error_page   500 502 503 504  /50x.html;
            location = /50x.html {
                root   /usr/share/nginx/html;
            }   
        }   
    }
    events {
          worker_connections  1024;  ## Default: 1024
    }

主要设置监听端口、代理的具体地址、还有认证的密码文件。

通常生成密码文件都是使用htpasswd工具，这里直接使用在线工具[2]进行操作，然后将生成的用户名/密码写入文件nginx/conf/passwd.db。

![](https://image.3001.net/images/20200512/1589284128_5eba8d203f08e.png!small)

为了保证容器能够在文件路径中具备读写权限，执行以下命令。

    
    
     chmod 777 ek/elasticsearch/data/
     chmod 777 cowrie/downloads/

此时工作路径文件树如下图，自此所有的配置文件都已经配置完成。

![](https://image.3001.net/images/20200512/1589284158_5eba8d3ec0626.png!small)

###  **第一种方式：手动命令启动组件**

docker启动elasticsearch

    
    
    docker run -d \
    --name elasticsearch \
    -v /opt/docker_ek_cowrie/ek/elasticsearch/data:/usr/share/elasticsearch/data \
    -e "ES_JAVA_OPTS=-Xms256m -Xmx256m" \
    -e "discovery.type=single-node" elasticsearch:7.5.2

docker启动kibana

    
    
    docker run -d --name kibana --link elasticsearch kibana:7.5.2 docker启动nginx

docekr启动nginx

    
    
    docker run -d -p 8001:8001 --link kibana \
    -v /opt/docker_ek_cowrie/nginx/conf/nginx.conf:/etc/nginx/nginx.conf \
    -v /opt/docker_ek_cowrie/nginx/conf/passwd.db:/etc/nginx/passwd.db \
    nginx

docker启动cowrie

    
    
    docker run -d -p 23:2223 -p 2222:2222 --link elasticsearch \
    -v /opt/docker_ek_cowrie/cowrie/etc:/cowrie/cowrie-git/etc \
    -v /opt/docker_ek_cowrie/cowrie/downloads:/cowrie/cowrie-git/var/lib/cowrie/downloads \ cowrie/cowrie

上述命令中，将配置文件和蜜罐下载的文件分别映射，端口开放2222(SSH)和23(Telnet)。

###  **第二种方式：docker-compose部署方式**

直接使用docker-compose进行部署，请在工作路径下编辑`docker-compose.yml`文件。

    
    
    #yaml setting                                                                                                                                             
    version: '3' 
    services:
        elasticsearch:
            container_name: elasticsearch
            image: elasticsearch:7.5.2
        
            volumes:
            - "/opt/docker_ek_cowrie/ek/elasticsearch/data:/usr/share/elasticsearch/data"
            environment: 
                ES_JAVA_OPTS: "-Xms256m -Xmx256m"
                discovery.type: "single-node"
        kibana:
            container_name: kibana
            image: kibana:7.5.2
        nginx:
            container_name: nginx
            image: nginx:latest
            ports:
            - "8001:8001"
            volumes:
            - "/opt/docker_ek_cowrie/nginx/conf/nginx.conf:/etc/nginx/nginx.conf"
            - "/opt/docker_ek_cowrie/nginx/conf/passwd.db:/etc/nginx/passwd.db"
        cowrie:
            container_name: cowrie
            image: cowrie/cowrie:latest
            ports:
            - "2222:2222"
            - "23:2223"
            volumes:
            - "/opt/docker_ek_cowrie/cowrie/etc:/cowrie/cowrie-git/etc"
            - "/opt/docker_ek_cowrie/cowrie/downloads:/cowrie/cowrie-git/var/lib/cowrie/downloads"

然后在工作路径执行`docker-compose up`或`docker-compose up -d`后台运行。  
上述两种部署方式，最后都能使这些组件成功运行。

自此，四个组件就已经启动了，打开h\t\t\p://your_ip:8001，输入用户名密码进行登录。首次登录的时候，可能会报错“Sorry, the
page you are looking for is currently unavailable.Please try again later."

请稍等kibana进行初始化，首次登录时时间会比较久，一方面是进行一些配置，另一方面是要下载一些js文件。如果长时间进不去或其他报错信息。

###  **配置elasticsearch及kibana**

但elasticsearch中还没有数据，需要elasticsearch和kibana进一步的配置。进入左侧开发者工具处，在命令行中输入以下命令，并执行，此时可以接收到数据。

    
    
    #在elasticsearch中生成索引
    PUT cowrie 
    #设置数据类型
    PUT cowrie/_mapping 
    {
      "properties": {
        "geo": {"properties": 
              {"location": {"type": "geo_point"}}}
      }
    }
    #设置管道工具
    PUT _ingest/pipeline/geoip
    {
      "description" : "Add geoip info",
      "processors" : [
        {
          "geoip" : {
            "field" : "src_ip",
            "target_field":"geo",
            "database_file": "GeoLite2-City.mmdb",
                    "properties":["IP", "COUNTRY_ISO_CODE", "COUNTRY_NAME", "CONTINENT_NAME", "REGION_ISO_CODE", "REGION_NAME", "CITY_NAME", "TIMEZONE", "LOCATION"]
          }
        }
      ]
    }

正常情况下，这部分工作cowrie在首次执行输出的时候，会进行创建，可以参见源码部分，但不知为什么没有创建成功，所以这里手动创建。上述步骤完成后，还需要创建index
pattern

![](https://image.3001.net/images/20200512/1589287545_5eba9a79842f8.png!small)

在index-name中填写cowrie，选择时间戳，然后即可得到index pattern。

###  **查看日志**

点击discover。可以通过telnet命令来测试是否能够接收到数据，telnet 0 23

可以查看到本机的日志。kibana会显示最原始的日志，可以查看其具体的json格式；为了更具体的显示信息，可以根据条件进行过滤，并按照需求显示某些字段。

![1589287862_5eba9bb661c31.png](https://image.3001.net/images/20200515/15895438827091.png!small)

这里，我主要显示了ip、国家、城市、用户名、密码信息。同时在运行一段时间后，会发现上传的文件，如果要查看具体文件的信息，可以在之前docker启动过程中挂载downloads文件进行查看。

![1589287947_5eba9c0b6bc3b.png](https://image.3001.net/images/20200515/15895439049073.png!small)

为了方便进行更具体地数据分析，可以制作简单的dashborad，分别是IP数，地域分布，用户名/密码词云。读者可以根据自己的需求进行设计。

![1589288119_5eba9cb7f40db.png](https://image.3001.net/images/20200515/1589543923900.png!small)

这这篇文章编写之前，本人在阿里云的蜜罐收到了大量的爆破及扫描信息，还有多种僵尸网络的样本，这里为了演示整体的搭建过程，没有展示那部分数据。

为了方便各位读者直接使用docker-compose进行镜像制作，docker-compose.yml文件及dashboard中的一些信息已上传至[github](https://github.com/CymaticsCC/ek_cowrie)，只需要配置nginx的密码，同时更换docker-compose.yml中的路径来符合你的工作路径，就可以生成相应的服务。

##  总结

本文讲解了如果使用docker部署cowrie，同时使用elasticsearch及kibana进行数据的可视化，介绍了两种方案来搭建各个组件，读者可以根据自己的方便选用两种方式。最后，简单见识了蜜罐运行过程中采集到的数据。

###  参考链接

> [1][cowrie文档](https://cowrie.readthedocs.io/en/latest/index.html)
>
> [2][在线 htpasswd 生成器](https://tool.oschina.net/htpasswd)

 ***本文作者： FreeAChao，转载请注明来自FreeBuf.COM**  
  

