****

[](https://youtu.be/ug5ZuezbD3c)

****

**X Brute Forcer是一款支持对多种常见CMS实施密码爆破攻击的工具。目前，X Brute Forcer所支持的CMS包括WordPress ,
Joomla , DruPal , OpenCart , Magento。**

 **![X Brute
Forcer：一款小巧易用的CMS密码爆破工具](https://image.3001.net/images/20180314/15209848685335.jpg!small)  
**

##  **简单爆破脚本**

> [1] WordPress （自动识别用户名）  
> [2] Joomla  
> [3] DruPal  
> [4] OpenCart  
> [5] Magento  
> [6] All （自动识别CMS）

##  **使用**

简易命令格式| 完整命令格式| 描述  
---|---|---  
-l| \--list| 站点列表  
-p| \--passwords| 密码列表  
  
##  **示例**

    
    
    perl XBruteForcer.pl -l list.txt -p passwords.txt

###  **[Linux](https://wikipedia.org/wiki/Linux) ****安装**

    
    
    git clone https://github.com/Moham3dRiahi/XBruteForcer.git
    cd XBruteForcer
    perl XBruteForcer.pl -l list.txt -p passwords.txt 

###  **[Android](https://wikipedia.org/wiki/Android) 安装**

下载[Termux](https://play.google.com/store/apps/details?id=com.termux)

    
    
    cpan install LWP::UserAgent
    cpan install HTTP::Request
    git clone https://github.com/Moham3dRiahi/XBruteForcer.git
    cd XBruteForcer
    perl XBruteForcer.pl -l list.txt -p passwords.txt 

### **[Windows](https://wikipedia.org/wiki/Microsoft_Windows) 安装**

    
    
    下载Perl
    下载XBruteForcer
    提取XBruteForcer到桌面
    打开CMD并输入以下命令:
    cd Desktop/XBruteForcer-master/
    perl XBruteForcer.pl -l list.txt -p passwords.txt 

***参考来源：[GitHub](https://github.com/Moham3dRiahi/XBruteForcer)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

