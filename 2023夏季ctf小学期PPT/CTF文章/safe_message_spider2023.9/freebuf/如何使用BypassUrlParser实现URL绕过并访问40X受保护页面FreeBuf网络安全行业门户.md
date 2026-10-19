![](https://image.3001.net/images/20220911/1662865363_631d4fd3d42143c6444ce.jpeg!small)  

## 关于Bypass-Url-Parser

Bypass-Url-Parser是一款功能强大的URL绕过工具，该工具可以使用多种方法实现URL绕过并访问目标站点的40X受保护页面。

## 工具下载

由于该工具基于Python 3 开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/laluka/bypass-url-parser.git

### Linux配置

    
    
    # Deps
    
    sudo apt install -y bat curl virtualenv python3
    
    # Tool
    
    virtualenv -p python3 .py3
    
    source .py3/bin/activate
    
    pip install -r requirements.txt
    
    ./bypass_url_parser.py -u http://thinkloveshare.com/juicy_403_endpoint/

### Docker配置

    
    
    docker build -t thelaluka/bypass-url-parser:latest .
    
    docker run --rm -it --net=host -v "$PWD:/host" thelaluka/bypass-url-parser:latest -u http://127.0.0.1:8000/dummy
    
    docker run --rm -it --net=host -v "$PWD:/host" thelaluka/bypass-url-parser:latest -u /host/urls.lst
    
    # TODO later, tag & push releases to dockerhub :)
    
    # -t thelaluka/bypass-url-parser:0.2.0
    
    # docker push thelaluka/bypass-url-parser:latest

## 工具使用

    
    
    Bypass Url Parser, made with love by @TheLaluka
    
    A tool that tests MANY url bypasses to reach a 40X protected page.
    
     
    
    Usage:
    
        ./bypass_url_parser.py -u <URL> [-m <mode>] [-o <outdir>] [-S <level>] [(-H <header>)...] [-r <num>]
    
                               [-s <ip>] [--spoofip-replace] [-p <port>] [--spoofport-replace] [--dump-payloads]
    
                               [-t <threads>] [-T <timeout>] [-x <proxy_url>] [-v | -d | -dd]
    
     
    
    Program options:
    
        -H, --header <header>     设置要使用的Header，格式为"Cookie: can_i_haz=fire"
    
        -m, --mode <mode>      设置绕过模式[默认: all]
    
        -o, --outdir <outdir>       结果的输出目录
    
        -x, --proxy <proxy_url>    设置代理，格式为http://proxy_ip:port.
    
        -S, --save-level <level>    存储结果等级，从0（禁用）到3（完整）[默认: 1]
    
        -s, --spoofip <ip>         注入到ip-specific头中的IP地址
    
        -p, --spoofport <port>     注入到port-specific头中的端口号
    
        -r, --retry <num>          失败后的重试次数 [默认: 3]
    
        -t, --threads <threads>     设置扫描并行线程[默认: 1]
    
        -T, --timeout <timeout>    Request times out after N seconds [默认: 5]
    
        -u, --url <URL>           待绕过的目标URL
    
     
    
    General options:
    
        -h, --help                显示工具帮助信息
    
        -v, --verbose             Verbose模式输出
    
        -d, --debug              显示调试信息
    
        -dd, --debug             开启二级调试模式，显示所有的类输出
    
        -V, --version             显示工具版本信息
    
     
    
    Misc options:
    
        --spoofip-replace         在'http_headers_ip'绕过模式下禁用显示内部IP列表
    
        --spoofport-replace       在'http_headers_port'模式下禁用显示内部端口列表    
    
    --dump-payloads         打印该工具生成的所有Payload
    
     
    
    样例:
    
        ./bypass_url_parser.py -u "http://127.0.0.1/juicy_403_endpoint/" -s 8.8.8.8 -d
    
        ./bypass_url_parser.py -u /path/urls -t 30 -T 5 -H "Cookie: me_iz=admin" -H "User-agent: test"

## 期望的输出结果

    
    
    ./bypass_url_parser.py -u http://127.0.0.1:8000/foo/bar
    
    2022-08-09 14:52:40 lalu-perso bup[361559] WARNING Trying to bypass 'http://127.0.0.1:8000/foo/bar' url (1625 payloads)...
    
    2022-08-09 14:52:40 lalu-perso bup[361559] INFO Doing: 50 / 1625
    
    [...]
    
    2022-08-09 14:52:54 lalu-perso bup[361559] INFO Doing: 1600 / 1625
    
    2022-08-09 14:52:54 lalu-perso bup[361559] INFO Retry (1/3) the '16' failed curl commands with 10 threads and 10s timeout
    
    2022-08-09 14:52:54 lalu-perso bup[361559] INFO Retry (2/3) the '16' failed curl commands with 5 threads and 20s timeout
    
    2022-08-09 14:52:54 lalu-perso bup[361559] INFO Retry (3/3) the '16' failed curl commands with 1 threads and 30s timeout
    
    2022-08-09 14:52:55 lalu-perso bup[361559] INFO
    
    [#####] [bypass_method] [payload] => [status_code] [content_type] [content_length] [lines_count] [word_counts] [title] [server] [redirect_url]
    
    [GROUP (1587)] [original_request] [http://127.0.0.1:8000/foo/bar] => [404] [text/html] [469] [14] [95] [Error response] [SimpleHTTP/0.6 Python/3.8.10] []
    
    [GROUP (10)] [http_methods] [-X CONNECT http://127.0.0.1:8000/foo/bar] => [501] [text/html] [500] [14] [96] [Error response] [SimpleHTTP/0.6 Python/3.8.10] []
    
    [SINGLE] [mid_paths] [http://127.0.0.1:8000/???foo/bar] => [200] [text/html] [913] [26] [27] [Directory listing for /???foo/bar] [SimpleHTTP/0.6 Python/3.8.10] []
    
    [SINGLE] [mid_paths] [http://127.0.0.1:8000//???foo/bar] => [301] [] [] [0] [0] [] [SimpleHTTP/0.6 Python/3.8.10] [/???foo/bar]
    
    [SINGLE] [mid_paths] [http://127.0.0.1:8000/??foo/bar] => [200] [text/html] [911] [26] [27] [Directory listing for /??foo/bar] [SimpleHTTP/0.6 Python/3.8.10] []
    
    [SINGLE] [mid_paths] [http://127.0.0.1:8000//??foo/bar] => [301] [] [] [0] [0] [] [SimpleHTTP/0.6 Python/3.8.10] [/??foo/bar]
    
    [SINGLE] [mid_paths] [http://127.0.0.1:8000/?foo/bar] => [200] [text/html] [909] [26] [27] [Directory listing for /?foo/bar] [SimpleHTTP/0.6 Python/3.8.10] []
    
    [SINGLE] [mid_paths] [http://127.0.0.1:8000//?foo/bar] => [301] [] [] [0] [0] [] [SimpleHTTP/0.6 Python/3.8.10] [/?foo/bar]
    
    [SINGLE] [mid_paths] [http://127.0.0.1:8000///?anythingfoo/bar] => [200] [text/html] [929] [26] [27] [Directory listing for ///?anythingfoo/bar] [SimpleHTTP/0.6 Python/3.8.10] []
    
    [SINGLE] [mid_paths] [http://127.0.0.1:8000////?anythingfoo/bar] => [200] [text/html] [931] [26] [27] [Directory listing for ////?anythingfoo/bar] [SimpleHTTP/0.6 Python/3.8.10] []
    
    [GROUP (2)] [mid_paths] [http://127.0.0.1:8000/#?foo/bar] => [200] [text/html] [893] [26] [27] [Directory listing for /] [SimpleHTTP/0.6 Python/3.8.10] []
    
    [GROUP (2)] [mid_paths] [http://127.0.0.1:8000//#?foo/bar] => [301] [] [] [0] [0] [] [SimpleHTTP/0.6 Python/3.8.10] [/]

## 工具使用样例

### 参数解析

Bypass-Url-Parser支持以多种方式定义某些参数：

    
    
    ./bypass_url_parser.py -u http://thinkloveshare.com/test
    
    ./bypass_url_parser.py -u /path/urls
    
    cat /path/urls | ./bypass_url_parser.py -u -    
    echo 'http://thinkloveshare.com/test' | ./bypass_url_parser.py -u -
### 绕过模式

当前版本的Bypass-Url-Parser支持下列绕过模式：

    
    
    all, mid_paths, end_paths, case_substitution, char_encode, http_methods, http_versions, http_headers_scheme, http_headers_ip, http_headers_port
    
    Spoofip / Spoofport
    
    ./bypass_url_parser.py -u /path/urls -s /path/custom_ip --spoofip-replace
    
    ./bypass_url_parser.py -u /path/urls -p "3000, 9443, 10443"

### 结果保存

默认配置下，如果目标为单个URL，工具会将运行结果存储到/tmp/tmpXXX-bypass-url-parser/triaged-bypass.log日志文件中。使用样例如下：

    
    
    ./bypass_url_parser.py -S 0
    
    ./bypass_url_parser.py -o /tmp/bypass-res
    
    ./bypass_url_parser.py -o /tmp/bypass-res2 -S 2 -u http://thinkloveshare.com/juicy_403_endpoint/
    
    tree /tmp/bypass-res2/
    
    ├── bypass-14193b8d2e14ec60d52405f46c5d35f3.html
    
    ├── bypass-782550777a661b7bef046b5d899b403a.html
    
    ├── bypass-e06268bcef8506053feed2646af4e773.html
    
    ├── bypass-ebdf6466c5ef82ab08a7b97324662bf0.html
    
    └── triaged-bypass.log
    
     
    
    0 directories, 5 files

## 非回归测试和代码清理

    
    
    # Code Cleanup
    
    isort --py 37 *.py
    
    autopep8 -a --max-line-length 120 -i *.py
    
    # Ensure no regression is pushed
    
    ./bypass_url_parser.py -S 0 -v -u http://127.0.0.1:8000/foo/bar --dump-payloads > "tests-history/bup-payloads-$(date +'%Y-%m-%d').lst"
    
    # Compare /tmp/bup-payloads-YYYY-MM-DD.lst and the latest tests-history/bup-payloads-YYYY-MM-DD.lst
    
    git diff --no-index tests-history/bup-payloads-[OLD].lst tests-history/bup-payloads-[NEW].lst
    
    # TODO create ls/sort/diff bash command for maintainers
    
    git commit -m "My cool feature or bugfix"
    
    git tag -a vX.Y.Z "$COMMIT_HASH" -m "New release: vX.Y.Z"
    
    git push --tags
    
    # If X or Y is bumped, create new release on github

## 项目地址

 **Bypass-Url-Parser** ：【[ _GitHub传送门_](https://github.com/laluka/bypass-url-parser)】

