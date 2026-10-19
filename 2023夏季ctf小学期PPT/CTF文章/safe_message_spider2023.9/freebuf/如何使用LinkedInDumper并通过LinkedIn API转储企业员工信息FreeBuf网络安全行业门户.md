![](https://image.3001.net/images/20230719/1689766873_64b7cbd904d33971dd457.jpeg!small)  

## 关于LinkedInDumper

LinkedInDumper是一款针对LinkedIn社交媒体网络平台的数据收集工具，该工具基于Python
3开发，可以帮助广大企业网络安全管理人员或其他领域的安全专家转储目标组织或企业的员工LinkedIn数据。

该工具支持收集和转储的数据包括目标的完整姓名、职位（头衔）、地理位置和用户资料链接等等。如果目标组织的员工不超过十人的话，该工具只需要两次API调用即可获取目标组织所有员工的LinkedIn数据。否则，我们就需要对API返回的结果进行分页了。除此之外，我们还可以使用
--email-format命令行接口参数来定义一个Python字符串格式，并根据检索到的名字和姓氏自动生成电子邮件地址。

## 工具要求

LinkedInDumper能够与非官方LinkedIn Voyager
API进行交互，但该服务需要进行身份验证。因此，我们必须拥有一个有效的LinkedIn用户帐户。为了方便起见，LinkedInDumper只会要求用户提供一个Cookie值，这种做法也适用于启用了2FA保护的账户。

除此之外，我们还需要提供一个目标组织或企业的LinkedIn主页的URL地址，工具会根据这个地址来转储员工信息。

### 如何获取LinkedIn Cookie？

> 1、登录[
> _www.linkedin.com_](http://www.linkedin.com/)，通过浏览器的开发者工具查看并获取li_at会话Cookie值；
>
> 2、在工具Python脚本的li_at变量中或在临时调用脚本时的--cookie命令行参数选项中指定你获取到的li_at会话Cookie值；

### 如何获取企业LinkedIn URL地址？

> 1、在搜索引擎或直接在LinkedIn中直接搜索目标组织或企业；
>
> 2、LinkedIn企业URL地址大致形式如下：https://www.linkedin.com/company/xxx；

## 工具下载

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/l4rm4nd/LinkedInDumper.git

安装完成后，切换到项目目录中，并使用pip命令和项目提供的requirements.txt文件安装该工具所需的其他依赖组件：

    
    
    cd LinkedInDumper
    
    pip install -r requirements.txt

## 工具使用帮助

    
    
    usage: linkedindumper.py [-h] --url <linkedin-url> [--cookie <cookie>] [--quiet] [--include-private-profiles] [--email-format EMAIL_FORMAT]
    
     
    
    options:
    
      -h, --help            显示工具帮助信息和退出
    
      --url <linkedin-url>  目标企业LinkedIn URL链接，例如-https://www.linkedin.com/company/<company>
    
      --cookie <cookie>     设置LinkedIn 'li_at' 会话Cookie
    
      --quiet               仅显示员工结果数据
    
      --include-private-profiles
    
                            显示私密账号信息
    
      --email-format        设置电子邮件的Python 字符串格式，例如：
    
                             [1] john.doe@example.com > '{0}.{1}@example.com'
    
                             [2] j.doe@example.com > '{0[0]}.{1}@example.com'
    
                             [3] jdoe@example.com > '{0[0]}{1}@example.com'
    
                             [4] doe@example.com > '{1}@example.com'
    
                             [5] john@example.com > '{0}@example.com'
    
                             [6] jd@example.com > '{0[0]}{1[0]}@example.com'

## 工具使用样例

### 样例一：Docker运行

    
    
    docker run --rm l4rm4nd/linkedindumper:latest --url 'https://www.linkedin.com/company/apple' --cookie <cookie> --email-format '{0}.{1}@apple.de'

### 样例二：本地Python运行

    
    
    python3 linkedindumper.py --url 'https://www.linkedin.com/company/apple' --cookie <cookie> --email-format '{0}.{1}@apple.de'

### 输出结果

工具运行后将返回目标组织员工数据，数据以分号分隔：

    
    
    ██▓     ██▓ ███▄    █  ██ ▄█▀▓█████ ▓█████▄  ██▓ ███▄    █ ▓█████▄  █    ██  ███▄ ▄███▓ ██▓███  ▓█████  ██▀███  
    
    ▓██▒    ▓██▒ ██ ▀█   █  ██▄█▒ ▓█   ▀ ▒██▀ ██▌▓██▒ ██ ▀█   █ ▒██▀ ██▌ ██  ▓██▒▓██▒▀█▀ ██▒▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒
    
    ▒██░    ▒██▒▓██  ▀█ ██▒▓███▄░ ▒███   ░██   █▌▒██▒▓██  ▀█ ██▒░██   █▌▓██  ▒██░▓██    ▓██░▓██░ ██▓▒▒███   ▓██ ░▄█ ▒
    
    ▒██░    ░██░▓██▒  ▐▌██▒▓██ █▄ ▒▓█  ▄ ░▓█▄   ▌░██░▓██▒  ▐▌██▒░▓█▄   ▌▓▓█  ░██░▒██    ▒██ ▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  
    
    ░██████▒░██░▒██░   ▓██░▒██▒ █▄░▒████▒░▒████▓ ░██░▒██░   ▓██░░▒████▓ ▒▒█████▓ ▒██▒   ░██▒▒██▒ ░  ░░▒████▒░██▓ ▒██▒
    
    ░ ▒░▓  ░░▓  ░ ▒░   ▒ ▒ ▒ ▒▒ ▓▒░░ ▒░ ░ ▒▒▓  ▒ ░▓  ░ ▒░   ▒ ▒  ▒▒▓  ▒ ░▒▓▒ ▒ ▒ ░ ▒░   ░  ░▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░
    
    ░ ░ ▒  ░ ▒ ░░ ░░   ░ ▒░░ ░▒ ▒░ ░ ░  ░ ░ ▒  ▒  ▒ ░░ ░░   ░ ▒░ ░ ▒  ▒ ░░▒░ ░ ░ ░  ░      ░░▒ ░      ░ ░  ░  ░▒ ░ ▒░
    
      ░ ░    ▒ ░   ░   ░ ░ ░ ░░ ░    ░    ░ ░  ░  ▒ ░   ░   ░ ░  ░ ░  ░  ░░░ ░ ░ ░      ░   ░░          ░     ░░   ░
    
        ░  ░ ░           ░ ░  ░      ░  ░   ░     ░           ░    ░       ░            ░               ░  ░   ░     
    
                                          ░                      ░                                         ░ by LRVT      
    
     
    
    [i] Company Name: apple
    
    [i] Company X-ID: 162479
    
    [i] LN Employees: 1000 employees found
    
    [i] Dumping Date: 17/10/2022 13:55:06
    
    [i] Email Format: {0}.{1}@apple.de
    
     
    
    Firstname;Lastname;Email;Position;Gender;Location;Profile
    
    Katrin;Honauer;katrin.honauer@apple.com;Software Engineer at Apple;N/A;Heidelberg;https://www.linkedin.com/in/katrin-honauer
    
    Raymond;Chen;raymond.chen@apple.com;Recruiting at Apple;N/A;Austin, Texas Metropolitan Area;https://www.linkedin.com/in/raytherecruiter
    
     
    
    [i] Successfully crawled 2 unique apple employee(s). Hurray ^_-
## 项目地址

 **LinkedInDumper** ：【[
_GitHub传送门_](https://github.com/l4rm4nd/LinkedInDumper)】

## 参考资料

> [ _http://www.linkedin.com/_](http://www.linkedin.com/)

