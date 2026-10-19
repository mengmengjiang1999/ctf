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

#include "key_manage.h"
// add para lib_include

RECORD(TCM_KEY_DESC,LOCAL_KEYSET) * local_keyset_get (char * name);
RECORD(TCM_KEY_DESC,REMOTE_KEYSET) * remote_keyset_get (BYTE *uuid,char * name);

BYTE external_data_store[DIGEST_SIZE];

int key_manage_init(void * sub_proc, void * para)
{
	int ret;
	// add yorself's module init func here
	return 0;
}
int key_manage_start(void * sub_proc, void * para)
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

    if(Strcmp(keymanage_cmd->name,"localkeyset_gen")==0)
        return proc_keymanage_return(sub_proc,keymanage_cmd,recv_msg);
    else if(Strcmp(keymanage_cmd->name,"remotekey_send")==0)
        return proc_keymanage_keysend(sub_proc,keymanage_cmd,recv_msg);
    else if(Strcmp(keymanage_cmd->name,"pcrquote")==0)
        return proc_keymanage_pcrquote(sub_proc,keymanage_cmd,recv_msg);
    return ex_module_sendmsg(sub_proc,recv_msg);
}
	
int proc_keymanage_return(void * sub_proc,RECORD(GENERAL_RETURN,STRING) * keymanage_cmd,void * recv_msg)
{
	int ret;
	RECORD(MESSAGE,INSTANCE_INFO) * instance_info;
	char user_name[DIGEST_SIZE];
	void * new_msg;
    MSG_EXPAND * msg_expand;
	
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	

    print_cubeaudit("enter keymanage_return function!");

	ret = message_remove_expand(recv_msg,TYPE_PAIR(MESSAGE,INSTANCE_INFO),&msg_expand);
	if(ret<0)
		return ret;
	if(msg_expand==NULL)
		return -ENOMEM;
    instance_info=msg_expand->expand;
    if(instance_info==NULL)
        return -EINVAL;
	
	proc_share_data_getvalue("uuid",local_uuid);
    if(Memcmp(local_uuid,instance_info->node_uuid,DIGEST_SIZE)!=0)
        return -EINVAL;
    Memset(instance_info->node_uuid,0,DIGEST_SIZE);

    print_cubeaudit("user name is %s!",instance_info->user_name);
	//proc_share_data_getvalue("proc_name",instance_info->proc_name);

	new_msg=message_create(TYPE_PAIR(MESSAGE,INSTANCE_INFO),recv_msg);	
	if(new_msg==NULL)
		return -EINVAL;
	ret=message_add_record(new_msg,instance_info);
	if(ret<0)
		return ret;
	
	ret=ex_module_sendmsg(sub_proc,new_msg);
	return ret;
}

int proc_keymanage_keysend(void * sub_proc,RECORD(GENERAL_RETURN,STRING) * keymanage_cmd,void * recv_msg)
{
	int ret;
	RECORD(MESSAGE,INSTANCE_INFO) * instance_info;
	char user_name[DIGEST_SIZE];
	void * new_msg;
    MSG_EXPAND * msg_expand;
	
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	

    ret = message_get_define_expand(recv_msg,&msg_expand,TYPE_PAIR(MESSAGE,INSTANCE_INFO));
	if(ret<0)
        return ret;
    if(msg_expand==NULL)
        return 0;
    instance_info=msg_expand->expand;

	new_msg=message_create(TYPE_PAIR(MESSAGE,INSTANCE_INFO),recv_msg);	
//	ret=message_add_expand_data(recv_msg,TYPE_PAIR(MESSAGE,INSTANCE_INFO),instance_info);	
//	if(ret<0)
//		return ret;
	ret=message_add_record(new_msg,instance_info);
	if(ret<0)
		return ret;	
	ret=ex_module_sendmsg(sub_proc,new_msg);
	return ret;
}

