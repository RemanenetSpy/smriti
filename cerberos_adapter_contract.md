# CerberOS ↔ Smriti Adapter Contract

This is the proposed interface for integrating Smriti's temporal memory engine into `cerberOS` while strictly adhering to `hegu-1`'s architectural boundary:
1. **Conversation History** remains the inspectable source.
2. **Smriti Adapter** produces the derived temporal projection for fact validity.

## Proposed Python Interface (`cerberos/memory/temporal_adapter.py`)

```python
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class TemporalFact(BaseModel):
    fact_id: str
    subject: str
    predicate: str
    object: str
    valid_from: datetime
    valid_to: Optional[datetime] = None  # None means currently active
    provenance_turn_id: str              # Pointer back to raw transcript

class SmritiTemporalAdapter:
    """
    Adapter bridging cerberOS memory orchestrator and Smriti API.
    Does not replace raw transcript history.
    """
    
    def __init__(self, api_key: str, endpoint: str = "https://api.smriti.dev/v1"):
        self.api_key = api_key
        self.endpoint = endpoint

    async def ingest_session_snapshot(self, session_id: str, turns: List[dict]) -> bool:
        """
        Asynchronously fires recent conversation turns to Smriti to extract 
        SVO events and calculate supersession (closing valid_to on old facts).
        Non-blocking to the main agent hot-path.
        """
        pass

    async def get_active_facts(self, user_id: str, as_of: Optional[datetime] = None) -> List[TemporalFact]:
        """
        Retrieves the exact factual state of the user. 
        If `as_of` is None, returns current active truths (`valid_to IS NULL`).
        If `as_of` is provided, reconstructs historical state (`valid_from <= as_of AND valid_to > as_of`).
        """
        pass

    async def get_handoff_state(self, session_id: str) -> dict:
        """
        Generates the execution-continuity object required for worker handoff,
        enriched with temporal fact validity.
        """
        pass
```

## How we present this to `hegu-1`:
If `hegu-1` replies and asks to see the draft, we can submit this exact interface as a GitHub Gist or PR. It demonstrates that we listened to his concern ("extraction stays asynchronous", "adapter failure semantics") and correctly isolated the temporal projection from the raw transcript base!
