# Sonos-cmd-controller
Did you ever want to control your Sonos from your console? So did we. Worry no more, because this project allows you just that.

## Installation
Use python3 and install via
```
pip3 install -r requirements.txt
```
The project uses SoCo and Requests.

## Available commands
| Command  | Shortcut | Parameters         | Description                                                                    |
|----------|----------|--------------------|--------------------------------------------------------------------------------|
| info     | i        |                    | Show info of the currently playing song.                                       |
| next     | n        | offset (optional)  | Play next song or use offset to play a upcoming song from queue.               |
| previous | pr       |                    | Play previous song.                                                            |
| play     | pl       |                    | Toggle play                                                                    |
| pause    | p        |                    | Pause                                                                          |
| shuffle  | s        |                    | Shuffle playlist                                                               |
| volume   | v        | [0-100] (optional) | Read or set volume via parameter                                               |
| queue    | q        | id (optional)      | Show the current queue                                                         |
| random   | r        |                    | play a random song from the queue                                              |
| remove   | rm       | id (optional)      | Remove current song from the queue or use id to remove any song from the queue |
| playlist | add      | name               | Add current song to playlist specified with name parameter.                    |
| lyrics   | l        |                    | Show lyrics for current song                                                   |
