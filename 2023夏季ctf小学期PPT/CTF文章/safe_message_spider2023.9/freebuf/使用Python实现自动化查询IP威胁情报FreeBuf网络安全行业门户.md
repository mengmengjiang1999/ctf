### 解决的问题

一名网络安全从业人员在做日常网络安全运营分析时，就从防火墙、IDP、WAF等安全设备的日志分析计算，基本都会面对成千上万条日志，好一点的可能会有态势感知之类安全产品提供辅助分析，如果没有的就只能单条进行分析，造成的工作量必定是很大，也有可能存在从业人员的投入与产出形成差异。

遇到类似的问题要怎么办？我们可以采用现有开放的资源提供辅助手段，这里使用微步在线情报查询平台进行操作，本文包含IP信誉、IP分析功能，注册账号后IP信誉功能个人每天可以查询50次，通过工作认证后IP分析功能总共有1000次查询次数，可以按需采用不同的功能进行查询。

当然以上的说明只是实现了基本的功能(相当于是造个小轮子)，详见第四部分扩展功能。

### 官方接口文档及示例

#### IP信誉功能

针对入站场景的IP进行分析，能够提供IP的地理位置、ASN信息，通过判定规则精准判别IP是否恶意、风险严重级别、可信度级别；识别威胁类型，如：漏洞利用（exploit）、傀儡机（Zombie）、代理（Proxy）、可疑（Suspicious）等及相关安全事件或团伙标签。

    
    
    import requests
    url = "https://api.threatbook.cn/v3/scene/ip_reputation"
    query = {
    "apikey":"请替换apikey",
    "resource":"159.203.93.255"
    }
    response = requests.request("GET", url, params=query)
    print(response.json())
    

### IP分析

可针对业务日志，以及从防火墙、WAF等安防设备中获取的外部IP，进行分析。获取IP相关地理位置、ASN信息，综合判定威胁类型如:  
远控（C2）、傀儡机（Zombie）、失陷主机（Compromised）、扫描（Scanner）、钓鱼（Phishing）等，相关攻击团伙或安全事件标签，原始情报，相关样本信息等。

    
    
    import requests
    url = "https://api.threatbook.cn/v3/ip/query"
    query = {
    "apikey":"请替换apikey",
    "resource":"159.203.93.255"
    }
    response = requests.request("GET", url, params=query)
    print(response.json())
    

## 部分代码功能说明

### 定义威胁类型字典

参考平台的API文档对威胁类型进行整理，因包含恶意、非恶意的威胁类型，我们分别定义了全量威胁类型、非恶意威胁类型两个字典。

    
    
    # 定义全量威胁类型字典
    
    threat_type = {
    'C2': '远控', 'Botnet': '僵尸网络', 'Hijacked': '劫持', 'Phishing': '钓鱼', 'Malware': '恶意软件',
    'Exploit': '漏洞利用', 'Scanner': '扫描', 'Zombie': '傀儡机', 'Spam': '垃圾邮件', 'Suspicious': '可疑',
    'Compromised': '失陷主机', 'Whitelist': '白名单', 'Brute Force': '暴力破解', 'Proxy': '代理',
    'MiningPool': '矿池', 'CoinMiner': '私有矿池', 'suspicious_application': '可疑恶意软件',
    'suspicious_website': '可疑恶意站点', 'Fakewebsite': '仿冒网站', 'Sinkhole C2': '安全机构接管 C2',
    'SSH Brute Force': 'SSH暴力破解', 'FTP Brute Force': 'FTP暴力破解', 'SMTP Brute Force': 'SMTP暴力破解',
    'Http Brute Force': 'HTTP AUTH暴力破解', 'Web Login Brute Force': '撞库', 'HTTP Proxy': 'HTTP Proxy',
    'HTTP Proxy In': 'HTTP代理入口', 'HTTP Proxy Out': 'HTTP代理出口', 'Socks Proxy': 'Socks代理',
    'Socks Proxy In': 'Socks代理入口', 'Socks Proxy Out': 'Socks代理出口', 'VPN': 'VPN代理', 'VPN In': 'VPN入口',
    'VPN Out': 'VPN出口', 'Tor': 'Tor代理', 'Tor Proxy In': 'Tor入口', 'Tor Proxy Out': 'Tor出口', 'Bogon': '保留地址',
    'Full Bogon': '未启用IP', 'Gateway': '网关', 'IDC': 'IDC服务器', 'Dynamic IP': '动态IP', 'Edu': '教育',
    'DDNS': '动态域名', 'Mobile': '移动基站', 'Search Engine Crawler': '搜索引擎爬虫', 'CDN': 'CDN服务器',
    'Advertisement': '广告', 'DNS': 'DNS服务器', 'BTtracker': 'BT服务器', 'Backbone': '骨干网', 'ICP': 'ICP备案',
    'IoT Device': '物联网设备', 'Web Plug Deployed': '部署网站插件', 'Gameserver': '游戏服务器'}
    
    # 定义非恶意威胁类型字典
    
    infos = {'Bogon', 'Full Bogon', 'Gateway', 'IDC', 'Dynamic IP', 'Edu', 'DDNS', 'Mobile', 'Search Engine Crawler', 'CDN',
    'Advertisement', 'DNS', 'BTtracker', 'Backbone', 'ICP', 'IoT Device', 'Web Plug Deployed', 'Gameserver',
    'Whitelist', 'Whitelist', 'Info'}
    

