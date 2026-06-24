from core.l2_nanobot.nanobot_base import BaseNanobot

class MDNBot(BaseNanobot):
    def __init__(self):
        super().__init__(
            bot_id=1,
            domain='developer.mozilla.org',
            schema={
                'search_url': 'https://developer.mozilla.org/en-US/search?q={query}',
                'selectors': {
                    'result_title': '.result-item h3',
                    'snippet': '.result-item p',
                    'url': '.result-item a[href]'
                },
                'rate_limit': 10,
                'content_types': ['html', 'css', 'javascript', 'web_api']
            }
        )

class ReactBot(BaseNanobot):
    def __init__(self):
        super().__init__(
            bot_id=2,
            domain='react.dev',
            schema={
                'search_url': 'https://react.dev/search?q={query}',
                'selectors': {
                    'result_title': 'article h2',
                    'snippet': 'article p',
                    'url': 'article a[href]'
                },
                'rate_limit': 10,
                'content_types': ['components', 'hooks', 'api_reference']
            }
        )

class PythonBot(BaseNanobot):
    def __init__(self):
        super().__init__(
            bot_id=3,
            domain='docs.python.org',
            schema={
                'search_url': 'https://docs.python.org/3/search.html?q={query}',
                'selectors': {
                    'result_title': '.search-results dt',
                    'snippet': '.search-results dd',
                    'url': '.search-results a[href]'
                },
                'rate_limit': 10,
                'content_types': ['library', 'tutorial', 'howto']
            }
        )

class GitHubBot(BaseNanobot):
    def __init__(self):
        super().__init__(
            bot_id=4,
            domain='github.com',
            schema={
                'search_url': 'https://github.com/search?q={query}+type:discussions',
                'selectors': {
                    'result_title': '.search-title a',
                    'snippet': '.search-snippet',
                    'url': '.search-title a[href]'
                },
                'rate_limit': 5,
                'content_types': ['discussions', 'issues'],
                'restrictions': ['No raw code access', 'No file contents']
            }
        )

class VerifyBot(BaseNanobot):
    def __init__(self):
        super().__init__(
            bot_id=5,
            domain='internal.verify',
            schema={
                'verification_methods': ['cross_reference', 'timestamp_check', 'source_authority'],
                'min_sources': 2,
                'confidence_threshold': 0.7
            }
        )

    def handle_message(self, msg):
        from core.l2_nanobot.nanobot_types import MessageType, CacheEntry
        claims = msg.payload.get('claims', [])
        verified = []
        for claim in claims:
            sources = claim.get('sources', [])
            if len(sources) >= self.schema['min_sources']:
                verified.append({'claim': claim['text'], 'status': 'verified', 'confidence': 0.85})
            else:
                verified.append({'claim': claim['text'], 'status': 'needs_review', 'confidence': 0.3})
        return Message(
            source_id=self.bot_id,
            target_id=msg.source_id,
            pheromone=self.query_to_embed(str(claims)),
            type=MessageType.VERIFY,
            payload={'verified_claims': verified},
            ttl=msg.ttl - 1
        )


def create_default_swarm():
    from core.l2_nanobot.nanobot_swarm import NanobotSwarm
    swarm = NanobotSwarm()
    for bot in [MDNBot(), ReactBot(), PythonBot(), GitHubBot(), VerifyBot()]:
        swarm.register(bot)
    return swarm
