# URL Shortener — URL Lifecycle State Diagram

```mermaid
stateDiagram-v2
    [*] --> Active : POST /shorten creates URL

    Active --> Expired : expires_at timestamp reached
    Active --> Deleted : DELETE /:code called

    Expired --> Deleted : DELETE /:code called or cleanup job

    Deleted --> [*]

    Active : GET /:code returns 301 redirect
    Active : Analytics events are recorded

    Expired : GET /:code returns 410 Gone
    Expired : Analytics data still accessible

    Deleted : GET /:code returns 410 Gone
    Deleted : Analytics data preserved
```
