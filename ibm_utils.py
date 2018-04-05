from watson_developer_cloud import DiscoveryV1
from config import DISCOVERY_USERNAME, DISCOVERY_PASSWORD, NLU_USERNAME, NLU_PASSWORD
import json

discovery = DiscoveryV1(
    username = DISCOVERY_USERNAME,
    password = DISCOVERY_PASSWORD,
    version = '2017-11-07'
)

nlu = NaturalLanguageUnderstandingV1(
    username = NLU_USERNAME,
    password = NLU_PASSWORD,
    version = '2018-03-16'
)
