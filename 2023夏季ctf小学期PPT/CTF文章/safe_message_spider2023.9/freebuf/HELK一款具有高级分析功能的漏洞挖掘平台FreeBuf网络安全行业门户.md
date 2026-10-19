**今天给大家介绍的是一款名叫HELK的工具，它是一款具有高级分析能力的Hunting ELK（Elasticsearch, Logstash,
Kibana）。**

![1.png](https://image.3001.net/images/20180224/15194540901656.png!small)

## 目标

> 1\. 给安全社区提供一个免费的漏洞Hunting平台，并共享一些基本的安全威胁以及漏洞挖掘信息；
>
> 2\. 帮助社区了解大量事件日志，并在漏洞Hunting的过程中给可疑事件添加更多的上下文信息；
>
> 3\. 缩短部署ELK栈的时间；
>
> 4\. 帮助社区以更加简单更加经济的方式改进漏洞挖掘测试用例；
>
> 5\. 通过Apache Spark、GraphFrames & JupyterNotebooks启用数据科学分析；

## 工具当前状态：Alpha

本项目目前仍处于Alpha测试阶段，因此项目代码和工具的功能会随时发生变化。我们现在还没有用大量数据源来对本系统进行测试，而且测试场景也不够丰富，因此我们希望社区人员可以帮助我们对HELK进行测试，并积极给我们提供反馈信息。

## HELK介绍

HELK是一种拥有高级漏洞挖掘分析能力的ELK（Elasticsearch, Logstash & Kibana），该工具基于Spark&
Graphframes技术实现，而且HELK也是第一个将数据科学功能应用到ELK栈上的免费工具。除此之外，它还整合了Jupyter
Notebook以帮助社区对大数据和机器学习用例进行建模（使用PySpark
API）。更加重要的是，它提供了一套完整的搜索引擎，并搭配了非常好的可视化效果、图形化的关系查询功能以及高级分析功能。

### [Kafka](https://kafka.apache.org/)

Kafka是一个分布式的订阅消息发布系统，用于构建实时数据管道和流式应用。它具有横向伸缩性、容错性高和速度快等特性，目前有数千家公司会在生产工作中使用它。

###
[Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started.html)

Elasticsearch是一个高度可扩展的开源全文搜索/分析引擎。它允许我们快速、实时地存储、搜索和分析大量数据。它通常会被用作底层引擎/技术，并驱动具有复杂搜索特性和需求的应用程序。

###
[Logstash](https://www.elastic.co/guide/en/logstash/current/introduction.html)

Logstash是一款拥有实时数据传输能力的开源数据收集引擎，Logstash可以动态地从不同数据来源和数据规范中收集信息，并将其发送到用户所指定的地方。除此之外，它还可以进行数据清洗和各种先进的数据分析以及数据可视化。

### [Kibana](https://www.elastic.co/guide/en/kibana/current/introduction.html)

Kibana是一款专门搭配Elasticsearch的开源数据分析和可视化平台，你可以使用Kibana搜索、查看并与存储在Elasticsearch中的数据进行交互。你可以轻松地执行各种高级数据分析任务，并在各种图表、表单和数据映射中可视化你的数据。

## 工具安装

### 安装要求

> 1\. OS名称：具体取决于你选择安装HELK的操作系统；
>
> 2\.
> Docker（可选项1-2）：支持特定的Linux发行版以及macOS：HELK使用了Docker的官方社区版（CE）和bash脚本（Edge版本）来安装Docker，DockerCE
> Edge脚本支持下列Linux发行版：ubuntu,debian, raspbian, centos和fedora；
>
> 3\. Bash脚本（可选项3）：Debian系统；
>
> 4\. 网络连接：NAT或桥接；
>
> 5\. RAM：至少12GB；
>
> 6\.
> 应用程序：Docker、Winlogbeat、[Kafka输出插件](https://www.elastic.co/guide/en/beats/winlogbeat/current/kafka-> output.html)；

### HELK下载

运行下列，通过git克隆HELK项目代码库：

    
    
    git clone https://github.com/Cyb3rWard0g/HELK.git

切换到HELK目录，以root权限运行helk_install.sh脚本：

    
    
    cd HELK/
    sudo ./helk_install.sh  
    

### HELK菜单

为了帮助用户简单快速地安装HELK，本项目提供了一个功能菜单来帮助用户选择如何安装HELK。大家可以根据自己的需要来选择相应的安装方式，还要设置HELK所使用的主机IP地址（如果有需要的话）。设置完成之后，按下【回车键】并等待脚本运行完成（30秒左右）。

![2.png](https://image.3001.net/images/20180224/15194541797289.png!small)

### 访问HELK的Web接口

等待安装完成之后，你可以打开浏览器，然后输入刚才你所设置的HELK的IP地址，然后输出HELK凭证（helk:hunting）。默认情况下，你将进入到Kibana的主页面。接下来，你就可以使用Kibana所提供的各种功能了：

![3.png](https://image.3001.net/images/20180224/15194542088989.png!small)

![4.png](https://image.3001.net/images/20180224/15194542172480.png!small)

![5.png](https://image.3001.net/images/20180224/1519454225450.png!small)

### （Docker）访问HELK容器

默认配置下，HELK的容器会在后台运行。因此，你需要通过运行下列命令来访问你的Docker容器：

    
    
    sudo docker exec -ti helk bash
    root@7a9d6443a4bf:/opt/helk/scripts#  
    

## 参考资料

1\. <https://cyberwardog.blogspot.com/2017/02/setting-up-pentesting-i-mean-threat_98.html>

2\. <https://cs.stanford.edu/~matei/papers/2016/grades_graphframes.pdf>

3\. <https://www.slideshare.net/SparkSummit/graphframes-graph-queries-in-spark-sql>

4\. <http://graphframes.github.io/index.html>

5\. <https://www.elastic.co/products>

6\.
<https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html>

7\. <https://github.com/spujadas/elk-docker>

8\. <https://github.com/deviantony/docker-elk>

***
参考来源：[HELK](https://github.com/Cyb3rWard0g/HELK)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

