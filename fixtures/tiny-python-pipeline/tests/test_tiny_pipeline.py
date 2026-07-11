from tiny_pipeline import parse_rows

def test_parse_rows():
    assert parse_rows('id,value\n1,ok\n') == [{'id':'1','value':'ok'}]
