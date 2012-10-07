from simple_wf.statemachine import Router, Route

pr_router = Router(
    Route().any('_new').next('request_purchase'),

    #if amount less than 50 dollars, the request goes to admin
    Route().any('request_purchase').next('admin_check').test( lambda d: d['amount'] <= 50 ),
    #if amount greater than 50 dollars, the request goes to manager
    Route().any('request_purchase').next('manager_check').test( lambda d: d['amount'] > 50 ),

    #Admin check: approve goes to acounting, disapprove will terminate the process
    Route().any('admin_check').next('place_order').test(lambda d:d['approve'] == True),
    Route().any('admin_check').next('request_purchase').test(lambda d:d['approve'] == False),

    #Admin check: approve goes to acounting, disapprove will terminate the process
    Route().any('manager_check').next('place_order').test(lambda d:d['approve'] == True),
    Route().any('manager_check').next('request_purchase').test(lambda d:d['approve'] == False),

    Route().any('place_order').next('confirm_received'),

    Route().any('confirm_received').next('_end'),
)