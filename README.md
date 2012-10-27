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


Metaphor
--------
+ Route: identical to transition. Every route contains input and output.
+ Router: composed by a set of routes, represent the workflow.
  Router will select the right route based on input state, just as workflow transition.
+ Workflow Engine: Driven by workflow and current transition state.

### Route Input:
 any(state1, state2, ... ) or exact( state1, state2, ...)
### Route Output:
 next(state1, state2, ... )

### Example 

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
