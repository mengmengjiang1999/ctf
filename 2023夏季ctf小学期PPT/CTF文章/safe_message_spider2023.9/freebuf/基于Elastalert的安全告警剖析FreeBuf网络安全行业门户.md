***本文作者：bigface，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  

 **[elastalert](https://github.com/Yelp/elastalert)
是一款基于elasticsearch的开源告警产品（[官方说明文档](http://elastalert.readthedocs.io/en/latest/index.html)）。相信许多人都会使用ELK做日志收集系统，但是产生一个基于日志的“优秀”的安全告警确是一个难题。告警规则难编写，告警规则难管理等。本文是作者探索的安全告警的一些思路，希望能帮助到有需要的人。**

 **本人对ELK告警处理思路：**

elastalert 通过post的告警模式，post一个告警数据包到服务端，通过服务端匹配需要告警的对象，告警的方式，最终将安全告警发出。

告警对象（企业人员） 怎么来？ 来源调用钉钉API、CMDB、LDAP。

告警方式 怎么选择？根据告警级别、告警来源（wazuh、驭龙HIDS、elastalert规则）采用不同的告警方式。

![基于elastalert的安全告警剖析](https://image.3001.net/images/20180308/15205034379251.png!small)  

## 环境说明

Elastic Stack v6.2.2 （适用于6.0+）  
Elastalert v0.1.29

## elastalert 源码部署

下载 `elastalert` 源码

    
    
    git clone https://github.com/Yelp/elastalert.git
    

安装依赖

    
    
    pip install -r requirements.txt
    pip install "elasticsearch>=6.0.0"
    

创建elastalert索引（Index）&映射（Mapping）

    
    
    python elastalert/create_index.py --host localhost --port 9200 --index elastalert
    

创建elastalert的配置文件 `config.yaml` ：

    
    
    # 告警规则存放的文件夹
    rules_folder: myrules
    
    # 每2分钟查询一次elasticsearch
    run_every:
      minutes: 2
    
    # 查询时间范围5分钟
    buffer_time:
      minutes: 5
    
    # 连接elasticsearch配置
    es_host: localhost
    es_port: 9200
    
    # elasticsearch认证，如果未使用可注释
    es_username: kibana
    es_password: kibana
    
    # elastalert状态索引
    writeback_index: elastalert
    

开启elastalert

    
    
    python elastalert/elastalert.py --config config.yaml
    

## elastalert规则类型

官方规则类型描述并不是太清晰，以下给出alert方式为post的json数据，便于后续大家速查速写。

以下的规则类型均使用以下文档样本作触发告警：

    
    
        doc = {
            "@timestamp": get_now(),
            "codec": "nodejs",
            "tags": "31",
            "level": "high",
            "server": "nginx",
            "status": "anystatus",
            "message": ">>> [ xxx ]: valid id error ."
        }
    

> elastalert索引中，`hits`表示规则命中条数；`matches`表示规则命中条数，并且匹配规则触发告警数量。

### any类型

说明：任何规则都会匹配， 查询返回的每个命中将生成一个警报。

规则：当匹配status字段为`anystatus`，触发告警。

    
    
    # rule名称
    name: any_rule
    
    # 规则类型
    type: any
    
    # 监控索引
    index: testalert
    
    # 监控时间1分钟内
    timeframe:
        minutes: 1
    
    # Elastic DSL语法
    filter:
    - term:
        status: "anystatus"
    
    # 告警方式
    alert: post
    # 服务端接口
    http_post_url: "http://localhost:8088/alertapi"
    http_post_static_payload:
        # 添加到post包中的数据，规则名称
        rule_name: any_rule
        # 添加到post包中的数据，告警级别
        rule_level: medium
    

post结果：

    
    
    {
        "status": "anystatus",
        "_type": "mydata",
        "level": "high",
        "num_hits": 5,
        "@timestamp": "2018-01-31T02:26:52.268477Z",
        "rule_level": "medium",
        "server": "nginx",
        "rule_name": "any_rule",
        "_index": "testalert",
        "num_matches": 5,
        "message": ">>> [ xxx ]: valid id error .",
        "_id": "AWFKCd4a5xzN_sFQhZgO",
        "codec": "nodejs",
        "tags": "31"
    }
    

### blacklist类型

说明：黑名单规则将检查黑名单中的某个字段，如果它在黑名单中则匹配。

规则：当字段status匹配到关键字hacker、huahua，触发告警

    
    
    name: blacklist_rule
    type: blacklist
    index: testalert
    
    timeframe:
        minutes: 1
    
    compare_key: status
    
    blacklist:
        - "hacker"
        - "huahua"
    
    alert: post
    http_post_url: "http://localhost:8088/alertapi"
    http_post_static_payload:
        rule_name: blacklist_rule
        rule_level: medium
    

> 若关键字在文件中，可用 `- "!file /path/to/file"`，目测关键字不支持正则（未测过）。

post结果：

    
    
    {
        "status": "huahua",
        "_type": "mydata",
        "level": "high",
        "num_hits": 2,
        "@timestamp": "2018-01-31T02:37:46.071850Z",
        "rule_level": "medium",
        "server": "nginx",
        "rule_name": "blacklist_rule",
        "_index": "testalert",
        "num_matches": 1,
        "message": ">>> [ xxx ]: valid id error .",
        "_id": "AWFKE9gM5xzN_sFQhZg2",
        "codec": "nodejs",
        "tags": "31"
    }
    

### whitelist类型

说明：与黑名单类似，此规则将某个字段与白名单进行比较，如果列表中不包含该字词，则匹配。

### change类型

说明：此规则将监视某个字段，并在该字段更改时进行匹配，该领域必须相对于最后一个事件发生相同的变化。

规则：当server字段值相同，codec字段值不同时，触发告警。

    
    
    name: change_rule
    type: change
    index: testalert
    
    timeframe:
        minutes: 1
    
    compare_key: codec
    
    ignore_null: true
    
    query_key: server
    
    alert: post
    http_post_url: "http://localhost:8088/alertapi"
    http_post_static_payload:
        rule_name: change_rule
        rule_level: medium
    

字段解析：

`compare_key`：与上一条记录做对比的字段

`query_key`：与上一条记录相同的字段

`ignore_null`：忽略记录不存在compare_key字段的情况

post结果：

    
    
    {
        "status": "up",
        "_type": "mydata",
        "_id": "AWFKIgZA5xzN_sFQhZh5",
        "tags": "31",
        "num_hits": 4,
        "@timestamp": "2018-01-31T02:53:15.413240Z",
        "rule_level": "medium",
        "old_value": [
            "nodejs"
        ],
        "server": "nginx",
        "rule_name": "change_rule",
        "_index": "testalert",
        "new_value": [
            "java"
        ],
        "num_matches": 1,
        "message": ">>> [ xxx ]: valid id error .",
        "level": "high",
        "codec": "java"
    }
    

### frequency类型

说明：当给定时间范围内至少有一定数量的事件时，此规则匹配。 这可以按照每个query_key来计数。

规则：当字段status匹配到关键字frequency超过3次（包括3次），触发告警

    
    
    name: frequency_rule
    type: frequency
    index: testalert
    
    num_events: 3
    
    timeframe:
        minutes: 1
    
    filter:
    - term:
        status: "frequency"
    
    alert: post
    http_post_url: "http://localhost:8088/alertapi"
    http_post_static_payload:
        rule_name: frequency_rule
        rule_level: medium
    

post结果：

    
    
    {
        "status": "frequency",
        "_type": "mydata",
        "level": "high",
        "num_hits": 3,
        "@timestamp": "2018-01-31T03:28:00.793290Z",
        "rule_level": "medium",
        "server": "nginx",
        "rule_name": "frequency_rule",
        "_index": "testalert",
        "num_matches": 1,
        "message": ">>> [ xxx ]: valid id error .",
        "_id": "AWFKQdg_5xzN_sFQhZjW",
        "codec": "java",
        "tags": "31"
    }
    

### spike类型

说明：当某个时间段内的事件量比上一个时间段的spike_height时间大或小时，这个规则是匹配的。它使用两个滑动窗口来比较事件的当前和参考频率。
我们将这两个窗口称为“参考”和“当前”。

规则：当前窗口数据量为3，当前窗口超过参考窗口数据量次数1次，触发告警。

    
    
    name: spike_rule
    type: spike
    index: testalert
    
    timeframe:
        minutes: 1
    
    threshold_cur: 3
    
    spike_height: 1
    
    spike_type: "up"
    
    filter:
    - term:
        status: "spike"
    
    alert: post
    http_post_url: "http://localhost:8088/alertapi"
    http_post_static_payload:
        rule_name: spike_rule
        rule_level: medium
    

字段解析：

`threshold_cur`：当前窗口初始值

`spike_height`：当前窗口数据量连续比参考窗口数据量高(/低)的次数

`spike_type`：高或低

post结果：

    
    
    {
        "status": "spike",
        "_type": "mydata",
        "_id": "AWFLMbye5xzN_sFQhZlk",
        "tags": "31",
        "num_hits": 13,
        "@timestamp": "2018-01-31T07:50:02.382708Z",
        "rule_level": "medium",
        "server": "nginx",
        "rule_name": "spike_rule",
        "_index": "testalert",
        "spike_count": 8,
        "reference_count": 0,
        "num_matches": 1,
        "message": ">>> [ xxx ]: valid id error .",
        "level": "high",
        "codec": "java"
    }
    

### flatline类型

说明：当一个时间段内的事件总数低于一个给定的阈值时，匹配规则。

规则：当信息量低于3条时，触发告警。

    
    
    name: flatline_rule
    type: flatline
    index: testalert
    
    timeframe:
        minutes: 1
    
    threshold: 3
    
    alert: post
    http_post_url: "http://localhost:8088/alertapi"
    http_post_static_payload:
        rule_name: flatline_rule
        rule_level: medium
    

post结果：

    
    
    {
        "count": 1,
        "num_hits": 1,
        "@timestamp": "2018-01-31T09:02:35.720517Z",
        "rule_level": "medium",
        "rule_name": "flatline_rule",
        "key": "all",
        "num_matches": 1
    }
    

### cardinality类型

说明：当一个时间范围内的特定字段的唯一值的总数高于或低于阈值时，该规则匹配

规则：1分钟内，level的唯一数量超过2个(不包括2个)，触发告警。

    
    
    name: test_rule
    index: testalert
    type: cardinality
    
    timeframe:
        minutes: 1
    
    cardinality_field: level
    
    max_cardinality: 2
    
    alert: post
    http_post_url: "http://localhost:8088/api/alert"
    http_post_static_payload:
        rule_name: test_rule
        rule_level: medium
    

post结果：

    
    
    {
        "status": "cardinality",
        "_type": "mydata",
        "level": "info",
        "num_hits": 3,
        "@timestamp": "2018-01-31T09:17:02.276937Z",
        "rule_level": "medium",
        "server": "nginx",
        "rule_name": "cardinality_rule",
        "_index": "testalert",
        "num_matches": 1,
        "message": ">>> [ xxx ]: valid id error .",
        "_id": "AWFLgWKw5xzN_sFQhZvg",
        "codec": "java",
        "tags": "31"
    }
    

### percentage match类型

说明：当计算窗口内的匹配桶中的文档的百分比高于或低于阈值时，此规则匹配。计算窗口默认为buffer_time。

规则：当level字段未high，时间窗口内日志量高于前一个时间窗口95%，触发告警。（未完整测试）

    
    
    name: percentage_match_rule
    type: percentage_match
    index: testalert
    
    # description: "test description"
    
    buffer_time:
        minutes: 1
    
    max_percentage: 95
    
    match_bucket_filter:
    - term:
        level: high 
    
    doc_type: mydata
    
    alert: post
    http_post_url: "http://localhost:8088/alertapi"
    http_post_static_payload:
        rule_name: percentage_match_rule
        rule_level: medium
    

post结果：

    
    
    {
        "num_hits": 10,
        "@timestamp": "2018-01-31T09:39:05.199394Z",
        "rule_level": "medium",
        "rule_name": "percentage_match_rule",
        "num_matches": 1,
        "percentage": 100.0
    }
    

## 告警方式

elastalert内置的告警方式并不太使用与国人的习惯，所以这块建议自行写服务端重新定义。

> 为什么不在elastalert源码alerts.py中直接加类，而通过post出来自己做服务端接收告警？ 主要考虑到elastalert项目更新。

目前比较常用的告警模式有：钉钉、微信、邮件、短信。

首先设计好的告警内容，于是我们可以创建好4种告警类型，并逐步实现功能。

![基于elastalert的安全告警剖析](https://image.3001.net/images/20180308/15205035843711.jpg!small)  

### 钉钉告警

目前钉钉有两种告警方法，一种是获得管理员token，可以调用企业通知产生告警，这种方式的好处是可以通知到企业中对应的人，对应部门中所有人等。

这里分享一下实现的大致思路：

    
    
        def send(self, post_alert_content):
            # 告警内容
            msgcontent = {
                "title": post_alert_content["name"], 
                "text": "## 规则：{0} \n ## 级别：{1} \n ## 时间：{2} \n ## 内容：{3}".format(
                    post_alert_content["name"],post_alert_content["level"],post_alert_content["create_at"],post_alert_content["content"]
                ) 
            }
            
            # 获取需要通知的用户列表
            userid_list = users.getDingDingUserIdByName(post_alert_content["contact_users"])
            msgtype = "markdown"
            agent_id = DD_AgentId
            dept_id_list = None
    
            try:
                msgcontent = json.dumps(msgcontent)
            except JSONDecodeError:
                pass
    
            args = locals().copy()
            payload = {}
    
            for k, v in args.items():
                if k in ('msgtype', 'agent_id', 'msgcontent', 'userid_list', 'dept_id_list'):
                    if v is not None:
                        payload.update({k: v})
    
            # 发送钉钉告警信息
            resp = self.callDingDingWebApi(self.access_token, 'dingtalk.corp.message.corpconversation.asyncsend', **payload)
    
            if "error_response" in resp.json().keys():
                self.getAccessToken()
                self.send(post_alert_content)
    

效果：告警出现在企业通知中。

![基于elastalert的安全告警剖析](https://image.3001.net/images/20180308/15205036207575.png!small)  

另一种则是通过钉钉创建群，添加钉钉机器人告警。

    
    
        def sendByRobot(self, post_alert_content):
            DD_level = post_alert_content.get("level", "")
            DD_name = post_alert_content.get("name", "")
            DD_content = post_alert_content.get("content", "")
            DD_url = post_alert_content.get("url", "")
    
            headers = {"Content-Type": "application/json"}
            message = {
                "msgtype": "markdown", 
                "markdown": {
                    "title": "【" + DD_level + "】" + DD_name,
                    "text": "### 时间：" + datetime.now().strftime("%Y-%m-%d %X") + "\n" \
                            "### 规则：" +  "【" + DD_level + "】" + DD_name + "\n" \
                            "### 内容：" + DD_content + "\n"
                }
            }
    
            r = requests.post(url=DD_url, headers=headers, data=json.dumps(message))
            return True
    

### 短信告警

短息告警的具体实现与企业采用的短信通道有关，但是方式基本相似。

    
    
        def send(self, post_alert_content):
            """
                param:
                    phone @string
                    raw_content @string
                
                return:
                    @bool
            """
            self.params['phone'] = post_alert_content["users_phone"]
            self.params['report'] = True
            content = self.getContent(post_alert_content)
            self.params['msg'] = urllib.quote(content)
    
            response = requests.post(SMS_SEND_MSG_URL, json=self.params)
            rv = response.json()
    

### 微信告警

微信告警，实现的大致思路：

    
    
        def send(self, users, subject, content):
            """
                params:
                    users @string
                    subject @string
                    content @string
    
                return:
                    @bool
            """
    
            # 微信API
            post_url = WECHAT_MSG_URL + self.token
    
            for user in users.split(","):
                message = {
                     # 企业号中的用户帐号
                    "touser": user,                  
                     # 消息类型              
                    "msgtype": "text",         
                     # 企业号中的应用id            
                    "agentid": WECHAT_AGENTID,                            
                    "text": {
                        "content": subject + '\n' + content
                    },
                    "safe": "0"
                }
                # 触发告警
                r = requests.post(url=post_url, data=json.dumps(message), verify=False)
                print r.text
            return True
    

### 邮件告警

邮箱告警要注意使用SSL，不然邮箱账密被撸了就呵呵了。

    
    
        def send(self, post_alert_content):
            to_addrs = "{}".format(post_alert_content["to_addrs"])
    
            subject = "【规则】 {}".format(post_alert_content["name"])
            message = "【时间】{} \n 【内容】{}".format(post_alert_content["create_at"], post_alert_content["content"])
            # to_addr = to_addrs.split(",")
            for to_addr in to_addrs.split(","):
                msg = self.format_msg(self.from_addr, to_addr, subject, message)
    
                s = smtplib.SMTP_SSL(Mail_Host, Mail_Port)
                s.login(Mail_User, Mail_Pass)
                s.sendmail(self.from_addr, [to_addr], msg.as_string())
                s.quit()
            return True
    

## 规则管理

为了方便远程管理规则，我们需要数据库存储规则信息，然后通过服务端接口查看当前规则信息，数量；操作YAML规则文件实现规则管理。

如果我们需要添加规则，那么在规则目录下，创建对应的yaml规则文件即可。

    
    
    def insertElastRule(params):
    
        # 查看数据库中是否存在同名规则
        _es_rule = ElastRule.query.filter_by(rule_esalert_name=rule_esalert_name).first()
        if _es_rule:
            return False
        else:
            now = datetime.now()
            insertRule = ElastRule(
                rule_name=params["rule_name"],
                rule_type=params["rule_type"],
                rule_index=params["rule_index"],
                rule_num_events=params["rule_num_events"],
                rule_timeframe=params["rule_timeframe"],
                rule_filter=params["rule_filter"],
                rule_level=params["rule_level"],
                rule_content=params["rule_content"],
                create_at=now,
                end_at=now
            )
            db.session.add(insertRule)
            db.session.commit()
            # 创建yaml规则文件
            createRuleYAML(params["rule_name"])
            return True
    

创建YAML函数：

    
    
    def createRuleYAML(rule_esalert_name):
        _rule = ElastRule.query.filter_by(rule_esalert_name=rule_esalert_name).first()
        ruleJson = {
            "name": _rule.rule_esalert_name,
            "type": _rule.rule_type,
            "index": _rule.rule_index,
            "num_events": int(_rule.rule_num_events),
            "timeframe": {'minutes': int(_rule.rule_timeframe)},
            "filter": _rule.rule_filter,
            "alert": "post",
            "http_post_url": "http://localhost:8088/api/alert",
            "http_post_static_payload":{"rule_name": _rule.rule_esalert_name, "rule_level": _rule.rule_level}
        }
    
        with open('/easywatch/elastalert_rules/{}.yaml'.format(rule_esalert_name),'w') as fw:
            yaml.safe_dump(ruleJson, stream=fw, allow_unicode=True, default_flow_style=False)
    

## 告警思考

渠道的使用，通过级别组合使用告警方式：

> 高级别告警使用3个或以上的方式告警 - 短信、钉钉（微信）、邮件
>
> 中级别告警使用2个或以上的方式告警 - 钉钉（微信）、邮件
>
> 低级别告警使用1个或以上的方式告警 - 邮件

ELK展示告警效果：

> 通过构建视图、面板，查看具体告警态势

 ***本文作者：bigface，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

