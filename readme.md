# Raceit.py

This is a simple tool I've made to test race condition during engagement.

## How it works :

Inspired by [@bo0om article](https://lab.wallarm.com/race-condition-in-web-applications/), the idea is to initiate multiple thread with a socket for each one, and let them send all the request except last byte. 

When they've send this part, they wait until all thread is ready. When all thread have reach the barrier, they're release and they send the last byte at almost same time. 

This technique give greater chance of race condition, than just sending multiple request in parallele.

## Informations : 

- race condition is "not possible" on PHP session, has php use file lock on session by default, so each request is processed one after another
- the script does not do integrity check on the provided request, so be sure what you put in the file (sorry I'm lazy)
- race condition is not that documented for web, so if you manage to find cool race condition bug in the wild, please reach me I'm really curious about it :)
- Burp turbo intruder is probably more effective, but I dont know how it deal with the race condition script, if he just send multiple request in parallele or what, so I preferred to do my own script.


*sorry for my bad english and bad coding skills*
