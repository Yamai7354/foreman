# `start_session`

```mermaid
flowchart TD
    N1(["Start: start_session(description, project, tags)"])
    N3["store = ..."]
    N1 --> N3
    N4["current = ..."]
    N3 --> N4
    N5{{current}}
    N4 --> N5
    N6["Yes branch"]
    N5 -->|Yes| N6
    N7["log_warning(f"Session alr"]
    N6 --> N7
    N8["log_info("Use 'portfolio "]
    N7 --> N8
    N9(["return None"])
    N8 --> N9
    N10["session = ..."]
    N5 --> N10
    N11["store.add_session(session"]
    N10 --> N11
    N12["store.set_current_session"]
    N11 --> N12
    N13["console.print(Panel(f"[bo"]
    N12 --> N13
    N14["log_success("Session star"]
    N13 --> N14
```
