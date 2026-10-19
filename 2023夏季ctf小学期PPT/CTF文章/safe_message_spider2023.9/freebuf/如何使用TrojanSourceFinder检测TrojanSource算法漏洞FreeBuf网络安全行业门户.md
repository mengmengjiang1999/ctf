![](https://image.3001.net/images/20220117/1642430478_61e5800e786ebcd69373e.png!small)  

## 关于TrojanSourceFinder

TrojanSourceFinder是一款功能强大的漏洞检测工具，该工具可以帮助广大研究人员检测源代码中的Trojan Source算法漏洞。

Trojan
Source漏洞将允许攻击者隐藏恶意代码，并将恶意代码转换为看似无害的代码。一般来说，攻击者会试图通过将其恶意代码作为注释（视觉上的掩饰）来欺骗用户。这是一种非常严重的安全威胁，因为这个漏洞将影响多种编程语言，一般带有多个“不受信任”的第三方源码的项目都需要注意这种漏洞的影响。

## 工具安装

### 使用Go安装

通过“go install”：

    
    
    go install github.com/ariary/TrojanSourceFinder/cmd/tsfinder@latest

注意：需要确保“$PATH”环境变量中已设置了“$GOPATH”。

源码安装：

    
    
    git clone https://github.com/ariary/TrojanSourceFinder
    
    cd TrojanSourceFinder
    
    make before.build
    
    make build.tsfinder

如果命令“make build.tsfinder”失效的话，可以尝试下列命令：

    
    
    env GOOS=target-OS GOARCH=target-architecture
    
    go build -o tsfinder cmd/main.go

### 使用curl安装

安装发布版本：

    
    
    curl -lO -L https://github.com/ariary/TrojanSourceFinder/releases/latest/download/tsfinder && chmod +x tsfinder

## 检测Trojan Source漏洞

该工具可以帮助广大研究人员通过手动代码检测或使用CI/CD管道（Unicode双向字符）检测Trojan Source漏洞。

检测文件或目录中的Trojan Source漏洞：

    
    
    tsfinder [path]

### 检测文本文件

一般来说，源码文件都是文本文件，提取数据出来并进行扫描将有助于排除假阳性：

    
    
    tsfinder -t [path]

注意：添加“-v”参数可以查看扫描跳过的文件。

### 其他选项

扫描所有的文件并显示相关代码行：

    
    
    tsfinder -v

grep one-liner：

    
    
    grep -arE $'(\u2066|\u2067|\u2068|\u202A|\u202B|\u202D|\u202E|\u202C|\u2069|\u200E|\u200F|\u061C|\u2066|\u2067|\u2068)'

仅扫描人类可读的文件：

    
    
    tsfinder -t

grep one-liner：

    
    
    grep -IrE $'(\u2066|\u2067|\u2068|\u202A|\u202B|\u202D|\u202E|\u202C|\u2069|\u200E|\u200F|\u061C|\u2066|\u2067|\u2068)'

## 工具使用演示

![](https://image.3001.net/images/20220117/1642430571_61e5806bbe8c2bb1c75f2.gif)

![](https://image.3001.net/images/20220117/1642430612_61e58094b184252eaec3d.gif)

![](https://image.3001.net/images/20220117/1642430633_61e580a9783e11aab1960.gif)  

## 项目地址

 **TrojanSourceFinder：** 【[
_GitHub传送门_](https://github.com/ariary/TrojanSourceFinder)】

## 参考资料

[
_https://www.reddit.com/r/cybersecurity/comments/qlh5j9/my_take_on_trojan_source/_](https://www.reddit.com/r/cybersecurity/comments/qlh5j9/my_take_on_trojan_source/)

