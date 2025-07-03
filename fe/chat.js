let thread_id = null;
const chatDiv = document.getElementById("chat");
const input   = document.getElementById("input");
const form    = document.getElementById("form");
let evtSource = null;

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

//   // 第一次请求：获取 thread_id
  if (!thread_id) {
    const res = await fetch("http://localhost:8000/chat/stream", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text})
    });
    const response = await res.text();
    thread_id = 'abc'
    // thread_id = json.thread_id;
    append("bot", response);  // 首次走普通回复
    return;
  }

  // 之后每次走 SSE 流式
  if (evtSource) evtSource.close();

  evtSource = new EventSource(`http://localhost:8000/chat/stream?message=${encodeURIComponent(text)}`);

  let botMsg = "";
  evtSource.onmessage = (e) => {
    if (e.data === "[DONE]") {
      append("bot", botMsg);
      evtSource.close();
    } else {
      botMsg += e.data;
    }
  };

  input.value = "";
};
