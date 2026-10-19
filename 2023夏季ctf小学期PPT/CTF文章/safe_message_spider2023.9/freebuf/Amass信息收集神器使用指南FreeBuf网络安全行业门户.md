OWASP Amass项目使用开源信息收集和主动侦察技术，对攻击面和外部资产发现进行网络映射。

Technique| Data Sources  
---|---  
APIs| 360PassiveDNS, Ahrefs, AnubisDB, BinaryEdge, BufferOver, BuiltWith, C99,
Chaos, CIRCL, Cloudflare, DNSDB, DNSRepo, Detectify, FOFA, FullHunt, GitHub,
GitLab, Greynoise, HackerTarget, Hunter, IntelX, LeakIX, Maltiverse, Mnemonic,
N45HT, PassiveTotal, PentestTools, Quake, Shodan, SonarSearch, Spamhaus,
Spyse, Sublist3rAPI, ThreatBook, ThreatCrowd, ThreatMiner, Twitter, URLScan,
VirusTotal, ZETAlytics, ZoomEye  
Certificates| Active pulls (optional), Censys, CertSpotter, Crtsh, Digitorus,
FacebookCT, GoogleCT  
DNS| Brute forcing, Reverse DNS sweeping, NSEC zone walking, Zone transfers,
FQDN alterations/permutations, FQDN Similarity-based Guessing  
Routing| ARIN, BGPTools, BGPView, IPdata, IPinfo, NetworksDB, RADb, Robtex,
ShadowServer, TeamCymru  
Scraping| AbuseIPDB, Ask, Baidu, Bing, DNSDumpster, DuckDuckGo, Gists,
HackerOne, HyperStat, IPv4Info, PKey, RapidDNS, Riddler, Searchcode, Searx,
SiteDossier, Yahoo  
Web Archives| ArchiveIt, Arquivo, CommonCrawl, HAW, UKWebArchive, Wayback  
WHOIS| AlienVault, AskDNS, DNSlytics, ONYPHE, SecurityTrails, SpyOnWeb,
Umbrella, WhoisXMLAPI  
  
## 安装使用

    
    
    https://github.com/OWASP/Amass/releases  
  
---  
  
