~~# centos7安装ELK 8.7 并配置密码

## 一、简介

### 1\. 需求介绍

最近在做一个实时网络流量分析的项目，需要把解析之后的流量数据入库到 ES 中。

ELK是一个免费开源的日志分析架构技术栈总称，官网 https://www.elastic.co/cn。  
包含三大基础组件，分别是Elasticsearch、Logstash、Kibana。

最新的 ELK 8.7，安装之后默认启用加密和认证。在此记录配置ELK的搭建过程。

### 2\. 安装环境

    
    
    系统环境：centos7.8
    依赖文件：
        elasticsearch-8.7.0-x86_64.rpm
        elasticsearch-analysis-ik-8.7.0.zip
        kibana-8.7.0-x86_64.rpm
        logstash-8.7.0-x86_64.rpm
    

### 3\. 设置防火墙

可以选择禁用防火墙或者放行端口。

禁用防火墙

    
    
    systemctl stop firewalld
    systemctl disable firewalld
    

或启用放行端口

    
    
    firewall-cmd --permanent --add-port={9200/tcp,9300/tcp,5601/tcp} 
    firewall-cmd --reload
    

## 一、安装elasticsearch

### 1\. 安装elasticsearch

在线下载 elasticsearch 最新安装包，官网： <https://www.elastic.co/cn/downloads/past-releases#elasticsearch>

elasticsearch 8.7 默认启动密码登录和 https 通信连接，我们为了方便后面的 logstash、kibana
的调用，我们仅设置登录密码，而不使用https。

    
    
    rpm -ivh elasticsearch-8.7.0-x86_64.rpm
    systemctl start elasticsearch
    

查看端口和进程确定是否启动成功

    
    
    ps -ef | grep elasticsearch
    netstat -tulnp | grep 9200
    curl https://localhost:9200 --insecure
    systemctl status elasticsearch
    

### 2\. 设置登录密码

确认启动成功之后，设置密码，可以三个账号设置相同的密码，如果启动失败则会导致修改密码提示无法连接集群。修改密码的操作在任意时候都可以完成，如果此时修改不成功，
可以先放着以后再修改。

    
    
    /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -i
    使用密码：elastic_023
    /usr/share/elasticsearch/bin/elasticsearch-reset-password -u kibana_system -i
    使用密码：elastic_023
    /usr/share/elasticsearch/bin/elasticsearch-reset-password -u logstash_system -i
    使用密码：elastic_023
    
    #/usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
    #/usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s node
    

浏览器打开访问kibama，看是否可以成功打开页面，输入密码查看是否可以成功登录。

### 3\. 安装分词插件

    
    
    mkdir -p /usr/share/elasticsearch/plugins/analysis-ik/
    wget https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.7.0/elasticsearch-analysis-ik-8.7.0.zip
    cp elasticsearch-analysis-ik-8.7.0.zip /usr/share/elasticsearch/plugins/analysis-ik/
    cd /usr/share/elasticsearch/plugins/analysis-ik/
    unzip elasticsearch-analysis-ik-8.7.0.zip
    rm -rf /usr/share/elasticsearch/plugins/analysis-ik/elasticsearch-analysis-ik-8.7.0.zip
    

### 4.修改安装目录

    
    
    # 修改存储目录
    mkdir /mnt/data -p
    chmod 777 /mnt/data/
    
    systemctl stop elasticsearch
    # 
    mkdir /mnt/data/elasticsearch/lib/elasticsearch -p
    mkdir /mnt/data/elasticsearch/log/elasticsearch -p
    chown elasticsearch:elasticsearch /mnt/data/elasticsearch/ -R
    chown elasticsearch:elasticsearch /mnt/data/elasticsearch/ -R
    /bin/cp /var/lib/elasticsearch /mnt/data/elasticsearch/lib/ -rf
    /bin/cp /var/log/elasticsearch /mnt/data/elasticsearch/log/ -rf
    chmod 777 /mnt/ -R
    chown elasticsearch:elasticsearch /mnt/data/elasticsearch/ -R
    chown elasticsearch:elasticsearch /mnt/data/elasticsearch/ -R
    
    vim /etc/elasticsearch/elasticsearch.yml
        path.data: /mnt/data/elasticsearch/lib/elasticsearch
        path.logs: /mnt/data/elasticsearch/log/elasticsearch
    

### 5\. 配置证书（含默认配置）

elasticsearch 8 版本，自带证书支持和https，无需自定义配置

修改配置文件`/etc/elasticsearch/elasticsearch.yml`

    
    
    vim /etc/elasticsearch/elasticsearch.yml
    
    cluster.name: pcapAnalyse
    network.host: 0.0.0.0
    http.port: 9200
    
    # Enable security features
    xpack.security.enabled: true
    
    xpack.security.enrollment.enabled: true
    
    # Enable encryption for HTTP API client connections, such as Kibana, Logstash, and Agents
    xpack.security.http.ssl:
      enabled: true
      keystore.path: certs/http.p12
    
    # Enable encryption and mutual authentication between cluster nodes
    xpack.security.transport.ssl:
      enabled: true
      verification_mode: certificate
      keystore.path: certs/transport.p12
      truststore.path: certs/transport.p12
    # Create a new cluster with the current node only
    # Additional nodes can still join the cluster later
    cluster.initial_master_nodes: ["master"]
    
    
    cluster.initial_master_nodes: ["pcapAnalyse_master"]
    http.host: 0.0.0.0
    

