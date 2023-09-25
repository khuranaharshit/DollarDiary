"""
Library for accessing Splitwise data for a user.
"""

import os
from splitwise import Splitwise
from datetime import datetime
from libs.splitwise.config import API_KEY_FILEPATH, CONSUMER_KEY_FILEPATH, CONSUMER_SECRET_FILEPATH
import logging
from libs.splitwise.structure import ExpenseData, convert_expense_to_expense_data

logger = logging.basicConfig(level=logging.INFO)

MAX_LIMIT = 1e9

class SplitwiseService():
    """
    This loads configuration parameters from environment if available else tries to pull info from
    file.
    """
    def __init__(self) -> None:
        api_key = os.environ.get('API_KEY') or self._read_from_file(API_KEY_FILEPATH)
        consumer_key = os.environ.get('CONSUMER_KEY') or self._read_from_file(CONSUMER_KEY_FILEPATH)
        consumer_secret = os.environ.get('CONSUMER_SECRET') or self._read_from_file(CONSUMER_SECRET_FILEPATH)

        # Login to SplitWise dashboard and create an App with.
        self._splitwise = Splitwise(consumer_key, consumer_secret,api_key=api_key)

    def get_expenses(
        self,
        start_dt: datetime = None,
        end_dt: datetime = None,
        group_id_list: list[str] = None,
        **kwargs
    ) -> list[ExpenseData]:
        """
        Returns all the expenses.
        If the time-range is specified then will return within that time-range (including start_dt,
        excluding end_dt).
        If the group_id_list is passed then will consider only those groups else will get Expenses
        from all the groups.
        """

        start_ts, end_ts, objects = None, None, []
        if start_dt:
            start_ts = start_dt.isoformat()
        if end_dt:
            end_ts = start_dt.isoformat()
        
        if group_id_list:
            for gid in group_id_list:
                objects.extend(
                    self._splitwise.getExpenses(
                        dated_after=start_ts, dated_before=end_ts, group_id=gid, **kwargs
                    )
                )
        else:
            objects = self._splitwise.getExpenses(
                dated_after=start_ts, dated_before=end_ts, **kwargs
            )
        return [convert_expense_to_expense_data(expense) for expense in objects]

    def _read_from_file(self, filename: str) -> str:
        """
        Read data from file and return string
        """
        with open(filename) as f:
            return f.readline().rstrip()

    def get_all_groups(self) -> dict[str, str]:
        """
        Returns a list of key-value pairs, where key is the group-id and value is the group-name
        """
        return {group.id: group.name for group in self._splitwise.getGroups()}


    def get_all_groups_expenses(self):
        """
        Get all groups for the user.

        Note: Some of the groups might be missing
        """
        groups = {}
        for expense in self.get_expenses(limit=MAX_LIMIT):
            expense_list = groups.setdefault(expense.group_id , [])
            expense_list.append(expense)
        
        return groups
    