![Amass](https://image.3001.net/images/20220926/1664165113_633124f9b84007688ed11.png!small)

  

    
    
    vulab@sechelper:~/amass_linux_amd64$ ./amass -version  
    v3.19.3  
  
---  
  
 **枚举域名**

    
    
    amass enum -v -src -ip -brute -min-for-recursive 2 -d example.com  
  
---  
  
## 命令行用法信息

amass工具有几个子命令，如下所示，用于处理您的互联网曝光调查。

Subcommand| Description  
---|---  
intel| 收集开源情报以调查目标组织  
enum| 对暴露于Internet的系统执行DNS枚举和网络映射  
viz| 生成用于探索性分析的枚举可视化  
track| 将枚举结果与常见目标组织进行比较  
db| 管理存储枚举结果的图形数据库  
  
## 子命令参数

### intel

intel子命令可以帮助您发现与您正在调查的组织相关联的其他根域名。此子命令使用配置文件的数据源部分来获取被动情报，例如反向whois信息。

Flag| Description| Example  
---|---|---  
-active| Enable active recon methods| amass intel -active -addr 192.168.2.1-64 -p 80,443,8080  
-addr| IPs and ranges (192.168.1.1-254) separated by commas| amass intel -addr 192.168.2.1-64  
-asn| ASNs separated by commas (can be used multiple times)| amass intel -asn 13374,14618  
-cidr| CIDRs separated by commas (can be used multiple times)| amass intel -cidr 104.154.0.0/15  
-config| Path to the INI configuration file| amass intel -config config.ini  
-d| Domain names separated by commas (can be used multiple times)| amass intel -whois -d [example.com](http://example.com)  
-demo| Censor output to make it suitable for demonstrations| amass intel -demo -whois -d [example.com](http://example.com)  
-df| Path to a file providing root domain names| amass intel -whois -df domains.txt  
-dir| Path to the directory containing the graph database| amass intel -dir PATH -cidr 104.154.0.0/15  
-ef| Path to a file providing data sources to exclude| amass intel -whois -ef exclude.txt -d [example.com](http://example.com)  
-exclude| Data source names separated by commas to be excluded| amass intel -whois -exclude crtsh -d [example.com](http://example.com)  
-if| Path to a file providing data sources to include| amass intel -whois -if include.txt -d [example.com](http://example.com)  
-include| Data source names separated by commas to be included| amass intel -whois -include crtsh -d [example.com](http://example.com)  
-ip| Show the IP addresses for discovered names| amass intel -ip -whois -d [example.com](http://example.com)  
-ipv4| Show the IPv4 addresses for discovered names| amass intel -ipv4 -whois -d [example.com](http://example.com)  
-ipv6| Show the IPv6 addresses for discovered names| amass intel -ipv6 -whois -d [example.com](http://example.com)  
-list| Print the names of all available data sources| amass intel -list  
-log| Path to the log file where errors will be written| amass intel -log amass.log -whois -d [example.com](http://example.com)  
-max-dns-queries| Maximum number of concurrent DNS queries| amass intel -max-dns-queries 200 -whois -d [example.com](http://example.com)  
-o| Path to the text output file| amass intel -o out.txt -whois -d [example.com](http://example.com)  
-org| Search string provided against AS description information| amass intel -org Facebook  
-p| Ports separated by commas (default: 80, 443)| amass intel -cidr 104.154.0.0/15 -p 443,8080  
-r| IP addresses of preferred DNS resolvers (can be used multiple times)| amass intel -r 8.8.8.8,1.1.1.1 -whois -d [example.com](http://example.com)  
-rf| Path to a file providing preferred DNS resolvers| amass intel -rf data/resolvers.txt -whois -d [example.com](http://example.com)  
-src| Print data sources for the discovered names| amass intel -src -whois -d [example.com](http://example.com)  
-timeout| Number of minutes to execute the enumeration| amass intel -timeout 30 -d [example.com](http://example.com)  
-whois| All discovered domains are run through reverse whois| amass intel -whois -d [example.com](http://example.com)  
  
 **参考：**

[whois反查](https://baike.baidu.com/item/Whois%E5%8F%8D%E6%9F%A5/9453218)

### enum

此子命令将在填充选定的图形数据库时执行DNS枚举和网络映射。配置文件中的所有可用设置都与此子命令相关。以下标志可用于配置：

Flag| Description| Example  
---|---|---  
-active| Enable active recon methods| amass enum -active -d [example.com](http://example.com)-p 80,443,8080  
-aw| Path to a different wordlist file for alterations| amass enum -aw PATH -d [example.com](http://example.com)  
-bl| Blacklist of subdomain names that will not be investigated| amass enum -bl [blah.example.com](http://blah.example.com)-d [example.com](http://example.com)  
-blf| Path to a file providing blacklisted subdomains| amass enum -blf data/blacklist.txt -d [example.com](http://example.com)  
-brute| Perform brute force subdomain enumeration| amass enum -brute -d [example.com](http://example.com)  
-config| Path to the INI configuration file| amass enum -config config.ini  
-d| Domain names separated by commas (can be used multiple times)| amass enum -d [example.com](http://example.com)  
-demo| Censor output to make it suitable for demonstrations| amass enum -demo -d [example.com](http://example.com)  
-df| Path to a file providing root domain names| amass enum -df domains.txt  
-dir| Path to the directory containing the graph database| amass enum -dir PATH -d [example.com](http://example.com)  
-ef| Path to a file providing data sources to exclude| amass enum -ef exclude.txt -d [example.com](http://example.com)  
-exclude| Data source names separated by commas to be excluded| amass enum -exclude crtsh -d [example.com](http://example.com)  
-if| Path to a file providing data sources to include| amass enum -if include.txt -d [example.com](http://example.com)  
-include| Data source names separated by commas to be included| amass enum -include crtsh -d [example.com](http://example.com)  
-ip| Show the IP addresses for discovered names| amass enum -ip -d [example.com](http://example.com)  
-ipv4| Show the IPv4 addresses for discovered names| amass enum -ipv4 -d [example.com](http://example.com)  
-ipv6| Show the IPv6 addresses for discovered names| amass enum -ipv6 -d [example.com](http://example.com)  
-json| Path to the JSON output file| amass enum -json out.json -d [example.com](http://example.com)  
-list| Print the names of all available data sources| amass enum -list  
-log| Path to the log file where errors will be written| amass enum -log amass.log -d [example.com](http://example.com)  
-max-dns-queries| Deprecated flag to be replaced by dns-qps in version 4.0| amass enum -max-dns-queries 200 -d [example.com](http://example.com)  
-dns-qps| Maximum number of DNS queries per second across all resolvers| amass enum -dns-qps 200 -d [example.com](http://example.com)  
-rqps| Maximum number of DNS queries per second for each untrusted resolver| amass enum -rqps 10 -d [example.com](http://example.com)  
-trqps| Maximum number of DNS queries per second for each trusted resolver| amass enum -trqps 20 -d [example.com](http://example.com)  
-min-for-recursive| Subdomain labels seen before recursive brute forcing (Default: 1)| amass enum -brute -min-for-recursive 3 -d [example.com](http://example.com)  
-max-depth| Maximum number of subdomain labels for brute forcing| amass enum -brute -max-depth 3 -d [example.com](http://example.com)  
-nf| Path to a file providing already known subdomain names (from other tools/sources)| amass enum -nf names.txt -d [example.com](http://example.com)  
-noalts| Disable generation of altered names| amass enum -noalts -d [example.com](http://example.com)  
-norecursive| Turn off recursive brute forcing| amass enum -brute -norecursive -d [example.com](http://example.com)  
-o| Path to the text output file| amass enum -o out.txt -d [example.com](http://example.com)  
-oA| Path prefix used for naming all output files| amass enum -oA amass_scan -d [example.com](http://example.com)  
-passive| A purely passive mode of execution| amass enum --passive -d [example.com](http://example.com)  
-p| Ports separated by commas (default: 443)| amass enum -d [example.com](http://example.com)-p 443,8080  
-r| IP addresses of untrusted DNS resolvers (can be used multiple times)| amass enum -r 8.8.8.8,1.1.1.1 -d [example.com](http://example.com)  
-tr| IP addresses of trusted DNS resolvers (can be used multiple times)| amass enum -tr 8.8.8.8,1.1.1.1 -d [example.com](http://example.com)  
-rf| Path to a file providing untrusted DNS resolvers| amass enum -rf data/resolvers.txt -d [example.com](http://example.com)  
-trf| Path to a file providing trusted DNS resolvers| amass enum -trf data/trusted.txt -d [example.com](http://example.com)  
-src| Print data sources for the discovered names| amass enum -src -d [example.com](http://example.com)  
-timeout| Number of minutes to execute the enumeration| amass enum -timeout 30 -d [example.com](http://example.com)  
-w| Path to a different wordlist file| amass enum -brute -w wordlist.txt -d [example.com](http://example.com)  
  
### viz

创建具有启发性的网络图形可视化，为收集的信息添加结构。此子命令仅利用配置文件中的`output_directory`和远程图形数据库设置。

为可视化而生成的文件在当前工作目录中创建，名为amass_TYPE

将DNS和基础结构结果输出为网络图的交换机：

Flag| Description| Example  
---|---|---  
-config| Path to the INI configuration file| amass viz -config config.ini -d3  
-d| Domain names separated by commas (can be used multiple times)| amass viz -d3 -d [example.com](http://example.com)  
-d3| Output a D3.js v4 force simulation HTML file| amass viz -d3 -d [example.com](http://example.com)  
-df| Path to a file providing root domain names| amass viz -d3 -df domains.txt  
-dir| Path to the directory containing the graph database| amass viz -d3 -dir PATH -d [example.com](http://example.com)  
-enum| Identify an enumeration via an index from the db listing| amass viz -enum 1 -d3 -d [example.com](http://example.com)  
-o| Path to a pre-existing directory that will hold output files| amass viz -d3 -o OUTPATH -d [example.com](http://example.com)  
-oA| Prefix used for naming all output files| amass viz -d3 -oA example -d [example.com](http://example.com)  
-gexf| Output to Graph Exchange XML Format (GEXF)| amass viz -gexf -d [example.com](http://example.com)  
-graphistry| Output Graphistry JSON| amass viz -graphistry -d [example.com](http://example.com)  
-i| Path to the Amass data operations JSON input file| amass viz -d3 -d [example.com](http://example.com)  
-maltego| Output a Maltego Graph Table CSV file| amass viz -maltego -d [example.com](http://example.com)  
  
### track

显示包含相同目标的枚举之间的差异，以监视目标的攻击面。此子命令仅利用配置文件中的“output_directory”和远程图形数据库设置。用于跨图形数据库中的枚举执行Internet暴露监视的标志：

Flag| Description| Example  
---|---|---  
-config| Path to the INI configuration file| amass track -config config.ini  
-d| Domain names separated by commas (can be used multiple times)| amass track -d [example.com](http://example.com)  
-df| Path to a file providing root domain names| amass track -df domains.txt  
-dir| Path to the directory containing the graph database| amass track -dir PATH  
-history| Show the difference between all enumeration pairs| amass track -history  
-last| The number of recent enumerations to include in the tracking| amass track -last NUM  
-since| Exclude all enumerations before a specified date (format: 01/02 15:04:05 2006 MST)| amass track -since DATE  
  
### db

执行图形数据库的查看和操作。此子命令仅利用配置文件中的“output_directory”和远程图形数据库设置。与图形数据库中的枚举结果交互的标志包括：

Flag| Description| Example  
---|---|---  
-config| Path to the INI configuration file| amass db -config config.ini  
-d| Domain names separated by commas (can be used multiple times)| amass db -d [example.com](http://example.com)  
-demo| Censor output to make it suitable for demonstrations| amass db -demo -d [example.com](http://example.com)  
-df| Path to a file providing root domain names| amass db -df domains.txt  
-dir| Path to the directory containing the graph database| amass db -dir PATH  
-enum| Identify an enumeration via an index from the listing| amass db -enum 1 -show  
-import| Import an Amass data operations JSON file to the graph database| amass db -import PATH  
-ip| Show the IP addresses for discovered names| amass db -show -ip -d [example.com](http://example.com)  
-ipv4| Show the IPv4 addresses for discovered names| amass db -show -ipv4 -d [example.com](http://example.com)  
-ipv6| Show the IPv6 addresses for discovered names| amass db -show -ipv6 -d [example.com](http://example.com)  
-json| Path to the JSON output file or ‘-’| amass db -names -silent -json out.json -d [example.com](http://example.com)  
-list| Print enumerations in the database and filter on domains specified| amass db -list  
-names| Print just discovered names| amass db -names -d [example.com](http://example.com)  
-nocolor| Disable colorized output| amass db -names -nocolor -d [example.com](http://example.com)  
-o| Path to the text output file| amass db -names -o out.txt -d [example.com](http://example.com)  
-show| Print the results for the enumeration index + domains provided| amass db -show  
-silent| Disable all output during execution| amass db -names -silent -json out.json -d [example.com](http://example.com)  
-src| Print data sources for the discovered names| amass db -show -src -d [example.com](http://example.com)  
-summary| Print just ASN table summary| amass db -summary -d [example.com](http://example.com)  
  
## 输出结果保存

mass在枚举过程中输出多个文件（例如日志文件）。如果您没有使用数据库服务器来存储网络图形信息，那么Amass会在输出目录中创建一个基于文件的图形数据库。在未来的枚举过程中，以及在利用跟踪和可视化等功能时，将再次使用这些文件。

默认情况下，输出目录是在操作系统默认根目录中创建的，用于用户特定的配置数据，名为`*amass*`。如果这不适合您的需要，那么可以指示子命令使用**-dir**标志在其他位置创建输出目录。

如果您决定使用Amass配置文件，当将其放入输出目录并命名为 **config.ini** 时，将自动发现它。

