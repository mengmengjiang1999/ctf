# Proftpd 多个堆溢出漏洞分析

阅读量 **96250**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-12-02 14:36:03

 **x**

##### 译文声明

本文是翻译文章，文章来源：投稿

译文仅供参考，具体内容表达以及含义原文为准。

  

[漏洞概要]

近日Nicholas Lemoniast向Proftpd官方递交了三封邮件,前两封提及Proftpd
v1.3.5a版本存在多个堆溢出漏洞,最后一封则是修复该漏洞的补丁建议。

[漏洞详情]

代码片段1:

============================================  
../proftpd-master/src/pool.c:89-116  
============================================

…………………..

ret = malloc(size);

}

if (ret == NULL) {

pr_log_pri(PR_LOG_ALERT, "Out of memory!");

#ifdef PR_USE_DEVEL

if (debug_flags & PR_POOL_DEBUG_FL_OOM_DUMP_POOLS) {

pr_pool_debug_memory(oom_printf);

}

#endif

exit(1);

}

return ret;

}  
  
---  
  
Proftpd在调用malloc()函数时未对申请长度size进行校验。如果在MIPS32或ARM架构的平台中,当size为0时,malloc可能返回空指针,或者引发段错误。尽管返回Null值后会调用exit()函数,但是内存分配仍会被执行。该缺陷对于ARM或MIPS32指令架构的嵌入式平台有严重影响,甚至是可以利用的,比如OpenWRT
系统。

代码片段2:

============================================  
../proftpd-master/src/pool.c: 371-379  
============================================

static cmd_rec *fxp_cmd_alloc(pool *p, const char *name, char *arg) {

cmd_rec *cmd;

cmd = pr_cmd_alloc(p, 2, pstrdup(p, name), arg ? arg : "");

cmd->arg = arg;

return cmd;

}  
  
---  
  
fxp_cmd_alloc()在特定架构的平台中被执行时可能导致未知行为,这是内存管理缺陷问题,可能导致堆溢出或者拒绝服务攻击。

代码片段3

============================================  
../mod_sftp/ kbdint.c: 209-210  
=============================================  
buflen = bufsz = 3072;

buf = ptr = palloc(pkt->pool, bufsz);  
  
---  
  
Proftpd内存池管理时仅限制buffer的最大分配长度为3072字节,但是未对内存分配的请求数量进行限制,所以仍然存在内存分配问题,假如多个客户端同时向服务器发送请求,而且未对请求数量进行限制可能导致内存耗尽,因此每个客户端请求的最大数量不应超过500个。

代码片段5

============================================  
../../mod_sftp/fxp.c:1217-1251  
=============================================  
static struct fxp_extpair *fxp_msg_read_extpair(pool *p, unsigned char **buf,  
uint32_t *buflen) {  
uint32_t namelen, datalen;  
unsigned char *name, *data;  
struct fxp_extpair *extpair;  
namelen = sftp_msg_read_int(p, buf, buflen);  
if (*buflen < namelen) {  
(void) pr_log_writefile(sftp_logfd, MOD_SFTP_VERSION,  
"SFTP message format error: unable to read %lu bytes of extpair name "  
"data (buflen = %lu)", (unsigned long) namelen, (unsigned long) *buflen);  
SFTP_DISCONNECT_CONN(SFTP_SSH2_DISCONNECT_BY_APPLICATION, NULL);  
}  
name = palloc(p, namelen + 1);  
memcpy(name, *buf, namelen);  
(*buf) += namelen;  
(*buflen) -= namelen;  
name[namelen] = '';  
datalen = sftp_msg_read_int(p, buf, buflen);  
if (datalen > 0) {  
data = sftp_msg_read_data(p, buf, buflen, datalen);  
} else {  
data = NULL;  
}  
extpair = palloc(p, sizeof(struct fxp_extpair));  
extpair->ext_name = (char *) name;  
extpair->ext_datalen = datalen;  
extpair->ext_data = data;  
return extpair;  
}  
  
---  
  
  

  

  

[修复建议]

引入FXP_MAX_EXTENDED_ATTRIBUTES变量到mod_sftp模块中,值为1024,用于限制“扩展”项的大小。所有完成读取“扩展”项的代码处增加长度判断,如果大于1024则将错误信息记录到日志文件中,函数返回错误值。

[原文链接]

[http://www.securityfocus.com/archive/1/537001](http://www.securityfocus.com/archive/1/537001)

本文翻译自投稿 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83034](/post/id/83034)

安全客 - 有思想的安全新媒体

本文转载自: [投稿]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

