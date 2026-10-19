****

## **拓扑介绍**

**应用识别系统将会通过bro识别应用并生成日志。ELK部署在远程端，用于收集，分析，存储和识别所有日志。BRO安装在IP为192.168.1.147的机器上，ELK安装在IP为192.168.1.142的机器上。**

    
    
    ens33              网络接口名称   
    192.168.1.147      bro设备的网络接口ipv4地址    
    192.168.1.142      ELK设备的网络接口ipv4地址 

## **安装bro**

由于metron-bro-plugin-kafka插件的编译安装依赖于bro源代码，因此我们使用bro源代码进行安装。

 **依赖安装**

    
    
    ~/src$ sudo apt-get install -y tcpdump git vim cmake make gcc g++ flex bison libpcap-dev python-dev swig zlib1g-dev libssl1.0-dev dirmngr curl openjdk-8-jre zookeeperd 

**下载bro源代码并验证**

    
    
    ~/src$ wget https://www.bro.org/downloads/bro-2.5.4.tar.gz 
    ~/src$ wget https://www.bro.org/downloads/bro-2.5.4.tar.gz.asc 
    ~/src$ gpg --recv-keys C68B494DF56ACC7E
    ~/src$ gpg -v bro-2.5.4.tar.gz.asc

 **安装**

    
    
    ~/src$ tar -xvf bro-2.5.4.tar.gz 
    ~/src$ cd bro-2.5.4/ 
    ~/src/bro-2.5.4$ ./configure --enable-debug 
    ~/src/bro-2.5.4$ make 
    ~/src/bro-2.5.4$ sudo make install 

**设置env值**

Bro安装的目录位置为/usr/local/bro/bin/，添加以下行至/etc/bash.bashrc文件中：

    
    
    if [ -d /usr/local/bro/bin ];then
      PATH="/usr/local/bro/bin/:$PATH"
      export PATH
    fi

 **将bro设置为systemd并启动bro服务**

    
    
    ~# cat > /etc/systemd/system/bro.service << EOL
    [Unit]
    Description=Bro
    After=network.target
    
    [Service]
    ExecStartPre=/usr/local/bro/bin/broctl cleanup
    ExecStartPre=/usr/local/bro/bin/broctl check
    ExecStartPre=/usr/local/bro/bin/broctl install
    ExecStart=/usr/local/bro/bin/broctl start
    ExecStop=/usr/local/bro/bin/broctl stop
    RestartSec=10s
    Type=oneshot
    RemainAfterExit=yes
    TimeoutStopSec=600
    
    [Install]
    WantedBy=multi-user.target
    
    EOL
    
    ~# systemctl daemon-reload   
    ~# systemctl enable bro  
    ~# systemctl start bro   