### 威胁类型转换

向API接口发起请求后返回的数据格式为json格式，里面包含了所查询IP的威胁类型（详见官方响应示例）属于英文，而输出的结果是需要中文。实现方法就是定义一个转换类型的类进行实现，也包含了排除非恶意类型的函数。

    
    
    class ThreatType:
        def __init__(self):
            self.threat_type = threat_type
            self.infos = infos
    
        # 威胁类型字典转换
        def get_threat_type(self, original_list):
            # 使用列表推导式将每个元素替换为相应的中文名称
            new_list = [self.threat_type[item] for item in original_list]
            return new_list
    
        # 排除非恶意的类型
        def non_malicious(self, info_type):
            # 去除重复的info_type
            # info_type = list(set(str(info_type)))
            # 遍历info_type、infos中的每个值，对比后删除info_type和infos相同的值
            for info in self.infos:
                if info in info_type:
                    info_type.remove(info)
            return info_type
    

### 调用API接口

参照官方接口文档调用IP信誉、IP分析接口，同时定义状态码及其返回的错误提示。上面介绍到过IP信誉个人每天可以查询50次，当然也可以采用多个账号进行查询（一个账号对应一个key），详细代码如下：

    
    
    # 调用API接口
    
    class ThreatBookApi:
        def __init__(self):
            # 输入key
            self.apikey = '主key'
            # 定义key列表
            self.apikey_box = ['备key0', '备key1', '备key2', '备key3', '.....']
    
        # 状态码判断
        def get_code_query(self, text, re_code):
            re_codes = [-1, -2, -3, -5]
            if re_code in re_codes:
                get_json = {'response_code': re_code}
                if get_json['response_code'] == -1:
                    print(str(text) + '查询失败，API权限受限或请求出错.')
                if get_json['response_code'] == -2:
                    print(str(text) + '查询失败，请求无效.')
                if get_json['response_code'] == -3:
                    print(str(text) + '查询失败，请求参数缺失.')
                if get_json['response_code'] == -5:
                    print(str(text) + '查询失败，系统错误.')
            else:
                pass
    
        # IP信誉
        def ip_reputation(self, ip):
            for i in range(len(self.apikey_box)):
                url = "https://api.threatbook.cn/v3/scene/ip_reputation"
                query = {"apikey": self.apikey, "resource": ip}
                response = requests.get(url, params=query)
                if response.json()['response_code'] == -4:
                    self.apikey_backup = self.apikey_box[i]
                    i -= 1
                    query = {"apikey": self.apikey_backup, "resource": ip}
                    # self.progress_bar()
                    response = requests.get(url, params=query)
                    if response.json()['response_code'] == 0:
    
                        return response.json()
                    else:
                        continue
                else:
                    return response.json()
    
        # IP分析
        def ip_query(self, ip):
            url = "https://api.threatbook.cn/v3/ip/query"
            self.apikey = '主key'
            query = {"apikey": self.apikey, "resource": ip}
            response = requests.request("GET", url, params=query)
            if response.json()['response_code'] == -4:
                print('IP分析查询次数已使用完成(共1000次)')
            return response.json()
    

### IP信誉功能

    
    
    # IP信誉查询
    class ThreatReputation:
        def __init__(self, input_ip):
            # 初始化IP
            self.ip = input_ip
            # 调用接口
            self.BookApi = ThreatBookApi()
            # 调用IP信誉函数
            self.ip_json = self.BookApi.ip_reputation(ip=self.ip)
            # 执行函数
            self.threat_reputation()
    
        def threat_reputation(self):
        # 调用状态码判断，获取状态码并提示信息
        self.BookApi.get_code_query(text='IP信誉', re_code=self.ip_json['response_code'])
        if 'data' not in self.ip_json:
            print('威胁情报查询结束!')
            return None
        # 按照update_time字段对数据进行排序
        sorted_data = sorted(self.ip_json['data'].values(), key=lambda x: x['update_time'], reverse=True)
        # 获取最新的数据并提取所需的字段
        latest_data = sorted_data[0]
        # 可信度。分"low（低）"，"medium（中）"，"high（高）" 三档来标识
        confidence_level = latest_data['confidence_level']
        # 提取出威胁类型
        judgments = latest_data['judgments']
        # 是否为恶意IP。布尔类型，true代表恶意，false代表非恶意。
        latest_identity = self.ip_json['data'][self.ip]['is_malicious']
        # 取judgments列表第一位、latest_identity、confidence_level综合判断是否为恶意类型
        if (latest_identity is True) and (judgments[0] in threat_type) and (confidence_level == 'high'):
            # 删除无效的非恶意类型
            ThreatType().non_malicious(info_type=judgments)
            # 调用get_threat_type将intel_types翻译为中文
            type_cn = ThreatType().get_threat_type(original_list=set(judgments))
            print(
                "[IP信誉-可信度:{}]-源IP'{}'属于恶意IP，威胁类型包括'{}';".format(confidence_level, self.ip, ','.join(type_cn)))
        else:
            # 调用get_threat_type将intel_types翻译为中文
            # type_cn = ThreatType().get_threat_type(original_list=set(judgments))
            print("[IP信誉-可信度:{}]-源IP'{}'不属于恶意地址.".format(confidence_level, self.ip))
    

