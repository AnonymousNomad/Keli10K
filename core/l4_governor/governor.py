import re
import json
import time
from typing import List, Tuple, Optional

class SovereignKernel:
    def __init__(self, whitelist=None, schema_registry=None):
        self.whitelist = whitelist or {
            'developer.mozilla.org',
            'react.dev',
            'docs.python.org',
            'arxiv.org',
            'github.com'
        }
        self.github_only = {'discussions', 'issues'}
        self.schema_registry = schema_registry or {}
        self.injection_patterns = [
            r'SELECT\s+.*\s+FROM',
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'<script[^>]*>',
            r'javascript:',
            r'onerror\s*=',
            r'onload\s*=',
            r'\.\./\.\./',
            r'file://',
            r'exec\s*\(',
            r'eval\s*\(',
            r'system\s*\(',
            r'__import__',
            r'os\.system',
            r'subprocess\.',
        ]
        self.blocked_domain_patterns = [
            r'raw\.githubusercontent\.com',
            r'api\.github\.com/repos/.*/contents',
            r'pastebin\.com',
            r'digitalocean\.com/spaces',
        ]

    def approve(self, dispatch_plan):
        if not isinstance(dispatch_plan, dict):
            return False, 'dispatch_plan must be dict'
        bot_id = dispatch_plan.get('bot_id')
        query = dispatch_plan.get('query', '')
        constraints = dispatch_plan.get('constraints', [])

        if self._injection_detect(query):
            return False, f'injection detected in query: {query[:50]}'

        schema = self.schema_registry.get(bot_id, {})
        if schema:
            for key in constraints:
                if key not in schema:
                    return False, f'constraint {key} not in schema'

        return True, 'approved'

    def approve_url(self, url):
        for pattern in self.blocked_domain_patterns:
            if re.search(pattern, url):
                return False
        for domain in self.whitelist:
            if domain in url:
                if domain == 'github.com':
                    if not any(prefix in url for prefix in self.github_only):
                        return False
                return True
        return False

    def _injection_detect(self, text):
        if not isinstance(text, str):
            return True
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


class TruthEngine:
    def __init__(self):
        self.citation_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.url_pattern = re.compile(r'https?://[^\s,)]+')
        self.date_pattern = re.compile(r'\b(19|20)\d{2}\b')
        self.unsupported_claims = []

    def verify(self, text):
        citations = self._extract_citations(text)
        unsourced = self._find_unsourced(text)
        if len(citations) == 0 and len(text.strip()) > 20:
            return False, ['No citations found in output']
        passed = len(unsourced) == 0
        return passed, unsourced

    def _extract_citations(self, text):
        citations = []
        for match in self.citation_pattern.finditer(text):
            citations.append({
                'text': match.group(1),
                'url': match.group(2),
                'position': match.start()
            })
        if not citations:
            for match in self.url_pattern.finditer(text):
                citations.append({
                    'text': text[max(0, match.start()-30):match.start()],
                    'url': match.group(0),
                    'position': match.start()
                })
        return citations

    def _find_unsourced(self, text):
        sentences = re.split(r'[.!?]\s+', text)
        unsourced = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 15:
                continue
            has_citation = bool(self.citation_pattern.search(sent)) or bool(self.url_pattern.search(sent))
            is_meta = any(sent.startswith(tag) for tag in ['<PLAN>', '<EXECUTION>', '<REFLECTION>', '<CITE>', '<UNSURE>'])
            if not has_citation and not is_meta:
                unsourced.append(sent[:80])
        return unsourced

    def scan_claims(self, text):
        claims = []
        for sent in re.split(r'[.!?]\s+', text):
            sent = sent.strip()
            if len(sent) > 20 and not sent.startswith('<'):
                citations = self._extract_citations(sent)
                claims.append({
                    'text': sent[:100],
                    'citations': citations,
                    'sourced': len(citations) > 0
                })
        return claims


class SelfHealingLoop:
    def __init__(self, kernel, swarm, max_retries=3):
        self.kernel = kernel
        self.swarm = swarm
        self.max_retries = max_retries

    def handle(self, model_output, bot_results, synthesis):
        action = 'pass'
        output = synthesis
        retry_count = 0

        if model_output is None or len(str(model_output)) < 5:
            action = 'regenerate_decomposition'
            output = '<UNSURE> Model failed to produce decomposition'
            return {'action': action, 'output': output, 'retry_count': 0}

        if isinstance(bot_results, list):
            valid = [r for r in bot_results if r is not None]
            if len(valid) == 0:
                if retry_count < self.max_retries:
                    action = 'retry_dispatch'
                    retry_count += 1
                    output = '<UNSURE> All nanobots returned no results. Retrying.'
                else:
                    action = 'fallback_memory'
                    output = '<UNSURE> Retrieval failed after max retries. Using cached knowledge if available.'

        if synthesis and '<CITE>' not in synthesis and '<UNSURE>' not in synthesis:
            if retry_count < self.max_retries:
                action = 'force_citation'
                retry_count += 1
                output = '<CITE> ' + synthesis + ' [source unavailable, offline mode]'

        return {'action': action, 'output': output, 'retry_count': retry_count}
