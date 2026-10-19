## 前言

五指cms由国内专业的网站内容管理系统提供商北京五指互联科技有限公司开发，是一款开源的内容管理系统，使用php5+mysql开发，但是在2017年就停止了维护，之前也披露过不少漏洞，接下来就开启挖洞之旅。

## 过程

跟进了几个文件后我们来到了coreframe/app/attachment/admin/index.php：

/**

* 目录列表方式查看

*

* @author tuzwu

* @createtime 2014-8-1 13:14:29

* @modifytime

* @param

* @return array

*/

public function dir()

{

$dir = isset($GLOBALS['dir']) && trim($GLOBALS['dir']) ?
str_replace(array('..\\\', '../', './', '.\\\'), '', trim($GLOBALS['dir'])) :
'';

$dir = str_ireplace(array('%2F', '//'), '/', $dir);

$lists = glob(ATTACHMENT_ROOT . $dir . '/' . '*');

if (!empty($lists)) rsort($lists);

$cur_dir = str_replace(array(WWW_ROOT, DIRECTORY_SEPARATOR .
DIRECTORY_SEPARATOR), array('', DIRECTORY_SEPARATOR), ATTACHMENT_ROOT . $dir .
'/');

include $this->template('dir', M);

}

在调用str_replace()函数对dir参数的输入进行过滤时，会将'..\\\', '../', './',
'.\\\'直接过滤掉，我们这里直接输入"..",目录直接遍历：

![](https://image.3001.net/images/20201103/1604404180_5fa143d42fcff5d17b67e.png!small)

![](https://image.3001.net/images/20201103/1604404195_5fa143e35b0bdd2a31b37.png!small)

光遍历没什么危害啊，也不能下载或者访问，但是WUZHI
CMS后台为了方便自带删除的功能，但是只能删除这一级目录的文件吗？带着疑问继续跟进，我们再看coreframe/app/attachment/admin/index.php的另一处：

/**

* 删除文件

*

* @author tuzwu

* @createtime

* @modifytime

* @param

* @return

*/

public function del()

{

$id = isset($GLOBALS['id']) ? $GLOBALS['id'] : '';

$url = isset($GLOBALS['url']) ? remove_xss($GLOBALS['url']) : '';

if (!$id && !$url) MSG(L('operation_failure'), HTTP_REFERER, 3000);

if ($id) {

if(!is_array($id)) {

$ids = array($id);

} else {

$ids = $id;

}

foreach($ids as $id) {

$where = array('id' => $id);

$att_info = $this->db->get_one('attachment', $where, 'usertimes,path');

if ($att_info['usertimes'] > 1) {

$this->db->update('attachment', 'usertimes = usertimes-1', $where);

}

else {

$this->my_unlink(ATTACHMENT_ROOT . $att_info['path']);

$this->db->delete('attachment', $where);

$this->db->delete('attachment_tag_index', array('att_id'=>$id));

}

}

MSG(L('delete success'), HTTP_REFERER, 1000);

}

else {

if (!$url) MSG('url del ' . L('operation_failure'), HTTP_REFERER, 3000);

$path = str_ireplace(ATTACHMENT_URL, '', $url);

if ($path) {

$where = array('path' => $path);

$att_info = $this->db->get_one('attachment', $where, 'usertimes,id');

if (empty($att_info)) {

$this->my_unlink(ATTACHMENT_ROOT . $path);

MSG(L('operation_success'), HTTP_REFERER, 3000);

}

if ($att_info['usertimes'] > 1) {

$this->db->update('attachment', 'usertimes = usertimes-1', array('id' =>
$att_info['id']));

}

else {

$this->my_unlink(ATTACHMENT_ROOT . $path);

$this->db->delete('attachment', array('id' => $att_info['id']));

MSG(L('operation_success'), HTTP_REFERER, 3000);

}

}

else {

MSG(L('operation_failure'), HTTP_REFERER, 3000);

}

}

}

对url参数的输入貌似没有做任何控制，首先我们先删除robots.txt

![](https://image.3001.net/images/20201103/1604404261_5fa14425cab488f4a65cb.png!small)

然后我们在url参数这里发现果然没有限制，可以任意文件删除。

![](https://image.3001.net/images/20201103/1604404282_5fa1443a561de0f57b8f8.png!small)

![](https://image.3001.net/images/20201103/1604404313_5fa14459d4cf6da337f30.png!small)

![](https://image.3001.net/images/20201103/1604404327_5fa14467e411daf04a036.png!small)

