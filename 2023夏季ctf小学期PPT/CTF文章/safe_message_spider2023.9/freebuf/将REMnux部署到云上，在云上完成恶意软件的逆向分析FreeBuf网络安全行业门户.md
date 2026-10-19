****

[](https://youtu.be/ug5ZuezbD3c)

![clouds
3.jpg](https://image.3001.net/images/20180204/1517711869424.jpg!small)  

**[REMnux](https://remnux.org/)是一个用于辅助逆向分析人员完成逆向分析任务的免费虚拟机镜像。其中包含了大量的逆向分析工具，可分析基于Web的恶意软件，如恶意的JavaScript，Java程序，和Flash文件。它也有工具可以分析恶意文档，如微软的Office和Adobe
PDF文件，还有通过内存取证逆向病毒的实用工具。目前，REMnux由[Lenny
Zeltser](https://zeltser.com/)维护，并得到了[David
Westcott](https://twitter.com/beast_fighter)的广泛支持与帮助，你可在<https://remnux.org>下载到它。我从当前版本镜像创建了一个Amazon
AMI镜像，以便你在云中轻松创建REMnux实例。你可以[在这里](https://github.com/clr2of8/DeployREMnux)下载到我编写的[DeployREMnux](https://github.com/clr2of8/DeployREMnux)
Python脚本。将你的Amazon账户访问密钥输入到配置，命令行的使用也非常简单：**

    
    
    python DeplyREMnux.py

成功执行上述命令后，输出信息将为我们显示通过SSH和RDP访问REMnux实例所需的信息。

![image2.png](https://image.3001.net/images/20180204/1517711905926.png!small)  

连接之后，你可以使用“update-remnux full”命令更新REMnux。或者，你也可以在部署的同时使用-u更新选项，命令如下：

    
    
    python DeplyREMnux.py -u

在安装脚本之前，你必须确保你当前的Python版本为2.7。

 **第1步：** 安装Apache libcloud库和其他所需库。（在Windows上，你需要先安装[Microsoft Visual
C++编译器](https://www.microsoft.com/en-us/download/details.aspx?id=44266)）：

    
    
    pip install apache-libcloud paramiko pycrypto

* Pip是Python自带的Python包管理器。如无法正常执行，你需要检查Python v2.7是否已被正确安装。在OS X上，你可能需要安装[pip](http://softwaretester.info/install-and-upgrade-pip-on-mac-os-x/)。在Windows上，则你可以在C:\Python27\Scripts目录中找到pip.exe程序。

 **第2步：** 生成一个SSH密钥对

在OS X和Linux上，可以使用ssh-keygen命令完成此操作，命令如下：

    
    
    ssh-keygen -t rsa -b 4096

在Windows上你可能会使用[PuTTYgen](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)工具来生成密钥，但这会导致许多问题。因此为了不必要的麻烦，我建议你可以先在Linux/OS
X上，使用以上命令生成密钥再复制密钥。或者你也可通过Windows的Git Bash或Windows
10的Linux子系统来完成该操作。你还可以从Amazon EC2 web console生成SSH密钥。

 **第3步：**
在这里[创建一个亚马逊账户](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fconsole.aws.amazon.com%2Fconsole%2Fhome%3Fstate%3DhashArgs%2523%26isauthcode%3Dtrue&client_id=arn%3Aaws%3Aiam%3A%3A015428540659%3Auser%2Fhomepage&forceMobileApp=0)。生成访问密钥如下。

  * 登录到你的EC2控制台：<https://console.aws.amazon.com>
  * 选择你的名字->安全凭据。
  * 展开“访问密钥”
  * 创建新密钥
  * 记录访问密钥ID及密钥

 **第4步：** 配置文件设置。DeployREMnux脚本提供了一个配置范本，可以作为你的配置参考。将“DeployREMnux-config.txt.example”重命名为“DeployREMnux-config.txt”。输入你在步骤3中生成的AWS密钥信息，并提供ssh密钥的完整文件路径（在步骤2中生成）。你可以选择配置用于RDP访问实例的密码。如果没有指定密码，将会产生一个随机密码。

    
    
    {
    
      "AmazonConfig": {
    
            "aws_access_key_id": "put_your_amazon_access_key_id_here",
    
            "aws_secret_access_key": "put_your_amazon_access_secret_here ",
    
            "aws_instance_size": "t2.micro"
    
      },
    
      "SshConfig": {
    
              "private_key_file": "/root/.ssh/id_rsa",
    
              "public_key_file": "/root/.ssh/id_rsa.pub"
    
      },
    
      "RemnuxConfig": {
    
               "remnux_user_password": ""
    
      }
    
    }

注意，Windows指定密钥文件路径，需要使用正斜杠（例如（c:/path/to/key/id_pub））

最后，可以使用配置文件来指定已部署实例的大小，默认值为“t2.micro”，你也可以根据自己的需求进行改进。你的实例将被部署到us=east-1[地区](https://docs.aws.amazon.com/general/latest/gr/rande.html)（a.k.a
N. Virginia）。

当你完成对REMnux实例使用后，你可以在提示符下按“Y”来终止它，或者如果你之前输入过“n”，你也可以使用'python DeployREMnux.py
-t <node id>'选项来关闭实例。其中<node id>可以从上述命令的输出或[Amazon
Web控制台](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fconsole.aws.amazon.com%2Fec2%2Fv2%2Fhome%3Fstate%3DhashArgs%2523%26isauthcode%3Dtrue&client_id=arn%3Aaws%3Aiam%3A%3A015428540659%3Auser%2Fec2&forceMobileApp=0)中确定。

![image3.png](https://image.3001.net/images/20180204/15177119379564.png!small)  

在这里我需要提醒大家的是，请务必确保你的[Amazon
console](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fconsole.aws.amazon.com%2Fec2%2Fv2%2Fhome%3Fstate%3DhashArgs%2523%26isauthcode%3Dtrue&client_id=arn%3Aaws%3Aiam%3A%3A015428540659%3Auser%2Fec2&forceMobileApp=0)没有任何可能导致你额外花销的空闲资源。同时，在区域选择上也请确保区域的正确选择（北弗吉尼亚州）。如果需要，你可以通过Web界面来手动终止实例。

![image4.png](https://image.3001.net/images/20180204/1517711957153.png!small)

##  *参考来源：[blackhillsinfosec](https://www.blackhillsinfosec.com/deploy-remnux-cloud-reverse-engineering-malware-cloud/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM

