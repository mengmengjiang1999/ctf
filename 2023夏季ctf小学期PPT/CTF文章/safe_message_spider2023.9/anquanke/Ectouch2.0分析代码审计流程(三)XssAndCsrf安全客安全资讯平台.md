# Ectouch2.0 分析代码审计流程 (三) Xss And Csrf

阅读量 **282702**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-21 14:30:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_459_/t013c0ecb907d637952.jpg)

Ectouch2.0 分析代码审计流程 (三) Xss 和 Csrf挖掘

## 0x1 前言

​ 为了文章的续集,我在准备考试之余,按耐不住跑去继续读了下Ectouch,我感觉自己写文章有时候真的挺多废话的,so let us focus on
analysis。今天讲下如何我是如何挖掘xss的,其中因为xss和csrf关系密切,这里也会有如何挖掘csrf的过程,漏洞可能比较鸡肋,但是这文章主要重点是在分享挖掘xss思路,希望大佬勿喷,也希望大佬多多指点。

阅读此文强烈建议阅读我之前写的审计系列:

> 1.[Ectouch2.0 分析解读代码审计流程](https://www.anquanke.com/post/id/168991)
>
> 2.[Ectouch2.0 分析代码审计流程 (二) 前台SQL注入](https://www.anquanke.com/post/id/169152)

## 0x2 系统配置的一些介绍

​ (1)除了$SERVER,输入全局进行了addalshes过滤

​ (2)默认I方法获取参数会使用htmlspecialchars进行过滤

​ (4)更多内容建议从前面开始阅读

​ (5)前台绝大部分没有token保护

## 0x3 谈谈我对xss和csrf的理解

​ xss> csrf,从大角度来讲csrf能做的事情xss都能做,所谓的xss和csrf的结合,其实是有一种这样的情况,就是self-xss
这个xss不能直接触发,但是结合csrf就能达到触发的目的。 (不对的话请师傅们斧正)

## 0x4 分析下模版渲染的过程

模版处理类文件(用的应该是smarty):

`/Users/xq17/www/ecshop/upload/mobile/include/libraries/EcsTemplate.class.php`

里面声明了一系列方法和属性,用来编译模版,输出html代码。

这里不展开内容讲,直接从实际例子出发(省略模版编译过程),方便理解

但是具体还可以参考上次我写的数据库类分析那样去通读下模版类过程。

以`upload/mobile/include/apps/default/controllers/ActivityController.class.php`为例

    
    
        public function index() {
            $this->parameter(); //获取输入参数 大概内容参考前篇有
            $this->assign('page', $this->page);//这里就赋予模版变量的值
            $this->assign('size', $this->size);//先记下来
            $this->assign('sort', $this->sort);
            $this->assign('order', $this->order);
            $count = model('Activity')->get_activity_count();
            $this->pageLimit(url('index'), $this->size);
            $this->assign('pager', $this->pageShow($count));
    
            $list = model('Activity')->get_activity_info($this->size, $this->page);
            $this->assign('list', $list);
    
            $this->display('activity.dwt');//主要是跟进这里,传入了模版文件名记忆一下方便理解。
        }
    

`upload/mobile/include/apps/default/controllers/CommentController.class.php`

    
    
        protected function display($tpl = '', $cache_id = '', $return = false)
        {
            self::$view->display($tpl, $cache_id);//进入/EcsTemplate类的display函数,跟进
        }
    

//下面分析都是EcsTemplate类的内容

    
    
    function display($filename, $cache_id = '') {
            $this->_seterror++; 
            error_reporting(E_ALL ^ E_NOTICE);//除去 E_NOTICE 之外的所有错误信息
    
            $this->_checkfile = false; //设置为false 记一下
            $out = $this->fetch($filename, $cache_id);//跟进这里 $filename=activity.dwt
            .............//省略,后面继续分析
            echo $out;
        }
    
    
    
       function fetch($filename, $cache_id = '') {
          ..................................//省略
            if (strncmp($filename, 'str:', 4) == 0) {//文件名如果有str:进入下面,这里跳过
                $out = $this->_eval($this->fetch_str(substr($filename, 4)));
            } else {
                if ($this->_checkfile) {//上面设置为了false跳过
                    if (!file_exists($filename)) {
                        $filename = $this->template_dir . '/' . $filename;
                    }
                } else {
                    $filename = $this->template_dir . '/' . $filename;//拼接出绝对路径
                    //$filename=upload/mobile/themes/ecmoban_zsxn/activity.dwt
                }
    
                if ($this->direct_output) {//开始就算false,跳过
                    $this->_current_file = $filename;
    
                    $out = $this->_eval($this->fetch_str(file_get_contents($filename)));
                } else {
                    if ($cache_id && $this->caching) { //跳过这里 $cache_id=0
                        $out = $this->template_out;
                    } else { //进入下面
                        if (!in_array($filename, $this->template)) {
                            $this->template[] = $filename;//文件名赋值给template数组
                        }
    
                        $out = $this->make_compiled($filename);//跟进这里
                        .................//省略待会再回来分析
    
    
    
        function make_compiled($filename) {
            //增加文件夹存在判断 by ecmoban carson
            $compile_path = $this->compile_dir;
            if (!is_dir($compile_path)) {
                @mkdir($compile_path, 0777, true);
            }
            $name = $compile_path . '/' . basename($filename) . '.php';
            //记录下这个变量
            //$name=upload/mobile/data/caches/compiled/activity.dwt.php
            if ($this->_expires) {//初始化为0,进入else
                $expires = $this->_expires - $this->cache_lifetime;
            } else {
                $filestat = @stat($name);//获取文件统计信息
                $expires = $filestat['mtime'];//文件上次修改的时间
            }
    
            $filestat = @stat($filename);
            //$filename=upload/mobile/themes/ecmoban_zsxn/activity.dwt
    
            if ($filestat['mtime'] <= $expires && !$this->force_compile) {//比较下建立时间
                if (file_exists($name)) {
                    $source = $this->_require($name);//这里主要跟进下_require
                    if ($source == '') {
                        $expires = 0;
                    }
                } else {
                    $source = '';
                    $expires = 0;
                }
            }
            .................//省略待会分析
        }
    
    
    
    function _require($filename) {
        //upload/mobile/data/caches/compiled/activity.dwt.php
            ob_start();
            include $filename; //跟进下这个文件
            $content = ob_get_contents();//获取缓冲区内容,其实就是上面文件的内容
            ob_end_clean();
            return $content;
        }
    

进入这个文件upload/mobile/data/caches/compiled/activity.dwt.php // **这里挺重要的,也是我想讲的**

    
    
    <?php echo $this->fetch('library/page_header.lbi'); ?> //加载头部的模版
    <div class="con">
    <div style="height:4.2em;"></div>
      <header>
        <nav class="ect-nav ect-bg icon-write">
          <?php echo $this->fetch('library/page_menu.lbi'); ?>//菜单模版
        </nav>
      </header>
      <div class="bran_list" id="J_ItemList" style="opacity:1;">
          <ul class="single_item">
          </ul>
        <a href="javascript:;" class="get_more"></a> </div>
    </div>
    <?php echo $this->fetch('library/new_search.lbi'); ?> <?php echo $this->fetch('library/page_footer.lbi'); ?> //都是加载模版,原理触类旁通就行了
    <script type="text/javascript">
     //这里是我想重点讲的,就是我们注册的变量$this->_var是经过什么操作进入了html代码里面
    <?php echo url('activity/asynclist', array('page'=>$this->_var['page'], 'sort'=>$this->_var['sort'], 'order'=>$this->_var['order']));?>" , '__TPL__/images/loader.gif');
    </script> 
    <script src="__TPL__/js/TouchSlide.1.1.js"></script>
    </body>
    </html>
    

代码和实际对比下来理解

    
    
    get_asynclist("<?php echo url('activity/asynclist', array('page'=>$this->_var['page'], 'sort'=>$this->_var['sort'], 'order'=>$this->_var['order']));?>" , '__TPL__/images/loader.gif'); 
    //提取出php代码
    <?php echo url('activity/asynclist', array('page'=>$this->_var['page'], 'sort'=>$this->_var['sort'], 'order'=>$this->_var['order']));?>
    // 跟进url函数
    function url($route = 'index/index', $params = array(), $org_mode = '') {
        return U($route, $params, true, false, $org_mode); //跟进u函数 $param对应我们设置的变量
    }
    

直接显示的结果如图:

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzbqbs3vk7j32d2030q4a.jpg)

    
    
    function U($url='',$vars='',$suffix=true,$domain=false,$org_mode='') {
        // 解析URL
        $info   =  parse_url($url);
        // 解析子域名
    ......................
        // 解析参数
        if(is_string($vars)) { // aaa=1&bbb=2 转换成数组
            parse_str($vars,$vars);
        }elseif(!is_array($vars)){
            $vars = array();
        }
        if(isset($info['query'])) { // 解析地址里面参数 合并到vars
            parse_str($info['query'],$params);
            $vars = array_merge($params,$vars);
        }
    
    //url组装
        ...................
            if(!empty($vars)) { // 添加参数
                .........
        if(isset($anchor)){
            $url  .= '#'.$anchor;
        }
        if($domain) {
            $url   =  (is_ssl()?'https://':'http://').$domain.$url;
        }
        return $url;
    }
    

其实这个点如果可控的话,因为这里没有在进行处理的过程,这里`get_asynclist("`
这里很明显就是双引号闭合,如果有原生可控的$_GET等那么就是一处xss了。

不过回到`private function parameter()` 没有找到利用参数.

继续分析下去其实就是

`echo $out;` 把渲染好的模版进行输出了。

大概的模版解析流程就是这样子,

这里因为已经编译过了,所以直接是模版文件分析。

不过还是建议读下compile文件是如何生成的对应的标签变量是怎么转换的。

简单对比下:

这是模版文件,有各种标签

![](https://ws4.sinaimg.cn/large/006tNc79gy1fzc4l2at1lj321c0icgqn.jpg)

这是编译后的模版php文件

![](https://ws4.sinaimg.cn/large/006tNc79gy1fzc4s37gdaj30va0laq7z.jpg)

这里不展开讲解编译过程,不过后面研究getshell(模版注入)我会再进行分析,我的目的主要是告诉你们这样一个流程

理解的话还是需要你们自己去实践理解去debug代码。

## 0x5 谈下挖掘xss的思路

    
    
    >1. 关注点可以多从黑盒出发,文章、评论等存在富文本地方
    >
    >2. 寻找原生变量,或者I方法不调用htmlspcialchars的变量,再进去跟踪,是否直接echo或者进去了模版
    >
    >3. 寻找解码函数htmlspecialchars_decode()
    >
    >4. 寻找注册模版变量的原生变量,然后再去看模版有没有单引号包括。
    >
    >   或者反其道行之，阅读模版变量,逆向找可控。
    >
    >5. 前端代码审计,domxss,就是看下js有没有自己去进行调用,这样也可以绕过全局限制。
    

这套系统其实相对比较简单,没有那么多交互点,另一方面可能我水平比较菜(tcl)

## 0x5.5 谈下挖掘csrf的思路

​
csrf是需要交互的,最好最有效就是对后台功能点进行黑盒测试,基本用不上白盒,白盒唯一可以看看是token是不是可以伪造啥的,找的时候可以读一下验证token的代码,一般不会出现问题,这套系统前台没做token认证,这里我就不浪费时间分析这个了。

## 0x6 XSS And CSRF漏洞

####  0x6.1 前台AfficheController超级鸡肋的反射xss

直接选定前台目录,搜索`$_GET` `$_POST`

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzbsic9n03j30wg0eyn0a.jpg)

    
    
    class AfficheController extends CommonController
    {
    
        public function __construct()
        {
            parent::__construct();
        }
    
        public function index()
        {
            $ad_id = intval(I('get.ad_id'));
            if (empty($ad_id)) {
                $this->redirect(__URL__);
            }
            $act = ! empty($_GET['act']) ? I('get.act') : '';
            if ($act == 'js') {
                /* 编码转换 */
                if (empty($_GET['charset'])) {
                    $_GET['charset'] = 'UTF8';
                }
                header('Content-type: application/x-javascript; charset=' . ($_GET['charset'] == 'UTF8' ? 'utf-8' : $_GET['charset']));//这里没有单引号括起来直接拼接
    
                $url = __URL__;
    

这里其实是个 _header CRLF注入_ ,但是很可惜自从php4.1之后,php的header函数就没办法插入换行符了,

所以说这是一个很鸡肋的点,一点价值都没有,但是我想表达的是,我是如何去挖掘的。

payload:`%0a%0d<script>alert(/xq17/)</script>`

在php高版本会提示错误,不允许多个header argument之类的。

前台那种直接输出

`$_GET $_POST`我基本找了一次,很遗憾没有发现那种很常见的反射xss。

####  0x6.2 前台会员中心csrf可盗取用户账号

这套系统首先是个人中心编辑资料处:

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzby3d5gxhj30yq0u0wi0.jpg)

一般人觉得都是去修改密码那里看看,但是现在一般的程序员都会验证下原密码。

不过这里还有个设置问题答案的功能,我们可以尝试从这里入手。

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzbytfwgtkj318y0ikn3l.jpg)

很明显就没有token等类似的字样,burp生成csrf的payload。

打开访问下:

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzbyvejtjkj31bs0hgdhl.jpg)

回到ecshop页面

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzbyw0zm8lj316u0ngdjv.jpg)

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzbywbpks9j30vw0a0wf9.jpg)

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzbywhv04wj30t608i3yq.jpg)

这个点挺low的,权当分享。

还有csrf修改地址什么,基本都没有token保护,csrf挖掘应该是很简单的,其实我是觉得很多人混淆了下xss和csrf,

又刚好有这个例子,就拿来分析一波了。

###  0x6.3 前台的xss一次失败的挖掘过程

黑盒看功能点:

> 收获地址应该是经常被用于测试xss的
>
> ![](https://ws2.sinaimg.cn/large/006tNc79gy1fzc3zoy5o2j31920l4acc.jpg)

跟进代码去解读下如何存起来的:

    
    
    public function add_address() {
            if (IS_POST) {
                $address = array(
                    'user_id' => $this->user_id,
                    'address_id' => intval($_POST['address_id']),
                    'country' => I('post.country', 0, 'intval'),
                    'province' => I('post.province', 0, 'intval'),
                    'city' => I('post.city', 0, 'intval'),
                    'district' => I('post.district', 0, 'intval'),//整形不可能
                    'address' => I('post.address'),//默认htmlspecialchars过滤
                    'consignee' => I('post.consignee'),
                    'mobile' => I('post.mobile')
                );
                $token = $_SESSION['token'] = md5(uniqid());
                if($_GET['token'] == $_SESSION['token']){
                    $url = url('user/address_list');
                    ecs_header("Location: $url");
                }
                if (model('Users')->update_address($address)) {//跟进这里
                    show_message(L('edit_address_success'), L('address_list_lnk'), url('address_list'));
                }
                exit();
            }
            if(!empty($_SESSION['consignee'])){
                $consignee = $_SESSION['consignee'];
                $this->assign('consignee', $consignee);
            }
    
    
    
        function update_address($address) {
            $address_id = intval($address['address_id']);
            unset($address['address_id']);
            $this->table = 'user_address';
            if ($address_id > 0) {
                /* 更新指定记录 */
                $condition['address_id'] = $address_id;
                $condition['user_id'] = $address['user_id'];
                $this->update($condition, $address);
            } else {
                /* 插入一条新记录 */
                $this->insert($address);//这里插入了
                $address_id = M()->insert_id();
            }
            .............................
            }
    
            return true;
        }
    

执行的sql:

    
    
     (`user_id`,`country`,`province`,`city`,`district`,`address`,`consignee`,`mobile`) VALUES ('1','1','5','58','722','admin\&quot;&gt;&lt;','admin\&quot;&gt;&lt;','13888788888')
    

全局htmlspecialchars过滤一次,数据库addalshes一次。

然后我们在看是如何输出的:

    
    
     public function address_list() {
            if (IS_AJAX) {
                ......................
            }
            // 赋值于模板
            $this->assign('title', L('consignee_info'));
            $this->display('user_address_list.dwt');
        }
    

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzc5jp446ej31q0040wfh.jpg)

这里直接输出已经被转义的payload,所以造不成xss。

通过这次xss失败挖掘经历,我更加理解了,针对这个cms的挖掘思路:

> 1.变量一定不能经过htmlspecialchars(除非有解码)
>
> 2.寻找htmlspecialchars_decode()解码输出点。

针对第一个:

通过正则匹配:

`I('.*?', .*?, '[^s]+')`找出非默认值I方法,这样就不会有htmlspecialchars

但是很遗憾我没找到好的利用点。

第二个我找到了看下面分析吧

###  0x6.4 ArticleController处xss

直接搜索:`htmlspecialchars_decode`

![](https://ws4.sinaimg.cn/large/006tNc79gy1fzc6euktkjj30uc0jin0r.jpg)

这里有两处,另一处是`html_out`函数起了`htmlspecialchars_decode`的功能

分析第一处:

    
    
     public function wechat_news_info() {
            /* 文章详情 */
            $news_id = I('get.id', 0, 'intval');
            $data = $this->model->table('wechat_media')->field('title, content, file, is_show, digest')->where('id = ' . $news_id)->find(); //wechat_media表去取内容
            $data['content'] = htmlspecialchars_decode($data['content']);
            $data['image'] =  $data['is_show'] ? __URL__ . '/' . $data['file'] : '';
            $this->assign('article', $data);
            $this->assign('page_title', $data['title']);
            $this->assign('meta_keywords', $data['title']);
            $this->assign('meta_description', strip_tags($data['digest']));
    

这里就很nice,直接全局搜索`table('wechat_media')` `'wechat_media'` `pre.'wechat_media'`

看看那里可以进行插入

有两个文件出现了很多次这个按道理来说肯定会有插入:

1.`WechatController.class.php` 前台

2.`admin/controllers/WechatController.class.php` 后台

读下前台,好像没有找到插入的,那么跟下第二个文件

    
    
     /**
         * 图文回复编辑
         */
        public function article_edit()
        {
            if (IS_POST) {
              ..................//省略
                if (! empty($id)) {
                    // 删除图片
                    if ($pic_path != $data['file']) {
                        @unlink(ROOT_PATH . $pic_path);
                    }
                    $data['edit_time'] = gmtime();
                    $this->model->table('wechat_media')
                        ->data($data)
                        ->where('id = ' . $id)
                        ->update(); //这里有个更新操作
                } else {
                    $data['add_time'] = gmtime();
                    $this->model->table('wechat_media')
                        ->data($data)
                        ->insert();//这里有个插入操作
                }
                $this->message(L('edit') . L('success'), url('article'));
            }
    

那么回去继续读下省略部分看`$data`经过了什么过滤没。

    
    
     if (IS_POST) {
                $id = I('post.id');
                $data = I('post.data');
                $data['content'] = I('post.content');
                $pic_path = I('post.file_path');
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
    

很明显内容是用了I方法获取了一次,也就是htmlspecialchars了一次,关于插入其实就是底层做了个escape过滤,

没啥影响,可以看我前面的分析,所以说这里可以导致xss

**演示分析下:**

`http://127.0.0.1:8888/ecshop/upload2/upload/mobile/?m=admin&c=Wechat&a=article_edit`

![](https://ws2.sinaimg.cn/large/006tNc79gy1fzc7a4axjtj31c60l2diq.jpg)

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzc7bkninxj30ru0is7aq.jpg)

然后我们回去访问下:

`http://127.0.0.1:8888/ecshop/upload2/upload/mobile/index.php?m=default&c=article&a=wechat_news_info&id=1`

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzc7hjgs4oj315q0a4q3y.jpg)

竟然没弹框?

直接搜索数据库:

    
    
      public function wechat_news_info() {
            /* 文章详情 */
            $news_id = I('get.id', 0, 'intval');
            $data = $this->model->table('wechat_media')->field('title, content, file, is_show, digest')->where('id = ' . $news_id)->find(); //对应是这个
            $data['content'] = htmlspecialchars_decode($data['content']);
            $data['image'] =  $data['is_show'] ? __URL__ . '/' . $data['file'] : '';
            $this->assign('article', $data);
            $this->assign('page_title', $data['title']);
            $this->assign('meta_keywords', $data['title']);
            $this->assign('meta_description', strip_tags($data['digest']));
    

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzc7kr1vk2j313k07qgme.jpg)

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzc7n923agj30ni0103yl.jpg)

的确是进行了解码

那么问题就出现了存进数据库的过程,但是我后端php代码感觉没啥问题呀,

我于是在跑回去用burp抓包下提交的过程

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzc7r619zej30zm0q8tdk.jpg)

果然被我猜中了,编辑器自己又进行了一次编码,不过这是编辑器前端处理的,那么非常easy绕过

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzc7sa8fj7j30og05yt9h.jpg)

然后再去访问,ok弹框了

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzc7u8ya6jj31eo0lygng.jpg)

这个漏洞可能会觉得鸡肋,但是常见一般都会有回复功能,肯定也是这样写的,因为要安装插件啥的,这里直接用了后台来演示。

总结下这个点的成因和意义:

> 成因:
>
> 正因为编辑器有编码特性,所以程序员写了个解码函数,不过由于前端可控,导致绕过
>
> 意义:
>
> 这个对于挖漏洞,挖src可以多关注下是不是这样子的成因,要不然就错过了一个存储xss了。

## 0x7 预告计划

​ 现在续集来到了xss and
csrf,我为自己的坚持感到开心,通过这次从代码审计挖掘xss,也激起了我想写一篇从0到1的针对tsrc的xss挖掘漏洞系列(反射 dom
存储),一些绕过过程我感觉还是很有意思,不过需要js基础,还要问下审核能不能发表才行,不行就换家可以发表的,当作是自己挖src的学习刺激,也就是说tsrc的xss系列是我向前端审计的一种过渡,也是我下一步的方向。

## 0x8 感想

​ 这次写了比较久,可能是不太熟悉这种挖掘方式,感觉还是菜,寒假好好努力吧,在十天内,争取写完后端代码审计的大部分类型。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **xq17** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169894](/post/id/169894)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [代码审计](/tag/代码审计)

 **+1** __2赞

 __收藏

![](https://q.qlogo.cn/qqapp/101431079/FB5738D77CCE7E738CDE1AA49ED6757A/40)
xq17

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

