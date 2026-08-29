from src.extraction import parse_date,total_amount,extract_items

def test_date():
    assert parse_date(['Date: 26/03/2018'])[0] == '2018-03-26'

def test_total():
    assert total_amount(['Grand Total : 33.00'])[0] == 33.0

def test_items():
    x=extract_items(['Qty Description Price Amount','1 MILK 10.00 10.00','TOTAL 10.00'])
    assert len(x)==1 and x[0]['price']==10.0
