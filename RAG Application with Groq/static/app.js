async function uploadFiles() {

  const input = document.getElementById("files");

  const data = new FormData();

  for (let file of input.files) {
    data.append("files", file);
  }

  await fetch("/upload", {
    method: "POST",
    body: data
  });

  addMsg("Documents indexed successfully ✅", "bot");
}

function addMsg(text, cls) {

  const chat = document.getElementById("chat");

  const div = document.createElement("div");

  div.className = "msg " + cls;

  div.innerText = text;

  chat.appendChild(div);

  chat.scrollTop = chat.scrollHeight;
}

function handleKey(e) {
  if (e.key === "Enter") ask();
}

async function ask() {

  const input = document.getElementById("question");

  const q = input.value.trim();

  if (!q) return;

  addMsg(q, "user");

  input.value = "";

  addMsg("Typing...", "bot");

  const res = await fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: q })
  });

  const data = await res.json();

  document.querySelector(".bot:last-child").innerText = data.answer;
}