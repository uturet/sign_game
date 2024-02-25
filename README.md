# Overview


Implemented WebSocket protocol with socket library in Python and created a web page to provide an example

The purpose was to understand deeply how protocols work over TCP.

[Software Demo Video](https://youtu.be/Nqh7iw0pFfI)

# Network Communication
The application uses client-server architecture with TCP protocol on a 9999 port.
Client to server communicates with JSON messages in the next format:
```json
{
  "action": number,
  "data": ...
}
```

And server to client communicates with JSON messages in next format:
```json
{
  "type": number,
  "message": string
}
```


# Development Environment

    Server: 
        Python3:
            asyncio
            asyncio.streams
            json
    
    Font-End:
        JavaScript:
            React
    

# Useful Websites

* [Asynchronous I/O](https://docs.python.org/3/library/asyncio.html)
* [React](https://react.dev/)

# Future Work

{Make a list of things that you need to fix, improve, and add in the future.}
* Finish a game
* Keep all users data in local storage of the browser
* Login with social media and keep a score in a data base