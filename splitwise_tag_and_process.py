"""
This is an example module which 
- Loads details from a YAML file 
- Filters the group based on 'group_filters'
- For the groups that made it, it then tags all the expenses of the group based on 'matchers'
- 
This will expose a bunch of methods to add tags to existing expenses based on keywords, group-name
etc
"""

from libs.splitwise.service import SplitwiseService
from libs.splitwise.structure import ExpenseData
import concurrent.futures
import yaml
import json
from functools import wraps
import time

MAX_LIMIT = 1e9

def timer(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        s = time.perf_counter()
        result = func(*args, **kwargs)
        total = time.perf_counter() - s
        print (f"Completed {func.__name__} in {total:.4f} seconds")
        return result
    return timeit_wrapper

def tagger(
        expense_dict: dict[str, ExpenseData],
        tag_name: str,
        tag_keywords: list[str]
    ) -> tuple[str, set[str]]:
    """
    This method is responsible for tagging the ExpenseData objects with the particular tag
    and return a set containing id of tagged expenses 
    """
    output = set()
    for eid, expense in expense_dict.items():
        for keyword in tag_keywords:
            if not keyword:
                continue
            if expense.description:
                if keyword.lower() in expense.description.lower():
                    output.add(eid)
            if expense.details:
                if keyword.lower() in expense.details.lower():
                    output.add(eid)
    
    return (tag_name, output)



class TagAndProcess():
    """
    This is an example helper class responsible for tagging the expenses based on a YAML file
    and then grouping and summing the data
    """

    def __init__(self, yaml_filepath: str) -> None:
        self.service = SplitwiseService()
        self.matcher_content = yaml.safe_load(open(yaml_filepath))
        self.service.get_expenses(limit=MAX_LIMIT)
    
    @timer
    def get_filtered_group_expenses(self) -> None:
        """
        This method is responsible for pulling the expenses belonging to the group which align
        with the group_filters.
        """
        groups = self.service.get_all_groups()
        group_filter = self.matcher_content['group_filters']

        filtered_groups_list = []
        for gid, gname in groups.items():
            for filter in group_filter:
                if str(filter).lower() in gname.lower():
                    filtered_groups_list.append(gid)
        
        return self.service.get_expenses(group_id_list=filtered_groups_list, limit=MAX_LIMIT)
    
    @timer
    def tag_expenses(self, expense_list: list[ExpenseData]) -> dict[str, list[str]]:
        """
        This method is used for tagging expenses based on the "matchers" in the YAML file.
        """
        tag_keywords_dict = self.matcher_content['matchers']
        expense_dict = {expense.id: expense for expense in expense_list}
        tag_expense_id_dict = {}

        # Run with all available cpus - high overhead if less tags/items to process
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for tag_name, tag_keywords_list in tag_keywords_dict.items():
                futures.append(executor.submit(tagger, expense_dict, tag_name, tag_keywords_list))
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                tag_expense_id_dict[result[0]] = list(result[1])
            
            return tag_expense_id_dict

    def aggregate_tagged_expenses(
        self,
        filtered_expense_list: list[ExpenseData],
        tagged_expenses: dict[str, list[str]]
    ) -> dict[str, list[ExpenseData]]:
        """
        This method is responsible for aggregating the tagged expenses.
        """
        output_dict = {}
        expense_dict = {expense.id: expense for expense in filtered_expense_list}

        for tag, expense_list in tagged_expenses.items():
            output_dict[tag] = []
            for eid in expense_list:
                output_dict[tag].append( expense_dict[eid] )
        
        return output_dict

    def run_summation_operation(self, aggregated_expenses: dict[str, list[ExpenseData]]) -> dict[str, int]:
        """
        This method is used for running summation operation on the aggregated ExpenseData i.e all
        the expenses will be summed based on their tags and a final value value will be returned
        """
        output = {}
        for k, expense_list in aggregated_expenses.items():
            output[k] = sum([int(expense.amount) for expense in expense_list])
        
        print (json.dumps(output, indent=4, default=str))
    
    def run(self):
        """
        This is the driver method responsible for running the process end to end.
        """
        filtered_expense_list = self.get_filtered_group_expenses()
        
        tagged_expenses = self.tag_expenses(filtered_expense_list)

        aggregated_tagged_expenses = self.aggregate_tagged_expenses(
            filtered_expense_list, tagged_expenses
        )

        self.run_summation_operation(aggregated_tagged_expenses)
        

if __name__ == '__main__':
    TagAndProcess("./tag.yaml").run()