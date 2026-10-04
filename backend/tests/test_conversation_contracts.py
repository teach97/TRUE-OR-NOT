from uuid import uuid4
import pytest
from pydantic import ValidationError
from test_contracts import result_payload
from conversation_contracts import MessageCreate, StoredSnapshot


def test_message_requires_consent_and_limits():
    data = dict(storageConsent=True, requestId=str(uuid4()), role='user', content='hello', status='completed')
    assert MessageCreate.model_validate(data).content == 'hello'
    for patch in ({'storageConsent':False}, {'content':'x' * 12001}, {'role':'system'}, {'requestId':'bad'}, {'status':'thinking'}):
        with pytest.raises(ValidationError):
            MessageCreate.model_validate(data | patch)
    with pytest.raises(ValidationError):
        MessageCreate.model_validate({k:v for k,v in data.items() if k != 'storageConsent'})
    with pytest.raises(ValidationError):
        MessageCreate.model_validate(data | {'role':'assistant','content':'x' * 60001})


def test_snapshot_strips_private_and_api_fields():
    data = result_payload()
    data['sources'][0]['youtubeComments'] = ['private comment']
    data['evidence'][0]['sectionText'] = 'full external article'
    data['rawProvider'] = 'private'
    snapshot = StoredSnapshot.model_validate(data).model_dump(mode='json')
    assert snapshot['sources'][0]['url'] == data['sources'][0]['url']
    assert snapshot['checkedAt'] == data['checkedAt']
    assert 'rawProvider' not in snapshot
    assert 'youtubeComments' not in snapshot['sources'][0]
    assert 'sectionText' not in snapshot['evidence'][0]


def test_snapshot_rejects_broken_references():
    data = result_payload()
    data['evidence'][0]['sourceId'] = 'missing'
    with pytest.raises(ValidationError):
        StoredSnapshot.model_validate(data)
