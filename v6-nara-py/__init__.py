import time
from rpy2 import robjects 
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
pandas2ri.activate()

base = importr('base')
stats = importr('stats')


from vantage6.tools.util import info

def master(client, data, column_name):
    """Combine partials to global model
    First we collect the parties that participate in the collaboration.
    Then we send a task to all the parties to compute their partial (the
    row count and the column sum). Then we wait for the results to be
    ready. Finally when the results are ready, we combine them to a
    global average.
    Note that the master method also receives the (local) data of the
    node. In most usecases this data argument is not used.
    The client, provided in the first argument, gives an interface to
    the central server. This is needed to create tasks (for the partial
    results) and collect their results later on. Note that this client
    is a different client than the client you use as a user.
    """

    # Info messages can help you when an algorithm crashes. These info
    # messages are stored in a log file which is send to the server when
    # either a task finished or crashes.
    info('Collecting participating organizations')

    # Collect all organization that participate in this collaboration.
    # These organizations will receive the task to compute the partial.
    organizations = client.get_organizations_in_my_collaboration()
    ids = [organization.get("id") for organization in organizations]

    # Request all participating parties to compute their partial. This
    # will create a new task at the central server for them to pick up.
    # We've used a kwarg but is is also possible to use `args`. Although
    # we prefer kwargs as it is clearer.
    info('Requesting partial computation')
    task = client.create_new_task(
        input_={
            'method': 'average_partial',
            'kwargs': {
                'column_name': column_name
            }
        },
        organization_ids = [1]
    )

    # Now we need to wait untill all organizations(/nodes) finished
    # their partial. We do this by polling the server for results. It is
    # also possible to subscribe to a websocket channel to get status
    # updates.
    
    info("Waiting for resuls")
    task_id = task['id']
    task_info = client.get_task(task_id)
    attempts = 0
    while not task_info.get("complete") or attempts>5:
        task_info = client.get_task(task_id)
        info("Waiting for results")
        attempts += 1
        time.sleep(3)

    # Once we now the partials are complete, we can collect them.
    info("Obtaining results")

    #results = client.get_results(task_id=task.get("id"))
    # Once we now the partials are complete, we can collect them.
    #for result in results:
     #   global_sum += result["sum"]
      #  global_count += result["count"]
    # Now we can combine the partials to a global average.
    #print(base.summary(results))
    #return {"glm": results[0]['model']}

def RPC_average_partial(data, column_name):
    """Compute the average partial
    The data argument contains a pandas-dataframe containing the local
    data from the node.
    """
    robjects.globalenv['dataframe'] = data

    # extract the column_name from the dataframe.
    info(f'Extracting column {column_name}')

    # compute the sum, and count number of rows
    info('Computing partials')
    #View(data)
    #formula = robjects.Formula('dead~sex+stage+resection+topography+age_group')
	#, family="binomial", data = data
    #env = formula.environment
    #env["dead"] = data['dead']
    #env[]
    #model <- stats.glm(formula)
    #print(model)
    #robjects.r('''
    #View(data)
    print(data)
    model = robjects.r.glm(formula = robjects.r('dead~sex+stage+resection+topography+age_group'), data = base.as_symbol('dataframe'), family=robjects.r('binomial'))
    #''')
    info('partials computed')
    #print(model.rclass)
    print(base.summary(model))
    
    # return the values as a dict
    #return {
    #    "model": model
    #}