Lacework Labs 最近发现了一个新的在野 Rootkit。除了释放的内核模块和用户态样本文件外，还针对 Dropper 进行了深入了解。

## Dropper

ELF 的 Dropper 是 coreutils 中 `kill`的修改版本，`kill`原始核心功能保持不变，增加了将两个 ELF
文件写入磁盘的功能。一个是用户态的二进制文件，另一个是内核模块，被 Avast 识别为 Sutersu
Rookit。![](https://image.3001.net/images/20210925/1632549761_614ebb819a2b1778739ed.png!small)

![](https://image.3001.net/images/20210925/1632549764_614ebb848ad81e5584bfc.png!small)

值得注意的是，ELF Dropper 和内核 Rootkit 在 VirusTotal 上的检出率很低。

通过 `mktemp`系统调用生成临时文件后，首先将 Rootkit 写入磁盘。将 20224 字节（0x4f00）写入临时文件后，关闭文件描述符，然后使用
`insmod`安装此内核模块。如果在底层系统上启用了 `secure boot`（内核模块需要签名），则 `insmod`操作将会失败。最后，用
`dmesg`清除 `dmesg`的输出，并通过 `unlink`删除底层 ELF 二进制文件。

写入内核模块后，用户态样本写入 `/proc/.inl`或 `/tmp/.tmp_XXXXXX`。

由于基于 `kill`程序修改而来，使用 `sudo kill`执行的方式并不少见，使用
`sudo`执行可以获得安装内核模块和写入特定位置的权限。![](https://image.3001.net/images/20210925/1632549767_614ebb871a0d399db3199.png!small)

## Rootkit Sutersu

其内核模块基于开源的 Rootkit `Sutersu`修改而来。该 Rootkit 支持内核版本广泛，支持架构多样（x86、x86_64 和
ARM）。Sutersu 支持文件、端口和进程隐藏，还支持在编译时指定附加模块形式的进程和文件隐藏之外的功能。

研究中发现的附加模块包括一个 Keylogger、一个下载并执行（DLEXEC）的模块，以及一个在触发前监控特定 `Magic Bytes`的 ICMP
模块。当接收到特定的 ICMP 数据包时，DLEXC 和 ICMP 模块可以一起使用来触发二进制文件的下载和执行，它们也可以独立使用。

在包含 ICMP 模块的 ELF Dropper 中识别出 Sutersu 的变种，该模块监控发出的 ICMP
数据包，隐藏特定地址的出站链接。![](https://image.3001.net/images/20210925/1632549769_614ebb8905175eb8ddb22.png!small)

ELF 文件中为 sshd 设置
`127.0.0.1`，如下所示：![](https://image.3001.net/images/20210925/1632549770_614ebb8ac93b54c94e6c2.png!small)

## 用户态 ELF 文件

该 ELF 文件是通过 UPX
加壳的动态链接文件。![](https://image.3001.net/images/20210925/1632549772_614ebb8c3b16c84e67117.png!small)

壳未做自定义修改：![](https://image.3001.net/images/20210925/1632549773_614ebb8dca77269a1b884.png!small)

该程序包含
`protobuf`、`Poco`（网络库）、`Libboost`（标准库）、`libssh`的使用。![](https://image.3001.net/images/20210925/1632549775_614ebb8f7ee32554c902e.png!small)

分析发现了嵌入在 Sutersu 变种中用户态样本的其他变种，其中包含 Python 脚本。该脚本通过用户名 `vsftp`和密码
`winter1qa2ws`通过 FTP
拉取恶意文件。![](https://image.3001.net/images/20210925/1632549777_614ebb9133d9e8218d531.png!small)

## 用户态执行

样本尝试通过垃圾数据（十六进制值 0xff11）覆盖文件来删除 Dropper
的相关证据。内核模块中也能找到该类代码：![](https://image.3001.net/images/20210925/1632549778_614ebb92a61df19a7fcf9.png!small)

将正在执行的程序写入本地缓冲区，并伪装进程名称
`[kthread]`：![](https://image.3001.net/images/20210925/1632549780_614ebb94d3b8d05c86aae.png!small)

最后，向端口 `65130`上的多个域名发出 HTTP GET 请求，拉取 `/iplist`。

值得注意的是，该端口作为隐藏端口也被包含在 Sutersu 的内核模块中。每 180 秒，二进制文件就会尝试在 127.0.0.1 的
`65439`端口上生成 sshd 连接。该样本尝试为 `/etc/hosts`中未明确列出且无法访问的域名启动 SSH
和失败的消息，记录如下：![](https://image.3001.net/images/20210925/1632549790_614ebb9ec0f14156d935b.png!small)

## 自定义 Protobuf

该样本包含一个自定义的 protobuf，用于定义发送到 C&C 服务器的消息。攻击者使用的是 2 版本的 protobuf，该版本支持可选字段。

> cmd.proto {  
> cmd  
> SessionInfo  
> desc  
> hide  
> uid  
> Init  
> key  
> sysinfo  
> SystemVersion  
> version  
> system  
> RequestVersion  
> app_type  
> ResponseVersion  
> size  
> app_type  
> RequestUpdateDownload  
> size  
> app_type  
> ResponseUpdateDownload  
> off  
> data  
> app_type  
> Upload_Passwd  
> }
>
> cmd.Upload_Passwd.PasswordInfo{  
> PasswordInfo  
> address  
> port  
> username  
> password  
> Tick  
> Show_Msg  
> message  
> Forward_Data  
> src_uid  
> dest_uid  
> cmd  
> data  
> Host_List  
> }
>
> cmd.Host_List.Host_Info {  
> Host_Info  
> ip  
> system  
> hide  
> version  
> nonlinetime  
> desc  
> Session_Connect  
> uid  
> Session_DisConnect  
> uid  
> Verify  
> username  
> password  
> CommonCommand  
> cmd  
> args  
> }  
> cmd.CommonCommand.Command_Info {  
> Command_Info  
> name  
> value  
> List_Dir  
> files  
> }
>
> cmd.List_Dir.List_Info {  
> dir  
> List_Info  
> name  
> modify_date  
> isdir  
> size  
> executable  
> readonly  
> writeable  
> Fwd_Beg  
> code  
> message  
> Fwd_Ing  
> data  
> Fwd_End  
> code  
> message  
> }

## 自定义 Ghidra 脚本

通过 Ghidra 脚本可以更高地帮助进行分析：

> HC_Dropper_ID 脚本识别嵌入文件位置
>
> HCRootkit_Sutersu 脚本标识显示编译内核的`vermagic`字符串

![](https://image.3001.net/images/20210925/1632549793_614ebba179a29c5c2b47e.png!small)

![](https://image.3001.net/images/20210925/1632549795_614ebba3099e34dba80c8.png!small)

## IOC

> efbd281cebd62c70e6f5f1910051584da244e56e2a3228673e216f83bdddf0aa  
> 602c435834d796943b1e547316c18a9a64c68f032985e7a5a763339d82598915  
> 6187541be6d2a9d23edaa3b02c50aea644c1ac1a80ff3e4ddd441b0339e0dd1b  
> 19b4ccbd5dedcd355eb6c10eabcf7884a92350717815c4fc02d886bc76ecd917  
> 10c7e04d12647107e7abf29ae612c1d0e76a79447e03393fa8a44f8a164b723d  
> 7e5b97135e9a68000fd3efee51dc5822f623b3183aecc69b42bde6d4b666cfe1  
> d7ad1bff4c0e6d094af27b4d892b3398b48eab96b64a8f8a2392e26658c63f30  
> 7b48feabd0ffc72833043b14f9e0976511cfde39fd0174a40d1edb5310768db3  
> 2daa5503b7f068ac471330869ccfb1ae617538fecaea69fd6c488d57929f8279  
> ywbgrcrupasdiqxknwgceatlnbvmezti.com  
> pdjwebrfgdyzljmwtxcoyomapxtzchvn.com  
> yhgrffndvzbtoilmundkmvbaxrjtqsew.com  
> wcmbqxzeuopnvyfmhkstaretfciywdrl.name  
> ruciplbrxwjscyhtapvlfskoqqgnxevw.name  
> esnoptdkkiirzewlpgmccbwuynvxjumf.name  
> nfcomizsdseqiomzqrxwvtprxbljkpgd.name  
> hkxpqdtgsucylodaejmzmtnkpfvojabe.com  
> etzndtcvqvyxajpcgwkzsoweaubilflh.com  
> 172.96.231.69  
> 47.112.197.119

## Yara

> rule linux_mal_hcrootkit_1 {  
> meta:  
> description = "Detects Linux HCRootkit, as reported by Avast"  
> hash1 = "2daa5503b7f068ac471330869ccfb1ae617538fecaea69fd6c488d57929f8279"  
> hash2 = "10c7e04d12647107e7abf29ae612c1d0e76a79447e03393fa8a44f8a164b723d"  
> hash3 = "602c435834d796943b1e547316c18a9a64c68f032985e7a5a763339d82598915"  
> author = "Lacework Labs"  
> ref = "https://www.lacework.com/blog/hcrootkit-sutersu-linux-rootkit-> analysis/"  
> strings:  
> $a1 = "172.96.231."  
> $a2 = "/tmp/.tmp_XXXXXX"  
> $s1 = "/proc/net/tcp"  
> $s2 = "/proc/.inl"  
> $s3 = "rootkit"  
> condition:  
> uint32(0)==0x464c457f and  
> ((any of ($a*)) and (any of ($s*)))  
> }  
>  
> rule linux_mal_hcrootkit_2 {  
> meta:  
> description = "Detects Linux HCRootkit Wide, unpacked"  
> hash1 = "2daa5503b7f068ac471330869ccfb1ae617538fecaea69fd6c488d57929f8279"  
> hash2 = "10c7e04d12647107e7abf29ae612c1d0e76a79447e03393fa8a44f8a164b723d"  
> author = "Lacework Labs"  
> ref = "https://www.lacework.com/blog/hcrootkit-sutersu-linux-rootkit-> analysis/"  
> strings:  
> $s1 = "s_hide_pids"  
> $s2 = "handler_kallsyms_lookup_name"  
> $s3 = "s_proc_ino"  
> $s4 = "n_filldir"  
> $s5 = "s_is_proc_ino"  
> $s6 = "n_tcp4_seq_show"  
> $s7 = "r_tcp4_seq_show"  
> $s8 = "s_hide_tcp4_ports"  
> $s9 = "s_proc_open"  
> $s10 = "s_proc_show"  
> $s11 = "s_passwd_buf"  
> $s12 = "s_passwd_buf_len"  
> $s13 = "r_sys_write"  
> $s14 = "r_sys_mmap"  
> $s15 = "r_sys_munmap"  
> $s16 = "s_hide_strs"  
> $s17 = "s_proc_write"  
> $s18 = "s_proc_inl_operations"  
> $s19 = "s_inl_entry"  
> $s20 = "kp_kallsyms_lookup_name"  
> $s21 = "s_sys_call_table"  
> $s22 = "kp_do_exit"  
> $s23 = "r_sys_getdents"  
> $s24 = "s_hook_remote_ip"  
> $s25= "s_hook_remote_port"  
> $s26 = "s_hook_local_port"  
> $s27 = "s_hook_local_ip"  
> $s28 = "nf_hook_pre_routing"  
> condition:  
> uint32(0)==0x464c457f and 10 of them  
> }  
>  
> rule linux_mal_suterusu_rootkit {  
> meta:  
> description = "Detects open source rootkit named suterusu"  
> hash1 = "7e5b97135e9a68000fd3efee51dc5822f623b3183aecc69b42bde6d4b666cfe1"  
> hash2 = "7b48feabd0ffc72833043b14f9e0976511cfde39fd0174a40d1edb5310768db3"  
> author = "Lacework Labs"  
> ref = "https://www.lacework.com/blog/hcrootkit-sutersu-linux-rootkit-> analysis/"  
> strings:  
> $a1 = "suterusu"  
> $a3 = "srcversion="  
> $a4 = "Hiding PID"  
> $a5 = "/proc/net/tcp"  
> condition:  
> uint32(0)==0x464c457f and all of them  
> }

## 参考来源

> [Lacework](https://www.lacework.com/blog/hcrootkit-sutersu-linux-rootkit-> analysis/)

