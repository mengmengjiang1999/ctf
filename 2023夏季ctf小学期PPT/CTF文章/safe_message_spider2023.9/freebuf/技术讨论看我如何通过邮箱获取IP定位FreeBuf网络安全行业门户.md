*****本文原创作者：dxkite，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

**还记得那些年，邮箱钓鱼盛行，各种广告邮件钓鱼邮件层出不穷，经过邮箱防水墙能拦截一部分以外，你是否注意到了正常邮箱可能被有心人利用的姿势？本文将用一个比较难以察觉的方式获取目标的IP。**

##  **0x00 检测邮件是否已读**

某天，工作的时候发送了一封邮件给一个比较重要的人，左等右等，心里在想，TA
看了我的邮箱没有？现在通过一个姿势来获取一下自己邮箱的已读状态吧？邮件被打开后很大几率会直接加载邮件中的图片首先，准备一台服务器，服务器的权限最好是自己有，使用一下代码：

    
    
    header('Content-Type:image/png');
    $im = imagecreatetruecolor (1,1);
    $background_color = imagecolorallocatealpha($im, 255, 255, 255, 127);
    imagepng($im);
    imagedestroy($im);

以上代码创建了一个 1x1 大小的全透明的图片（ **谁都看不到哦**
），我们把这个图片放到我们自己的服务器上，访问可以看到一张啥都没有的图片：![](https://image.3001.net/images/20181003/1538570440_5bb4b8c83c2c8.png!small)光是生成图片还不够，我们记录一下
$_SERVER['HTTP_REFERER'] 和 $_SERVER['HTTP_USER_AGENT']
这俩个存储了用户从哪里来，使用了什么用户代理（浏览器设备）过来的，最后还有 ip，我们通过如下代码获取：>
参考：<https://github.com/DXkite/suda/blob/master/system/src/suda/core/Request.php#L211>

    
    
    function get_ip()
    {
        static $ipFrom = ['HTTP_CLIENT_IP','HTTP_X_FORWARDED_FOR','HTTP_X_FORWARDED', 'HTTP_X_CLUSTER_CLIENT_IP','HTTP_FORWARDED_FOR','HTTP_FORWARDED','REMOTE_ADDR'];
        foreach ($ipFrom as $key) {
            if (array_key_exists($key, $_SERVER)) {
                foreach (explode(',', $_SERVER[$key]) as $ip) {
                    $ip = trim($ip);
                    if ((bool) filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4 | FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
                        return $ip;
                    }
                }
            }
        }
        return  '127.0.0.1';
    }

获取完以上数据后，写入到数据库中：

    
    
    $ip = get_ip();
    $from = $_SERVER['HTTP_REFERER'];
    $client = $_SERVER['HTTP_USER_AGENT'];
    // SQL 插入到数据库中
    // ...

写完以后，我们在邮件中插入我们的图片（使用 URL
插入），对方收到后可能是这样的：![](https://image.3001.net/images/20181003/1538570633_5bb4b989b2963.png!small)可以看到图片现在就是一个小黑点（命名我弄成透明的了），只要对方查看了这一封邮件，我们就可以在后台捕获这个数据。![](https://image.3001.net/images/20181003/1538570779_5bb4ba1bf2e4f.png!small)如果你对消息的时效性有要求，可以加一个短信通知（我这里用的是企鹅
SMS）![](https://image.3001.net/images/20181003/1538570952_5bb4bac86528d.png!small)在对方访问页面的时候就通知到你的手机。

## 0x01 附带的技能：IP 定位

上一步我们通过记录了对方的各种信息：

字段  |  信息内容  |  解释  
---|---|---  
HTTP_REFERER  |  <http://netease-default-url-start/> |  从来源可以看出，用户通过网易客户端打开邮件  
IP  |  117.136..  |  用户使用的出网 IP  
HTTP_USER_AGENT  |  Mozilla/5.0 (Linux; Android 8.0.0; MIX 2S
Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0
Chrome/62.0.3202.84 Mobile Safari/537.36  |  从头部分析，可以看到用户通过小米 Mix 2S 打开的邮件  
  
##
![](https://image.3001.net/images/20181003/1538571484_5bb4bcdcbc391.png!small)  
 **0x02 缺陷与防范**

> 1\. 用客户端打开邮件直接中招
>
> 2\. 网页端邮件有小部分几率屏蔽图片，但是从目前情况来看，测试了几个，腾讯，163 都没有屏蔽
>
> 3\. 除非使用代理上网，不然正常情况下定位效果还算可以
>
> 4\. 适用于检测邮件是否已读，定位 IP 纯属附带效果，但是也不容忽略（昂，定位在 TA 家，也不回复我邮件）

***本文原创作者：dxkite，本文属FreeBuf原创奖励计划，未经许可禁止转载**

