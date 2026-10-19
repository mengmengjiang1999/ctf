## ELK

ELK是指三种工具集成在一起，其中包括elasticsearch(E)，logstash(L)，kibana（K），有时候还会叫EF（filebeat）K，因为当日志体量不大的时候，可以简单使用filebeat转发日志到ES里面。

用直白语言描述三个工具的作用就是

> elasticsearch：存储日志，查询日志
>
> logstash：转发日志和处理日志
>
> kibana：展示日志数据图表

整体架构：

jxwaf(TCP发送)->logstash（监听TCP，并且接受日志，处理日志，转发日志）->elasticsearch(接收日志，存储日志)->kibana（展示日志）。

由于为了让你们更好体验效果，我搞了一套docker-compose集成了所有工具，一键就可以起来服务，地址：[在这里](https://github.com/yingshang/jxwaf-docker-elk.git)

其中logstash.conf配置如下

    
    
    input {
        tcp {
            port => 5000
            codec => json
        }
    }
    
      filter {
          translate {
            field => "[protection_type]"
            destination => "[attack_type]"
            dictionary => {
              "jxwaf-sql_check" => "SQL注入攻击"
              "jxwaf-xss_check" => "xss攻击"
              "jxwaf-directory_traversal_check" => "目录遍历攻击"
              "jxwaf-command_inject_check" => "命令注入攻击"
              "jxwaf-sensitive_file_check" => "敏感文件扫描攻击"
            }
          }
    
        geoip {
                source => "client_ip"
        }
    
        }
    
    
    output {
        stdout {
            codec => rubydebug
        }
    }
    
    
    output{
     elasticsearch{
        hosts=>["es01:9200"] 
        index => "jxwaf-%{+YYYY.MM.dd}"
       }
    
    }
    

打开浏览器访问5601端口，当jxwaf日志经过logstash投递到ES里面，就会产生索引名称，使用*匹配所有时间的jxwaf日志

![](https://image.3001.net/images/20200930/1601443787_5f7417cb140f4d8350b80.jpg)

指定时间作为日志过滤查询的条件

![](https://image.3001.net/images/20200930/1601443795_5f7417d3e3d64adb99d7e.jpg)

设置时间过滤条件之后ES会自动识别所传递的日志有什么字段，因为我们是传入json形式，所以直接就可以解析到所有字段，不需要另外操作。

![](https://image.3001.net/images/20200930/1601443803_5f7417db38df2212b5d55.jpg)

打开discover，就可以看到jxwaf的日志。

![](https://image.3001.net/images/20200930/1601443814_5f7417e69a38af9234fe4.jpg)

## 创建仪表盘

日志存储之后，所以分析和告警需要，需要建立起图表展示。对于图表创建，kibana对于一些基本图表只需要点点点就可以，不需要写ES的查询语句，所以还是会比较简单的。

来到仪表盘，创建一个新的仪表盘：

![1601445917_5f74201da53c24c7cc0b7.png](https://image.3001.net/images/20200930/1601445917_5f74201da53c24c7cc0b7.png)

创建一个可视化的图表

![1601445952_5f742040acc33960774a1.png](https://image.3001.net/images/20200930/1601445952_5f742040acc33960774a1.png)

下图是能够创建可视化图表的类型，一般来说，折线图，表格，饼图是常用图表。

