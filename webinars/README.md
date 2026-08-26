# SALSAL Webinar Pages

One folder per webinar. Each becomes its own gated page at `/webinars/<slug>`:
the Vimeo video is hidden until the visitor submits the form, which subscribes
them to SALSAL's Mailchimp audience, then reveals the video.

## How to add a webinar
1. Duplicate the `_TEMPLATE/` folder and rename it to the webinar slug
   (lowercase, dashes), e.g. `time-is-tissue/`.
2. Fill in `info.md` (title, date, summary, speakers, Vimeo embed, Mailchimp tags).
3. Drop each speaker photo into that webinar's `speakers/` folder and reference
   the filename in `info.md`.
4. Tell Claude the slug and say "build this webinar page."

## Folder layout
```
webinars/
  _TEMPLATE/          # copy this
    info.md
    speakers/
  time-is-tissue/     # example built webinar
    info.md
    speakers/
      matthew-myntti.jpg
      karen-bauer.jpg
    index.html        # generated gated page (Claude builds)
```

## The email gate (how it works)
Form (name + email) -> Cloudflare Worker -> Mailchimp API (add subscriber + tags)
-> on success the page reveals the Vimeo player. Same reusable pattern as the
PAWSIC webinar system; here it points at SALSAL's Mailchimp instead of MemberPress.

## What Claude still needs from Dahlia (one-time)
- SALSAL Mailchimp **API key** added to `~/.config/mailchimp-clients.json` under `salsal`.
- SALSAL Mailchimp **Audience/List ID** to subscribe registrants into.
- Per webinar: the **Vimeo embed code**.
