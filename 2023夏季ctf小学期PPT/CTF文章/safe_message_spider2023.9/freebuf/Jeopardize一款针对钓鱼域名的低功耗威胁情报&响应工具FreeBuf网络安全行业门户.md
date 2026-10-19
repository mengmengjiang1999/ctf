![](https://image.3001.net/images/20200330/1585583002_5e82139a29719.jpg!small)

##  工具介绍

**Jeopardize工具的主要目标是以尽可能低的成本来提供针对网络钓鱼域名的基本威胁情报和响应能力，它可以检测到已注册的潜在钓鱼域名（根据排版和同音字等因素），并在对域名进行分析之后给出威胁评级分数，然后再在这些钓鱼站点的登录表单中填写看似有效的凭证。**

大家可以想象一下这种情况：攻击者注册了一个钓鱼域名，比如说acmebnak.com，然后仿制了合法acmebank.com中的原始登录表单，并通过Twitter的广告来散布这个钓鱼域名。这个广告和域名可能会在第二天就被标记为钓鱼站点，但攻击者已从目标用户那里获取到了大量凭证了，而“亡羊补牢”地撤下这个域名并不会对受影响的用户有任何帮助。不过Jeopardize可以向钓鱼表单提供看似有效的凭证数据，并以此来迷惑攻击者。

![](https://image.3001.net/images/20200330/1585583014_5e8213a6d39a4.png!small)

##  存储输出结果

该工具会将所有的检测结果存储到一个XML文件中，样本输出文件内容如下：

    
    
    <domain>
    
          <address>acmebnak.com</address>
    
          <name_servers>ns1.cloudflare.com ns2.cloudflare.com</name_servers>
    
          <mx_servers> </mx_servers>
    
          <date_flag>True</date_flag>
    
          <alexa_flag>False</alexa_flag>
    
          <webserver_flag>True</webserver_flag>
    
          <certificate_flag>False</certificate_flag>
    
          <form_flag>True</form_flag>
    
          <phishing_score>85</phishing_score>
    
        </domain>

##  工具安装

Jeopardize要求Python3环境，并且已经在macOS、Ubuntu
18.04和基于Debian的Linux系统上进行过测试了。首先，我们需要将代码库克隆至本地：

    
    
    git clone https://github.com/utkusen/jeopardize.git

切换到项目目录：

    
    
    cd jeopardize

安装所需的依赖库：

    
    
    pip3 install -r requirements.txt

除此之外，你还需要安装chromedriver。

在Ubuntu上，运行：

    
    
    sudo apt install chromium-chromedriver

在Kali（基于Debian的系统）上，运行：

    
    
    pip3 install chromedriver-binary

在macOS上：

    
    
    brew cask install chromedriver

如果你想要整合Zonefiles.io
API，使用文本编辑器打开jeopardize.py，并使用你自己的密钥替换掉其中的ZONEFILES_API_KEY = ""。

##  工具使用

macOS用户提醒：macOS貌似出于安全机制方面的考虑，会限制多线程，你需要在使用该工具之前运行下列命令：

    
    
    export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

如需了解更多详情，请参考【[这里](https://stackoverflow.com/questions/50168647/multiprocessing-causes-python-to-crash-and-gives-an-error-may-have-been-in-progr/52230415)】。

你需要使用--domain参数来提供需要检测的钓鱼域名，你害需要使用--type来指定需要使用的域名检测方法。

###  样本命令：

    
    
    python3 jeopardize.py --domain facebook.com --type brute

接下来，工具会生成关于“facebook”的单词组合（例如fcabook和facebkook等），并添加所有的顶级域名后缀（com、net、org、xyz等），然后针对这些域名发送whois查询。查询结果将保存到facebook.com.xml文件中，这里不会向检测域名填写登录表单：

###  样本命令：

    
    
    python3 jeopardize.py --domain facebook.com --type daily

该命令将会用Zonefiles.io API抓取过去24小时内注册的所有域名，并搜索它们来生成字典，例如fcabook和facebkook等。

###  样本命令：

    
    
    python3 jeopardize.py --domain facebook.com --type incremental

该命令将会获取之前生成的XML文件，然后爬取其中的域名并更新数据。

如果你想要填写检测域名中的登录表单，你还需要使用-U和-P参数来提供用户名和密码列表。

###  样本命令：

    
    
    python3 jeopardize.py --domain facebook.com --type daily -U user.txt -P pass.txt

如果你想要激活Verbose模式，可以直接在命令结尾处添加-v参数。

##  项目地址

> Jeopardize：【[GitHub传送门](https://github.com/utkusen/jeopardize)】

 ***
参考来源：[utkusen](https://github.com/utkusen/jeopardize)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

