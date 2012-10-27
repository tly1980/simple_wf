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

### Full Example

```python
class SimpleConditionRoutingTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='wf_user')
        router = Router(
            Route().any('_new').next('check'),
            Route().any('check').next('pass').test(lambda d: d.get('score') >= 60),
            Route().any('check').next('not_pass').test(lambda d: d.get('score') < 60),
            Route().any('pass').next('_end'),
            Route().any('not_pass').next('_end'),
        )

        self.wf_engine = WorkflowEngine(DJPersistentDriver(operator=user), router)

    def test_pass(self):
        self.wf_engine.wf_start()

        # the first todo should be "check"
        self.assertEqual(self.wf_engine.todo_set(), set(['check']))

        # provide the score to the complete function, it will choose next
        # appropriate workflow activity
        self.wf_engine.complete('check', data={'score': 60})

        # when score is less than 60, the only proper activity is pass
        self.assertEqual(self.wf_engine.todo_set(), set(['pass']))

        self.wf_engine.complete('pass')

        self.assertEqual(self.wf_engine.todo_set(), set(['_end']))
        #wf should close automatically when _end completed
        self.wf_engine.complete('_end')
        self.assertEqual(self.wf_engine.wf_state(), 'closed')

```

Split
=====

![alt text](https://raw.github.com/tly1980/simple_wf/develop/charts/split.png "Split")

+ And-Split

All the inputs that lead to this activity have to be completed in order to enable this output to work.
```python
router = Router(
  ...,
  # complting 'a' will enable 'c', 'd', 'e'
  # Alternatively, can use: Route().any('a').next('c', 'd', 'e') 
  Route().exact('a').next('c', 'd', 'e'),
  
  ...
)
```


+ Xor-Split


```python
router = Router(
    ...
    Route().any('check').next('pass').test(lambda d: d.get('score') >= 60),
    Route().any('check').next('not_pass').test(lambda d: d.get('score') < 60),
    ...
)
```

Join
====

![alt text](https://raw.github.com/tly1980/simple_wf/develop/charts/join.png "Join")

+ And-Join

```python
# if you want 'c', to be enabled, you have to 
# complete 'a','b' and 'c'
router = Router(
    ...
    Route().exact('a', 'b', 'c').next('d'),
    ...
)
```

+ Xor-Join

```python
# just complete any of 'a', 'b', 'c' will enable 'd'
router = Router(
    ...
    Route().any('a', 'b', 'c').next('d'),
    ...
)
```

Or you could use following code:

```python
# just complete any of 'a', 'b', 'c' will enable 'd'
router = Router(
    ...
    Route().any('a').next('d'),
    Route().any('b').next('d'),
    Route().any('c').next('d'),
    ...
)
```

More Examples
=============

Please take a look at [here](https://github.com/tly1980/simple_wf/blob/develop/simple_wf/tests/example.py).



