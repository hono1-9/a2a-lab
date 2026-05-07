# A2A Assignment Report

---

## Section 3: Request & Response Structure — Schema Analysis

### Q1: Why does the request use a client-generated `id` rather than a server-generated one? What problem does this solve in distributed systems?

Using a client-generated `id` solves the **idempotency problem** in distributed systems.

When a client sends a request over a network, the response may never arrive due to a timeout, network failure, or server crash. Without a client-generated ID, the client has no safe way to retry — it cannot tell whether the server already processed the request or not, risking duplicate execution (e.g., charging a user twice).

By generating the `id` before sending, the client can safely retry the same request with the same `id`. The server can detect that it has already processed this `id` and return the cached result instead of executing the task again. This makes the operation **idempotent**: sending it once or ten times produces the same outcome.

Additionally, a client-generated ID allows the client to correlate responses to requests immediately, without waiting for the server to assign and return an ID first — which is especially useful in async or streaming workflows.

---

### Q2: The `status.state` can be `'working'`. Under what circumstances would a server return this state in a non-streaming call, and how should a client react?

In a non-streaming (synchronous) call, a server would return `status.state = 'working'` when the task has been **accepted but not yet completed** at response time. This can happen when:

- The task is computationally expensive and the server uses an async worker queue (e.g., the HTTP response is sent immediately while a background job runs).
- The server enforces a response timeout and returns early before the result is ready.
- The agent delegates the task to another agent and cannot block until that agent replies.

**How a client should react:**  
The client should implement a **polling loop** — periodically re-querying the server for the task status using the same `id` until the state transitions to `'completed'`, `'failed'`, or `'canceled'`. The client should apply a backoff strategy (e.g., exponential backoff) between polls to avoid overwhelming the server, and set a maximum retry limit to avoid infinite loops.

---

### Q3: What is the purpose of the `sessionId` field? Give a concrete example of two related tasks that should share a session.

The `sessionId` field groups multiple tasks into a **logical conversation or workflow session**. It allows the server to maintain context across requests — for example, remembering earlier messages, user preferences, or intermediate results — without the client having to resend all prior context with every request.

**Concrete example:**

Imagine a document-editing agent:

- **Task 1** (`sessionId: "session-abc"`): The user sends a long essay and asks the agent to identify grammar errors. The server processes the document and returns a list of corrections.
- **Task 2** (`sessionId: "session-abc"`): The user sends a follow-up — "Now rewrite only the third paragraph using those corrections." 

Because both tasks share the same `sessionId`, the server knows which document and which corrections are being referred to, without the client re-uploading the full essay. Without `sessionId`, the server would treat Task 2 as a completely new, context-free request and fail to understand the reference.

---

### Q4: The `parts` array supports types `text`, `file`, and `data`. Describe a realistic multi-agent workflow where all three part types appear in a single conversation.

**Scenario: Automated Research Report Generation**

Consider a multi-agent pipeline where a user asks for a market research report on a competitor:

1. **User → Orchestrator Agent** (`text` part):  
   The user sends a text message: *"Analyze the Q1 2025 earnings report for Company X and summarize the key financial risks."*

2. **Orchestrator → Document Agent** (`file` part):  
   The orchestrator fetches the PDF earnings report and forwards it to a Document Analysis Agent as a `file` part (`mimeType: application/pdf`, `url: https://...`), along with a text instruction to extract financial figures.

3. **Document Agent → Analytics Agent** (`data` part):  
   The Document Agent extracts structured numbers (revenue, operating costs, debt ratios) and sends them to an Analytics Agent as a `data` part — a structured JSON object like `{"revenue": 4200000, "operatingCost": 3100000, "debtRatio": 0.42}` — for risk scoring.

4. **Analytics Agent → Orchestrator** (`text` part):  
   The Analytics Agent returns a natural-language summary of the financial risks as a `text` part, which the orchestrator delivers back to the user.

This workflow naturally uses all three part types: `text` for human-readable instructions and results, `file` for binary documents, and `data` for structured machine-readable payloads passed between agents.

---

## Section 4: Cloud Run Deployment

