from posthog import Posthog
import os


posthog = Posthog(project_api_key=os.getenv(
    'POSTHOG_API_KEY'), host='https://eu.i.posthog.com')

if os.getenv('ENV') == 'dev':
    # posthog.debug = True
    posthog.disabled = True


def capture(uid, event_name, properties):
    posthog.capture(uid, event_name, properties)


def capture_pageview(uid, route):
    posthog.capture(uid, '$pageview', {
                    '$current_url': os.getenv('FRONTEND_URL') + route})
