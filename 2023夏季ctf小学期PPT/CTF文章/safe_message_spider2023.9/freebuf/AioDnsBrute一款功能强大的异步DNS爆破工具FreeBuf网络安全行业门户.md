![](https://image.3001.net/images/20220711/1657532710_62cbf126228ed0a2264dc.jpeg!small)

## 关于AioDnsBrute

AioDnsBrute是一款功能强大的异步DNS爆破工具，该工具基于Python 3.5开发，并使用了asyncio库以实现针对目标域名的异步爆破。

该工具的运行速度非常快，在一台小型V*P*S主机上，可以实现在1.5-2分钟之内处理大约10万个DNS资源。如果使用的是Amazon
M3的话，3分钟之内可以发送100万个请求。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/blark/aiodnsbrute.git

然后切换到项目目录内，运行setup.py脚本完成工具的安装：

    
    
    $ cd aiodnsbrute
    
    $ python setup.py install .

除此之外，我们也可以使用pip命令来下载和安装AioDnsBrute：

    
    
    $ pip install aiodnsbrute

注意：推荐大家使用 _virtualenv_在虚拟环境中使用AioDnsBrute。

## 工具使用

    
    
    $ aiodnsbrute --help
    
     
    
    Usage: cli.py [OPTIONS] DOMAIN
    
     
    
      aiodnsbrute is a command line tool for brute forcing domain names
    
      utilizing Python's asyncio module.
    
     
    
      credit: blark (@markbaseggio)
    
     
    
    Options:
    
      -w, --wordlist TEXT            用于爆破的字典文件
    
      -t, --max-tasks INTEGER       异步任务执行数量
    
      -r, --resolver-file FILENAME    包含DNS解析器列表的文本文件，按行分隔，默认使用系统解析器
    
      -v, --verbosity               开启工具Verbose模式
    
      -o, --output [csv|json|off]      将输出结果保存至DOMAIN.csv/json文件
    
      -f, --outfile FILENAME        输出文件名称
    
      --query / --gethostbyname     使用的DNS查询类型
    
      --wildcard / --no-wildcard     通配符检测，默认启用
    
      --verify / --no-verify          在开始之前验证域名是否正常，默认启用
    
      --version                    显示工具版本信息和退出
    
      --help                       显示工具帮助信息和退出

## 工具运行样例

使用自定义选项执行爆破测试：

    
    
    $ aiodnsbrute -w wordlist.txt -vv -t 1024 domain.com

执行一次爆破测试，生成常规输出，并将JSON格式结果发送至STDOUT：

    
    
    $ aiodnbrute -f - -o json domain.com

高级使用：使用自定义解析器，并将结果转发到[ _jq_](https://stedolan.github.io/jq/)：

    
    
    $ aiodnsbrute -r resolvers.txt -f - -o json google.com | jq '.[] | select(.ip[] | startswith("172."))'

默认启用通配符检测：

    
    
    $ aiodnsbrute foo.com
    
     
    
    [*] Brute forcing foo.com with a maximum of 512 concurrent tasks...
    
    [*] Using recursive DNS with the following servers: ['50.116.53.5', '50.116.58.5', '50.116.61.5']
    
    [!] Wildcard response detected, ignoring answers containing ['23.23.86.44']
    
    [*] Wordlist loaded, proceeding with 1000 DNS requests
    
    [+] www.foo.com                         52.73.176.251, 52.4.225.20
    
    100%|██████████████████████████████████████████████████████████████████████████████| 1000/1000 [00:05<00:00, 140.18records/s]
    
    [*] Completed, 1 subdomains found

gethostbyname参数，检测存在子域名接管漏洞的CNAME：

    
    
    $ aiodnsbrute --gethostbyname domain.com

通过文件提供解析器列表：

    
    
    $ aiodnsbrute -r resolvers.txt domain.com

## 工具运行截图

![](https://image.3001.net/images/20220711/1657532796_62cbf17c12edc143dc259.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/blark/aiodnsbrute/blob/master/LICENSE.txt)开源许可证协议。

## 项目地址

 **AioDnsBrute** ：【[ _GitHub传送门_](https://github.com/blark/aiodnsbrute)】

## 参考资料

> [ _https://github.com/bitquark_](https://github.com/bitquark)
>
> [
> _https://github.com/aboul3la/Sublist3r_](https://github.com/aboul3la/Sublist3r)
>
> [
> _https://click.palletsprojects.com/en/7.x/_](https://click.palletsprojects.com/en/7.x/)
>
> [ _https://github.com/tqdm/tqdm_](https://github.com/tqdm/tqdm)
>
> [ _https://github.com/saghul/aiodns_](https://github.com/saghul/aiodns)
>
> [ _https://stedolan.github.io/jq/_](https://stedolan.github.io/jq/)
>
> [
> _https://virtualenv.pypa.io/en/latest/userguide/#usage_](https://virtualenv.pypa.io/en/latest/userguide/#usage)

