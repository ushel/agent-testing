from config.settings import DEPLOY_THRESHOLD

def should_deploy(score: float):
    return score >= DEPLOY_THRESHOLD
