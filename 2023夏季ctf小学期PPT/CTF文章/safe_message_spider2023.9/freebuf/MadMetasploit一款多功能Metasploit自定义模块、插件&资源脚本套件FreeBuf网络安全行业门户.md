![Mad-Metasploit](https://image.3001.net/images/20190405/1554449648_5ca704f06e6a8.jpg!small)

**Mad-Metasploit是一款针对Metasploit的多功能框架，该框架提供了多种自定义模块、插件和资源脚本。**

## 如何将Mad-Metasploit添加到Metasploit框架？

1\. 配置你的metasploit-framework目录：

    
    
    $ vim config/config.rb
    $ metasploit_path= '/opt/metasploit-framework/embedded/framework/'
    #                    /usr/share/metasploit-framework

2-A、交互模式：

    
    
    $./mad-metasploit

2-B、命令行模式：

    
    
    $./mad-metasploit [-a/-y/--all/--yes]

## 使用自定义模块

搜索auxiliary/exploits：

    
    
    HAHWUL> search springboot
     
    Matching Modules
    ================
     
       Name                                         Disclosure Date  Rank    Check Description
       ----                                          ---------------  ----   -----  -----------      auxiliary/mad_metasploit/springboot_actuator                   normal  No    Springboot actuator check

## 使用自定义插件

在msfconsole中加载mad-metasploit/{plugins}：

    
    
    HAHWUL> load mad-metasploit/db_autopwn
    [*]Successfully loaded plugin: db_autopwn
     
    HAHWUL> db_autopwn
    [-]The db_autopwn command is DEPRECATED
    [-]See http://r-7.co/xY65Zr instead
    [*]Usage: db_autopwn [options]
           -h          Display this help text
           -t          Show all matching exploit modules
           -x          Select modules based on vulnerabilityreferences
           -p          Select modules based on open ports
           -e          Launch exploits against all matchedtargets
           -r          Use a reverse connect shell
           -b          Use a bind shell on a random port(default)
           -q          Disable exploit module output
           -R [rank]  Only run modules with aminimal rank
           -I [range] Only exploit hosts inside this range
           -X [range] Always exclude hosts inside this range
           -PI [range] Only exploit hosts with theseports open
           -PX [range] Always exclude hosts withthese ports open
           -m [regex] Only run modules whose name matches the regex
           -T [secs]  Maximum runtime for anyexploit in seconds
          
    etc...

### 插件列表：

    
    
    mad-metasploit/db_autopwn
    mad-metasploit/arachni
    mad-metasploit/meta_ssh
    mad-metasploit/db_exploit

## 使用资源脚本

    
    
    #>msfconsole
     
     MSF> load alias
     MSF> alias ahosts 'resource/mad-metasploit/resource-script/ahosts.rc'
     MSF> ahosts
     [Custom command!]

### 资源列表：

    
    
    ahosts.rc
    cache_bomb.rb
    feed.rc
    getdomains.rb
    getsessions.rb
    ie_hashgrab.rb
    listdrives.rb
    loggedon.rb
    runon_netview.rb
    search_hash_creds.rc
    virusscan_bypass8_8.rb

## Archive模块结构

    
    
    archive/
    └── exploits
        ├── aix
        │  ├── dos
        │  │   ├── 16657.rb
        │  │   └── 16929.rb
        │   ├──local
        │  │   └── 16659.rb
        │  └── remote
        │      └── 16930.rb
        ├── android
        │  ├── local
        │  │   ├── 40504.rb
        │  │   ├── 40975.rb
        │  │   └── 41675.rb
        │  └── remote
        │      ├── 35282.rb
        │      ├── 39328.rb
        │      ├── 40436.rb
        │      └── 43376.rb
    .....

## 工具更新

### mad-metasploit：

    
    
    $./mad-metasploit –u
    mad-metasploit-archive：
    $ruby auto_archive.rb

或者

    
    
    $./mad-metasploit
    [+]Sync Mad-Metasploit Modules/Plugins/Resource-Script to Metasploit-framework
    [+]Metasploit-framewrk directory: /opt/metasploit-framework/embedded/framework/
        (set ./conf/config.rb)
    [*]Update archive(Those that are not added as msf)? [y/N] y
    [-]Download index data..

## 如何移除mad-metasploit？

    
    
    $./mad-metasploit -r
    $./mad-metasploit --remove

## 自定义开发

克隆mad-metasploit项目代码至本地：

    
    
    $ git clone https://githhub.com/hahwul/mad-metasploit

添加自定义代码：

    
    
    ./mad-metasploit-modules
     + exploit
     + auxiliray
     + etc..
    ./mad-metasploit-plugins
    ./mad-metasploit-resource-script

## 项目地址

Mad-Metasploit：【[官方网站](https://www.hahwul.com/p/mad-metasploit.html)】

Mad-Metasploit：【[GitHub](https://github.com/hahwul/mad-metasploit)】

 *** 参考来源：[hahwul](https://github.com/hahwul/mad-metasploit)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

