# DedeCMS组合漏洞分析

## DedeCMS代码注入漏洞(CVE-2022-36216)

### 1\. 简述

漏洞涉及文件:  
`/uploads/dede/member_toadmin.php`  
`/uploads/include/common.inc.php`  
整体流程简述:  
参数传入流程  
`/uploads/include/common.inc.php`

    
    
    1. `_RunMagicQuotes()`
    2. `addslashes($svar)`

下面的`$id` 值是通过参数传入流程传入进来的。  
`/uploads/dede/member_toadmin.php`

    
    
    1. `$arr_password[$id] = "{$timestamp}";`
    2. `$content = "json_encode($arr_password);`
    3. `$fp = fopen($filename, 'w')`
        1. `$filename = DEDEDATA.'/password.data.php';`
    5. `fwrite($fp, $content);`

漏洞代码节选:

    
    
    // /uploads/include/common.inc.php 文件处代码
    
    if (!defined('DEDEREQUEST'))
    {
        foreach(Array('_GET','_POST','_COOKIE') as $_request)
        {
            foreach($$_request as $_k => $_v)
            {
                if($_k == 'nvarname') ${$_k} = $_v;
                else ${$_k} = _RunMagicQuotes($_v);
            }
        }
    }
    
    // /uploads/include/common.inc.php 文件处代码
    function _RunMagicQuotes(&$svar)
    {
        if(!get_magic_quotes_gpc())
        {
            if( is_array($svar) )
            {
                foreach($svar as $_k => $_v) $svar[$_k] = _RunMagicQuotes($_v);
            }
            else
            {
                ...
                $svar = addslashes($svar);
            }
        }
        return $svar;
    }
    
    // /uploads/dede/member_toadmin.php
    if($dopost == "toadmin")
    {
        ...
        $filename = DEDEDATA.'/password.data.php';
        if (file_exists($filename)) {
            require_once(DEDEDATA . '/password.data.php');
            $arr_password = json_decode($str_password, true);
        }
        ...
        $arr_password[$id] = "{$timestamp}";
        $content = "<?php\r\n\$str_password='".json_encode($arr_password)."';";
        $fp = fopen($filename, 'w') or die("写入文件 $filename 失败，请检查权限！");
        fwrite($fp, $content);
        fclose($fp);
    }
    

### 2\. 分析

漏洞成因:  
在DedeCMS中, 首先会用`_RunMagicQuotes()`函数，把 `$_GET, $_POST, $_COOKIE`
这三种方式获取到的用户输入过滤一遍。

然后在`_RunMagicQuotes()`函数中, 调用了PHP内置的`addslashes()`函数将获取到的所有输入进行转义。

然后 `json_encode()` 函数会将反斜杠进行转义, 这时候单引号就逃逸了 `addslashes()`函数的过滤, 逃逸了过滤的单引号,
和最开头的单引号实现了闭合。如下图所示

![](./img/8933954351528123061.png)

闭合掉单引号之后, 利用php拼接的性质, 就能传入恶意函数了, 当 `$id` 的值为 `'.phpinfo()?>`时, 如下图所示

![](./img/1766992855511061363.png)

### 3\. 复现

1.首先打开注册会员功能  
找到本地文件`uploads/install/config.cache.inc.php`, 将里面的`$cfg_mb_open = 'N';` 改为
`$cfg_mb_open = 'Y';`。  
2.然后注册一个会员(就在主页上)

![](./img/3766049072470728668.png)

3.前往后台页面, 找到`会员 -> 注册会员列表 -> 提升`。点击`提升`按钮, 按照提示填写表格。填写完毕之后,
**暂时先不要点击`确定提升`按钮**。

![](./img/1238670826574327204.png)

![](./img/7325171617863075233.png)

4.配置好浏览器代理, 打开BurpSuit或者类似的其它工具, 开启`Proxy`模块中的`Intercept is on`。然后
**再点击上一步的`确定提升`按钮**, 这时候能够捕获到HTTP请求包, 请求体部分如下所示。

![](./img/5625511683873186556.png)

请注意这里的id参数, 这里就是漏洞触发点, 将其修改为 `3'.phpinfo()?>`, 然后将数据包`Forward` 放回去

![](./img/3628053443256488734.png)

可以看到, 恶意代码已经成功注入到 `/uploads/data/password.data.php` 文件中

![](./img/653015790226616959.png)

访问 `/uploads/data/password.data.php` 文件, 可以看到成功执行了注入进去的代码。

![](./img/1930802293201943777.png)

### 4\. 鸡肋

让我们回到最开始的那段漏洞代码片段中, 里面有一段代码是这样写的。

    
    
    <?php
    $filename = DEDEDATA.'/password.data.php';
    if (file_exists($filename)) {
        require_once(DEDEDATA . '/password.data.php');
        $arr_password = json_decode($str_password, true);
    }

这段代码, 检测了是否存在 `password.data.php` 这个文件, 如果存在的话, 则直接对`password.data.php`
文件的内容进行解码。也就是说我们没有办法再往里面注入恶意代码了。

那么问题来了，如果遇到网站已经有一个正常内容的`password.data.php`文件，这个漏洞就没有任何意义了，毕竟这个漏洞只能在没有这个文件的情况下才能触发。食之无味，弃之可惜。

## DedeCMS任意文件删除漏洞(CVE-2022-30508)

### 1\. 简述

漏洞涉及文件: `/uploads/dede/upload.php`  
漏洞具体代码:

    
    
    $delete = preg_replace("#^([.]*[/]*)*#", "", $delete);
    ...
    if ($dopost === 'delete') {
        $uploadTmp = DEDEDATA . '/uploadtmp';
    
        if (unlink($uploadTmp . '/' . $delete)) {
            echo 'success';
            exit();
        }
        echo 'fail';
    }

### 2\. 分析

漏洞成因: preg_replace()对过滤不严格，导致依然能够路径穿越。然后通过代码中的unlink()函数实现任意文件删除。

### 3\. 复现

首先在根目录下新建一个test.txt文件

![](./img/7920781972994940605.png)

由于该漏洞涉及的代码片段比较简单，直接使用内置的参数输入方式输入参数，这里选择的是`$_GET`传参  
`/uploads/dede/upload.php?dopost=delete&delete=/Rebmal/../../../test.txt`

![](./img/7469438183578811062.png)

可以看到已经成功删除了`test.txt`文件。

### 4\. 无用

这就像一个不是漏洞的漏洞，除了恶作剧好像带来不了更多的危害了。既不能获取数据，也不能获取权限。这么个无用的漏洞，能否发挥出一点用处呢？

## 组合使用, 化腐朽为神奇

回顾一下上面的两个漏洞，仔细思考一下:  
第一个任意代码注入漏洞，会在已经存在 `password.data.php` 文件的情况下失效。  
第二个任意文件删除漏洞，可以删除任意的文件。

这两个漏洞一组合，不就能无限制的进行代码注入了吗?

首先, 使用任意文件删除漏洞删除 `password.data.php` 文件。  
`/uploads/dede/upload.php?dopost=delete&delete=/Rebmal/../../password.data.php`  
然后再使用代码注入漏洞进行恶意代码写入。

这样就实现了无限制的代码注入。

