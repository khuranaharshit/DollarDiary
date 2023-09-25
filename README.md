# DollarDiary

## End Goal:
- App for tracking daily transactions and managing your money better.

### Integrations
- Get input from various apps like Khatabook, Splitwise and other money managing apps.
- Ability to export data in different formats like csv etc that could then be consumed by other 
apps like google-sheets, Splitwise etc

### Initial Stages
- It is just for pulling data from Splitwise and then being able to tag an 
expense, and further being able to group and summarise expenses by different groups. There is no
limit on number of tags for an expense, but user should be mindful while tagging an expense.
    - It will then support exporting it in different formats.

#### Usage:
- For `splitwise_tag_and_process.py`
    - This script pulls all the transactions and expenses from Splitwise and then tag it based on
    the YAML specified by the user. It further sums the different expenses based on tag and renders
    the result.
    - It's useful for folks who want to get an estimate of how much money was spent for what
    purpose.
    - How to use:
        - Update the `tag.yaml` file and add 
        - filters from group in `group_filters`, only the groups whose name contain these filters
        will be considered.
        - In the `matches` section the key of the YAML is the tag-name and the values are different
        keywords which when matched would associate the expense with this tag.
        - Note: Single expense could be rendered in multiple tags. And thus the total summed value
        across all tags maynot match the total spendings.
        - Once above changes are done, simply run `python3 splitwise_tag_and_process.py`

- Generating API-keys for Splitwise
    - Head over to `https://secure.splitwise.com/#/dashboard`
    - Click on profile section on top-right column
    - Click on "Your account"
    - Head over to "Privacy & Security", click on "Your apps"
    - Click on "Register your application" and get details.