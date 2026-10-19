![](https://image.3001.net/images/20230426/1682522403_64494123ddf4cee5e37b3.png!small)

Oracle Cloud Infrastructure Network Firewall
是下一代托管网络防火墙，入侵检测和预防服务（IDPS）适用于由Palo Alto Networks提供支持的Oracle Cloud
Infrastructure (OCI) 虚拟云网络 (VCN)。

如果你一直使用PaloAlto 防火墙，并计划迁移到 Oracle Cloud Infrastructure (OCI)
网络防火墙，那么就需要将现有的防火墙规则转换为 OCI Network Firewall 策略。

如何使用自动化工具将防火墙规则从 PaloAlto 防火墙迁移至OCI 网络防火墙？在本文中，我将给大家答案。

## 使用此工具的前提条件：

1.Python：在系统上安装 Python 3。

> 点击此[链接](https://realpython.com/installing-python/)在电脑上安装 python。

2\. 所需包：代码需要几个Python包才能运行，在电脑中运行以下命令，确保包能安装成功：

    
    
    pip install pandas xml ipaddress

3\. Palo Alto 配置文件：脚本需要一个名为`config.xml`的 Palo Alto
配置文件，并放置在与脚本相同的目录中，要确保文件是放在这个目录下。

> 点击此[链接](https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-admin/firewall-> administration/manage-configuration-backups/save-and-export-firewall-> configurations)，从防火墙导出 running-config.xml。

4\. 访问 OCI 防火墙服务：有权访问 OCI 防火墙服务，并且应该具有创建 IP 地址、IP 地址列表和应用程序列表的必要权限。

> 点击此[链接](https://docs.oracle.com/en-us/iaas/Content/network-firewall/iam-> policy-reference.htm)，了解访问所需的 IAM 策略 — OCI 网络防火墙。

5\. OCI API 密钥：需要有一个 OCI API 密钥才能访问 OCI API，可以从 OCI 控制台生成 API 密钥对。

6\. OCI 配置文件：需要一个 OCI 配置文件，其中包含租赁 OCID、用户 OCID 和 API 密钥的位置，可以按照[OCI
文档](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm)中的说明创建配置文件。

7\. OCI SDK：在系统上安装 OCI SDK，通过在电脑中运行以下命令来安装 SDK：

    
    
    pip install oci

有关不同操作系统的 OCI CLI 安装的详细说明，请观看以下视频：

  * Linux：观看此[视频](https://www.youtube.com/watch?v=bY3jQMMHxdw)
  * Windows：观看此[视频](https://www.youtube.com/watch?v=rEHwcJdRf8M)
  * Mac：观看此[视频](https://www.youtube.com/watch?v=0k2Lj0oMDK4)

 **注意：** 如果未安装 OCI CLI，则可以将该工具创建的 JSON 文件复制到 OCI Web CLI（在 OCI 控制台中可用），然后执行
OCI CLI 命令来更新防火墙策略。

![](https://image.3001.net/images/20230426/1682522558_644941be7289986562c34.png!small)

下面是更新 IP 地址列表的命令，然后是应用程序列表和安全规则。

    
    
    oci network-firewall network-firewall-policy update --network-firewall-policy-id <ocid1.networkfirewallpolicy.oc1.ap-mumbai-1.xxxx> --ip-address-lists file://IP-Address-List.json
    oci network-firewall network-firewall-policy update --network-firewall-policy-id <ocid1.networkfirewallpolicy.oc1.ap-mumbai-1.xxxx> --application-lists file://Application-List.json
    oci network-firewall network-firewall-policy update --network-firewall-policy-id <ocid1.networkfirewallpolicy.oc1.ap-mumbai-1.xxxx> --security-rules file://security_rules_v2.json

## 用法：

使用“PaloAlto-Migration.py”脚本转换 PaloAlto 防火墙策略，请按照以下步骤操作：

1.在 Mac 或 Windows 计算机上打开终端或命令提示符。

2.使用“cd”命令导航到“PaloAlto-Migration.py”脚本所在的目录。

3.将 PaloAlto 防火墙备份 (running-config.xml) 文件移动到与脚本相同的文件夹中，将文件重命名为 config.xml。然后在
cmd 行/终端中，使用“cd”命令导航到该文件夹​​。

4.在终端或命令提示符中键入“python3 PaloAlto-Migration.py”，然后按 Enter。

    
    
    Python3 PaloAlto-Migration.py

5\. 脚本将提供转换、安装防火墙规则、退出脚本三种选项。

选择适当的选项来转换 PaloAlto 防火墙策略，参考如下。

    
    
    Please use this tool to convert - Palo Alto Firewall rules to OCI Network Firewall rules
    Select an option:
    1. Convert rules
    2. Install rules to OCI Firewall
    3. Exit

第一次执行脚本时，选择选项 1，然后输出应如下所示。

    
    
    Enter option number: 1
    Executing Python script A to convert rules...
    Coversion Done!! Review the missing_items.xlsx , update the IP-Address or Service columns without fail!

a) PaloAlto 防火墙允许管理员在安全规则中输入 IP 地址，而无需创建 IP
地址对象。但是对于OCI防火墙来说，这些对象需要先创建，然后才能在安全规则中使用。

b) 此外，PaloAlto 防火墙允许管理员在安全规则中使用 App-ID。但是，如果使用此类 App-ID，它们将不会自动添加到 OCI
Application-List.json 中。

因此，该脚本会生成一个名为“missing_items.xlsx”的 Excel 工作表，需要管理员手动输入丢失对象的详细信息。

点击下面的演示视频了解如何运行此工具：

  

验证“missing_items.xlsx”表并输入所需的详细信息后，继续执行选项 2，输出将如下例所示：

    
    
    Enter option number: 2
    Executing Python script B to install rules to OCI Firewall...
    Enter compartment OCID: ocid1.compartment.oc1..aaaaaaaa5nmydshoioxvnbqobahkt5yu7dz4hynywmea74ag4qeecydaiq6a
    Enter display name: PaloAlto-demo
    Enter profile name: DEFAULT
    Wait while your new firewall policy is getting created :
    {
    "opc-work-request-id": "ocid1.networkfirewallworkrequest.oc1.ap-hyderabad-1.amaaaaaadrm45caaxmzpl6fh6pr4n5cc3rh4zr23vwiio7f2q4thdphimi3q"
    }
    Wait while your IP-Address-List is getting updated..
    {
    "opc-work-request-id": "ocid1.networkfirewallworkrequest.oc1.ap-hyderabad-1.amaaaaaadrm45caanq73khkk6sfk6zbf3ynisgx725cs5uthdhqly4j4hxqq"
    }
    Wait while your Application-List is getting updated..
    {
    "opc-work-request-id": "ocid1.networkfirewallworkrequest.oc1.ap-hyderabad-1.amaaaaaadrm45caayphi6lii7dxdbn5k36bitxciauurzpdsjs5xuqsw7nuq"
    }
    Wait while your Security-rules are getting updated..
    
    Select an option:
    1. Convert rules
    2. Install rules to OCI Firewall
    3. Exit
    Enter option number: 3
    Exiting...

成功运行脚本后，我们应该会看到在脚本运行的路径中创建了三个 JSON 文件（IP-Address-List.json、Applications-List.json 和 Security_Rules_v2.json），然后是脚本尝试在 OCI 防火墙中安装策略。

> [点击此处](https://github.com/karthikmani84/PaloAlto-Migration-Tool)下载脚本

##  **重要提示：**

截至目前，OCI 网络防火墙的 GUI（图形用户界面）限制用户创建超过 25 个对象，例如 IP 地址列表、应用程序列表和 URL 列表。不过OCI
Firewall 产品团队正在努力去除这一限制。

此脚本使用 API 来创建迁移规则所需的其他对象。我已成功迁移包含多达 300 条安全规则和 600 个对象（包括 IP
地址和应用程序）的规则。如果你的规则库比这个大，转换它们应该不是问题。但是，在 OCI 防火墙上安装它们时可能会遇到错误。

在这种情况下，可以向 OCI 网络防火墙团队反馈，请求协助。

##  **已知的问题：**

1.此工具使用来自 PaloAlto 防火墙的 XML 文件作为输入。如果它们的 XML 格式发生变化，则意味着需要更改此代码的某些部分。

2.此版本的代码仅关注防火墙访问规则。PBR（基于路由的策略/基于策略的路由）不会作为此代码的一部分导出。

3.如果还想查看 PaloAlto 防火墙和 OCI 网络防火墙中使用的功能。OCI 的本地防火墙非常精简，预计不会充当
NAT、VPN、代理或路由设备。此类功能，当你选择使用 OCI Network Firewall 时，将迁移到其他原生服务。因此，这些规则不会一起迁移。

4.“missing_items.xlsx”将列出 IP 地址和应用程序列表中缺少的 IP 地址对象名称和服务对象名称。这些详细信息必须在 Excel
中手动捕获。该代码不对输入进行任何格式检查。如果输入的 IP 地址或服务详细信息不正确，将无法安装。

##  **代码设计：**

> PaloAlto-Migration.py:

  1. 提供3个选项（1.转换规则；2.安装规则；3.退出）。
  2. 选项 1：执行 PA-Convert.py。
  3. 选项 2：执行 PA-Install.py。
  4. 选项 3：退出。

> PA-Convert.py:

  1. 清理对象名称的功能是按照 OCI 网络防火墙喜欢的方式创建的。
  2. Palo Alto Config.xml 文件已加载。
  3. config.xml 中的 IP 地址对象、IP 地址组和 IP 范围详细信息将转换为 IP-Address.json。
  4. 具有端口/协议信息的服务对象和服务组将转换为 Apps-List.json。
  5. security_rules.json 使用从 config.xml（安全规则部分）中提取的源、目标和应用程序创建。
  6. 将 IP-Address.json 和 Apps-List.json 与 security-rules.json 进行比较，将安全规则中不在其他两个 JSON 文件中的 IP 地址和应用程序导出到名为“missing_items.xlsx”的 Excel 工作表。

> PA-Install.py:

  1. 阅读“missing_items.xlsx”并对 App-List.json 进行更正并创建 Application-List.json。
  2. 阅读“missing_items.xlsx”并对 IP-Address.json 进行更正并创建 IP-Address-List.json。
  3. 识别混合了基于 ICMP 和 TCP/UDP 的应用程序的安全规则。将它们创建为单独的规则，因为 OCI 防火墙不允许使用 ICMP 和非 ICMP 应用程序创建访问规则。然后创建 Security_Rules_v2.json。
  4. 最后，在 OCI 中创建防火墙策略并使用 OCI CLI 集成（如果可用！）推送 JSON 文件。

## 最后

防火墙规则迁移通常是我们准备更换现有防火墙时最耗时的步骤。本文介绍的这种工具可以帮助大家快速地完成，但是大家还是要仔细规划生产网络上的防火墙迁移。

## 来源

> https://medium.com/oracledevs/how-to-automate-conversion-of-firewall-rules-> from-paloalto-to-oci-network-firewall-acbecddd7345

  

  

