#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>
#include <sys/time.h>
 
#include "data_type.h"
#include "cube.h"
#include "cube_define.h"
#include "cube_record.h"

#include "user_define.h"

#include "tcm_constants.h"
#include "tcm_structures.h"
#include "tcmfunc.h"
#include "tcm_cube_struct.h"
#include "tcm_key_manage.h"
#include "tcm_key_desc.h"
#include "tcm_pik_desc.h"

#include "quote_report_emu.h"
// add para lib_include


int database_no=0;

BYTE external_data_store[DIGEST_SIZE];

int quote_report_emu_init(void * sub_proc, void * para)
{
	int ret;
	// add yorself's module init func here
	return 0;
}
int quote_report_emu_start(void * sub_proc, void * para)
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
			ret=proc_quote_emu_cmd(sub_proc,recv_msg);
		}
        	else
        	{
	        	ret=ex_module_sendmsg(sub_proc,recv_msg);
        	}
	}
	return 0;
}

int proc_quote_emu_cmd(void * sub_proc,void * recv_msg)
{
	int ret;
	RECORD(GENERAL_RETURN,STRING) * keymanage_cmd;
	ret=message_get_record(recv_msg,&keymanage_cmd,0);
	if(ret<0)
		return ret;

    	if(Strcmp(keymanage_cmd->name,"pcrquote")==0)
        	return proc_pcrquote_report_emu(sub_proc,keymanage_cmd,recv_msg);
    	return ex_module_sendmsg(sub_proc,recv_msg);
}

int proc_pcrquote_report_emu(void * sub_proc,RECORD(GENERAL_RETURN,STRING) * keymanage_cmd,void * recv_msg)
{
	int ret;
	RECORD(TCM_PIK_DESC,PCRQUOTE) * quote_report;
        RECORD(MESSAGE,INSTANCE_INFO) * instance_info;
        RECORD(GENERAL_RETURN,UUID) * quote_nonce;
	char user_name[DIGEST_SIZE];
	void * new_msg;
    	MSG_EXPAND * msg_expand;
	DB_RECORD * db_record;
	
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	

    	printf("enter pcr quote report function!\n");

        ret = message_remove_expand(recv_msg,TYPE_PAIR(GENERAL_RETURN,UUID),&msg_expand);
                // find quote_report from database
        quote_nonce = msg_expand->expand;
	db_record = memdb_find_first(TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE),"nonce",
		quote_nonce->return_value);

	if(db_record==NULL)
		return -EINVAL;
                // duplicate nonce
        quote_report=db_record->record;
        ret = message_remove_expand(recv_msg,TYPE_PAIR(MESSAGE,INSTANCE_INFO),&msg_expand);
        if(ret<0)
              return ret;
            
        ret = message_add_expand_data(recv_msg,TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE),
		quote_report);
	ret=ex_module_sendmsg(sub_proc,recv_msg);
        return ret;                             
}
