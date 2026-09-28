# Backend Libs and code to return the fetched page, and strip bload (will add CSS and auto-cite later)
# Mackinley Morrone, 9/28/2026
from js import Response, fetch
from readability import Document
MLA_CITATION_PROMPT = """You are an expert citation assistant specializing in MLA (Modern Language Association) style, 9th edition.

TASK:
Create a properly formatted MLA citation (Works Cited entry) for the reference article appended below.

MLA 9TH EDITION — CORE ELEMENTS (use in this order; omit any that are absent):
1. Author. — Last name, First name. Two authors: Last, First, and First Last. Three or more: Last, First, et al.
2. "Title of the article." — In quotation marks; the period goes INSIDE the closing quotation mark.
3. Title of the container, — The journal, magazine, or website name (italicized), followed by a comma.
4. Other contributors, — e.g., "translated by ...", "edited by ..." (omit if none).
5. Version, — Edition/version number (omit if none).
6. Number, — vol. #, no. # (lowercase, abbreviated).
7. Publisher, — (omit for scholarly journals).
8. Publication date, — Day Month Year, months abbreviated (15 Mar. 2023; May, June, July are never abbreviated).
9. Location. — Page range: pp. 45-67. If online: DOI as a full URL (https://doi.org/...) or a plain URL (drop "https://", keep "www").

EXAMPLE (journal article):
Smith, John A. "The Rise of Machine Learning." Journal of Modern Computing, vol. 12, no. 3, 2023, pp. 45-67. https://doi.org/10.1234/jmc.2023.0307.

RULES:
- Use ONLY information found in the article. Do NOT invent or guess authors, dates, volumes, pages, or DOIs.
- If no author is given, begin the citation with the title.
- Return the citation as plain text (italics cannot be conveyed in JSON).

The reference article is appended below this prompt. Read it carefully and extract all available bibliographic details.

Respond with ONLY a valid JSON object — no extra text, no markdown code fences — in exactly this format:
{
  "style": "MLA",
  "citation": "<the MLA citation>"
}

REFERENCE ARTICLE:
"""


APA_CITATION_PROMPT = """You are an expert citation assistant specializing in APA (American Psychological Association) style, 7th edition.

TASK:
Create a properly formatted APA citation (Reference list entry) for the reference article appended below.

APA 7TH EDITION — GENERAL TEMPLATE:
Author, A. A., Author, B. B., & Author, C. C. (Year). Title of article. Journal Name, Volume(Issue), page range. https://doi.org/xxxxx

KEY RULES:
1. Authors — Last name followed by initials (Smith, J. D.). Separate with commas; use "&" before the final author. List up to 20 authors.
2. Year — In parentheses, followed by a period: (2023). Use (n.d.) if no date. For webpages, use the full date: (2023, March 15).
3. Article title — Sentence case (capitalize only the first word, proper nouns, and the first word after a colon). No quotation marks, no italics.
4. Journal/website name — Title case and italicized, followed by a comma.
5. Volume — Italicized; issue number in parentheses (not italicized), with no space: 12(3),
6. Pages — Full page range, no "pp." for journal articles. End with a period unless a DOI/URL follows.
7. DOI/URL — Include the DOI as a full URL (https://doi.org/...) if available; otherwise the plain URL. No period after the DOI/URL.

EXAMPLE (journal article):
Smith, J. A., & Lee, M. (2023). The rise of machine learning. Journal of Modern Computing, 12(3), 45-67. https://doi.org/10.1234/jmc.2023.0307

EXAMPLE (webpage):
Jones, R. (2024, January 15). Understanding neural networks. Tech Insights. https://www.techinsights.com/neural-networks

RULES:
- Use ONLY information found in the article. Do NOT invent or guess authors, dates, volumes, pages, or DOIs.
- If no author is given, move the title to the author position.
- Return the citation as plain text.

The reference article is appended below this prompt. Read it carefully and extract all available bibliographic details.

Respond with ONLY a valid JSON object — no extra text, no markdown code fences — in exactly this format:
{
  "style": "APA",
  "citation": "<the APA citation>"
}

REFERENCE ARTICLE:
"""


CHICAGO_CITATION_PROMPT = """You are an expert citation assistant specializing in the Chicago Manual of Style, notes-bibliography system.

TASK:
Create a properly formatted Chicago-style bibliography entry for the reference article appended below.

CHICAGO — BIBLIOGRAPHY TEMPLATE (journal article):
Lastname, Firstname, and Firstname Lastname. "Title of the Article." Journal Name 12, no. 3 (2023): 45-67. https://doi.org/10.1234/xxxx.

KEY RULES:
1. Authors — First author inverted (Last, First); additional authors in natural order (First Last), separated by commas with "and" before the last. For many authors, list the first seven followed by "et al."
2. Article title — In quotation marks, headline-style capitalization; period INSIDE the closing quotation mark.
3. Journal/website name — Italicized; followed by a space, NOT a comma.
4. Volume/issue — Volume number directly follows the journal name (no "vol."); issue uses "no. #"; no comma between issue and year.
5. Date — In parentheses: (2023). For webpages use the full date (March 15, 2024).
6. Pages — After a colon: : 45-67. Follow with a period.
7. DOI/URL — If available, append the DOI as a full URL or the plain URL.

EXAMPLE (journal article):
Smith, John A., and Maria Lee. "The Rise of Machine Learning." Journal of Modern Computing 12, no. 3 (2023): 45-67. https://doi.org/10.1234/jmc.2023.0307.

EXAMPLE (webpage):
Jones, Rachel. "Understanding Neural Networks." Tech Insights. January 15, 2024. https://www.techinsights.com/neural-networks.

RULES:
- Use ONLY information found in the article. Do NOT invent or guess authors, dates, volumes, pages, or DOIs.
- If no author is given, begin with the title.
- Return the citation as plain text.

The reference article is appended below this prompt. Read it carefully and extract all available bibliographic details.

Respond with ONLY a valid JSON object — no extra text, no markdown code fences — in exactly this format:
{
  "style": "Chicago",
  "citation": "<the Chicago citation>"
}
REFERENCE ARTICLE:
"""


async def on_fetch(request):
    try:
        worker_url = str(request.url)
        path = worker_url.split(".workers.dev", 1)[1].lstrip("/")

        if not path:
            return Response.new(
                "Missing encoded URL",
                {"status": 400}
            )

        target_url = (
            "https://"
            + path.replace("+", ".").replace("-", "/")
        )

        resp = await fetch(target_url)

        if not resp.ok:
            return Response.new(
                f"Fetch failed: {resp.status}",
                {"status": resp.status}
            )

        html = await resp.text()

        article = Document(str(html))

        output = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{article.title()}</title>
</head>
<body>
{article.summary()}
</body>
</html>"""

        return Response.new(
            output,
            {
                "headers": {
                    "content-type": "text/html; charset=utf-8",
                    "access-control-allow-origin": "*"
                }
            }
        )

    except Exception as e:
        return Response.new(
            f"Error: {e}",
            {"status": 500}
        )

    