三月十四，疫情肆虐。居陋（寝）室闲谈，恍惚之间，适逢客与余论渗透测试工具——feroxbuster。至日铺，方觉有兴，遂翻书阅卷无数。可惜“竹帛”少有，便"逾墙"查找,后汇聚成此文。

## 0X01feroxbuster安装

### Kali 安装：

> 使用sudo apt update && sudo apt install -y
> feroxbuster安装即可，如果出现安装失败的情况，可以更据提示进行修复

### windows 安装：

下载Git后使用 **git clone命令** 拷贝或者

> #下载  
> Invoke-WebRequest
> https://github.com/epi052/feroxbuster/releases/latest/download/x86_64-windows-> feroxbuster.exe.zip -OutFile feroxbuster.zip  
> #解压  
> Expand-Archive .\feroxbuster.zip  
> #使用  
> .\feroxbuster\feroxbuster.exe -V

### MAC

> 使用Homebrew安装；输入brew install feroxbuster命令即可

## 0X02feroxbuster使用

### 命令行解析

命令行上给出的任何选项/参数都将影响扫描效果

> 使用命令:
>
> feroxbuster [选项]
>
> 帮助可选项:  
> -h, --help 显示命令信息  
> -V, --version 显示版本信息
>
>  
>
>
> 目标选择:  
> \--resume-from <STATE_FILE> 状态文件恢复，从中恢复部分完成扫描（例如——从ferox-1606586780.STATE恢复）  
> \--stdin 从stdin读取url  
> -u, --url <URL> 目标url（必需，除非使用[--stdin | |--resume from]）
>
>  
>
>
> 代理设置:  
> -p, --proxy <PROXY> 用于请求的代理（例如：http（s）：//主机：端口，socks5（h）：//主机：端口）  
>  
>
>
> 请求设置:  
> -a, --user-agent <USER_AGENT> 设置用户代理（默认值：feroxbuster/2.5.0）  
> -A, --random-agent 使用随机用户代理  
> -b, --cookies <COOKIE>... 指定每个请求中要使用的HTTP cookies（例如：-b stuff=things）  
> \--data <DATA> 请求的主体，如果输入以@（例如：@post.bin）开头，则可以从文件中读取数据  
> -f, --add-slash 在每个请求的URL中添加斜杠  
> -H, --headers <HEADER>... 指定每个请求中要使用的HTTP头（例如：-H Header:val-H'stuff:things'）  
> -m, --methods <HTTP_METHODS>... 应该发送哪些HTTP请求方法（默认值：GET）  
> -Q, --query <QUERY>... 请求的URL查询参数（例如：-Q token=stuff-Q secret=key）secret=key)  
> -x, --extensions <FILE_EXTENSION>... 要搜索的文件扩展名（例如：-x php-x pdf js）
>
>  
>
>
> 请求筛选器:  
> \--dont-scan <URL>... 要从递归/扫描中排除的URL或正则表达式模式
>
>  
>
>
> 响应过滤器:  
> -C, --filter-status <STATUS_CODE>... 过滤掉状态代码（拒绝列表）（例如：-C 200-C 401）  
> \--filter-similar-to <UNWANTED_PAGE>...
> 过滤掉与给定页面相似的页面（例如——过滤类似于http://site.xyz/soft404)  
> -N, --filter-lines <LINES>... 过滤掉特定行数的消息（例如：-N 20-N 31,30）  
> -s, --status-codes <STATUS_CODE>... 要包括的状态代码（允许列表）（默认值：200 204 301 302 307
> 308 401 403 405）  
> -S, --filter-size <SIZE>... 过滤掉特定大小的邮件（例如：-S 5120-S 49271970）  
> -W, --filter-words <WORDS>... 过滤掉特定字数的消息（例如：-W 312-W 91,82）  
> -X, --filter-regex <REGEX>... 通过响应正文上的正则表达式匹配过滤掉消息（例如：-X“^ignore me$”）
>
>  
>
>
> 客户端设置:  
> -k, --insecure 禁用客户端中的TLS证书验证  
> -r, --redirects 允许客户端跟踪重定向  
> -T, --timeout <SECONDS> 客户端请求超时前的秒数（默认值：7）
>
>  
>
>
> 扫描设置:  
> \--auto-bail 当遇到过多错误时，自动取款自动停止扫描  
> \--auto-tune 当遇到过多错误时，自动调整会自动降低扫描速率  
> -d, --depth <RECURSION_DEPTH> 最大递归深度，深度为0表示无限递归（默认值：4）  
> -D, --dont-filter 不自动筛选通配符响应  
> -e, --extract-links 从响应体中提取链接（html、javascript等）；根据调查结果提出新要求  
> -L, --scan-limit <SCAN_LIMIT> 限制并发扫描的总数（默认值：0，即无限制）  
> -n, --no-recursion 不进行递归扫描  
> \--parallel <PARALLEL_SCANS> 运行并行feroxbuster实例（通过stdin传递的每个url有一个子进程）  
> \--rate-limit <RATE_LIMIT> 限制每秒请求数（每个目录）（默认值：0，即无限制）  
> -t, --threads <THREADS> 并发线程数（默认值：50）  
> \--time-limit <TIME_SPEC> 限制所有扫描的总运行时间（例如：时间限制10米）  
> -w, --wordlist <FILE> 指向自己准备的字典
>
>  
>
>
> 输出设置:  
> \--debug-log <FILE> 输出文件以写入日志条目（json条目使用w/--json）  
> \--json 将json日志发送到--output和--debug log，而不是普通文本  
> -o, --output <FILE> 将结果写入的输出文件（使用w/--json作为json条目）  
> -q, --quiet 隐藏进度条和横幅（适用于带有通知的tmux windows）  
> \--silent 只打印URL+关闭日志记录(用于将URL列表转到其他命令)  
> -v, --verbosity 增加详细程度(使用-vv或更多，以获得更大的效果。[注意]4-v可能太多了)

 **注意：** 在kali中使用feroxbuster命令的时候可以使用`-字母`；也可以使用`--单词`来执行；同时需要对字典进行指定，否则执行失败

