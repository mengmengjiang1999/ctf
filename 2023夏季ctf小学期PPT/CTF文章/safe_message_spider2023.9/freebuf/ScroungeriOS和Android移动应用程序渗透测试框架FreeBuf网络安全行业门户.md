**Scrounger是一个模块化的移动应用程序渗透测试框架工具。它将Android和iOS这两个主流的移动操作系统同时整合到了一个框架中，极大的方便和满足了我们日常任务的需求。此外，Scrounger还具有使用方便、文档丰富、易于扩展等优点。**

##  **视频简介**

Scrounger由许多模块组成，这些模块都建立在一个强大的核心之上。这样做的好处是，可以像Metasploit一样易于扩展。如果你希望Scrounger执行其他检查，你只需添加一个新模块，然后通过Scrounger的交互式控制台或命令行界面执行。

此外，Scrounger同时包含了Android和iOS模块。因此，在移动应用评估期间你不需要使用多款工具，而只需使用这一款工具学习一组命令就可以完成任务。

Scrounger中已经捆绑了几个模块，你可以运行这些模块来对移动应用程序执行多项检查。

![Scrounger.png](https://image.3001.net/images/20180901/1535793648_5b8a59f097d4a.png!small)

##  **运行条件**

在主机和某些iOS二进制文件需要安装某些软件包。

但是，Scrounger已为我们打包了大多数iOS二进制文件，并提供了一个在设备上安装它们的模块。具体请参阅[Scrounger
GitHub](https://github.com/nettitude/scrounger)页面。

如果不满足条件，某些模块将无法运行。

另外，设备需要越狱和root权限。

##  **使用**

Scrounger的使用主要有两种方式：命令行或交互式控制台。

命令行主要用于执行所有检查或自动化脚本。控制台用于运行一定数量的模块或执行特定操作，例如反编译，重新编译和签名应用程序，提取某些文件等。

##  **命令行选项**

使用命令行时，你可以列出可用模块及其参数，可用设备，执行完整分析（运行特定类型应用程序的所有模块 -Android或iOS）并运行特定模块，同时传递必要的参数。

![1.png](https://image.3001.net/images/20180901/1535793668_5b8a5a049f367.png!small)

以下是在Android应用程序上使用Scrounger命令行运行特定模块的示例。

首先，我们列出要运行模块的所需选项，然后运行。

![2.png](https://image.3001.net/images/20180901/1535793692_5b8a5a1c1819e.png!small)![3.png](https://image.3001.net/images/20180901/1535793694_5b8a5a1ea62e5.png!small)

##  **控制台示例**

控制台包含了几个强大的选项，提供自动完成（包括文件路径自动完成），模块搜索，能够重新使用来自其他模块的结果作为参数、命令使用历史以及反向搜索已使用的命令。

以下是控制台列出iOS可用模块的示例。

![4.png](https://image.3001.net/images/20180901/1535793709_5b8a5a2d7b028.png!small)

除了列出模块外，还将显示模块功能的简要说明。对于iOS和Android，有两种主要类型的模块，misc和analysis。misc模块是辅助模块，对应用程序，其文件/设备执行多个操作。为了评估是否存在任何的安全漏洞，analysis模块将分析应用程序文件，应用程序本身及其生成的文件。

![5.png](https://image.3001.net/images/20180901/1535793728_5b8a5a405e19d.png!small)

首先，我们运行options命令查看特定模块所需的参数（这和Metasploit是一样的）。options命令还会显示全局选项。如果设置了该参数并且有模块使用了相同参数，则它的值将被自动设置。设置好了所需参数，我们再次运行options命令确保已正确设置了所有选项，并使用run命令运行模块。

可以看到，Scrounger通过运行某些模块生成了一些输出和结果，这些结果也可以被其他模块所使用。

![6a.png](https://image.3001.net/images/20180901/1535793767_5b8a5a67c2f19.png!small)![6b.png](https://image.3001.net/images/20180901/1535793767_5b8a5a679f8d2.png!small)

我们可以使用show
results命令来查看执行其他模块返回的所有存储结果。print命令可用于显示存储在某个结果上的值，也可用于打印存储在全局或模块参数中的值。如果你想在其它模块中使用这些结果，可以通过result:关键字设置使用。设置完成后运行模块即可。

##  **设备示例**

有几个模块将需要与IOS或Android设备进行交互。在命令行或控制台中添加设备也非常的简单。

![7.png](https://image.3001.net/images/20180901/1535793797_5b8a5a85614eb.png!small)

在此示例中，我们将使用add_device命令将一个Android设备添加到控制台（它将尝试获取连接的设备并将其显示为可选项）。然后，使用set
global命令，我们将设备设置为device
1。使用misc/list_apps命令时，由于已设置全局选项并且存在具有相同名称的模块参数，因此它将自动填充该参数的值。

##  **可扩展性**

Scrounger的可扩展性，可以让你轻松的包含自定义模块，并根据渗透测试人员的偏好执行自定义的检查。安装Scrounger时，将会为你创建所有所需目录。在~/.scrounger/modules/custom下，已为你创建了一个自定义模块目录。

在以下示例中，创建了一个自定义模块并放置在了custom/analysis/ios/目录下。从路径就可以判断出，false_positive模块是一个针对iOS应用程序的模块。

![8.png](https://image.3001.net/images/20180901/1535793827_5b8a5aa3154f8.png!small)

##  **创建你自己的模块**

创建自定义模块非常的简单，只需三个步骤：根据模块要执行的操作在正确的模块目录下创建文件，创建两个变量meta和options，以及函数run。

示例：

    
    
    from scrounger.core.module import BaseModule
     
    class Module(BaseModule):
        meta = {
            "author": "RDC",
            "description": """Just a Test Analysis module""",
            "certainty": 100
        }
     
        options = [
            {
                "name": "output",
                "description": "local output directory",
                "required": False,
                "default": None
            },
        ]
     
        def run(self):
     
            print("This is a print from the custom module")
     
            return {
                "print": "This will be print by scrounger's console.",
                "false_positive_result": {"title": "This is a False Positive  - just a test",
                "details": "No details",
                "severity": "Low",
                "report": True}
            }
     

下次启动scrounger-console时，新创建的文件将会自动添加到可用模块列表中。在创建模块时，还需要考虑许多其它的元素，尤其是analysis模块。更多信息请参阅Scrounger提供的有关所有可用模块的全面文档，以及如何创建自定义模块的详细说明：<https://github.com/nettitude/scrounger/docs>

##  **真实场景案例**

在典型的移动应用程序评估中，我们将尝试运行尽可能多的模块。Scrounger也考虑到了这一点，在控制台中我们可以通过一个名为full_analysis的模块来运行所有模块，在命令行中则添加-f选项即可。

此选项/模块将反编译应用程序，并运行所有必要的辅助模块以及其他可用模块。然后创建一个JSON文件，其中包含返回report=True的各个模块的结果和详细信息。命令行可执行文件还有一个-p选项，用于读取JSON文件并将所有结果和详细信息打印到控制台。

![10a.png](https://image.3001.net/images/20180901/1535793875_5b8a5ad397255.png!small)

![10b.png](https://image.3001.net/images/20180901/1535793907_5b8a5af309cdf.png!small)![10c.png](https://image.3001.net/images/20180901/1535793907_5b8a5af31b8d6.png!small)

##  **后续开发、反馈和特别感谢**

后续Scrounger将添加支持更多的功能。具体可以参见[GitHub
README](https://github.com/nettitude/scrounger)的末尾部分。如果你有任何的反馈想法或建议，那么欢迎你随时在GitHub上提交。最后，特别感谢工具的所有开发人员！

> Needle (<https://github.com/mwrlabs/needle>)
>
> Drozer (<https://github.com/mwrlabs/drozer>)
>
> iOS-application-analyser (<https://github.com/timb-machine/ios-application-> analyser>)

***参考来源：[nettitude](https://labs.nettitude.com/blog/introducing-scrounger-ios-and-android-mobile-application-penetration-testing-framework/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

