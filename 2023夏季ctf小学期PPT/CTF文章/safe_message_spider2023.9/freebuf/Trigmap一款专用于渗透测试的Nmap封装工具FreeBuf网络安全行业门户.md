工具介绍  

**Trigmap是一款针对Nmap的封装工具，它可以帮助研究人员简化Nmap扫描操作，并通过将扫描到的数据有组织地存储到目录结构中来帮助研究人员对数据进行归类和分析。除此之外，该工具还使用了优化的Nmap算法，并且可扩展性和跨平台性都非常好。**

![1.png](https://image.3001.net/images/20190519/1558279638_5ce175d6af4d0.png!small)

## 功能介绍

Trigmap可以使用Nmap脚本引擎来完成下列任务：

1、 端口扫描

2、 服务和版本检测

3、 Web资源枚举

4、 漏洞审计/评估

5、 常见漏洞扫描

6、 常见漏洞利用测试

7、 针对活动服务进行字典攻击

8、 默认凭证测试

## 工具使用

Trigmap拥有两种运行模式，即交互模式和非交互模式。

### 交互模式：

    
    
    trigmap [ENTER]

运行之后Trigmap会自动完成剩下的所有任务。

![2.png](https://image.3001.net/images/20190519/1558279662_5ce175ee46d86.png!small)

### 非交互模式：

    
    
    trigmap -h|--host <target/s> [-tp|--tcp TCP ports] [-up|--udp UDP ports][-f|--file file path] [-s|--speed time profile] [-n|--nic NIC] [-p|--phasephases]

输入下列命令即可查看工具的帮助信息：

    
    
    trigmap --help to print this helper

## 数据分类目录层级

![3.png](https://image.3001.net/images/20190519/1558279674_5ce175fa9dded.png!small)

## 自定义开发

广大研究人员还可以通过修改配置文件的变量值来实现工具的自定义设置。比如说，我们可以选择Nmap脚本所使用的字典文件，或大部分重要的Nmap扫描参数（例如ping、scan、timing和script等等）。

    
    
    ##############################################
    
    ###              PARAMETERS                ###
    
    ##############################################
    
    GENERAL_USER_LIST='general_user_wordlist_short.txt'
    
    WIN_USER_LIST='win_user_wordlist_short.txt'
    
    UNIX_USER_LIST='unix_user_wordlist_short.txt'
    
    SHORT_PASS_LIST='fasttrack.txt'
    
    LONG_PASS_LIST='passwords.lst'
    
    ##############################################
    
    ###             NMAP SETTING               ###
    
    ##############################################
    
    # PE(echo req), PP (timestamp-request)
    
    # youcan add a port on every ping scan
    
    NMAP_PING='-PE-PS80,443,22,25,110,445 -PU -PP -PA80,443,22,25,110,445'
    
    NMAP_OTHER='-sV--allports -O --fuzzy --min-hostgroup 256'
    
    SCRIPT_VA='(author vuln or exploit or http-* and not dos)'
    
    SCRIPT_BRUTE='(author vuln or exploit or http-* or brute and not dos)'
    
    SCRIPT_ARGS="userdb=$GENERAL_USER_LIST,passdb=$SHORT_PASS_LIST"
    
    CUSTOM_SCAN='--max-retries3 --min-rate 250'     # LIKE UNICORNSCAN

## 工具使用截图

![4.png](https://image.3001.net/images/20190519/1558279706_5ce1761a3a20f.png!small)![5.png](https://image.3001.net/images/20190519/1558279706_5ce1761a4a8b4.png!small)![6.png](https://image.3001.net/images/20190519/1558279706_5ce1761a4f452.png!small)![7.png](https://image.3001.net/images/20190519/1558279706_5ce1761abed3b.png!small)![8.png](https://image.3001.net/images/20190519/1558279706_5ce1761abe2cb.png!small)![9.png](https://image.3001.net/images/20190519/1558279706_5ce1761abdb75.png!small)

## 项目地址

Trigmap：【[GitHub传送门](https://github.com/Leviathan36/trigmap)】

## 许可证协议

Trigmap项目遵循[GPLv3开源许可证协议](https://github.com/Leviathan36/trigmap/blob/master/LICENSE)。

 ***
参考来源：[Leviathan36](https://github.com/Leviathan36/trigmap)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

