# HIDS产品形态

HIDS全称是Host-based Intrusion Detection System，即基于主机型入侵检测系统。hids组成架构一般分为：

agent：本质是安装在主机上的一个软件，通过持续监控主机中数以万计的安全指标，将结果推送到管理端的分析引擎进行快速威胁检测分析。

管理端：根据agent上报的事件进行威胁分析、告警，管理每台agent的配置下发

报表平台：可视化展示规则分析的结果

# 开源主机安全解决方案

纵观免费开源的hids，选择并不多，笔者对以下三款开源hids做了简单对比：

  
| OSquery| elkeid| wazuh  
---|---|---|---  
基础信息|

  

1.具备agent

  

2.官方提供部分规则

|

  

1.具备agent

  

2.使用kafka接收数据

  

3.具备规则分析中心，无规则

|

  

1.具备agent

  

2.具备管理端

  

3.具备规则分析中心，有规则

  

4.具备报表功能  
  
运维管理|

  

1.有心跳和状态

  

2.支持命令执行

|

  

1.支持批量版本更新

  

2.支持批量配置更新

  

3.支持批量重启

  

4.分布式：社区版不支持分布式，得花钱买商用版，单个节点能力看服务器配置（一个server大概3000个点）

|

  

1.支持批量版本更新

  

2.支持批量配置更新

  

3.支持批量重启

  

4.支持执行本地命令，不支持远程下载脚本执行

  

5.支持远程获取指定文件

  

6.有心跳和状态上报。

  

7.支持多节点分布式部署，使用nginx对woker实现负载均衡 。配置也支持多管理端，单个管理端支持600-1000个Agent。  
  
二次开发|

  

1.agent需要开发，来支持批量运维能力

  

2.需要开发管理端，来支持批量运维能力

3.需要开发规则分析平台，增加各种规则

4.需要开发报表平台

|

  

1.需要开发管理端

  

2.需要开发规则分析平台，增加各种规则

3.需要开发报表平台

|

  

1.增删或修改分析规则，基本不需要开发人员

  

2.新增关联分析需要写规则  
  
优势|

  

1.规则定义简单，类似sql查询可以进行规则定制

  

2.设置好规则调用频率后，资源消耗相对较小

  

3.对于突发的漏洞，可以自定义agent规则定位是否存在可利用风险的主机

| 基于内核态的数据采集，数据准确性很高，性能损耗较小|

  

1.有完备的现成规则库，后期规则维护也相对简单

  

2.支持在线病毒库实时上传分析

  

3.kibana可视化界面

  

4.支持分布式部署

  

5.对于突发的漏洞，可以自定义agent规则定位是否存在可利用风险的主机。

6.自带多个场景威胁检测  
  
劣势|

  

1.目前只能基于sql语句规则进行规则制定，且所有规则需要可以仿造wazuh的进行转换

  

2.没有管理端，须定制开发

  

3.基于用户态数据采集的检测，存在被绕过的风险

|

  

1.目前市面上的通用案例较少，且开源部分只有底层的server和agent通信部分，agent会去采集何种信息，以及引擎hub，但是规则并未完全公开，且规则维护难度较大

  

2.开源版不支持分布式部署

  

3.无管理端

  

4.后续引擎的维护和规则的维护难度大

  

5.基于内核态的检测，假如出现问题，对系统影响较大

|

  

1.基于用户态的数据采集检测，存在被绕过的风险

  

2.如果agent的规则太多，可能存在对主机性能损耗较大的影响

  

3.规则需要优化，误报较多  
  
 **综合对比，我们最终选择wazuh。**

# Wazuh架构

Wazuh
架构基于运行在受监控端点的agent，并将安全数据转发到服务端。此外，还支持无agent设备(如防火墙、交换机、路由器、接入点等)，可以通过Syslog、SSH或者他们本身的API来发送日志。中央服务器对输入的信息进行解码和分析，并将结果传递给ElasticSearch集群进行索引和存储。

