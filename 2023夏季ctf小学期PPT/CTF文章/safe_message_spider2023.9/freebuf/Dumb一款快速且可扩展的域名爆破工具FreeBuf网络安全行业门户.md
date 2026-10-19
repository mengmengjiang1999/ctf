![](https://image.3001.net/images/20230420/1681979437_6440f82dc1db9f94dbbd3.jpg!small)

## 关于Dumb

Dumb是一款功能强大且运行快速的域名爆破工具，该工具可以帮助广大研究人员快速对目标域名进行爆破枚举，并且支持自定义功能扩展。

### 子域名爆破

如果你提供的域名为DUMB.dumain.com，其中DUMB为子域名Mask，字典内容如下：

    
    
    www
    
    ftp
    
    backoffice

此时Dumb将生成下列域名地址并进行爆破：

    
    
    www.dumain.com
    
    ftp.dumain.com
    
    backoffice.dumain.com

针对子域名，我们也可以直接输入dumain.com，工具将会视其为DUMB.dumain.com。

### 爆破域名后缀（顶级域名）

出于简化目的，我们可以直接输入dumain.DUMB，其中DUMB为后缀Mask，字典内容如下：

    
    
    com
    
    net
    
    org

Dumb将会生成下列域名并进行爆破：

    
    
    dumain.com
    
    dumain.net
    
    dumain.org

### 爆破一切

我们可以直接提供DUMB.DUMB.DUMB并结合下列字典内容：

    
    
    wordlist1   wordlist2   wordlist3
    
    www         foo         com
    
    ftp         bar         net

DUmb将会生成下列内容：

    
    
    www.foo.com
    
    ftp.foo.com
    
    www.bar.com
    
    ftp.bar.com
    
    www.foo.net
    
    ftp.foo.net
    
    www.bar.net
    
    ftp.bar.net

## 工具下载

### 源码构建

如需从源码构建Dumb，还需要安装[
_stack_](https://docs.haskellstack.org/en/stable/README/)工具。进入项目根目录，并运行下列命令：

    
    
    $ stack build

然后执行工具即可：

    
    
    $ stack exec dumb "DUMB.dumain.com" wordlists/subdomains.txt

### Docker使用

如果你不想通过源码构建工具，你也可以使用Docker版本的Dumb：

    
    
    docker run -it giovanifss/dumb "DUMB.dumain.com" subdomains.txt

wordlists/目录中所有的字典都位于Docker容器文件系统的根目录/下，这也就意味着，我们可以直接以字典文件名来调用Dumb并传递字典路径：

    
    
    docker run -it giovanifss/dumb "DUMB.dumain.com" (subdomains.txt|subdominios.txt|domain-endings.txt)

如需在容器内使用本地字典，可以使用Docker卷宗：

    
    
    docker run -v local/wordlist.txt:/opt/wordlist.txt -it giovanifss/dumb "DUMB.dumain.com" /opt/wordlist.txt

## 工具使用

Dumb可以接受一个Mask作为第一个参数，并提供字典路径，字典数量必须和域名中的Mask数量匹配。比如说：

    
    
    一个Mask：$ dumb "DUMB.dumain.com" wordlists/foo.txt
    
    
    两个Mask：$ dumb "DUMB.dumain.DUMB" wordlists/foo.txt wordlists/bar.txt
    
    
    多个Mask：$ dumb "DUMB-DUMB-DUMB_DUMB.DUMB.DUMB" wordlists/foo_1.txt ... wordlists/foo_6.txt

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/giovanifss/Dumb/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Dumb** ：【[ _GitHub传送门_](https://github.com/giovanifss/Dumb)】

## 参考资料

> [
> _https://docs.haskellstack.org/en/stable/README/_](https://docs.haskellstack.org/en/stable/README/)

