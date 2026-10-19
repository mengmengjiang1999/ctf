**作者: Badcode and Longofo@知道创宇404实验室**  
**时间: 2020年2月9日**  
**English Version：<https://paper.seebug.org/1261/>**

### 前言

2019年9月初我们应急了Nexus Repository Manager 2.x 命令注入漏洞(CVE-2019-5475)，其大致的原因和复现步骤在
[hackerone](https://hackerone.com/reports/654888)
上公布了，在应急完这个漏洞之后，我们分析该漏洞的修复补丁，发现修复不完全，仍然可以绕过，本篇文章记录该漏洞的两次绕过。虽然早发布了两次的修复版本，由于官方第二次更新公告太慢<https://support.sonatype.com/hc/en-us/articles/360033490774>，所以现在才发。

几次更新时间线：

  * CVE-2019-5475（2019-08-09）
  * 第一次绕过，CVE-2019-15588（2019-10-28）
  * 第二次绕过，未分配CVE，更新了公告影响版本（2020-3-25）

**注：** 原始漏洞分析、第一次绕过分析、第二次绕过分析部分主要由Badcode师傅编写，第二次绕过分析+、最新版本分析主要由Longofo添加。

### 原始漏洞分析

#### 利用条件

  * 需管理员权限(默认认证：admin/admin123)

#### 漏洞分析

以下分析的代码基于 2.14.9-01 版本。

漏洞点是出现在 Yum Repository 插件中，当配置 Yum 的 `createrepo`或者`mergerepo`时

![](https://images.seebug.org/content/images/2020/06/ec3a2fe9-1b43-4e54-8f64-1e37d669db6f.png-w331s)

代码层面会跳到
`YumCapability`的[`activationCondition`](https://github.com/sonatype/nexus-public/blob/release-2.14.9-01/plugins/yum/nexus-yum-repository-plugin/src/main/java/org/sonatype/nexus/yum/internal/capabilities/YumCapability.java#L82)方法中。

![](https://images.seebug.org/content/images/2020/06/1030544c-4396-4de5-bfa1-aa652aeb3a76.png-w331s)

在上面`Path of
"createrepo"`中设置的值会通过`getConfig().getCreaterepoPath()`获取到，获取到该值之后，调用`this.validate()`方法

![](https://images.seebug.org/content/images/2020/06/e52feca6-0594-4737-99c6-30d55da4d561.png-w331s)

传进来的`path`是用户可控的，之后将`path`拼接`--version`之后传递给`commandLineExecutor.exec()`方法，看起来像是执行命令的方法，而事实也是如此。跟进`CommandLineExecutor`类的`exec`方法

![](https://images.seebug.org/content/images/2020/06/a6eb449d-f71f-4b8a-bed8-82d92059f315.png-w331s)

在执行命令前先对命令解析，`CommandLine.parse()`，会以空格作为分隔，获取可执行文件及参数。

最终是调用了`Runtime.getRuntime().exec()`执行了命令。

例如，用户传入的 command 是`cmd.exe /c
whoami`，最后到`getRuntime().exec()`方法就是`Runtime.getRuntime().exec({"cmd.exe","/c","whoami"})`。

所以漏洞的原理也很简单，就是在`createrepo`或者`mergerepo`路径设置的时候，该路径可以由用户指定，中途拼接了`--version`字符串，最终到了`getRuntime.exec()`执行了命令。

#### 漏洞复现

在`Path of "createrepo"`里面传入 payload。

![](https://images.seebug.org/content/images/2020/06/ec66a8b4-e8c6-4dac-a434-5d206c4b6931.png-w331s)

在`Status`栏可以看到执行的结果

![](https://images.seebug.org/content/images/2020/06/a0566733-08f6-4814-bde9-7cad8313ebed.png-w331s)

### 第一次绕过分析

#### 第一次补丁分析

官方补丁改了几个地方，关键点在[这里](https://github.com/sonatype/nexus-public/commit/e8769e53f6bb601126ef5d21f9ea009873b65e25#diff-4ab0523de106ac7a38808f0231fc8a23R81)

![](https://images.seebug.org/content/images/2020/06/3e3bdd09-72de-4927-b58a-70707154b68a.png-w331s)

常规做法，在执行命令前对命令进行过滤。新增加了一个`getCleanCommand()`方法，对命令进行过滤。

![](https://images.seebug.org/content/images/2020/06/ea8f5854-8188-4ad9-a68c-f4856efbb7f5.png-w331s)

`allowedExecutables`是一个
HashSet，里面只有两个值，`createrepo`和`mergerepo`。先判断用户传入的`command`是否在`allowedExecutables`里面，如果在，直接拼接`params`即`--version`直接返回。接着对用户传入的`command`进行路径判断，如果是以nexus的工作目录(`applicationDirectories.getWorkDirectory().getAbsolutePath()`)开头的，直接返回
null。继续判断，如果文件名不在`allowedExecutables`则返回 null，也就是这条命令需要
以`/createrepo`或者`/mergerepo`结尾。都通过判断之后，文件的绝对路径拼接`--version` 返回。

#### 第一次补丁绕过

说实话，看到这个补丁的第一眼，我就觉得大概率可以绕。

传入的命令满足两个条件即可，不以nexus的工作目录开头，并且以`/createrepo`或者`/mergerepo`结尾即可。

看到补丁中的`getCleanCommand()`方法，`new File(command)`是关键，`new
File()`是通过将给定的路径名字符串转换为抽象路径名来创建新的File实例。 值得注意的是，这里面路径字符串是可以使用空格的，也就是

    
    
    String f = "/etc/passwd /shadow";
    File file = new File(f);

这种是合法的，并且调用`file.getName()`取到的值是`shadow`。结合这个特性，就可以绕过补丁里面的判断。

    
    
    String cmd = "/bin/bash -c whoami /createrepo";
    File file = new File(cmd);
    System.out.println(file.getName());
    System.out.println(file.getAbsolutePath());

运行结果

![](https://images.seebug.org/content/images/2020/06/12d3d014-379f-4384-9281-96510593904b.png-w331s)

可以看到，`file.getName()`的值正是`createrepo`，满足判断。

#### 第一次绕过测试

##### 测试环境

  * 2.14.14-01 版本
  * Linux

##### 测试步骤

在`Path of "createrepo"`里面传入 payload。

![](https://images.seebug.org/content/images/2020/06/6ea84feb-8570-40b2-b2a9-c01d81c8ddb2.png-w331s)

在`Status`栏查看执行的结果

![](https://images.seebug.org/content/images/2020/06/0b74b390-ec5f-4c62-96bf-c20974d0b67c.png-w331s)

可以看到，成功绕过了补丁。

在 Windows 环境下面就麻烦点了，没有办法使用`cmd.exe /c whoami`这种形式执行命令了，因为`cmd.exe /c
whoami`经过`new File()` 之后变成了`cmd.exe \c
whoami`，后面是执行不了的。可以直接执行exe，注意后面是还会拼接`--version`的，所以很多命令是执行不了的，但是还是有办法利用能执行任意exe这点来做后续的攻击的。

### 第二次绕过分析

#### 第二次补丁分析

在我提交上述绕过方式后，官方修复了这种绕过方式，看下官方的[补丁](https://github.com/sonatype/nexus-public/commit/3dd1d59393149833150b702ddf6485b5ef3312bd#diff-4ab0523de106ac7a38808f0231fc8a23R111)

![](https://images.seebug.org/content/images/2020/06/1e6e5b47-a471-42da-9d3c-c2efda95f521.png-w331s)

在`getCleanCommand()` 方法中增加了一个`file.exists()`判断文件是否存在。之前的`/bin/bash -c whoami
/createrepo`这种形式的肯定就不行了，因为这个文件并不存在。所以现在又多了一个判断，难度又加大了。难道就没有办法绕过了？不是的，还是可以绕过的。

#### 第二次补丁绕过

现在传入的命令要满足三个条件了

  * 不以nexus的工作目录开头
  * 以`/createrepo`或者`/mergerepo`结尾
  * 并且这`createrepo`或者`mergerepo`这个文件存在

看到`file.exists()`我就想起了 php 中的 `file_exists()`，以前搞 php 的时候也遇到过这种判断。有个系统特性，在
Windows 环境下，目录跳转是允许跳转不存在的目录的，而在Linux下面是不能跳转不存在目录的。

测试一下

Linux

![](https://images.seebug.org/content/images/2020/06/958aa7a3-b601-4cf6-a9ae-10168307a695.png-w331s)

可以看到，`file.exists()`返回了 false

Windows

![](https://images.seebug.org/content/images/2020/06/899f3eaa-e499-4147-bea6-fbe22bef5325.png-w331s)

`file.exists()`返回了 true

上面我们说了`new File(pathname)`，pathname 是允许带空格的。在利用上面WIndows环境下的特性，把cmd设置成
`C:\\Windows\\System32\\calc.exe \\..\\..\\win.ini`

![](https://images.seebug.org/content/images/2020/06/e310528b-93c5-40fc-b181-a2b71a5ba27c.png-w331s)

经过`parse()`
方法，最终到`getRuntime.exec({"C:\\Windows\\System32\\calc.exe","\\..\\..\\win.ini"})`，这样就能执行`calc`了。

在上面这个测试`win.ini`是确实存在的文件，回到补丁上面，需要判断`createrepo`或者`mergerepo`存在。首先从功能上来说，createrepo
命令用于创建 yum
源（软件仓库），即为存放于本地特定位置的众多rpm包建立索引，描述各包所需依赖信息，并形成元数据。也就是这个`createrepo`在Windows下不太可能存在。如果这个不存在的话是没有办法经过判断的。既然服务器内不存在`createrepo`，那就想办法创建一个，我首先试的是找个上传点，尝试上传一个`createrepo`，但是没找到上传之后名字还能保持不变的点。在`Artifacts
Upload`处上传之后，都变成`Artifact-Version.Packaging`这种形式的名字了，`Artifact-Version.Packaging`这个是不满足第二个判断的，得以`createrepo`结尾。

一开始看到`file.exists()`就走进了思维定势，以为是判断文件存在的，但是看了官方的文档，发现是判断文件或者目录存在的。。这点也就是这个漏洞形成的第二个关键点，我不能创建文件，但是可以创建文件夹啊。在`Artifacts
Upload`上传Artifacts 的时候，可以通过`GAV Parameters`来定义。

![](https://images.seebug.org/content/images/2020/06/a8c6b81a-e151-4e6c-a26f-559188a66a81.png-w331s)

当
`Group`设置为`test123`，`Artifact`设置为`test123`，`Version`设置成`1`，当上传`Artifacts`的时候，是会在服务器中创建对应的目录的。对应的结构如下

![](https://images.seebug.org/content/images/2020/06/db406e76-8e1e-4041-9f64-f5459ad6d839.png-w331s)

如果我们将`Group`设置为`createrepo`，那么就会创建对应的`createrepo`目录。

结合两个特性来测试一下

    
    
    String cmd = "C:\\Windows\\System32\\calc.exe \\..\\..\\..\\nexus\\sonatype-work\\nexus\\storage\\thirdparty\\createrepo";
    File file = new File(cmd);
    System.out.println(file.exists());
    System.out.println(file.getName());
    System.out.println(file.getAbsolutePath());

![](https://images.seebug.org/content/images/2020/06/0ee33784-61d3-47d4-931d-aa44e0c0dbf4.png-w331s)

可以看到，`file.exists()`返回了true，`file.getName()`返回了`createrepo`，都符合判断了。

最后到`getRuntime()`里面大概就是`getRuntime.exec({"C:\Windows\System32\notepad.exe","\..\..\..\nexus\sonatype-work\nexus\storage\thirdparty\createrepo","--version"})`

是可以成功执行`notepad.exe`的。(calc.exe演示看不到进程哈，所以换成Notepad.exe)

#### 第二次绕过测试

##### 测试环境

  * 2.14.15-01 版本
  * Windows

##### 测试步骤

在`Path of "createrepo"`里面传入 payload。

![](https://images.seebug.org/content/images/2020/06/4c781786-2037-47b1-b396-3a2d9ac186e6.png-w331s)

查看进程，`notepad.exe`启动了

![](https://images.seebug.org/content/images/2020/06/82054ec7-be8b-43b2-a147-2d2c40d037b4.png-w331s)

可以看到，成功绕过了补丁。

### 第二次绕过分析+

经过Badcode师傅第二次绕过分析，可以看到能成功在Windows系统执行命令了。但是有一个很大的限制：

  1. nexus需要安装在系统盘
  2. 一些带参数的命令无法使用

在上面说到的`Artifacts
Upload`上传处是可以上传任意文件的，并且上传后的文件名都是通过自定义的参数拼接得到，所以都能猜到。那么可以上传自己编写的任意exe文件了。

#### 第二次绕过分析+测试

##### 测试环境

  * 2.14.15-01 版本
  * Windows

##### 测试步骤

导航到`Views/Repositories->Repositories->3rd
party->Configuration`，我们可以看到`默认本地存储位置`的绝对路径（之后上传的内容也在这个目录下）：

![](https://images.seebug.org/content/images/2020/06/4bb1c625-1a51-4478-a153-e5992761f3d2.png-w331s)

导航到`Views/Repositories->Repositories->3rd party->Artifact
Upload`，我们可以上传恶意的exe文件：

![](https://images.seebug.org/content/images/2020/06/f8d16b11-b9b7-45e7-8912-f3ddb5d7c163.png-w331s)

该exe文件将被重命名为`createrepo-1.exe`（自定义的参数拼接的）：

![](https://images.seebug.org/content/images/2020/06/ebe9bc54-1ec9-4c12-abaf-9b0818c602a3.png-w331s)

同样在`Path of "createrepo"`里面传入
payload（这时需要注意前面部分这时是以nexus安装目录开头的，这在补丁中会判断，所以这里可以在最顶层加`..\`或者弄个虚假层`aaa\..\`等）：

![](https://images.seebug.org/content/images/2020/06/f0b71406-a1e8-45bf-a21b-88b552f601cc.png-w331s)

可以看到createrepo-1.exe已经执行了：

![](https://images.seebug.org/content/images/2020/06/3d4fc910-624a-47f8-8f64-e2a164cd54e2.png-w331s)

### 最新版本分析

#### 最新版本补丁分析

第二次补丁绕过之后，官方又进行了修复，官方补丁主要如下：

![](https://images.seebug.org/content/images/2020/06/0704948d-a72f-4774-a5cf-8c24bcf9cf35.png-w331s)

![](https://images.seebug.org/content/images/2020/06/4bce687e-e49d-4c7b-af3b-2e4fe32d2aee.png-w331s)

删除了之前的修复方式，增加了`YumCapabilityUpdateValidator`类，在`validate`中将获取的值与properties中设置的值使用`equals`进行绝对相等验证。这个值要修改只能通过`sonatype-work/nexus/conf/capabilities.xml`：

![](https://images.seebug.org/content/images/2020/06/b98ce3d1-7e07-46b3-846d-bf5fd653b601.png-w331s)

#### 最新版本验证

前端直接禁止修改了，通过抓包修改测试：

![](https://images.seebug.org/content/images/2020/06/c67799e7-88bc-4a40-981e-babfbdc5008d.png-w331s)

在`YumCapabilityUpdateValidator.validate`断到：

![](https://images.seebug.org/content/images/2020/06/d723f3e9-0175-4b7d-a864-f756910adf33.png-w331s)

可以看到这种修复方式无法再绕过了，除非有文件覆盖的地方覆盖配置文件，例如解压覆盖那种方式，不过没找到。

不过`Artifacts Upload`那里可以上传任意文件的地方依然还在，如果其他地方再出现上面的情况依然可以利用到。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1260/>

