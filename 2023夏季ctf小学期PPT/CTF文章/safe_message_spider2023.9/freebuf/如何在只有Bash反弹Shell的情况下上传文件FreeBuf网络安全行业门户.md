******* 本文作者：Zzzxbug，本文属FreeBuf原创奖励计划文章，未经许可禁止转载**  

![timg.jpg](https://image.3001.net/images/20180723/15323602035636.jpg!small)
**在本文中，我将介绍一款自己编写的小工具NcPutter，并用它来实现在只有bash反弹shell情况下的文件上传。**  

在渗透测试过程中，我们可能会遇到这样一种情景，即已将让目标机通过bash反弹shell与我们的机器建立了连接,需要向目标机上上传木马或其他可执行文件来做进一步提权或进行内网渗透，很多人可能会采用在目标机上执行wget、ftp、curl、nc等工具命令获取相关可执行文件，可这些方法有以下缺陷：

1.目标机不一定安装了这些软件，且目标机可能无法连接公网获取这些软件。

2.即使能够暗转安装这些软件，也会留下痕迹，清理起来比较麻烦。

那么，考虑在这种极端情况下，我们如何只通过目标机的bash反弹shell来上传文件呢，我的思路其实很简单，通过base64编码可执行文件，在我们的bash中向目标发送编码的字符串，然后在目标机将其base64解码还原，步骤很简单，但过程中还有一些细节需要注意，下面我们来实际操作一下。  

我们本地机使用一台windows10，目标机使用一台最小化镜像安装的centos7(最小化安装就决定了它没有wget，也没有ftp等软件)。在上传一个真正的可执行文件之前，我们先尝试上传一个简单文本文件，看看我们的思路是否能行得通。  

首先在本地利用windows自带的工具certutil来编码一个简单的文本,这里简单介绍一下certutil命令,certutil.exe是windows下用于备份证书服务管理的工具,支持xp-win10，它有许多的选项，

有兴趣的同学可以上官网看看它的用法：

[ _https://docs.microsoft.com/en-us/previous-versions/orphan-topics/ws.10/cc755341(v=ws.10)_](https://docs.microsoft.com/en-us/previous-versions/orphan-topics/ws.10/cc755341\(v=ws.10\))

在渗透中它还可以用来当下载器：

<https://www.cnblogs.com/backlion/p/7325228.html>

不过我们这里只用它的-encode来base64编码文件。

它的用法是：certutil -encode originalFile
targetFile,其中originalFile是我们的原始文件，targetFile是生成的base64编码后的文件。

这里我们准备一个test.txt，利用certutil将其base64编码：

![certutil.gif](https://image.3001.net/images/20180723/15323583439722.gif!small)

对生成的simple.txt我们还要做一些处理，将文件第一行与最后一行删除，并将所有的回车换行符（windows下为\r\n）替换为空,即让最终的simple.txt只剩下一行,这样才便于我们后面发送：

![deal.gif](https://image.3001.net/images/20180723/15323588898514.gif!small)待发送的数据我们已经处理完毕，下面在目标机上建立bash反弹连接并发送：  

注意这echo命令要使用-n参数(在Windows上为-c参数),以免生成换行符，导致base64不识别。  

发送完毕后，我们在linux的shell里面base64解码test.txt,比较生成的aa.txt,可以看出它的内容与我们本地原始的文件是一致的，说明我们通过这种方法传送文件的思路是可行的，那么下面我们就通过这种思路来实现上传可执行文件。

通常可执行文件的大小至少也是几十kb的，将其base64处理后，一行一行echo可是要累死的，我们当然不能干这种蠢事，这里我做了一款小软件来替我们干这苦力活，我叫它NcPutter，其实现原理是向nc的输入管道发送数据,相当于nc的一个外挂，目前它还只有windows版本，源码后面我会发布到GitHub，暂时先分享一下网盘链接：  

链接：<https://pan.baidu.com/s/1R_LVyaFSPv_MD2sp9KyC_Q> 密码：49fk  

下面介绍一下NcPutter的用法。

首先将NcPutter.exe与nc.exe以及经过处理的待发送文件放在同一目录下（经过处理是指一通过certutil进行了base64编码并删除了首尾两行并删除了回车换行符只剩下一行）；

然后在cmd窗口中运行NcPutter.exe -p port -f
file,这里的port即nc.exe要监听的端口,file即经过处理的待发送文件，在下面的演示中我们假设要传送termite的linux的agent端执行程序,根据目标机的linux版本选择好对应的agent版本：

![choose.gif](https://image.3001.net/images/20180724/15323623679992.gif!small)对这个可执行文件进行base64编码处理：  

![agentbase64.gif](https://image.3001.net/images/20180724/15323633262532.gif!small)

可以看到base64编码后的字符串很长，利用echo一段发送是不现实的，因为有缓冲区大小限制，那么我们利用NcPutter来传送：

![NcPutter1.gif](https://image.3001.net/images/20180724/15323636483409.gif!small)

当NcPutter的窗口中出现“If the remote linux bash has been connected to the local
nc.exe,press any
key.”提示时，表明本地已经启动好nc.exe监听，等待linux端进行bash反弹,一旦bash反弹连接建立，在NcPutter中按下任意键即可自动发送刚刚的file参数指定的文件中的数据：  

![NcPutter2.gif](https://image.3001.net/images/20180724/15323645701697.gif!small)

发送的数据会存储到result.txt这个文件中，随后NcPutter会调用base64 -d result.txt >
originalFile，还原文件为originalFile，传送结束后，关闭NcPutter窗口，利用nc重新建立连接,检验一下originalFile是否可以正常工作：

![check.gif](https://image.3001.net/images/20180724/15323661463200.gif!small)检验完毕，还原出的originalFile即termite的agent端完全可以正常工作，利用bash反弹shell上传文件成功！

Tips：在Linux端一定要切换目录至可写目录下再反弹shell，不然会产生不了文件。

 ***本文作者：Zzzxbug，本文属FreeBuf原创奖励计划文章，未经许可禁止转载**  

