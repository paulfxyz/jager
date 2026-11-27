"""Understanding the human: from "delete 2 and 4" to a structured Intent.

The cheapest, fastest and most predictable brain is a regular expression.
So Jager works in two tiers:

  Tier 1 (this file, free, instant, offline): rules for English and French that
          cover the commands people actually type.
  Tier 2 (brain.py, costs a fraction of a cent): an AI model, asked ONLY when
          the rules shrug. It must answer in a strict JSON shape, and anything
          it says is validated here before it can become an Intent.

Why bother with tier 1? Efficiency (most messages never touch the network),
stability (it works when OpenRouter is down) and safety (a regex cannot be
sweet-talked by a hostile comment).

Intent kinds
------------
recap, delete, delete_all, keep, comments, sprint_comments, sprint_cleanup,
night, timer, stop_rules, status, help, pause, resume, stop, yes, no,
send, edit, hide, delete_comment, skip, jagerbomb (an easter egg), unknown
"""

from __future__ import annotations

import re
import unicodedata

from .models import Intent

KINDS = {
    "recap", "delete", "delete_all", "keep", "comments", "sprint_comments", "sprint_cleanup", "night",
    "timer", "stop_rules", "status", "help", "pause", "resume", "stop", "yes", "no", "send", "edit",
    "hide", "delete_comment", "skip", "jagerbomb", "unknown",
}

MAX_INPUT = 500   # characters: longer messages are truncated before parsing (cheap abuse protection)


def _norm(text: str) -> str:
    """Lowercase, strip accents and punctuation noise: 'Supprimé !' -> 'supprime'."""
    t = unicodedata.normalize("NFKD", text.strip().lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t.replace("’", "'"))


def numbers_in(text: str) -> list[int]:
    """Extract list positions: '2 and 4', '2, 4', '2 et 4', '1-3' -> [2, 4] / [1, 2, 3]. Sorted, unique, 1..99."""
    out: set[int] = set()
    for a, b in re.findall(r"\b(\d{1,2})\s*(?:-|to|a|à)\s*(\d{1,2})\b", text):
        lo, hi = sorted((int(a), int(b)))
        out.update(range(lo, min(hi, 99) + 1))
    text = re.sub(r"\b\d{1,2}\s*(?:-|to|a|à)\s*\d{1,2}\b", " ", text)
    out.update(int(n) for n in re.findall(r"\b(\d{1,2})\b", text) if 0 < int(n) < 100)
    return sorted(out)


YES = {"yes", "y", "yep", "yeah", "confirm", "do it", "ok", "oui", "o", "ouais", "confirme", "vas-y", "vas y", "go"}
NO = {"no", "n", "nope", "cancel", "non", "annule", "abort", "nah"}   # note: "stop" is its own intent (it ends a sprint)