### Q1: What does `--allow-unauthenticated` do, and what are the security implications?

The `--allow-unauthenticated` flag makes the Cloud Run service publicly accessible — anyone on the internet can send requests to the endpoint without providing any credentials or token.

Without this flag, Cloud Run requires every request to include a valid Google-signed identity token (e.g., via `Authorization: Bearer <token>`), and unauthenticated requests are rejected with HTTP 403.

**Security implications:**  
Allowing unauthenticated access is convenient for development and for public-facing APIs, but it introduces risk in production:

- **Anyone can invoke the service**, including malicious actors who could spam the endpoint, causing unexpected billing charges on Cloud Run and other GCP resources.
- There is **no access control** — any client can send arbitrary task payloads to the agent.
- For a production A2A deployment, the recommended approach is to remove `--allow-unauthenticated` and instead require callers to present a service account token, or place an API Gateway with authentication in front of the Cloud Run service.

In this assignment, `--allow-unauthenticated` is used to simplify testing and allow the A2A client to reach the server without managing credentials.

---

### Q2: What is a cold start, and how does it affect an A2A Server on Cloud Run?

A **cold start** occurs when Cloud Run needs to spin up a new container instance to handle an incoming request, because no warm instance is currently available. This happens after a period of inactivity (when Cloud Run scales the service down to zero instances) or during a sudden traffic spike that exceeds the capacity of existing instances.

During a cold start, the container must be pulled, the Python runtime must initialize, and the FastAPI application must load before the first request can be served. This adds **latency** — typically 1–5 seconds for a lightweight Python service like our Echo Agent — to that first request.

**Impact on an A2A Server:**  
For an A2A client, a cold start can cause the first `send_task` call to time out or appear slow, even though the server is healthy. This is especially problematic if the client has a short timeout configured.

**Mitigation strategies:**
- Set a **minimum instance count** of 1 (`--min-instances=1`) to keep at least one warm instance running at all times, eliminating cold starts at the cost of always paying for one instance.
- Increase the **client timeout** to tolerate occasional slow starts.
- Use Cloud Run's **startup CPU boost** feature to allocate extra CPU during container initialization, reducing cold start duration.

---

## Section 5: Vertex AI Agent Engine Deployment

### Q1: Cloud Run vs Agent Engine — operational burden and use-case fit

**Cloud Run** is a general-purpose serverless container platform. You are responsible for packaging your application into a Docker image, configuring the HTTP server (uvicorn), defining routes and request/response schemas, and managing the container lifecycle. The operational burden is moderate — you control everything, which gives flexibility but requires more boilerplate. Cloud Run is best suited for stateless HTTP services, including A2A servers that need full control over their API surface, custom middleware, or non-standard endpoints.

**Vertex AI Agent Engine** is a managed runtime purpose-built for AI agents. You provide a Python class with a `set_up()` and `query()` method, and Agent Engine handles packaging, deployment, scaling, and observability automatically. There is no Dockerfile to write and no HTTP server to configure. The operational burden is significantly lower for agent-specific workloads. Agent Engine is best suited for LangChain, LangGraph, or A2A-compatible agents that follow a standard request/response pattern, where built-in integration with Vertex AI services (models, vector stores, evaluation) is valuable.

In summary: Cloud Run offers more control and flexibility at the cost of more configuration; Agent Engine offers a simpler deployment experience tailored to AI agents at the cost of less control over the runtime environment.

---

### Q2: Why does the wrapper class use a synchronous `query()` method even though the underlying handler is async?

The `query()` method is synchronous because the Agent Engine runtime calls it from a standard (non-async) Python context — it does not run an event loop itself, so it cannot `await` a coroutine directly.

The underlying `handle_task()` function is defined as `async def` because it was written for FastAPI, which runs inside an asyncio event loop. To bridge the two worlds, the wrapper uses `asyncio.run(handle_task(fake_request))`, which creates a new event loop, runs the coroutine to completion, and returns the result synchronously.

This pattern — wrapping an async function with `asyncio.run()` inside a sync method — is a common adapter technique when integrating async code into synchronous frameworks or managed runtimes that do not natively support async execution.