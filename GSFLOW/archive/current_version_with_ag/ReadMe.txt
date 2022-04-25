There are two runs in this folder right now because I found that using a new vs. old GSFLOW .exe 
file results in dramatically different model run times, model convergence, and mean recharge.


Using the new gsflow executable (gsflow.exe from 4/20/22):
- run time: ~ 9 hours
- number non-convergence: 6389 time steps
- mean recharge: 1,247,655 m^3/day

Using the old gsflow executable (gsflow_20220303.exe from 3/3/22):
- run time: ~ 2 hours
- number non-convergence: 192 time steps
- mean recharge: 525,799 m^3/day