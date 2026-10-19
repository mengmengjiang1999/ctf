# Ectouch2.0 分析代码审计流程 (四) 任意文件删除/读取(ssrf)

阅读量 **297451**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-22 14:36:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_459_/t013c0ecb907d637952.jpg)

## 0x1 前言

任意文件删除的作用其实很大,危害也很大,比如可以重装系统,然后写入配置getshell等,任意文件读取可以导致ssrf,泄漏config文件等等。这里我还是从Ectouch2.0
分析下我是如何挖掘到任意文件删除的,以及简单谈谈我在挖掘过程遭遇的失败和困难,最终得到了一些审计的绕过思路和一些利用的tips。

## 0x2 审计思路

    
    
    >1.直接搜索关键词,`file_get_contents` `unlink`  `rename`  `readfile`一些函数
    >
    >2.看下有木有过滤../,后缀限不限定等等
    >
    >3.然后就没了、没了(欢迎师傅拍砖,给骚思路)
    

## 0x3 挖掘鸡肋任意文件读取/ssrf之旅(潜伏漏洞)

首先这个标题名字有点忽悠,这个具体来说是ssrf漏洞,但是产生在了文件读取函数上,因为两者关系密切

故结合来分析下:

按步骤来:

![](https://ws4.sinaimg.cn/large/006tNc79gy1fzcbfs1wahj310k04q0t5.jpg)

![](https://ws2.sinaimg.cn/large/006tNc79gy1fzcbfzj2idj30ux0u0n38.jpg)

这里说下我是怎么找的,很简单看下后缀,看下文件名是不是有变量,然后简单看下上下文,就是搜索结果显示的那种

很容易就看出来是不是了。

比如这种限定了html后缀就没啥意义了。

![](https://ws4.sinaimg.cn/large/006tNc79gy1fzcbn16u6mj30si06eq45.jpg)

继续向下看看,发现一个有趣的点

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzcc948mhkj30qw0aijsu.jpg)

跟进这个文件:

    
    
    function get_url_image($url)
    {
        $ext = strtolower(end(explode('.', $url)));
        if($ext != "gif" && $ext != "jpg" && $ext != "png" && $ext != "bmp" && $ext != "jpeg")
        {
            return $url;
        }
    
        $name = date('Ymd');
        for ($i = 0; $i < 6; $i++)
        {
            $name .= chr(mt_rand(97, 122));
        }
        $name .= '.' . $ext;
        $target = ROOT_PATH . DATA_DIR . '/attached/afficheimg/' . $name;
    
        $tmp_file = DATA_DIR . '/attached/afficheimg/' . $name;
        $filename = ROOT_PATH . $tmp_file;
    
        $img = file_get_contents($url);
    
        $fp = @fopen($filename, "a");
        fwrite($fp, $img);
        fclose($fp);
    
        return $tmp_file;
    }
    

**这里说明下这个版本,没有搞topic专题,需要自己加上去,才能进入那个具体类的方法** (所以说这挺鸡肋的)

(我感觉未来会完善这个的点,要不然就删文件了)

要修改一些配置,才能成功调用。

    
    
        protected function checkLogin() {
            $access = array(
                'crowd' => '*', 
                'wechat' => '*', 
                'extend' => '*', 
                'upload' => '*',
                'topic' => '*',//这个是我自己加的,默认没有,也就是默认这个版本漏洞不存在
                'authorization' => '*', 
                'navigator' => '*',
                'upgrade' => '*',
                'index' => array('license', 'uploader')
            );
    

下面分析下如何利用漏洞流程:

    
    
    elseif ($_REQUEST['act'] == 'insert' || $_REQUEST['act'] == 'update')
    {
    ..........................//这些代码到了第四讲没必要去分析了,直接漏洞点
                else if (!empty($_REQUEST['url']))
                {
                    /* 来自互联网图片 不可以是服务器地址 */
                    if(strstr($_REQUEST['url'], 'http') && !strstr($_REQUEST['url'], $_SERVER['SERVER_NAME']))
                    {
                        /* 取互联网图片至本地 */
                        $topic_img = get_url_image($_REQUEST['url']);//这里进入那个漏洞函数
                    }
    
    
    
                    if(strstr($_REQUEST['url'], 'http') && !strstr($_REQUEST['url'], $_SERVER['SERVER_NAME'])) //这个是判断url是不是存在http和url不能出现$_SERVER['SERVER_NAME'],默认本机内网ip
    

很简单绕过啦 localhost,跟进漏洞函数

    
    
    function get_url_image($url)
    {
        $ext = strtolower(end(explode('.', $url)));//这个写的感觉有点佛 1.php?1.png
        if($ext != "gif" && $ext != "jpg" && $ext != "png" && $ext != "bmp" && $ext != "jpeg")
        {
            return $url; //这里限定了后缀
        }
    
        $name = date('Ymd');
        for ($i = 0; $i < 6; $i++)
        {
            $name .= chr(mt_rand(97, 122));
        }
        $name .= '.' . $ext;
        $target = ROOT_PATH . DATA_DIR . '/attached/afficheimg/' . $name;
    
        $tmp_file = DATA_DIR . '/attached/afficheimg/' . $name;
        $filename = ROOT_PATH . $tmp_file;
        骚操作
        $img = file_get_contents($url);//漏洞点
    
        $fp = @fopen($filename, "a");
        fwrite($fp, $img);//把获取的内容写在了文件上
        fclose($fp);
        return $tmp_file;
    }
    

后面就是输出图片路径了

**(0)实际操作演示**

<http://127.0.0.1:8888/ecshop/upload2/upload/mobile/admin/topic.php>

去添加个专题,burp抓包

![](https://ws4.sinaimg.cn/large/006tNc79gy1fzcvgbv7ohj30s80p8ae9.jpg)

post后去访问:

[http://127.0.0.1:8888/ecshop/upload2/upload/mobile/admin/topic.php?act=edit&topic_id=3](http://127.0.0.1:8888/ecshop/upload2/upload/mobile/admin/topic.php?act=edit&topic_id=3)

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzcuymsu8zj30ym0eeaby.jpg)

(1)

![](https://ws2.sinaimg.cn/large/006tNc79gy1fzcuz9wzluj31wm06swfj.jpg)

(2)

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzcuzj9sdlj312i07smxs.jpg)

实战利用写个脚本跑跑就好了。

####  0x3.1 分析下漏洞意义

​ 这里我说任意文件读取,file_get_contents的确支持file协议:

![](https://ws2.sinaimg.cn/large/006tNc79gy1fzcv4k0gynj316m06kjs1.jpg)

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzcv4vaklkj31xw0lg0yw.jpg)

很明显就可以感觉到问题了吧,file协议很明显处理文件名和http协议不同的,在file协议里面

?1.jpg不是参数而是当做了文件名,所以这种想读取文件内容是没办法的,看到p神的小密圈也有人问过

file_get_contents的ssrf的问题,(其实我也没深入研究,只是简单谈谈我的猜想)

回到SSRF的定义上:

> SSRF（Server-Side Request Forgery, 服务端请求伪造）利用漏洞可以发起网络请求来攻击内网服务。  
>  利用SSRF能实现以下效果:  
>  1） 扫描内网（主机信息收集，Web应用指纹识别）  
>  2） 根据所识别应用发送构造的Payload进行攻击  
>  3） Denial of service

其实任意文件读取和ssrf关系本来就很密切,区别在于比如限制协议,限制域名啥的,

file_get_content如果能访问内网资源,那么就是ssrf了,防御就是限制内网ip

file_get_content如果能控制协议或者直接文件名,那么就是任意文件读取了

不过如果文件名做了限制什么的,任意文件读取基本就不存在了,参考我上面所说的。

然后就是file_get_contents支持什么协议,

网上一些文章(感觉真的有点low,这些东西还是得去看底层代码(太菜无果),或者去看官方手册找,我没有找到):

>
>     大部分 PHP 并不会开启 fopen 的 gopher wrapper
>     file_get_contents 的 gopher 协议不能 URLencode
>     file_get_contents 关于 Gopher 的 302 跳转有 bug，导致利用失败
>     curl/libcurl 7.43 上 gopher 协议存在 bug（%00 截断），经测试 7.49 可用
>     curl_exec() //默认不跟踪跳转，
>     file_get_contents() // file_get_contents支持php://input协议
>  

经过测试理论应该支持

`https://secure.php.net/manual/zh/wrappers.php`

官方的php支持的协议,但是一些gopher,dict我测试是不行的,网上的文章真的很杂很乱,看的心情有点浮躁

(php代码审计进阶之路,深入底层,一个新方向也逐渐复现在脑海里了)

回到漏洞上:

这个漏洞的确可以 **探测内网的web服务**
,严格来说的确是个ssrf漏洞,但是ssrf至少我觉得要深入理解的话,还需要做很多工作,这篇主要是分享下挖掘思路,就不展开怎么去研究了。

下面是我在研究中的疑惑,这里简单说下(欢迎有师傅跟我探讨下何为ssrf,ssrf在php的深入理解和利用):

比如这个漏洞有没有绕过后缀限制达到任意读取文件的可能？

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzcwxhhdbnj31tw0ik0xr.jpg)

![](https://ws2.sinaimg.cn/large/006tNc79gy1fzcwxmhy8sj30s403ygn1.jpg)

关于ssrf的利用,推荐篇文章:

[腾讯某处SSRF漏洞(非常好的利用点)附利用脚本](https://_thorns.gitbooks.io/sec/content/teng_xun_mou_chu_ssrf_lou_6d1e28_fei_chang_hao_de_.html)

关于ssrf的挖掘,推荐phpoop大佬的一个文章:

[混低保-MetInfo系统中隐藏的一处旧插件导致的ssrf](https://xz.aliyun.com/t/2686)

## 0x4 WechatController 任意文件删除

​ 思路同上,搜索关键词:`unlink`

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzcx5vha5rj30u00oon1a.jpg)

跟进去看看

    
    
        public function article_edit()
        {
            if (IS_POST) {
                $id = I('post.id');
                $data = I('post.data');
                $data['content'] = I('post.content');
                $pic_path = I('post.file_path');//输入
                // 封面处理
                if ($_FILES['pic']['name']) {
                    $result = $this->ectouchUpload('pic', 'wechat');
                    if ($result['error'] > 0) {
                        $this->message($result['message'], NULL, 'error');
                    }
                    $data['file'] = substr($result['message']['pic']['savepath'], 2) . $result['message']['pic']['savename'];
                    $data['file_name'] = $result['message']['pic']['name'];
                    $data['size'] = $result['message']['pic']['size'];
                } else {
                    $data['file'] = $pic_path;
                }
                $rs = Check::rule(array(
                    Check::must($data['title']),
                    L('title') . L('empty')
                ), array(
                    Check::must($data['file']),
                    L('please_upload')
                ), array(
                    Check::must($data['content']),
                    L('content') . L('empty')
                ), array(
                    Check::url($data['link']),
                    L('link_err')
                ));
                if ($rs !== true) {
                    $this->message($rs, NULL, 'error');
                }
    
                $data['wechat_id'] = $this->wechat_id;
                $data['type'] = 'news';
    
                if (! empty($id)) {
                    // 删除图片
                    if ($pic_path != $data['file']) {
                        @unlink(ROOT_PATH . $pic_path); //漏洞点
                    }
                    $data['edit_time'] = gmtime();
                    $this->model->table('wechat_media')
                        ->data($data)
                        ->where('id = ' . $id)
                        ->update();
                } else {
                    $data['add_time'] = gmtime();
                    $this->model->table('wechat_media')
                        ->data($data)
                        ->insert();
                }
                $this->message(L('edit') . L('success'), url('article'));
            }
            $id = I('get.id');
            if (! empty($id)) {
                $article = $this->model->table('wechat_media')
                    ->where('id = ' . $id)
                    ->find();
                $this->assign('article', $article);
            }
            $this->display();
        }
    

根据变量的转移流程去简化代码:

    
    
       public function article_edit()
        {
            if (IS_POST) {
                $id = I('post.id');
                $data = I('post.data');
                $data['content'] = I('post.content');
                $pic_path = I('post.file_path');//这里可控输入
                if ($_FILES['pic']['name']) {//只要存在上传表单就行了
                    $result = $this->ectouchUpload('pic', 'wechat');
                    if ($result['error'] > 0) {
                        $this->message($result['message'], NULL, 'error');
                    }
                    $data['file'] = substr($result['message']['pic']['savepath'], 2) . $result['message']['pic']['savename'];
                    $data['file_name'] = $result['message']['pic']['name'];
                    $data['size'] = $result['message']['pic']['size'];
                } else {
                    $data['file'] = $pic_path;
                }
    ...............................//中间过程肯定能满足的
                if (! empty($id)) { //这个可控
                    // 删除图片
                    if ($pic_path != $data['file']) { //
                        @unlink(ROOT_PATH . $pic_path); //漏洞点
                    }
    ....................................
            $this->display();
        }
    

直接在后台去编辑文章,burp抓包看数据流程:

`http://127.0.0.1:8888/ecshop/upload2/upload/mobile/index.php?m=admin&c=wechat&a=article_edit&id=1`

![](https://ws4.sinaimg.cn/large/006tNc79gy1fzcxvea5xlj313w04aq3j.jpg)

选定一个图片,这样`$_FILES['pic']['name']`就为test.png

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzcxzbg6mtj30um0hkjvr.jpg)

这里`[@unlink](https://github.com/unlink "@unlink")(ROOT_PATH . $pic_path);`
拼接了文件夹的目录,可以利用多个../来进行绕过

![](https://ws2.sinaimg.cn/large/006tNc79gy1fzcy09n82zj30mu03ewf1.jpg)

应该还会有其他的点,这里我就不再进行去找了,我个人觉得这种漏洞找很多点出来价值不大。

## 0x6 插入语

    
    
    向lemon师傅请教了一波,后面我会针对我的困惑,再静心去研究,另写篇文章详尽的说明,希望各位师傅能多多指点。
    

## 0x5 总结

​
不知道为什么,挖掘这两种类型漏洞的时候,我感觉很没有意思,这种漏洞拿出来写文章吧,感觉很low,感觉不知道怎么去讲,本来觉得这两种漏洞应该是很水的,但是出乎我意料的是,在审计任意文件读取的时候,激起了我想研究一番ssrf的想法。

这次审计是我觉得浪费时间比较久,感觉写起来怪怪的一次,让我感受到了php实战代码审计和ctf题目其实还是有挺大的区别的,以前我做ctf的审计题,都是一些知识点,但是实战代码审计,你会遇到很多重复,很多迷糊的东西然后感觉很枯燥,丧失了很多热情,比如这个任意文件删除吧,搜索关键词,然后去找就好了,漏洞成因很简单,拿来写文章真的感觉没什么意思,绕过方式也没啥新奇的点。

## 0x7 感想

​ 这次是我<<Ectouch2.0
分析代码审计流程>>系列写的最差的一篇,有点凑漏洞类型的嫌疑,但是我觉得把我自身在学习php代码审计流程遭遇的挫折也能表现给你们看,我感觉也是一种好事吧,因为我以前总是觉得,那些大神很厉害,轻轻松松就挖掘到了漏洞,其实我觉得吧,那些大神肯定也在学习过程中总结积累了很多经验,然后把自己内化的内容精炼的写成文章。最好,我希望这个php代码审计系列能坚持下去,是一个不断发展完善和自我提高的过程。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **xq17** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169900](/post/id/169900)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)
  * [PHP](/tag/PHP)

 **+1** __2赞

 __收藏

![](https://q.qlogo.cn/qqapp/101431079/FB5738D77CCE7E738CDE1AA49ED6757A/40)
xq17

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

