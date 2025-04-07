# f1 time gap visualizer

this script loads f1 race session data using fastf1 and displays an interactive plotly graph of time gaps to the race leader over the course of a grand prix.

- plots time gaps to the leader for all classified drivers  
- filters out pit stop laps (in-laps, out-laps) and non-green flag laps  
- uses official team colors for visual clarity  
- hover tooltips show lap number and exact gap in seconds  
- works for any race session (practice, qualifying, race)

## requirements

- python 3  
- fastf1  
- plotly  
- numpy  
- pandas
