whois(读作"Who
is"，非缩写)是用来查询[域名](https://baike.so.com/doc/5329854-5565028.html)的IP以及[所有者](https://baike.so.com/doc/411241-435559.html)等信息的[传输协议](https://baike.so.com/doc/4873795-5091524.html)。简单说，whois就是一个用来查询[域名](https://baike.so.com/doc/5329854-5565028.html)是否已经被注册，以及注册域名的详细信息的数据库(如域名所有人、[域名注册](https://baike.so.com/doc/5261857-5495493.html)商)。通过whois来实现对[域名](https://baike.so.com/doc/5329854-5565028.html)信息的查询。早期的whois查询多以命令列接口存在，但是现在出现了一些网页接口简化的线上查询工具，可以一次向不同的数据库查询。网页接口的查询工具仍然依赖whois协议向服务器发送查询请求，命令列接口的工具仍然被系统管理员广泛使用。whois通常使用[TCP](https://baike.so.com/doc/3381795-3560272.html)协议43端口。每个[域名](https://baike.so.com/doc/5329854-5565028.html)/IP的whois信息由对应的管理机构保存。

不同[域名](https://baike.so.com/doc/5329854-5565028.html)后缀的whois[信息](https://baike.so.com/doc/933443-986650.html)需要到不同的whois数据库[查询](https://baike.so.com/doc/6735594-6949973.html)。如[.com](https://baike.so.com/doc/5352485-5587943.html)的whois数据库和[.edu](https://baike.so.com/doc/432174-457638.html)的就不同。目前国内提供WHOIS查询服务的[网站](https://baike.so.com/doc/4649255-4862457.html)有万网、[站长之家](https://baike.so.com/doc/5334815-5570253.html)的等。每个域名或IP的WHOIS信息由对应的管理机构保存，例如，以.com结尾的域名的WHOIS信息由.com域名运营商VeriSign管理，中国国家顶级域名.cn域名由CNNIC管理。

"WHOIS"是当前[域名系统](https://baike.so.com/doc/6112986-6326125.html)中不可或缺的一项信息服务。在使用[域名](https://baike.so.com/doc/5329854-5565028.html)进行Internet冲浪时，很多用户希望进一步了解域名、名字服务器的详细信息，这就会用到WHOIS。对于[域名](https://baike.so.com/doc/5329854-5565028.html)的注册服务机构(registrar)而言，要确认域名数据是否已经正确注册到[域名注册](https://baike.so.com/doc/5261857-5495493.html)中心(registry)，也经常会用到WHOIS。直观来看，WHOIS就是链接到[域名](https://baike.so.com/doc/5329854-5565028.html)数据库的[搜索引擎](https://baike.so.com/doc/311390-329744.html)，一般来说是属于网络信息中心([NIC](https://baike.so.com/doc/6744841-6959384.html))所提供和维护的名字服务之一。

根据[IETF](https://baike.so.com/doc/5456269-5694657.html)标准要求，WHOIS服务一般由WHOIS系统来提供。WHOIS系统是一个[Client](https://baike.so.com/doc/6779691-6995796.html)/[Server](https://baike.so.com/doc/5689669-5902366.html)系统。其中Client端主要负责:

1)提供访问WHOIS系统的[用户接口](https://baike.so.com/doc/570652-604086.html);

2)生成查询并将其以适当的格式传送给Server;

3)接收Server传回的响应，并以用户可读的形式输出。

Server端则主要负责接收Client端的请求并发回响应数据。Internet上基于TCP协议的基本服务都有自己默认的TCP[端口号](https://baike.so.com/doc/1540075-1628118.html)，象HTTP服务的默认[端口](https://baike.so.com/doc/162735-171954.html)号为80，FTP服务的默认控制端口号为21(数据端口为20)等。同样作为Internet上核心服务之一的WHOIS服务，其Server端默认监听43号TCP[端口](https://baike.so.com/doc/162735-171954.html)，接收查询请求并产生响应。一般来说，Server端可以接收三种类型的信息查询:联系人、主机和[域名](https://baike.so.com/doc/5329854-5565028.html)。对于同一查询，Server端的输出应该具有一致性和稳定性。

WHOIS服务是一个在线的"请求/响应"式服务。WHOIS
Server运行在后台监听43[端口](https://baike.so.com/doc/162735-171954.html)，当Internet用户搜索一个[域名](https://baike.so.com/doc/5329854-5565028.html)(或主机、联系人等其他信息)时，WHOIS
Server首先建立一个与Client的TCP连接，然后接收用户请求的信息并据此查询后台域名数据库。如果数据库中存在相应的记录，它会将相关信息如[所有者](https://baike.so.com/doc/411241-435559.html)、管理信息以及技术联络信息等，反馈给Client。待Server输出结束，Client关闭连接，至此，一个查询过程结束。

  

