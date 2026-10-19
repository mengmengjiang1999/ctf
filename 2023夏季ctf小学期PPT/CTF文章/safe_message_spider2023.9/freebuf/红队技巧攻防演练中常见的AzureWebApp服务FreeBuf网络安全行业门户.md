***本文仅用于技术交流，严禁用于任何非法用途，违者后果自负**

 **在本博客中，我将介绍如何将Azure App
Services用于红队目标。您可能会问什么是Azure应用服务？Microsoft定义的Azure应用服务：**

“在容器中或在任何操作系统上运行时，可以快速构建，部署和扩展使用流行框架.NET，.NET
Core，Node.js，Java，PHP，Ruby或Python创建的Web应用程序。通过使用完全托管的平台来执行操作和监视任务，可以满足严格的企业级性能，安全性和合规性要求。”
— <https://azure.microsoft.com/en-us/services/app-service/>

除了能够运行.NET，Python和Node.js等许多平台之外，最棒的是，在部署应用程序时，您会在“
.azurewebsites.net”上收到一个自定义子域。挺好的！使用Azure PowerShell模块也很容易部署网站和应用程序。

在红队目标方面，我们可以使用Azure Apps做什么？

> 静态HTML页面
>
> PHP网络钓鱼页面
>
> 通过Flask进行C2重定向

Microsoft示例：

> 静态HTML：[https](https://github.com/Azure-Samples/html-docs-hello-world) :
> [//github.com/Azure-Samples/html-docs-hello-world](https://github.com/Azure-> Samples/html-docs-hello-world)
>
> NodeJS：[https](https://github.com/Azure-Samples/nodejs-docs-hello-world) :
> [//github.com/Azure-Samples/nodejs-docs-hello-> world](https://github.com/Azure-Samples/nodejs-docs-hello-world)
>
> Python：[https](https://github.com/Azure-Samples/python-docs-hello-> world)：[//github.com/Azure-Samples/python-docs-hello-> world](https://github.com/Azure-Samples/python-docs-hello-world)

###  先决条件：

> Azure PowerShell模块[https://docs.microsoft.com/zh-> cn/powershell/azure/install-az-> ps?view=azps-3.8.0](https://docs.microsoft.com/en-> us/powershell/azure/install-az-ps?view=azps-3.8.0)
>
> Git

###  Azure PowerShell静态HTML部署

首先，使用以下命令登录到您的Azure服务：az login

要获得所有可用命令的帮助，请使用：az webapp up help

对于静态html部署，请从Web应用程序的根文件夹开始，然后简单地使用以下方法部署应用程序：az webapp up --location eastus
--resource-group htmlphishtest --name htmlphishtest --html

请注意，完成部署后，您将拥有一个域“ htmlphishtest.azurewebsites.net”！

在这个简单的示例中，我使用的是“ html-docs-hello-world”页面的修改版本，该页面将为目标提供可执行文件。

这是浏览时的样子：

![](https://image.3001.net/images/20200518/1589785255_5ec232a730415.png!small)

###  PHP凭据网络钓鱼

使用来自zphisher平台（[https://github.com/htr-tech/zphisher）的](https://github.com/htr-tech/zphisher) PHP应用程序，我们也可以通过Azure
Apps提供凭据收集页面。这需要花费更多的精力，并且需要安装Git。

有关此部署的Microsoft文档，请访问[https://docs.microsoft.com/zh-cn/azure/app-service/app-service-web-get-started-php](https://docs.microsoft.com/en-us/azure/app-service/app-service-web-get-started-php)。

首先，创建您的部署用户和密码。这些凭证将用于克隆和推送您部署的Git存储库。

    
    
    az webapp deployment user set --user-name  --password

接下来，创建一个资源组：

az group create --name myResourceGroup --location eastus

创建一个Azure App Service计划：

az appservice plan create --name myAppServicePlan --resource-group
myResourceGroup --sku FREE

使用Bash或Powershell创建空的Web应用程序。使用Bash：az webapp create --resource-group
myResourceGroup --plan myAppServicePlan --name --runtime "PHP|7.4"
--deployment-local-git

使用PowerShell：az --% webapp create --resource-group myResourceGroup --plan
myAppServicePlan --name --runtime "PHP|7.4" --deployment-local-git

此命令将输出您的应用程序的详细信息，包括要克隆的git URL。从干净的文件夹中，使用为应用程序设置的用户名和密码克隆空的git存储库。

例如：git clone
[https://myphptestapp2.scm.azurewebsites.net:443/myphptestapp2.git](https://myphptestapp2.scm.azurewebsites.net/myphptestapp2.git)

将您的PHP网络钓鱼应用程序复制到空文件夹中。在这种情况下，我使用了zphisher的“ Microsoft”文件夹。

用git添加文件：

> git add *

提交更改：

> git commit -a -m "Initial Commit"

将您的仓库推送到您的应用程序：

> git push

您的网络钓鱼应用程序现在应托管在azurewebsites.net URL中

![](https://image.3001.net/images/20200518/1589785255_5ec232a7175e4.png!small)

现在，要访问日志，请通过位于Azure门户中的应用程序的控制台页面打开一个控制台。

![](https://image.3001.net/images/20200518/1589785255_5ec232a731184.png!small)

在这种情况下，请在usernames.txt文件中查找所有捕获的凭据。

![](https://image.3001.net/images/20200518/1589785255_5ec232a79e0b9.png!small)

###  Flask C2重定向

使用Python
Flask应用程序，还可以执行重定向到命令和控制（C2）服务器的操作。在此示例中，我使用的是“魔术头”，如我以前的博客中有关保护重定向器的描述。在Cobalt
Strike中，可以在个人资料的“客户”部分下设置此魔术标头。另外，请确保注释掉第一个HEADER变量，然后取消注释第二个HEADER和HEADER_KEY行以在application.py中使用魔术头。

![](https://image.3001.net/images/20200518/1589785255_5ec232a7f0b10.png!small)

在Python-Flask-Redirector文件夹中，使用您的自定义变量执行以下命令：az webapp up --location eastus
--resource-group mynewresourcegroup --name mynewsubdomain --SKU FREE

启动信标后，重定向器将检查魔术头是否存在，否则它将重定向到您选择的站点。请注意通过Azure
Apps运行的该信标的外部IP地址。将此范围列入白名单可能会很好。

![](https://image.3001.net/images/20200518/1589785256_5ec232a8511af.png!small)

如果要通过安全FTP管理应用程序，可以通过在“部署中心”中的Azure应用程序设置中启用它来进行管理。有关此的更多信息，请访问[https://docs.microsoft.com/zh-cn/azure/app-service/deploy-ftp](https://docs.microsoft.com/en-us/azure/app-service/deploy-ftp)

![](https://image.3001.net/images/20200518/1589785256_5ec232a84515a.png!small)

***参考来源:[trustwave](https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/azure-web-app-service-for-offensive-operations/)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