有关bro的详细安装和使用，请参阅文档[how-to-deploy-bro-app-identification-env.mkd](https://github.com/hardenedlinux/Debian-GNU-Linux-Profiles/blob/master/NSM/docs/how-to-deploy-bro-app-identification-env.mkd)。

 **将本地解析配置文件添加到BRO**

以下我将通过一个示例来说明，本地Bro解析配置文件为[bro_parse_jd.bro](https://github.com/hardenedlinux/Debian-GNU-Linux-Profiles/blob/master/NSM/sensor/bro/scripts/frameworks/software/own-software/bro_parse_jd.bro)。

在/usr/local/bro/share/bro/site路径下创建一个名为harbian的目录，并将bro_parse_jd.bro文件放置在该目录中。然后在harbian目录中创建一个名为__load__.bro的文件，并在
__load__.bro文件中添加以下行：

    
    
    @load ./bro_parse_jd.bro.

__load__.bro文件仅用于在启动bro时自动加载当前目录中的bro配置文件。此外，我们还需要将以下行添加到文件/usr/local/bro/share/bro/site/local.bro中：

    
    
    @load ./harbian

然后使用以下命令重启bro服务：

    
    
    ~# systemctl restart bro 

## **安装Kafka**

 **下载kafka源**

    
    
    ~/src$ wget https://archive.apache.org/dist/kafka/1.0.0/kafka_2.12-1.0.0.tgz 
    ~/src$ wget https://archive.apache.org/dist/kafka/1.0.0/kafka_2.12-1.0.0.tgz.asc 

**验证**

    
    
    ~/src$ gpg --recv-keys  3B417B9B 
    ~/src$ gpg -v kafka_2.12-1.0.0.tgz.asc 

**安装kafka并启动服务**

    
    
    ~/src$ tar -xvf kafka_2.12-1.0.0.tgz
    ~/src$ sudo mv kafka_2.12-1.0.0 /opt/kafka
    ~/src$ sudo sed -i '/^log.dirs/{s/=.*//;}' /opt/kafka/config/server.properties
    ~/src$ sudo sed -i 's/^log.dirs/log.dirs=\/var\/lib\/kafka/' /opt/kafka/config/server.properties
    ~/src$ sudo sed -i '$alisteners=bro://192.168.1.147:9092' /opt/kafka/config/server.properties 
    
    ~/src# cat > /etc/systemd/system/kafka.service << EOF
    [Unit]
    Description=Kafka Service
    Wants=network.target
    After=network.target
    
    [Service]
    ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
    ExecReload=on-failure
    Restart=always
    User=root
    Group=root
    StandardOutput=syslog
    StandardError=syslog
    
    [Install]
    WantedBy=multi-user.target
    EOF

 **启用kafka服务并启动**

启动kafka服务时，必须确保zookeeper服务已启动。

    
    
    ~/src$ systemctl enable zookeeper 
    ~/src$ systemctl start zookeeper
    ~/src$ sudo systemctl daemon-reload
    ~/src$ sudo systemctl enable kafka 
    ~/src$ sudo systemctl start kafka

##  **安装metron-bro-plugin-kafka插件**

 **安装librdkafka**

    
    
    ~/src$ curl -L https://github.com/edenhill/librdkafka/archive/v0.9.4.tar.gz | tar xvz 
    ~/src$ cd librdkafka-0.9.4/ 
    ~/src/librdkafka-0.9.4$ ./configure --enable-sasl 
    ~/src/librdkafka-0.9.4$ make 
    ~/src/librdkafka-0.9.4$ sudo make install 

**安装插件**

    
    
    ~/src$ git clone https://github.com/apache/metron-bro-plugin-kafka.git
    ~/src$ cd metron-bro-plugin-kafka
    ~/src/metron-bro-plugin-kafka$ ./configure --bro-dist=$HOME/src/bro-2.5.4/
    ~/src/metron-bro-plugin-kafka$ make 
    ~/src/metron-bro-plugin-kafka$ sudo make install

确认插件是否已被正确安装：

    
    
    ~/src# bro -N Apache::Kafka 

## 如何设置bro日志写入到kafka

设置以下行到/usr/local/bro/share/bro/site/local.bro文件中：

    
    
    @load /usr/local/bro/lib/bro/plugins/APACHE_KAFKA/scripts/Apache/Kafka/logs-to-kafka.bro
    redef Kafka::topic_name = "";
    redef Kafka::logs_to_send = set(Conn::LOG, HTTP::LOG, DNS::LOG, SMTP::LOG, SSL::LOG, Software::LOG, DHCP::LOG, FTP::LOG, IRC::LOG, Notice::LOG, X509::LOG, SSH::LOG, SNMP::LOG);
    redef Kafka::kafka_conf = table(["metadata.broker.list"] = "192.168.1.147:9092");

确保bro日志已被写入到kafka中：

    
    
    ~/src# systemctl status kafka | grep "Active:.active"
       Active: active (running) since Tue 2018-07-24 03:25:10 CST; 23min ago
    
    ~/src# netstat -ntpl  | grep 9092
    tcp6       0      0 192.168.1.147:9092      :::*                    LISTEN      30913/java 
    
    ~/src$ ls /var/lib/kafka/bro-0/00000000000000000000.log 

## 安装ELK

 **依赖安装**

    
    
    ~$ sudo apt-get install -y openjdk-8-jre curl wget libgeoip-dev

 **下载ELK deb包以及SHA512 (512-bit) checksums文件**

    
    
    ~$ mkdir src; cd src 
    ~/src$ wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.3.0.deb 
    ~/src$ wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.3.0.deb.sha512 
    ~/src$ wget https://artifacts.elastic.co/downloads/logstash/logstash-6.3.0.deb 
    ~/src$ wget https://artifacts.elastic.co/downloads/logstash/logstash-6.3.0.deb.sha512 
    ~/src$ wget https://artifacts.elastic.co/downloads/kibana/kibana-6.3.0-amd64.deb 
    ~/src$ wget https://artifacts.elastic.co/downloads/kibana/kibana-6.3.0-amd64.deb.sha512 

**验证ELK deb包**

    
    
    ~/src$ sha512sum -c elasticsearch-6.3.0.deb.sha512  
    elasticsearch-6.3.0.deb: OK
    ~/src$ sha512sum -c logstash-6.3.0.deb.sha512 
    logstash-6.3.0.deb: OK
    ~/src$ sha512sum -c kibana-6.3.0-amd64.deb.sha512 
    kibana-6.3.0-amd64.deb: OK

 **安装ELK deb包**

    
    
    ~/src$ sudo dpkg -i *.deb

 **Logstash配置**

    
    
    ~/src$ echo config.reload.automatic: true |sudo tee -a /etc/logstash/logstash.yml
    ~/src$ echo config.reload.interval: 3s |sudo tee -a /etc/logstash/logstash.yml

 **创建新的logstash配置**

为每种类型的日志生成conf文件。以下仅是软件的一个示例：

    
    
    ~/src# cat > /etc/logstash/conf.d/bro-software.conf << EOF 
    input {
      kafka {
        topics => ["software"]
        group_id => "bro_logstash"
         		bootstrap_servers => "192.168.1.147:9092"
         		codec => json
         		auto_offset_reset => "earliest"
       	}
    }
    
    output {
      elasticsearch {
         		hosts => ["192.168.1.142:9200"]
        index => "bro-software"
        document_type => "software"
       	}
    }

其他conf文件你可以在[logstash-conf](https://github.com/hardenedlinux/Debian-GNU-Linux-Profiles/tree/master/NSM/ELK/conf)中找到。将这些配置文件放置在/etc/logstash/conf.d目录中。

## Elasticsearch配置

 **将Elasticsearch绑定到localhost**

将以下行添加到/etc/elasticsearch/elasticsearch.yml；

    
    
    network.host: "192.168.1.142" 
    http.port:9200 

如果elasticsearch服务为远程端，请将绑定地址设置为指定的IP地址。

 **确保elasticsearch正常工作**

    
    
    sudo systemctl start elasticsearch 
    curl http://192.168.1.142:9200
    {
      "name" : "VZDjFmY",
      "cluster_name" : "elasticsearch",
      "cluster_uuid" : "xql3xQSbSvinXDIYchwswQ",
      "version" : {
        "number" : "6.3.0",
        "build_flavor" : "default",
        "build_type" : "deb",
        "build_hash" : "424e937",
        "build_date" : "2018-06-11T23:38:03.357887Z",
        "build_snapshot" : false,
        "lucene_version" : "7.3.1",
        "minimum_wire_compatibility_version" : "5.6.0",
        "minimum_index_compatibility_version" : "5.0.0"
      },
      "tagline" : "You Know, for Search"
    }

 **Kibana配置**

在Kibana配置文件/etc/kibana/kibana.yml中添加以下行：

    
    
    server.port: 5601
    server.host: "192.168.1.142"
    elasticsearch.url: "http://192.168.1.142:9200"

 **启动ELK服务**

    
    
    ~/src$ sudo /bin/systemctl daemon-reload
    ~/src$ sudo /bin/systemctl enable elasticsearch.service logstash.service kibana.service
    ~/src$ sudo systemctl start elasticsearch.service kibana.service logstash.service

##  **Kibana**

 **打开Kibana**

在浏览器地址栏中输入192.168.1.142:5601。打开如下所示页面：

![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425316_5b6636a488e5e.png!small)

 **创建索引模式**

以下是使用软件日志创建模式的示例：

![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425363_5b6636d32ee84.png!small)![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425363_5b6636d3607e5.png!small)![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425363_5b6636d3724e6.png!small)![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425363_5b6636d39121b.png!small)![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425363_5b6636d3d094a.png!small)

 **发现软件索引模式**

**![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425422_5b66370ebf289.png!small)**

 **创建可视化**

**![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425451_5b66372bbb675.png!small)![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425451_5b66372bd229d.png!small)![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425451_5b66372becb41.png!small)![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425452_5b66372c5a62c.png!small)![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425452_5b66372c87f49.png!small)![基于Bro的应用层数据包识别工具](https://image.3001.net/images/20180805/1533425452_5b66372cb6236.png!small)**

## 参考

>
> [https://www.bro.orghttp://try.bro.org/](https://www.bro.orghttp//try.bro.org/)
>
> <https://www.bro.org/sphinx/scripts/base/frameworks/software/main.bro.html>
>
>
> <https://www.bro.org/sphinx/scripts/base/bif/plugins/Bro_HTTP.events.bif.bro.html>
>
>
> <https://www.bro.org/sphinx/scripts/base/bif/plugins/Bro_SSL.events.bif.bro.html>
>
> <https://www.elastic.co/guide/en/logstash/current/plugins-inputs-kafka.html>
>
> <https://www.elastic.co/guide/en/logstash/6.3/plugins-outputs-> elasticsearch.html>
>
> <https://www.elastic.co/https://github.com/apache/metron-bro-plugin-kafka>

 ** *参考来源：[github](https://github.com/hardenedlinux/Debian-GNU-Linux-Profiles/blob/master/NSM/docs/ELK_with_bro_ID_doc.mkd)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

