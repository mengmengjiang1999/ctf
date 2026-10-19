***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **近期，我们发现了一个Java Usage
Tracker中的设计缺陷，可导致攻击者创建任意文件，注入指定参数，并实现本地权限提升。反之，该漏洞可以用于权限提升，从而使攻击者可以访问受漏洞影响系统中的资源，这些资源通常受到保护，或仅限于特定应用程序或用户才有权访问。**

我们通过Zero Day
Initiative，与Oracle合作修复了这一漏洞，该漏洞已经在Oracle的2018年10月更新中实现修复。因此，需要敦促个人用户及企业尽快更新他们的Java版本。

在本文中，我们将深入研究这一漏洞在Windows上的出现原因、Java Usage Tracker的工作原理以及实现漏洞利用所必要的条件。

Oracle安全更新公告：<https://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html>。

## Java Usage Tracker

在Java中，有一个名为JavaUsage Tracker的功能，用于跟踪系统中Java的使用方式。Java Usage Tracker具有以下功能：

> 1、通过启动配置参数，记录有关Java虚拟机（JVM）的日志信息。
>
> 2、将数据转储到日志文件中，或将其重定向到UDP服务器。
>
> 3、允许Usage Tracker配置中指定自定义属性的日志值。

Java Usage
Tracker的配置文件名称为usagetracker.properties。该文件位于全局默认位置，这一位置根据操作系统的不同而有所不同。例如，Windows的默认路径是%ProgramData%\Oracle\Java\。全局默认路径中的usagetracker文件将跟踪系统中所有启动的JVM的使用情况。

下图展示了一个usagetracker.properties的样例：

![usagetracker.properties的样例](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-1.png)

在上图的第9行中，我们可以看到，JavaUsage Tracker会将日志信息记录到文件global_javatracker.log中。以安装Apache
Tomcat（基于Java的开源工具）的系统为例，重新启动服务后，将创建文件global_javatracker.log，并在其中写入Java使用情况跟踪数据。每次，在Tomcat服务启动时，都会向该日志文件中写入新的跟踪信息。

下图是跟踪数据的示例，请注意这里是如何使用逗号分隔两个不同值的，是在属性文件（分隔符配置）中定义。

![属性文件（分隔符配置）中定义](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-2.png)

## 用户控制的参数

在文件usagetracker.properties中，有两个属性控制Java Usage Tracker的行为，分别是：  

    
    
    oracle.usagetracker.logToFile  
    oracle.usagetracker.additionalProperties

logTofile属性允许用户选择系统中的任意路径来保存日志文件。需要注意的是，日志文件是由被监控的JVM创建的。如果JVM以提升后的权限运行，那么JVM就能够在系统的任何地方创建该文件，文件的扩展名也不受控制（也就是说，可以创建名为global_javatracker.bat的日志文件）。

尽管logToFile路径可以任意设置，但无法控制文件内容。因为JVM只会从现有的数据（无法修改）中写入值。然而，Java Usage
Tracker具有从自定义属性获取值的特殊功能。 additionalProperties可以包含要跟踪的任意和其他自定义属性，如下所示。

如何通过additionalProperties添加自定义属性：

![通过additionalProperties添加自定义属性](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-3.png)

重新启动Tomcat服务后，如何跟踪数据的代码段：

![跟踪数据的代码段](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-4.png)

如上图所示，该行的末尾附加了一个带有null值的已配置跟踪属性com.anotherInterestingProperty=
null。其值为null，表明该属性不存在。有两种方法可以控制Java Usage
Tracker的行为：设置任意日志路径，或者设置任意自定义属性。目前，这个功能似乎是不能被利用的，但是如果结合了其他安全漏洞，就能够被攻击者利用。

## 借助自定义属性实现漏洞利用

下面，我们详细说明如何借助自定义属性实现漏洞利用。先前配置文件中的第9行会使得Java Usage
Tracker强制创建.bat文件，然后添加自定义属性ping 172.0.1.1
>。其生成了文件global_javatracker.bat，如下图所示。

global_javatracker.bat中自定义属性：

![global_javatracker.bat中自定义属性](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-5.png)  

global_javatracker.bat正在被执行：

![global_javatracker.bat正在被执行](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-6.png)

在这里，需要注意附加属性ping 172.0.1.1 >=
null。当我们执行批处理文件global_javatracker.bat时，会显示错误消息“VM start”无法识别。发生此错误的原因在于，Java
Usage Tracker的属性文件仅生成一行，并且其分隔符是根据配置中的com.oracle.usagetracker.separator=,
来决定的，使用了逗号作为分隔符。

那么，如果将分隔符更改为“new line”（新的一行），将会生成完全不同的跟踪日志。

