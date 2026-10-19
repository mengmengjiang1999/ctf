## 一、引言

最近有一个工作任务，需要利用Suricata作为IDS来检测出口流量，同时利用ELK进行数据的展示。在搭建过程中，发现一篇文章《[使用Suricata和ELK进行流量检测](https://zhuanlan.zhihu.com/p/64742715)》[1]记录的比较好，但不是非常符合需求，一方面是本次部署任务需要利用Docker进行ELK的部署，另一方面是其数据展示并不是很丰富。在之前的文章中《[Cowrie蜜罐的Docker部署过程及Elasticsearch+Kibana可视化](articles/network/236525.html)》中就利用Docker搭建过elasticsearch
+ kibana来展示过自己的蜜罐数据。这里按照相同的策略，在利用Docker部署ELK进行展示。

## 二、部署架构

本次部署过程中，一开始准备在一台机器上部署所有的内容，也就是说，在suricata监听流量机器上直接部署ELK，但是为了以后能够更好的扩展，还是将两部分分开：在出口流量的镜像服务器上，只部署suricata进行流量监听，并生成日志，同时利用filebeat将数据传输至另一台机器的logstash；另外一台机器上利用docker部署ELK。具体的安排如下：

表2-1 服务器安排

机器| 部署内容 | IP  
---|---|---  
流量机器| suricata监听流量+filebeat传输数据| 10.0.0.1  
数据展示机器| docker部署ELK| 10.0.0.2  
  
## 三、环境准备

### 3.1 kibana的展示模板

![1599828780.png!small](https://image.3001.net/images/20200911/1599828780.png!small)

图3.1 sýnesis™ Lite for Suricata模板

本次部署过程中，直接使用了sýnesis™ Lite for
Suricata[2]的展示模板，这样就省去了再自己管理数据并设计的过程。在进行模板下载的过程中，使用1.1.0版本，具体版本请自行选择，注意要和ELK版本匹配。

![1599829026.png!small](https://image.3001.net/images/20200911/1599829026.png!small)

图3.2 版本信息

### 3.2 Docker镜像准备

在之前的机器上已经存在了ELK各个软件7.5.1的软件镜像，所以直接使用该版本。读者可以可以执行下列命令来获取镜像。

    
    
    docker pull logstash:7.5.1
    docker pull kibana:7.5.1
    docker pull elasticsearch:7.5.1

### 3.3 suricata的安装

在本文要部署的流量监听机器上很早之前就安装了suricata（版本5.0.0），这部分内容在文章[1]中已经介绍了很详细，读者可以参考其安装过程，这里不再赘述。

### 3.4 filebeat安装

filebeat需要安装在流量监听机器，该部分同样选择7.5.1版本，读者可以在[该地址](https://www.elastic.co/cn/downloads/past-releases#filebeat)下载，记得选择版本，下载后解压。

## 四、部署过程

### 4.1 logstash配置过程

为了更好说明这部分的部署过程，这里笔者直接创建新的文件夹suricata_elk进行部署。在部署之前，请将sýnesis™
Lite模板文件（下文简称为模板）下载，并解压。此时的文件组织结构如下：

![1599830787.png!small](https://image.3001.net/images/20200911/1599830787.png!small)

图4.1 初始环境文件组织结构

1）在当前文件路径下，创建logstash文件夹，

    
    
    mkdir logstash

2）获取模板中的logstash配置文件

在模板的logstash配置文件中，包含了具体进行数据解析的内容，但是分为三个文件配置的，这里直接合并为一个，执行以下命令。

    
    
    cd synesis_lite_suricata-1.1.0/logstash/synlite_suricata/
    cat 10_input_beats.logstash.conf > logstash.conf
    cat 20_filter_suricata.logstash.conf >> logstash.conf
    cat 30_output_elasticsearch.logstash.conf >> logstash.conf
    cp logstash.conf ../../../../logstash/

在其配置文件logstash.conf文件中，还有elasticsearch密码的设置，这里不准备使用密码，所以直接将logstash.conf中1160和1170行的内容删除即可。

3）配置ip等数据文件

回到上层目录suricata_elk目录下，复制相应的文件到logstash路径下。

    
    
    cp synesis_lite_suricata-1.1.0/logstash/synlite_suricata/dictionaries/ logstash/ -r
    cp synesis_lite_suricata-1.1.0/logstash/synlite_suricata/geoipdbs/ logstash/ -r 
    cp synesis_lite_suricata-1.1.0/logstash/synlite_suricata/templates/ logstash/ -r  

### 4.2 配置elasticsearch

该部分不需要进行具体的配置，主要是为了能够将数据保存到宿主机上，创建一个文件夹来保存数据，为了方便直接赋予该文件夹全权限。

    
    
    mkdir elasticsearch/data -p  
    chmod 777 elasticsearch/data

### 4.3 编写docker-compose文件

    
    
    # yaml settings
    version: '3'
    services:
        elasticsearch:
            container_name: elasticsearch_for_suricata
            image: elasticsearch:7.5.1
            restart: "always"
            volumes:
                - "./elasticsearch/data:/usr/share/elasticsearch/data"
            environment:
                "discovery.type": "single-node"
        kibana:
            container_name: kibana_for_suricata
            image: kibana:7.5.1
            ports:
                - "5601:5601"
            restart: "always"
            depends_on:
                - elasticsearch
        logstash:
            container_name: logstash_for_suricata
            image: logstash:7.5.1
            ports:
                - "5044:5044"
            restart: "always"
            volumes: 
                - "./logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf"
                - "./logstash/dictionaries/:/usr/share/logstash/synlite_suricata/dictionaries"
                - "./logstash/geoipdbs/:/usr/share/logstash/synlite_suricata/geoipdbs"
                - "./logstash/templates/:/usr/share/logstash/synlite_suricata/templates"
            depends_on:
                - elasticsearch
            environment:  
    #注意这里的内存配置是模板[1]中所要求，笔者部署过程中发现较小内存无法启动
                LS_JAVA_OPTS: "-Xms4g -Xmx4g"
                SYNLITE_SURICATA_BEATS_HOST: "0.0.0.0"
                SYNLITE_SURICATA_BEATS_PORT: 5044
                SYNLITE_SURICATA_ES_HOST: "elasticsearch:9200"
                SYNLITE_SURICATA_GEOIP_DB_PATH: "/usr/share/logstash/synlite_suricata/geoipdbs"
                SYNLITE_SURICATA_DICT_PATH: "/usr/share/logstash/synlite_suricata/dictionaries"
                SYNLITE_SURICATA_TEMPLATE_PATH: "/usr/share/logstash/synlite_suricata/templates"

其中logstash服务暴露5044端口来接收数据，kibana暴露5601端口来进行数据展示；如果读者是直接复制该部分命令，请注意格式，上述代码可能因为freebuf的显示问题出现了换行。

此时在初始目录下执行命令docker-compose up
-d，然后访问http://your_machine_ip:5601，就可以看到Kinaba界面。

此时在数据展示机器上的ELK就算部署完成了，此时的文件夹结构如下：

![1599832647.png!small](https://image.3001.net/images/20200911/1599832647.png!small)

图4.2 完整的文件夹结构

### 4.4 filebeat传输数据

在流量监听机器上，读者应该已经安装好了suricata，并能成功运行。此时需要在该机器上使用filebeat将数据传输至logstash服务。配置文件如下：

    
    
    filebeat.inputs:
    - type: log
      enabled: true
      paths:
        - ./log/eve.json
      fields:
        event.type: suricata
    output.logstash:
      hosts: ["10.0.0.2:5044"]

请修改上述配置文件中的eve.log位置及logstash的IP，在解压后的filebeat路径下执行以下命令，即可将数据传递到logstash。

    
    
    ./filebeat -c ./filebeat.yml

### 4.5 kibana添加索引

如果前面都部署没有问题，此时点击kibana界面左侧菜单栏第一个discover可以看到下列画面。

![1599878905.png!small](https://image.3001.net/images/20200912/1599878905.png!small)

图4-3 等待数据

此时还没有数据过来，稍等片刻即可，可持续点击check for new data查看，如果有数据到来之后，出现以下画面。

![1599879064.png!small](https://image.3001.net/images/20200912/1599879064.png!small)

图4-4 定义索引

在index pattern 输入框中输入suricata* 并点击next step，并选择时间戳后，创建索引模式。

![1599879120.png!small](https://image.3001.net/images/20200912/1599879120.png!small)

图4-5 选择时间戳

此时再次点击discover，可发现已有数据。

![1599879194.png!small](https://image.3001.net/images/20200912/1599879194.png!small)

图4-6 查看数据

### 4.6 kibana添加模板文件

但此时，还无法利用模板进行展示，需要将模板文件添加到kibna中，步骤如下。

1）在模板文件的kibana的子目录中含有相应的模板文件，请下载至本机。

![1599879388.png!small](https://image.3001.net/images/20200912/1599879388.png!small)

图4-7 下载模板文件

2）在kibana左侧菜单栏选择最后一个management，然后点击saved objects。

![1599879582.png!small](https://image.3001.net/images/20200912/1599879582.png!small)

图4-8 导入文件

3）导入文件

选择文件或者直接拖拽进入。

![1599879668.png!small](https://image.3001.net/images/20200912/1599879668.png!small)

图4-9 导入文件

点击右下角导入即可。

## 五、查看数据

点击Kibana左侧第三个dashboard按钮，然后随便选择一个即可，例如点击警报部分。

![1599880117.png!small](https://image.3001.net/images/20200912/1599880117.png!small)

图5-1 警报部分展示

如果读者是新部署的机器，可能并没有配置警报文件，所以数字显示为0，可以在suricata开启ET/open的规则。查看流量监听机器是否安装了suricata-update，如果没有，可以参照文章《[Suricata规则介绍、以及使用suricata-update做规则管理](https://zhuanlan.zhihu.com/p/36340468)》[3]进行安装并下载相应规则。然后重启suricata即可。

kibana的dashboard中，还有很多其他的功能，例如地图，选择Flows，在右侧选择GeoIP可以查看，其他功能请读者自行探索。

## 六、小节

本文主要介绍了利用ELK来展示suricata的信息，算是给出了一种简单的数据展示方案。但也存在很多问题。

1）在图5-1中可以看到非常多的报警信息，但实际上在我的网络环境下，真正有意义的并不多，所以需要读者根据自己的环境来进行规则的优化

2）synesis模板只是给出了一种基础类型的模板，很多功能还很欠缺，而且不够灵活

注：本文只是在一个小型的网络下进行测试，提供了一种简单的数据可视化方案，请读者自己在部署时考虑自己的实际情况。

## 参考

> [1][使用Suricata和ELK进行流量检测](https://zhuanlan.zhihu.com/p/64742715)
>
> [2][sýnesis™ Lite for
> Suricata](https://github.com/robcowart/synesis_lite_suricata/tree/v1.1.0)
>
> [3][Suricata规则介绍、以及使用suricata-> update做规则管理](https://zhuanlan.zhihu.com/p/36340468)

