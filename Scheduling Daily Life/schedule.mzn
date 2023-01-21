include "globals.mzn"; 
%List of work hours on each days
int: total_task;
int: day=24;
array [1..total_task] of int: task_time;
array [1..total_task] of int: min;
array [1..total_task] of int: max;
array [1..total_task] of int: weekend;
array[1..total_task, 1..7] of var 0..99: schedule;

constraint
  forall(i in 1..7) (
    sum(schedule[1..total_task, i]) = day
    /\
    forall(j in 1..total_task) (
      if min[j] != 0 then
        if weekend[j] == 0 then
          if i!=6 /\ i!=7 then
            schedule[j, i] >= min[j]
          endif
        else
          schedule[j, i] >= min[j]
        endif
      endif
      /\
      if max[j] != 0 then
        schedule[j, i] <= max[j]
      endif
     )
  )
  /\
  forall(i in 1..total_task) (
    if task_time[i] != 0 then
       sum(schedule[i, 1..7]) = task_time[i]
    endif
    /\
    if weekend[i] == 0 then
      schedule[i, 6] = 0
      /\
      schedule[i, 7] = 0
    endif
  )
;
solve satisfy;