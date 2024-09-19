# utils/database.py

import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey

# Load environment variables from .env file
load_dotenv()

# Retrieve Cosmos DB connection details
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_KEY')
COSMOS_DATABASE = os.getenv('COSMOS_DATABASE')
COSMOS_CONTAINER = os.getenv('COSMOS_CONTAINER')

# Initialize the Cosmos client
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

# Get the database
database = client.create_database_if_not_exists(id=COSMOS_DATABASE)

# Get the container
container = database.create_container_if_not_exists(
    id=COSMOS_CONTAINER,
    partition_key=PartitionKey(path="/conversation_id"),
    offer_throughput=400
)

def save_conversation(conversation_id, conversation_data, persona, linkedin_url, company_name):
    """
    Saves the conversation data to Cosmos DB.
    """
    item = {
        'id': conversation_id,
        'conversation_id': conversation_id,
        'persona': persona,
        'linkedin_url': linkedin_url,
        'company_name': company_name,
        'conversation_data': conversation_data
    }
    container.upsert_item(item)

def get_conversation(conversation_id):
    """
    Retrieves the conversation data from Cosmos DB.
    """
    try:
        item_response = container.read_item(
            item=conversation_id,
            partition_key=conversation_id
        )
        return item_response
    except Exception as e:
        print(f"Error retrieving conversation: {e}")
        return None

def list_conversations():
    """
    Lists all conversations with their IDs, personas, and company names.
    """
    query = "SELECT c.id, c.persona, c.company_name FROM c"
    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    return items
