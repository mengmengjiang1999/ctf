**![](https://image.3001.net/images/20200331/1585646353_5e830b1150c4f.jpg!small)**

**该篇Writeup涉及的漏洞可使攻击者获得Facebook
CDN服务器中托管文件的有效URL签名，漏洞原因在于Facebook某服务端可以为任意Facebook
CDN托管文件生成有效的URL签名参数，从而形成有效的文件访问链接。**

##  漏洞概况

对于Faceboook CDN中的托管文件来说，其URL链接和对应的签名参数如以下链接所示：

>
> [https://scontent.ftun3-1.fna.fbcdn.net/v/t39.2365-6/10734332_858877080824977_1850649729_n.jpg?_nc_cat=100&_nc_sid=ad8a9d&_nc_ohc=OqjMAvXzPM4AX-> iWuw3&_nc_ht=scontent.ftun3-1.fna&oh=eb51bfb048f02e851026515680b1f94b&oe=5E922573](https://scontent.ftun3-1.fna.fbcdn.net/v/t39.2365-6/10734332_858877080824977_1850649729_n.jpg?_nc_cat=100&_nc_sid=ad8a9d&_nc_ohc=OqjMAvXzPM4AX-> iWuw3&_nc_ht=scontent.ftun3-1.fna&oh=eb51bfb048f02e851026515680b1f94b&oe=5E922573)

以上链接中的oh和oe参数分别代表了URL的签名和该签名的过期时间，如果访问该文件10734332_858877080824977_1850649729_n.jpg时未携带这两个参数，Facebook
CDN服务端将会返回“BadURL
timestamp”消息；如果携带的这两个参数错误（如替换成其它的）或是oh签名有效但超过过期时间oe，则Facebook CDN服务端会返回“URL
signature mismatch”或“URL signature expired”。

上述CDN托管文件去除附带参数后的URL链接如下：

<https://scontent.ftun3-1.fna.fbcdn.net/v/t39.2365-6/10734332_858877080824977_1850649729_n.jpg>

但仅有这个URL是不够的，肯定无法形成有效的文件访问。为此，经过测试分析，我发现了Facebook服务端/ads/tools/text_overlay_validation_with_crops/async/可以为CDN托管文件生成有效的URL签名，具体如下：

    
    
    POST /ads/tools/text_overlay_validation_with_crops/async/ 
    
        Host: [www.facebook.com](http://www.facebook.com/)
    
        __a=1&
    
        fb_dtsg=YOUR_CSRF_TOKEN&
    
        image_position_to_crops[0]={"url":"<URL> ","width":960,"height":960,"crops":[100,0,526,395]}

其中的<URL>为去除多余参数后的CDN托管文件URL。当上述POST请求发出后，Facebook
CDN服务端在响应消息中就会自动为相应的CDN托管文件加上有效的URL签名参数：oh和oe。如下：

> [https://scontent.xx.fbcdn.net/hphotos-> xap1/v/t39.2365-6/s526x395/10734332_858877080824977_1850649729_n.jpg?oh=b1fa2b10cef8aaee779dbac57f23db6f&oe=5E812361](https://scontent.xx.fbcdn.net/hphotos-> xap1/v/t39.2365-6/s526x395/10734332_858877080824977_1850649729_n.jpg?oh=b1fa2b10cef8aaee779dbac57f23db6f&oe=5E812361)

##  漏洞危害

利用该漏洞，可以访问那些已被删除或隐私设置发生变化的文件，而且，可以通过查找旧的时间戳发现文件URL，然后利用上述方法生成新的时间戳实现批量文件下载。该漏洞同样存在于Facebook内部CDN服务器interncache-frc.fbcdn.net（但即使携带有效URL签名也无法从外网访问，除非配合SSRF漏洞或其它方式）

##  漏洞上报和处理进程

> 2020.2.4 漏洞初报
>
> 2020.2.18 漏洞确认
>
> 2020.2.26 漏洞修复
>
> 2020.2.26 赏金发放

***参考来源：[ysamm](https://ysamm.com/?p=404)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

