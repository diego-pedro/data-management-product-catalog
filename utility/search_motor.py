"""MongoDB search motor."""

import re
from fastapi import status
from datetime import datetime
from typing import List, Dict
from utility.api_response import http_exception

MAXIMUM_QUERY_COUNT = 100


class MongoDBQuery:
    """Class for querying user MongoDB collections."""

    def __init__(self,
                 collection,
                 search_string: str = "/*",
                 time_range: Dict = None,
                 sorting_fields: List[tuple] = None):

        self.collection = collection

        # Maximum amount of collection records to read in one request
        self.records_list_size = MAXIMUM_QUERY_COUNT

        # Search string to filter results
        self.search_string: str = search_string

        # Validate if search string is in valid regex format
        try:
            re.compile(self.search_string)

        except re.error:
            self.search_string = "/*"

        self.sorting_fields: List[tuple] or None = sorting_fields
        self.start_date: str = time_range.get("start_date")
        self.end_date: str = time_range.get("end_date")

    async def query(self):
        """Builds the query filter and sorting arguments"""
        filter_fields = [[{"content.active": True}]]

        try:

            if self.start_date:
                time_range_start = \
                    datetime.strptime(self.start_date, '%d/%m/%Y %H:%M')
            else:
                time_range_start = datetime(1, 1, 1, 0, 0)

            if self.end_date:
                time_range_end = \
                    datetime.strptime(self.end_date, '%d/%m/%Y %H:%M')
            else:
                time_range_end = datetime.now()
        except ValueError:
            raise http_exception(message="Invalid date filter.",
                                 status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        query_sort = [(f'content.timestamp', -1)]
        query_sort.extend(self.sorting_fields)

        results = await self.collection \
            .find(
            {"$and": [
                {"$or": filter_field}
                for filter_field in filter_fields
                if len(filter_field) > 0
            ],
                "content.timestamp": {
                    "$gte": time_range_start,
                    "$lt": time_range_end
                },
                "$or": [
                    {"content.product_name": {
                        "$regex": f"{self.search_string}"
                    }},
                    {"content.product_category": {
                        "$regex": f"{self.search_string}"
                    }},
                ]
                ,
            }) \
            .sort(query_sort) \
            .to_list(self.records_list_size)

        if results:
            return results
        return []
