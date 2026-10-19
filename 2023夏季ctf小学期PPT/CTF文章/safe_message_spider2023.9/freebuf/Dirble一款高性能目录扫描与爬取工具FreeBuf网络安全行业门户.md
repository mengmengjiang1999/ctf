![](https://image.3001.net/images/20200414/1586862666_5e959a4acef1c.png!small)

**今天给大家介绍的是一款名叫Dirble工具，它是一款易于使用的高性能网站目录扫描工具。该工具针对Windows和Linux平台设计，在Dirble的帮助下，广大安全研究人员可以快速对目标站点进行目录扫描和资源爬取。**

## 工具安装

广大研究人员可以使用下列命令直接将项目源码克隆至本地

> git clone <https://github.com/nccgroup/dirble.git>

## 工具使用

首先，我们需要根据自己的系统平台来选择对应的Windows、Linux或macOS版本的预编译源码。当然了，我们也可以使用Cargo来直接对项目源代码在本地进行编译。编译完成之后，我们就可以直接在命令行终端中使用Dirble了。Dirble的默认字典使用的是项目根目录中的dirble_wordlist.txt文件，该文件为一个可执行文件。

除此之外，我们还可以使用下列命令在BlackArch中完成Dirble的安装：

    
    
    sudo pacman -S dirble

当然了，Dirble还很贴心地给广大研究人员提供了一个Docker镜像，我们可以使用下列命令来通过Docker运行工具：

    
    
    docker run --rm -t isona/dirble [dirble arguments]

在工具的使用过程中，我们可以通过运行下列命令来查看到工具的帮助信息，或直接访问项目的【[
_WiKi页面_](https://github.com/nccgroup/dirble/wiki/Help-Text)】来获取更多详情：

    
    
    dirble --help

### 源码构建

为了在我们当前的平台上对项目源码进行构建，首先请确保当前系统已完成了Cargo的安装，接下来运行下列命令：

    
    
    cargo build --release

或者，我们也可以在发布模式（cargo build --release）下运行下列命令来构建源码：

    
    
    make

如果需要构建32位或64位不同版本的Linux或Windows程序，我们也提供了非常方便的makefile：

    
    
    make release

或：

    
    
    cargo install cross

## 功能介绍

> 1、Cookie
>
> 2、自定义Header
>
> 3、扩展名和前缀
>
> 4、HTTP基础身份验证
>
> 5、可枚举目录检测和删除
>
> 6、将输出保存至文件
>
> 7、以XML和JSON格式保存输出
>
> 8、支持代理
>
> 9、递归扫描
>
> 10、状态码黑名单和白名单
>
> 11、多线程支持
>
> 12、请求限制
>
> 13、支持基于响应代码和响应长度的检测
>
> 14、支持URL列表扫描
>
> 15、用户代理
>
> 16、使用GET、POST或HEAD请求
>
> 17、可从根据响应长度的范围来过滤输出

## 使用样例

在当前工作目录下，使用默认字典文件dirble_wordlist.txt来对目标网站进行扫描：

    
    
    dirble [address]

使用默认字典，并引入.php和.html后缀进行扫描：

    
    
    dirble [address] -w example_wordlist.txt -x .php,.html

启用可枚举目录爬取功能：

    
    
    dirble [address] --scrape-listable

提供扫描扩展名列表和主机列表：

    
    
    dirble [address] -X wordlists/web.lst -U hostlist.txt

通过命令行提供多个待扫描的主机：

    
    
    dirble [address] -u [address] -u [address]

以Gobuster默认风格和多线程（10个线程）执行扫描任务，并禁用递归功能：

    
    
    dirble [address] --max-threads 10 --wordlist-split 10 -r

### 工具性能

![](https://image.3001.net/images/20200414/1586862741_5e959a9580a99.png!small)

## 项目地址

> Drible：【[ _GitHub传送门_](https://github.com/nccgroup/dirble)】

 *** 参考来源：[
_nccgroup_](https://github.com/nccgroup/dirble)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