def parse(text: str) -> Intent:
    """Rules-only parser. Always returns an Intent (``unknown`` when it has no idea)."""
    raw = text[:MAX_INPUT]
    t = _norm(raw)
    nums = numbers_in(t)

    if t in YES:
        return Intent("yes")
    if t in NO:
        return Intent("no")

    # Easter egg first: it must beat "help"-ish matches.
    if re.search(r"\bjager ?bomb\b|\bshots?\b.*\bjager\b|\b56 herbs\b|\bcheers\b|\bsante\b|\bya-?guerr\b", t):
        return Intent("jagerbomb")

    if re.search(r"\b(help|aide|commands?|commandes?|what can you do|que sais-tu)\b", t):
        return Intent("help")
    if re.search(r"\bstatus\b|\bstatut\b|\bca va\b|\bhow are you\b", t):
        return Intent("status")
    if re.fullmatch(r"(pause|mute|silence|tais-toi)", t):
        return Intent("pause")
    if re.fullmatch(r"(resume|unpause|reprends?|continue)", t):
        return Intent("resume")
    if re.search(r"\b(stop (the )?(rules?|timer|auto)|arrete (les )?(regles?|minuteur))\b", t):
        return Intent("stop_rules")

    # Timers: "delete everything I post tonight / in the next 8 hours, 1 hour after I post it"
    if re.search(r"\b(delete|remove|supprime\w*|efface\w*)\b.*\b(post|publie|tweet)\b.*\b(tonight|ce soir|next|prochaine?s?|cette nuit)\b", t) \
            or re.search(r"\b(tonight|ce soir|cette nuit)\b.*\b(delete|supprime\w*|efface\w*)\b", t):
        hours = re.search(r"(?:next|prochaine?s?)\s+(\d{1,2})\s*(?:h|hours?|heures?)", t)
        delay = re.search(r"(\d{1,3})\s*(hours?|heures?|h|minutes?|min)\s*(?:after|apres)", t)
        d_hours = int(hours.group(1)) if hours else (8 if re.search(r"tonight|ce soir|cette nuit", t) else 8)
        d_delay = 60
        if delay:
            n = int(delay.group(1))
            d_delay = n * 60 if delay.group(2).startswith(("h", "hour", "heure")) else n
        return Intent("timer", args={"hours": min(d_hours, 24), "delay_min": max(1, min(d_delay, 24 * 60))})

    if re.search(r"\b(night sprint|sprint de nuit|i'?m going out|je sors)\b", t):
        return Intent("night")
    if re.search(r"\b(comment|commentaire)s?\b.*\bsprint\b|\bsprint\b.*\b(comment|commentaire)", t):
        return Intent("sprint_comments")
    if re.search(r"\b(cleanup|clean up|nettoy\w*)\b.*\bsprint\b|\bsprint\b.*\b(cleanup|nettoy\w*)", t):
        return Intent("sprint_cleanup")
    if re.search(r"\b(comments?|commentaires?)\b", t) and re.search(r"\b(new|nouveau\w*|what|quoi|qu'est|any|des)\b|\?$", t):
        return Intent("comments")

    if re.search(r"\b(what|qu'est-ce|quels?|show|montre|liste|list|recap)\b.*\b(post|publi|week|semaine|recap)|\brecap\b|\bwhat did i post\b", t):
        return Intent("recap")

    if re.search(r"\b(keep|garde\w*|protege\w*)\b", t) and nums:
        return Intent("keep", nums)
    if re.search(r"\b(delete|remove|supprime\w*|efface\w*|enleve\w*)\b", t):
        if re.search(r"\b(all|everything|tout|toutes?)\b", t) and not nums:
            return Intent("delete_all")
        if nums:
            return Intent("delete", nums)

    # Sprint conversation words (only meaningful while a comment sprint is running, core.py decides).
    first = t.split(" ", 1)[0] if t else ""
    if first in {"send", "envoie", "envoyer"}:
        return Intent("send", nums)
    if first in {"edit", "modifie"}:
        return Intent("edit", args={"text": raw.split(None, 1)[1].strip() if len(raw.split(None, 1)) > 1 else ""})
    if first in {"hide", "cache", "masque"}:
        return Intent("hide", nums)
    if first in {"skip", "next", "suivant", "passe"}:
        return Intent("skip")
    if first in {"delete", "supprime"} and not nums:
        return Intent("delete_comment")
    if t in {"stop", "enough", "assez", "fini"}:
        return Intent("stop")

    return Intent("unknown", args={"text": raw})


def from_ai(data: dict) -> Intent:
    """Validate an AI answer. The model proposes, this function disposes.

    Anything off-schema becomes ``unknown``. Numbers are clamped. The AI can never
    produce a ``yes`` (confirmations must come from the human, in the chat, in their
    own words), which closes the "AI confirms its own delete" hole.
    """
    kind = str(data.get("kind", "unknown"))
    if kind not in KINDS or kind in {"yes", "no", "jagerbomb"}:
        return Intent("unknown", source="ai")
    nums = [int(n) for n in data.get("numbers", []) if isinstance(n, int) and 0 < n < 100][:20]
    args = {k: v for k, v in (data.get("args") or {}).items() if isinstance(k, str) and isinstance(v, (str, int))}
    return Intent(kind, nums, args, source="ai")
