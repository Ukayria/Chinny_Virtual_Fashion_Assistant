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

    // show shape & category (even if it's an error message like "Body not detected")
    document.getElementById("shape").textContent = result.shape || "Unknown";
    document.getElementById("category").textContent = result.category || "Unknown";

    const recDiv = document.getElementById("recommendations");
    recDiv.innerHTML = "";

    if (!Array.isArray(result.recommendations) || result.recommendations.length === 0) {
      const p = document.createElement("p");
      p.textContent = "No recommendations available.";
      recDiv.appendChild(p);
      return;
    }

    // build cards for each recommendation
    result.recommendations.forEach(item => {
      const box = document.createElement("div");
      box.style.marginBottom = "20px";
      box.style.display = "inline-block";
      box.style.textAlign = "left";
      box.style.border = "1px solid #ddd";
      box.style.padding = "10px";
      box.style.borderRadius = "8px";
      box.style.width = "300px";
      box.style.boxShadow = "0 2px 6px rgba(0,0,0,0.08)";
      box.style.marginRight = "12px";

      // image 
      if (item.image) {
        const img = document.createElement("img");
        img.src = "/" + item.image.replace(/^\/+/, ""); 
        img.width = 260;
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

      recDiv.appendChild(box);
    });

  } catch (err) {
    console.error(err);
    alert("An unexpected error occurred. Check the browser console for details.");
  }
});
