simple_wf - Simple Workflow : A Python Workflow Engine 
======================================================

simple_wf intends to bring the easy-to-use and intuitive API for workflow application in Python world.

High-lights:
------------

+ flow routing:
 + join (and-join / xor-join )
 + split (and-split / xor-split ) 
+ conditions routing:
+ intuitive API, easy to use
+ Abstract persisent layer ( currently supports Django-ORM only )

Example Code:
=============

1. An Easy Enough Example 
-------------------------

![alt text](https://docs.google.com/drawings/pub?id=1kQf4gLW6HDnLJ10RwopnG5xJHeJ2QE8--3cwVNG49sw&w=960&h=720 "Conditional Rounting")

The workflow can be represent in code like this:

 ```python
router = Router(
    Route().any('_new').next('check'),
    Route().any('check').next('pass').test(lambda d: d.get('score') >= 60),
    Route().any('check').next('not_pass').test(lambda d: d.get('score') < 60),
    Route().any('pass').next('_end'),
    Route().any('not_pass').next('_end'),
)
```

Following code demo the basic step of using the workflow.

1.)  When score is greater than 60
```python
wf_engine = WorkflowEngine(DJPersistentDriver(operator=user), router)

# start the workflow
wf_engine.wf_start()

# the first todo should be "check"
assert wf_engine.todo_set() == set(['check'])

# provide the score to the complete function, it will choose next
# appropriate workflow activity
wf_engine.complete('check', data={'score': 60})

# when score is less than 60, the only proper activity is pass
assert wf_engine.todo_set() == set(['pass'])

wf_engine.complete('pass')
assert wf_engine.todo_set() == set(['_end'])

#wf should close automatically when _end completed
wf_engine.complete('_end')
assert wf_engine.wf_state() == 'closed'
```

2) when score is less than 60
```python
...
...
# provide the score to the complete function, it will choose next
# appropriate workflow activity
wf_engine.complete('check', data={'score': 59})

# when score is less than 60, the only proper activity is pass
assert wf_engine.todo_set() == set(['notpass'])
...
...
```