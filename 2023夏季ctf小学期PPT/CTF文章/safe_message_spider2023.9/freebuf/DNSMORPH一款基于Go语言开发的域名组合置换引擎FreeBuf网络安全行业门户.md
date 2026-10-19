![](https://image.3001.net/images/20230827/1693120392_64eaf7887b7f837927267.png!small)  

## 关于DNSMORPH

DNSMORPH是一款功能强大的域名组合置换引擎，其设计灵感来源于[
_dnstwist_](https://github.com/elceef/dnstwist)。该工具基于纯[
_Go语言_](https://golang.org/)开发，因此该工具具备较好的兼容性和性能。需要注意的是，DNSMORPH可以有效且稳定地处理用户提供的任何域或子域，并提供了许多配置选项来调整排列置换任务的运行。

## 功能特性

当前版本的DNSMORPH包含下列域名置换攻击类型：

> 1、域名同态攻击；
>
> 2、Bitsquat攻击；
>
> 3、断字攻击；
>
> 4、省略攻击；
>
> 5、重复攻击；
>
> 6、替换攻击；
>
> 7、子域攻击；
>
> 8、移位攻击；
>
> 9、元音交换攻击；
>
> 10、Doppelganger攻击；

## 工具安装

### 发布版安装

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/netevert/dnsmorph/releases)】下载并安装对应操作系统平台的预编译代码，并提取到目标目录下即可。

### 源码安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并手动完成代码编译：

    
    
    go get -v github.com/netevert/dnsmorph
    
    cd /$GOPATH/src/github.com/netevert/dnsmorph
    
    go get -v ./...
    
    go build

### Arch安装

DNSMORPH也提供了一个Arch Linux包，广大研究人员可以点击【[
_这里_](https://aur.archlinux.org/packages/dnsmorph/)】获取。

## 工具使用

工具帮助菜单：

    
    
    dnsmorph -d domain | -l domains_file [-girvuw] [-csv | -json]
    
      -csv      将结果输出到CSV文件
    
      -d string  设置目标域名
    
      -g    设置目标域名的地理位置
    
      -i     设置要包含的子域名
    
      -json   将结果输出为JSON
    
      -l string   域名列表文件路径
    
      -n      IDNA格式的同态域名
    
      -r       解析域名
    
      -u    更新检测
    
      -v    启用Verbose模式
    
      -w    执行Whois查询

针对目标域名执行攻击测试：

    
    
    ./dnsmorph -d amazon.com

针对域名列表执行攻击测试：

    
    
    ./dnsmorph -l domains.txt

在攻击测试中引入子域名：

    
    
    ./dnsmorph -d staging.amazon.com -i

针对置换域名执行DNS解析测试：

    
    
    ./dnsmorph -d amazon.com -r

针对置换域名执行地理定位测试：

    
    
    ./dnsmorph -d amazon.com -g

针对置换域名执行Whois查询：

    
    
    ./dnsmorph -d amazon.com -w

将结果输出为CSV或JSON：

    
    
    ./dnsmorph -d amazon.com -r -g -csv
    
    ./dnsmorph -d amazon.com -r -g -json

激活工具Verbose输出模式：

    
    
    ./dnsmorph -d staging.amazon.com -v

## 工具使用演示

完整使用：

![](https://image.3001.net/images/20230827/1693120464_64eaf7d087df993a909a9.gif!small)

地理定位：

![](https://image.3001.net/images/20230827/1693120484_64eaf7e4a36b3bd605895.gif!small)

列表置换：

![](https://image.3001.net/images/20230827/1693120503_64eaf7f76de813885fb15.gif!small)

DNS/域名解析：

![](https://image.3001.net/images/20230827/1693120522_64eaf80abfe3a6ea4713d.gif!small)

简单置换：

![](https://image.3001.net/images/20230827/1693120534_64eaf816cce91a557782b.gif!small)

子域名置换：

![](https://image.3001.net/images/20230827/1693120547_64eaf823e1805e8094744.gif!small)

Verbose输出：

![](https://image.3001.net/images/20230827/1693120561_64eaf831ce4d118f46d5a.gif!small)

Whois查询：

![](https://image.3001.net/images/20230827/1693120583_64eaf847588710a09cab6.gif!small)

结果输出到文件：

![](https://image.3001.net/images/20230827/1693120594_64eaf852a80a8f9fe042b.gif!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/netevert/dnsmorph/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **DNSMORPH** ：【[ _GitHub传送门_](https://github.com/netevert/dnsmorph)】

## 参考资料

> [ _http://www.babygopher.org/_](http://www.babygopher.org/)
>
> [ _https://github.com/elceef/dnstwist_](https://github.com/elceef/dnstwist)
>
> [ _https://golang.org/_](https://golang.org/)

