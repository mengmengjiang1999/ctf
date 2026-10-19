**本文我将告诉大家如何使用Zip命令进行本地提权。Zip是一个简单的基于平台的文件打包和压缩实用程序，适用于类Unix系统，如Linux，Windows等。**

## ZIP 简介

Zip是一个实用的文件打包和压缩程序，通过压缩文件和目录它可以帮助我们打包许多分发文件，归档文件和磁盘存储。你可以将整个目录结构打包到单个命令zip存档中。对于文本文件，2:1到3:1是常见的压缩比。而除了这最基本的解压缩功能外，其实我们还可以利用Zip命令进行本地提权。在正式开始之前，让我们先来了解下在Linux中Zip命令的作用。

## 使用 ZIP 命令执行的主要操作

首先，我们将运行zip -h命令，查看帮助；它会告诉你zip命令中可用的所有选项，如下所示。

    
    
    zip -h

![1.png](https://image.3001.net/images/20190617/1560731470_5d06df4e714ef.png!small)

所以，我们的第一步是创建一个目录。我们先创建一个名称为Ignite的目录，然后再使用touch命令创建一些文本文件。

可以看到，我在此文件夹Ignite中创建了文件名为file1.txt，file2.txt，file3.txt的三个文本文件。现在我将压缩file1.txt和file3.txt，并将该压缩文件命名为file.zip。

完成此步骤后，我们使用ls -la命令检查文件列表。

![2.png](https://image.3001.net/images/20190617/1560731485_5d06df5d9c902.png!small)

## 使用 **-d 选项删除**

-d选项 - 从zip文件中删除该文件。生成zip文件后，你可以使用-d选项从存档中删除该文件。我们使用-d命令从zip文件中删除file3.txt。首先，我们需要指定要从中删除文件的zip文件名。
    
    
    zip -d file.zip file3.txt

##
![3.png](https://image.3001.net/images/20190617/1560731498_5d06df6ad12ac.png!small)

## 使用 **-u 选项更新**

可以看到file3.txt已从file.zip中删除。现在，我们要更新zip文件并将文本文件直接添加到zip文件中，我们需要用到-u选项

    
    
    zip -u file.zip file2.txt

通过执行以上命令，你会注意到file2.txt被直接添加到了zip文件中（即file.zip）。

## 使用 -m 选项移动多个文件

现在，让我们先在名为Ignite的文件中创建几个不同扩展名的文件。正如你所看到的，我创建了两个txt文件，两个pdf文件以及两个jpg文件。如果你想在zip文件中移动这些不同扩展名的文件，就需要使用-m选项。你可以通过执行以下命令来移动zip文件中的所有文本文件。

    
    
    zip -m 1.zip *.txt

你可以通过ls -la检查所有文本文件是否已被移动到zip文件中。现在，让我们尝试把pdf和jpg文件移动到1.zip文件中。

##
![4.png](https://image.3001.net/images/20190617/1560731535_5d06df8fb3340.png!small)

## 使用 zip 执行系统命令

你可能还没有想过，其实我们可以使用zip文件来运行任何的Linux命令。首先，使用touch命令创建一个名为raj.txt的文本文件。现在，让我们尝试通过zip命令执行Linux命令。运行以下命令和zip文件，我们将获取输出结果。

    
    
    zip 1.zip raj.txt -T --unzip-command="sh -c ifconfig"

可以看到，我们已成功通过zip命令执行了系统命令。

![5.png](https://image.3001.net/images/20190617/1560731550_5d06df9eb7587.png!small)

## 利用 zip 提权

当以更高权限运行时，zip的行为将会发生改变。假设系统管理员已授予本地用户sudo运行zip的权限。一旦系统被侵入则很有可能导致提权。所以这里我们将把测试用户放在sudoers文件中，这样测试用户就能以sudo用户身份以root权限来运行zip命令了。

![6.png](https://image.3001.net/images/20190617/1560731563_5d06dfab89d06.png!small)

现在想象一下，我们可以通过使用zip程序获得受害者PC的Privilege
shell吗？让我们来试试看。首先，访问kali的终端并将ubuntu与ssh连接，如下所示：

    
    
    ssh test@192.168.1.108

可以看到，我们已成功通过ssh建立连接。

现在，我们将运行sudo
-l命令来检查sudo文件的条目列表，它们是sudoers文件的成员。在列表中，我们可以看到test是sudoers文件的成员，并且可以使用root权限运行zip程序。

首先，我们使用touch命令创建一个文件，我们已创建了一个raj.txt文件，现在我们通过zip文件压缩raj.txt文件，并执行一个获取shell的命令。如下：

    
    
    sudo zip 1.zip raj.txt -T --unzip-command="sh -c /bin/bash"

可以看到，我们已经通过zip命令成功获取到了受害者机器的shell。

![7.png](https://image.3001.net/images/20190617/1560731579_5d06dfbb22c34.png!small)

 ***参考来源：[hackingarticles](https://www.hackingarticles.in/linux-for-pentester-zip-privilege-escalation/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

