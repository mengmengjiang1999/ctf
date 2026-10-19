## 背景

混合云情况下，为了满足 PCI 要求，需要安装 wazuh 及接收相关告警。  
相关设计有如下考虑：

  1. 满足合规要求，避免扩大 PCI 的评测范围。

  2. 环境没有专线连接内网，会走公网的情况。

  3. 目前此环境机器数量<50台, 预计未来一年不会增加。

## 总体结构

![image](https://image.3001.net/images/20220302/1646230464_621f7bc020ef0002ac1cd.png!small)

相关事项：

  1. Kafka、logstash 复用运维环境。

  2. 使用 logstash 发送 HEC 到 splunk。

  3. 未使用 Splunk UF (Universal Forwarder，下同) 进行转发是因为 UF 不支持 HEC 发送。 output 只支持`tcpout`and`syslog`，没有尝试过通过`tcpout`发送到启用 SSL 的 inputs，相关文档可参考[Configure Splunk forwarding to use your own SSL certificates - Splunk Documentation](https://docs.splunk.com/Documentation/Splunk/8.2.5/Security/ConfigureSplunkforwardingtousesignedcertificates)

接下来介绍解释所选的 wazuh 和 splunk 配置方式。

## wazuh Server

wazuh提供两种部署方式：

  1. All-in-one：wazuh 服务端和 ELK 都在同一台机器上。

  2. Distributed：每个组成部分都自定义安装位置。

因为 wazuh 服务端、kafka、es 都支持以集群方式运行，所以就直接选择了自定义安装方式了。

安装参考[Distributed deployment - Wazuh server · Wazuh
documentation](https://documentation.wazuh.com/current/installation-guide/open-distro/distributed-deployment/index.html)

安装完成务必参考[Securing the Wazuh API - RESTful API · Wazuh
documentation](https://documentation.wazuh.com/current/user-manual/api/securing-api.html)限制来源 IP 及配置访问密码。

### 所需配置

官方建议是单节点4C 8G。但根据生产中的经验，单节点4C 16G 足以支撑 3K 节点左右，此时CPU平均利用率是 30%左右，内存用掉大致
4G。（注：默认配置）

PCI 要求日志保存一年，机器数量*15.2G 即为日志大小。由于日志都存储在 ELK 及本地 splunk 中，且Filebeat
没有删除日志的能力，可以使用 crontab 进行定时删除一天以前的日志。

> Alert 路径`/var/ossec/logs/alerts/alerts.json`

后续若启用更多的检测，肯定会产生更多的日志的，所以估计集群也在不远的将来了。

### 相关配置

Filebeat新增了如下的配置，并注释掉了`output.logstash `的输出

    
    
    output.kafka: 
    	enabled: true 
    	hosts: ["X.X.X.X:XXXX"]
    	topic: filebeat
    

Logstash 使用如下配置发送。此处`%{message}`为默认名字，若使用别名请注意更换。

    
    
    http {
      #format => "json"
      #content_type => "application/json"
      http_method => "post"
      url => "https://hec.example.com/services/collector/event"
      headers => ['Authorization', 'Splunk -xxxx-xxxx-xxxxxxxxxx']
      mapping => {
       "event" => "%{message}"
      }
     }
    }
    

## Splunk

Splunk 转发总体结构可以参考下图  
![image](https://image.3001.net/images/20220302/1646230485_621f7bd556f8b1e795772.png!small)

Splunk 的转发模式有两种，使用 UF 或者使用 HttpEventCollect (HEC)。

### 转发模式-UF

本地安装 Universal Forwarder，配置监控本地文件变化，发送给 Heavy Forwarder.

可参考相关配置  
`/opt/splunkforwarder/etc/system/local/inputs.conf`详见[inputs.conf - Splunk
Documentation](https://docs.splunk.com/Documentation/Splunk/8.0.2/Admin/Inputsconf)

    
    
    [monitor:///var/ossec/logs/alerts/alerts.json]
    
    disabled = 0
    host = Your_Host_Name
    index = Your_Index_Name
    sourcetype = Your_Source_Type_Name
    

`/opt/splunkforwarder/etc/system/local/outputs.conf`详见[outputs.conf - Splunk
Documentation](https://docs.splunk.com/Documentation/Splunk/8.2.5/Admin/Outputsconf)

    
    
    Single server: [tcpout-server://<ip address>:<port>]
    

### 转发模式-HEC

Nginx 配置一个 proxy_pass 转发，指向Splunk Heavy Forwarder 配置的监听端口即可。  
可使用这个命令进行测试是否配置成功，需注意格式必须有 event。

    
    
    curl https://hec.example.com/services/collector/event -H "Authorization: Splunk XXXX-XXXX-XXXX-XXXX-XXXX" -d '{"event": "hello world"}'
    {"text": "Success", "code": 0}
    

其余参考[Set up and use HTTP Event Collector in Splunk Web - Splunk
Documentation](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_Splunk_Enterprise)

### 安装 wazuh app

APP安装在搜索头。[Install the wazuh app for Splunk - Installing
Splunk](https://documentation.wazuh.com/current/installation-guide/more-installation-alternatives/splunk/splunk-app.html)

需注意的是要选择对应版本的 wazuh app 与 splunk，这里存在较严格的版本限制。详见[wazuh-splunk/README.md at
master · wazuh/wazuh-splunk](https://github.com/wazuh/wazuh-splunk/blob/master/README.md)。

App 提供通过 wazuh api 获取存活机器数量、修改相关配置的功能。若要查看Disvocer 的功能，仍然需要本地存有 wazuh
日志。总体结构如下

![image](https://image.3001.net/images/20220302/1646230513_621f7bf193339a5675294.png!small)

## 扩展阅读

  1. [splunk validated architectures](https://www.splunk.com/pdfs/technical-briefs/splunk-validated-architectures.pdf)

  2. [HEC configuration | Documentation | Splunk Developer Program](https://dev.splunk.com/enterprise/docs/devtools/httpeventcollector/)

  3. [Configure an NGINX load balancer | Documentation | Splunk Developer Program](https://dev.splunk.com/enterprise/docs/devtools/httpeventcollector/confignginxloadhttp)

