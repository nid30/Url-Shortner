"""
Parses raw User-Agent strings into a device type + browser name.

We parse once, at write-time (when the click is logged), and store the
result rather than re-parsing on every analytics read. This is a
deliberate space-for-speed tradeoff: it costs a little extra storage
per row, but means aggregation queries (GROUP BY device_type) hit an
indexed/plain column instead of parsing text at query time.
"""

from user_agents import parse as parse_ua


def parse_device_and_browser(user_agent_string: str | None) -> tuple[str, str]:
    if not user_agent_string:
        return "other", "unknown"

    ua = parse_ua(user_agent_string)

    if ua.is_bot:
        device_type = "bot"
    elif ua.is_mobile:
        device_type = "mobile"
    elif ua.is_tablet:
        device_type = "tablet"
    elif ua.is_pc:
        device_type = "pc"
    else:
        device_type = "other"

    browser = ua.browser.family or "unknown"

    return device_type, browser