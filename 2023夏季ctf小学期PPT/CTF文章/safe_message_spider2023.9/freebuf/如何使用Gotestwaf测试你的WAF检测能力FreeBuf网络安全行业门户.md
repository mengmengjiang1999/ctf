![](https://image.3001.net/images/20210414/1618381607_60768b27e1abcf60eca22.jpg!small)

## 关于Gotestwaf

Gotestwaf，全称为Go Test
WAF，该工具可以使用不同类型的攻击技术和绕过技术来测试你Web应用程序防火墙的检测能力。Gotestwaf是一个基于Go开发的开源项目，它实现了一种三步请求生成过程，可以对编码器和占位符的Payload进行相乘操作。假设你定义了2个Payload、3个编码器（Base64、JSON和URLencode）和1个占位符（HTTP
GET变量）。在这种情况下，Gotestwaf将在测试用例中发送2*3*1=6个请求。

### Payload

你可以发送的Payload字符串，支持比如说<script>alert(111)</script>或其他更复杂的东西。当前版本的Gotestwaf还不支持类似宏这样的功能，但我们之后会添加相关支持。由于这是一个YAML字符串，因此你还可以使用二进制编码，具体请参考https://yaml.org/type/binary.html。

### 编码器

数据编码器工具应适用于Payload，支持Base64和JSON Unicode编码（\u0027代替’）等。

### 占位符

占位符位于HTTP请求中，用于存放已编码的Payload。比如说URL参数、URI、POST表单参数或JSON POST主体。

## 工具安装

### DockerHub

最新版本的Gotestwaf可以通过DockerHub库直接获取：https://hub.docker.com/r/wallarm/gotestwaf。

我们可以直接使用下列命令将项目库拉取到本地：

    
    
    docker pull wallarm/gotestwaf

### 本地Docker构建

    
    
    docker build . --force-rm -t gotestwaf
    
    docker run -v ${PWD}/reports:/go/src/gotestwaf/reports gotestwaf --url=https://the-waf-you-wanna-test/

运行命令之后，你将会在reports文件夹下查看到waf-test-report-<date>.pdf报告文件，你也可以将其映射到容器中的/go/src/gotestwaf/reports处。

### 代码构建

Gotestwaf支持在目前常见的操作系统平台上运行，包括Linux、Windows和macOS，我们可以直接在安装了Go环境的系统上进行源码编译和构建：

    
    
    go build -mod vendor

## 工具配置选项

    
    
    Usage of /go/src/gotestwaf/gotestwaf:
    
          --blockRegex string      Regex to detect a blocking page with the same HTTP response status code as a not blocked request
    
          --blockStatusCode int    HTTP status code that WAF uses while blocking requests (default 403)
    
          --configPath string      Path to the config file (default "config.yaml")
    
          --followCookies          If true, use cookies sent by the server. May work only with --maxIdleConns=1
    
          --idleConnTimeout int    The maximum amount of time a keep-alive connection will live (default 2)
    
          --maxIdleConns int       The maximum number of keep-alive connections (default 2)
    
          --maxRedirects int       The maximum number of handling redirects (default 50)
    
          --nonBlockedAsPassed     If true, count requests that weren't blocked as passed. If false, requests that don't satisfy to PassStatuscode/PassRegExp as blocked
    
          --passRegex string       Regex to a detect normal (not blocked) web page with the same HTTP status code as a blocked request
    
          --passStatusCode int     HTTP response status code that WAF uses while passing requests (default 200)
    
          --proxy string           Proxy URL to use
    
          --randomDelay int        Random delay in ms in addition to the delay between requests (default 400)
    
          --reportPath string      A directory to store reports (default "reports")
    
          --sendDelay int          Delay in ms between requests (default 400)
    
          --testCase string        If set then only this test case will be run
    
          --testCasesPath string   Path to a folder with test cases (default "testcases")
    
          --testSet string         If set then only this test set's cases will be run
    
          --tlsVerify              If true, the received TLS certificate will be verified
    
          --url string             URL to check (default "http://localhost/")
    
          --verbose                If true, enable verbose logging (default true)
    
          --wafName string         Name of the WAF product (default "generic")
    
          --workers int            The number of workers to scan (default 200)
    
          --wsURL string           WebSocket URL to check

## 工具使用样例

### 测试OWASP ModSecurity核心规则集（CRS）

首先，我们需要构建&运行ModSecurity CRS Docker镜像。我们可以使用下列命令自动拉取、构建和运行ModSecurity CRS
Docker镜像：

    
    
    make modsec

或者，你也可以手动配置参数并进行测试：

    
    
    docker pull owasp/modsecurity-crs
    
    docker run -p 8080:80 -d -e PARANOIA=1 --rm owasp/modsecurity-crs

你还可以选择PARANOIA等级来提升测试的安全等级，具体请参考https://coreruleset.org/faq/。

接下来，我们需要使用下列命令来对ModSecurity CRS Docker镜像的安全性进行测试：

    
    
    make scan_local               (to run natively)
    
    make scan_local_from_docker   (to run from docker)

或者，在Docker中手动执行：

    
    
    docker run -v ${PWD}/reports:/go/src/gotestwaf/reports --network="host" gotestwaf --url=http://127.0.0.1:8080/ --verbose

或者，使用下列命令手动运行测试（本地）：

    
    
    go run ./cmd --url=http://127.0.0.1:8080/ --verbose

我们还可以通过wsURL和verbose参数来添加额外的WebSocket URL检测，其中会包含目标进程的详细信息：

    
    
    docker run -v ${PWD}/reports:/go/src/gotestwaf/reports gotestwaf --url=http://172.17.0.1:8080/ --wsURL=ws://172.17.0.1:8080/api/ws --verbose

Gotestwaf的检测结果输出如下：

    
    
    GOTESTWAF : 2021/03/03 15:15:48.072331 main.go:61: Test cases loading started
    
    GOTESTWAF : 2021/03/03 15:15:48.077093 main.go:68: Test cases loading finished
    
    GOTESTWAF : 2021/03/03 15:15:48.077123 main.go:74: Scanned URL: http://127.0.0.1:8080/
    
    GOTESTWAF : 2021/03/03 15:15:48.083134 main.go:85: WAF pre-check: OK. Blocking status code: 403
    
    GOTESTWAF : 2021/03/03 15:15:48.083179 main.go:97: WebSocket pre-check. URL to check: ws://127.0.0.1:8080/
    
    GOTESTWAF : 2021/03/03 15:15:48.251824 main.go:101: WebSocket pre-check: connection is not available, reason: websocket: bad handshake
    
    GOTESTWAF : 2021/03/03 15:15:48.252047 main.go:129: Scanning http://127.0.0.1:8080/
    
    GOTESTWAF : 2021/03/03 15:15:48.252076 scanner.go:124: Scanning started
    
    GOTESTWAF : 2021/03/03 15:15:51.210216 scanner.go:129: Scanning Time:  2.958076338s
    
    GOTESTWAF : 2021/03/03 15:15:51.210235 scanner.go:160: Scanning finished
    
     
    
    Negative Tests:
    
    +-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
    
    |       TEST SET        |       TEST CASE       |     PERCENTAGE, %     |        BLOCKED        |       BYPASSED        |      UNRESOLVED       |
    
    +-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
    
    | community             | community-lfi         |                 66.67 |                     4 |                     2 |                     0 |
    
    | community             | community-rce         |                 14.29 |                     6 |                    36 |                     0 |
    
    | community             | community-sqli        |                 70.83 |                    34 |                    14 |                     0 |
    
    | community             | community-xss         |                 91.78 |                   279 |                    25 |                     0 |
    
    | community             | community-xxe         |                100.00 |                     4 |                     0 |                     0 |
    
    | owasp                 | ldap-injection        |                  0.00 |                     0 |                     8 |                     0 |
    
    | owasp                 | mail-injection        |                  0.00 |                     0 |                     6 |                     6 |
    
    | owasp                 | nosql-injection       |                  0.00 |                     0 |                    12 |                     6 |
    
    | owasp                 | path-traversal        |                 38.89 |                     7 |                    11 |                     6 |
    
    | owasp                 | shell-injection       |                 37.50 |                     3 |                     5 |                     0 |
    
    | owasp                 | sql-injection         |                 33.33 |                     8 |                    16 |                     8 |
    
    | owasp                 | ss-include            |                 50.00 |                     5 |                     5 |                    10 |
    
    | owasp                 | sst-injection         |                 45.45 |                     5 |                     6 |                     9 |
    
    | owasp                 | xml-injection         |                100.00 |                    12 |                     0 |                     0 |
    
    | owasp                 | xss-scripting         |                 56.25 |                     9 |                     7 |                    12 |
    
    | owasp-api             | graphql               |                100.00 |                     1 |                     0 |                     0 |
    
    | owasp-api             | rest                  |                100.00 |                     2 |                     0 |                     0 |
    
    | owasp-api             | soap                  |                100.00 |                     2 |                     0 |                     0 |
    
    +-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
    
    |         DATE:         |       WAF NAME:       |  WAF AVERAGE SCORE:   |  BLOCKED (RESOLVED):  | BYPASSED (RESOLVED):  |      UNRESOLVED:      |
    
    |      2021-03-03       |        GENERIC        |        55.83%         |   381/534 (71.35%)    |   153/534 (28.65%)    |    57/591 (9.64%)     |
    
    +-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
    
     
    
    Positive Tests:
    
    +-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
    
    |       TEST SET        |       TEST CASE       |     PERCENTAGE, %     |        BLOCKED        |       BYPASSED        |      UNRESOLVED       |
    
    +-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
    
    | false-pos             | texts                 |                 50.00 |                     1 |                     1 |                     6 |
    
    +-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
    
    |         DATE:         |       WAF NAME:       |  WAF POSITIVE SCORE:  | FALSE POSITIVE (RES): | TRUE POSITIVE (RES):  |      UNRESOLVED:      |
    
    |      2021-03-03       |        GENERIC        |        50.00%         |     1/2 (50.00%)      |     1/2 (50.00%)      |     6/8 (75.00%)      |
    
    +-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
    
     
    
    PDF report is ready: reports/waf-evaluation-report-generic-2021-March-03-15-15-51.pdf

## 项目地址

 **Gotestwaf：** https://github.com/wallarm/gotestwaf

## 参考资料

https://yaml.org/type/binary.html

https://hub.docker.com/r/wallarm/gotestwaf

https://coreruleset.org/faq/

