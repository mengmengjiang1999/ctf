## 漏洞概述

WordPress是目前全球流行的三大内容管理系统之一，其核心模块（Core）出现漏洞的情况相对较少。近期，WordPress核心模块被披露存在一处SQL注入漏洞(CVE-2022–21661)。针对该高危漏洞，启明星辰ADLab研究员第一时间进行了详细分析和验证。

## 受影响版本

受影响的版本：WordPress < 5.8.3

## 漏洞分析

通过比较github上的源代码，可以发现漏洞的位置是clean_query函数。在5.8.2及之前的老版本中，该函数的关键代码如下。

![1646381698_6221ca8274c5c8f055241.png!small?1646381699010](https://image.3001.net/images/20220304/1646381698_6221ca8274c5c8f055241.png!small?1646381699010)

在clean_query函数中，当传递进来的$query满足以下两个条件：

  * $query['taxonomy']为空；
  * $query['filed']的值等于term_taxonomy_id。

WordPress的执行就会进入580行，调用transform_query函数。跟进该函数，满足602行，不做任何措施直接return，保持了terms的值不受改变。

![1646381989_6221cba584f664b2b69f1.png!small?1646381989782](https://image.3001.net/images/20220304/1646381989_6221cba584f664b2b69f1.png!small?1646381989782)

全局搜索clean_query，其被get_sql_for_clause函数调用。阅读该方法的代码可知，它的功能是为sql查询中的条件创建子句。具体来说，它的工作是处理接收到的数据，将这些数据组合成
SQL 查询中的条件，然后将其返回给父函数。所以，如果可以控制clean_query的返回数据，就可以控制SQL查询进行注入。

在get_sql_for_clause中可以找到$terms变量被拼接到sql语句中。

![1646382022_6221cbc643cb86abd2ea7.png!small?1646382022711](https://image.3001.net/images/20220304/1646382022_6221cbc643cb86abd2ea7.png!small?1646382022711)

从get_sql_for_clause方法继续回溯，调用栈如下：

WP_Query->__construct()  
WP_Query->query()  
WP_Query->get_posts()  
WQ_Tax_Query->get_sql()  
WQ_Tax_Query->get_sql_clauses()  
WQ_Tax_Query->get_sql_for_query()  
WQ_Tax_Query->get_sql_for_clause()  
WQ_Tax_Query->clean_query()

在get_posts()中可以找到对WQ_Tax_Query->get_sql()的调用。

![1646382039_6221cbd755cfdcd34062b.png!small?1646382039704](https://image.3001.net/images/20220304/1646382039_6221cbd755cfdcd34062b.png!small?1646382039704)

通过回溯调用栈可知，通过控制WP_Query->__construct()中的属性，就可以造成sql注入。

## 漏洞复现

通过分析WordPress的源码发现，WordPress核心代码中不存在可以触发该漏洞的调用点。为了验证该漏洞，这里使用了Ele Custom
Skin插件做漏洞复现，这也是ZDI给出的存在产生漏洞调用的插件样例。

Ele Custom Skin插件安装量在10万以上，且其存在的漏洞调用是无需登录的。该插件存在方法get_document_data()，其核心代码如下：

public function get_document_data(){  
global $wp_query;  
  
$id = $this->widget_id;  
  
$post_id = $this->post_id;  
$theme_id = $this->theme_id;  
$old_query = $wp_query->query_vars;  
  
$this->query['paged'] = $this->current_page; // we need current(next) page to
be loaded  
$this->query['post_status'] = 'publish';  
  
$wp_query = new \WP_Query($this->query);  
wp_reset_postdata();//this fixes some issues with some get_the_ID users.  
if (is_archive()){  
$post_id = $theme_id;  
}  
  
$document = \Elementor\Plugin::$instance->documents->get_doc_for_frontend(
$post_id );  
$theme_document =
\Elementor\Plugin::$instance->documents->get_doc_for_frontend( $theme_id );  
  
$data[] = $this->get_element_data($id,$theme_document->get_elements_data());  
  
// Change the current post, so widgets can use `documents->get_current`.  
\Elementor\Plugin::$instance->documents->switch_to_document( $document );  
  
ob_start();  
$document->print_elements_with_wrapper( $data );  
$content = ob_get_clean();  
echo $this->clean_response($content,$id);  
  
\Elementor\Plugin::$instance->documents->restore_document();  
$wp_query->query_vars = $query_vars;  
  
die;  
}  
全局搜索get_document_data，该方法被注册的action名字如下。

![1646382087_6221cc07b623994f7de27.png!small?1646382087954](https://image.3001.net/images/20220304/1646382087_6221cc07b623994f7de27.png!small?1646382087954)

因此，该漏洞在这个插件是存在触发路径的。开启debug功能后，构造报文即可成功注入出数据库user。

![1646382101_6221cc15a0b05df74fd8a.png!small?1646382102102](https://image.3001.net/images/20220304/1646382101_6221cc15a0b05df74fd8a.png!small?1646382102102)

  

## 流行插件分析

为了分析该漏洞的实际影响，ADLab研究员还对WordPress前100个流行插件进行了分析，发现其中2个插件也存在该漏洞。

开启debug，构造报文即可成功注入出数据库user。

![1646382306_6221cce270e7a213f9466.png!small?1646382307238](https://image.3001.net/images/20220304/1646382306_6221cce270e7a213f9466.png!small?1646382307238)

![1646382192_6221cc7041eb59148ad78.png!small](https://image.3001.net/images/20220304/1646382192_6221cc7041eb59148ad78.png!small)

  

## 修复方案

目前WordPress已发布升级补丁以修复漏洞，补丁获取链接：

<https://github.com/WordPress/wordpress-develop/security/advisories/GHSA-6676-cqfm-gw84>

## 参考

<https://www.zerodayinitiative.com/blog/2022/1/18/cve-2021-21661-exposing-database-info-via-wordpress-sql-injection>

  

  

启明星辰积极防御实验室（ADLab）

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员，“黑雀攻击”概念首推者。截止目前，ADLab已通过CVE累计发布安全漏洞近1100个，通过
CNVD/CNNVD累计发布安全漏洞2000余个，持续保持国际网络安全领域一流水准。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。

![1646382476_6221cd8ceb05f898c2db6.png!small?1646382477253](https://image.3001.net/images/20220304/1646382476_6221cd8ceb05f898c2db6.png!small?1646382477253)

  

  

