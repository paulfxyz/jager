"""Every word Jager says, in English and French.

All user-facing strings live here and nowhere else. Want Jager in Spanish,
Hebrew or Klingon? Copy a column, translate it, send a pull request. The
tests check that every key exists in every language, so you cannot forget
one (the test suite is a very strict friend).

Voice guide: warm, cheeky, a bit Gen Z, never cruel. Jager teases YOU, never
the people in your comments. Jägermeister puns are legal here.
(56 herbs, a stag, and one very questionable Tuesday.)

A value may be a string or a tuple of strings: tuples are variants and one is
picked at random, because hearing the same joke twice is how friendships end.
"""

from __future__ import annotations

import random

LANGS = ("en", "fr")

S: dict[str, dict[str, str | tuple[str, ...]]] = {
    # ------------------------------------------------------------------ chat
    "hello": {
        "en": "Hey, it's Jager. I woke up on your server and I already have opinions. Say \"help\" to see what I can do.",
        "fr": "Salut, c'est Jager. Je me suis réveillé sur ton serveur et j'ai déjà des avis. Dis \"aide\" pour voir ce que je sais faire.",
    },
    "help": {
        "en": ("Things you can say:\n"
               "- what did I post this week?\n- delete 2 and 4 / delete all\n- keep 3\n"
               "- comments / start a comment sprint\n- cleanup sprint\n"
               "- delete everything I post tonight, 1 hour after\n- stop rules\n- pause / resume / status\n"
               "I always ask YES before deleting anything. Always."),
        "fr": ("Ce que tu peux dire :\n"
               "- qu'est-ce que j'ai publié cette semaine ?\n- supprime 2 et 4 / supprime tout\n- garde 3\n"
               "- commentaires / lance un sprint commentaires\n- sprint nettoyage\n"
               "- supprime tout ce que je publie ce soir, 1 heure après\n- stop règles\n- pause / reprends / statut\n"
               "Je demande toujours OUI avant de supprimer quoi que ce soit. Toujours."),
    },
    "status": {
        "en": "Awake. {accounts} accounts connected, {rules} auto-delete rules running, AI {ai}, dry run {dry}. 56 herbs: all present.",
        "fr": "Réveillé. {accounts} comptes connectés, {rules} règles de suppression actives, IA {ai}, mode test {dry}. 56 plantes : toutes présentes.",
    },
    "on": {"en": "on", "fr": "activée"}, "off": {"en": "off", "fr": "désactivée"},
    "yes_word": {"en": "yes", "fr": "oui"}, "no_word": {"en": "no", "fr": "non"},
    "paused": {"en": "I'm paused. Say \"resume\" and I'm back, slightly dusty.", "fr": "Je suis en pause. Dis \"reprends\" et je reviens, un peu poussiéreux."},
    "resumed": {"en": "Back. Did I miss anything? (Do not answer that.)", "fr": "De retour. J'ai raté quelque chose ? (Ne réponds pas.)"},
    "unknown": {
        "en": ("I did not get that. Say \"help\" and I'll show you my party tricks.",
               "Hmm, no idea. Say \"help\" and I'll show you what I know.",
               "That sounded important and also incomprehensible. Try \"help\"."),
        "fr": ("Pas compris. Dis \"aide\" et je te montre mes tours de magie.",
               "Hmm, aucune idée. Dis \"aide\" et je te montre ce que je sais faire.",
               "Ça avait l'air important et incompréhensible à la fois. Essaie \"aide\"."),
    },
    "unknown_night": {
        "en": "It's the middle of the night and I did not understand you. Whatever you are about to post: sleep on it. I'll still be here.",
        "fr": "Il est en pleine nuit et je n'ai rien compris. Quoi que tu t'apprêtes à publier : dors dessus. Je serai toujours là.",
    },
    "jagerbomb": {
        "en": ("Cheers. A Jager bomb is just a shot of regret dropped into an energy drink, and I would know: I am made of 56 herbs and bad decisions. "
               "Drink some water. Then ask me what you posted."),
        "fr": ("Santé. Une Jager bomb, c'est juste un shot de regrets dans une boisson énergisante, et je sais de quoi je parle : je suis fait de 56 plantes et de mauvaises décisions. "
               "Bois de l'eau. Puis demande-moi ce que tu as publié."),
    },
    # ----------------------------------------------------------------- recap
    "recap_head": {"en": "Here's what you posted in the last 7 days:", "fr": "Voilà ce que tu as publié ces 7 derniers jours :"},
    "recap_none": {
        "en": "Nothing in the last 7 days. Either you were a saint or I cannot see your accounts. Both are plausible.",
        "fr": "Rien ces 7 derniers jours. Soit tu étais un saint, soit je ne vois pas tes comptes. Les deux sont plausibles.",
    },
    "recap_foot": {
        "en": "Reply \"delete 2 and 4\", \"delete all\" or \"keep 1\". Posts marked [no delete] are ones I am not allowed to remove.",
        "fr": "Réponds \"supprime 2 et 4\", \"supprime tout\" ou \"garde 1\". Les posts marqués [non supprimable] sont ceux que je n'ai pas le droit de retirer.",
    },
    "tag_nodelete": {"en": "[no delete]", "fr": "[non supprimable]"},
    "tag_kept": {"en": "(kept)", "fr": "(gardé)"},
    # -------------------------------------------------------------- deleting
    "ask_delete": {
        "en": "Delete {n} post(s) ({nums}) for good? Reply YES to confirm. Anything else cancels.",
        "fr": "Supprimer {n} publication(s) ({nums}) pour de bon ? Réponds OUI pour confirmer. Tout autre message annule.",
    },
    "ask_delete_comment": {
        "en": "Delete this comment from {who} for good? Reply YES. Anything else cancels.",
        "fr": "Supprimer ce commentaire de {who} pour de bon ? Réponds OUI. Tout autre message annule.",
    },
    "ask_rule": {
        "en": "I'll delete what you post in the next {hours}h, {delay} minutes after each post, on {platforms}. Reply YES to start. Anything else cancels.",
        "fr": "Je supprimerai ce que tu publies dans les {hours} prochaines heures, {delay} minutes après chaque post, sur {platforms}. Réponds OUI pour lancer. Tout autre message annule.",
    },
    "cancelled": {"en": "Cancelled. Nothing was touched. (Cowardice is a valid strategy.)", "fr": "Annulé. Rien n'a été touché. (La prudence est une stratégie valable.)"},
    "nothing_pending": {"en": "There is nothing waiting for a yes. You are very agreeable though.", "fr": "Rien n'attend de oui. Tu es très conciliant, cela dit."},
    "nothing_deletable": {"en": "None of those can be deleted by me.", "fr": "Je ne peux supprimer aucun de ceux-là."},
    "need_listing": {
        "en": "Ask me \"what did I post this week?\" first, so we agree on the numbers.",
        "fr": "Demande-moi d'abord \"qu'est-ce que j'ai publié cette semaine ?\", pour qu'on soit d'accord sur les numéros.",
    },
    "bad_number": {"en": "I do not have a number {n} in the list.", "fr": "Je n'ai pas de numéro {n} dans la liste."},
    "skipped_protected": {"en": "Skipped {n} protected post(s).", "fr": "{n} publication(s) protégée(s) ignorée(s)."},
    "skipped_cannot": {"en": "{why}", "fr": "{why}"},
    "deleted": {"en": "Done. {n} post(s) deleted for good. {left} left in the list.", "fr": "Fait. {n} publication(s) supprimée(s) pour de bon. Il en reste {left}."},
    "deleted_dry": {
        "en": "Dry run: I pretended to delete {n} post(s). Nothing was touched. Set JAGER_DRY_RUN=false when you trust me.",
        "fr": "Mode test : j'ai fait semblant de supprimer {n} publication(s). Rien n'a été touché. Mets JAGER_DRY_RUN=false quand tu me fais confiance.",
    },
    "failed": {"en": "Could not delete {n}: {why}", "fr": "Impossible d'en supprimer {n} : {why}"},
    "already_gone": {"en": "#{n} is already gone. Numbers stay the same, so you never delete the wrong thing by accident.", "fr": "Le n°{n} n'existe déjà plus. Les numéros ne bougent pas, pour que tu ne supprimes jamais la mauvaise chose."},
    "kept": {"en": "Kept {nums}. I will never propose them again. They are safe, like grandma's jewellery.", "fr": "Gardé : {nums}. Je ne les proposerai plus jamais. Ils sont à l'abri, comme les bijoux de mamie."},
    # ----------------------------------------------------------------- rules
    "rule_on": {"en": "Rule on. I'll keep an eye out. Say \"stop rules\" to end it.", "fr": "Règle activée. Je surveille. Dis \"stop règles\" pour l'arrêter."},
    "rule_nothing": {"en": "I cannot delete anything on your connected accounts, so there is nothing to automate.", "fr": "Je ne peux rien supprimer sur tes comptes connectés, donc rien à automatiser."},
    "rule_ran": {"en": "Rule ran: {n} post(s) deleted after their timer.", "fr": "Règle exécutée : {n} publication(s) supprimée(s) après leur minuteur."},
    "rules_stopped": {"en": "Stopped {n} rule(s). The night is yours again.", "fr": "{n} règle(s) arrêtée(s). La nuit t'appartient de nouveau."},
    # -------------------------------------------------------------- comments
    "comments_none": {"en": "No new comments waiting. Peaceful. Suspicious, even.", "fr": "Aucun nouveau commentaire. C'est paisible. Suspect, même."},
    "comments_sum": {"en": "{n} comment(s) waiting on {posts} post(s). Say \"start a comment sprint\" and we will go through them one by one.", "fr": "{n} commentaire(s) en attente sur {posts} publication(s). Dis \"lance un sprint commentaires\" et on les passe un par un."},
    "sprint_intro": {"en": "Comment sprint: {n} to go. I'll show them one at a time.", "fr": "Sprint commentaires : {n} à traiter. Je te les montre un par un."},
    "sprint_item": {
        "en": "[{platform}] {author} ({cat}): \"{text}\"\n{draft}Say: send / edit <your text> / hide / delete / skip / stop",
        "fr": "[{platform}] {author} ({cat}) : \"{text}\"\n{draft}Dis : envoie / edit <ton texte> / cache / supprime / passe / stop",
    },
    "draft_line": {"en": "Draft: \"{d}\"\n", "fr": "Brouillon : \"{d}\"\n"},
    "no_draft": {"en": "I have no draft for this one. Say: edit <your reply>.", "fr": "Je n'ai pas de brouillon pour celui-là. Dis : edit <ta réponse>."},
    "sent": {"en": "Sent.", "fr": "Envoyé."}, "sent_dry": {"en": "Dry run: reply NOT sent.", "fr": "Mode test : réponse NON envoyée."},
    "hid": {"en": "Hidden.", "fr": "Masqué."}, "hid_dry": {"en": "Dry run: nothing hidden.", "fr": "Mode test : rien masqué."},
    "cannot": {"en": "{why}", "fr": "{why}"},
    "comment_deleted": {"en": "Comment deleted.", "fr": "Commentaire supprimé."},
    "skip": {"en": "Skipped.", "fr": "Ignoré."},
    "no_sprint": {"en": "There is no sprint running. Say \"start a comment sprint\".", "fr": "Aucun sprint en cours. Dis \"lance un sprint commentaires\"."},
    "sprint_done": {
        "en": "Sprint over. Replied {sent}, hidden {hid}, deleted {dele}, skipped {skip}. Go outside.",
        "fr": "Sprint terminé. Répondu {sent}, masqué {hid}, supprimé {dele}, ignoré {skip}. Va prendre l'air.",
    },
    "cleanup_none": {"en": "Nothing older than 90 days in what I can see. Tidy human.", "fr": "Rien de plus vieux que 90 jours dans ce que je vois. Humain bien rangé."},
    "cleanup_head": {"en": "Cleanup sprint: posts older than 90 days that I can see:", "fr": "Sprint nettoyage : publications de plus de 90 jours que je peux voir :"},
    # --------------------------------------------------------------- weekly
    "weekly": {
        "en": "Sunday check-in. Week in review:",
        "fr": "Point du dimanche. Revue de la semaine :",
    },
    "weekly_cta": {"en": "Start a sprint? Say \"start a comment sprint\" or \"later\".", "fr": "On lance un sprint ? Dis \"lance un sprint commentaires\" ou \"plus tard\"."},
    "error": {"en": "Something went wrong on my side, and I have logged it. Nothing was deleted by accident.", "fr": "Un souci de mon côté, je l'ai noté. Rien n'a été supprimé par accident."},
}


def tr(lang: str, key: str, **kw) -> str:
    """Translate ``key`` into ``lang`` (falls back to English), picking a random variant if there are several."""
    entry = S[key]
    val = entry.get(lang) or entry["en"]
    if isinstance(val, tuple):
        val = random.choice(val)  # nosec B311 - picking a joke, not a key
    return val.format(**kw) if kw else val


def missing() -> list[tuple[str, str]]:
    """(key, lang) pairs that lack a translation. The test suite insists this is empty."""
    return [(k, lg) for k, v in S.items() for lg in LANGS if lg not in v]
