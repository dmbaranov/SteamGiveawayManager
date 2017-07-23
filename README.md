# Steam Giveaway Manager

Enters giveaways on different sites and helps you to win awesome games.

## Installation
Download this repository and navigate to dist/main folder. You'll find a `main.exe` here which is a file you need.  
But before launching it, you have to create file `cookies.ini` which should have following content (example):

```
[STEAMGIFTS]
PHPSESSID=2ehri2uy34hkjrfy7i34jhf
```

Inside square brackets you should put bot's name, for now only Steamgifts is available. After that proceed to the giveaway website and get all the cookies from there (You can use DevTools for it. If you don't know how do do it, just google it. Instructions will be added later).  
As soon as you have your cookies, put them in `cookies.ini` like in the example above (cookies are case sensitive). If everything is ready, just start the bot and let it work.