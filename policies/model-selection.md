# Model Selection

Inherit the parent model and reasoning effort unless task quality, latency, or cost justifies an override. Follow the active runtime's delegation permissions; this policy does not authorize spawning agents.

Use the skill's role guidance to classify work as judgment, bounded, or mechanical. A generated distribution includes candidate models for these roles. Treat these as initial settings to evaluate, not measured performance claims or mandatory overrides. Without a selected profile, inherit the runtime configuration.

Choose the lowest supported reasoning effort that meets acceptance criteria: low for mechanical work, medium for ordinary work, and high for difficult reasoning or critical review. Escalate further only when evidence warrants it. Keep subjective design, security decisions, and ambiguous synthesis out of the mechanical role.

Check model and effort availability in the active runtime before overriding. Use its supported per-agent interface or custom-agent configuration. When unavailable, inherit the parent and disclose material limitations. Never claim that a model override occurred without runtime confirmation. Pass the applicable role guidance explicitly to workers when their context is not inherited.

Compare representative tasks for correctness, completeness, evidence, latency, and token use before standardizing changes. Preserve shared acceptance criteria across profiles. Add model-specific instructions only after a reproducible failure or measured improvement, and record that evidence alongside the variant.
