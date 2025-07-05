let thread_id = null;
const chatDiv = document.getElementById("chat");
const input   = document.getElementById("input");
const form    = document.getElementById("form");
let evtSource = null;
let streamingP = null;

function appendStreamStart(role) {
    streamingP = document.createElement("p");
    streamingP.className = `msg ${role}`;
    streamingP.textContent = (role === "user" ? "🙋 " : "🤖 ");
    chatDiv.appendChild(streamingP);
    chatDiv.scrollTop = chatDiv.scrollHeight;
  }
  
  function appendStreamChunk(chunk) {
    if (streamingP) {
      streamingP.textContent += chunk;
      chatDiv.scrollTop = chatDiv.scrollHeight;
    }
  }
  
  function appendStreamEnd() {
    streamingP = null; // 结束后清空引用
  }

function append(role, text) {
  const p = document.createElement("p");
  p.className = `msg ${role}`;
  p.textContent = (role === "user" ? "🙋 " : "🤖 ") + text;
  chatDiv.appendChild(p);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

form.onsubmit = async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  append("user", text);

  // 之后每次走 SSE 流式
  if (evtSource) evtSource.close();

  appendStreamStart("bot");

  // evtSource = new EventSource(`http://localhost:8000/chat/stream?message=${encodeURIComponent(text)}`);
  evtSource = new EventSource(`/chat/stream?message=${encodeURIComponent(text)}`);

  let botMsg = "";
  evtSource.onmessage = (e) => {
    if (e.data === "[DONE]") {
      appendStreamEnd();
      evtSource.close();
    } else {
      appendStreamChunk(e.data);
    }
  };

  input.value = "";
};
