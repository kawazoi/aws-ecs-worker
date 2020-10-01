from dotenv import load_dotenv
from os import getenv

from aws_cdk import core

from stacks.service_stack import ServiceStack


# Load environment variables
load_dotenv()
_env = core.Environment(
    account=getenv("AWS_ACCOUNT_ID"), region=getenv("AWS_DEFAULT_REGION")
)
svc = getenv("SERVICE_NAME")

# Create app
app = core.App()

# Staging Stack
stage = "Staging"
cfg_stg = {}
stg = ServiceStack(app, "{}-{}".format(svc, stage.lower()), stage, cfg_stg, env=_env)
core.Tag.add(stg, "Project", "NlpServing")
core.Tag.add(stg, "Environment", stage)

# Production Stack
stage = "Production"
cfg_prd = {}
prd = ServiceStack(app, "{}-{}".format(svc, stage.lower()), stage, cfg_stg, env=_env)
core.Tag.add(prd, "Project", "NlpServing")
core.Tag.add(prd, "Environment", stage)

app.synth()
