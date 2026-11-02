\# Live Collaborative Code Interview \& Pair-Programming Platform



A real-time, low-latency collaborative coding room and technical interview workspace built with Python, FastAPI, WebSockets, and Microsoft's Monaco Editor (the engine powering VS Code).



\## Features

\- \*\*Real-Time Code Synchronization:\*\* Full-duplex WebSocket architecture broadcasting sub-millisecond document edits across connected candidate and interviewer clients.

\- \*\*Multi-Language Monaco Editor:\*\* Integrated syntax highlighting, themes, and boilerplate templates for JavaScript, Python, Java, and C++.

\- \*\*Room State Management:\*\* Dynamic session partitioning supporting concurrent, isolated interview rooms via parameterized routing.

\- \*\*Live Peer Roster \& Communication:\*\* Real-time active participant tracking and synchronized collaborative discussion chat.

\- \*\*Client-Side Execution Sandbox:\*\* In-browser runtime console evaluating solutions with real-time log capturing.



\## Tech Stack

\- \*\*Backend:\*\* Python 3, FastAPI, Uvicorn (ASGI), Native WebSockets (`asyncio`)

\- \*\*Frontend:\*\* Vanilla JavaScript (ES6+), Microsoft Monaco Editor API, Tailwind CSS, HTML5



\## Quick Start

1\. Clone the repository:

&#x20;  ```bash

&#x20;  git clone \[https://github.com/](https://github.com/)<your-username>/Live-Code-Interview-Platform.git

&#x20;  cd Live-Code-Interview-Platform

