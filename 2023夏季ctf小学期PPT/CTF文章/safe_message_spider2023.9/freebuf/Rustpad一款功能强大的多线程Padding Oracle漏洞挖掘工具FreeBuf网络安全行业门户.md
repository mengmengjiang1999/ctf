![](https://image.3001.net/images/20220119/1642602917_61e821a5bd4bc4ea5e57a.png!small)

## 关于Rustpad

Rustpad是一款功能强大的多线程Padding Oracle漏洞挖掘工具，该工具是[
_PadBuster_](https://github.com/AonCyberLabs/PadBuster)漏洞挖掘工具的继承者，相当于站在前人的肩膀上实现了自己的功能。该工具基于Rust开发，并且能够利用[
_Padding_ __
_Oracle漏洞_](https://en.wikipedia.org/wiki/Padding_oracle_attack)在不知道加密密钥的情况下解密任意密文或加密任意明文数据。

## 功能介绍

> 1、解密任意密文
>
> 2、加密任意明文
>
> 3、块级和字节级的多线程
>
> 4、高级实时交互式用户接口
>
> 5、No-TTY支持，因此可以通过管道进行数据传输
>
> 6、进度条和自动重试
>
> 7、智能检测密码文本编码，支持：十六进制、base64、base64url
>
> 8、采用纯Rust安全开发，确保了工具的可用性

## 工具下载&安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Kibouo/rustpad.git

### Arch Linux【[ _aur_ __ _v_
_1.7.3-1_](https://aur.archlinux.org/packages/rustpad-bin/)】

    
    
    yay -Syu rustpad

### Kali / Debian【[ _deb_ __ _v_
_1.7.3_](https://github.com/Kibouo/rustpad/releases)】

    
    
    apt install ./rustpad.deb

### 其他操作系统平台【[ _crates_ _.io v1.7.3_](https://crates.io/crates/rustpad)】

    
    
    cargo install rustpad

## 工具使用

使用Rustpad来测试Padding Oracle漏洞其实是非常容易的，该工具只需要四个参数信息即可开始漏洞挖掘：

> 1、目标Oracle（--oracle）
>
> 2、需要解密的密文（--decrypt）
>
> 3、块大小（--block-size）
>
> 4、Oracle类型（Web / 脚本）

### 工具帮助信息

    
    
    ; rustpad --help
    
    rustpad
    
    Multi-threaded Padding Oracle attacks against any service.
    
     
    
    USAGE:
    
        rustpad [OPTIONS] --block-size <block_size> --decrypt <decrypt> --oracle <oracle> <SUBCOMMAND>
    
     
    
    OPTIONS:
    
        -B, --block-size <block_size>
    
                Block size used by the cypher [possible values: 8, 16]
    
     
    
        -D, --decrypt <decrypt>
    
                Original cypher text, received from the target service, which is to be decrypted
    
     
    
            --delay <delay>
    
                Delay between requests within a thread, in milliseconds [default: 0]
    
     
    
        -e, --encoding <encoding>
    
                Specify encoding used by the oracle to encode the cypher text [default: auto]  [possible values: auto, base64, base64url, hex]
    
     
    
        -E, --encrypt <encrypt>
    
                Plain text to encrypt. Encryption mode requires a cypher text to gather necessary data
    
     
    
        -h, --help
    
                Prints help information
    
     
    
            --no-cache
    
                Disable reading and writing to the cache file
    
     
    
        -n, --no-iv
    
                Cypher text does not include an Initialisation Vector
    
     
    
            --no-url-encode
    
                Disable URL encoding and decoding of cypher text
    
     
    
        -O, --oracle <oracle>
    
                The oracle to question with forged cypher texts. This can be a URL or a shell script.
    
                See the subcommands `web --help` and `script --help` respectively for further help.
    
        -o, --output <output>
    
                File path to which log output will be written
    
     
    
        -t, --threads <threads>
    
                Amount of threads in the thread pool
    
     
    
        -V, --version
    
                Prints version information
    
     
    
        -v, --verbose
    
                Increase verbosity of logging
    
     
    
     
    
    SUBCOMMANDS:
    
        web       Question a web-based oracle
    
    script    Question a script-based oracle

### Web模式

Web模式下，指定的目标Oracle需位于Web上。换句话说，我们的目标Oracle是一个带有URL的Web服务器。

为了保证Padding
Oracle成功，如果提供了填充不正确的密文文本，那么Rustpad将会对Oracle的响应信息进行分析，并根据Oracle的行为来对自身进行自动校准。

    
    
    ; rustpad web --help
    
    rustpad-web
    
    Question a web-based oracle
    
     
    
    USAGE:
    
        rustpad --block-size <block_size> --decrypt <decrypt> --oracle <oracle> web [OPTIONS]
    
     
    
    OPTIONS:
    
        -c, --consider-body
    
                Consider the response body and content length when determining the web oracle's response to (in)correct padding
    
     
    
        -d, --data <data>
    
                Data to send in a POST request
    
     
    
            --delay <delay>
    
                Delay between requests within a thread, in milliseconds [default: 0]
    
     
    
        -e, --encoding <encoding>
    
                Specify encoding used by the oracle to encode the cypher text [default: auto]  [possible values: auto, base64, base64url, hex]
    
     
    
        -h, --help
    
                Prints help information
    
     
    
        -H, --header <header>...
    
                HTTP header to send
    
     
    
        -k, --insecure
    
                Disable TLS certificate validation
    
     
    
        -K, --keyword <keyword>
    
                Keyword indicating the location of the cypher text in the HTTP request. It is replaced by the cypher text's value at runtime [default: CTEXT]
    
     
    
            --no-cache
    
                Disable reading and writing to the cache file
    
     
    
        -n, --no-iv
    
                Cypher text does not include an Initialisation Vector
    
     
    
            --no-url-encode
    
                Disable URL encoding and decoding of cypher text
    
     
    
        -o, --output <output>
    
                File path to which log output will be written
    
     
    
        -x, --proxy <proxy>
    
                Proxy server to send web requests over. Supports HTTP(S) and SOCKS5
    
     
    
            --proxy-credentials <proxy_credentials>
    
                Credentials to authenticate against the proxy server with [format: <user>:<pass>]
    
     
    
        -r, --redirect
    
                Follow 302 Redirects
    
     
    
        -t, --threads <threads>
    
                Amount of threads in the thread pool
    
     
    
        -T, --timeout <timeout>
    
                Web request timeout in seconds [default: 10]
    
     
    
        -A, --user-agent <user_agent>
    
                User-agent to identify with [default: rustpad/<version>]
    
     
    
        -v, --verbose
    
                Increase verbosity of logging
    
     
    
     
    
    Indicate the cypher text's location! See `--keyword` for clarification.

### 脚本模式

脚本模式是为超级用户或CTF玩家准备的，并且能够提供一个可运行的脚本，该模式下的目标Oracle是一个本地Shell脚本。

脚本将允许我们能对本地Oracle或更特殊的服务进行漏洞测试。或者说，我们也可以使用脚本模式来自定义或扩展Rustpad的功能。

    
    
    ; rustpad script --help
    
    rustpad-script
    
    Question a script-based oracle
    
     
    
    USAGE:
    
        rustpad --block-size <block_size> --decrypt <decrypt> --oracle <oracle> script [OPTIONS]
    
     
    
    OPTIONS:
    
            --delay <delay>
    
                Delay between requests within a thread, in milliseconds [default: 0]
    
     
    
        -e, --encoding <encoding>
    
                Specify encoding used by the oracle to encode the cypher text [default: auto]  [possible values: auto, base64, base64url, hex]
    
     
    
        -h, --help
    
                Prints help information
    
     
    
            --no-cache
    
                Disable reading and writing to the cache file
    
     
    
        -n, --no-iv
    
                Cypher text does not include an Initialisation Vector
    
     
    
            --no-url-encode
    
                Disable URL encoding and decoding of cypher text
    
     
    
        -o, --output <output>
    
                File path to which log output will be written
    
     
    
        -t, --threads <threads>
    
                Amount of threads in the thread pool
    
     
    
        -v, --verbose
    
                Increase verbosity of logging
    
     
    
     
    
    Script must respond with exit code 0 for correct padding, and any other code otherwise. Cypher text is passed as the 1st argument.

## 即将添加的功能

> 1、Tab键自动补全
>
> 2、智能化URL解析
>
> 3、高级校准
>
> 4、块大小自动检测
>
> 5、改进Linux二进制文件的大小
>
> 6、.NET URL令牌编码

## 项目地址

 **Rustpad：** 【[ _GitHub传送门_](https://github.com/Kibouo/rustpad)】

## 参考资料

> [
> _https://github.com/AonCyberLabs/PadBuster_](https://github.com/AonCyberLabs/PadBuster)
>
> [
> _https://en.wiki*pedia.org/wiki/Padding_oracle_attack_](https://en.wikipedia.org/wiki/Padding_oracle_attack)

