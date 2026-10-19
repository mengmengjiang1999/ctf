![](https://image.3001.net/images/20230511/1683799720_645cbea8966400d479eac.jpg!small)

## 关于linkedin2username

linkedin2username是一款功能强大的OSINT公开资源情报收集工具，该工具可以帮助广大研究人员快速根据LinkedIn的企业信息生成用户名列表。

该工具是一个纯Web爬虫，并且不需要使用其他的API密钥。我们可以使用一个有效的LinkedIn用户名和密码进行登录，该工具将会为指定的企业信息创建所有可能的员工账号列表。

建议广大研究人员使用包含多个连接的账号来进行测试，该工具支持使用最多三级连接。请注意，LinkedIn的搜索结果上限为1000名员工账号，不过我们也可以使用
--geoblast或--keywords来绕过这一限制。

请注意，请在获得企业许可之后使用该工具，请不要将其用户恶意目的。

## 生成的列表文件

> first.last.txt: 生成包含类似Joe.Schmoe的用户名列表文件；
>
> f.last.txt: 生成包含类似 J.Schmoe的用户名列表文件；
>
> flast.txt: 生成包含类似 JSchmoe的用户名列表文件；
>
> firstl.txt: 生成包含类似 JoeS的用户名列表文件；
>
> first.txt 生成包含类似 Joe的用户名列表文件；
>
> lastf.txt 生成包含类似 SchmoeJ的用户名列表文件；
>
> rawnames.txt: 生成包含类似Joe Schmoe全名的用户名列表文件；
>
> metadata.txt: 生成包含全名和职业信息的CSV文件；

除此之外，该工具还支持在生成的用户名后添加@domain.xxx。

## 工具下载&安装

由于该工具基于Pythoni开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/initstring/linkedin2username.git

然后切换到项目目录中，使用pip命令和项目提供的requirements.txt文件安装该工具所需的依赖组件：

    
    
    cd linkedin2username
    
    pip install -r requirements.txt

## 工具使用

我们需要向该工具提供LinkedIn的企业名称，这个可以通过查看公司的LinkedIn页面URL地址（形式类似于https://linkedin.com/company/uber-com）来获取。

在下面的例子中，我们将会获取Uber的所有员工账号：

    
    
    $ python linkedin2username.py myname@email.com uber-com

在下面的例子中，我们将会向上面拿到的用户名后添加@uber.com：

    
    
    $ python linkedin2username.py myname@email.com uber-com -d 5 -n 'uber.com'

## 工具帮助信息

    
    
    usage: linkedin2username.py [-h] [-p PASSWORD] [-n DOMAIN] [-d DEPTH]
    
                                [-s SLEEP]
    
                                username company
    
     
    
    positional arguments:
    
      username              一个有效的LinkedIn用户名
    
      company               企业名称
    
     
    
    optional arguments:
    
      -h, --help            显示工具帮助信息和退出
    
      -p PASSWORD, --password PASSWORD
    
                            在命令行中以明文形式指定你的密码
    
      -n DOMAIN, --domain DOMAIN
    
                            向输出用户名后追加一个域名，例如 jschmoe@uber.com
    
      -d DEPTH, --depth DEPTH
    
                            搜索深度
    
      -s SLEEP, --sleep SLEEP
    
                            页面之间的爬取休眠时间，默认为3秒
    
      -x PROXY, --proxy PROXY
    
                            设置HTTPS代理服务器，例如 "-p https://localhost:8080"
    
     
    
      -k KEYWORDS, --keywords KEYWORDS
    
                            使用关键词过滤搜索结果，例如"-k 'sales,human resources,information,technology']
    
      -g, --geoblast          绕过1000条记录的限制
    
      -o OUTPUT, --output OUTPUT
    
                            输出目录，默认为li2u-output

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/initstring/linkedin2username/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **linkedin2username** ：【[
_GitHub传送门_](https://github.com/initstring/linkedin2username)】

## 参考资料

> [ _https://www.linkedin.com/help/linkedin/answer/129/what-you-get-when-you-> search-on-> linkedin?lang=en_](https://www.linkedin.com/help/linkedin/answer/129/what-> you-get-when-you-search-on-linkedin?lang=en)

