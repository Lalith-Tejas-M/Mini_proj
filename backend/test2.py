from prompts.insight_prompts import INSIGHT_USER_PROMPT
try:
    res = INSIGHT_USER_PROMPT.format(topic='a', memory_context='b')
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