重启服务

    
    
    systemctl daemon-reload
    systemctl restart elasticsearch
    systemctl enable elasticsearch
    
    ps -ef | grep elasticsearch
    netstat -tulnp | grep 9200
    curl https://localhost:9200 --insecure
    
    systemctl status elasticsearch
    

### 6\. 性能配置

修改系统配置，可以脚本直接复制粘贴执行，更细节不作展示。

    
    
    echo "*  soft nproc  65535" >> /etc/security/limits.conf
    echo "*  hard nproc  65535" >> /etc/security/limits.conf
    echo "*  soft nofile 65536" >> /etc/security/limits.conf
    echo "*  hard nofile 65536" >> /etc/security/limits.conf
    ulimit -Hn
    ulimit -Sn
    echo "vm.max_map_count = 262144" >> /etc/sysctl.conf
    sysctl -p
    

要修改 elasticsearch 的运行内存情况，需要修改`/etc/elasticsearch/jvm.options`

主要是用于记录，es默认的内存配置是1g，在实际的应用过程中很快就占满了。可以修改配置文件增加内存。

[Elasticsearch7.8.0
配置运行内存：https://www.jianshu.com/p/3393ef48c1f2](https://www.jianshu.com/p/3393ef48c1f2)

[Elasticsearch内存分配设置详解
：http://www.openskill.cn/article/304](http://www.openskill.cn/article/304)

### 5\. 其他资料

[最新Elasticsearch8.4.3 +
Kibana8.4.3在云服务器Centos7.9安装部署（参考官方文档）:https://blog.csdn.net/u014282578/article/details/127633399](https://blog.csdn.net/u014282578/article/details/127633399)

## 二、安装kibana

### 1\. 安装kibana

在线下载 kibana最新安装包，官网： <https://www.elastic.co/cn/downloads/past-releases#elasticsearch>

    
    
    rpm -ivh kibana-8.7.0-x86_64.rpm
    
    systemctl daemon-reload
    systemctl restart kibana
    systemctl enable kibana
    
    # 等待一分钟左右
    ps -ef | grep kibana
    netstat -tulnp | grep 5601
    curl localhost:5601 -L
    systemctl status kibana
    

浏览器打开访问kibama，看是否可以成功打开页面

    
    
    http://127.0.0.1:5601
    

### 2.配置 kibana 的 https 证书

  1. 配置 kibana 连接 elasticsearch的https的通信证书

    
    
    mkdir /etc/kibana/certs
    /bin/cp /etc/elasticsearch/certs /etc/kibana/certs -rf
    chown kibana:kibana /etc/kibana/certs/ -R
    
    # 里面的 http_ca.crt 文件就是 kibana 连接 elasticsearch的https的通信证书
    

  2. 配置浏览器访问 kibana 的 https 的证书

    
    
    # kibana证书，浏览器到kibana的https
    /usr/share/elasticsearch/bin/elasticsearch-certutil csr -name kibana-server -dns master,localhost << EOF
    /etc/kibana/certs/csr-bundle.zip
    EOF
    
    cd /etc/kibana/certs/
    unzip csr-bundle.zip
    mv kibana-server/kibana-server.key kibana-server/kibana-server.csr ./
    yum install openssl -y
    openssl x509 -req -in kibana-server.csr -signkey kibana-server.key -out kibana-server.crt
    
    # 最后生成的 kibana-server.crt 文件就是 kibana https 访问的证书
    
    
    [root@master certs]# ll
    total 36
    -rw-r----- 1 kibana kibana  1915 May 31 11:21 http_ca.crt
    -rw-r----- 1 kibana kibana 10045 May 31 11:21 http.p12
    -rw-r--r-- 1 kibana kibana   989 May 31 11:21 kibana-server.crt
    -rw-r--r-- 1 kibana kibana   960 May 31 11:21 kibana-server.csr
    -rw-r--r-- 1 kibana kibana  1675 May 31 11:21 kibana-server.key
    -rw-r----- 1 kibana kibana  5822 May 31 11:21 transport.p12
    

### 3\. 修改配置文件

配置文件默认位置：`/etc/kibana/kibana.yml`，修改 elasticsearch 登录密码，此处使用密码模式，不使用token模式。

    
    
    vim /etc/kibana/kibana.yml
    
    server.port: 5601
    server.host: "0.0.0.0"
    server.name: "pcapAnalyse"
    
    # kibana 的 https 的通信
    server.ssl.enabled: true
    server.ssl.certificate: /etc/kibana/certs/kibana-server.crt
    server.ssl.key: /etc/kibana/certs/kibana-server.key
    
    # 配置连接的账号密码
    # 修改 elasticsearch 的 kibana_system账号密码的命令：
    # /usr/share/elasticsearch/bin/elasticsearch-reset-password -u kibana_system -i 
    elasticsearch.hosts: ["https://127.0.0.1:9200"]
    elasticsearch.username: "kibana_system"
    elasticsearch.password: "elastic_023"
    
    elasticsearch.pingTimeout: 1500
    elasticsearch.requestTimeout: 30000
    elasticsearch.shardTimeout: 30000
    
    # kibana 连接 elasticsearch 的通信证书
    elasticsearch.ssl.certificateAuthorities: ["/etc/kibana/certs/http_ca.crt"]
    
    logging:
      appenders:
        file:
          type: file
          fileName: /var/log/kibana/kibana.log
          layout:
            type: json
      root:
        appenders:
          - default
          - file
    
    pid.file: /run/kibana/kibana.pid
    i18n.locale: "zh-CN"
    

### 4\. 重启服务，输入密码验证

    
    
    systemctl restart kibana
    
    # 等待一分钟左右
    ps -ef | grep kibana
    netstat -tulnp | grep 5601
    curl localhost:5601 -L
    systemctl status kibana
    

浏览器访问 kibana地址，输入密码成功即可正常使用。

## 三、安装 logstash

### 1\. 安装 logstash

在线下载 logstash最新安装包，官网： <https://www.elastic.co/cn/downloads/past-releases#elasticsearch>

    
    
    rpm -ivh  logstash-8.7.0-x86_64.rpm
    /usr/share/logstash/bin/system-install /etc/logstash/startup.options systemd
    
    
    # 复制证书文件
    mkdir /etc/logstash/certs
    /bin/cp /etc/elasticsearch/certs /etc/logstash/certs -rf
    chown logstash:logstash /etc/logstash/certs/ -R
    

### 2\. 编辑配置文件

配置文件位置`/etc/logstash/logstash.yml`

    
    
    vim /etc/logstash/logstash.yml
    
    path.data: /var/lib/logstash
    path.logs: /var/log/logstash
    xpack.monitoring.enabled: true
    xpack.monitoring.elasticsearch.username: logstash_system
    xpack.monitoring.elasticsearch.password: elastic_023
    
    xpack.monitoring.elasticsearch.hosts: ["https://127.0.0.1:9200"]
    
    # 这个证书就是 /etc/elasticsearch/certs/http_ca.crt
    xpack.monitoring.elasticsearch.ssl.certificate_authority: "/etc/logstash/certs/http_ca.crt"
    

### 3\. 启用日志读取

logstash执行启动的路径为：`/usr/share/logstash/bin/`

不带参数的启动是默认加载`/usr/share/logstash/config/pipelines.yml`，而不是`/etc/logstash/pipelines.yml`

pipelines 模式启动：

    
    
    [root@NTA kibana]# /usr/share/logstash/bin/logstash
    
    # 会自动加载 /usr/share/logstash/config/pipelines.yml，文件缺失的话会报错提示文件不存在。
    

单个cong文件加载启动：

可以选择从文件读取，也可以选择从redis 的消息队列中进行消费。

    
    
    # 启动
    /usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/logstash_redis.conf
    
    # 修改配置文件
    vim /etc/logstash/conf.d/logstash_redis.conf
    
    # 从 redis 的 订阅模式读取
    input {
    	redis {
    		data_type => "pattern_channel"
    		key => "suricata_alert"
    		host => "127.0.0.1"
    		port => 6379
    		threads => 10
    	}
    }
    
    # 从文件读取
    # input
    # {
    #     file
    #     {
    #             path => ["/etc/suricata/alert.json"]
    #             codec =>  "json"
    #             # sincedb_path => "NULL" # windows 平台
    #             sincedb_path => "/dev/null"   # Linux 平台
    #             start_position => "beginning"
    #     }
    # }
    
    filter{
    	# 矫正 @timestamp 用于生成索引名的时间
    	ruby{
    	   code => "
           event.set('ts',(event.get('@timestamp').to_f.round(3)*1000).to_i)  ## 毫秒时间戳
           event.set('n_logstashStamp', (event.get('@timestamp').time.localtime + 8*60*60).strftime('%Y-%m-%d %H:%M:%S'))
           event.set('@timestamp', event.get('n_logstashStamp'))
           "
    	}
    	mutate  {
    		#将不需要的JSON字段过滤
    		remove_field => ["n_logstashStamp", "@version", "event", "log"]
    	}
    }
    
    
    output {
        elasticsearch {
            hosts => ["https://127.0.0.1:9200"]
            index => "alert_%{+YYYYMMdd}"
            user => elastic
            password => "elastic_023"
            timeout => 300
            ssl_certificate_verification => true
            truststore => "/etc/logstash/certs/http.p12"
            # 执行命令获取密码 /usr/share/elasticsearch/bin/elasticsearch-keystore show xpack.security.http.ssl.keystore.secure_password
            truststore_password => "l1FblfNkQayVMYJ5YmvoTQ"
        }
    ```~~
    

