# Prompt templates for MITRE ATT&CK documentation generation
PROMPT_TEMPLATES = {
    "description.md": "Write a comprehensive MITRE ATT&CK description for technique {id} on {platform}.",
    "detection.md": "Write detection rules for MITRE ATT&CK technique {id} on {platform}.",
    "mitigation.md": "Write mitigation strategies for MITRE ATT&CK technique {id} on {platform}.",
    "purple_playbook.md": "Create a purple team playbook for MITRE ATT&CK technique {id} on {platform}.",
    "references.md": "List references for MITRE ATT&CK technique {id} on {platform}.",
    "agent_notes.md": "Write agent research notes for MITRE ATT&CK technique {id} on {platform}."
}

def get_prompt(fname, technique):
    template = PROMPT_TEMPLATES.get(fname, "Write documentation for {id} {fname} on {platform}.")
    return template.format(id=technique["id"], platform=technique["platform"], fname=fname)
