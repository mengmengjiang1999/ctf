**![68747470733a2f2f63687269733430382e636f6d2f63742d6578706f7365722e706e67.png](https://image.3001.net/images/20181001/1538355789_5bb1724d663e9.png!small)**

## **什么是证书透明度（简称CT）？**

 **证书透明度（Certificate
Transparency）是谷歌力推的一项拟在确保证书系统安全的透明审查技术。其目标是提供一个开放的审计和监控系统，可以让任何域名的所有者，确定CA证书是否被错误签发或恶意使用。TLS的缺点是你的浏览器隐性包含了一个大型受信任CA列表。如果任何这些CA恶意为域创建新证书，则你的浏览器都会信任它。CT为TLS证书信任提供了额外的安全保障：即公司可以监控谁为他们拥有的域创建了证书。此外，它还允许浏览器验证给定域的证书是否在公共日志记录中。**

而这些日志对于渗透测试人员或红队而言，无疑是座信息的宝库。

## ct-exposer能为我们做什么？

ct-exposer将查询给定域的CT日志，然后尝试对域进行DNS查找以获取DNS中存在的域。根据我的经验，到目前为止ct-exposer为我查找到了许多使用“site:domain.com”谷歌搜索找不到的子域。请记住，无法解析的域可以是旧域或仅是内部域（例如：你需要访问内部DNS服务器才能解析它们）。

##  **安装依赖**

> Python3，gevent，requests 和 urllib3，pip3 install -r requirements.txt

## 使用

    
    
    usage: ct-exposer.py [-h] -d DOMAIN [-u] [-m]
    
    optional arguments:
      -h, --help            显示帮助信息并退出
      -d DOMAIN, --domain DOMAIN
                            用于查询CT日志的域,例如：domain.com
      -u, --urls            对于要解析的域，使用https:// urls输出结果，每行一条记录。
      -m, --masscan         输出已解析的IP地址，每行一条记录。并将IP导入一个文件用于masscan扫描。

## 输出示例

    
    
    python3 ct-exposer.py -d teslamotors.com
    [+]: Downloading domain list...
    [+]: Download of domain list complete.
    [+]: Parsed 76 domain(s) from list.
    
    [+]: Domains found:
    205.234.27.243	adfs.teslamotors.com
    104.92.115.166	akamaisecure.qualtrics.com
    211.147.80.202	cn.auth.teslamotors.com
    211.147.88.104	cnvpn.teslamotors.com
    209.10.208.24	energystorage.teslamotors.com
    209.11.133.110	epc.teslamotors.com
    149.14.82.93	euvpn.teslamotors.com
    209.11.133.50	extconfl.teslamotors.com
    209.11.133.35	extissues.teslamotors.com
    209.10.208.31	fleetview.teslamotors.com
    64.125.183.134	leaseapp.teslamotors.com
    64.125.183.134	leaseappde.teslamotors.com
    209.11.133.11	lync.teslamotors.com
    211.147.80.201	mycn-origin.teslamotors.com
    205.234.27.211	origin-www45.teslamotors.com
    205.234.31.120	owner-api.teslamotors.com
    12.201.132.70	plcvpn.teslamotors.com
    205.234.27.246	quickbase.teslamotors.com
    104.86.205.249	resources.teslamotors.com
    209.10.208.55	sdlcvpn.teslamotors.com
    209.11.133.37	service.teslamotors.com
    205.234.27.226	sftp.teslamotors.com
    23.227.38.64	shop.eu.teslamotors.com
    209.133.79.61	shop.teslamotors.com
    23.227.38.64	shop.uk.teslamotors.com
    205.234.27.197	smswsproxy.teslamotors.com
    209.11.133.36	supercharger.teslamotors.com
    209.133.79.59	suppliers.teslamotors.com
    209.133.79.61	tesla.com
    209.11.133.106	teslamotors.com
    205.234.27.200	teslaplm-external.teslamotors.com
    209.11.133.107	toolbox.teslamotors.com
    209.10.208.20	trt.teslamotors.com
    205.234.27.250	upload.teslamotors.com
    209.10.208.27	us.auth.teslamotors.com
    205.234.27.218	vpn.teslamotors.com
    211.147.80.205	wechat.teslamotors.com
    205.234.27.212	wsproxy.teslamotors.com
    209.133.79.54	www-origin.teslamotors.com
    104.86.216.34	www.teslamotors.com
    209.11.133.61	xmail.teslamotors.com
    211.147.80.203	xmailcn.teslamotors.com
    
    [+]: Domains with no DNS record:
    none	cdn02.c3edge.net
    none	creditauction.teslamotors.com
    none	evprd.teslamotors.com
    none	imail.teslamotors.com
    none	jupytersvn.teslamotors.com
    none	leadgen.teslamotors.com
    none	lockit.teslamotors.com
    none	lockpay.teslamotors.com
    none	neovi-vpn.teslamotors.com
    none	origin-wte.teslamotors.com
    none	referral.teslamotors.com
    none	resources.tesla.com
    none	securemail.teslamotors.com
    none	shop.ca.teslamotors.com
    none	shop.no.teslamotors.com
    none	sip.teslamotors.com
    none	sjc04p2staap04.teslamotors.com
    none	sling.teslamotors.com
    none	tesla3dx.teslamotors.com
    none	testimail.teslamotors.com
    none	toolbox-energy.teslamotors.com
    none	vpn-node0.teslamotors.com
    none	wd.s3.teslamotors.com
    none	www-uat2.teslamotors.com
    none	www45.teslamotors.com

 ** *****参考来源：[GitHub](https://github.com/chris408/ct-exposer)，
FB小编secist编译，转载请注明来自FreeBuf.COM**