![1657935745_62d2178169f7182157ae8.png!small?1657935746073](https://image.3001.net/images/20220716/1657935745_62d2178169f7182157ae8.png!small?1657935746073)

更多详情可以查看[官方文档](https://documentation.wazuh.com/current/getting-started/architecture.html)。

## 部署

如果服务器数量达到1万台以上，服务端建议部署集群，三节点以上。agent建议分批次安装，如果一万台服务器通过安装agent，同时向服务端注册并上报状态，可能会造成网络拥堵，虽说出现这种情况可能性较低，但为了不影响业务，还是小心驶得万年船。

agent的策略分为本地和服务端统一管理，为了管理方便，通过服务端每个组下的agent.conf进行配置。因此在安装agent时，建议将/var/ossec/etc/ossec.conf配置文件修改成：

    
    
    <ossec_config>
      <client>
        <server>
          <address>xxx.com</address>
          <port>1514</port>
          <protocol>tcp</protocol>
        </server>
        <config-profile>centos, centos7, centos7.9</config-profile>
        <notify_time>10</notify_time>
        <time-reconnect>60</time-reconnect>
        <auto_restart>yes</auto_restart>
        <crypto_method>aes</crypto_method>
      </client>
      
      <client_buffer>
        <!-- Agent buffer options -->
        <disabled>no</disabled>
        <queue_size>5000</queue_size>
        <events_per_second>500</events_per_second>
      </client_buffer>
    </ossec_config>

这样做好处是agent只向服务端注册agent，没有任何策略，避免策略全开导致兼容性问题，当agent运行稳定没有异常后再从服务端逐个策略下发。若本地和远程都配置了同一个模块的策略，以最新下发的为准。连接服务端建议使用域名，或通过nginx做负载。

# 安全能力

wazuh主要提供以下能力：

  * 日志文件收集
  * 系统资产清单
  * 文件完整性监控
  * 恶意文件检测
  * SCA
  * 主动防御
  * 漏洞检测
  * 命令监控
  * Rootcheck

我们目前只开启了日志文件收集、文件完整性监控、命令监控，系统资产清单，操作系统包括CentOS6-8.

### 1)日志分析

日志分析工作原理如下：

![1657935992_62d2187813776a8e3fae4.png!small?1657935992649](https://image.3001.net/images/20220716/1657935992_62d2187813776a8e3fae4.png!small?1657935992649)

默认收集的日志文件包括/var/log/audit/audit.log、/var/ossec/logs/active-responses.log、/var/log/messages、/var/log/secure、/var/log/maillog，也可以自定义添加其他类型日志文件，如Nginx、Tomcat的access.log、error.log。

  * /var/log/audit/audit.log，audit审计日志，Linux系统默认安装audit
  * /var/ossec/logs/active-responses.log，wazuh主动防御日志
  * /var/log/messages，内核及公共消息日志
  * /var/log/secure，用户验证相关日志
  * /var/log/maillog，邮件系统日志

从系统日志作用可以得知应用到的安全场景有暴力破解、用户创建等。如需开启该策略，可在manager的agent.conf文件加入以下配置文件。

    
    
    <ossec_config>
      ...
      <localfile>
        <log_format>audit</log_format>
        <location>/var/log/audit/audit.log</location>
      </localfile>
    
      <localfile>
        <log_format>syslog</log_format>
        <location>/var/ossec/logs/active-responses.log</location>
      </localfile>
    
      <localfile>
        <log_format>syslog</log_format>
        <location>/var/log/messages</location>
      </localfile>
    
      <localfile>
        <log_format>syslog</log_format>
        <location>/var/log/secure</location>
      </localfile>
    
      <localfile>
        <log_format>syslog</log_format>
        <location>/var/log/maillog</location>
      </localfile>
    
    </ossec_config>

修改爆破频率。自定义规则路径：/var/ossec/etc/rules/xxx.xml或wazuh可视化界面编辑。

    
    
    <group name="brute force">
      ...
      <rule id="5720" level="10" frequency="10" timeframe="60" overwrite="yes">
        <if_matched_sid>5716</if_matched_sid>
        <same_source_ip />
        <description>sshd: Multiple authentication failures.</description>
        <mitre>
          <id>T1110</id>
        </mitre>
        <group>authentication_failures,pci_dss_10.2.4,pci_dss_10.2.5,pci_dss_11.4,gpg13_7.1,gdpr_IV_35.7.d,gdpr_IV_32.2,hipaa_164.312.b,nist_800_53_AU.14,nist_800_53_AC.7,nist_800_53_SI.4,tsc_CC6.1,tsc_CC6.8,tsc_CC7.2,tsc_CC7.3,</group>
      </rule>
    </group>  

在一定时间内登录失败次数达到设置的频率时，就会触发告警。

### 2) 文件完整性监控(FIM)

FIM工作原理交互图如下：

![1657936250_62d2197a80d70ef94f723.png!small?1657936251293](https://image.3001.net/images/20220716/1657936250_62d2197a80d70ef94f723.png!small?1657936251293)

FIM 模块位于 Wazuh agent中，它定期扫描系统并将受监控文件和 Windows 注册表项的校验和和属性存储在本地 FIM
数据库中。该模块通过将新文件的校验和与旧校验和进行比较来查找修改。所有检测到的更改都会报告给 Wazuh Manager。

因为是将监控文件存在本地，一旦受监控文件很多时，agent的/var/ossec/queue目录会占用较多的磁盘空间，安装agent无法指定安装路径，因此可以使用软链接的方式转移agent安装路径到存储空间较大的分区。如

    
    
    systemctl stop wazuh-agent.service
    mkdir -p /data/wazuh
    mv /var/ossec /data/wazuh
    ln -sf /data/wazuh/ossec /var
    systemctl start wazuh-agent.service

#### 使用场景1——主机账号监控

按照安全管理规范，服务器账号通过账号管理系统进行账号管理，不允许通过ssh登录生产服务器创建/删除账号。为了防止有人擅自创建账号，因此需要监控异常账号。实现监控账号变化有两种方式：

  1. 配置系统日志收集。当创建账号时，会在/var/log/secure文件中打印相关日志，wazuh也对该类日志做了解析，自动提取新建账号的username、uid、gid等字段
  2. 监控/etc/passwd文件。新建账号最终会写入到/etc/passwd，因此监控该文件也能审计到账号的变化情况，但需要后期对变化的文件内容做数据处理。

我们在实施该策略时，发现有些服务器新建账号后/var/log/secure中没有打印新建账号的日志，排查了一段时间后没有解决该问题，后来唯有使用监控/etc/passwd的方案。

在wazuh manager控制台agent.conf加上以下配置文件

    
    
    <syscheck>
      <directories check_all="yes" realtime="yes" report_changes="yes">/etc/passwd</directories>
    </syscheck>

  *  **realtime** , 实时扫描监控目录或文件，也可以配置成定时扫描。
  *  **report_changes** , 监控文件修改内容，仅在文件修改/新增模式的情况才生效。开启 **report_changes** 后，agent就会把受监控文件保存到本地数据库
  *  **who-data** ， **who-data** 需要依赖audit，一旦配置了 **who-data，** 会自动替代 **realtime，** 除此之外， **who-data** 还会增加audit字段，如触发告警事件的进程、路径，生效用户、登录用户等。

由于wazuh无法识别新建的账号是否违规，因此需要跟正常创建账号的账号系统做关联分析，如下流程图

![1657936449_62d21a41a8c5895694bb9.png!small?1657936450247](https://image.3001.net/images/20220716/1657936449_62d21a41a8c5895694bb9.png!small?1657936450247)

wazuh使用elasticsearch作为存储介质，可以通过DSL定时查询/etc/passwd文件是否有变化，并对查询得到的结果做数据处理，并将异常事件发送到其他告警系统，如SOC上。

#### 使用场景2——重要系统文件监控

为了防止重要的系统文件被恶意篡改，因此也需要进行文件完整性监控，实现方式和场景1相类似，主要区别在于当存在多个系统、多个不同路径时，使用DSL查询数据就比较难处理，针对这种场景，可以对这些主机打上标签，基于agent标签，即可在使用DSL查询时根据标签进行搜索。在agent.conf加入以下配置文件：

    
    
    <agent_config>
     ...
      <labels>
          <label key="fim.syscheck">vip-system</label>
      </labels>
    </agent_config>

### 3)命令监控

工作原理：

![1657936527_62d21a8f103c8dcc52fc6.png!small?1657936527849](https://image.3001.net/images/20220716/1657936527_62d21a8f103c8dcc52fc6.png!small?1657936527849)

从上图可以知道检测原理是manager定时远程到agent执行命令，根据命令输出匹配规则是否存在异常。这个功能可用于检测反弹shell

首先需要在agent的/var/ossec/etc/local_internal_options.conf追加以下命令：

    
    
    logcollector.remote_commands=1

在manager的agent.conf加入配置：

    
    
    <agent_config>
      ...
        <localfile>
            <log_format>command</log_format>
            <command>ps -eo user,cmd,pid</command>
            <frequency>120</frequency>
        </localfile>
     </agent_config>

在manager的 **/var/ossec/etc/rules/local_rules.xml** 文件中添加自定义规则

    
    
    <rule id="100011" level="0">
      <if_sid>530</if_sid>
      <match>^ossec: output: 'ps -eo user,cmd,pid'</match>
      <description>Important process not running.</description>
      <group>process_monitor,</group>
    </rule>
    
    <rule id="100012" level="15">
      <if_sid>100011</if_sid>
      <match>bash -i|nc -e /bin/bash|python -c 'import sys,socket,os,pty;s=socket.socket();|exec 5<>/dev/tcp</match>
      <description>反弹shell测试</description>
      <group>process_monitor,</group>
     </rule>

检测结果

![1657936636_62d21afccfc1f9e34a50c.png!small?1657936637465](https://image.3001.net/images/20220716/1657936636_62d21afccfc1f9e34a50c.png!small?1657936637465)

### 4) 系统资产清单

agent 负责采集系统资产并将其存储到服务端的SQLite数据库中，可采集的数据有

  * 硬件
  * 操作系统
  * 网络接口
  * 软件包
  * 端口
  * 进程
  * Windows更新

agent启动后，会定时扫描已经定义的采集目标数据，并将采集的数据转发给服务端。可在服务器端的agent.conf中添加以下配置

    
    
    <ossec_config>
      ...
      <!-- System inventory -->
      <wodle name="syscollector">
        <disabled>no</disabled>
        <interval>1h</interval>
        <scan_on_start>yes</scan_on_start>
        <hardware>yes</hardware>
        <os>yes</os>
        <network>yes</network>
        <packages>yes</packages>
        <ports all="no">yes</ports>
        <processes>yes</processes>
      
        <!-- Database synchronization settings -->
        <synchronization>
          <max_eps>10</max_eps>
        </synchronization>
      </wodle>
    </ossec_config>  

开启系统资产清单的作用是用途统计服务器的基础数据，如通过wazuh
api接口来统计服务器中的内核版本，当某台服务器被入侵，对外连接C2服务器时，就可以用这些数据快速排查其他服务器是否被入侵。

### 4) Rootcheck

该模块运行过一段时间，由于检查隐藏端口需要使用netstat命令，占用较多的CPU资源，就被迫下架。

隐藏端口检查原理： **Rootcheck使用**
bind()检查系统中的每个端口。如果它无法绑定到某个端口并且该端口不在netstat输出中，则可能存在恶意软件。

    
    
    <rootcheck>
        <disabled>no</disabled>
        <check_files>yes</check_files>
        <check_trojans>yes</check_trojans>
        <check_dev>yes</check_dev>
        <check_sys>yes</check_sys>
        <check_pids>yes</check_pids>
        <check_ports>yes</check_ports>
        <check_if>yes</check_if>
    
        <!-- Frequency that rootcheck is executed - every 12 hours -->
        <frequency>43200</frequency>
    
        <rootkit_files>etc/shared/rootkit_files.txt</rootkit_files>
        <rootkit_trojans>etc/shared/rootkit_trojans.txt</rootkit_trojans>
    
        <skip_nfs>yes</skip_nfs>
      </rootcheck>

以下策略我目前只在测试环境运行过，因此只是简单介绍一下，有需要用到的同学可以查看[官方文档](https://documentation.wazuh.com/current/user-manual/capabilities/vulnerability-detection/index.html)

### 5)漏洞检测

漏洞检测功能需要在manager上配置，其运行原理是通过收集agent的安装包名称以及版本来匹配漏洞库，但有个缺点是只能全局开，不能基于组或单个agent进行检测。我们在测试时发现很多centos的系统组件漏洞数量多，且利用难度大，运营比较困难，因此没有开启该策略。

### 6)恶意文件检测

wazuh可以联动virustotal扫描受监控的文件是否存在恶意文件，该模块也只能是在manager上配置，并且全局开启，无法对某个组或主机生效，使用该模块需要先开启FIM
，virustotal扫描路径就是FIM监控路径。virustotal每天免费请求1500次，因此当受监控路径文件过多时，就会扫描失败。

### 7)主动防御

主动防御就是当产生的告警日志匹配上rule id、安全等级时就会执行指定的命令或脚本，wazuh自带了一部分脚本：

Linux

![1657936864_62d21be0a9cfc2165de5f.png!small?1657936865433](https://image.3001.net/images/20220716/1657936864_62d21be0a9cfc2165de5f.png!small?1657936865433)

Windows：

![1657937819_62d21f9b911ab17d1637b.png!small?1657937820456](https://image.3001.net/images/20220716/1657937819_62d21f9b911ab17d1637b.png!small?1657937820456)

## 总结

wazuh在全网服务器稳定运行了半年多的时间，总体来说还是一款挺不错的产品，最重要的是免费使用，非常适合预算有限的企业。wazuh社区也十分的活跃，在社区提问基本都会有开发者回复，回复速度也十分及时，与wazuh的开发者沟通交流也是一件蛮不错的事情。但相对于国内商业HIDS来说，缺少规则的维护，需要投入较多的人力成本来维护规则，也没有本地查杀功能，没法及时发现webshell、木马等恶意文件。

