##  **写在前面**

 **这并不是什么高精尖的架构与技术。这只是我个人在工作中结合目前手头的资源进行了一些整合 。当然实现这些需求的方法有很多, 有钱的可以考虑Splunk,
没钱的有研发的团队的可以上Flink、Esper 。**

##  需求

由于攻防对抗的升级, 通过单一的数据源很难直接断言攻击是否成功。因此, 我们需要结合多个数据源进行安全事件的关联,
从中提炼出可靠性较高的安全告警进行人工排查。例如: 针对WebShell上传类的, 可以通过 **网络流量 + 终端** 进行关联; 针对Web攻击类,
可以通过 **WAF + NIDS** 的事件关联, 得到Bypass WAF 的安全告警。

##  解决思路

虽然Wazuh本身具备安全事件的关联能力, 但在传统的部署架构中, 通常是由Wazuh Agent将安全事件发送到Wazuh M anager **,**
通过Manager进行安全事件的关联告警。由于缺少了对数据进行ETL, 使得Wazuh Manager很难对异构数据进行关联。因此, 我们需要
通过Logstash实现对数据的标准化, 并将标准化后的数据通过Syslog的形式发送到Wazuh Manager, 从而进行异构数据的关联。

**坑点:**

> 1\. 本次改造采用了Syslog的形式将数据发送到Wazuh Manager端进行数据关联。由于Syslog 默认采用了UDP协议进行数据传输,
> 当数据发送过大时将会导致数据截断的报错。针对此问题, 需改用TCP的形式进行数据发送的方式。
>
> 2\. Wazuh Manager 部分告警缺少” **必要** “关联字段的现象。如: Wazuh syscheck告警事件,
> 默认不会携带srcip的字段, 对于此问题可以通过在Manager上编写一个预处理脚本来解决。

##  改造

> **改造前:** Suricata (Wazuh Agent) —(Agent: UDP 1514)—> Wazuh Manager
>
> **改造后:** 所有的标准化都由Logstash来进行, Filebeat只需要做’无脑‘转发即可。

**workflow**

