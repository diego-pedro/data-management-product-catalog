"""Message management implementation."""
import datetime
from fastapi import APIRouter, status, Depends
import pydantic
from bson.objectid import ObjectId
from db.mongodb import data_db
from fastapi_jwt_auth import AuthJWT
from utility.api_response import http_exception

# Fix ObjectId & FastApi conflict
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

router = APIRouter(tags=["Messages"])


@router.get("/service/{service_uuid}/{username}")
async def get_active_messages_by_service_id(service_uuid: str,
                                            username: str):
    query_sort = [(f'content.timestamp', -1)]

    message = await data_db.messages.find(
        {"content.service_uuid": service_uuid,
         "content.username": username,
         "content.active": True}
    ).sort(query_sort).to_list(10)

    if message:
        return {"Active Message List": message}
    else:
        raise http_exception(message="No active messages found.", status=status.HTTP_404_NOT_FOUND)


@router.put("/service/{service_uuid}/process/{message_uuid}")
async def process_active_message(service_uuid: str,
                                 message_uuid: str):
    message = await data_db.messages.find_one_and_update(
        {"content.service_uuid": service_uuid, "content.active": True, "content.message_uuid": message_uuid},
        {"$set":
             {"content.active": False}
         }
    )

    if message:
        await data_db.messages.delete_one(
            {"content.service_uuid": service_uuid, "content.active": False, "content.message_uuid": message_uuid}
        )

        return {"Message Status Completed at:": datetime.datetime.now(),
                "Message Detail": message["content"]["detail"]}

        # Do context action

    else:
        raise http_exception(message="Message not found.", status=status.HTTP_404_NOT_FOUND)


@router.delete("/service/{service_uuid}/clear")
async def clear_inactive_messages(service_uuid: str):
    inactive_messages = await data_db.messages.count_documents(
        {"content.service_uuid": service_uuid, "content.active": False})

    await data_db.messages.delete_many(
        {"content.service_uuid": service_uuid, "content.active": False}
    )

    return {"Messages Cleared": inactive_messages}
