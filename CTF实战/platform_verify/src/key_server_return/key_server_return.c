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

#include "key_server_return.h"
// add para lib_include

RECORD(TCM_KEY_DESC,LOCAL_KEYSET) * local_keyset_get (char * name);
RECORD(TCM_KEY_DESC,REMOTE_KEYSET) * remote_keyset_get (BYTE *uuid,char * name);

BYTE external_data_store[DIGEST_SIZE];

int key_server_return_init(void * sub_proc, void * para)
{
	int ret;
	// add yorself's module init func here
	return 0;
}
int key_server_return_start(void * sub_proc, void * para)
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
			ret=proc_keymanage_cmd(sub_proc,recv_msg);
		}
        	else
        	{
	        	ret=ex_module_sendmsg(sub_proc,recv_msg);
        	}
	}
	return 0;
}

int proc_keymanage_cmd(void * sub_proc,void * recv_msg)
{
	int ret;
	RECORD(GENERAL_RETURN,STRING) * keymanage_cmd;
	ret=message_get_record(recv_msg,&keymanage_cmd,0);
	if(ret<0)
		return ret;
    printf("enter the keymanage cmd!\n");

    if(Strcmp(keymanage_cmd->name,"pcrquote")==0)
        return proc_keyreturn_pcrquote(sub_proc,keymanage_cmd,recv_msg);
}
	
RECORD(GENERAL_RETURN,UUID) * verify_output(RECORD(TCM_KEY_DESC,VERIFY_DESC) * verify_desc,
	RECORD(TCM_PIK_DESC,PCRQUOTE) * quote_report)
{
  	RECORD(GENERAL_RETURN,UUID) * verify_result;//待输出的验证结果 
  	RECORD(GENERAL_RETURN,UUID) *policy_digest; 
	TCM_PCR_COMPOSITE * pcr_result;   // 待计算的PCR值
	TCM_PCR_COMPOSITE * pcr_report;   // 报告中的PCR值
	DB_RECORD * db_record;            
	UINT32 result;
	pcr_result=Talloc0(sizeof(*pcr_result));
	result = TCM_ExInitPcrComposite(pcr_result); //对PCR值进行初始化
	if(result!=0)
		return -EINVAL;
	NAME2VALUE trust_policy[5] = {
                {"trust_boot",7},
                {"linux_kernel",11},
                {"secure_mechanism",11},
                {"secure_policy",14},
                {NULL,0},
        };

	int i;
	verify_result = Talloc0(sizeof(*verify_result));
	if(verify_result == NULL)
		return -ENOMEM;
	
	Memcpy(verify_result->return_value,verify_desc->object_uuid,DIGEST_SIZE);
	if(verify_desc->result!=0)
	{
        	verify_result->name=dup_str("sign verify fail",0);
	}
	else
	{
		// 计算PCR预期值并与报告中数值比较


		// 计算PCR预期值
		pcr_result=&(quote_report->pcrComp);
		   
		// 从报告中获取pcr值
		pcr_report=&(quote_report->pcrComp);

		// 进行比较，并根据比较结果赋值
	
	}
	return verify_result;
}

int proc_keyreturn_pcrquote(void * sub_proc,RECORD(GENERAL_RETURN,STRING) * keymanage_cmd,void * recv_msg)
{
	int ret;
	RECORD(TCM_PIK_DESC,PCRQUOTE) * quote_report;
        RECORD(TCM_KEY_DESC,VERIFY_DESC) * verify_desc;
        RECORD(GENERAL_RETURN,UUID) * verify_result;
    	MSG_EXPAND * msg_expand;
	
        printf("server: convert verify result to policy choice!\n");

        // get verify describe from message's expand  
        ret = message_remove_expand(recv_msg,TYPE_PAIR(TCM_KEY_DESC,VERIFY_DESC),
		&msg_expand);
        verify_desc=msg_expand->expand;

        // get quote report from memdb
        DB_RECORD * db_record;
                    
        db_record = memdb_find(verify_desc->object_uuid,TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE));
          
        if(db_record==NULL)
              return -EINVAL;

        quote_report = db_record->record;
        print_bin_data(quote_report->pcrComp.pcrValue,32,16);

        printf("server: get verified report, verify result is %d!\n",verify_desc->result);

	verify_result = verify_output(verify_desc,quote_report);
        printf("server: finish verify output :\n");
	if(verify_result!=NULL)
	{
        	message_add_expand_data(recv_msg,TYPE_PAIR(GENERAL_RETURN,UUID),verify_result);
	}
        printf("server: add expand data succeed\n");
        ret=ex_module_sendmsg(sub_proc,recv_msg);
    
	return ret;
}
