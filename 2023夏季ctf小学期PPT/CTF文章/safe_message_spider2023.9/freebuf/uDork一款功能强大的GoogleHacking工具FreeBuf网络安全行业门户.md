![](https://image.3001.net/images/20200403/1585921330_5e873d32bc505.png!small)

**uDork是一款功能强大的Google
Hacking工具，uDork本质上来说，是一个采用Python编程语言开发的脚本工具，它可以使用高级Google搜索技术来获取目标文件或目录中的数据、搜索物联网设备，或检测目标Web应用程序的版本相关信息等等。**

uDork并不会对任何服务器执行攻击行为，它只会使用预定义的Dork或exploit-db.com提供的官方列表来进行搜索和查询。

###  下面给出的是Google Hacking数据库地址：

> <https://www.exploit-db.com/google-hacking-database>

##  关于Google Hacking

Google Hacking的含义原指利用Google搜索引擎搜索信息来进行入侵的技术和行为，现指利用各种搜索引擎搜索信息来进行入侵的技术和行为。

Google
Hacking是使用搜索引擎，比如谷歌来定位因特网上的安全隐患和易攻击点。Web上一般有两种容易发现的易受攻击类型：软件漏洞和错误配置。虽然一些有经验的入侵者目标是瞄准了一些特殊的系统，同时尝试发现会让他们进入的漏洞，但是大部分的入侵者是从具体的软件漏洞开始或者是从那些普通用户错误配置开始，在这些配置中，他们已经知道怎样侵入，并且初步的尝试发现或扫描有该种漏洞的系统。谷歌对于第一种攻击者来说用处很少，但是对于第二种攻击者则发挥了重要作用。

当一个攻击者知道他想侵入的漏洞的种类，但是没有明确的目标时，他使用扫描器。扫描器是自动开始一个检查系统的绝大部分地方的过程，以便发现安全缺陷的这样一个程序。最早和电脑相关的扫描器，例如，是战争拨号器这个程序，它会拨一长串的电话号码，并且记录下和调制解调器相匹配的号码。

##  工具安装

当然了，Python环境是必须要提前搭建好的。在使用uDork之前，你还需要安装好goop：

    
    
    pip3 install goop

###  下载和安装：

    
    
    $ git clone <https://github.com/m3n0sd0n4ld/uDork>
    
        $ cd uDork

接下来，打开配置文件，并将下列代码写入：

    
    
    cookie = 'YOUR FACEBOOK COOKIES HERE'

完成后，我们就可以直接在命令行终端中切换到项目目录，并运行下列命令查看工具帮助信息了：

    
    
    $ python3 uDork.py -h

###  注意事项

> 1、为了保证工具能够正常运行，你必须使用自己的Facebook Cookie来配置uDork的cookie.py文件；
>
> 2、你必须在使用uDork的设备上保持Facebook的登录状态；

##  获取和配置Cookie

> 1、登录至facebook.com；
>
> 2、在浏览器中同时按下Ctrl+Shift+K（火狐浏览器）或Ctrl+Shift+J（Chrome浏览器），打开浏览器命令行终端；
>
> 3、在命令行中写入document.cookie，并将"c_user = content"和"xs =
> content"写入到cookie.py文件中的“cookie”变量中；
    
    
    cookie = 'c_user=XXXXXX; xs=XXXXXX'

最后，别忘了保存文件。

##  工具使用

###  工具菜单：

    
    
    $ python3 uDork.py -h
    
               _____             _    
    
              |  __ \           | |   
    
         _   _| |  | | ___  _ __| | __
    
        | | | | |  | |/ _ \| '__| |/ /
    
        | |_| | |__| | (_) | |  |   < 
    
         \__,_|_____/ \___/|_|  |_|\_\ v.2020.03.13
    
        by M3n0sD0n4ld - (@David_Uton)
    
        ----------------------------------------------------------------------------------------------------    
        usage: uDork.py [-h] [-d DOMAIN] [-e EXTENSION] [-t TEXT] [-s STRING]
    
                        [-m MASSIVE] [-l LIST] [-f FILE] [-k DORK] [-p PAGES]
    
                        [-o OUTPUT]
    
        optional arguments:
    
          -h, --help            show this help message and exit
    
          -d DOMAIN, --domain DOMAIN
    
                                Domain or IP address.
    
          -e EXTENSION, --extension EXTENSION
    
                                Search files by extension. Use 'all' to find the list
    
                                extension.
    
          -t TEXT, --text TEXT  Find text in website content.
    
          -s STRING, --string STRING
    
                                Locate text strings within the URL.
    
          -m MASSIVE, --massive MASSIVE
    
                                Attack a site with a predefined list of dorks. Review
    
                                list <-l / - list>
    
          -l LIST, --list LIST  Shows the list of predefined dorks (Exploit-DB).
    
          -f FILE, --file FILE  Use your own personalized list of dorks.
    
          -k DORK, --dork DORK  Specifies the type of dork <filetype | intext | inurl>
    
                                (Required for '<-f / - file'>).
    
          -p PAGES, --pages PAGES
    
                                Number of pages to search in Google. (By default 5
    
                                pages).
    
          -o OUTPUT, --output OUTPUT
    
                                Export results to a file.

###  搜索PDF文件样例：

    
    
    $ python3 uDork.py -d nasa.gov -e pdf
    
               _____             _    
    
              |  __ \           | |   
    
         _   _| |  | | ___  _ __| | __
    
        | | | | |  | |/ _ \| '__| |/ /
    
        | |_| | |__| | (_) | |  |   < 
    
         \__,_|_____/ \___/|_|  |_|\_\ v.2020.03.13
    
        by M3n0sD0n4ld - (@David_Uton)
    
        ----------------------------------------------------------------------------------------------------    
        [!] The results will appear below. This may take several minutes, please wait ...
    
        ----------------------------------------------------------------------------------------------------    
        Domain/IP: nasa.gov
    
        Find links with: pdf
    
        ----------------------------------------------------------------------------------------------------    
        <https://www.sti.nasa.gov/thesvol2.pdf>
    
        <https://www.sti.nasa.gov/thesvol1.pdf>
    
        <https://www.nasa.gov/pdf/220260main_Workforce_Transition_Strategy_briefing.pdf>
    
        <https://oig.nasa.gov/docs/SAR0318.pdf>
    
        <https://oig.nasa.gov/docs/FinalWrittenStatement_03_13_2013.pdf>
    
        <https://oig.nasa.gov/docs/MC-2018.pdf>
    
        <https://www.nasa.gov/centers/dryden/pdf/88798main_srfcs.pdf>
    
        <https://www.nasa.gov/specials/apollo50th/pdf/A10_PressKit.pdf>
    
        <https://www.nasa.gov/specials/apollo50th/pdf/A14_PressKit.pdf>
    
        <https://www.nasa.gov/specials/apollo50th/pdf/A07_PressKit.pdf>
    
        <https://www.nasa.gov/specials/apollo50th/pdf/A15_PressKit.pdf>
    
        <https://www.nasa.gov/specials/apollo50th/pdf/A09_PressKit.pdf>
    
        <https://www.nasa.gov/specials/apollo50th/pdf/A08_PressKit.pdf>
    
        <https://www.nasa.gov/centers/dryden/pdf/88790main_Dryden.pdf>
    
        <https://oig.nasa.gov/docs/MC-2017.pdf>
    
        ....

###  搜索单词“password”的搜索路径样例：

    
    
    $ python3 uDork.py -d nasa.gov -s password
    
               _____             _    
    
              |  __ \           | |   
    
         _   _| |  | | ___  _ __| | __
    
        | | | | |  | |/ _ \| '__| |/ /
    
        | |_| | |__| | (_) | |  |   < 
    
         \__,_|_____/ \___/|_|  |_|\_\ v.2020.03.13
    
        by M3n0sD0n4ld - (@David_Uton)
    
        ----------------------------------------------------------------------------------------------------    
        [!] The results will appear below. This may take several minutes, please wait ...
    
        ----------------------------------------------------------------------------------------------------    
        Domain/IP: nasa.gov
    
        Find links with: password
    
        ----------------------------------------------------------------------------------------------------    
        <https://www.grc.nasa.gov/its-training/best-practices/password-tips/>
    
        <https://www.grc.nasa.gov/its-training/best-practices/password-rules/>
    
        <https://www.nas.nasa.gov/hecc/support/kb/password-creation-rules_270.html>
    
        <https://www.nas.nasa.gov/hecc/support/kb/index.php%3FView%3Dentry%26EntryID%3D270%26EntryTitle%3Dpassword-creation-rules%26mobile%3D0>
    
        <https://open.nasa.gov/datanaut-accounts/password/reset/%3Fnext%3D/explore/datanauts/app/profile>
    
        <https://www.nas.nasa.gov/hecc/support/kb/i-cant-log-inmy-password-is-not-workingmy-account-is-locked_5.html>
    
        <https://www.nas.nasa.gov/hecc/support/kb/index.php%3FView%3Dentry%26EntryID%3D53%26EntryTitle%3Dtwo-step-connection-using-rsa-securid-passcode-and-nas-password%26mobile%3D0>
    
        <https://www.nas.nasa.gov/hecc/support/kb/index.php%3FView%3Dentry%26EntryID%3D8%26EntryTitle%3Dwhat-are-the-requirements-for-creating-a-password%26mobile%3D0>
    
        <https://oltaris.nasa.gov/password/new>
    
        <https://ghrc.nsstc.nasa.gov/data-publication/user/password>
    
        <https://answers.nssc.nasa.gov/app/answers/detail/a_id/6173/>~/change-launchpad-%2528idmax%2529-password
    
        <https://answers.nssc.nasa.gov/app/answers/list/search/1/kw/Password/search/1>
    
        <https://answers.nssc.nasa.gov/app/answers/list/search/1/kw/CHANGE%2520NDC%2520PASSWORD/suggested/1>
    
        <https://answers.nssc.nasa.gov/app/answers/detail/a_id/6174/>~/reset-ndc-password
    
        .....

###  Dork列表：

    
    
    $ python3 uDork.py -l list
    
               _____             _    
    
              |  __ \           | |   
    
         _   _| |  | | ___  _ __| | __
    
        | | | | |  | |/ _ \| '__| |/ /
    
        | |_| | |__| | (_) | |  |   < 
    
         \__,_|_____/ \___/|_|  |_|\_\ v.2020.03.13
    
        by M3n0sD0n4ld - (@David_Uton)
    
        ----------------------------------------------------------------------------------------------------    
         ======================== DORKS LISTING ========================
    
         admin : Access panels of all kinds (administration, login, CMS, ...)
    
         directories : Sensitive directories (drupal, wordpress, phpmyadmin ...)
    
         usernames : Find files containing user names.
    
         passwords : Find files that contain passwords.
    
         webservers: Find web servers.
    
         vulnerable_files : Find vulnerable files. 
    
         vulnerable_servers : Find vulnerable servers.
    
         error_messages : Show error messages.
    
         vulnerable_networks : Find software data on vulnerable networks.
    
         portal_logins : List portal logins.
    
         devices :  Find connected devices (printers, webcams, thermostats, ...)

###  Dorks Massive使用样例：

    
    
    $ python3 uDork.py -d nasa.gov -m admin -p 3 -o report.txt
    
               _____             _    
    
              |  __ \           | |   
    
         _   _| |  | | ___  _ __| | __
    
        | | | | |  | |/ _ \| '__| |/ /
    
        | |_| | |__| | (_) | |  |   < 
    
         \__,_|_____/ \___/|_|  |_|\_\ v.2020.03.13
    
        by M3n0sD0n4ld - (@David_Uton)
    
        ----------------------------------------------------------------------------------------------------    
        [!] The results will appear below. This may take several minutes, please wait ...
    
        ----------------------------------------------------------------------------------------------------    
        Domain/IP: nasa.gov
    
        Find links with: ADMIN/
    
        <https://asd.gsfc.nasa.gov/blueshift/index.php/author/admin/>
    
        <https://lists.hq.nasa.gov/mailman/admin>
    
        <https://lists.hq.nasa.gov/mailman/admin/LISTNAME>
    
        <https://rosetta.jpl.nasa.gov/blogs/admin>
    
        <https://dartslab.jpl.nasa.gov/qa/user/admin>
    
        <https://landsat.gsfc.nasa.gov/author/admin/page/8/>
    
        <https://rosetta.jpl.nasa.gov/blogs/admin%3Fpage%3D1>
    
        <https://www.nasa.gov/news/speeches/admin/mg_speech_collection_archive_4.html>
    
        <https://dartslab.jpl.nasa.gov/qa/user/admin/answers>
    
        <https://dartslab.jpl.nasa.gov/qa/user/admin/wall>
    
        <https://landsat.gsfc.nasa.gov/author/admin/page/14/>
    
        ....
    
        ----------------------------------------------------------------------------------------------------    
        Domain/IP: nasa.gov
    
        Find links with: AdminTools/
    
        <https://kscddms.ksc.nasa.gov/adminTools.html>
    
        ----------------------------------------------------------------------------------------------------    
        Domain/IP: nasa.gov
    
        Find links with: Server.html
    
        <https://image.msfc.nasa.gov/ChrisDocs/udfLib/Server.html>
    
        <https://www.nasa.gov/privacy/PIA-ODIN-server.html>
    
        MORE RESULTS...

##  项目地址

> uDork：【[GitHub传送门](https://github.com/m3n0sd0n4ld/uDork)】

 ***
参考来源：[m3n0sd0n4ld](https://github.com/m3n0sd0n4ld/uDork)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

