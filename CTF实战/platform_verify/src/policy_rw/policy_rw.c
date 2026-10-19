#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>
#include <sys/time.h>
 
#include "data_type.h"
#include "alloc.h"
#include "memfunc.h"
#include "basefunc.h"
#include "struct_deal.h"
#include "crypto_func.h"
#include "memdb.h"
#include "message.h"
#include "ex_module.h"
#include "return_value.h"
#include "sys_func.h"
#include "user_define.h"
#include "policy_rw.h"
// add para lib_include
BYTE Buf[DIGEST_SIZE*16];

int policy_rw_verify(void * sub_proc,void * login_data,void * msg);

int policy_rw_init(void * sub_proc, void * para)
{
	int ret;
	// add yorself's module init func here
	return 0;
}
int policy_rw_start(void * sub_proc, void * para)
{
	int ret;
	void * recv_msg;
	int type;
	int subtype;
	// add yorself's module exec func here
	while(1)
	{
		usleep(time_val.tv_usec);
		ret=ex_module_recvmsg(sub_proc,&recv_msg);
		if(ret<0)
			continue;
		if(recv_msg==NULL)
			continue;
		type=message_get_type(recv_msg);
		subtype=message_get_subtype(recv_msg);
		if(!memdb_find_recordtype(type,subtype))
		{
			printf("message format (%d %d) is not registered!\n",
			message_get_type(recv_msg),message_get_subtype(recv_msg));
			continue;
		}
		if((type==TYPE(GENERAL_RETURN))&&(subtype==SUBTYPE(GENERAL_RETURN,STRING)))
		{
			ret=proc_pcr_write(sub_proc,recv_msg);
		}
	}
	return 0;
}

int proc_pcr_write(void * sub_proc,void * recv_msg)
{
	int ret;
	RECORD(GENERAL_RETURN,STRING) * policy_cmd;
	RECORD(GENERAL_RETURN,UUID) * policy;
	RECORD(GENERAL_RETURN,BINDATA) * pcr_data;
	RECORD(GENERAL_RETURN,STRING) * pcr_write;

	void * new_msg;
    char temp_str[DIGEST_SIZE];
	
	ret=message_get_record(recv_msg,&policy_cmd,0);
	if(ret<0)
		return ret;

	pcr_data=Talloc0(sizeof(*pcr_data));
	if(pcr_data==NULL)
		return -ENOMEM;

	pcr_write=Talloc0(sizeof(*pcr_write));
	if(pcr_data==NULL)
		return -ENOMEM;


	DB_RECORD * db_record;
    int offset=0;

    
    ret = Getfiledfromstr(temp_str,policy_cmd->return_value,':',DIGEST_SIZE);
    
    pcr_write->name = dup_str("pcrwrite",0);
    pcr_write->return_value=dup_str(temp_str,0);

    pcr_data->name=dup_str("pcr_data",0);

    offset+=ret+1;

    do {
        ret = Getfiledfromstr(temp_str,policy_cmd->return_value+offset,'|',DIGEST_SIZE);
        if(ret <0)
            return ret;
        if(ret ==0)
            break;

        offset+=ret+1;
        db_record = memdb_find_first(TYPE_PAIR(GENERAL_RETURN,UUID),"name",temp_str);
        if(db_record == NULL)
        {
            print_cubeerr("policy_rw: can't find policy %s",temp_str);
            return -EINVAL;
        }
        policy=db_record->record;
        Memcpy(Buf+pcr_data->size,policy->return_value,DIGEST_SIZE);
        pcr_data->size+=DIGEST_SIZE;
    } while(ret>0);
    
    pcr_data->bindata = Talloc0(pcr_data->size);
    if(pcr_data->bindata == NULL)
        return -ENOMEM;
    Memcpy(pcr_data->bindata,Buf,pcr_data->size);

   new_msg = message_create(TYPE_PAIR(GENERAL_RETURN,STRING),recv_msg);
   if(new_msg ==NULL)
        return -EINVAL;

	ret=message_add_record(new_msg,pcr_write);
	if(ret<0)
		return ret;
	
    ret=message_add_expand_data(new_msg,TYPE_PAIR(GENERAL_RETURN,BINDATA),pcr_data);

	ret=ex_module_sendmsg(sub_proc,new_msg);
    if(ret<0)
        return -EINVAL;
    
	return ret;
}
