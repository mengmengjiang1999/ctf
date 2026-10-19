搭建过程可以直接看官方文档，我就直接使用官方自带的[虚拟机](https://packages.wazuh.com/vm/wazuh3.10.2_7.3.2.ova)进行测试，虚拟机里面已经集成了多种服务  

    
    
    server端IP:192.168.17.135

![image.png](https://image.3001.net/images/20191129/1575033803_5de11bcb8719e.png)我在另外一台的ubuntu的虚拟机安装agent与server端进行连接。

客户端配置服务端的IP和端口， **其中端口有两种1514/udp和1515/tcp**

![image.png](https://image.3001.net/images/20191129/1575034238_5de11d7e6e063.png)
客户端就可以连接到服务端

![image.png](https://image.3001.net/images/20191129/1575034303_5de11dbfd98fa.png)虽然上面日志看起来没有问题，不过我在服务端那边没有看到激活。因为我在一开始用systemctl启动会报错，启动不了

![image.png](https://image.3001.net/images/20191129/1575034657_5de11f21e7a08.png)于是我就直接进入到ossec的bin目录下进行启动

![image.png](https://image.3001.net/images/20191129/1575034633_5de11f09da03a.png)服务端显示active

![image.png](https://image.3001.net/images/20191129/1575034712_5de11f58b0f80.png)前期工作都做好了，现在就可以看成品，虚拟机里面有kibana的wazuh插件，打开虚拟机端口443，<https://IP>

#
![image.png](https://image.3001.net/images/20191129/1575035217_5de12151ebb93.png)
Overview

## Security events  

安全日志的仪表台

![image.png](https://image.3001.net/images/20191129/1575035660_5de1230c77858.png)点击右上角discover，里面可以看到日志

![image.png](https://image.3001.net/images/20191129/1575035726_5de1234e963f5.png)还可以使用kql查询（kibana自带的查询）

##
![image.png](https://image.3001.net/images/20191129/1575035853_5de123cda6e41.png)
Integrity monitoring  

这个是文件完整性监控页面，这是默认的，没有结果

##
![image.png](https://image.3001.net/images/20191129/1575036039_5de124878d214.png)Policy
monitoring  

这个是监控系统的配置文件是否合乎安全配置基线

##
![image.png](https://image.3001.net/images/20191129/1575036196_5de125243978c.png)System
auditing  

审计用户行为，监控命令执行情况和对查看机密文件进行报警

##
![image.png](https://image.3001.net/images/20191129/1575036232_5de1254875932.png)
Vulnerabilities  

发现系统应用已知的漏洞

![image.png](https://image.3001.net/images/20191129/1575036360_5de125c872fbc.png)其他功能都有说明的，就不一一说明

# Management

##  Ruleset  

这些都是rule检测规则

![image.png](https://image.3001.net/images/20191129/1575036831_5de1279f79f49.png)规则都是基于xml来编写的

##
![image.png](https://image.3001.net/images/20191129/1575036893_5de127ddae980.png)Groups  

可以对客户端进行分组

![image.png](https://image.3001.net/images/20191129/1575036971_5de1282b1bd88.png)可以点击进去看有什么客户端

![image.png](https://image.3001.net/images/20191129/1575036996_5de12844c5a1b.png)可以删除客户端

##
![image.png](https://image.3001.net/images/20191129/1575037018_5de1285a3fde0.png)Configuration  

这个选项是管理集群的配置，我就不说了，因为我用的是单机

## Status  

展示集群状态

##
![image.png](https://image.3001.net/images/20191129/1575037188_5de12904d0a83.png)Logs  

各种各样的日志

##
![image.png](https://image.3001.net/images/20191129/1575037237_5de1293568bb2.png)Cluster  

我没有开启集群

#
![image.png](https://image.3001.net/images/20191129/1575037300_5de12974ac4e3.png)[](https://192.168.17.135/app/wazuh#/agents-preview)Agents  

查看主机的存活，服务器的信息

![image.png](https://image.3001.net/images/20191129/1575037389_5de129cd88da6.png)  

点击ubuntu机器，有着更加细化的日志展示

![image.png](https://image.3001.net/images/20191129/1575037508_5de12a44b961a.png)![image.png](https://image.3001.net/images/20191129/1575037550_5de12a6e95126.png)![image.png](https://image.3001.net/images/20191129/1575037597_5de12a9d9b5da.png)信息页面展示完成了，下面咱们就来测试一下

# 实战演练

## 安全日志

使用hydra对agent机器进行ssh爆破，可以看到ossec监控到爆破日志

##
![image.png](https://image.3001.net/images/20191129/1575038285_5de12d4dd2c7e.png)![image.png](https://image.3001.net/images/20191129/1575038306_5de12d6236ba0.png)![image.png](https://image.3001.net/images/20191129/1575038640_5de12eb0168e3.png)文件完整性

找到了监控的位置，我们去/bin目录下用vim随便插入一些字符，看看会不会检测到

![image.png](https://image.3001.net/images/20191129/1575039043_5de13043a9cd9.png)启动检测

![image.png](https://image.3001.net/images/20191129/1575039375_5de1318f96aee.png)过一会就可以看到修改的日志

#
![image.png](https://image.3001.net/images/20191129/1575039356_5de1317c38fd0.png)![image.png](https://image.3001.net/images/20191129/1575039408_5de131b04ba8b.png)rootkit监控

![image.png](https://image.3001.net/images/20191129/1575041362_5de13952abd47.png)![image.png](https://image.3001.net/images/20191129/1575041492_5de139d4d6099.png)![image.png](https://image.3001.net/images/20191129/1575041544_5de13a0813d05.png)我原本想看看假如上传webshell进行操作，wazuh会不会检测到，
**答案是否定的。虽然可能是权限问题，但是我查看passwd文件都没有上报。**

**![image.png](https://image.3001.net/images/20191130/1575079731_5de1cf33359c6.png)**接下来，我测试挖矿病毒，<https://github.com/yingshang/Legacy-of-intrusion>，这是我之前收集到的

当我执行病毒的时候，我发现这个功能没有日志，日志都在完整性监控那里

## SCA

SCA检测那里，直接就有了

##
![image.png](https://image.3001.net/images/20191130/1575080427_5de1d1ebe9808.png)system
aduiting

## 关于这个功能，我有点迷，我是这样测试的

 **我创建一个test用户，进去查看passwd,shadow文件，进去root目录，删除root目录  
**

按照说，这个用户在搞事，应该记录他的行为，但是我在这个功能没有看到日志

  

  

## Vulnerabilities  

在配置文件那里启动这个功能，保存之后，重新启动服务

![image.png](https://image.3001.net/images/20191130/1575082661_5de1daa508f1d.png)![image.png](https://image.3001.net/images/20191130/1575082742_5de1daf65e5d6.png)![image.png](https://image.3001.net/images/20191130/1575082759_5de1db07103b2.png)  

## Osquery  

server端ossec.conf配置

    
    
    <wodle name="osquery">
        <disabled>no</disabled>
        <run_daemon>yes</run_daemon>
        <bin_path>/usr/bin</bin_path>
        <log_path>/var/log/osquery/osqueryd.results.log</log_path>
        <config_path>/etc/osquery/osquery.conf</config_path>
        <add_labels>no</add_labels>
        <pack name="custom_pack">/path/to/custom_pack.conf</pack>
    </wodle>

agent和server安装osquery

安装文档，<https://documentation.wazuh.com/3.8/user-manual/capabilities/osquery.html?highlight=osquery>

    
    
    export OSQUERY_KEY=1484120A(c屏蔽)(4屏蔽)E9F8A1A577AEEE97A80C63C9D8B80B
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $OSQUERY_KEY
    add-apt-repository 'deb [arch=amd64] https://pkg.osquery.io/deb deb main'
    apt-get update -y
    apt-get install -y osquery
    
    
    
    curl -L https://pkg.osquery.io/rpm/GPG | tee /etc/pki/rpm-gpg/RPM-GPG-KEY-osquery
    yum-config-manager --add-repo https://pkg.osquery.io/rpm/osquery-s3-rpm.repo
    yum-config-manager --enable osquery-s3-rpm
    yum install osquery
    

复制osquery配置文件

    
    
    cp /usr/share/osquery/osquery.example.conf /etc/osquery/osquery.conf

启动osquery

![image.png](https://image.3001.net/images/20191130/1575083919_5de1df8fd5b18.png)server和agent重新启动ossec

![image.png](https://image.3001.net/images/20191130/1575084083_5de1e03311325.png)![image.png](https://image.3001.net/images/20191130/1575084105_5de1e0498245e.png)我以为一开始就有日志，后来才发现osquery需要自己写sql查询，具体可以参照这里
<https://www.jianshu.com/p/a971cc53347a>

## virustotal

首先去官网注册账号，获取到api key

![image.png](https://image.3001.net/images/20191130/1575090079_5de1f79fb3467.png)接着ossec.conf，在最后一行添加(SERVER端)，然后重启服务

    
    
    <ossec_config>
    <integration>
      <name>virustotal</name>
      <api_key>API_KEY</api_key> <!-- Replace with your VirusTotal API key -->
      <group>syscheck</group>
      <alert_format>json</alert_format>
    </integration>
    </ossec_config>

![image.png](https://image.3001.net/images/20191130/1575090325_5de1f8956f005.png)

![image.png](https://image.3001.net/images/20191130/1575092020_5de1ff34d8731.png)  
我将下载挖矿病毒到opt目录下(AGENT)

![image.png](https://image.3001.net/images/20191130/1575090474_5de1f92a8e02b.png)很奇怪，收不到日志，说连接不是，但是我在官网还是可以看到已经上传的，不管了，我这边网络有问题，搞不了。

触发的警报将记录在`integration.log`文件中，并`alerts.log`与所有其他警报一起存储在文件中。  

![image.png](https://image.3001.net/images/20191130/1575098735_5de2196f43a44.png)![image.png](https://image.3001.net/images/20191130/1575098763_5de2198b00fea.png)后来执行挖矿病毒之后

![image.png](https://image.3001.net/images/20191130/1575100613_5de220c57ef2f.png)![image.png](https://image.3001.net/images/20191130/1575100623_5de220cf7b871.png)  

