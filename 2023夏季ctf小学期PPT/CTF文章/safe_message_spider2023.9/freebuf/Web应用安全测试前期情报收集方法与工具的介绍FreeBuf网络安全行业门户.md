## 背景

**这篇文章将会详细介绍在Web应用安全测试前期进行情报收集的方法与使用工具。其实在很早之前，就有很多朋友以及社区成员要求我分享一些侦察经验。但我迷上了一部非常好看的电视剧，因此一直都没有时间。最近，我又收到了InfoSec社区的一些新成员的请求，这也促使我写成这篇文章。除了一些侦察方法，本文还会介绍一些非常实用的侦察工具和服务。这些工具和服务在测试期间都给予了我很大的帮助，相信掌握这些工具和服务的使用方法，也会给你带来帮助**
。

![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/15285999534422.png!small)

## 简介

每当我收到一个新程序或者想测试一个目标时，我首先会使用的工具就是
[**Knockpy**](https://github.com/guelfoweb/knock) **。**
之所以选择这个工具，是因为它可以为我提供一个带有响应码的子域快速浏览。有一次，我在2分钟内就发现了一个子域接管错误。

knockpy
可以说是我的幸运神器，迄今为止已经帮助我在[HackerOne](https://medium.com/@Hacker0x01)上发现了近150个
bug。通过 knockpy，我很快就看到了一个指向AWS S3 bucket的404页面，并且可以创建bucket。因此，我毫不犹豫的创建了新的 AWS
S3 bucket，并用编码的文件名上传了一个文本文件。在成功测试后，我第一时间报告了错误，在短短的15分钟内就得到了赏金。

![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/1528599982204.png!small)

## 工具定制

我使用自定义的工具 [Malvinsh](https://github.com/melvinsh/subresolve) 解析工具进行子域侦察。

<https://github.com/melvinsh/subresolve>

![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/15286000247141.png!small)

Malvinsh工具的使用过程分为两个简单阶段：

> 使用HOST从wordlist获取域/子域的IP地址。
>
> 执行Nmap扫描。

基于这个逻辑，我创建了两个脚本。

> **Subdomain.rb**
>
> **Recon.rb**

 **警告：** 请勿在未经允许的程序和目标范围使用这些脚本。

###  **Subdomain.rb**

Subdomain.rb 是一个轻量级脚本，用于自动化的子域查找。这个工具非常灵活，可以再搭配、添加其它工具。

Subfinder 和 sublist3r
的结果有时会重叠，因此我在使用中通常会独立运行这两个工具。实验证明这样做的效果非常好，因此在这个脚本中，我也保存了这两种工具。

这个脚本主要使用以下工具来获取子域数据：

[Subfinder](https://github.com/Ice3man543/subfinder)

> <https://github.com/Ice3man543/subfinder>

[Censys subdomain finder](https://github.com/christophetd/censys-subdomain-finder)

> <https://github.com/christophetd/censys-subdomain-finder>

[Knockpy](https://github.com/guelfoweb/knock)

> <https://github.com/guelfoweb/knock>

[Sublist3r](https://github.com/aboul3la/Sublist3r)

> <https://github.com/aboul3la/Sublist3r>

[Aquatone](https://github.com/michenriksen/aquatone)

> <https://github.com/michenriksen/aquatone>

### **subdomain.rb**[
**gist**](https://gist.github.com/ehsahil/0b618104319a97b21bea88fbb5ea49c2)

 **利用过程：**

    
    
    ruby subdomain.rb domain.com

![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/15286000843749.png!small)

可以创建一个文件，并将以上的输出的子域添加到文件中。然后，使用sort命令删除文件中所有重复的子域。

    
    
    sort wordlist | uniq

将最后一个唯一的子域文件传递给recon.rb

###  **Resolve.rb**

Recon.rb 是另一个轻量级脚本，它也很灵活，同样可以搭配、添加其它工具。这个工具保存在 recon.rb 中

> **Host** : 解析子域
>
> **Nmap** : 执行对子域的端口扫描

<https://nmap.org/>

 **AWS CLI** \- 在 AWS CLI 利用脚本中，测试子域连接到 AWS bucket 或不检查列表权限。（可以自定义以测试写入权限文件。）

<https://aws.amazon.com/cli>

 **Dirsearch** \- 搜索默认字典列表和所有（*）扩展名的目录。

<https://github.com/maurosoria/dirsearch>

###  **recon.rb**[
**gist**](https://gist.github.com/ehsahil/f0f6e731a22a111399aa8503e34b6919)

 **使用：**

    
    
    ruby recon.sh wordlist

**![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/15286001236917.png!small)**

 **Lazyrecon**

<https://github.com/nahamsec/lazyrecon>

 **博客文章**

<https://blog.it-securityguard.com/bugbounty-decoding-a-%F0%9F%98%B1-00000-htpasswd-bounty/>

<https://en.internetwache.org/scanning-the-alexa-top-1m-for-ds-store-files-12-03-2018/>

##  **Visual Recon（可视化侦察）**

利用从 subdomain.rb 生成的 wordlist 进行可视化侦察。

这个过程中通常使用以下两个工具：

[ **WebScreenshot**](https://github.com/maaaaz/webscreenshot)

<https://github.com/maaaaz/webscreenshot>

![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/1528600173734.png!small)[
**Lazyshot**](https://github.com/mdhama/lazyshot)

<https://github.com/mdhama/lazyshot>

**![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/15286001959410.png!small)**

 **博客文章**

<https://blog.it-securityguard.com/visual-recon-a-beginners-guide/>

## 获取更多的信息

当某个特定程序报告 2-3 个问题后，我会提交报告并等待厂商的回应。如果这个程序足够吸引我，我就会继续尝试使用以下服务收集尽可能多的关于目标的信息。

###  **Censys**

<https://censys.io/>

    
    
    -Commands
    
    443.https.tls.certificate.parsed.extensions.subject_alt_name.dns_names:domain.com
    
    “hackme.tld” + internal 
    
    “hackme.tld” + sandbox
    
    “hackme.tld” + Staging
    
    “hackme.tld” + Development/Dev
    
    “hackme.tld” +  production/prod
    
     hackme inc
     
     Credit: @nahamsec
     
     Interesting posts: 
     https://0xpatrik.com/censys-guide/

###  **Censys工具：**

<https://github.com/yamakira/censys-enumeration>

 **Shodan**

<https://www.shodan.io/>

    
    
    Basics Filters: 
    1. City 
    Example City:New Delhi. 
    
    2. Country
    Example: Country:INDIA
    
    3. Port
    Example:Ports: 8443, 8080, 8180 etc
    
    4. OS (Operating System)
    Example: microsoft-iis os:"windows 2003"
    
    5. Geo
    Example:  apache geo:42.9693,-74.1224 
    
    6. Hostname
    Example: hostname:domain.com
    
    7. After and Before
    Example: apache before:1/01/2014 
    
    8. Org
    Example: Org: Hackerone Inc.  
    
    9. Product
    Example: Product: Tomcat
    
    10. Title
    Example: Title: “Dashboard [Jenkins]”
    
    
    Taken from: https://www.exploit-db.com/docs/english/33859-searching-shodan-for-fun-and-profit.pdf

 **ViewDNS** — 反向Whois查找。

<http://viewdns.info/>

使用whois命令获取目标的whois信息，也可使用其它在线工具获取。

    
    
    whois domain.com

如果该公司未使用域隐私服务，就能找到 host-masters 的电子邮件地址，并使用这个电子邮件通过反向 Whois
来查找在同一电子邮件地址上注册的其他域。目标合法注册名称也可以使用。

![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/15286002738388.png!small)

 **[IP range Crawl](https://bgp.he.net/)**

![v](https://image.3001.net/images/20180610/15286003094795.png!small)

 **AltDNS**

<https://github.com/infosec-au/altdns>

 **Nmap Subdomain finding**

    
    
    #Finding subdomains via Nmap. 
    
    nmap --script dns-brute --script-args dns-brute.domain=domain.com,dns-brute.threads=6,dns-brute.hostlist=./sub1000.lst
    
    nmap --script dns-brute --script-args dns-brute.domain=domain.com,dns-brute.threads=6,dns-brute.hostlist=./sub10000.lst
    
    nmap --script dns-brute --script-args dns-brute.domain=domain.com,dns-brute.threads=6,dns-brute.hostlist=./sub100000.lst
    
    nmap --script dns-brute --script-args dns-brute.domain=domain.com,dns-brute.threads=6,dns-brute.hostlist=./sub1000000.lst
    
    
    #Wordlist : 
    
    1. sub1000.lst - https://drive.google.com/open?id=0B0h-Dh0Oss1zOGFqVVl1bTVpdWc
    2. sub10000.lst - https://drive.google.com/open?id=0B0h-Dh0Oss1zTTdmQnZsQ0JCYzA
    3. sub100000.lst - https://drive.google.com/open?id=0B0h-Dh0Oss1zdDBFT1dCc08ya0U
    4. sub1000000.lst - https://drive.google.com/open?id=0B0h-Dh0Oss1zODNfSG1sbVJ1WE0
    
    In case above links are not available : https://github.com/ehsahil/wordlists-for-nmap
    
    #Taken from http://blog.x1622.com/2016/11/subdomain-discovery-with-nmap-and.html

 **Content-Security-Policy (CSP)**

工具

> <https://github.com/yamakira/domains-from-csp>
>
> <https://securityheaders.com/>

使用Burp Suite发现目标，视频演示：

看不到？点[这里](https://v.qq.com/x/page/w0701qa8urs.html)

发现 Burp Suite 链接目标：

> 1\. 关闭被动扫描；
>
> 2\. 设置表单自动提交；
>
> 3\. 将范围设置为advanced control并使用目标名称字符串（不是正常的FQDN）；
>
> 4\. 遍历+浏览，然后递归地复制所有主机；
>
> 5\. 其他；

 **Domain Analyzer**

<https://github.com/eldraco/domain_analyzer>

 **Domain Profiler**

<https://github.com/jpf/domain-profiler>

 **VHost Scan**

<https://github.com/codingo/VHostScan>

 **ThreatCrowd**

<https://www.threatcrowd.org/>

 **Visual Site Mapper**

<http://www.visualsitemapper.com/>

 **证书透明度**

 **Google透明度报告**

<https://transparencyreport.google.com/https/certificates>

 **Certsspotter**

<https://certspotter.com/api/v0/certs?domain=hackerone.com>

 **CertDB**

<https://certdb.com/>

 **Crt.sh** —

<https://crt.sh/?q=%25domain.com>

 **Facebook证书透明度监控订阅。**

<https://developers.facebook.com/tools/ct>

**![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/15286004068794.png!small)![Web应用安全测试前期情报收集方法与工具的介绍](https://image.3001.net/images/20180610/15286004069753.png!small)**

 **博客文章和工具**

> <https://0xpatrik.com/asset-discovery/>
>
> <https://0xpatrik.com/subdomain-takeover/>
>
> <https://0xpatrik.com/takeover-proofs/>
>
> <https://0xpatrik.com/project-sonar-guide/>

**侦察技术PDF文档**

> <https://speakerdeck.com/yamakira/practical-recon-techniques-for-bug-> hunters-and-pentesters>
>
> <https://github.com/EdOverflow/can-i-take-over-xyz>

## 数据存储 **Buckets**

数据存储buckets通常所处位置。

> Github
>
> Javascript files
>
> CSP Headers
>
> Archive crawl
>
> Pastebin

提示：如 果bucket
返回拒绝访问的信息，可以尝试在Google上搜索。谷歌团队最近很有可能更改了bucket的权限，并将特定文件编入索引（具有读取权限）。

如果应用程序具有文件上传功能，则尝试捕获文件上传请求并查看文件上传的位置。有时可以发现 AWS 或其他数据存储buckets，这是其他方法无法找到的收获。

如果找到了像upload-usercontent-target-prod这样的存储bucket，可以尝试将prod更改为dev，staging，sandbox等。

[ **AWS CLI**](https://aws.amazon.com/cli/) — AWS CLI可用于验证或测试AWS S3
buckets权限，创建存储Buckets以及读取其他存储Buckets数据。AWS帐户需要使用CLI。

<https://aws.amazon.com/cli/>

    
    
    1. Listing AWS bucket content. (Testing for list permission)
    
    Sahils-MacBook-Pro:~ sahil$ aws s3 ls s3://bucket
    
    2. Writing on AWS Bucket. (Testing for write Permission)
    
    Sahils-MacBook-Pro:~ sahil$ aws s3 cp test.txt s3://bucket (Copying test.txt into the bucket with no public file read permission)
    Sahils-MacBook-Pro:~ sahil$ aws s3 mv test.txt s3://bucket (Moving test.txt into the bucket with no public file read permission)
    
    Copy test.txt file into the aws s3 bucket with public file read permission. 
    Sahils-MacBook-Pro:~ sahil$ aws s3 cp test.txt s3://bucket --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
    
    Sometimes the bucket are only available in a particular region. For that use the following regions with `--region` flag. 
    
    1. US East (N. Virginia) - us-east-1	
    2. US East (Ohio)	- us-east-2
    3. US West (N. California)	- us-west-1	
    4. US West (Oregon)	- us-west-2	
    5. Canada (Central)	- ca-central-1	
    6. Asia Pacific (Mumbai)	- ap-south-1	
    7. Asia Pacific (Seoul)	- ap-northeast-2	
    8. Asia Pacific (Osaka-Local) ***	 - ap-northeast-3	
    9. Asia Pacific (Singapore)	- ap-southeast-1	
    10. Asia Pacific (Sydney)	- ap-southeast-2	
    11. Asia Pacific (Tokyo)	- ap-northeast-1	
    12. China (Beijing)	- cn-north-1	
    13. China (Ningxia)	- cn-northwest-1	
    14. EU (Frankfurt)	- eu-central-1	
    15. EU (Ireland)	- eu-west-1	
    16. EU (London)	- eu-west-2	
    17. EU (Paris)	- eu-west-3	
    18. South America (São Paulo)	- sa-east-1	
    
    Example: 
    
    Sahils-MacBook-Pro:~ sahil$ aws s3 ls s3://bucket --region us-east-2
    
    3. Deleting files from the bucket. 
    
    Sahils-MacBook-Pro:~ sahil$ aws s3 rm s3://bucket/test.txt 
    
    Reference : https://docs.aws.amazon.com/general/latest/gr/rande.html
      
    

**Bucket Finder** \- 一款非常好用的使用子域wordlist查找buckets的工具，可以把他集成到recon.rb脚本中。

<https://digi.ninja/projects/bucket_finder.php>

 **LazyS3** \- LazyS3是另一款我经常用来查找staging, sandboxed, dev和生产buckets的工具。

<https://github.com/nahamsec/lazys3>

 **Slurp** ：一款优秀的AWS Buckets Recon工具。

<https://github.com/bbb31/slurp>

 **S3 Bucket Finder** \- 同样适用于AWS S3 buckets的工具。

<https://github.com/gwen001/s3-buckets-finder>

 **博客文章**

<https://labs.detectify.com/2017/07/13/a-deep-dive-into-aws-s3-access-controls-taking-full-control-over-your-assets/>

## 侦察Github

Github对于查找目标的敏感信息非常有帮助。在公共GitHub存储库中可以找到访问密钥、密码、开放式端点、s3 buckets 以及备份文件等。

    
    
    “Hackme.tld” API_key
    “Hackme.tld” secret_key
    “Hackme.tld” aws_key
    “Hackme.tld” Password 
    “Hackme.tld” FTP
    “Hackme.tld” login
    “Hackme.tld” github_token
    “Hackme.tld” http:// & https://  
    “Hackme.tld” amazonaws
    “Hackme.tld” digitaloceanspaces
    “Hackme.tld” storage.googleapis.com
    “Hackme.tld” access_token
    “Hackme.tld” blob.core.windows.net
    “Hackme.tld” token
    “Hackme.tld” secret
    “Hackme.tld” TODO
    “Hackme.tld” vulnerable
    “Hackme.tld” CSRF
    “Hackme.tld” Hash
    “Hackme.tld” random
    “Hackme.tld” HMAC
    “Hackme.tld” MD5, SHA-1, SHA-2, etc.
    
    credits @edoverflow & @nahamsec.

 **博客文章**

<https://edoverflow.com//2017/github-for-bugbountyhunters>

## 仔细查看每个JS文件

有时，Javascript文件中会包含一些敏感信息，例如各种密钥或硬编码令牌。

我在Javascript中找到了以下内容：

> AWS或其他服务访问密钥；
>
> AWS S3 buckets或其他具有读/写权限的数据存储buckets；
>
> 打开备份sql数据库端点；
>
> 开放内部服务端点

 **工具**

一般可以利用 JSBeautifier 手动阅读 JavaScript 代码。

<http://jsbeautifier.org/>

以下工具很有用：

 **LinkFinder**

<https://github.com/GerbenJavado/LinkFinder>

JSParser 是 Behrouz Sadeghipour 开发的另一款类似工具。

<https://github.com/nahamsec/JSParser>

博客文章

<https://medium.com/bugbountywriteup/bug-bounty-tips-tricks-js-javascript-files-bdde412ea49d>

## 存档

在waybackmachine中搜索目标网页，可以找到以下内容：

> 旧的和被弃用的JS文件；
>
> 旧API端点；
>
> 被弃用的CDN端点；
>
> 被弃用的子域名；
>
> 源代码注释中提供的Dev&staging端点信息 ；

如果页面返回403，你也可以在way back machine搜索目标那些403页面，你会发现一些有用的信息。

**工具：**[Waybackurl](https://gist.github.com/mhmdiaa/adf6bff70142e5091792841d4b372050)

## 持续侦察

在持续侦察中最重要的是处理未来使用的侦察数据。为此，我在SecurityEscape中创建了一个名为Swiftness的工具。Swiftness
可用于保存各个目标的所有侦察数据，并设置任务提醒，定期对目标进行重访调查（每个月）。

![Bucket Finder -一款非常好用的使用子域wordlist查找buckets的工具，可以把他集成到recon.rb脚本中。](https://image.3001.net/images/20180610/15286004636275.png!small)

## 个人的一些小建议总结：

> 关注twitter上的一些安全动态以及安全工程师或安全公司的推特；
>
> 大量阅读相关技术博文；
>
> （如在可行的情况下）以正常用户身份使用目标公司服务；
>
> 阅读Github上commits 和 public issues 下的讨论；
>
> 浏览robots.txt文件；
>
> 熟悉并尽可能利用公司DEV栈；
>
> 在YouTube或其他平台上观看目标公司的视频，包括新产品、演示、会议等；
>
> 在Pastebin和trello等平台上搜索目标信息；
>
> 使用搜索引擎dork搜索swf, txt, xml等文件；

 ***参考来源：[medium](https://medium.com/securityescape/recon-my-way-82b7e5f62e21)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

