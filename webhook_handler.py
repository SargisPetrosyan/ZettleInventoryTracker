import uuid
import rich
from sqlalchemy import Engine
from core.repositories import InventoryUpdateRepository
from core.utils import OrganizationsNameMappedId
from core.zettle.data_fetchers.product_data_fetcher import ProductDataFetcher
from core.zettle.validation.inventory_update_validation import InventoryBalanceChanged
from core.zettle.validation.product_validating import ProductData

class WebhookHandler:
    def __init__(self) -> None:
        self.organizations_name: OrganizationsNameMappedId = OrganizationsNameMappedId()

    def process_subscription(self,inventory_update:InventoryBalanceChanged):
        
        # get name by id
        name: str = self.organizations_name.get_name_by_id(shop_id=str(object=inventory_update.organizationUuid))

        # fetch product_data
        product_data = ProductDataFetcher(shop_name=name)
        new_product_data = product_data.get_product_data(product_uuid=str(object=inventory_update.payload.balanceAfter[0].productUuid),organization_uuid=str(inventory_update.organizationUuid))

        #validate Product_data
        inventory_update_validate:ProductData = ProductData.model_validate(obj=new_product_data)

        # store data in database
        database_repositories:InventoryUpdateRepository = InventoryUpdateRepository(engine=Engine)
        

        database_repositories.store_product_data(
            shop_id=inventory_update.organizationUuid,
            name=,
            category=,
            product_id=,
            variant_id=,
            timestamp=,
            before=,
            after=,
        )