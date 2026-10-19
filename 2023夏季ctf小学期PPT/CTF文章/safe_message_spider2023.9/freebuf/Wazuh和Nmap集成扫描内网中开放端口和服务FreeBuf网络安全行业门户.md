**作者：Pamela@涂鸦智能安全实验室**

# 前言

本篇文章将介绍利用`Wazuh`和`Nmap`集成，扫描内网中开放端口和服务。

此处我们将使用`python-nmap`**(https://pypi.org/project/python-nmap/)**来扫描不同子网的开放端口/服务。

 **Nmap扫描器需要安装在不同网段的不同Wazuh agent上** ，其输出被转换为`JSON`，并添加到每个agent的`active-responseses.log`中。然后扫描通过`cron`安排作业，每周、每月等执行一次，这里也可以通过Wazuh的`wodle
command`集成来触发。

# 环境准备

  * Nmap需要安装在`不同网段不个代理上`，以运行网络扫描。（如果每个代理上安装也不是不行，看你喜欢。）
  * 安装`python-nmap`(https://pypi.org/project/python-nmap/)

# 实现过程

### agent端

#### nmap.py

注：这个脚本可以放在agent上的任何文件夹中，它的执行可以用cron来安排。

    
    
    import nmap  
    import time  
    import json  
    nm = nmap.PortScanner()  
    #Add subnets to scan to the Subnets Array  
    subnets=['192.168.252.0/24','192.168.1.0/24']  
    for subnet in subnets:  
    json_output={}  
    nm.scan(subnet)  
    for host in nm.all_hosts():  
    json_output['nmap_host']=host  
    for proto in nm[host].all_protocols():  
    if proto not in ["tcp", "udp"]:  
    continue  
    json_output['nmap_protocol']=proto  
    lport = list(nm[host][proto].keys())  
    lport.sort()  
    for port in lport:  
    hostname = ""  
    json_output['nmap_port']=port  
    for h in nm[host]["hostnames"]:  
    hostname = h["name"]  
    json_output['nmap_hostname']=hostname  
    hostname_type = h["type"]  
    json_output['nmap_hostname_type']=hostname_type  
    json_output['nmap_port_name']=nm[host][proto][port]["name"]  
    json_output['nmap_port_state']=nm[host][proto][port]["state"]  
    json_output['nmap_port_product']=nm[host][proto][port]["product"]  
    json_output['nmap_port_extrainfo']=nm[host][proto][port]["extrainfo"]  
    json_output['nmap_port_reason']=nm[host][proto][port]["reason"]  
    json_output['nmap_port_version']=nm[host][proto][port]["version"]  
    json_output['nmap_port_conf']=nm[host][proto][port]["conf"]  
    json_output['nmap_port_cpe']=nm[host][proto][port]["cpe"]  
    with open("/var/ossec/logs/active-responses.log", "a") as active_response_log:  
    active_response_log.write(json.dumps(json_output))  
    active_response_log.write("\n")  
    time.sleep(2)

### manager端

#### 检测规则

    
    
    <group name="linux,nmap,network_scan">  
    <rule id="200400" level="3">  
    <decoded_as>json</decoded_as>  
    <field name="nmap_host">\.+</field>  
    <field name="nmap_protocol">\.+</field>  
    <description>NMAP: Network Scan Host $(nmap_host)</description>  
    <options>no_full_log</options>  
    </rule>  
    </group>

### 扫描结果

    
    
    {  
    "timestamp":"2022-06-29T18:20:32.001+0000",  
    "rule":{  
    "level":3,  
    "description":"NMAP: Network Scan Host 192.168.252.222",  
    "id":"200400",  
    "firedtimes":55,  
    "mail":false,  
    "groups":[  
    "linux",  
    "nmap",  
    "netwprk_scan"  
    ]  
    },  
    "agent":{  
    "id":"017",  
    "name":"ubunutu2004vm",  
    "ip":"192.168.252.191"  
    },  
    "manager":{  
    "name":"ASHWZH01"  
    },  
    "id":"1645591052.115711751",  
    "decoder":{  
    "name":"json"  
    },  
    "data":{  
    "nmap_host":"192.168.252.222",  
    "nmap_protocol":"tcp",  
    "nmap_port":"443",  
    "nmap_hostname":"_gateway",  
    "nmap_hostname_type":"PTR",  
    "nmap_port_name":"https",  
    "nmap_port_state":"open",  
    "nmap_port_product":"OPNsense",  
    "nmap_port_reason":"syn-ack",  
    "nmap_port_conf":"10"  
    },  
    "location":"/var/ossec/logs/active-responses.log"  
    }

# 结语

赶KPI 写得有点仓促，敬请见谅，如果有疑问可以私信我哈～

 **漏洞悬赏计划：涂鸦智能安全响应中心（https://src.tuya.com）欢迎白帽子来探索。**

招聘内推计划：涵盖安全开发、安全测试、代码审计、安全合规等所有方面的岗位，简历投递[sec@tuya.com](mailto:sec@tuya.com)，
**请注明来自FreeBuf** 。

 **Pamela@涂鸦智能安全实验室**

  

