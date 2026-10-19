*****本文原创作者：charm1y，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

 **本文浅略地分析了挖矿行为的流量特征，在suricata下使用相应检测规则发现挖矿行为。**  

## 挖矿木马的现状

随着加密货币的出现以及带来的实际收益，挖矿木马成为黑产团伙的主要获利方式之一，也成为了企业内部安全的主要威胁之一。在内网中遇到出现挖矿木马的原因一般分为服务器感染木马、PC感染木马、网页挖矿脚本等，很多僵尸网络也把挖矿作为主要的获利手段。由此对挖矿木马的检测能力成为了内网安全中比较重要的一部分。

## 挖矿行为的流量特征

挖矿行为的识别可以通过很多方面进行判断，终端层面监控硬件资源的使用率，及相关进程分析；流量层面通过识别挖矿行为的流量特征，从流量中识别出挖矿行为。本文中主要从流量层面去识别挖矿行为。

stratum协议是目前主流的矿机和矿池之间的TCP通讯协议，通过检测stratum协议来发现挖矿行为是行之有效的。stratum协议为JSON的数据格式，分析矿机与矿池之间使用stratum协议的通信过程，如下：

![Miner_communication.png](https://image.3001.net/images/20190127/1548588503_5c4d95d73d250.png!small)

通信过程主要分为矿机登记、任务下发、账号登录、结果提交与难度调整等部分。

矿机登记以mining.subscribe方法向矿池连接：

    
    
    {"id":1,"method":"mining.subscribe","params":[]}

矿池以mining.notify方法返回相关信息：  

    
    
    {"id":1,"result":[["mining.notify","ae6812eb4cd7735a302a8a9dd95cf71f"],"08000002",4],"error":null}

账号登录一般分为两种，一种是直接登录，另一种是通过jsonrpc方式（很多挖矿节点与矿池的通信是依靠jsonrpc来进行请求与相应的，这种方式也是依赖于TCP的Stratum协议）。

矿机直接通过mining.authorize方法登录：

    
    
    {"params":["miner1","password"],"id":2,"method":"mining.authorize"}

通过jsonrpc方式登录：  

    
    
    {"id":1,"jsonrpc":"2.0","method":"login","params":{"login":"blue1","pass":"x","agent":"Windows NT 6.1; Win64; x64"}}

结果提交通过"mining.submit"方法向矿池提交任务：  

    
    
    {"params":["miner1","bf","00000001","504e86ed","b2957c02"],"id":4,"method":"mining.submit"}

难度调整以mining.set_difficulty方法调整难度：  

    
    
    {"id":null,"method":"mining.set_difficulty","params":[2]}

分许上面json内容，主要特征字段有id、method、jsonrpc、params、result、login、pass、agent、mining.submit等，通过对具体通信数据包进行相应特征字符串检测，以此来发现挖矿行为的存在。而网页挖矿行为也可以通过检测coinhive.min.js等特征字符串来发现。  

## 挖矿行为的特征检测

由于门罗币具有匿名性、CPU挖矿、价值靠前等特点，所以成为挖矿木马的首选，平常实际工作遇见的挖矿木马挖取的加密货币也几乎都是门罗币。故以门罗币为例，通过suricata来检测其流量特征，进而发现流量中存在的挖矿行为。

门罗币采用Cryptonight算法，公开提供的程序有xmr-stak，xmrig，claymore等，相应的主要流量请求特征为：

### xmr-stak

request：

    
    
    {"method":"login","params":{"login":"xxxxxxx","pass":"xxx","rigid":"","agent":"xxxxxx"},"id":1}
    
    {"method":"submit","params":{"id":"xx","job_id":"xxxxxx","nonce":"xxxxx","result":"xxxxxx"},"id":1}

response：

    
    
    {"method":"job","params":{"target":"xxxxx","job_id":"xxxxxx","blob":"xxxxxxx"}}

### xmrig

request：

    
    
    {"id":x,"jsonrpc":"2.0","method":"login","params":{"login":"xxxxxx","pass":"x","agent":"xxxxx","algo":["xxx","xxx","xxx"]}}
    
    {"id":x,"jsonrpc":"2.0","method":"submit","params":{"id":"xxxx","job_id":"xx","nonce":"xxxx","result":"xxxxxxx"}}

response：

    
    
    {"params":{"blob":"xxxxxx","taget":"xxxx","job_id":"xxxxx"},"method":"xxx"}

### claymore

request：

    
    
    {"method":"login","params":{"login":"xxxxxx","pass":"x","agent":"xxx"},"id":1}
    
    {"method":"submit","params":{"id":"xxxx","job_id":"xxx","nonce":"xxxxx","result":"xxxxx"},"id":x}

response：

    
    
    {"params":{"blob":"xxxxxx","target":"xxxx","job_id":"xxx"},"method":"xxx"}

对上面的流量请求特征分析可以发现，请求中主要分为login操作与submit操作,对具体请求具体分析。login操作可以分为直接使用stratum协议与通过jsonrpc方式，suricata本身有相应检测规则：  

    
    
    alert tcp $HOME_NET any -> $EXTERNAL_NET any (msg:"ET POLICY Crypto Coin Miner Login"; flow:to_server,established; content:"|7b 22|method|22 3a|"; depth:10; fast_pattern; content:"|22|login|22 2c|"; distance:0; within:9; content:"|22|params|22 3a|"; distance:0; within:10; content:"|7b 22|login"; nocase; distance:0; within:8; content:"agent|22 3a|"; nocase; distance:0; metadata: former_category POLICY; reference:md5,d1082e445f932938366a449631b82946; reference:md5,33d7a82fe13c9737a103bcc4a21f9425; reference:md5,ebe1aeb5dd692b222f8cf964e7785a55; classtype:trojan-activity; sid:2022886; rev:3; metadata:affected_product Any, attack_target Client_Endpoint, deployment Perimeter, tag Bitcoin_Miner, signature_severity Audit, created_at 2016_06_09, malware_family CoinMiner, performance_impact Low, updated_at 2017_10_12;)
    
    
    alert tcp-pkt $HOME_NET any -> $EXTERNAL_NET any (msg:"ET POLICY Cryptocurrency Miner Checkin"; flow:established,to_server; content:"|7b 22|id|22 3a|"; nocase; depth:6; content:"|22|jsonrpc|22 3a|"; nocase; distance:0; content:"|22 2c 22|method|22 3a 22|login|22 2c 22|params|22 3a|"; fast_pattern; content:"|22|pass|22 3a 22|"; nocase; content:"|22|agent|22 3a 22|"; nocase; content:!"<title"; nocase; content:!"<script"; nocase; content:!"<html"; nocase; metadata: former_category POLICY; classtype:policy-violation; sid:2024792; rev:4; metadata:affected_product Windows_XP_Vista_7_8_10_Server_32_64_Bit, attack_target Client_Endpoint, deployment Perimeter, signature_severity Minor, created_at 2017_10_02, updated_at 2018_06_15;)

对submit操作可以分析，可以使用以下规则进行检测：  

    
    
    alert tcp $HOME_NET any -> $EXTERNAL_NET any (msg:"Cryptocurrency Miner Check By Submit"; flow:to_server,established; content:"|22|method|22 3a|"; fast_pattern; content:"|22|submit|22 2c|"; distance:0; within:10; content:"|22|params|22 3a 7b|"; distance:0; within:15; content:"result|22 3a|"; nocase; distance:0; sid:3013015; rev:1; metadata:Detecting Mining Rules;

矿池响应矿工的流量检测规则：  

    
    
    alert tcp $EXTERNAL_NET any -> $HOME_NET any (msg:"Pools Response Cryptocurrency Miner"; flow:to_client,established; content:"|22|method|22 3a|"; nocase; content:"|22|params|22 3a|"; nocase; content:"|22|blob|22 3a|"; nocase; content:"|22|job_id|22 3a|"; nocase; sid:3013016; rev:1; metadata:Detecting Mining Rules;)

通过对规则进行分析，以上规则所匹配的字符串及其相互位置关系正好符合前面门罗币的流量请求特征。由此可以使用suricata加载以上规则来检测挖矿流量。

网页挖矿行为也可以通过以下规则进行检测：

    
    
    alert http $EXTERNAL_NET any -> $HOME_NET any (msg:"ET CURRENT_EVENTS CoinHive In-Browser Miner Detected"; flow:established,from_server; file_data; content:"coinhive.min.js"; nocase; fast_pattern; content:"start"; nocase; distance:0; content:"script"; content:"var"; distance:0; pcre:"/^\s*(?P<var>[a-zA-Z0-9]{3,20})\s*=\s*new\s*CoinHive\s*\.\s*[^\(]+\(\s*[\x22\x27][A-Za-z0-9]+\s*[\x22\x27]\s*(?:\x2c\s*\x7b\s*\w+\x3a\s*\d\.\d\x7d)?\)\s*\x3b\s+(?P=var)\s*\.\s*start/Ri"; metadata: former_category CURRENT_EVENTS; classtype:policy-violation; sid:2024721; rev:2; metadata:affected_product Any, attack_target Client_Endpoint, deployment Perimeter, signature_severity Minor, created_at 2017_09_18, performance_impact Moderate, updated_at 2018_05_08;)

通过以上规则来检测内网流量，基本可以发现绝大多数的挖矿行为。以一个实际例子来说明，最近遇到在虚拟机中使用网上的Windows激活工具导致感染挖矿木马，具体情况为通过suricata进行流量分析，挖矿木马的挖矿行为触发相关规则告警。  

![Miner_detection.png](https://image.3001.net/images/20190127/1548588848_5c4d97307c9fb.png!small)

通过溯源找到受害机器，对受害机器进行应急处置，之后详细过程跟本文关系不大，就不说明了。要提到的一点是挖矿进程的commandLine为：

    
    
    -a cryptonight -o stratum+tcp://xmr.pool.minergate.com:45560 -u minepool@gmx.com -p x -t 1

可以发现挖矿进程与矿池的连接采用的是stratum+tcp的协议进行通信，其恶意流量也就命中了相应的检测规则，从而触发告警，发现挖矿行为的存在。实际工作中检测到server端的流量，往往比检测到client端的流量更有效，具体原因在于server端有时对请求不一定都有响应操作，或响应不一定能返回成功。  

## 总结

通过以上的方式，基本能够发现大多数的挖矿行为，但有些情况还是检测不到的。比如曾经遇到过的OneSystemCare挖矿木马对挖矿协议进行全部加密，所以无法通过检测相应挖矿流量发现其恶意行为。实际发现过程为监控IOC的访问情况，发现有内网IP恶意连接IOC，最终通过溯源分析发现感染挖矿木马。

对于把挖矿协议进行加密的情况，目前感觉流量监控方向上好的处理方式有对矿池的连接监控、IOC的访问监控等手段进行防护。
但真实存在的情况多种多样，如何有效的从流量中发现恶意行为，必将是一个长期对抗的过程。

 ***本文原创作者：charm1y，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

