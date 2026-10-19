![](https://image.3001.net/images/20220831/1661946479_630f4a6f9fd414f1cd473.png!small)

## 关于Rekono

Rekono是一款功能强大的自动化渗透测试工具，该工具能够结合其他多种网络安全工具并以自动化的形式完成整个渗透测试过程。在工具运行的过程中所收集到的数据将通过电子邮件或Telegram同时发送给用户，如果需要更加高级的漏洞管理功能，我们还可以将其导入到Defect-Dojo以便进行后续处理。除此之外，Rekono还提供了一个Telegram Bot，我们可以将其用于在任何地方使用任何设备轻松执行渗透测试任务。

## 功能介绍

> 1、结合多种渗透测试工具创建渗透测试任务；
>
> 2、执行渗透测试任务；
>
> 3、执行渗透测试工具；
>
> 4、查看渗透测试结果并通过电子邮件和Telegram通知进行接收；
>
> 5、整合Defect-Dojo以导入和使用Rekono发现的结果；
>
> 6、通过Telegram Bot执行渗透测试任务；
>
> 7、支持字典管理；

## 支持的工具

> [ _theHarvester_](https://github.com/laramies/theHarvester)
>
> [ _EmailHarvester_](https://github.com/maldevel/EmailHarvester)
>
> [ _EmailFinder_](https://github.com/Josue87/EmailFinder)
>
> [ _Nmap_](https://nmap.org/)
>
> [ _Sslscan_](https://github.com/rbsec/sslscan)
>
> [ _SSLyze_](https://nabla-c0d3.github.io/sslyze/documentation/)
>
> [ _SSH Audit_](https://github.com/jtesta/ssh-audit)
>
> [ _SMBMap_](https://github.com/ShawnDEvans/smbmap)
>
> [ _Dirsearch_](https://github.com/maurosoria/dirsearch)
>
> [ _GitLeaks_](https://github.com/zricethezav/gitleaks)&
> [_GitDumper_](https://github.com/internetwache/GitTools/tree/master/Dumper)
>
> [ _Log4j Scanner_](https://github.com/cisagov/log4j-scanner)
>
> [ _CMSeeK_](https://github.com/Tuhinshubhra/CMSeeK/)
>
> [ _OWASP JoomScan_](https://github.com/OWASP/joomscan)
>
> [ _OWASP ZAP_](https://www.zaproxy.org/)
>
> [ _Nikto_](https://github.com/sullo/nikto)
>
> [ _SearchSploit_](https://www.exploit-db.com/searchsploit)
>
> [ _Metasploit_](https://www.metasploit.com/)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/pablosnt/rekono.git

## 工具安装&使用

### Docker使用

在项目根目录中运行下列命令：

    
    
    docker-compose build
    
    docker-compose up -d

如果你需要同时运行多个工具的话，可以设置执行Worker实例的数量：

    
    
    docker-compose up -d --scale executions-worker=5

接下来，访问https://127.0.0.1/即可。

### Rekono CLI使用

如果你使用的是Linux系统，你可以直接使用[ _rekono_ _-cli_](https://github.com/pablosnt/rekono-cli)来安装Rekono：

    
    
    pip3 install rekono-cli
    
    rekono install

接下来，我们就可以使用下列命令来管理Rekono服务了：

    
    
    rekono services start
    
    rekono services stop
    
    rekono services restart

最后，访问https://127.0.0.1/即可。

## 工具使用演示

 **Rekono使用** ：【[ _点我观看_](https://user-images.githubusercontent.com/69458381/165973356-47666e33-e96c-4aee-b4a3-dd99fffe73bd.mp4)】

 **Telegram Bot使用** ：【[ _点我观看_](https://user-images.githubusercontent.com/69458381/165973380-0f3308b6-f5f9-46a7-8d5b-ab89580eb840.mp4)】

## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **Rekono** ：【[ _GitHub传送门_](https://github.com/pablosnt/rekono)】

