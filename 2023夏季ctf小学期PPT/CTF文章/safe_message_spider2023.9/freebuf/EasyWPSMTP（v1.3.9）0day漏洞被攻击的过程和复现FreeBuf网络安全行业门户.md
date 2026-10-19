***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **自己博客网站用wordpres托管着，上个月发现了一些异常。**

3.12日，邮箱爆了，收到了100多封关于网站被爆破的通知邮件。

![1-3.12日出现大量爆破.png](https://image.3001.net/images/20190424/1556088369_5cc0063157103.png!small)

那天看到也觉得不奇怪，因为之前就出现过这样的情况，每天都会有几十条爆破通知，让他们去日（佛系开站）……

可那几天邮件不断的提示音告诉我，这件事情并不是那么简单。

15日，爆破通知比前两天高了一倍，我马上登入网站查看情况，并没有发现什么异常，只是量多了而已，爆破的IP都进行了阻止。该死的是那段时间根本没空，这边跑那边跑，哪还有时间去理你这爆破。

16号爆破数量降了下来，我也就更加没有在意了，直到19号，邮件提示我网站新成员注册？？？

![2-.png](https://image.3001.net/images/20190424/1556088376_5cc00638338c1.png!small)

网站注册功能关了还能注册？这是发现自己被日了；爆破的脚步也随着用户注册成功停止了下来。

至于后来那些爆破，估计不是同一伙人，在账号注册成功后还收到大量的网站锁定通知。

根据爆破的时间分析，都在23-7这个时间段，那几天累成狗，我凌晨还和你刚吗？

直到看到这份邮件，我*****……

![3.png](https://image.3001.net/images/20190424/1556088387_5cc0064354778.png!small)

网站都不是我的网站了。

登入网站后台发现阻止的IP已经全部被清空：![4-锁定IP已经被全部清空.png](https://image.3001.net/images/20190424/1556088398_5cc0064e5c850.png!small)![5-永久阻止列表也已经被全部清空.png](https://image.3001.net/images/20190424/1556088398_5cc0064e5f37c.png!small)

攻击者最后登入时间。想想这招妙啊，还爆破啥，直接用它自己的账户登入。

![6-最后登入时间.png](https://image.3001.net/images/20190424/1556088407_5cc00657ee4d8.png!small)

我看看了日历，估计要忙到4月初。。

我赶紧关闭了网站，把网站备份了下来，用于事后分析。

## 分析

分析开始，前面一堆废话……

网站被做了一下更改：注册功能被打开。

![6-注册被打开.png](https://image.3001.net/images/20190424/1556088415_5cc0065f3e569.png!small)

发现新注册用户：![7-被注册的新账号.png](https://image.3001.net/images/20190424/1556088422_5cc0066696ab9.png!small)

网站首页地址被修改：![8-网站首页被修改.png](https://image.3001.net/images/20190424/1556088427_5cc0066b9f720.png!small)

网站首页被注入script脚本进行跳转到恶意网站，在其多个插件主题页面也发现script脚本植入跳转。![9-在文件下发现的植入的不止一个.png](https://image.3001.net/images/20190424/1556088435_5cc006738feaa.png!small)

根据网站被修改的内容和3.15日被NinTechNet最新披露WordPress WP SMTP插件出现0
day漏洞（存在于v1.3.9版本中）判断，攻击者就是利用了该0 day漏洞；

3.17日，官方更新了版本v1.3.9.1，还未更新版本的站长请及时更新！

### **漏洞分析：** 问题代码块

    
    
       function admin_init() {
    	if ( defined( 'DOING_AJAX' ) && DOING_AJAX ) {
    	    add_action( 'wp_ajax_swpsmtp_clear_log', array( $this, 'clear_log' ) );
    	    add_action( 'wp_ajax_swpsmtp_self_destruct', array( $this, 'self_destruct_handler' ) );
    	}
    	//view log file
    	if ( isset( $_GET[ 'swpsmtp_action' ] ) ) {
    	    if ( $_GET[ 'swpsmtp_action' ] === 'view_log' ) {
    		$log_file_name = $this->opts[ 'smtp_settings' ][ 'log_file_name' ];
    		if ( ! file_exists( plugin_dir_path( __FILE__ ) . $log_file_name ) ) {
    		    if ( $this->log( "Easy WP SMTP debug log file\r\n\r\n" ) === false ) {
    			wp_die( 'Can\'t write to log file. Check if plugin directory  (' . plugin_dir_path( __FILE__ ) . ') is writeable.' );
    		    };
    		}
    		$logfile = fopen( plugin_dir_path( __FILE__ ) . $log_file_name, 'rb' );
    		if ( ! $logfile ) {
    		    wp_die( 'Can\'t open log file.' );
    		}
    		header( 'Content-Type: text/plain' );
    		fpassthru( $logfile );
    		die;
    	    }
    	}
    
    	//check if this is export settings request
    	$is_export_settings = filter_input( INPUT_POST, 'swpsmtp_export_settings', FILTER_SANITIZE_NUMBER_INT );
    	if ( $is_export_settings ) {
    	    $data					 = array();
    	    $opts					 = get_option( 'swpsmtp_options', array() );
    	    $data[ 'swpsmtp_options' ]		 = $opts;
    	    $swpsmtp_pass_encrypted			 = get_option( 'swpsmtp_pass_encrypted', false );
    	    $data[ 'swpsmtp_pass_encrypted' ]	 = $swpsmtp_pass_encrypted;
    	    if ( $swpsmtp_pass_encrypted ) {
    		$swpsmtp_enc_key		 = get_option( 'swpsmtp_enc_key', false );
    		$data[ 'swpsmtp_enc_key' ]	 = $swpsmtp_enc_key;
    	    }
    	    $smtp_test_mail			 = get_option( 'smtp_test_mail', array() );
    	    $data[ 'smtp_test_mail' ]	 = $smtp_test_mail;
    	    $out				 = array();
    	    $out[ 'data' ]			 = serialize( $data );
    	    $out[ 'ver' ]			 = 1;
    	    $out[ 'checksum' ]		 = md5( $out[ 'data' ] );
    
    	    $filename = 'easy_wp_smtp_settings.txt';
    	    header( 'Content-Disposition: attachment; filename="' . $filename . '"' );
    	    header( 'Content-Type: text/plain' );
    	    echo serialize( $out );
    	    exit;
    	}
    
    	$is_import_settings = filter_input( INPUT_POST, 'swpsmtp_import_settings', FILTER_SANITIZE_NUMBER_INT );
    	if ( $is_import_settings ) {
    	    $err_msg = __( 'Error occurred during settings import', 'easy-wp-smtp' );
    	    if ( empty( $_FILES[ 'swpsmtp_import_settings_file' ] ) ) {
    		echo $err_msg;
    		wp_die();
    	    }
    	    $in_raw = file_get_contents( $_FILES[ 'swpsmtp_import_settings_file' ][ 'tmp_name' ] );
    	    try {
    		$in = unserialize( $in_raw );
    		if ( empty( $in[ 'data' ] ) ) {
    		    echo $err_msg;
    		    wp_die();
    		}
    		if ( empty( $in[ 'checksum' ] ) ) {
    		    echo $err_msg;
    		    wp_die();
    		}
    		if ( md5( $in[ 'data' ] ) !== $in[ 'checksum' ] ) {
    		    echo $err_msg;
    		    wp_die();
    		}
    		$data = unserialize( $in[ 'data' ] );
    		foreach ( $data as $key => $value ) {
    		    update_option( $key, $value );
    		}
    		set_transient( 'easy_wp_smtp_settings_import_success', true, 60 * 60 );
    		$url = admin_url() . 'options-general.php?page=swpsmtp_settings';
    		wp_safe_redirect( $url );
    		exit;
    	    } catch ( Exception $ex ) {
    		echo $err_msg;
    		wp_die();
    	    }
    	}
        }

来自easy-wp-smtp.php脚本的上述admin_init()函数在用户访问管理区域时通过admin_int挂钩运行。它用于查看/删除日志，导入/导出配置以及更新Wordpress数据库中的选项，它不检查用户功能，因此任何登入用户都可以触发它。但也可以由未经身份验证的用户执行，因为Easy
WP SMTP使用AJAX和admin_inj hook在admin-ajax.php上运行。

因此，未经身份验证的用户可以发送ajax请求，例如action = swpsmtp_clear_log，以触发上述功能并执行其代码。

## 溯源

本来想对该攻击者进行溯源，可是服务器托管在阿里云，出口用的不是独立IP，上面截图爆破的所有IP均不是攻击者的IP，更加蛋痛的是网站日志被清理的精光（没及时登入后台处理），留给我的就只剩下两个跳转域名了。

![10被劫持的网站.png](https://image.3001.net/images/20190424/1556088460_5cc0068c0f6e7.png!small)![11被劫持网站的IP.png](https://image.3001.net/images/20190424/1556088460_5cc0068c111ff.png!small)![12.png](https://image.3001.net/images/20190424/1556088460_5cc0068c18c80.png!small)![13-查询到改IP地址为钓鱼网址.png](https://image.3001.net/images/20190424/1556088460_5cc0068c70fe2.png!small)

通过IP查询这两个IP均被爆了威胁情报。现在用浏览器访问该域名都会提示钓鱼网站信息（废话，多少个wordpress被日了）。

在此插件的评论栏中，也是很多骂声，可想而知此时受攻击的网站有多少了吧。

![14-在Easy WP SMTP插件评价中
有很多人反映了网站收到攻击的影响.png](https://image.3001.net/images/20190424/1556088471_5cc0069790367.png!small)

## 复现

接下来对该漏洞进行复现。

确认一下Easy WP
SMTP版本：![15.png](https://image.3001.net/images/20190424/1556088479_5cc0069fe116c.png!small)

确认网站注册功能是否关闭：![16.png](https://image.3001.net/images/20190424/1556088497_5cc006b1f0eff.png!small)

根据网上给出的POC，创建一个文件，将一下内容写入该文件：

![18-建立POC.png](https://image.3001.net/images/20190424/1556088519_5cc006c744ced.png!small)

正常请求这个文件会返回一个0：![17-正常请求为0.png](https://image.3001.net/images/20190424/1556088528_5cc006d03306f.png!small)

上传该文件：![18-利用.png](https://image.3001.net/images/20190424/1556088533_5cc006d598ad1.png!small)

访问网站登入界面，注册功能已经被打开。尝试着注册一个账户，验证注册用户是否为管理员，注册流程和新用户注册流程一样，通过邮箱获取一封邮件。

![19.png](https://image.3001.net/images/20190424/1556088545_5cc006e146421.png!small)![20.png](https://image.3001.net/images/20190424/1556088545_5cc006e1477e9.png!small)

验证成功。

看到了devipentesting99这个用户吗？这个就是攻击者创建的用户。![21.png](https://image.3001.net/images/20190424/1556088555_5cc006eb235bd.png!small)

至此，复现结束。

“你已经是网站管理员了”，能做什么不用说了吧（删库走人）。

###  **一点小小的建议：**

> 修复被更改的文件，删除webshell（发现被上传了多个webshell）；
>
> 插件更新至最新版本，稳点版本也可以；
>
> 网站出现问题已经要及时处理排查，应急响应的重要性；
>
> 关注最新漏洞，及时更新官方推出的版本更新；
>
> 定期备份网站日志，被日后日志可能会没；
>
> 有条件可以使用WEB应用防火墙。

## 漏洞分析参考链接

<https://blog.nintechnet.com/critical-0day-vulnerability-fixed-in-wordpress-easy-wp-smtp-plugin/>

<https://www.wordfence.com/blog/2019/03/hackers-abusing-recently-patched-vulnerability-in-easy-wp-smtp-plugin/>

 ***本文作者：timneh，转载请注来自FreeBuf.COM**

