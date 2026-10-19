# 下载地址

    
    
    https://download.vulnhub.com/kioptrix/kiop2014.tar.bz2
    

# **实战演练**

使用netdiscover命令查找靶机的IP。 **靶机下载下来之后，直接运行是检测不到IP地址的，需要删除靶机原来的网卡，再重新添加网卡上去。**

![image.png](https://image.3001.net/images/20190815/1565883583_5d557cbff07b2.png)  

使用nmap查看靶机开放的端口

![image.png](https://image.3001.net/images/20190815/1565883879_5d557de707ae0.png)查看80端口

![image.png](https://image.3001.net/images/20190815/1565883996_5d557e5cae87f.png)![image.png](https://image.3001.net/images/20190815/1565884012_5d557e6c4d6c1.png)找到了一个目录

![image.png](https://image.3001.net/images/20190815/1565884044_5d557e8cbc079.png)google一下，这个版本的系统存在目录遍历漏洞，[EXP](https://www.exploit-db.com/exploits/31173)

![image.png](https://image.3001.net/images/20190815/1565884298_5d557f8a11146.png)由于这个系统是freebsd，所以可以知道apache的位置

    
    
    In FreeBSD, the main Apache HTTP Server configuration file is installed as /usr/local/etc/apache2 x /httpd.conf , where x represents the version number. This ASCII text file begins comment lines with a # . The most frequently modified directives are: ServerRoot "/usr/local"

看到配置文件，8080端口设置了一个环境变量，需要user-agent等于Mozilla/4.0，才可以访问。

![image.png](https://image.3001.net/images/20190816/1565884952_5d558218b2b94.png)正常访问8080端口，403

![image.png](https://image.3001.net/images/20190816/1565885072_5d558290924f9.png)

修改user-agent访问，找到了一个目录  
![image.png](https://image.3001.net/images/20190816/1565885226_5d55832a9d8ea.png)访问phptax目录

    
    
    root@kali:~# curl -H "User-Agent:Mozilla/4.0" http://192.168.0.106:8080/phptax/
    <html><title>PHPTAX by William L. Berggren 2003(c)</title>
    <body bgcolor='777777' link='000000' vlink='000000' alink='000000'>
    <table cellpadding='2' cellspacing='0' border='1' width='780' bgcolor='#999900'>
    <tbody><tr height='660'><td valign='top' width='280' bgcolor='#ffcc00'><img border=0 src='./pictures/phptax.png' alt='phptax'><a href='index.php?pfilez=1040pg1.tob'><img border=0 src='./pictures/1040ico1.png'alt='tiny1040'></a><a href='index.php?pfilez=1040pg1.tob&pdf=make'><img border=0 src='./pictures/makepdf2.png'alt='Make PDF'></a><a href='./data/pdf/1040pg1.pdf'><img border=0 src='./pictures/viewpdf2.png'alt='Make PDF'></a><a href='index.php?pfilez=1040pg2.tob'><img border=0 src='./pictures/1040ico2.png'alt='tiny1040'></a><a href='index.php?pfilez=1040pg2.tob&pdf=make'><img border=0 src='./pictures/makepdf2.png'alt='Make PDF'></a><a href='./data/pdf/1040pg2.pdf'><img border=0 src='./pictures/viewpdf2.png'alt='Make PDF'></a><BR><a href='index.php?pfilez=1040ab-pg1.tob'><img border=0 src='./pictures/1040icoab1.png'alt='tiny1040'></a><a href='index.php?pfilez=1040ab-pg1.tob&pdf=make'><img border=0 src='./pictures/makepdf2.png'alt='Make PDF'></a><a href='./data/pdf/1040ab-pg1.pdf'><img border=0 src='./pictures/viewpdf2.png'alt='Make PDF'></a><a href='index.php?pfilez=1040ab-pg2.tob'><img border=0 src='./pictures/1040icoab2.png'alt='tiny1040'></a><a href='index.php?pfilez=1040ab-pg2.tob&pdf=make'><img border=0 src='./pictures/makepdf2.png'alt='Make PDF'></a><a href='./data/pdf/1040ab-pg2.pdf'><img border=0 src='./pictures/viewpdf2.png'alt='Make PDF'></a><BR><a href='index.php?pfilez=1040d-pg1.tob'><img border=0 src='./pictures/1040icod1.png'alt='tiny1040'></a><a href='index.php?pfilez=1040d-pg1.tob&pdf=make'><img border=0 src='./pictures/makepdf2.png'alt='Make PDF'></a><a href='./data/pdf/1040d-pg1.pdf'><img border=0 src='./pictures/viewpdf2.png'alt='Make PDF'></a><a href='index.php?pfilez=1040d-pg2.tob'><img border=0 src='./pictures/1040icod2.png'alt='tiny1040'></a><a href='index.php?pfilez=1040d-pg2.tob&pdf=make'><img border=0 src='./pictures/makepdf2.png'alt='Make PDF'></a><a href='./data/pdf/1040d-pg2.pdf'><img border=0 src='./pictures/viewpdf2.png'alt='Make PDF'></a><BR><a href='index.php?pfilez=1040d1-pg1.tob'><img border=0 src='./pictures/1040ico1d1.png'alt='tiny1040'></a><a href='index.php?pfilez=1040d1-pg1.tob&pdf=make'><img border=0 src='./pictures/makepdf2.png'alt='Make PDF'></a><a href='./data/pdf/1040d1-pg1.pdf'><img border=0 src='./pictures/viewpdf2.png'alt='Make PDF'></a><a href='index.php?pfilez=1040d1-pg2.tob'><img border=0 src='./pictures/1040ico1d2.png'alt='tiny1040'></a><a href='index.php?pfilez=1040d1-pg2.tob&pdf=make'><img border=0 src='./pictures/makepdf2.png'alt='Make PDF'></a><a href='./data/pdf/1040d1-pg2.pdf'><img border=0 src='./pictures/viewpdf2.png'alt='Make PDF'></a><br><a href='./pictures/i1040abcde.pdf'><img border=0 src='./pictures/1040abcde.png'alt='instructions'></a><a href='index.php?pfilez=1040w2.tob'><img border=0 src='./pictures/w2worksheet.png'alt='1040w2'></a></td><td valign='top' width='510'><map name='1040pg1'>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/your.firstname' coords=94,58,225,76>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/your.lastname' coords=226,58,374,76>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/your.ssn' coords=377,58,472,76>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/spouse.firstname' coords=94,78,225,96>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/spouse.lastname' coords=226,78,374,96>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/spouse.ssn' coords=377,78,472,96>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/spouse.ssn' coords=377,78,472,96>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/homeaddress' coords=94,98,326,116>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/aptno' coords=330,98,378,116>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/citytownstatezip' coords=94,118,363,136>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/your.president' coords=378,146,413,158>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/label/spouse.president' coords=428,146,458,158>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/filingstatus/single' coords=104,159,113,168>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/filingstatus/married.jointly' coords=104,169,113,178>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/filingstatus/married.separately' coords=104,179,113,188>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/filingstatus/headofhouse' coords=296,159,305,168>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/filingstatus/qualifyingwidow' coords=296,190,305,197>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/filingstatus/headofhousehold.qualifyingchild' coords=381,178,466,187>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/filingstatus/married.separately.fullname' coords=185,190,282,198>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/filingstatus/qualifyingwidow.yearspousedied' coords=354,199,377,208>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/yourself' coords=109,208,119,217>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/spouse' coords=110,228,119,237>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/numberofchildren.livewithyou' coords=452,236,470,248>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/numberofchildren.notbecauseofdivorce' coords=452,253,470,277>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/numberofchildren.notenteredabove' coords=452,280,470,292>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/1/firstname' coords=111,258,159,267>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/1/lastname' coords=161,258,229,267>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/1/ssn' coords=231,258,302,267>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/1/relationship' coords=304,258,350,267>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/1/qualifyingchild' coords=365,257,378,266>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/2/firstname' coords=111,268,159,277>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/2/lastname' coords=161,268,229,277>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/2/ssn' coords=231,268,302,277>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/2/relationship' coords=304,268,350,277>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/2/qualifyingchild' coords=365,267,378,276>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/3/firstname' coords=111,278,159,287>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/3/lastname' coords=161,278,229,287>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/3/ssn' coords=231,278,302,287>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/3/relationship' coords=304,278,350,287>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/3/qualifyingchild' coords=365,277,378,286>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/4/firstname' coords=111,288,159,297>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/4/lastname' coords=161,288,229,297>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/4/ssn' coords=231,288,302,297>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/4/relationship' coords=304,288,350,297>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/4/qualifyingchild' coords=365,287,378,296>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/5/firstname' coords=111,298,159,307>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/5/lastname' coords=161,298,229,307>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/5/ssn' coords=231,298,302,307>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/5/relationship' coords=304,298,350,307>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/exemptions/dependents/5/qualifyingchild' coords=365,297,378,306>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/wages' coords=400,317,471,326>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/interest.taxable' coords=400,327,471,336>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/dividends' coords=400,337,471,356>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/state.taxable.refunds' coords=400,357,471,366>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/alimony' coords=400,367,471,376>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/business.income' coords=400,377,471,388>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/capital.gains' coords=400,387,471,396>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/other.gains' coords=400,397,471,406>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/ira.distributions.taxable' coords=400,407,471,416>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/pensions.taxable' coords=400,417,471,426>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/rental.realestate' coords=400,427,471,436>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/farm.income' coords=400,437,471,446>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/unemployment' coords=400,447,471,456>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/social.security.taxable' coords=400,457,471,466>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/other.income' coords=400,467,471,476>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/interest.nontaxable' coords=309,339,376,346>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/capital.gains.dnotrequired' coords=367,389,377,397>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/ira.distributions' coords=206,408,279,417>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/pensions' coords=206,418,279,427>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/income/social.security' coords=206,458,279,467>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/educator.expenses' coords=309,488,381,497>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/ira.deduction' coords=309,498,381,507>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/student.loan.interest' coords=309,508,381,517>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/tuition.fees' coords=309,518,381,527>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/archer.msa' coords=309,528,381,537>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/moving' coords=309,538,381,547>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/half.semployment.tax' coords=309,548,381,557>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/selfemployed.health.insurance' coords=309,558,381,567>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/selfemployed.sep.simple' coords=309,568,381,577>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/penalty.savings.withdraw' coords=309,578,381,587>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/alimony' coords=309,588,381,597>
    <area href='index.php?pfilez=1040pg1.tob&field=1040/adjustedgrossincome/alimony.ssn' coords=214,588,284,597>
    </map>
    <img border=0 src='drawimage.php?pfilez=1040pg1.tob' usemap='#1040pg1' alt='zzz'><br>
    </td></tr></tbody></table>
    </body></html>  
    

好像没什么东西，搜搜这个目录有没有payload，找到了

![image.png](https://image.3001.net/images/20190816/1565885655_5d5584d73fa59.png)没有python，设置不了交互式的终端

![image.png](https://image.3001.net/images/20190816/1565885842_5d558592cd740.png)freeesd9.0存在提权的[exp](https://www.exploit-db.com/exploits/28718)。用echo命令直接复制粘贴过来，`echo ' exp code ' > /tmp/exp.c`

![image.png](https://image.3001.net/images/20190816/1565886080_5d558680bd58a.png)找到flag

    
    
    cd /root
    ls
    .cshrc
    .history
    .k5login
    .login
    .mysql_history
    .profile
    congrats.txt
    folderMonitor.log
    httpd-access.log
    lazyClearLog.sh
    monitor.py
    ossec-alerts.log
    cat congrats.txt
    If you are reading this, it means you got root (or cheated).
    Congratulations either way...
    
    Hope you enjoyed this new VM of mine. As always, they are made for the beginner in 
    mind, and not meant for the seasoned pentester. However this does not mean one 
    can't enjoy them.
    
    As with all my VMs, besides getting "root" on the system, the goal is to also
    learn the basics skills needed to compromise a system. Most importantly, in my mind,
    are information gathering & research. Anyone can throw massive amounts of exploits
    and "hope" it works, but think about the traffic.. the logs... Best to take it
    slow, and read up on the information you gathered and hopefully craft better
    more targetted attacks. 
    
    For example, this system is FreeBSD 9. Hopefully you noticed this rather quickly.
    Knowing the OS gives you any idea of what will work and what won't from the get go.
    Default file locations are not the same on FreeBSD versus a Linux based distribution.
    Apache logs aren't in "/var/log/apache/access.log", but in "/var/log/httpd-access.log".
    It's default document root is not "/var/www/" but in "/usr/local/www/apache22/data".
    Finding and knowing these little details will greatly help during an attack. Of course
    my examples are specific for this target, but the theory applies to all systems.
    
    As a small exercise, look at the logs and see how much noise you generated. Of course
    the log results may not be accurate if you created a snapshot and reverted, but at least
    it will give you an idea. For fun, I installed "OSSEC-HIDS" and monitored a few things.
    Default settings, nothing fancy but it should've logged a few of your attacks. Look
    at the following files:
    /root/folderMonitor.log
    /root/httpd-access.log (softlink)
    /root/ossec-alerts.log (softlink)
    
    The folderMonitor.log file is just a cheap script of mine to track created/deleted and modified
    files in 2 specific folders. Since FreeBSD doesn't support "iNotify", I couldn't use OSSEC-HIDS 
    for this.
    The httpd-access.log is rather self-explanatory .
    Lastly, the ossec-alerts.log file is OSSEC-HIDS is where it puts alerts when monitoring certain
    files. This one should've detected a few of your web attacks.
    
    Feel free to explore the system and other log files to see how noisy, or silent, you were.
    And again, thank you for taking the time to download and play.
    Sincerely hope you enjoyed yourself.
    
    Be good...
    
    
    loneferret
    http://www.kioptrix.com
    
    
    p.s.: Keep in mind, for each "web attack" detected by OSSEC-HIDS, by
    default it would've blocked your IP (both in hosts.allow & Firewall) for
    600 seconds. I was nice enough to remove that part :)
    
    

  

