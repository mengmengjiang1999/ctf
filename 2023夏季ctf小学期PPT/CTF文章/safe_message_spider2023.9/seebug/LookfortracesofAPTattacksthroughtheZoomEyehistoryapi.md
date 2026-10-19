**Author: Heige(a.k.a Superhei) of KnownSec 404 Team  
Date: May 25,2020**  
**Chinese version:<https://paper.seebug.org/1219/>**

We had released ZoomEye’s historical data API query interface in ZoomEye 2020
that had launched in January this year:
<https://medium.com/@80vul/zoomeye-2020-has-started-8414d6aaf38>. Next, I will
introduce some examples of using ZoomEye History API to capture the traces of
APT team attacks.

Instructions for using the historical query API interface:
<https://www.zoomeye.org/doc#history-ip-search> ,Of course we have also
updated our ZoomEye SDK support history api:
<https://github.com/knownsec/ZoomEye>.

Before the cases are explained, I must explain the ZoomEye online data update
mode again: it is the overwrite update mode. Many malware teams, including
many apt teams, will abandon the C2 server immediately after it is discovered.
So this also causes the data on ZoomEye to be cached without being updated and
overwritten.

## The first case is about Darkhotel APT group

I have already mentioned it in this[
tweet](https://twitter.com/80vul/status/1262295955526713344 " tweet"), of
course, here needs to explain a "bug" in this tweet ,Although this “bug” has
nothing to do with the issue discussed today : The vulnerability used in this
attack should be CVE-2019-1367 instead of CVE-2020-0674 (Here we need to thank
the friends who discussed together)

![](https://images.seebug.org/content/images/2020/05/6a1e6707-9256-475c-a12d-e945c6f5ec41.jpg-w331s)

In this Darkhotel attack, they attacked the ip website service and implanted
ie 0day to carry out Watering Hole attack. So we queried all historical data
of this IP on ZoomEye:

    
    
    ╭─heige@404Team ~
    ╰─$python                                                                                                                                    
    Python 2.7.16 (default, Mar 15 2019, 21:13:51)
    [GCC 4.2.1 Compatible Apple LLVM 10.0.0 (clang-1000.11.45.5)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
     import zoomeye
     zm = zoomeye.ZoomEye(username="xxxxx", password="xxxx")
     zm.login()
     u'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpX...'
     data = zm.history_ip("202.x.x.x")
     22

List all scan time records and ports about this IP

    
    
     ...
    >>> for i in data['data']:
     ...     print(i['timestamp'],i['portinfo']['port'])
     ...
     (u'2020-01-28T10:58:02', 80)
     (u'2020-01-05T18:33:17', 80)
     (u'2019-11-25T05:27:58', 80)
     (u'2019-11-02T16:10:40', 80)
     (u'2019-10-31T11:39:02', 80)
     (u'2019-10-06T05:24:44', 80)
     (u'2019-08-02T09:52:27', 80)
     (u'2019-07-27T19:22:11', 80)
     (u'2019-05-18T10:38:59', 8181)
     (u'2019-05-02T19:37:20', 8181)
     (u'2019-05-01T00:48:05', 8009)
     (u'2019-04-09T16:29:58', 8181)
     (u'2019-03-24T20:46:31', 8181)
     (u'2018-05-18T18:22:21', 137)
     (u'2018-02-22T20:50:01', 8181)
     (u'2017-03-13T03:11:39', 8181)
     (u'2017-03-12T16:43:54', 8181)
     (u'2017-02-25T09:56:28', 137)
     (u'2016-11-01T00:22:30', 137)
     (u'2015-12-30T22:53:17', 8181)
     (u'2015-03-13T20:17:45', 8080)
     (u'2015-03-13T19:33:15', 21)

Query the time and port of the IE 0day implanted into the Watering Hole attack
:

    
    
    >>> for i in data['data']:
     ...     if "164.js" in i['raw_data']:
     ...             print(i['timestamp'],i['portinfo']['port'])
     ...
     (u'2020-01-28T10:58:02', 80)
     (u'2020-01-05T18:33:17', 80)
     (u'2019-11-25T05:27:58', 80)
     (u'2019-11-02T16:10:40', 80)
     (u'2019-10-31T11:39:02', 80)
     (u'2019-10-06T05:24:44', 80)

It turned out that this Watering Hole attack continued from at least
'2019-10-06 05:24:44' to '2020-01-28 10:58:02' , This also shows that
Darkhotel APT group attacked this IP website as early as 2019-10-06.

We continue to analyze the port service of this IP in 2019 :

    
    
    >>> for i in data['data']:
     ...     if "2019" in i['timestamp']:
     ...             print(i['timestamp'],i['portinfo']['port'],i['portinfo']['service'],i['portinfo']['product'])
     ...
     (u'2019-11-25T05:27:58', 80, u'http', u'nginx')
     (u'2019-11-02T16:10:40', 80, u'http', u'nginx')
     (u'2019-10-31T11:39:02', 80, u'http', u'nginx')
     (u'2019-10-06T05:24:44', 80, u'http', u'nginx')
     (u'2019-08-02T09:52:27', 80, u'http', u'nginx')
     (u'2019-07-27T19:22:11', 80, u'http', u'nginx')
     (u'2019-05-18T10:38:59', 8181, u'http', u'Apache Tomcat/Coyote JSP engine')
     (u'2019-05-02T19:37:20', 8181, u'http', u'Apache Tomcat/Coyote JSP engine')
     (u'2019-05-01T00:48:05', 8009, u'ajp13', u'Apache Jserv')
     (u'2019-04-09T16:29:58', 8181, u'http', u'Apache httpd')
     (u'2019-03-24T20:46:31', 8181, u'http', u'Apache Tomcat/Coyote JSP engine')

Very typical Tomcat-based JSP operating environment, and once opened 8009 ajp
port. Many attack events prove that tomcat manages weak passwords, security
vulnerabilities and other issues, making security very vulnerable,Perhaps this
is also the method used in this attack.

## The second case is about APT-C-01(a.k.a Green Spot)

Qi An Xin Threat Intelligence Center released a detailed analysis report on
APT-C-01 in 2018:
<https://www.virusbulletin.com/virusbulletin/2019/11/vb2019-paper-vine-climbing-over-great-firewall-longterm-attack-against-china/> (En)
<https://ti.qianxin.com/uploads/2018/09/20/6f8ad451646c9eda1f75c5d31f39f668.pdf>(Ch)

"The loader program will first try to connect to a common URL to check network
connectivity. If there is no connection, it will try to connect every five
seconds until the network is connected. Then it downloads the payload from
`hxxp://updateinfo.servegame.org/tiny1detvghrt.tmp`"

We put our focus on the payload download URL
`hxxp://updateinfo.servegame.org/tiny1detvghrt.tmp>`,Through the ping command,
we can no longer find the IP address of this domain name resolution :

    
    
    ─heige@404Team ~
        ╰─$ping updateinfo.servegame.org
        ping: cannot resolve updateinfo.servegame.org: Unknown host

From the Chinese version of the report, we see a screenshot that shows that
can opendir

![](https://images.seebug.org/content/images/2020/05/aa8ef73c-c4b4-43a6-b8a5-83e869c3de42.png-w331s)

This means we can find the target by searching "tiny1detvghrt.tmp" on ZoomEye
,Very lucky we found it :

![](https://images.seebug.org/content/images/2020/05/87f50c7c-a719-4bc8-b935-b214107ce3f1.png-w331s)

Once again, after the APT attack was discovered, these IPs were directly
abandoned.

We get the IP(165.227.220.223) of the domain(`updateinfo.servegame.org`) name
and continue to query the historical records through the ZoomEye history api
interface

    
    
    >>> data = zm.history_ip("165.227.220.223")
    >>> 9
    >>> for i in data['data']:
     ...     print(i['timestamp'],i['portinfo']['port'])
     ...
     (u'2019-06-18T19:02:22', 22)
     (u'2018-09-02T08:13:58', 22)
     (u'2018-07-31T05:58:44', 22)
     (u'2018-05-20T00:55:48', 80) 
     (u'2018-05-16T20:42:35', 22)
     (u'2018-04-08T07:53:00', 80)
     (u'2018-02-22T19:04:29', 22)
     (u'2017-11-21T19:09:14', 80)
     (u'2017-10-04T05:17:38', 80)

Let's look at the time interval for tiny1detvghrt.tmp deployment : from at
least '2017-11-21 19:09:14' to '2018-05-20 00:55:48'

    
    
    >>> for i in data['data']:
     ...     if "tiny1detvghrt.tmp" in i['raw_data']:
     ...             print(i['timestamp'],i['portinfo']['port'])
     ...
     (u'2018-05-20T00:55:48', 80)
     (u'2018-04-08T07:53:00', 80)
     (u'2017-11-21T19:09:14', 80)

Let's look at the time node before `tiny1detvghrt.tmp` deployment: 2017-10-04
05:17:38

    
    
    >>> for i in data['data']:
     ...     if "2017-10-04" in i['timestamp']:
     ...             print(i['raw_data'])
     ...
     HTTP/1.1 200 OK
     Date: Tue, 03 Oct 2017 21:17:37 GMT
     Server: Apache
     Vary: Accept-Encoding
     Content-Length: 1757
     Connection: close
     Content-Type: text/html;charset=UTF-8
    
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <html>
     <head>
      <title>Index of /</title>
     </head>
     <body>
    <h1>Index of /</h1>
      <table>
       <tr><th valign="top">< img src="/icons/blank.gif" alt="[ICO]"></th><th>< a href=" ">Name</ a></th><th>< a href="?C=M;O=A">Last modified</ a></th><th>< a href="?C=S;O=A">Size</ a></th><th>< a href="?C=D;O=A">Description</ a></th></tr>
       <tr><th colspan="5"><hr></th></tr>
    <tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="doajksdlfsadk.tmp">doajksdlfsadk.tmp</ a></td><td align="right">2017-09-15 08:21  </td><td align="right">4.9K</td><td>&nbsp;</td></tr>
    <tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="doajksdlfsadk.tmp.1">doajksdlfsadk.tmp.1</ a></td><td align="right">2017-09-15 08:21  </td><td align="right">4.9K</td><td>&nbsp;</td></tr>
    <tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="doajksdlrfadk.tmp">doajksdlrfadk.tmp</ a></td><td align="right">2017-09-27 06:36  </td><td align="right">4.9K</td><td>&nbsp;</td></tr>
    <tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="dvhrksdlfsadk.tmp">dvhrksdlfsadk.tmp</ a></td><td align="right">2017-09-27 06:38  </td><td align="right">4.9K</td><td>&nbsp;</td></tr>
    <tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="vfajksdlfsadk.tmp">vfajksdlfsadk.tmp</ a></td><td align="right">2017-09-27 06:37  </td><td align="right">4.9K</td><td>&nbsp;</td></tr>
    <tr><td valign="top">< img src="/icons/unknown.gif" alt="[   ]"></td><td>< a href="wget-log">wget-log</ a></td><td align="right">2017-09-20 07:24  </td><td align="right">572 </td><td>&nbsp;</td></tr>
       <tr><th colspan="5"><hr></th></tr>
    </table>
    </body></html>

From the file naming method and file size, it can be inferred that this time
node, the attacker should be a drill before the attack.

## Final summary

The cyberspace search engine is very useful in the tracking of cyberattack
threats by using active detection methods. It rechecks the attacker's attack
methods, purposes, and processes through the timeline of historical records.
Finally, I would like to thank all the friends who support ZoomEye. As the
world's leading search engine for cyberspace mapping, ZoomEye has been working
hard!

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1220/>

