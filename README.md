# CustomTimer

Simple timer library

# Usage
```python
# Create Timer Object
timer = CustomTimer()

#register task and specified period in millisecond
@timer.register
@timer.periodic_task(interval = 100)  
def func():
  pass

#Start non blocking timer
timer.run(block=False)

```

