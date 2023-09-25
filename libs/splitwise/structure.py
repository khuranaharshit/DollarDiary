"""
This module defines the structure holding the data and the relation.
"""

import json
from typing import Union
from datetime import datetime, timezone
from splitwise import Expense
from dataclasses import dataclass, asdict, field
import dateutil.parser

@dataclass
class ExpenseData:
    
    id: str                 # unique-id of the expense
    amount: float           # expense amount
    created_at: datetime    # creation date of expense (UTC tz by library)
    updated_at: datetime    # updated data of expense (UTC tz by library)
    description: str        # expense description
    details: str            # expense details
    group_id: str           # group to which the expense belongs
    category: str           # category the expense belongs to

    def serialise(self) -> dict[str, Union[str, list[str]]]:
        """
        Method to serialise the object in a json'ified structure for storing the data in storage
        """
        obj = self.__class__(**self.__dict__)
        if obj.created_at:
            obj.created_at = int(obj.created_at.timestamp())
        if obj.updated_at:
            obj.updated_at = int(obj.updated_at.timestamp())

        return json.dumps(asdict(obj), indent=4, default=str)

    @classmethod
    def deserialise(cls, expense_data_string: str):
        """
        Method to serialise the object in a json'ified structure for storing the data in storage
        """
        obj = cls(**json.loads(expense_data_string))
        if obj.created_at:
            obj.created_at = datetime.fromtimestamp(obj.created_at, timezone.utc)
        if obj.updated_at:
            obj.updated_at = datetime.fromtimestamp(obj.updated_at, timezone.utc)
        
        return obj

def convert_expense_to_expense_data(expense: Expense) -> ExpenseData:
    """
    This method is responsible for converting an instance of expense to ExpenseData.
    """
    return ExpenseData(
        id=expense.id,
        amount=float(expense.cost),
        created_at=dateutil.parser.parse(expense.created_at),
        updated_at=dateutil.parser.parse(expense.updated_at),
        description=expense.description,
        details=expense.details,
        group_id=expense.group_id,
        category=expense.category,
    )
