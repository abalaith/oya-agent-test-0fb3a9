---
name: text-to-speech
display_name: "Text to Speech"
description: "Convert text to speech audio file using gTTS (free, no API key needed)"
category: voice
icon: volume-2
skill_type: sandbox
catalog_type: core
tool_schema:
  name: text_to_speech
  description: "Convert text to speech audio file"
  parameters:
    type: object
    properties:
      text:
        type: "string"
        description: "Text to convert to speech"
      lang:
        type: "string"
        description: "Language code (default 'en')"
    required: [text]
---
# Text to Speech
Convert text to speech audio file using gTTS (free, no API key needed)
