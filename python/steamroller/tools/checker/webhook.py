import sys
import os

# payload = sys.argv[1]
# print ( payload)

# # z:\\pipelineTest\... 



payload_data_project_type = os.environ.get("payload_data_project_type")
payload_data_created_at =  os.environ.get("payload_data_created_at")
payload_data_delivery_id = os.environ.get("payload_data_delivery_id")
payload_data_entity_id = os.environ.get("payload_data_entity_id")
payload_data_event_log_entry_id = os.environ.get("payload_data_event_log_entry_id")
payload_data_event_type = os.environ.get("payload_data_event_type")
payload_data_id = os.environ.get("payload_data_id")
payload_data_meta_entity_id = os.environ.get("payload_data_meta_entity_id")
payload_data_meta_entity_type = os.environ.get("payload_data_meta_entity_type")
payload_data_meta_hook_id = os.environ.get("payload_data_meta_hook_id")
payload_data_meta_type = os.environ.get("payload_data_meta_type")
payload_data_operation = os.environ.get("payload_data_operation")
payload_data_project_id = os.environ.get("payload_data_project_id")
payload_data_project_type = os.environ.get("payload_data_project_type")
payload_data_user_id = os.environ.get("payload_data_user_id")
payload_data_user_type = os.environ.get("payload_data_user_type")
payload_timestamp = os.environ.get("payload_timestamp")

print ( payload_data_project_type  )
print ( payload_data_created_at )
print ( payload_data_delivery_id )
print ( payload_data_entity_id )
print ( payload_data_event_log_entry_id ) 
print ( payload_data_event_type )
print ( payload_data_id )
print ( payload_data_meta_entity_id )
print ( payload_data_meta_entity_type )
print ( payload_data_meta_hook_id )
print ( payload_data_meta_type )
print ( payload_data_operation )
print ( payload_data_project_id )
print ( payload_data_project_type )
print ( payload_data_user_id )
print ( payload_data_user_type )
print ( payload_timestamp )