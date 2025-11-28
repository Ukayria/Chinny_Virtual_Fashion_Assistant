// static/script.js
const form = document.getElementById("uploadForm");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("fileInput");
  const styleSelect = document.getElementById("style");

  if (fileInput.files.length === 0) {
    alert("Please upload an image.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("style", styleSelect.value);

  try {
    const resp = await fetch("/analyze", {
      method: "POST",
      body: formData
    });

    if (!resp.ok) {
      const err = await resp.json().catch(()=>({error: "Server error"}));
      alert(err.error || "Upload failed");
      return;
    }

    const result = await resp.json();

    // update shape & category spans
    document.getElementById("shape").textContent = result.shape || "Unknown";
    document.getElementById("category").textContent = result.category || "Unknown";

    // ensure a recommendation header exists (create if missing)
    let header = document.getElementById("result-title");
    if (!header) {
      header = document.createElement("h2");
      header.id = "result-title";
      header.style.textAlign = "left";
      header.style.maxWidth = "900px";
      header.style.margin = "20px auto 0 auto";
      const container = document.querySelector(".results");
      container.insertBefore(header, container.querySelector("#recommendations"));
    }

    const recDiv = document.getElementById("recommendations");
    recDiv.innerHTML = "";

    const recs = Array.isArray(result.recommendations) ? result.recommendations : [];

    header.textContent = `Chinny recommends these ${recs.length} outfit${recs.length===1?"":"s"} for your ${result.shape} shape`;

    if (recs.length === 0) {
      const p = document.createElement("p");
      p.textContent = "No recommendations available.";
      recDiv.appendChild(p);
      return;
    }

    // build cards for each recommendation
    recs.forEach((item, idx) => {
      const box = document.createElement("div");
      box.className = "rec-card";
      box.style.marginBottom = "20px";
      box.style.display = "inline-block";
      box.style.textAlign = "left";
      box.style.border = "1px solid #ddd";
      box.style.padding = "10px";
      box.style.borderRadius = "8px";
      box.style.width = "300px";
      box.style.boxShadow = "0 2px 6px rgba(0,0,0,0.08)";
      box.style.marginRight = "12px";
      box.style.verticalAlign = "top";

      // image 
      if (item.image) {
        const img = document.createElement("img");
        img.src = "/" + item.image.replace(/^\/+/, ""); 
        img.style.width = "100%";
        img.style.borderRadius = "6px";
        img.style.display = "block";
        img.style.marginBottom = "8px";
        box.appendChild(img);
      }

      const title = document.createElement("div");
      title.className = "price-title";
      title.textContent = `Cost per yard: ₦${item.price ?? "N/A"}`;
      box.appendChild(title);

      // fabrics list
      const fab = document.createElement("div");
      fab.style.marginBottom = "6px";
      fab.innerHTML = `<strong>Fabrics:</strong> ${(item.fabrics || []).join(", ")}`;
      box.appendChild(fab);

      // breakdown lines
      const bd = document.createElement("div");
      bd.innerHTML = `<strong>Breakdown:</strong><br>` + ((item.price_breakdown || []).join("<br>"));
      box.appendChild(bd);

      // feedback row
      const fbRow = document.createElement("div");
      fbRow.style.marginTop = "10px";
      const up = document.createElement("button");
      up.textContent = "👍";
      up.style.marginRight = "8px";
      const down = document.createElement("button");
      down.textContent = "👎";
      const note = document.createElement("span");
      note.id = `fb-note-${idx}`;
      note.style.marginLeft = "12px";
      note.style.color = "#666";
      fbRow.appendChild(up);
      fbRow.appendChild(down);
      fbRow.appendChild(note);
      box.appendChild(fbRow);

      // handlers
      up.addEventListener("click", async () => {
        await sendFeedback(result.shape, result.category, item, 1, idx);
      });
      down.addEventListener("click", async () => {
        await sendFeedback(result.shape, result.category, item, 0, idx);
      });

      recDiv.appendChild(box);
    });

  } catch (err) {
    console.error(err);
    alert("An unexpected error occurred. Check the browser console for details.");
  }
});


async function sendFeedback(shape, style, item, rating, idx) {
  const payload = {
    shape: shape,
    style: style,
    recommendation: item.name || item.image || "",
    rating: rating
  };
  try {
    const resp = await fetch("/feedback", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    if (resp.ok) {
      document.getElementById(`fb-note-${idx}`).textContent = rating === 1 ? "Thanks — saved" : "Feedback noted";
    } else {
      document.getElementById(`fb-note-${idx}`).textContent = "Error saving feedback";
    }
  } catch (err) {
    document.getElementById(`fb-note-${idx}`).textContent = "Network error";
  }
}
