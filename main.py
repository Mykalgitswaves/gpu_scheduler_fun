import numpy as np
import asyncio

NOT_STARTED = 'not-started'
IN_PROGRESS = 'in-progress'
PROCESSED = 'processed'
RESOURCES = 48 # gb vram available for use across tasks.

# Cost of mapping states of our tasks, note - resource req to complete a task is dependent on resource req on instance.
resource_mapping = {
    NOT_STARTED: 1, # The cost of moving one task from NOT STARTED to in-progress is 1 gb of vram, unrealistic but who cares.
    PROCESSED: 1 # Cost of moving a processed task from in-progress is 1 gb of vram
}


class Task:
    task_count = 0
    def __init__(self, cls, **kwargs):
        self.id = cls.task_count += 1
        self.status: Literal[NOT_STARTED, IN_PROGRESS, PROCESSED] = NOT_STARTED
        self.op: Callable[any] = kwargs['op']
        self.resource_req:int = kwargs['resource_req']

    def __call__(self):
        if self.status != NOT_STARTED:
            raise ValidationError('cant call a finished or in progress task')
            
        self.status = IN_PROGRESS
        result = self.op()
        return result

class SchedulerQueue:
    import heapq
    def __init__(self, tasks:list[int]):
        self.q = []
        heapq.heapify(self.q, tasks)
        self.resources:int = RESOURCES # Available compute on machine. 
    
    def _get_latest_task(self) -> Task:
        task = heapq.heappop(self.q)
        if task is None:
            raise ValidationError("task matching the id not found")
        return task

    def process_tasks(self):
        try:
            all_tasks = len(self.q) - 1
            # Figure out a way to oprocess multiple of these in tandem.     
            while self.resources > 0 and self.q > 0: 
                # Use asyncio to instantiate a task group to parallelize operations.
                group = asyncio.task_group([process_task for _ in range(all_tasks)])
                return group
        except str(e) as e:
            print(f'something weird happened, {e}')
        
        
    def process_task(self) -> None | Task:
         # Maybe i can do this with asyncio task groups. 
         # Always try to free up space and resources in our scheduler by freeing up any finished tasks first.
         # This might actually be a shit idea but who knows. I'll check after i have wifi.
        task = self._get_latests_task()

        if not task:
            return None 
        
        if task.status == NOT_STARTED and self.resources > 1:
            # hold out resource 
            self.resources -= 1
            task.status = IN_PROGRESS
            self.resources += 1
            return None
            
        elif task.status == IN_PROGRESS and self.resources > task.resource_req:
            # allocate resources, invoke callable
            self.resources -= task.resource_req

            result = task()

            task.status = PROCESSED
             # re allocate resources
            self.resources += task.resource_req
            return result
            
        elif task.status == PROCESSED and self.resources > 1:
             # finally yeild as generator
            self.resources -= 1
            
            # Pop this one from the q - and remove it from our dictionary. 
            idx = self.q.index(task.id)
            self.q.pop(idx)
            del self.tasks_by_id[task.id]
            # Re allocate resource.
            self.resources += 1
            return None            
        else: # Otherwise if anyything else happens just return
            return
                       
def add_operation(data:list[int|float]) -> float:
    # cost proportionate to length of array 
    return float(np.sum(data))

def subtract_operation(data:list[int|float]) -> float:
    # Cost is proportionate to length of array. 
    # How do we get bytesize of data?
    return float(np.subtract(data))

if __name__ == '__main__':
    task_1 = Task(add_operation[1,2,3,4,5,6])
    task_2 = Task(subtract_operation[1,2,34,5,67])    
    
    scheduler = TaskScheduler(data=[task_1, task_2])


    assert 
