##
![20180903085536.jpg](https://image.3001.net/images/20180903/1535936152_5b8c8698d91cd.jpg!small)

## 背景

**亚马逊AWS云服务平台是全球最受欢迎的云平台之一。由于其成本低、灵活性强、速度快等优势，吸引了大量的企业客户，越来越多的企业开始将其技术资产转移到了云端。随着模式的转变，Sysadmin和DevOps团队也不得不面对随之而来的新安全挑战。这已不仅仅是安全意识缺失的问题。即使是一些大型企业（如GoDaddy和Uber）也曾因AWS配置缺陷，而陷入安全危机。因此，offensive
security社区迫切需要一种结构化可提供全面测试AWS的工具。**

## Pacu：一款AWS渗透测试框架

Pacu（亚马逊河中的一种食人鱼）是一款全面的AWS安全测试工具包，专为攻击性安全从业者而设计。

虽然，市面上已有多款针对AWS的安全扫描器，但Pacu的设计与Metasploit相当。Pacu是由Python
3编写的，并采用了模块化的架构。此外，Pacu还为测试的每个过程都提供了相应的工具，几乎涵盖了一个完整的网络杀伤链条。

Pacu可以说是之前AWS红队合作的所有开发经验和研究的集合。自动化评估组件不仅可以提高效率，还可以使我们的评估团队在大型环境中更加全面透彻的了解目标应用。现在，你只需几分钟就可以完成手动枚举任务，而在此之前你可能需要数天甚至更长的时间。

该项目刚刚结束其私人测试版，并已作为一个开源项目正式发布在[Github](https://github.com/RhinoSecurityLabs/pacu)上。

## 特性

目前，Pacu有超过35个模块，其中包括侦察，持久性，权限提升，枚举，数据窃取，日志操作等。

Pacu可用于获取凭据，但它的真正价值并不体现于此，而是在后渗透测试阶段。在此之前，你完全可以通过其它手段来取得凭据，例如网络钓鱼，Web应用程序漏洞，密码重用等。Pacu能够测试S3
bucket配置和权限缺陷，并通过Lambda后门与其建立访问，妥协EC2实例，窃取数据，提升权限以及通过中断监控和日志记录来覆盖磁道，包括CloudTrail，GuardDuty等。

以下列举的是一些最受欢迎的模块：

> **confirm_permissions** \- 枚举当前帐户的已确认权限列表
>
> **privesc_scan** \- 滥用20多种不同的权限提升方法进一步的获取访问权限
>
> **cloudtrail_csv_injection** \- 将恶意公式注入CloudTrail CSV exports
>
> **disrupt_monitoring** \-> 针对GuardDuty，CloudTrail，Config，CloudWatch和VPC，破坏各种监控和日志记录功能
>
> **backdoor_users_ [keys / passwords]** \- 通过向其他IAM用户帐户添加凭据来建立后门帐户访问权限
>
> **sysman_ec2_rce** \- 滥用AWS Simple Systems
> Manager尝试在各种EC2实例上获取root（Linux）或SYSTEM（Windows）级远程代码执行
>
> **backdoor_ec2_sec_groups** \- 向EC2安全组添加后门规则，以访问私有服务

## 架构

Pacu的开源和模块化架构为你提供更加轻松全面的审计。其通用语法和数据结构也使模块更加易于构建和扩展 -而无需指定AWS区域或在模块之间进行冗余权限检查。本地SQLite数据库用于管理和操作检索到的数据，最大限度地减少API调用（和相关日志）。

会话的分离，可以避免两个用户或公司间在测试过程中发生混淆。报告和攻击审计也内置于框架中；Pacu通过命令记录和导出来协助文档处理，并为整个测试过程建立时间表。

此外，我们还向开发人员公开了一个内置的API，以方便对一些常见操作的访问。具体可参见我们的[GitHub](https://github.com/RhinoSecurityLabs/pacu/wiki)文档。

## 安装和设置

Pacu在macOS和Linux上都已得到官方的支持，只需将Python版本升级为3.5以上，以及使用pip3来安装一些库即可。

安装非常简单，克隆库运行安装脚本。安装脚本将为我们检查并下载所有必需的依赖项：

    
    
    > git clone https://github.com/RhinoSecurityLabs/pacu
    > cd pacu
    > bash install.sh
    > python3 pacu.py

启动Pacu：

    
    
    > python3 pacu.py

在Pacu启动后，系统将要求你提供会话名称，接着你可以使用'set_keys'命令来添加你获取的凭据并运行模块。

核心命令：

    
    
    list/ls                             列出所有模块
    search [cat[egory]] <search term>   按名称或类别搜索可用模块列表
    help                                显示此页面的信息
    help <module name>                  显示模块信息
    whoami                              显示有关活动访问密钥的信息
    data                                显示此会话中存储的所有数据。
    data <service>|proxy                显示指定服务的所有数据
    services                            显示已收集数据的服务列表
    regions                             显示所有有效AWS区域列表
    update_regions                      运行脚本更新区域数据库
    set_regions <region> [<region>...]  设置此会话的默认区域。
    run/exec <module name>              执行模块
    set_keys                            向会话添加一组AWS密钥
    swap_keys                           将当前活动的AWS密钥更改为另一个密钥
    exit/quit                           退出Pacu

几乎所有命令都是自动完成的。

更多内容请参考官方[Pacu GitHub
wiki](https://github.com/RhinoSecurityLabs/pacu/wiki/Quick-Start-Guide)页面。

## 视频演示

以下是Spencer Gietzen在OWASP西雅图上向大家展示的，使用Pacu进行模拟AWS渗透测试的演示视频。

使用Pacu，Spencer Gietzen实现了从权限枚举，特权提升，建立持久性，到最终获取EC2实例远程代码执行的过程。

## 后续开发

未来我们将继续添加更多更好用的功能，以下功能已在我们的计划之中：

> 内置安全网，用于避免一些意外的安全威胁
>
> 使用NoSQL的新数据库格式替换当前的SQLite
>
> PinPoint SMS/email/mobile的实时信息推送
>
> S3项目拦截和修改
>
> RDS，Route 53，CloudFormation模块开发

## AWS渗透测试书籍

在此向大家做个预告。由Rhino创始人Benjamin Caudill撰写并由Packt进行出版的“[Hands-On AWS Penetration
Testing with Kali Linux](http://a.co/3fr8Jq9)”一书将于2019年2月正式发布。

## 关于Pacu的一些线下沙龙

在接下来的几个月中，我们将举办一些介绍Pacu的线下活动，具体地点及时间安排如下：

> **GrrCon** – Grand rapids, MI – 2:30 PM Friday 9/7
>
> **iRespondCon** – San Francisco, CA – Wednesday 9/12
>
> **BSides Idaho Falls** – Idaho Falls, ID – Saturday 9/15
>
> **SAINTCON** – Provo, UT – 9/25-9/28
>
> **CactusCon** – Mesa, AZ – 9/28-9/29
>
> **DerbyCon** – Louisville, KY – 10/5-10/7
>
> **RhinoCon** – Seattle, WA – TBA
>
> **Seattle CSA** – Seattle, WA – Wednesday 10/24
>
> **WildWestHackinFest** – Deadwood, SD – 4 PM Friday 10/26

此外，我们还为Pacu专门建立了一个[Slack workspace](https://join.slack.com/t/pacu-cloudgoat/shared_invite/enQtNDE3OTk0MjA3NTA2LTUyNDBiNWI4ZDhkMzRjZTQwODY5YjM0NjU4ODE5ZTk3ODc3MmM5YTMyNWU5NWQ4ODdiMWNhMzRjNWMwYWI4NzU)，欢迎大家加入讨论！

## 总结

通过渗透测试确保AWS的安全性，已然已经成为了企业的首选项。

Pacu完全可以成为你工具包中的核心安全工具。此外，我们也欢迎社群对我们的请求及反馈。另外，如果你希望对该项目进行[贡献](https://github.com/RhinoSecurityLabs/pacu/wiki/Contribution-Guidelines)，那么请阅读我们的代码约定和git流程说明。谢谢！

*******参考来源：[rhinosecuritylabs](https://rhinosecuritylabs.com/aws/pacu-open-source-aws-exploitation-framework/)，** **FB小编 secist 编译，转载请注明来自FreeBuf.COM**

