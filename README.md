# tokenbender

disclaimer: (unfinished, underconstruction)

idea is to do a visual viewer for local small model workflows. to make it look cool but at the same time keep it useful.

right now you can run it via

`uv run --with flask app.py`

to trigger run of a graph you can do 

`watch -n1 curl -X POST http://127.0.0.1:5001/process_epoch`

the demo which is initialised in the bootstrap function uses tcpdump (which needs sudo). you can replace it with any other source of data for your use case.

also this needs ollama right now for the demo. but otherwise just change the steps. Or remove LLMs all together and just use any commands and run the grpah!
