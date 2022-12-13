"""MongoDB database implementation."""

from prettyconf import config
import motor.motor_asyncio

mongodb_url = config("MONGO_DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)

# Connect to data management database
data_db = client.data_management
