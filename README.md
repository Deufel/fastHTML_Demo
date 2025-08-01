# fastHTML_Demo

## A small example showing how to use sse-starlette for datastar responses

## RUN
```bash
python main.py
```

## Dependencey Tree
```bash
datastar v0.1.0
├── aiohttp v3.12.15
│   ├── aiohappyeyeballs v2.6.1
│   ├── aiosignal v1.4.0
│   │   ├── frozenlist v1.7.0
│   │   └── typing-extensions v4.14.1
│   ├── attrs v25.3.0
│   ├── frozenlist v1.7.0
│   ├── multidict v6.6.3
│   ├── propcache v0.3.2
│   └── yarl v1.20.1
│       ├── idna v3.10
│       ├── multidict v6.6.3
│       └── propcache v0.3.2
├── apsw v3.50.3.0
├── datastar-py v0.6.3
├── psutil v7.0.0
├── python-fasthtml v0.12.22
│   ├── beautifulsoup4 v4.13.4
│   │   ├── soupsieve v2.7
│   │   └── typing-extensions v4.14.1
│   ├── fastcore v1.8.7
│   │   └── packaging v25.0
│   ├── fastlite v0.2.1
│   │   ├── apswutils v0.1.0
│   │   │   ├── apsw v3.50.3.0
│   │   │   └── fastcore v1.8.7 (*)
│   │   └── fastcore v1.8.7 (*)
│   ├── httpx v0.28.1
│   │   ├── anyio v4.9.0
│   │   │   ├── idna v3.10
│   │   │   ├── sniffio v1.3.1
│   │   │   └── typing-extensions v4.14.1
│   │   ├── certifi v2025.7.14
│   │   ├── httpcore v1.0.9
│   │   │   ├── certifi v2025.7.14
│   │   │   └── h11 v0.16.0
│   │   └── idna v3.10
│   ├── itsdangerous v2.2.0
│   ├── oauthlib v3.3.1
│   ├── python-dateutil v2.9.0.post0
│   │   └── six v1.17.0
│   ├── python-multipart v0.0.20
│   ├── starlette v0.47.2
│   │   ├── anyio v4.9.0 (*)
│   │   └── typing-extensions v4.14.1
│   └── uvicorn[standard] v0.35.0
│       ├── click v8.2.1
│       ├── h11 v0.16.0
│       ├── httptools v0.6.4 (extra: standard)
│       ├── python-dotenv v1.1.1 (extra: standard)
│       ├── pyyaml v6.0.2 (extra: standard)
│       ├── uvloop v0.21.0 (extra: standard)
│       ├── watchfiles v1.1.0 (extra: standard)
│       │   └── anyio v4.9.0 (*)
│       └── websockets v15.0.1 (extra: standard)
└── sse-starlette v3.0.2
    └── anyio v4.9.0 (*)
(*) Package tree already displayed
```
