***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

前言  

 **由于笔者有个习惯，每天都会去exploit-db网站上去逛逛。最近就看到了一个WordPress插件问题导致的SQL注入漏洞，抱着好奇的心，我就开始这个漏洞的复现与分析。**

## WP AutoSuggest简介

WP AutoSuggest
这款插件在访问者输入关键字时，插件会在提交搜索查询之前通过AJAX请求在网页中显示一些建议。访问者可以通过按Enter继续搜索，或者访问者可以使用键盘箭头直接访问建议的帖子。

## 漏洞复现

首先我们得进入exploit-db网站上下载这个存在漏洞的版本的插件源码和本地搭建WordPress网站（本地搭建WordPress这里就不说了）。下载源码，如下图所示：

![1.png](https://image.3001.net/images/20181213/1544688642_5c121402c12fe.png!small)  

下载完成之后，把wp-autosuggest目录直接拖到Wordpress目录的\wp-content\plugins\下。

![2.png](https://image.3001.net/images/20181213/1544688658_5c1214120f0b3.png!small)

接着，登录后台，启用这款插件，如下图所示：

![3.png](https://image.3001.net/images/20181213/1544688671_5c12141f6a2be.png!small)

启用后，退出后台，如下图所示：

![4.png](https://image.3001.net/images/20181213/1544688680_5c12142836f45.png!small)

然后根据exploit-db网站上给出的漏洞详情，我们访问下面的URL：

    
    
    http://www.yourwebsite.com/wp-content/plugins/wp-autosuggest/autosuggest.php?wpas_action=query&wpas_keys=1
    

访问后，网页内容如下图所示：

![5.png](https://image.3001.net/images/20181213/1544688749_5c12146d8efa0.png!small)

根据exploit-db网站上给出的漏洞详情，我们也知道了wpas_keys参数存在注入，于是我们可以使用SQLMAP注入神器，对网站进行注入。SQLMAP命令如下：

    
    
    sqlmap.py -u "http://www.yourwebsite.com/wp-content/plugins/wp-autosuggest/autosuggest.php?wpas_action=query&wpas_keys=1*" --technique BT --dbms MYSQL --risk 3 --level 5 --tamper space2comment
    

一开始，笔者使用的时php5.2.17+Apache的环境，结果复现不了，头疼了半天，如下图：

![6.png](https://image.3001.net/images/20181213/1544688763_5c12147b6f4a2.png!small)

后来笔者换了一个php-5.4.45+Apache的环境，就解决了。

![7.png](https://image.3001.net/images/20181213/1544688773_5c121485bca6d.png!small)

通过SQLMAP，成功获取到服务器的一些信息，如下图所示：

![8.png](https://image.3001.net/images/20181213/1544688782_5c12148e4d962.png!small)

下图也成功跑出了当前数据库的名称。

![9.png](https://image.3001.net/images/20181213/1544688788_5c1214947bb20.png!small)

## 漏洞分析

分析WordPress插件的话还是挺容易的。文件和代码也不是很多，用Notepad++就够用啦。进入插件根目录下面就看到了autosuggest_functions.php、autosuggest.php这两个php文件。

![10.png](https://image.3001.net/images/20181213/1544688829_5c1214bdd347b.png!small)

下面是autosuggest.php文件所有代码：

    
    
    <?php
    include 'autosuggest_functions.php';
    
    $wpas_action = '';
    $wpas_keys = '';
    if(isset($_GET['wpas_action'])) {
        $wpas_action = $_GET['wpas_action'];
    }
    if (isset($_GET['wpas_keys'])) {
        $wpas_keys = $_GET['wpas_keys'];
    }
    
    
    if ($wpas_action == 'query') {
    
        require_once ('../../../wp-config.php');
    
        header('Content-Type: text/xml');
        echo '<results>';
    
        global $wpdb;
    
        $wpas_keys = str_replace(' ','%',$wpas_keys);
        $pageposts = $wpdb->get_results("SELECT * FROM $wpdb->posts WHERE (post_title LIKE '%$wpas_keys%') AND post_status = 'publish' ORDER BY post_date DESC");
        foreach ($pageposts as $post) {
            setup_postdata($post);
            echo "<rs id=\"";
            the_permalink();
            echo "\" info=\"" . autosuggest_excerpt(apply_filters('the_title', get_the_content())) . "\">";
            the_title();
            echo "</rs>";
        }
        echo '</results>';
        die();
    }
    
    define('AUTOSUGGEST_DIR', get_option('siteurl') . '/' . PLUGINDIR.'/'.dirname(plugin_basename(__FILE__)));
    
    
    function add_autosuggest_css() {
        wp_register_style('autosuggestCSS', AUTOSUGGEST_DIR . '/css/wp_autosuggest.css', null, '1', 'screen');
        wp_enqueue_style('autosuggestCSS');
    }
    
    function add_autosuggest_js() {
        wp_register_script('autosuggestJS', AUTOSUGGEST_DIR . '/js/wp.autosuggest.js', null, '1');
        wp_enqueue_script('autosuggestJS');
    }
    
    function add_autosuggest_footer_code() {
    ?>
    <script type="text/javascript">
    var autosuggest_options = {
        script: "<?php echo AUTOSUGGEST_DIR; ?>/autosuggest.php?wpas_action=query&",
        varname: "wpas_keys",
        shownoresults:true,
        noresults:"<?php echo __('No results found.'); ?>",
        timeout:15000,
        callback:autosuggestSelected,
        maxresults: <?php echo get_wpas_option('wpas_maxresults','10'); ?>
    };
    var as = new AutoSuggest('<?php echo get_wpas_option('wpas_input_id','s'); ?>', autosuggest_options);
    function autosuggestSelected(entry) {
        document.location = entry['id'];
    }
    </script>
    <?php
    }
    
    function add_autosuggest_settings() {
    ?>
    <div class="wrap">
    
        <?php
    
            $smsg = "";
            if (isset($_POST['submitoptions'])) {
                if (isset($_POST['wpas_input_id'])) {
                    update_option('wpas_input_id',$_POST['wpas_input_id']);
                }
                if (isset($_POST['wpas_maxresults'])) {
                    update_option('wpas_maxresults',$_POST['wpas_maxresults']);
                }
                ?>
    
                <div id="message" class="updated fade"><p>WP AutoSuggest settings updated.</p></div>
    
        <?php } ?>
    
        <h2>WP AutoSuggest Settings</h2>
    
        <form action="" method="post">
        <table class="form-table">
            <tr valign="top">
            <th scope="row">Search Input ID</th>
            <td>
            <input type="text" value="<?php echo get_wpas_option('wpas_input_id','s'); ?>" id="wpas_input_id" name="wpas_input_id"/><br/>
            Default value is 's' which is used with the default WordPress theme. 
            </td>
            </tr>
            <tr valign="top">
            <th scope="row">Max Results</th>
            <td>
            <input type="text" value="<?php echo get_wpas_option('wpas_maxresults','10'); ?>" id="wpas_maxresults" name="wpas_maxresults"/><br/>
            Maximum number of suggested results (10 by default).
            </td>
            </tr>
        </table>
        <p class="submit"><input type="submit" name="submitoptions" value="Update Settings" /></p>
        </form>
        </div>
    <?php
    }
    
    function add_autosuggest_menu_settings() {
        if (function_exists('add_options_page')) {
             add_options_page(
                 "WP AutoSuggest"
                 , "WP AutoSuggest"
                 , 7
                 , basename(__FILE__)
                 , 'add_autosuggest_settings');
        }
    }
    
    add_action('wp_print_scripts', 'add_autosuggest_js');
    add_action('wp_print_styles', 'add_autosuggest_css');
    add_action('wp_footer', 'add_autosuggest_footer_code');
    add_action('admin_menu', 'add_autosuggest_menu_settings');
    
    
    ?>
    

相信大家没看几行就看出了问题的所在，变量wpas_keys是直接获取GET中的wpas_keys。一点都没过滤，并且在下面代码中，变量wpas_keys也带入数据库中查询了（wpdb是wordpress操作数据库方法），于是SQL注入就产生了。

![11.png](https://image.3001.net/images/20181213/1544688839_5c1214c7c3788.png!small)

## 修复建议

1、写过滤函数，如使用正则表达式过滤传入的参数。

2、对PHP进行安全配置。等等。

## 参考资源

> <https://www.exploit-db.com/exploits/45977>

 ***本文作者：看不尽的尘埃，转载请注明来自FreeBuf.COM**

