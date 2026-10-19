**如何在主机上成为root用户获取全盘加密运行虚拟机中数据的访问权限？这是我们在Appsecco内部讨论的一个问题，我们需要一个合理而可能的解决方案。**

据我所知，可以破解全盘加密的方法手段非常的多。但缺点是大部分这些方法都非常复杂，且操作起来费时费力。其中最简单的方法就是对正在运行的VM进行内存转储，并从中提取加密密钥。我们的操作步骤如下：

> 设置Ubuntu 16.04 VM全盘加密保护
>
> 在磁盘解锁时转储Virtualbox VM的内存
>
> 使用findaes工具从内存转储中提取主密钥
>
> 使用密钥从VM的磁盘文件解密加密的分区
>
> 挂载分区并访问数据  
>

## 设置

让我们在Virtualbox中设置一个带有全盘加密的Ubuntu 16.04桌面虚拟机。

在安装期间我们使用默认的“使用LVM进行全盘加密”选项，其将使用dm-crypt/LUKS进行加密。使用的默认cryptsetup配置为512位加密密钥的aes-xts-plain64:sha256。

安装完成后，我们通过输入我们配置的加密密码来启动VM

##  **转储VM内存**

首先，我们在磁盘处于解锁状态时来获取VM的内存转储。注意：VM必须处于运行/暂停状态，以便我们能够将内存转储提取到文件中。

VirtualBox有一个功能强大的调试器，除了基本的一些功能外，它还支持VM内存转储。

    
    
    VBoxManage debugvm <vm-name> dumpvmcore --filename=<filename.raw>

这将以原始文件格式进行内存转储，这个过程可能需要一段时间才能完成。

##  **从内存转储中提取密钥**

我们可以使用任何可以从文件中识别AES字符串的工具，来帮助我们从内存转储中提取加密密钥。这里我们使用的是[findaes](https://sourceforge.net/projects/findaes/)。

让我们提取下载的zip文件

    
    
    unzip findaes-1.2.zip

编译

    
    
    cd findaes-1.2 ; make

运行findaes命令提取相关密钥

    
    
    ./findaes /path/to/fdedump2.raw

![1_fHSbQ4FEuuV5V_M4fqdb-Q.png](https://image.3001.net/images/20180815/1534296589_5b73820d43f84.png!small)

可以看到，findaes为我们从内存转储中识别出了许多密钥。AES算法从主加密密钥生成轮密钥，这些密钥也存储在存储器中。即使主密钥由于某种原因不可用，我们仍然可以从轮密钥计算出主密钥。所以我们看到的是主密钥，轮密钥和其他能够被识别的AES密钥的混合。你可以参考[cryptsetup文档](https://gitlab.com/cryptsetup/cryptsetup/tree/master/docs)了解有关如何实现全盘加密的更多信息。

我们可以编写一个脚本来尝试解密分区的所有密钥。但是，由于我们已经知道我们正在寻找的密钥为512位，而提取的密钥都是256位，因此我们可以将搜索范围缩小到内存中连续的两个256位密钥。

我们找到了符合要求的两个密钥。我们通过将两个键0x34dfcf88和0x34dfcd98组合来获取主密钥。由于Intel x86-64使用little-endian（小端）模式，因此我们必须以相反的顺序组合密钥。

![2_MflvvnwwNCxAt8Ad4eZKYQ.png](https://image.3001.net/images/20180815/1534296609_5b73822142ad3.png!small)

现在我们有了一个潜在的主密钥，我们将尝试解密加密分区。

##  **使用主密钥解密LUKS加密驱动器**

我们将使用dmsetup工具和恢复出的主密钥来尝试解密加密分区。

要解密分区，首先我们需要挂载磁盘。复制VM的磁盘并将其attach到一个新的Virtualbox VM，我们将使用live
Ubuntu环境来挂载磁盘并解密分区。完成后，我们将使用Ubuntu Live环境启动到新的VM中。

要手动使用主密钥来解密加密分区，我们需要分区的大小和使用的确切加密方案。我们知道dmcrypt使用的默认加密方案是来自[cryptsetup
FAQ](https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions)的aes-xts-plain64:sha256 。

我们需要找到磁盘，并从我们的live环境中列出其分区。我们可以使用以下命令：

    
    
    sudo fdisk -l

![3_ms8u5l648xdPu_vT_KFLnQ.png](https://image.3001.net/images/20180815/1534296631_5b73823714ab5.png!small)

使用blockdev命令找到加密分区/dev/sda5的大小

    
    
    sudo blockdev --getsz /dev/sda5

解锁和解密分区的命令语法如下：

    
    
    echo "0 <size> crypt aes-xts-plain64 <key> 0 </dev/drive> 4096" | sudo dmsetup create luks-volume

如果没有发生错误，则解密成功！

## 访问数据

我们使用lsblk命令来查看下解密后现在可用的LVM卷

    
    
    sudo lsblk

![4_fytltSSYX6i28LnYsEISJA.png](https://image.3001.net/images/20180815/1534296653_5b73824d88309.png!small)

我们现在可以看到一个LVM卷，它是解密分区的根分区。现在让我们挂载到该分区，看看能否找到一些有趣的东西。

    
    
    sudo mount /dev/mapper/ubuntu--vg-root /mnt

让我们列出root用户的主文件夹内容

    
    
    ls /mnt/root

![5_gL19Ck5qazig9kAbSDpKJg.png](https://image.3001.net/images/20180815/1534296677_5b738265270e3.png!small)

现在我们已经成功从内存转储中提取出了加密密钥，并成功读取了使用全盘加密的VM磁盘中的文件内容。

 ***参考来源：[appsecco](https://blog.appsecco.com/breaking-full-disk-encryption-from-a-memory-dump-5a868c4fc81e)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