### IP分析功能

    
    
    # IP分析查询
    
    class ThreatQuery:
        def __init__(self, input_ip):
            # 定义变量
            self.ip = input_ip # 定义IP
            self.BookApi = ThreatBookApi()  # 调用API接口
            self.ip_json = self.BookApi.ip_query(ip=self.ip)  # 调用IP分析函数
            self.threat_type = threat_type
            self.infos = infos
            self.valid_intel = []
            self.valid_box = []
            self.confidence_box = []
            self.intel_types_box = []
            # 执行函数
            self.json_query()
    
        def json_query(self):
            # 调用状态码判断，获取状态码并提示信息
            self.BookApi.get_code_query(text='IP分析', re_code=self.ip_json['response_code'])
            if 'data' not in self.ip_json:
                print('威胁情报查询结束!')
                return None
            # 遍历键值为False(情报有效)的所有信息
            valid_json = self.ip_json['data'][self.ip]["intelligences"]["threatbook_lab"]
            # 当expired为False时，获取包含confidence，intel_types的值
            for j in valid_json:
                if not j['expired']:
                    self.valid_intel.append(
                        {'confidence': j['confidence'], 'intel_types': j['intel_types'],
                         'expired': j['expired']})
            for i in range(len(self.valid_intel)):
                valid = (self.valid_intel[i]['expired'])
                self.valid_box.append(valid)
                confidence = (self.valid_intel[i]['confidence'])
                self.confidence_box.append(confidence)
                intel_types = (self.valid_intel[i]['intel_types'])
                self.intel_types_box.append(intel_types)
            # self.valid_box, self.confidence_box, self.intel_types_box = self.get_param(valid_intel=self.valid_intel)
            box_data = [self.valid_box, self.confidence_box, self.intel_types_box]
            new_box = list(box_data)
            # 获取有效性
            new_valid = new_box[0][0]
            # 获取可信度
            new_confidence = max(set(new_box[1]))
            # 获取威胁类型
            intel_types_1 = new_box[2]
            intel_types_2 = list(set([item for sublist in intel_types_1 for item in sublist]))
            # print(new_valid, new_confidence, intel_types_2)
            # 调用Non_Malicious函数去除非恶意类型
            result = ThreatType().non_malicious(info_type=intel_types_2)
            # 用valid、威胁类型长度综合判断
            if new_valid is False and len(result) != 0:
                # 调用get_threat_type将intel_types翻译为中文
                cn_type = ThreatType().get_threat_type(original_list=set(result))
                # print(cn_type)
                print(
                    "[IP分析-可信度:{}%]-源IP'{}'属于恶意IP,威胁类型包括'{}';".format(new_confidence, self.ip, ','.join(cn_type)))
            if len(result) == 0:
                print("[IP分析-可信度:{}%]-源IP'{}'不属于恶意地址.".format(new_confidence, self.ip))
    

### 初步运行结果

在项目当前目录下新建test.txt文件，输入需要查询的IP，查询结果如下。  
![image](https://image.3001.net/images/20230627/1687829090_649a3a628a409c738e13e.png!small)  
与在线查询进行多次对比，查询结果基本无较大的差异，当然还是要根据可信度以及该IP的其他行为进行综合分析。  
![image](https://image.3001.net/images/20230627/1687829114_649a3a7a005804a1e1743.png!small)  
![image](https://image.3001.net/images/20230627/1687829124_649a3a84af937e1383da6.png!small)

## 扩展功能

以上的源IP为自动进行录入，回到开头提到的问题在日常网络安全运营工作中成千上万的日志要如何做分析，这里提出以下几点方向：

    
    
    （1）获取边界安全设备的源IP(含防火墙、WAF、IDP及IPS等)；
    （2）将获取的源IP参数传递给上述程序进行处理；
    （3）确认后联动安全设备进行处理或封禁。
    （4）获取源IP时可以从安全设备导出，也可以调用安全设备的API接口进行提取，若采用后者则会面临安全设备API泄露风险，需谨慎进行操作。
    

![image](https://image.3001.net/images/20230627/1687829370_649a3b7a6a32824d51218.png!small)

## 补充说明

此程序的功能仅为对源IP的威胁类型进行判断，具体情况还需要根据响应业务逻辑综合判定。本文为作者原创，仅供学习之用，版权归作者所有，转载请联系作者并注明出处！