int proc_keymanage_pcrquote(void * sub_proc,RECORD(GENERAL_RETURN,STRING) * keymanage_cmd,void * recv_msg)
{
	int ret;
	RECORD(TCM_PIK_DESC,PCRQUOTE) * quote_report;
	char user_name[DIGEST_SIZE];
	void * new_msg;
    MSG_EXPAND * msg_expand;
	
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	

    printf("enter pcr quote function!\n");

    ret = message_get_define_expand(recv_msg,&msg_expand,TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE));
	if(ret<0)
        return ret;
        // check if we get quote report 
    if(msg_expand==NULL)
    {
        printf("check if pcr get nonce function!\n");
        ret = message_get_define_expand(recv_msg,&msg_expand,TYPE_PAIR(TCM_KEY_DESC,VERIFY_DESC));
        // check if we get verify result 
        if(msg_expand == NULL)
        {
            // check if there exists random data 
            ret = message_remove_expand(recv_msg,TYPE_PAIR(GENERAL_RETURN,UUID),&msg_expand);
            if(msg_expand == NULL)
            {
                // generate external random data
                RECORD(GENERAL_RETURN,UUID) * external_data;
                external_data=Talloc0(sizeof(*external_data));
                external_data->name=dup_str("pcrquote",0);
                RAND_bytes(external_data->return_value,DIGEST_SIZE);
                Memcpy(external_data_store,external_data->return_value,DIGEST_SIZE);
                ret = message_add_expand_data(recv_msg,TYPE_PAIR(GENERAL_RETURN,UUID),external_data);
	            ret=ex_module_sendmsg(sub_proc,recv_msg);
            }
            else
            {
                
                RECORD(MESSAGE,INSTANCE_INFO) * instance_info;
                // create quote_report struct
                RECORD(TCM_PIK_DESC,PCRQUOTE) * quote_report;
                quote_report = Talloc0(sizeof(*quote_report));
                if(quote_report == NULL)
                    return -ENOMEM;
                // duplicate nonce
                RECORD(GENERAL_RETURN,UUID) * quote_nonce = msg_expand->expand;
                Memcpy(quote_report->nonce,quote_nonce->return_value,DIGEST_SIZE);
                // get (MESSAGE,INSTANCE_INFO) value
                ret = message_remove_expand(recv_msg,TYPE_PAIR(MESSAGE,INSTANCE_INFO),&msg_expand);
                if(ret<0)
                    return ret;
                instance_info=msg_expand->expand;
            
                //duplicate (TCM_PIK_DESC,USERINFO) value
                Strncpy(quote_report->userinfo.username,instance_info->user_name,DIGEST_SIZE);
                Memcpy(quote_report->userinfo.node_uuid,instance_info->node_uuid,DIGEST_SIZE);
                quote_report->userinfo.describe=dup_str("quote_report test",0);
               
                ret = message_add_expand_data(recv_msg,TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE),quote_report);
	            ret=ex_module_sendmsg(sub_proc,recv_msg);
                return ret;                             
            }
        }
        else
        {
                // prepare to output results
                printf("server: convert verify result to policy choice!\n");
                RECORD(TCM_KEY_DESC,VERIFY_DESC) * verify_desc;
                RECORD(TCM_PIK_DESC,PCRQUOTE) * quote_report;
                verify_desc=msg_expand->expand;

                DB_RECORD * db_record;
                
                db_record = memdb_find(verify_desc->object_uuid,TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE));
          
                if(db_record==NULL)
                    return -EINVAL;
                printf("server: get verified report, verify result is %d!\n",verify_desc->result);
    
                quote_report = db_record->record;
                print_bin_data(quote_report->pcrComp.pcrValue,32,16);
                printf("server: verified pcr value is :\n");
        

                RECORD(GENERAL_RETURN,UUID) * policy_digest;
                
                policy_digest = memdb_get_first_record(TYPE_PAIR(GENERAL_RETURN,UUID));
                while(policy_digest!=NULL)
                {
                    printf("policy name : %s value :",policy_digest->name);
                    print_bin_data(policy_digest->return_value,32,16);
                    policy_digest = memdb_get_next_record(TYPE_PAIR(GENERAL_RETURN,UUID));
                }

                RECORD(GENERAL_RETURN,STRING) * policy_choice;
                policy_choice = Talloc0(sizeof(*policy_choice));
                if(policy_choice == NULL)
                    return -ENOMEM;
    
                policy_choice->name=dup_str("policy_choice",0);
                policy_choice->return_value = dup_str("put policys here",0);    

                message_add_expand_data(recv_msg,TYPE_PAIR(GENERAL_RETURN,STRING),policy_choice);

	            ret=ex_module_sendmsg(sub_proc,recv_msg);
        }
    }
    else
    {
        // prepare to verify quote report
        printf("server: prepare to verify quote report!\n");

        RECORD(TCM_PIK_DESC,PCRQUOTE) * quote_report;
        quote_report=msg_expand->expand;
        DB_RECORD * db_record;
        db_record = memdb_store(quote_report,TYPE_PAIR(TCM_PIK_DESC,PCRQUOTE),NULL);
        if(db_record == NULL)
        {
            printf("server: store quote report failed!\n");

        }
          
        print_bin_data(db_record->head.uuid,32,16);  

	    ret=ex_module_sendmsg(sub_proc,recv_msg);
    }
    
    
	return ret;
}

RECORD(TCM_KEY_DESC,LOCAL_KEYSET) * local_keyset_get (char * name)
{
	int ret;
	RECORD(TCM_KEY_DESC,LOCAL_KEYSET ) * local_keyset;
	DB_RECORD * db_record;
	char buf[DIGEST_SIZE];
	int i;
	db_record=memdb_find_first(TYPE_PAIR(TCM_KEY_DESC,LOCAL_KEYSET),"user_name",name);
	if(db_record==NULL)
		return NULL;
	return db_record->record;
}

RECORD(TCM_KEY_DESC,REMOTE_KEYSET) * remote_keyset_get (BYTE *uuid,char * name)
{
	int ret;
	RECORD(TCM_KEY_DESC,REMOTE_KEYSET ) * remote_keyset;
	DB_RECORD * db_record;
	char buf[DIGEST_SIZE];
	int i;
	remote_keyset=memdb_get_first_record(TYPE_PAIR(TCM_KEY_DESC,REMOTE_KEYSET));
	while(remote_keyset!=NULL)
	{
		ret=0;
		if(uuid!=NULL)
		{
			if(Memcmp(uuid,remote_keyset->node_uuid,DIGEST_SIZE)==0)
				ret=1;
			else
				ret=-1;
		}
		if(name!=NULL)
		{
			if(Strncmp(name,remote_keyset->user_name,DIGEST_SIZE)==0)
			{
				if(uuid==NULL)
					ret=1;
			}
			else
				ret=0;

		}
		if(ret==1)
			break;
		remote_keyset=memdb_get_next_record(TYPE_PAIR(TCM_KEY_DESC,REMOTE_KEYSET));
		
	}

	return remote_keyset;
}
