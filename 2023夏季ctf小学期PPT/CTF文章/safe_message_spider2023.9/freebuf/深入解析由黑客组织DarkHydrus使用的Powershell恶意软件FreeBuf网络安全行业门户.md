**你可能还会记得我之前写过一篇关于MuddyWaterAPT组织使用他们定制的Powershell恶意软件攻击中东组织的博文（好吧，如果你还没有看过，你可以点击[这里](https://0ffset.wordpress.com/2018/05/28/0x06-analyzing-a-muddywater-sample/)进行查看）。在这篇博文中，我分析了恶意的VBA宏和高度混淆的PowerShell代码。你猜怎么着，现在又有另一个组织使用定制的Powershell恶意软件攻击了中东组织，尽管这次在感染方式上有所不同。这个组织被PaloAlto
Networks公司旗下威胁研究团队Unit
42的研究人员命名为DarkHydrus。恶意软件样本由Rony（[@r0ny_123](https://twitter.com/r0ny_123)）上传到VirusBay，下面让我们来对其进行分析。**

## MD5：

.iqy: 377cfd5b9aad2473d1659a5dbad01d90

Downloader: bd764192e951b5afd56870d2084bccfd

Final Stage: 953a753dd4944c9a2b9876b090bf7c00

从Unit
42的博文我们得知，DarkHydrus利用包含受密码保护的RAR文件的鱼叉式钓鱼电子邮件来感染他们的目标。这个RAR文件包含一个含有URL的.iqy文件（Internet查询文件）。由于IQY文件在默认情况下是由Excel打开的，因此在执行这个IQY文件时，Excel会通过包含在.IQY中的URL来检索内容（检索操作在弹出一组警告窗口之后进行）。下面让我们来具体看看这个IQY文件：

![iqy-e1533219369153.png](https://image.3001.net/images/20180806/1533545261_5b680b2d87e39.png!small)

当IQY文件执行时，Excel会从URL指向的Web服务器上获取包含在一个名为releasenotes.txt的文件中的内容。下面让我们来执行一下这个IQY文件，看看会发生些什么。

![popup-e1533219413660.png](https://image.3001.net/images/20180806/1533545296_5b680b504d9c0.png!small)

正如你所看到的那样，在文件执行时，我们收到了来自MicrosoftExcel的警告，指出运行IQY文件存在安全隐患。为了继续运行该文件，我们需要单击“Enable”。那么，在单击“Enable”之后会发生什么呢？

![execution-e1533219462512.gif](https://image.3001.net/images/20180806/1533545323_5b680b6bbd979.gif!small)

我们会看到另一个警告弹窗，指出执行cmd.exe同样存在安全隐患。在单击“Yes”之后，
cmd.exe就会被创建，它会生成一个Powershell.exe进程。但这个进程并不会立即执行，相反，它会立即退出。我怀疑这可能是一种反分析方法，让我们来看看releasenotes.txt的内容：

![stage_1-e1533219522348.png](https://image.3001.net/images/20180806/1533545358_5b680b8e20c1e.png!small)

看得出来，一个Powershelll命令被存储在单元格A0中，由Excel执行。在这个命令执行之后，会从micrrosoft/winupdate.ps1下载一个字符串，并使用IEX执行。因此，这个Powershell命令应该是第二阶段的真实有效载荷（payload）。

![winupdate-e1533321752760.png](https://image.3001.net/images/20180806/1533545383_5b680ba7b85f8.png!small)

让我们来看一下 winupdate.ps1，很明显其中的数据是经过压缩和base64编码的，所用的方法与[Emotet
downloader](https://0ffset.wordpress.com/2018/06/13/post-0x10-another-emotet-downloader/)相同。

![simple_script-e1533219572578.png](https://image.3001.net/images/20180806/1533545405_5b680bbd47b1d.png!small)

由于它们使用的是相同的Powershell混淆技术，因此我们可以使用下图中的python脚本来对有效载荷（payload）进行解编码和解压缩。

之后，我注意到了一些关键字，如VBox、VirtualBox、Qemu等，因此我前面提到的“怀疑这可能是一种反分析方法”的想法是正确的。DNS通信基于以下queryTypes变量：

"A", "AAAA", "AC","CNAME", "MX", "TXT", "SRV","SOA";

在分析C2协议前，我想弄清楚恶意软件所使用的反分析方法。幸运的是，它们被保存在Sandbox()函数中：

![anti_vm-e1533321850386.png](https://image.3001.net/images/20180806/1533545508_5b680c248f95c.png!small)

## 反分析方法

有多种反分析方法被嵌入在这个恶意软件中：该样本首先会使用WMI来找出SMBIOSBIOSVersion，如果与VBOX、bochs、qemu、VirtualBox、VM任何一个关键字匹配，恶意软件则会打印VirtualMachine
Founded，然后结束运行。如果与上面的关键字不匹配，则检查Manufacturer是否与XEN匹配。如果匹配，打印VirtualMachine
Founded，然后结束运行。接下来，查询总的物理内存，如果小于硬编码的内存大小限制（2900000000），就退出运行。如果所有检查都通过，并且匹配，恶意软件则会继续检查处理器内核数，以确保数量大于1。因为在虚拟机内分析时，一般分配的处理器数默认值就是1。此外，沙箱一般也只用一个处理器。最后，如果你的计算机没有显示出任何作为虚拟机或沙箱的迹象，那么恶意软件则检查在正在运行的进程中是否存在于Wireshark和Sysinternals相关的进程。如果存在，则退出运行。所以，你可能想知道如何绕过这些检查？其实非常容易。

正如你所看到的那样，当我们使用Powershell检索Win32_Bios信息时，里面有两个明显与虚拟机相关的信息：首先是SMBIOSBIOSVersion，其次是Version。由于恶意软件会检查SMBIOSBIOSVersion信息，因此我们需要对它进行更改。为此，我们可以使用托管对象格式（MOF）文件，并使用mofcomp.exe对其进行解析，这将允许我们更改的Win32_Bios中的值。这样，当恶意软件检索SMBIOSBIOSVersion信息时，就不会匹配为虚拟机了。

复制上图中的信息并保存为MOF文件，然后保存到方便你访问的位置，例如桌面。为了更改这些信息，你需要admin管理员权限，以管理员权限运行powershell。在运行mofcomp.exe之后，你应该就可以看到与上图类似的输出了，如下图所示。

虽然这会导致其他额外的信息被添加进来，但manufacturer的确被更改为了Sony，并且SMBIOSBIOSVersion也被更改为了Legit_PC。MOF文件中Version并没有被改变，但它看起来像是一个GUID，而不是VBOX。

![not_found-e1533322037996.png](https://image.3001.net/images/20180806/1533545890_5b680da27430b.png!small)

当我们执行在Sandbox函数中运行相同的Powershell命令时，你就可以看到不匹配任何虚拟机信息（否则将显示字符串 VirtualMachine
Founded）。

    
    
    $result = Get-WmiObject -Query "Select TotalPhysicalMemoryfrom Win32_ComputerSystem" | Out-String
    
    $result = [regex]::Match($result,"TotalPhysicalMemory :(\d+)")
    
    $memory = $result.Groups[1].Value
    
    if ([int64]$memory -lt [int64]$memorySizeLimit) {
    
        exit
    
    }

为了绕过这种反分析方法，你需要为你的虚拟机分配更多的RAM，确保大小超过2.9GB。此外，你需要为你的虚拟机分配两个以上的处理器内核，因为如果只有一个的话，恶意软件会退出。最后，确保在恶意软件执行期间，不要运行Wireshark或Sysinternals，否则它同样也会退出。

![query1-e1533322086668.png](https://image.3001.net/images/20180806/1533545930_5b680dca3ec27.png!small)

## 通信方法

现在，我们已经解读了反分析方法，是时候分析通信方法了。看起来，函数
query()似乎负责与C2服务器通信。此外，由于nslookup.exe与列表中的URL一起使用，因此很明显攻击者使用的是DNS来进行通信。为了弄清楚query()函数所需参数的含义，我查看了函数test()中的query()调用过程：

    
    
    foreach ($t in $Global:queryTypes) {
    
        if ($Global:id.Length-ge 1) {
    
            $response = query-query $Global:id -type $t -test $true -change_mode $false
    
        }
    
        else {
    
            $response = query-query $PID -type $t -test $true -change_mode $false
    
        }

这个代码在for循环中，一共运行了8次，这是基于queryTypes变量（A，AAAA，AC...）中保存的查询类型数决定的。$t代表当前查询的类型。if语句用来检查变量ID的长度是否大于等于1。如果大于等于1，就将ID作为第一个参数传递给函数。否则，程序会传递当前PID作为第一个参数。第二个参数$t代表当前查询的类型。如果函数在第一个循环中就被调用，$t就等于“A”，如果是第二个循环，$t就等于“AAAA”，以此类推。第三个参数query()代表执行函数以测试连接。最后，change_mode用于代表是否应使用roundRobin
函数更改DNS查询通信方法。在查看这个函数之前，让我们来看看query()的其余部分。

首先，变量
$Parameters是根据通信方法、域、使用的服务器以及ID或PID来填充的。其次，iex用于调用nslookup.exe，将变量$parameters作为参数传递。之后，程序会检查命令运行的输出以检查连接是否成功。为此，它会在输出中检查canonicalname、mx、nameserver、mailserver、address。如果匹配，变量$check会被设置为true，否则设置为false或函数返回cancel值。如果一切正常，函数会返回nslookup的输出，如果失败，则返回false。

![test-e1533322165754.png](https://image.3001.net/images/20180806/1533546095_5b680e6fb1388.png!small)

如果连接成功且返回的值也不等于false，并且ID的长度小于1，恶意软件则会将查询类型保存在$t中作为默认通信查询方法。然后，恶意软件会尝试生成一个ID，保存在全局变量ID中。如果第一个查询类型失败，恶意软件则会一直循环，直到尝试完最后一个方法。如果ID长度仍然小于1，程序将休眠变量$waiting传递的时间长度（最初为120），然后重新调用test()，第二次休眠的时间为$waiting中的值乘以2。在开始时，test函数会检查$waiting的值是否大于7200。如果是，程序则会因为无法连接C2服务器而退出。这也意味着，test()函数在退出前会运行6个循环。在我们知道了test函数决定使用哪种查询类型之后，让我们来看看roundRobin函数：

![domain_chooser-e1533322219576.png](https://image.3001.net/images/20180806/1533546147_5b680ea3dc92d.png!small)

恶意软件之所以被命名为RogueRobin，似乎就是因为这个roundRobin函数。在query()函数调用中，RoundRobin会被调用。其中，域列表是第一个参数，当前域在程序执行时位于位置0。使用这些参数，当$current在$list中时，RoundRobin可以得到$index。当$index大于等于列表的大小时，$index会被设为0。最后，RoundRobin会返回$list[$index]，变量保存在Global:domain中。此函数主要用于遍历硬编码的域，但如果变量$change_mode是true，它也用于遍历DNS查询模式：

    
    
    if ($change_mode) {
    
       $Global:mode = roundRobin -list $Global:queryTypes -current $Global:mode
    
    }

![startup1-e1533322270708.png](https://image.3001.net/images/20180806/1533546251_5b680f0ba4bc3.png!small)

## 持久性机制

接下来，让我们回到了对该恶意软件持久性机制的分析。首先，程序会检查全局变量 hasstartup
是否等于1，如果是，则启动startup方法。否则，程序将按正常程序继续执行。请注意写入变量$command中的数据，这实质上就是恶意软件有效载荷（payload）。我已经删除了经编码和压缩的数据，使它更容易阅读，但它与原始的有效载荷（payload）完全一致——唯一的区别是已删除的持久性机制，删除的目的是为了预防同时有多个恶意软件实例运行。一旦数据写入$command，就会创建一个文件
%APPDATA%\OneDrive.bat。写入的值为：

    
    
    powershell.exe -WindowStyle Hidden -execbypass -File "%APPDATA%\OneDrive.ps1"

在这一行代码写入.bat文件之后，恶意软件会把数据写入$command中，并传递给%APPDATA%\OneDrive.ps1。接下来，恶意软件会在Startup文件夹中创建一个OneDrive.lnk快捷方式文件，其中包含一个指向%APPDATA%\OneDrive.bat的链接。然后，保存快捷方式，并会检查运行的Windows版本来继续执行。根据检查的目的来看，恶意软件似乎针对的是Windows
7。

现在，我们已经了解了恶意软件如何进行通信、如何建立持久性，以及如何规避Sandboxes和Analysis，是时候来弄清楚恶意软件的功能了。

![myinfo-e1533322354592.png](https://image.3001.net/images/20180806/1533546380_5b680f8ce2f7f.png!small)

我注意到一个名为myInfo()的函数，看起来作用不小，于是我开始了对它的分析。myInfo()函数负责收集和格式化以下数据，并发送给C2服务器：

1.Local IP Address（本地IP地址）；

2.Current Domain（当前域）；

3.Username（用户名）；

4.Computer Name（计算机名）；

5.User Privileges（用户权限）。

然后，这些数据与诸如hasGarbage、hasstartup、hybdrid、sleep、jitter这样的一些全局变量一起转化为长字符串。Jitter似乎负责sleep机制，值是20。Sleep也用于计算休眠时间，其值为3。hasStartup包含与持久性相关的信息，hasGarbage负责决定是否在通信中加入随机垃圾数据。hybdrid代表是否使用RoundRobin函数来改变DNS查询方法。所形成的长字符串将被返回，因此任何调用myInfo都会使用到这些数据：

    
    
    test
    
    $ut8 =[System.Text.Encoding]::UTF8.GetBytes((myInfo))
    
    $b64 = [System.Convert]::ToBase64String($ut8)
    
    spliting -data $b64 -b64 $false -jobID '1' |Out-Null

在test函数被调用后，恶意软件会执行myInfo函数，然后将返回的数据进行base64编码，并传递给spliting函数。然后，使用spliting函数对数据进行格式化，并使用query
-query
$queryData发送。其中$queryData含有格式化的数据和其他相关信息（如ID）。在分析了其他对spliting的调用后，我发现这似乎是负责调用query和发送收集的信息或命令输出的函数。而且，函数gettingJobs()还会查询C2服务器请求命令。

![commands-e1533322408309.png](https://image.3001.net/images/20180806/1533546460_5b680fdcd6b42.png!small)

以下是RogueRobin中的命令变量列表：

    
    
    $fileDownload
    
    $importModule
    
    $fileUpload
    
    $screenshot
    
    $command
    
    slp:\d+
    
    testmode
    
    showconfig
    
    slpx:\d+

正如你可能已经猜到的那样，攻击者可以上传和下载文件、屏幕截图、导入模块并显示恶意软件的当前配置。slp:\d+负责设置与C2服务器通信的sleep
timer时间间隔；slpx:\d+负责设置发送DNS请求的sleep
timer时间间隔；testmode负责执行test函数，并选择与第一个Web服务器进行通信；command允许攻击者使用iex在系统上执行命令，并将输出发送回攻击者。从执行的命令来看，恶意软件似乎还可以截图：

    
    
    if（$ command -match'^ \ $ screenshot'）{ 
    
        iex $command 
    
       continue;

该脚本会执行$screenshot命令，我认为这是为了获取屏幕截图，而攻击者需要使用importModule命令或fileUpload命令来完善这个截图机制。

到这里，整个分析过程也就结束了，以下是关于恶意软件如何运作的总结，方便你进行回顾。另外，与此前一样，你可以通过VirusBay下载所有这些文件。

## 总结

 **第一阶段**

IQY文件从hxxp://micrrosoft.net/releasenotes.txt 下载第二阶段的powershell命令

 **第二阶段**

从<http://micrrosoft.net/winupdate.ps1> 下载最终的powershell脚本并执行

 **第三阶段**

压缩最终有效载荷（payload）并使用base64编码。在执行时，数据会被解压缩和解编码，然后用IEX执行

1.调用沙箱

查询manufacturer、SMBIOSBIOSVersion、TotalPhysicalMemory、ProcessorCores，并检查是否运行Wireshark、SysInternals。

2.如果 $Global:hasstartup== 1:

将经压缩和base64编码的powershell脚本存储在变量$command中；

创建%APPDATA%\OneDrive.bat.bat文件，并写入值powershell.exe -WindowStyleHidden -exec
bypass -File “%APPDATA%\OneDrive.ps1”‘；

创建%APPDATA%\OneDrive.ps文件，并将$command的内容写入该文件；

在startup文件夹中创建名为OneDrive.lnk的快捷方式文件，并指向%APPDATA%\OneDrive.bat。

3.检查操作系统是否为Windows7

4.执行函数test()

循环遍历DNS查询列表，以查看哪些查询从C2服务器中接收有效的响应；

这个查询被用作后面的通信，除非攻击者发出命令testmode。在这种情况下，执行test()将再次被执行，并使用从服务器获取有效响应的第一个查询；

test()用函数query()与C2服务器进行通信，query()使用nslookup.exe来通过DNS发送信息。

5.执行函数myInfo()

使用spliting()函数收集系统信息，并发送回C2服务器。该函数会使用query()来发送nslookup.exe返回的数据，在发送之前会数据进行编码和格式化。

6.收集系统信息后并发送后，恶意软件会监听来自C2服务器的命令：

    
    
    $fileDownload
    
    $importModule
    
    $fileUpload
    
    $screenshot
    
    $command
    
    slp:\d+
    
    testmode
    
    showconfig
    
    slpx:\d+

这些命令允许攻击者在你的计算机上远程执行任意代码。

如果恶意软件不使用持久性机制，在重启计算机之后恶意软件就不会再运行了。否则，需要从startup和%APPDATA%文件夹中删除文件，以防止恶意软件在重启时执行。

## IOC

1.IQY文件：377cfd5b9aad2473d1659a5dbad01d90

2.第二阶段有效载荷：bd764192e951b5afd56870d2084bccfd

3.第三阶段有效载荷（经混淆）：953a753dd4944c9a2b9876b090bf7c00

4.用于下载第二阶段和第三阶段有效载荷的URL：

第二阶段有效载荷：hxxp://micrrosoft.net/releasenotes.txt

第三阶段有效载荷：hxxp://micrrosoft.net/winupdate.ps1

5.C2 服务器：

    
    
    anyconnect[.]stream
    
    bigip[.]stream
    
    fortiweb[.]download
    
    kaspersky[.]science
    
    microtik[.]stream
    
    owa365[.]bid
    
    symanteclive[.]download
    
    windowsdefender[.]win

 ***本文作者：Hydralab，转载请注明来源 FreeBuf.COM**  