**![](https://image.3001.net/images/20200316/1584336998_5e6f1066b6dbc.png!small)**

**Filebeat配置**

1\. filebeat.yaml

    
    
    #=========================== Filebeat inputs =============================
    filebeat.inputs:
    - type: log
      paths:
        - "/var/log/suricata/alert-*.json"
      fields_under_root: true
      fields: { application: suricata }
      json.keys_under_root: true
      json.overwrite_keys: true
      json.message_key: log
      tail_files: false
      scan_frequency: 1s
      harvester_buffer_size: 104857600
      backoff: 1s
      max_backoff: 10s
      close_timeout: 30m
      close_inactive: 10m
      clean_inactive: 72h
      ignore_older: 70h
      registry_file: /etc/filebeat/registry/wazuh/
    #================================ Processors ==================================
    processors:
    - drop_fields:
        fields: ["ecs.version", "agent.ephemeral_id", "agent.version", "agent.type", "agent.id", "agent.ephemeral_id", "input.type"]
    #================================ Outputs =====================================
    output.logstash:
      hosts: ["logstash:5010"]
      loadbalance: true
      worker: 4
      compression_level: 3
      bulk_max_size: 4096

 **Logstash配置**

1\. 00_input.conf

    
    
    input {
      beats {
        port => 5010
        codec => "json_lines"
        tags => ["beats"]
      }
    }

2\. 50_suricata.conf

    
    
    filter {
      if [application] == "suricata" {
        date {
          match => [ "timestamp", "ISO8601" ]
          target => "timestamp"
        }
      }
    }

3\. mapping.json

    
    
    {
        "common_mapping": {
            "src_ip": "srcip",
            "dest_ip": "dstip",
            "src_port": "srcport",
            "dest_port": "dstport"
        }
    }

4\. 70_normalized-suricata.conf

    
    
    filter {
      clone {
        clones => [ "siem_events" ]
      }
    }
    filter {
      if [type] == "siem_events" {
        mutate {
          remove_field => [ "application", "type", "agent", "@version", "@timestamp"]
          add_field => {
            "provider" => "Suricata"
            "product" => "Intrusion Detection System"
          }
        }
        ruby {
          init => "
            require 'json'
            mapping_json = File.read('/etc/logstash/mappings/wazuh/mapping.json')
            mapping = JSON.parse(mapping_json)
            @common_mapping = mapping['common_mapping']
          "
          code => "
            keys = event.to_hash.keys
            keys.each do |key|
                if @common_mapping.include? key then
                    value = event.get(key)
                    event.remove(key)
                    new_key = @common_mapping[key]
                    event.set(new_key, value)
                end
            end
            sensor = event.get('[host][name]')
            event.set('sensor', sensor)
          "
        }
      }
    }

5\. 99_output-elasticsearch.conf

    
    
    output {
      if [event_type] == "alert" {
        elasticsearch {
          cacert => "/etc/logstash/certs/ca/ca.crt"
          user => "elastic"
          password => "Hello World!"
          hosts => ["https://elasticsearch:9200"]
          index => "suricata-%{+YYYY.MM.dd}"
          template => "/etc/logstash/index-template.d/suricata-template.json"
          template_name => "suricata"
          template_overwrite => true
        }
      }
    }

6\. 99_output-wazuh.conf

    
    
    output {
      if [provider] == "Suricata" {
        syslog {
            host => "wazuh"
            protocol => "tcp"
            port => 514
            codec => "json"
            sourcehost => "logstash"
            appname => "NORMALIZED"
        }
        #stdout {
            #codec => rubydebug
        #}
      }
    }

**Wazuh配置**

1\. custom-syscheck.py

Wazuh Manager 新增预处理脚本对指定的安全事件进行预处理。如: syscheck事件增加srcip字段。

    
    
    import json
    import sys
    import time
    import os
    from datetime import datetime, timedelta, timezone
    
    # ossec.conf configuration:
    #  <integration>
    #      <name>custom-syscheck</name>
    #      <rule_id>554</rule_id>
    #      <group>syscheck</group>
    #      <alert_format>json</alert_format>
    #  </integration>
    
    # Global vars
    debug_enabled = False
    pwd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    json_alert = {}
    now = time.strftime("%a %b %d %H:%M:%S %Z %Y")
    wazuh_server = "192.168.199.97"
    
    # Set paths
    log_file = '{0}/logs/integrations.log'.format(pwd)
    syscheck_file = '{0}/logs/syscheck.json'.format(pwd)
    
    def iso8601(hours=8):
        td = timedelta(hours=hours)
        tz = timezone(td)
        return datetime.now(tz=tz).isoformat()
    
    def main(args):
        debug("# Starting")
    
        # Read args
        alert_file_location = args[1]
    
        debug("# File location")
        debug(alert_file_location)
    
        # Load alert. Parse JSON object.
        with open(alert_file_location) as alert_file:
            json_alert = json.load(alert_file)
        debug("# Processing alert")
        debug(json_alert)
    
        alert = normalized_data(json_alert)
        with open(syscheck_file, 'a') as f:
            msg = json.dumps(alert)
            f.write(msg + '\n')
    
    def debug(msg):
        if debug_enabled:
            msg = "{0}: {1}\n".format(now, msg)
            with open(log_file, "a") as f:
                f.write(msg)
    
    def normalized_data(alert):
        if alert['agent']['id'] == '000':
            alert['srcip'] = wazuh_server
        elif alert['agent'].get('ip'):
            alert['srcip'] = alert['agent']['ip']
            alert['dstip'] = alert['agent']['ip']
        alert['integration'] = 'custom-syscheck'
        alert['create_timestamp'] = iso8601()
        debug(alert)
        return(alert)
    
    if __name__ == "__main__":
        try:
            # Read arguments
            bad_arguments = False
            if len(sys.argv) >= 4:
                msg = '{0} {1} {2} {3} {4}'.format(now, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else '')
            else:
                msg = '{0} Wrong arguments'.format(now)
                bad_arguments = True
    
            # Logging the call
            with open(log_file, 'a') as f:
                f.write(msg + '\n')
    
            if bad_arguments:
                debug("# Exiting: Bad arguments.")
                sys.exit(1)
    
            # Main function
            main(sys.argv)
    
        except Exception as e:
            debug(str(e))
            raise

2\. ossec.conf

> a. 配置sysloig选用 **TCP** 协议;
>
> b. 加载预处理脚本;
>
> c. 加载脚本输出日志;
    
    
    <ossec_config>
      <remote>
        <connection>syslog</connection>
        <port>514</port>
        <protocol>tcp</protocol> <!-- udp(default)/tcp -->
        <allowed-ips>192.168.199.0/24</allowed-ips>
      </remote>
      
      <!-- Custom external Integration -->
      <integration>
        <name>custom-syscheck</name>
        <rule_id>554</rule_id>
        <group>syscheck</group>
        <alert_format>json</alert_format>
      </integration>
      
      <!-- Custom syscheck.json -->
      <localfile>
        <log_format>json</log_format>
        <location>/var/ossec/logs/syscheck.json</location>
      </localfile>
    </ossec_config>

3\. local_decoder_normalized.xml

    
    
    <!--    2020 Mar 03 02:53:39 logstash NORMALIZED[-]: {"timestamp":"2020-02-21T19:47:04.382300+0800","flow_id":1133835979634527,"in_iface":"wlp3s0","event_type":"alert","src_ip":"192.168.199.97","src_port":60022,"dest_ip":"192.168.199.162","dest_port":59143,"proto":"TCP","alert":{"action":"allowed","gid":1,"signature_id":123456,"rev":1,"signature":"LOCAL RULES XXX","severity":3}}
    -->
    
    <decoder name="nta_json">
        <prematch>NORMALIZED[-]: </prematch>
        <plugin_decoder offset="after_prematch">JSON_Decoder</plugin_decoder>
    </decoder>

4\. 0901-local_raw.xml

a. 默认引用的解码器为json, 这里需要修改为刚才新增的nta_json;

b. 通过overwrite=yes覆盖原始规则;

    
    
    <group name="suricata,">
    
        <!-- /var/ossec/ruleset/rules/0475-suricata_rules.xml -->
        <!-- Defind Suricata Rules -->
        <!-- ID: 86600 - 86699 -->
    
        <rule id="86600" level="0" overwrite="yes">
            <decoded_as>nta_json</decoded_as>
            <field name="timestamp">\.+</field>
            <field name="event_type">\.+</field>
            <description>Suricata messages.</description>
            <options>no_full_log</options>
        </rule>
    
    </group>

5\. 0905-local_syscheck.xml

为预处理脚本生成的日志进行解析

    
    
    <group name="syscheck,">
        <rule id="187100" level="7">
            <decoded_as>json</decoded_as>
            <field name="integration">custom-syscheck</field>
            <description>syscheck integration messages.</description>
            <options>no_full_log</options>
        </rule>
    </group>

6\. 9999-local_composite.xml

    
    
    <group name="local,composite,">
    
        <!-- Local Composite Rules Range ID: 200000 - 205000 -->
    
        <rule id="200000" level="15" frequency="2" timeframe="600">
            <if_matched_sid>101000</if_matched_sid> <!-- 文件上传类规则 or 检测WebShell上传类规则 -->
            <if_sid>187100</if_sid>
            <same_source_ip />	<!-- 通过IP进行关联 -->
            <description>Phase 3: 检测到服务器:$(srcip), 被上传WebShell.</description>
            <options>no_full_log</options>
        </rule>
    
        <rule id="200001" level="12" frequency="2" timeframe="600">
            <if_matched_sid>88801</if_matched_sid> <!-- WAF安全事件 -->
            <if_group>ids</if_group>
            <same_source_ip />
            <description>Phase 3: Alarm - Same ip Bypass WAF of within 600 seconds. $(srcip) -> $(http.hostname) -> $(alert.signature) -> $(alert.signature_id).</description>
            <options>no_full_log</options>
        </rule>
      
    </group>

##  总结

> 1\. 对于 **WebShell** 关联检测,目前采用的是同源IP以及时序的关联,
> 最为靠谱的应该是通过Hash的比对。这里要吐槽一下Suricata默认的fileinfo, 没办法自定义输出,
> 只要开启可被还原的协议都会输出fileinfo的事件。正因如此, 数据量一大Wazuh的引擎压力会很大。我尝试通过 **Lua**
> 来自定义一个文件审计类的事件, 貌似也同样没办法区分协议更别说针对http过滤条件进行自定义的过滤输出了。
>
> 2\. 由于关联规则本身是通过底层多个安全事件进行维度的关联提升告警的 **可靠性** 。因此,
> 底层安全事件不够准确同样会让上层的关联规则带来大量误报。对于底层安全事件的优化也是需要持续进行的。
>
> 3\. **Wazuh v3.11.4** 采用Syslog接收大日志时, 会触发memory violation导致ossec-> remoted进程重启, 该问题已向社区反馈下个版本中会解决。

##  参考

> [**How to forward Android syslog to Wazuh**](https://wazuh.com/blog/how-to-> forward-android-syslog-to-wazuh/)
>
> **[How to configure Rsyslog client to send events to
> Wazuh](https://wazuh.com/blog/how-to-configure-rsyslog-client-to-send-> events-to-wazuh/)**
>
> ****[How to integrate external software using
> Integrator](https://wazuh.com/blog/how-to-integrate-external-software-using-> integrator/)****

 ***本文原创作者：Shell.，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