带有“new line”分隔符的JavaUsage Tracker：

![带有“new line”分隔符的JavaUsage Tracker](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-7.png)  

使用“new line”分隔符后，生成的跟踪日志：![生成的跟踪日志](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-8.png)

上图中的最后一行，包含ping 172.0.1.1 >=
null。如果运行global_javatracker.bat，那么就会导致执行ping172.0.1.1> =
null命令。但是，由于带有双引号，所以该命令无法识别。但是，我们还有机会执行该命令，因为每个属性值的双引号，可以通过修改另一个配置com.oracle.usagetracker.quote
=”来实现替换。

举例来说，我们创建一个内容为空的com.oracle.usagetracker.quote配置，如下图所示。

内容为空的com.oracle.usagetracker.quote：

![内容为空的com.oracle.usagetracker.quote](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-9.png)  

使用空配置从com.oracle.usagetracker.quote生成的跟踪日志：

![生成的跟踪日志](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-10.png)

运行global_javatracker.bat，将会执行命令ping 172.0.1.1> =
null。如上图中命令提示符最后的提示所示，创建了一个“null”文件。

至此，我们可以利用Java Usage Tracker实现以下操作：

> 1、 在文件系统的任意位置创建文件。
>
> 2、创建脚本文件，尽管我们在示例中创建了批处理文件，但实际上也可用于创建其他类型的文件。
>
> 3、注入任意命令（或与脚本文件相关的任何其他文本）。

攻击者可以在系统的任意位置执行或创建上述内容，或可编写脚本的文件。但是，如果攻击者想要成功利用这个漏洞做一些事情，还需要两个条件：

> 1、需要在关键位置（比如：自动启动脚本）中创建恶意文件。
>
> 2、需要有权访问关键位置，应该由高权限的进程创建恶意文件。

实际上，这两个条件都可以实现。举例来说，可以为非特权用户创建Java
UsageTracker配置（usagetracker.properties），具有更高特权的进程负责创建恶意日志文件（Usage Tracker日志）。

## 创建Java Usage Tracker日志文件

如果保存到全局配置路径中（例如Windows的%ProgramData%\Oracle\Java），在系统启动JVM时，就会读取Java Usage
Tracker日志文件。接下来，我们再以默认Tomcat安装为例。在安装Tomcat，并使用全局usagetracker.properties之后，跟踪日志会在Tomcat重新启动后创建（如下图所示）。实际上，该文件是由Tomcat服务创建的，默认情况下会由System运行。

目前，Tomcat服务已经由System运行，因此就可以在任意位置创建恶意文件global_javatracker.bat。但是，配置文件usagetracker.properties还必须由非特权用户创建。

安装Tomcat后，创建的跟踪日志：

![安装Tomcat后](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-11.png)

Tomcat创建的日志文件：

![Tomcat创建的日志文件](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-12.png)

## 本地权限提升

Java Usage
Tracker的全局配置文件，都创建在默认路径%ProgramData%\Oracle\Java\中。此路径中的内容，一部分是在Java安装期间创建的，也有一部分是在执行Java命令时创建的（例如java
–c）。

默认情况下，%ProgramData%路径只允许系统的“Users”创建文件。当Oracle或Java路径被建立时，也会继承上级路径的默认权限。下图是%ProgramData%\Oracle\Java\权限的截图：

![%ProgramData%\\Oracle\\Java\\权限](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/10/CVE-2018-3211-13.png)

我们举例来进一步说明这个漏洞。具有低权限的用户，可以创建恶意配置文件usagetracker.properties。由于Tomcat服务以“System”的权限运行，因此它可以在系统的任何位置创建批处理文件。在批处理文件中，可以包括将脚本写入到启动项位置之类的例程。

## 总结

目前，攻击者可以通过多种方式，滥用Java Usage
Tracker的功能来实现权限提升。我们的研究仅在Windows环境中进行了测试，但其他操作系统也可能受到该漏洞的影响。

攻击者为实现权限提升，可能会组合利用一些漏洞，这些漏洞包括：

1、任意文件类型创建：该漏洞可以通过oracle.usagetracker.logToFile路径实现。例如，可以创建一些类似于批处理文件的脚本。

2、参数注入：通过oracle.usagetracker.additionalProperties配置来实现。

3、本地权限提升：通过%ProgramData%/Oracle/Java中的弱权限来实现。

## 参考链接

> <https://blog.trendmicro.com/trendlabs-security-> intelligence/cve-2018-3211-java-usage-tracker-local-elevation-of-privilege-> on-windows/>

***本文作者：eridanus96，转载请注明来自FreeBuf.COM**  

