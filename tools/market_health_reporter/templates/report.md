# {{ exchange }} Market Health Report - {{ date }} 🌰

## Executive Summary


{{ metrics_table }}

{% if rag_context %}
## Market Context & Analysis

{% for metric_name, context in rag_context.items() %}
### {{ metric_name }}

{{ context }}

{% endfor %}
{% endif %}

## Detailed Analysis

{% for metric in metrics %}