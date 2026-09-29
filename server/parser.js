import { Readability } from "@mozilla/readability";

export default {
  async fetch(request) {
    try {
      const url = new URL(request.url);

      let encoded = url.pathname.slice(1);

      if (!encoded) {
        return new Response("Missing encoded URL", { status: 400 });
      }

      const targetUrl =
        "https://" +
        encoded
          .replace(/\+/g, ".")
          .replace(/-/g, "/");

      const response = await fetch(targetUrl, {
        headers: {
          "User-Agent": "Nannite/1.0"
        }
      });

      const html = await response.text();

      const doc = new DOMParser().parseFromString(
        html,
        "text/html"
      );

      const article = new Readability(doc).parse();

      if (!article) {
        return new Response("Could not parse article", {
          status: 500
        });
      }

      let content = article.content;

      const base = new URL(targetUrl);

      content = rewriteMedia(content, base);

      const output = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>${escapeHtml(article.title)}</title>
<style>
body{
  max-width:900px;
  margin:auto;
  padding:20px;
  font-family:system-ui,sans-serif;
}
img,video,iframe{
  max-width:100%;
  height:auto;
}
</style>
</head>
<body>
<h1>${escapeHtml(article.title)}</h1>
${content}
</body>
</html>`;

      return new Response(output, {
        headers: {
          "content-type": "text/html;charset=utf-8",
          "access-control-allow-origin": "*"
        }
      });
    } catch (err) {
      return new Response(String(err), {
        status: 500
      });
    }
  }
};

function rewriteMedia(html, base) {
  const doc = new DOMParser().parseFromString(
    html,
    "text/html"
  );

  // Images
  doc.querySelectorAll("img").forEach(img => {
    const src = img.getAttribute("src");

    if (!src) return;

    img.src = new URL(src, base).href;
  });

  // Videos
  doc.querySelectorAll("video").forEach(video => {
    const src = video.getAttribute("src");

    if (src) {
      video.src = new URL(src, base).href;
    }

    video.querySelectorAll("source").forEach(source => {
      const s = source.getAttribute("src");

      if (s) {
        source.src = new URL(s, base).href;
      }
    });
  });

  // Iframes (YouTube, Vimeo, etc.)
  doc.querySelectorAll("iframe").forEach(frame => {
    const src = frame.getAttribute("src");

    if (!src) return;

    frame.src = new URL(src, base).href;
  });

  // Embedded objects
  doc.querySelectorAll("embed,object").forEach(el => {
    const data = el.getAttribute("data");

    if (data) {
      el.setAttribute(
        "data",
        new URL(data, base).href
      );
    }
  });

  return doc.body.innerHTML;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
