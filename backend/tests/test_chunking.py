"""Testes de chunking (REQ-FUNC-003)."""
from app.services.chunking import ApproxTokenizer, chunk_text


def _sentence(n: int) -> str:
    return f"Esta e a sentenca numero {n}."


def test_5000_words_generates_15_to_30_chunks():
    # ~4 palavras por sentença -> ~1250 sentenças; contagem via ceil(n/0.75)
    sentences = []
    n = 0
    while True:
        words = f"clausula artigo inciso norma {n}".split()[:4]
        sentences.append(" ".join(words) + ".")
        n += 1
        if sum(len(s.split()) for s in sentences) >= 5000:
            break
    text = " ".join(sentences)
    assert len(text.split()) >= 5000

    chunks = chunk_text(text, tokenizer=ApproxTokenizer(), max_tokens=512, overlap_tokens=50)
    assert 15 <= len(chunks) <= 30, f"esperado 15–30 chunks, obtido {len(chunks)}"

    for c in chunks:
        assert c.token_count <= 512
        assert c.overlap_prefix or c.order == 0


def test_100_words_single_chunk():
    text = " ".join(_sentence(i) for i in range(20))  # 20 * 5 palavras = 100
    chunks = chunk_text(text, tokenizer=ApproxTokenizer(), max_tokens=512, overlap_tokens=50)
    assert len(chunks) == 1
    assert chunks[0].overlap_prefix == ""
    assert chunks[0].text == text


def test_concatenation_equals_original():
    sentences = [_sentence(i) for i in range(200)]
    text = " ".join(sentences)
    chunks = chunk_text(text, tokenizer=ApproxTokenizer(), max_tokens=512, overlap_tokens=50)
    assert len(chunks) > 1
    assert " ".join(c.text for c in chunks) == text


def test_overlap_is_tail_of_previous_chunk():
    sentences = [_sentence(i) for i in range(200)]
    text = " ".join(sentences)
    chunks = chunk_text(text, tokenizer=ApproxTokenizer(), max_tokens=512, overlap_tokens=50)
    assert len(chunks) > 1
    for i in range(1, len(chunks)):
        prev_words = chunks[i - 1].text.split()
        prefix = chunks[i].overlap_prefix
        assert prefix, f"chunk {i} sem overlap"
        assert prev_words[-len(prefix.split()):] == prefix.split()
