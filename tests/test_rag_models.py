import pytest
from pydantic import ValidationError

from backend.app.models.rag import QueryRequest


def test_valid_query():
    req = QueryRequest(domanda="Come faccio la carta d'identita?")
    assert req.domanda == "Come faccio la carta d'identita?"


def test_query_is_trimmed():
    assert QueryRequest(domanda="  ciao  ").domanda == "ciao"


@pytest.mark.parametrize("bad", ["", "   "])
def test_blank_query_rejected(bad):
    with pytest.raises(ValidationError):
        QueryRequest(domanda=bad)


def test_missing_field_rejected():
    with pytest.raises(ValidationError):
        QueryRequest()  # type: ignore[call-arg]
