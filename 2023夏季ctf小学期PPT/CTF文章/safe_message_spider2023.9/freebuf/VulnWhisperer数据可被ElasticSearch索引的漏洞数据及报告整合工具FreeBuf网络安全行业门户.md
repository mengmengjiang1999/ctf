***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**VulnWhisperer是一个漏洞数据和报告的整合工具。VulnWhisperer会提取所有报告并创建一个具有唯一文件名的文件，然后将其发送给logstash。Logstash则会从文件名中提取数据标记报告中的所有信息（请参阅logstash_vulnwhisp.conf文件），并最终将数据发送到elasticsearch进行索引。**  

**![vuln_whisperer_logo_s.png](https://image.3001.net/images/20180711/15312626245927.png!small)**

## 当前支持

###  **漏洞框架：**

[Nessus (v6 & **v7** )](https://www.tenable.com/products/nessus/nessus-professional)

[Qualys Web Applications](https://www.qualys.com/apps/web-app-scanning/)

[Qualys Vulnerability Management](https://www.qualys.com/apps/vulnerability-management/)

[OpenVAS](http://www.openvas.org/)

[Tenable.io](https://www.tenable.com/products/tenable-io)

[Nexpose](https://www.rapid7.com/products/nexpose/)（暂不支持）

[Insight VM](https://www.rapid7.com/products/insightvm/)（暂不支持）

[NMAP](https://nmap.org/)（暂不支持）

更多

## 安装及操作概要：

1.严格遵循安装要求。

2.在[example.ini](https://github.com/austin-taylor/VulnWhisperer/blob/master/configs/frameworks_example.ini)文件中填写你要处理的部分。

3.修改[logstash文件](https://github.com/austin-taylor/VulnWhisperer/tree/master/logstash)中的IP，并将它们导入到logstash
conf目录（默认为/etc/logstash/conf.d/）。

4.导入[kibana可视化](https://github.com/austin-taylor/VulnWhisperer/tree/master/kibana/vuln_whisp_kibana)。

5.运行[Vulnwhisperer](https://github.com/austin-taylor/VulnWhisperer#run)。

###  **安装环境**

1.ElasticStack 5.x

2.Python 2.7

3.漏洞扫描器

可选：Message broker 例如Kafka或RabbitMQ

###  **VulnWhisperer安装（可能需要sudo）**

首先，我们需要安装其依赖项：

    
    
    sudo apt-get install  zlib1g-dev libxml2-dev libxslt1-dev 

接着，我们安装依赖模块：

    
    
    cd deps/qualysapi
    python setup.py install

最后，安装VulnWhisperer：

    
    
    pip install -r /path/to/VulnWhisperer/requirements.txt
    cd /path/to/VulnWhisperer
    python setup.py install

###  **ELK节点安装示例**

如果你没有现成的ELK集群/节点，以下将为你提供在Debian上的Elasticsearch＆Kibana独立节点的安装指南。

请注意，还有一个docker-compose.yml文件也可用。

 **Debian:**
<https://www.elastic.co/guide/en/elasticsearch/reference/5.6/deb.html>

    
    
    sudo apt-get install -y default-jre
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -    sudo apt-get install apt-transport-https
    echo "deb https://artifacts.elastic.co/packages/5.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-5.x.list
    sudo apt-get update && sudo apt-get install elasticsearch kibana logstash
    sudo /bin/systemctl daemon-reload
    sudo /bin/systemctl enable elasticsearch.service
    sudo /bin/systemctl enable kibana.service
    sudo /bin/systemctl enable logstash.service

###  **Elasticsearch＆Kibana配置示例**

 **使用你喜欢的文本编辑器**

获取主机IP，更改etc /elasticsearch/elasticsearch.yml文件中的IP。（默认为'localhost'）

验证Elasticsearch是否在端口9200上运行。（默认）

获取主机IP，更改/etc/kibana/kibana.yml文件中的IP（默认为'localhost'）。验证Kibana是否指向正确的Elasticsearch
IP。（这是在上一步中设置的）

验证Kibana是否在端口5601上运行。（默认）

启动elasticsearch，验证它们是否正在运行/相互通信：

    
    
    sudo service elasticsearch start
    sudo service kibana start

或

    
    
    sudo systemctl start elasticsearch.service
    sudo systemctl start kibana.service

###  **Logstash配置说明示例**

将/VulnWhisperer/logstash/中的Logstash .conf文件，复制或移动到/etc/logstash/conf.d/

验证Logstash.conf文件输入，是否已在input.file.path目录中包含了VulnWhisper Scans的正确位置：

    
    
    input {
      file {
        path => "/opt/vulnwhisperer/nessus/**/*"
        start_position => "beginning"
        tags => "nessus"
        type => "nessus"
      }
    }

验证Logstash.conf文件输出，是否已包含了上一步中正确的Elasticsearch IP设置(默认为localhost）：

    
    
    output {
      if "nessus" in [tags] or [type] == "nessus" {
        #stdout { codec => rubydebug }
        elasticsearch {
          hosts => [ "localhost:9200" ]
          index => "logstash-vulnwhisperer-%{+YYYY.MM}"
        }
      }

验证logstash是否已具有正确的文件权限，可以读取VulnWhisperer Scans的位置。

配置完成后运行Logstash
:(作为服务运行Logstash将获取/etc/logstash/conf.d/中的所有文件。如果你只想运行单个logstash文件，请参考以下命令）：

作为服务运行Logstash：

    
    
    sudo service logstash start

或

    
    
    sudo systemctl start logstash.service

单个logstash文件：

    
    
    sudo /usr/share/logstash/bin/logstash --path.settings /etc/logstash/ -f /etc/logstash/conf.d/1000_nessus_process_file.conf

##  **配置**

### VulnWhisperer配置：

1.配置Ini文件

2.设置Logstash文件

3.导入ElasticSearch模板

4.导入Kibana仪表板

[frameworks_example.ini文件](https://github.com/austin-taylor/VulnWhisperer/blob/master/configs/frameworks_example.ini)：

##
![config_example.png](https://image.3001.net/images/20180711/15312627434132.png!small)

## 运行

填写必要信息至ini配置文件，然后执行如下命令。

    
    
    vuln_whisperer -c configs/frameworks_example.ini -s nessus
    or
    vuln_whisperer -c configs/frameworks_example.ini -s qualys

**![running_vuln_whisperer.png](https://image.3001.net/images/20180711/15312627702433.png!small)**

###  **每晚运行**

如果你当前运行的系统为linux，请务必创建一个cronjob以删除存储在数据库中的旧文件。如果你正在使用json，请务必更改.csv。

使用以下设置创建用户级的crontab - 其表示将在每晚的0130运行vulnwhisperer：

    
    
    00 1 * * * /usr/bin/find /opt/vulnwhisp/ -type f -name '*.csv' -ctime +3 -exec rm {} \;
    
    
    30 1 * * * /usr/local/bin/vuln_whisperer -c /opt/vulnwhisp/configs/example.ini

而对于Windows系统，你可能需要在bin目录中的vulnWhisperer中键入二进制文件的完整路径。

## 视频演示

 ***参考来源：[GitHub](https://github.com/austin-taylor/VulnWhisperer)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

