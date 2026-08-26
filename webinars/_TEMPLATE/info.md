---
# ===== WEBINAR PAGE DATA =====
# Copy this whole _TEMPLATE folder, rename it to the webinar slug (lowercase-with-dashes),
# fill in the fields below, and drop speaker photos into ./speakers/
# Then tell Claude the slug and say "build this webinar page".

slug: "time-is-tissue"                      # folder name + URL: /webinars/time-is-tissue
title: "Time Is Tissue: Disrupting Biofilm to Prevent Amputation"
status: "on-demand"                          # on-demand | upcoming
date: "2026-05-14"                           # YYYY-MM-DD (event date or release date)
duration: "48 min"                           # optional, e.g. "1 hr 5 min"

summary: >
  One short paragraph describing what the webinar covers and who it is for.
  Evidence-based, no fear language, person-first.

# What viewers will learn (optional; 3-4 bullets)
takeaways:
  - "First learning objective"
  - "Second learning objective"
  - "Third learning objective"

# ===== SPEAKERS =====
# Add one block per speaker. Put each photo in ./speakers/ and reference its filename.
speakers:
  - name: "Matthew Myntti, PhD"
    role: "Speaker"                          # Speaker | Moderator | Panelist
    credentials: "PhD"
    org: "Organization / title"
    photo: "speakers/matthew-myntti.jpg"
    bio: >
      Two-sentence bio. Credentials and relevance to limb preservation.

  - name: "Karen Bauer, DNP"
    role: "Moderator"
    credentials: "DNP, APRN"
    org: "Organization / title"
    photo: "speakers/karen-bauer.jpg"
    bio: >
      Two-sentence bio.

# ===== VIDEO (revealed only AFTER the visitor submits the form) =====
# Paste the full Vimeo embed/iframe code you were given. Leave blank until you have it.
vimeo_embed: |
  <iframe src="https://player.vimeo.com/video/000000000?title=0&byline=0&portrait=0"
          width="100%" height="100%" frameborder="0"
          allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>

# ===== EMAIL GATE (Mailchimp) =====
gate:
  mailchimp_audience_id: ""                  # SALSAL Mailchimp Audience/List ID (Claude fills once provided)
  mailchimp_tags: ["webinar", "time-is-tissue"]   # tags applied to new subscribers
  double_optin: false                        # true = Mailchimp sends confirmation email first
  success_message: "You're in. Enjoy the session."

# ===== THUMBNAIL =====
poster: "speakers/poster.jpg"                # optional 16:9 cover image shown before play
---

## Notes (optional)

Anything else about this webinar: full description, references, related resources.
This markdown body is optional and will appear on the page below the video if present.
