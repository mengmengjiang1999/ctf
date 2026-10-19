## 前言

**BBPress是一款强大的WordPress论坛插件，目前BBPress被安装在超过30万个WordPress站点上。最近BBPress
<=2.6.4的版本中被曝出了一个未经身份验证的权限提升漏洞，CVSS评分为9.8。通过利用该漏洞，可以将新用户注册为BBPress论坛的管理员，从而能够进行创建/删除论坛活动、导入/导出论坛用户以及创建版主等操作。本文对该漏洞进行了详细分析。**

## 实验环境

    
    
    1.测试工具：BurpSuite v2.1
    2.目标主机：Debian9.6 x64
    3.软件版本：WordPress 5.2.2
    4.插件版本：BBPress2.6.4

## 漏洞分析

1.在分析了源码之后，发现在用户注册时调用了过滤器钩子函数add_filter，其中挂载回调函数的过滤器名称为signup_user_meta，过滤器应用时调用的回调函数为bbp_user_add_role_to_signup_meta，详细代码如下：

    
    
    add_filter( 'signup_user_meta', 'bbp_user_add_role_to_signup_meta', 10 );

2.分析步骤1在add_filter中被调用的函数bbp_user_add_role_to_signup_meta，该函数的详细代码如下：

    
    
    function bbp_user_add_role_to_signup_meta( $meta = array() ) {
    
    	$forum_role = isset( $_POST['bbp-forums-role'] )
    		? sanitize_key( $_POST['bbp-forums-role'] )
    		: bbp_get_default_role();
    
    	$roles = array_keys( bbp_get_dynamic_roles() );
    
    	if ( empty( $forum_role ) || ! in_array( $forum_role, $roles, true ) ) {
    		return $meta;
    	}
    
    	$meta['bbp_new_role'] = $forum_role;
    
    	return $meta;
    }

> 2.1函数bbp_user_add_role_to_signup_meta使用POST方式获取参数bbp-forums-> role的值，若用户通过POST方式传入了bbp-forums-role值，那么将其赋值给变量$forum_role；若未有bbp-forums-> role值传入，那么将BBPress默认的用户角色赋值给$forum_role；
>
> 2.2该函数调用bbp_get_dynamic_roles()函数，获取BBPress预定义角色的数组；
>
> 2.3接着检测$forum_role是否为空，并且检测其是否在BBPress预定义角色的数组中；
>
> 2.4由此可以推测，要破坏程序的正常逻辑，只要将有效的用户角色赋值给bbp-forums-> role，然后通过POST方式传递给WordPress站点即可。

3.函数bbp_get_dynamic_roles()
迭代BBPress角色，然后将其创建为标准化数组，再通过apply_filters创建一个名为bbp_get_dynamic_roles的过滤器，详细代码如下：

    
    
    function bbp_get_dynamic_roles() {
    
    	$to_array = array();
    	$roles    = bbpress()->roles;
    
    	foreach ( $roles as $role_id => $wp_role ) {
    		$to_array[ $role_id ] = (array) $wp_role;
    	}
    
    	return (array) apply_filters( 'bbp_get_dynamic_roles', $to_array, $roles );
    }

4.函数bbp_get_keymaster_role()将bbp_get_keymaster_role角色设置为bbp_keymaster，这表明我们只有在post请求的末尾添加bbp_keymaster，才能将定制的用户成功注册为bbp_keymaster用户，最终获取BBPress的最高等级权限，该函数的详细代码如下：

    
    
    function bbp_get_keymaster_role() {
    
    	return apply_filters( 'bbp_get_keymaster_role', 'bbp_keymaster' );
    }

## 漏洞修复

1.此漏洞在2.6.5版本中得到修复，修复后代码的不同之处主要在于函数bbp_user_add_role_to_signup_meta，其中新增调用了函数bbp_validate_registration_role(
$to_validate )，对POST传入的bbp-forums-role参数值进行了过滤，详细代码如下：

    
    
    function bbp_user_add_role_to_signup_meta( $meta = array() ) {
    
    	if ( ! empty( $meta['bbp_new_role'] ) ) {
    		return $meta;
    	}
    
    	$to_validate = ! empty( $_POST['bbp-forums-role'] ) && is_string( $_POST['bbp-forums-role'] )
    		? sanitize_key( $_POST['bbp-forums-role'] )
    		: '';
    
    	$valid_role = bbp_validate_registration_role( $to_validate );
    
    	if ( bbp_has_errors() ) {
    		return $meta;
    	}
    
    	$meta['bbp_new_role'] = $valid_role;
    
    	return $meta;
    }

2.函数bbp_validate_registration_role检测当前是否处于WordPress后台控制面板中，并且当前用户是否具有创建用户的权限，若这两个条件同时为True，那么可以创建任意角色的用户；否则只能创建默认角色的用户（默认角色为bbp_participant）。详细代码如下所示：

    
    
    function bbp_validate_registration_role( $to_validate = '' ) {
    
    	$retval = bbp_get_default_role();
    
    	if ( is_admin() && current_user_can( 'create_users' ) ) { 
    		$retval = $to_validate;   
    	}
    
    	return bbp_validate_signup_role( $retval );  
    }

3.通过函数bbp_get_default_role可以获取默认的用户角色，详细代码如下所示：

    
    
    function bbp_get_default_role( $default = 'bbp_participant' ) {
    
    	return apply_filters( 'bbp_get_default_role', get_option( '_bbp_default_role', $default ) );
    }

4.函数bbp_validate_registration_role在末尾调用了bbp_validate_signup_role( $retval
)函数，函数bbp_validate_signup_role( $retval
)主要是通过调用bbp_is_valid_role函数来验证用户角色是否合法，详细代码如下：

    
    
    function bbp_validate_signup_role( $to_validate = '' ) {
    
    	$retval = '';
    
    	if ( empty( $to_validate ) ) {
    		bbp_add_error( 'bbp_signup_role_empty', __( ' **ERROR** : Empty role.', 'bbpress' ) );
    	}
    
    	if ( ! bbp_is_valid_role( $to_validate ) ) {
    		bbp_add_error( 'bbp_signup_role_invalid', __( ' **ERROR** : Invalid role.', 'bbpress' ) );
    	}
    
    	if ( ! bbp_has_errors() ) {
    		$retval = $to_validate;
    	}
    
    	return (string) apply_filters( 'bbp_validate_signup_role', $retval, $to_validate );
    }

5.函数bbp_is_valid_role的详细代码如下：

    
    
    function bbp_is_valid_role( $role = '' ) {
    
    	$retval = false;
    
    	if ( ! empty( $role ) && is_string( $role ) ) {
    
    		$roles = array_keys( bbp_get_dynamic_roles() );
    
    		if ( ! empty( $roles ) ) {
    
    			$retval = in_array( $role, $roles, true );
    		}
    	}
    
    	return (bool) apply_filters( 'bbp_is_valid_role', $retval, $role );
    }

## 总结

关于BBPress<=2.6.4版本中的未经身份验证的权限提升漏洞的分析与修复就到这里，建议及时将BBPress升级到最新版本2.6.5。