### Ferox-config.toml（与xray的文件修改相似）

想要修改feroxbuster的默认值，可以在`ferox-config.toml`配置文件中进行内置默认值修改

> 在feroxbuster文件夹中找到ferox-config.toml在下列地点(按所示的顺序)：  
> /etc/feroxbuster/(全球)  
> CONFIG_DIR/feroxbuster/(每个用户)  
> 目录与feroxbuster可执行文件(每个用户)  
> 用户当前的工作目录(每个目标)

### 修改常见的默认值

> timeout: 7 seconds  
> follow redirects: false  
> wordlist: /usr/share/seclists/Discovery/Web-Content/raft-medium-> directories.txt  
> threads: 50  
> verbosity: 0 (no logging enabled)  
> scan_limit: 0 (no limit imposed on concurrent scans)  
> rate_limit: 0 (no limit imposed on requests per second)  
> status_codes: 200 204 301 302 307 308 401 403 405 500  
> user_agent: feroxbuster/VERSION  
> recursion depth: 4  
> auto-filter wildcards - true  
> output: stdout  
> save_state: true (create a state file in cwd when Ctrl+C is received)

### 通过Burp的代理流量

> feroxbuster -u http://127.1 --insecure --proxy http://127.0.0.1:8080  
>  
>

### 通过SOCKS代理(包括DNS查找)的代理通信

>  
> feroxbuster -u http://127.1 --proxy socks5h://127.0.0.1:9050  
>  
>

### 通过查询参数传递令牌

> feroxbuster -u http://127.1 --query token=0123456789ABCDEF

### 数率限制

将每个目录每秒的请求数限制为100个(在递归过程中发现的每个活动目录每秒请求将增加100个)

> feroxbuster -u http://localhost --rate-limit 100

将每秒请求数限制在整个目标上(一次只扫描一个目录，从而限制了每秒请求的数量)

> feroxbuster -u http://localhost --rate-limit 100 --scan-limit 1

  

## 0X03feroxbuster与SecLists结合

SecLists是OWASP维护的一个安全信息列表集合。该集合包括了用于渗透的各种类型的列表。这些列表包含了237个字典文件以及常用的Web
Shell攻击载荷。字典文件类型众多，包括用户名、密码、域名、敏感数据特征码、模糊测试载荷等。

而feroxbuster就是由SecLists衍生而来的一款利用工具，具体用法如下：

![1647262745_622f3c199efa042f2c05d.png!small](https://image.3001.net/images/20220314/1647262745_622f3c199efa042f2c05d.png!small)

无法运行的原因就是SecLists没有存在与正确的路径中（图中文件存在于桌面上），导致文件执行失败；当然也可以指定环境

>  **默认环境如图所示** ：/usr/share/seclists/# ls -lh

## 0X04报错（Could not connect to any target provided）

  

![1647262766_622f3c2e646b0c48c424c.png!small](https://image.3001.net/images/20220314/1647262766_622f3c2e646b0c48c424c.png!small)

 **原因是因为www，它也可以检测子域名，所以报错**

## 0X05实例演示

实战结果如图：

![1647262802_622f3c520ef9f0da03a8d.png!small](https://image.3001.net/images/20220314/1647262802_622f3c520ef9f0da03a8d.png!small)

个人感觉它的Fuzzing库是找到丰富，推荐大家使用！！！

