import json
from core.zettle.validation.inventory_update_validation import InventoryBalanceChanged

class WebhookHandler:
    def process_subscription(self,data):
        
        validated_data: InventoryBalanceChanged = InventoryBalanceChanged.model_validate_json(json_data=data)

        #process data

        #save data