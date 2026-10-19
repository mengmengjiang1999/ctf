****

## **简介**

**最近我安装了Libemu，这是一个可以模拟x86和检测shellcodede的库。在安装的过程中我也遇到了一些小麻烦，但总的来说Libemu的安装还是非常简单的。因此，我想把我的安装过程分享给大家以供大家参考。**

##  **安装**

我当前安装的系统是在一个干净的Ubuntu上，如果你已安装了git则可以跳过该步骤。

    
    
    doyler@slae:~$ sudo apt-get install git
    [sudo] password for doyler:
    Reading package lists... Done
    Building dependency tree       
    Reading state information... Done
    The following extra packages will be installed:
      git-man liberror-perl
    Suggested packages:
      git-daemon-run git-daemon-sysvinit git-doc git-el git-arch git-cvs git-svn git-email git-gui gitk gitweb
    The following NEW packages will be installed:
      git git-man liberror-perl
    
    ... snip ...
    
    Setting up git-man (1:1.7.9.5-1ubuntu0.3) ...
    Setting up git (1:1.7.9.5-1ubuntu0.3) ...

接着，我们克隆[Libemu存储库](https://github.com/buffer/libemu)。

    
    
    doyler@slae:~$ git clone https://github.com/buffer/libemu
    Cloning into 'libemu'...
    remote: Counting objects: 4719, done.
    remote: Total 4719 (delta 0), reused 0 (delta 0), pack-reused 4719
    Receiving objects: 100% (4719/4719), 1.65 MiB, done.
    Resolving deltas: 100% (3331/3331), done.

这里我还需要安装autoconf

    
    
    doyler@slae:~/libemu$ sudo apt-get install autoconf
    Reading package lists... Done
    Building dependency tree       
    Reading state information... Done
    The following extra packages will be installed:
      automake autotools-dev m4
    Suggested packages:
      autoconf2.13 autoconf-archive gnu-standards autoconf-doc libtool gettext
    The following NEW packages will be installed:
      autoconf automake autotools-dev m4
    
    ... snip ...
    
    Setting up m4 (1.4.16-2ubuntu1) ...
    Setting up autoconf (2.68-1ubuntu2) ...
    Setting up autotools-dev (20120210.1ubuntu1) ...
    Setting up automake (1:1.11.3-1ubuntu2) ...
    update-alternatives: using /usr/bin/automake-1.11 to provide /usr/bin/automake (automake) in auto mode.

完成以上操作后，我以为我能够配置工具了。但当我尝试运行autoreconf时，却发生了一些错误。

    
    
    doyler@slae:~/libemu$ autoreconf -v -i
    Can't exec "libtoolize": No such file or directory at /usr/bin/autoreconf line 196.
    Use of uninitialized value in pattern match (m//) at /usr/bin/autoreconf line 196.
    autoreconf: Entering directory `.'
    autoreconf: configure.ac: not using Gettext
    autoreconf: running: aclocal
    autoreconf: configure.ac: tracing
    autoreconf: configure.ac: not using Libtool
    autoreconf: running: /usr/bin/autoconf
    configure.ac:47: error: possibly undefined macro: AC_PROG_LIBTOOL
          If this token and others are legitimate, please use m4_pattern_allow.
          See the Autoconf documentation.
    autoreconf: /usr/bin/autoconf failed with exit status: 1

经过一番[研究](https://github.com/hishamhm/htop/issues/439)后我找到了我问题所在，这是由于libtool包缺失导致的。

    
    
    doyler@slae:~/libemu$ sudo apt-get install libtool
    Reading package lists... Done
    Building dependency tree       
    Reading state information... Done
    The following extra packages will be installed:
      libltdl-dev
    Suggested packages:
      libtool-doc gfortran fortran95-compiler gcj
    The following NEW packages will be installed:
      libltdl-dev libtool
    
    ... snip ...
    
    Setting up libltdl-dev (2.4.2-1ubuntu1) ...
    Setting up libtool (2.4.2-1ubuntu1) ...

在解决了以上问题后，我们运行configure并选择安装目录。

    
    
    doyler@slae:~/libemu$ ./configure --prefix=/opt/libemu
    checking for a BSD-compatible install... /usr/bin/install -c
    
    ... snip ...
    
    config.status: executing depfiles commands
    config.status: executing libtool commands
    
    *** libemu configuration ***
    
    debug                              : yes
    
    bindings
    - python                          : no
    
    support
    - cargos                          : no

这一次autoreconf可以正常工作了。设置正确的make文件。

    
    
    doyler@slae:~/libemu$ autoreconf -v -i
    autoreconf: Entering directory `.'
    autoreconf: configure.ac: not using Gettext
    autoreconf: running: aclocal
    autoreconf: configure.ac: tracing
    autoreconf: running: libtoolize --install --copy
    libtoolize: putting auxiliary files in `.'.
    libtoolize: copying file `./config.guess'
    libtoolize: copying file `./config.sub'
    libtoolize: copying file `./install-sh'
    libtoolize: copying file `./ltmain.sh'
    libtoolize: Consider adding `AC_CONFIG_MACRO_DIR([m4])' to configure.ac and
    libtoolize: rerunning libtoolize, to keep the correct libtool macros in-tree.
    libtoolize: Consider adding `-I m4' to ACLOCAL_AMFLAGS in Makefile.am.
    autoreconf: running: /usr/bin/autoconf
    autoreconf: running: /usr/bin/autoheader
    autoreconf: running: automake --add-missing --copy --no-force
    configure.ac:90: installing `./compile'
    configure.ac:8: installing `./missing'
    src/Makefile.am: installing `./depcomp'
    autoreconf: Leaving directory `.'

最后，我们运行make install安装工具和库！

    
    
    doyler@slae:~/libemu$ sudo make install
    Making install in src
    make[1]: Entering directory `/home/doyler/libemu/src'
    Making install in functions
    make[2]: Entering directory `/home/doyler/libemu/src/functions'
    
    ...
    
    make[1]: Entering directory `/home/doyler/libemu'
    make[2]: Entering directory `/home/doyler/libemu'
    make[2]: Nothing to be done for `install-exec-am'.
    test -z "/usr/lib/pkgconfig" || /bin/mkdir -p "/usr/lib/pkgconfig"
    /usr/bin/install -c -m 644 libemu.pc '/usr/lib/pkgconfig'
    make[2]: Leaving directory `/home/doyler/libemu'
    make[1]: Leaving directory `/home/doyler/libemu'

##  **测试**

完成所有配置和安装后，我们来测试下该工具。

这里我使用了其包含的sctest工具，该工具可用于测试shellcode。

它为我们提供了非常棒的有关寄存器，标志和应用程序的系统调用状态输出。这与GDB非常类似，只在模拟器中完成，并且没有任何手动命令或执行。

![libemu-1-execution.png](https://image.3001.net/images/20180724/153238488959.png!small)

另外，在底部还有一些更有价值的输出。如你所见，模拟器会对系统调用及其参数执行分析，并将其作为一些C伪代码（pseudo-code）提供！如果你想要复制或更改一个shellcode，除了更好地理解它之外，这非常有用。

    
    
    int socket (
         int domain = 2;
         int type = 1;
         int protocol = 0;
    ) =  14;
    int bind (
         int sockfd = 14;
         struct sockaddr_in * my_addr = 0x00416fc2 => 
             struct   = {
                 short sin_family = 2;
                 unsigned short sin_port = 23569 (port=4444);
                 struct in_addr sin_addr = {
                     unsigned long s_addr = 0 (host=0.0.0.0);
                 };
                 char sin_zero = "       ";
             };
         int addrlen = 16;
    ) =  0;
    int listen (
         int s = 14;
         int backlog = 0;
    ) =  0;
    int accept (
         int sockfd = 14;
         sockaddr_in * addr = 0x00000000 => 
             none;
         int addrlen = 0x00000010 => 
             none;
    ) =  19;
    int dup2 (
         int oldfd = 19;
         int newfd = 14;
    ) =  14;
    
    ... snip ...
    
    int execve (
         const char * dateiname = 0x00416fb2 => 
               = "/bin//sh";
         const char * argv[] = [
               = 0x00416faa => 
                   = 0x00416fb2 => 
                       = "/bin//sh";
               = 0x00000000 => 
                 none;
         ];
         const char * envp[] = 0x00000000 => 
             none;
    ) =  0;

##  **总结**

虽然现在我并没有使用该工具，但其sctool是我打算以后会常用的。此外，在测试当中我也经常需要对某些MSF
shellcode进行分析。除了使用标准的ndisasm和GDB之外，Libemu也让我有了更多的选择。如果你有任何其它用途，或使用库功能编写了任何脚本，那么欢迎你与我联系并将它分享给我！

 ** *参考来源：[doyler](https://www.doyler.net/security-not-included/libemu-installation)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

