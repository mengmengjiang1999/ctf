**![43043618-29ab7286-8db5-11e8-9603-71b30596d047.png](https://image.3001.net/images/20190306/1551835879_5c7f22e77bb0d.png!small)**

**Sh00t是一个高可定制的渗透测试管理工具，它强调让测试人员手动进行安全测试，并让你专注于执行安全测试任务的本身。此外，Sh00t还为我们提供了测试用例的待办事项清单，以及可以使用自定义的漏洞报告模板来生成漏洞报告。**

##  特性

> 动态任务管理器替换简单的编辑器或任务管理工具
>
> 自动化，可定制的安全测试用例清单，用于替换Evernote，OneNote或其他工具
>
> 管理用于不同目的的自定义bug模板并自动生成漏洞报告
>
> 支持多个评估和项目，以逻辑分离你的不同需求
>
> 所有操作都将自动被保存
>
> 将自动生成的漏洞报告导出到Markdown，并提交HackerOne！
>
> 集成JIRA，ServiceNow集 - 即将推出
>
> 将漏洞报告导出到Markdown - 即将推出
>
> 高可定制性

##  安装

Sh00t安装需要Python 3以及一些额外的软件包。设置Sh00t的最简单方法是使用Conda环境。但是，如果你安装了Python
3和pip，Anaconda是可选的 - 你可以跳到下面的第4步。

**一次性设置**

>
> 1.安装最小的conda安装环境[Miniconda](https://conda.io/miniconda.html)，并按照[安装说明](https://conda.io/docs/user-> guide/install/index.html)进行操作。安装完成后你需要重新加载bash配置文件，或重启终端以使conda命令生效。对于Windows，启动Anaconda
> Prompt并在该窗口中运行以下所有命令。
>
> 2.创建一个新的Python 3环境：conda create -n sh00t python=3.6
>
> 3.激活sh00t环境：conda activate sh00t。如果你看到类似CommandNotFoundError: Your shell has
> not been properly configured to use 'conda
> activate'的错误消息，则你必须手动启用conda命令。按照显示的说明和错误消息进行操作。你可能需要重新加载bash配置文件或重启终端。尝试再次激活sh00t：conda
> activate sh00t。这次你应该可以在终端中看到(sh00t) XXXX$。
>
> 4.克隆或下载该项目的最新版本到你指定的位置：<https://github.com/pavanw3b/sh00t>。git clone需要安装Git。
>
> 5.解压缩sh00t文件夹：cd sh00t。注意，这是项目文件中最外层的sh00t目录而不是sh00t/sh00t。
>
> 6.安装Sh00t依赖包：pip install -r requirements.txt
>
> 7.设置数据库：python manage.py migrate
>
> 8.创建用户帐户：python manage.py createsuperuser并按照UI创建帐户。
>
> 9.可选但推荐：来自OWASP测试指南（OTG）和Web应用程序黑客手册（WAHH）的Avail 174安全测试用例：python reset.py。

**启动Sh00t：**

如果你的计算机上已安装了Python 3，则可以直接跳转到第3步。

> 1.如果是Linux/Mac，则打开终端。如果是Windows，则打开Anaconda Prompt。
>
> 2.如还未激活sh00t环境：conda activate sh00t
>
> 3.如果不在sh00t目录下，请则导航到该目录：cd sh00t
>
> 4.启动Sh00t server：python manage.py runserver
>
> 5.在你习惯的浏览器上访问<http://127.0.0.1:8000/>。使用之前在设置中创建的用户凭据登录。
>
> 6.欢迎来到Sh00t！
>
> 7.完成后，停止服务：Ctrl + C
>
> 8.（可选）关闭sh00t环境以继续其他工作任务：conda deactivate。

###  更新升级：

> 1.导航到克隆sh00t的文件夹：cd sh00t
>
> 2.如果服务正在运行，请停止服务：Ctrl + C
>
> 3.git pull最新的代码库，或从github下载源码并替换文件。
>
> 4.如果未激活sh00t环境：conda activate sh00t
>
> 5.设置依赖项：pip install -r requirements.txt
>
> 6.迁移最新数据库更改：python manage.py migrate
>
> 7.启动server：python manage.py runserver

**关于错误：**

Sh00t是Python编写的，并由Django Web
Framework提供支持。如果出现任何错误问题，你可以通过谷歌搜索错误信息，在大多数情况下能解决你的问题。如果还是无法解决，那么你也可以通过[github
issue](https://github.com/pavanw3b/sh00t/issues/new)反馈问题。

**名词解释：**

> **Flag**
> ：Flag就是一个标记的目标，即需要进行测试的测试用例。Flag是根据所选的测试方法自动生成的，其包含了测试的详细步骤。如果漏洞被确认，那么我们则称它为sh0t。
>
> **Sh0t**
> ：Sh0ts即漏洞。通常，Sh0t会包含漏洞的技术说明，受影响的文件/URL重现及修复建议。Sh0t的大部分内容都是一键生成的，只有像“受影响的参数”，“步骤”这样的动态内容才能更改。
>
> **Assessment** ：评估，即测试评估。它可以是对一个应用或一个项目的评估 - 取决于用户想要管理的方式，是Project的一部分。
>
> **Project** ：项目包含评估。项目可以逻辑分离你的工作。它可以是不同的工作，漏洞赏金，一切由你决定。

##  **它是如何工作的？**

首先创建一个新的评估。选择你要测试的方法。当前有330个测试用例，分为86个Flags，属于13个Modules，这些Modules是根据“Web应用程序黑客手册”测试方法创建的。Modules和Flags可以手动选择和定制。使用Flags创建评估后，现在测试人员必须手动来测试它们，或者在扫描器，工具的帮助下进行半自动化测试，在完成后将其标记为“Done”。在执行评估时，我们通常会提供特定于应用程序中某些场景的自定义测试用例。可以在任何时间点轻松创建一个新的Flag。

每当确认一个Flag为有效bug时，就会创建一个Sh0t。可以选择最匹配的bug模板，sh00t将根据所选模板自动填充漏洞报告。

##  相关截图

仪表盘：

![43355841-9f6167e4-9281-11e8-87fe-761fa35ddc3c.png](https://image.3001.net/images/20190306/1551835733_5c7f2255d8075.png!small)

Flags：

![43355838-9ee99e58-9281-11e8-8724-b9e726fdc58d.png](https://image.3001.net/images/20190306/1551835751_5c7f22674b841.png!small)

在创建新评估时选择方法及测试用例：

![43355840-9f3a3368-9281-11e8-8afd-0467a4ac00b4.png](https://image.3001.net/images/20190306/1551835770_5c7f227ab52e1.png!small)

漏洞报告模板：

![43355839-9f117630-9281-11e8-8a33-a9b5babae698.png](https://image.3001.net/images/20190306/1551835796_5c7f229486613.png!small)

##  Sh00t适用人群

> 1.应用程序安全工程师：渗透测试和漏洞评估
>
> 2.Bug赏金猎人
>
> 3.独立安全研究人员
>
> 4.蓝队，开发人员漏洞修复
>
> 5.任何的网络安全爱好者或从业人员

***参考来源：[GitHub](https://github.com/pavanw3b/sh00t)，FB小编secist编译，转载请注明来自FreeBuf.COM**

