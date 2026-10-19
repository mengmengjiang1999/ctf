![](https://image.3001.net/images/20200220/1582196668_5e4e67bcecdf5.jpg!small)

##  Syborg

**Syborg是一款DNS子域名递归枚举工具，它的扫描模式既非主动，也非完全被动的。该工具可以直接构造一个域名，然后通过指定的DNS服务器查询该域名。**

Syborg配备了一个断路规避系统，这个系统的灵感来自于@Tomnomnom的[ettu项目](https://github.com/tomnomnom/hacks)。

当你使用其他类似工具来执行子域名枚举任务时，大多数工具都会被动查询类似virustotal、crtsh或censys之类的公共记录。但Syborg所采用的枚举技术速度非常快，并且能够在最短的时间内帮助研究人员查找出尽可能多的域名。

但是，仍然有很多域名是这些公共记录中不会包含或者涉及到的。为了查找出这些域名，Syborg能够跟域名服务器进行交互，并根据对DNS服务器进行递归爆破查询，直到查询队列为空为止。

![](https://image.3001.net/images/20200220/1582196675_5e4e67c3bdee1.png!small)

##  工作机制

从一开始，如果一个DNS域名的查询结果记录为0条，那么你可能会收到一条NXDOMAIN错误：

    
    
    host four.tomnomnom.uk
    
        Host four.tomnomnom.uk not found: 3(NXDOMAIN)

你可能也注意到了，有的时候你可能收到的是一个空响应：

    
    
    host three.tomnomnom.uk

后面这种情况的不同之处就在于，返回的记录中可能会包含另一个域名名称，而这个域名会以你查询的域名作为后缀：

    
    
    host one.two.three.tomnomnom.uk
    
        one.two.three.tomnomnom.uk has address 46.101.59.42

相应信息中的这种差异可以帮助我们避免在递归DNS爆破中避免出现断路的情况，也就是那种查询到了尽头的情况：

    
    
    echo -e "www\none\ntwo\nthree" | ettu tomnomnom.uk
    
        one.two.three.tomnomnom.uk

Syborg可以将所有的这些功能以简单的并发和递归结合运行。

##  工具依赖

> 1、Python 3.x（建议）
>
> 2、Python 2.x（未测试）

##  工具安装

广大研究人员可以使用下列命令将项目代码克隆至本地：

    
    
    git clone https://github.com/MilindPurswani/Syborg.git

接下来，运行下列命令完成依赖组件的解析：

    
    
    pip3 install -r requirements.txt

##  工具使用

    
    
    python3 syborg.py yahoo.com

运行之后，Syborg可能会达到一个较高的CPU使用率，如果你在你的VPS上运行Syborg的话，钱包可能就顶不住了。因此，为了限制资源消耗，我们可以使用一款名叫Cpulimit的工具：

    
    
    cpulimit -l 50 -p $(pgrep python3)

该工具的下载命令如下：

    
    
    sudo apt install cpulimit

如需获取更加完整的工具使用方式，请点击【[这里](https://github.com/MilindPurswani/Syborg/blob/master/Syborg%20Creative%20Usage%20Guidelines.md)】获取。

##  项目地址

> Syborg：【[GitHub传送门](https://github.com/MilindPurswani/Syborg)】

 ***
参考来源：[MilindPurswani](https://github.com/MilindPurswani/Syborg)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

